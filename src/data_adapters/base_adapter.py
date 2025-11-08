"""
适配器基类

提供通用功能和数据标准化。
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any
from .target_interface import IDataTarget
from ..utils.logger import get_logger


class BaseAdapter(IDataTarget):
    """适配器基类，提供通用功能"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        self._rate_limiter = None
    
    def _standardize_dataframe(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        标准化数据格式为backtrader要求的格式
        
        Args:
            raw_data: 原始数据DataFrame
            
        Returns:
            pd.DataFrame: 标准格式的数据，包含列：open, high, low, close, volume
        """
        self.logger.debug(f"开始数据标准化，原始数据形状: {raw_data.shape}")
        
        # 定义标准列名映射
        column_mapping = {
            'open': ['open', 'Open', 'OPEN', 'o'],
            'high': ['high', 'High', 'HIGH', 'h'], 
            'low': ['low', 'Low', 'LOW', 'l'],
            'close': ['close', 'Close', 'CLOSE', 'c'],
            'volume': ['volume', 'Volume', 'VOLUME', 'v']
        }
        
        # 查找匹配的列名
        standardized_columns = {}
        for standard_col, possible_cols in column_mapping.items():
            for col in possible_cols:
                if col in raw_data.columns:
                    standardized_columns[standard_col] = col
                    break
            
            if standard_col not in standardized_columns:
                self.logger.warning(f"未找到列 {standard_col}，可用列: {list(raw_data.columns)}")
        
        # 创建标准化的DataFrame
        if len(standardized_columns) < 4:  # 至少需要OHLC
            raise ValueError(f"数据列不完整，找到的列: {list(standardized_columns.keys())}")
        
        standard_data = pd.DataFrame()
        for standard_col, original_col in standardized_columns.items():
            standard_data[standard_col] = raw_data[original_col]
        
        # 确保数据按时间排序
        if 'datetime' in raw_data.columns:
            standard_data = standard_data.set_index(pd.to_datetime(raw_data['datetime']))
        elif 'date' in raw_data.columns:
            standard_data = standard_data.set_index(pd.to_datetime(raw_data['date']))
        elif standard_data.index.name in ['datetime', 'date']:
            standard_data.index = pd.to_datetime(standard_data.index)
        
        # 确保索引是datetime类型
        if not isinstance(standard_data.index, pd.DatetimeIndex):
            standard_data.index = pd.to_datetime(standard_data.index)
        
        # 填充缺失的volume列
        if 'volume' not in standard_data.columns:
            standard_data['volume'] = 0
            self.logger.warning("未找到volume列，设置为0")
        
        self.logger.debug(f"数据标准化完成，最终数据形状: {standard_data.shape}")
        return standard_data
    
    def _handle_api_error(self, error: Exception) -> None:
        """
        处理API错误
        
        Args:
            error: 异常对象
        """
        error_msg = f"API错误: {str(error)}"
        self.logger.error(error_msg)
        
        # 根据错误类型进行不同处理
        if "timeout" in str(error).lower():
            self.logger.error("请求超时，请检查网络连接")
        elif "401" in str(error) or "unauthorized" in str(error).lower():
            self.logger.error("认证失败，请检查API密钥")
        elif "429" in str(error) or "rate limit" in str(error).lower():
            self.logger.error("请求频率超限，请稍后重试")
        else:
            self.logger.error("未知错误")
    
    def _validate_date_range(self, start_date: datetime, end_date: datetime) -> bool:
        """
        验证日期范围
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            bool: 日期范围是否有效
        """
        if start_date >= end_date:
            self.logger.error(f"开始日期 {start_date} 不能晚于或等于结束日期 {end_date}")
            return False
        
        # 检查日期是否过于久远
        now = datetime.now()
        if start_date < now.replace(year=now.year - 20):
            self.logger.warning(f"开始日期 {start_date} 过于久远，可能无法获取数据")
        
        return True
