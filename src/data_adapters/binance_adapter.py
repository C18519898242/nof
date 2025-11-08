"""
币安数据适配器

从币安API获取历史价格数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from binance.client import Client
from .base_adapter import BaseAdapter
from ..utils.logger import get_logger


class BinanceAdapter(BaseAdapter):
    """币安数据适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = get_logger('BinanceAdapter')
        
        # 币安API配置
        self.api_key = config.get('api_key')
        self.api_secret = config.get('secret_key')
        self.testnet = config.get('testnet', False)
        self.proxy = config.get('proxy')
        
        # 初始化币安客户端
        try:
            if self.api_key and self.api_secret:
                # 配置代理
                client_config = {}
                if self.proxy:
                    client_config = {
                        'proxies': {
                            'http': self.proxy,
                            'https': self.proxy
                        }
                    }
                
                # 创建客户端
                if self.testnet:
                    self.client = Client(
                        self.api_key, 
                        self.api_secret,
                        testnet=True,
                        **client_config
                    )
                    self.logger.info(f"币安测试网客户端初始化成功 (代理: {self.proxy})")
                else:
                    self.client = Client(
                        self.api_key, 
                        self.api_secret,
                        **client_config
                    )
                    self.logger.info(f"币安客户端初始化成功 (代理: {self.proxy})")
            else:
                self.client = Client()
                self.logger.warning("未提供币安API密钥，使用公开客户端")
                
        except Exception as e:
            self.logger.error(f"币安客户端初始化失败: {e}")
            self.client = None
        
        self.rate_limit_delay = config.get('rate_limit_delay', 0.1)  # API调用间隔
    
    def get_data(self, symbol: str, start_date: datetime, end_date: datetime, **kwargs) -> pd.DataFrame:
        """
        获取币安历史数据
        
        Args:
            symbol: 交易对符号 (例如: 'BTCUSDT', 'ETHUSDT')
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数 (interval='1h', etc.)
            
        Returns:
            pd.DataFrame: OHLCV数据
        """
        try:
            self.logger.info(f"获取币安数据: {symbol}, {start_date} 到 {end_date}")
            
            # 参数处理
            interval = kwargs.get('interval', '1h')
            binance_symbol = self._convert_symbol(symbol)
            
            # 获取数据
            if self.client:
                df = self._get_klines(binance_symbol, start_date, end_date, interval)
            else:
                df = self._generate_mock_data(symbol, start_date, end_date)
            
            if df.empty:
                self.logger.warning(f"未获取到数据: {symbol}")
                return self._generate_empty_data(start_date, end_date)
            
            self.logger.info(f"成功获取 {len(df)} 条数据记录")
            return df
            
        except Exception as e:
            self.logger.error(f"获取币安数据失败: {e}")
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
            binance_symbol = self._convert_symbol(symbol)
            # 简单验证：检查长度和字符
            return len(binance_symbol) >= 6 and binance_symbol.isalnum()
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
                # 获取交易对信息
                exchange_info = self.client.get_exchange_info()
                symbols = [symbol['symbol'] for symbol in exchange_info['symbols'] 
                          if symbol['status'] == 'TRADING']
                self.logger.info(f"获取到 {len(symbols)} 个可用交易对")
                return symbols
            else:
                # 返回一些常见的交易对
                return [
                    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
                    'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'MATICUSDT'
                ]
            
        except Exception as e:
            self.logger.error(f"获取交易对列表失败: {e}")
            return [
                'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
                'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'MATICUSDT'
            ]
    
    def get_supported_intervals(self) -> List[str]:
        """
        获取支持的时间间隔列表
        
        Returns:
            List[str]: 支持的时间间隔列表
        """
        return [
            '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', 
            '6h', '8h', '12h', '1d', '3d', '1w', '1M'
        ]
    
    def _convert_symbol(self, symbol: str) -> str:
        """
        转换交易对符号格式
        
        Args:
            symbol: 输入符号 (例如: 'BTC-USD', 'BTC/USD', 'BTCUSD', 'BTCUSDT')
            
        Returns:
            str: 币安格式的符号 (例如: 'BTCUSDT')
        """
        # 移除分隔符
        clean_symbol = symbol.replace('-', '').replace('/', '').upper()
        
        # 如果已经是币安格式
        if clean_symbol.endswith('USDT') or clean_symbol.endswith('BUSD') or clean_symbol.endswith('BTC') or clean_symbol.endswith('ETH'):
            return clean_symbol
        
        # 处理常见转换
        if clean_symbol.endswith('USD'):
            return clean_symbol.replace('USD', 'USDT')
        
        # 默认假设是USDT交易对
        if not any(clean_symbol.endswith(suffix) for suffix in ['USDT', 'BUSD', 'BTC', 'ETH']):
            return clean_symbol + 'USDT'
        
        return clean_symbol
    
    def _get_klines(self, symbol: str, start_date: datetime, 
                   end_date: datetime, interval: str) -> pd.DataFrame:
        """获取K线数据"""
        try:
            import time
            
            # 转换时间格式
            start_ts = int(start_date.timestamp() * 1000)
            end_ts = int(end_date.timestamp() * 1000)
            
            all_klines = []
            current_end = end_ts
            
            # 分批获取数据
            while current_end > start_ts:
                current_start = max(current_end - 1000 * self._get_interval_ms(interval), start_ts)
                
                try:
                    klines = self.client.get_klines(
                        symbol=symbol,
                        interval=interval,
                        startTime=current_start,
                        endTime=current_end,
                        limit=1000
                    )
                    
                    if klines:
                        all_klines.extend(klines)
                    
                    current_end = current_start
                    time.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    self.logger.error(f"获取K线数据失败: {e}")
                    break
            
            if not all_klines:
                return pd.DataFrame()
            
            # 转换为DataFrame
            data = []
            for kline in all_klines:
                data.append({
                    'timestamp': pd.to_datetime(kline[0], unit='ms'),
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5])
                })
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"获取K线数据失败: {e}")
            return pd.DataFrame()
    
    def _get_interval_ms(self, interval: str) -> int:
        """获取时间间隔的毫秒数"""
        interval_map = {
            '1m': 60 * 1000,
            '3m': 3 * 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '30m': 30 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '2h': 2 * 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '6h': 6 * 60 * 60 * 1000,
            '8h': 8 * 60 * 60 * 1000,
            '12h': 12 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000,
            '3d': 3 * 24 * 60 * 60 * 1000,
            '1w': 7 * 24 * 60 * 60 * 1000,
            '1M': 30 * 24 * 60 * 60 * 1000,
        }
        return interval_map.get(interval, 60 * 60 * 1000)  # 默认1小时
    
    def _generate_mock_data(self, symbol: str, start_date: datetime, 
                        end_date: datetime) -> pd.DataFrame:
        """生成模拟数据作为fallback"""
        try:
            from .mock_adapter import MockAdapter
            
            # 创建模拟适配器
            mock_config = {
                'price_range': [50000, 70000] if 'BTC' in symbol else [3000, 4000],
                'volatility': 0.03,
                'trend': 0.0001
            }
            mock_adapter = MockAdapter(mock_config)
            
            # 获取模拟数据
            df = mock_adapter.get_data(symbol, start_date, end_date)
            
            self.logger.info(f"使用模拟数据替代 {symbol}: {len(df)} 条记录")
            return df
            
        except Exception as e:
            self.logger.error(f"生成模拟数据失败: {e}")
            return pd.DataFrame()
    
    def _generate_empty_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """生成空的数据框架"""
        # 创建时间索引
        date_range = pd.date_range(start=start_date, end=end_date, freq='h')
        
        # 创建空的OHLCV数据
        empty_data = pd.DataFrame(index=date_range)
        empty_data['open'] = 0.0
        empty_data['high'] = 0.0
        empty_data['low'] = 0.0
        empty_data['close'] = 0.0
        empty_data['volume'] = 0.0
        
        return empty_data
    
    def get_adapter_info(self) -> Dict[str, Any]:
        """
        获取适配器信息
        
        Returns:
            Dict[str, Any]: 适配器信息
        """
        return {
            'name': 'BinanceAdapter',
            'version': '1.0.0',
            'description': '币安数据适配器，支持加密货币历史数据获取',
            'supported_timeframes': ['minute', 'hour', 'day', 'week', 'month'],
            'supported_intervals': self.get_supported_intervals(),
            'requires_auth': False,  # 公开数据不需要认证
            'testnet_supported': True,
            'proxy_supported': True,
            'rate_limits': {
                'requests_per_second': 10,
                'requests_per_minute': 1200
            }
        }
