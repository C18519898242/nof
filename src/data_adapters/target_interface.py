"""
数据适配器目标接口

定义统一的数据格式标准。
"""

from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any


class IDataTarget(ABC):
    """数据适配器目标接口，定义统一的数据格式标准"""
    
    @abstractmethod
    def get_data(self, symbol: str, start_date: datetime, end_date: datetime, **kwargs) -> pd.DataFrame:
        """
        获取标准化数据
        
        Args:
            symbol: 交易对代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
        
        Returns:
            pd.DataFrame: 标准格式的数据，包含列：open, high, low, close, volume
        """
        pass
    
    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """验证交易对是否有效"""
        pass
    
    @abstractmethod
    def get_supported_intervals(self) -> list:
        """获取支持的时间间隔"""
        pass
