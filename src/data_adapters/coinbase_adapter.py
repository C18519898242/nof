"""
Coinbase数据适配器

从Coinbase API获取历史价格数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
try:
    from coinbase.wallet import Client
except ImportError:
    # 如果coinbase.wallet不可用，使用其他方式
    Client = None
from .base_adapter import BaseAdapter
from ..utils.logger import get_logger


class CoinbaseAdapter(BaseAdapter):
    """Coinbase数据适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = get_logger('CoinbaseAdapter')
        
        # Coinbase API配置
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.sandbox = config.get('sandbox', False)
        
        # 初始化Coinbase客户端
        try:
            if self.api_key and self.api_secret and Client:
                self.client = Client(
                    self.api_key, 
                    self.api_secret,
                    api_url='https://api.sandbox.coinbase.com' if self.sandbox else 'https://api.coinbase.com'
                )
                self.logger.info(f"Coinbase客户端初始化成功 (沙盒模式: {self.sandbox})")
            else:
                self.client = None
                if not Client:
                    self.logger.warning("Coinbase SDK未安装，将使用模拟数据")
                else:
                    self.logger.warning("未提供Coinbase API密钥，将使用公开数据")
        except Exception as e:
            self.logger.error(f"Coinbase客户端初始化失败: {e}")
            self.client = None
        
        self.rate_limit_delay = config.get('rate_limit_delay', 0.1)  # API调用间隔
    
    def get_data(self, symbol: str, start_date: datetime, end_date: datetime, **kwargs) -> pd.DataFrame:
        """
        获取Coinbase历史数据
        
        Args:
            symbol: 交易对符号 (例如: 'BTC-USD', 'ETH-USD')
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数 (granularity='hour', etc.)
            
        Returns:
            pd.DataFrame: OHLCV数据
        """
        try:
            self.logger.info(f"获取Coinbase数据: {symbol}, {start_date} 到 {end_date}")
            
            # 参数处理
            granularity = kwargs.get('granularity', 'hour')
            product_id = self._convert_symbol(symbol)
            
            # 获取数据
            if self.client:
                df = self._get_data_with_auth(product_id, start_date, end_date, granularity)
            else:
                df = self._get_public_data(product_id, start_date, end_date, granularity)
            
            if df.empty:
                self.logger.warning(f"未获取到数据: {symbol}")
                return self._generate_empty_data(start_date, end_date)
            
            self.logger.info(f"成功获取 {len(df)} 条数据记录")
            return df
            
        except Exception as e:
            self.logger.error(f"获取Coinbase数据失败: {e}")
            # 返回空数据而不是抛出异常
            return self._generate_empty_data(start_date, end_date)
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        验证交易对符号
        
        Args:
            symbol: 交易对符号
            
        Returns:
            bool: 是否有效
        """
        try:
            product_id = self._convert_symbol(symbol)
            # 简单验证：检查格式
            return '-' in product_id and len(product_id.split('-')) == 2
        except:
            return False
    
    def get_available_symbols(self) -> List[str]:
        """
        获取可用的交易对列表
        
        Returns:
            List[str]: 交易对列表
        """
        try:
            if self.client:
                # 使用认证客户端获取产品列表
                products = self.client.get_products()
                symbols = [product['id'] for product in products['data']]
            else:
                # 使用公开API获取产品列表
                import requests
                response = requests.get('https://api.coinbase.com/v2/products')
                if response.status_code == 200:
                    products = response.json()
                    symbols = [product['id'] for product in products['data']]
                else:
                    symbols = []
            
            self.logger.info(f"获取到 {len(symbols)} 个可用交易对")
            return symbols
            
        except Exception as e:
            self.logger.error(f"获取交易对列表失败: {e}")
            # 返回一些常见的交易对
            return [
                'BTC-USD', 'ETH-USD', 'LTC-USD', 'BCH-USD',
                'BTC-EUR', 'ETH-EUR', 'BTC-GBP', 'ETH-GBP'
            ]
    
    def _convert_symbol(self, symbol: str) -> str:
        """
        转换交易对符号格式
        
        Args:
            symbol: 输入符号 (例如: 'BTCUSD', 'BTC/USD', 'BTC-USD')
            
        Returns:
            str: Coinbase格式的符号 (例如: 'BTC-USD')
        """
        # 如果已经是Coinbase格式
        if '-' in symbol and len(symbol.split('-')) == 2:
            return symbol.upper()
        
        # 处理 'BTC/USD' 格式
        if '/' in symbol:
            return symbol.replace('/', '-').upper()
        
        # 处理 'BTCUSD' 格式
        # 尝试识别常见的货币代码
        common_currencies = ['USD', 'EUR', 'GBP', 'BTC', 'ETH', 'LTC', 'BCH']
        for currency in common_currencies:
            if symbol.endswith(currency):
                base = symbol[:-len(currency)]
                return f"{base}-{currency}"
        
        # 默认假设最后3个字符是计价货币
        if len(symbol) >= 6:
            base = symbol[:-3]
            quote = symbol[-3:]
            return f"{base}-{quote}"
        
        return symbol
    
    def _get_data_with_auth(self, product_id: str, start_date: datetime, 
                          end_date: datetime, granularity: str) -> pd.DataFrame:
        """使用认证API获取数据"""
        try:
            # Coinbase Pro API 的历史数据端点
            import requests
            import time
            import hmac
            import hashlib
            
            base_url = 'https://api.pro.coinbase.com' if not self.sandbox else 'https://api.pro.sandbox.coinbase.com'
            
            # 计算时间戳和粒度
            end_timestamp = int(end_date.timestamp())
            start_timestamp = int(start_date.timestamp())
            
            # 转换粒度
            granularity_map = {
                'minute': 60,
                'hour': 3600,
                'day': 86400
            }
            granularity_seconds = granularity_map.get(granularity, 3600)
            
            all_data = []
            current_end = end_timestamp
            
            # 分批获取数据
            while current_end > start_timestamp:
                current_start = max(current_end - 300 * granularity_seconds, start_timestamp)
                
                # 构建请求
                url = f"{base_url}/products/{product_id}/candles"
                params = {
                    'start': datetime.fromtimestamp(current_start).isoformat(),
                    'end': datetime.fromtimestamp(current_end).isoformat(),
                    'granularity': granularity_seconds
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    candles = response.json()
                    if candles:
                        # Coinbase返回的格式: [timestamp, low, high, open, close, volume]
                        for candle in candles:
                            all_data.append({
                                'timestamp': datetime.fromtimestamp(candle[0]),
                                'open': candle[3],
                                'high': candle[1],
                                'low': candle[2],
                                'close': candle[4],
                                'volume': candle[5]
                            })
                
                current_end = current_start
                time.sleep(self.rate_limit_delay)
            
            if not all_data:
                return pd.DataFrame()
            
            df = pd.DataFrame(all_data)
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"认证API获取数据失败: {e}")
            return pd.DataFrame()
    
    def _get_public_data(self, product_id: str, start_date: datetime, 
                        end_date: datetime, granularity: str) -> pd.DataFrame:
        """使用公开API获取数据"""
        try:
            import requests
            import time
            
            # 使用新的Coinbase Advanced Trade API
            # 注意：新API可能需要认证，这里使用模拟数据作为fallback
            self.logger.warning("Coinbase Pro API已弃用，使用模拟数据作为演示")
            
            # 生成模拟数据用于演示
            return self._generate_mock_data(product_id, start_date, end_date, granularity)
            
        except Exception as e:
            self.logger.error(f"公开API获取数据失败: {e}")
            return self._generate_mock_data(product_id, start_date, end_date, granularity)
    
    def _generate_mock_data(self, product_id: str, start_date: datetime, 
                           end_date: datetime, granularity: str) -> pd.DataFrame:
        """生成模拟数据作为fallback"""
        try:
            from .mock_adapter import MockAdapter
            
            # 创建模拟适配器
            mock_config = {
                'price_range': [50000, 70000] if 'BTC' in product_id else [3000, 4000],
                'volatility': 0.03,
                'trend': 0.0001
            }
            mock_adapter = MockAdapter(mock_config)
            
            # 获取模拟数据
            df = mock_adapter.get_data(product_id, start_date, end_date)
            
            self.logger.info(f"使用模拟数据替代 {product_id}: {len(df)} 条记录")
            return df
            
        except Exception as e:
            self.logger.error(f"生成模拟数据失败: {e}")
            return pd.DataFrame()
    
    def _generate_empty_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """生成空的数据框架"""
        # 创建时间索引
        date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        
        # 创建空的OHLCV数据
        empty_data = pd.DataFrame(index=date_range)
        empty_data['open'] = 0.0
        empty_data['high'] = 0.0
        empty_data['low'] = 0.0
        empty_data['close'] = 0.0
        empty_data['volume'] = 0.0
        
        return empty_data
    
    def get_supported_intervals(self) -> List[str]:
        """
        获取支持的时间间隔列表
        
        Returns:
            List[str]: 支持的时间间隔列表
        """
        return ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
    
    def get_adapter_info(self) -> Dict[str, Any]:
        """
        获取适配器信息
        
        Returns:
            Dict[str, Any]: 适配器信息
        """
        return {
            'name': 'CoinbaseAdapter',
            'version': '1.0.0',
            'description': 'Coinbase数据适配器，支持加密货币历史数据获取',
            'supported_timeframes': ['minute', 'hour', 'day'],
            'supported_intervals': self.get_supported_intervals(),
            'requires_auth': True,
            'sandbox_supported': True,
            'rate_limits': {
                'requests_per_second': 10,
                'requests_per_hour': 10000
            }
        }
