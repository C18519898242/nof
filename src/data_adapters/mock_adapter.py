"""
Mock适配器

用于测试的模拟数据适配器。
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any
from .base_adapter import BaseAdapter


class MockAdapter(BaseAdapter):
    """Mock数据适配器，用于测试"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config or {})
        self.logger.info("Mock适配器初始化完成")
    
    def get_data(self, symbol: str, start_date: datetime, end_date: datetime, **kwargs) -> pd.DataFrame:
        """
        获取模拟数据
        
        Args:
            symbol: 交易对代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
            
        Returns:
            pd.DataFrame: 模拟的OHLCV数据
        """
        self.logger.info(f"获取模拟数据: {symbol}, {start_date} 到 {end_date}")
        
        # 验证日期范围
        if not self._validate_date_range(start_date, end_date):
            raise ValueError("日期范围无效")
        
        # 生成日期范围
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 生成模拟价格数据
        np.random.seed(42)  # 确保可重现
        
        # 基础价格
        base_price = 100.0
        
        # 生成随机价格走势
        returns = np.random.normal(0, 0.02, len(date_range))
        prices = [base_price]
        
        for ret in returns[:-1]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, 1.0))  # 价格不能为负
        
        # 生成OHLC数据
        data = []
        for i, (date, close_price) in enumerate(zip(date_range, prices)):
            # 生成当天的OHLC
            daily_volatility = close_price * 0.02
            high = close_price + abs(np.random.normal(0, daily_volatility))
            low = close_price - abs(np.random.normal(0, daily_volatility))
            open_price = low + (high - low) * np.random.random()
            
            # 确保OHLC的逻辑正确
            high = max(high, open_price, close_price)
            low = min(low, open_price, close_price)
            
            # 生成交易量
            volume = int(np.random.normal(1000000, 200000))
            volume = max(volume, 100000)
            
            data.append({
                'datetime': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        self.logger.info(f"生成模拟数据: {len(df)} 条记录")
        
        # 标准化数据格式
        return self._standardize_dataframe(df)
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        验证交易对格式
        
        Args:
            symbol: 交易对代码
            
        Returns:
            bool: Mock适配器接受任何非空符号
        """
        if not symbol or not isinstance(symbol, str):
            self.logger.error(f"无效的交易对: {symbol}")
            return False
        
        # Mock适配器接受任何符号，但记录日志
        self.logger.info(f"验证交易对: {symbol} - 通过")
        return True
    
    def get_supported_intervals(self) -> list:
        """
        获取支持的时间间隔
        
        Returns:
            list: Mock适配器支持所有常见时间间隔
        """
        return [
            '1m', '5m', '15m', '30m', '1h', '4h', '1d',
            '1w', '1M'  # 分钟、小时、天、周、月
        ]
    
    def get_available_symbols(self) -> list:
        """
        获取可用的交易对列表
        
        Returns:
            list: 模拟的交易对列表
        """
        return [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA',
            'BTC-USD', 'ETH-USD', 'BNB-USD',
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT'
        ]
