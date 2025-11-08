"""
适配器工厂

根据配置创建对应的适配器实例。
"""

from typing import Dict, Any, Type
from .target_interface import IDataTarget
from .mock_adapter import MockAdapter
from .coinbase_adapter import CoinbaseAdapter
from .binance_adapter import BinanceAdapter
from ..utils.logger import get_logger


class AdapterFactory:
    """适配器工厂，根据配置创建对应的适配器实例"""
    
    _adapters: Dict[str, Type[IDataTarget]] = {
        'mock': MockAdapter,
        'coinbase': CoinbaseAdapter,
        'binance': BinanceAdapter,
        # 未来的适配器将在这里注册
        # 'csv': CSVAdapter,
        # 'yahoo': YahooFinanceAdapter,
        # 'database': DatabaseAdapter,
    }
    
    _logger = get_logger('AdapterFactory')
    
    @classmethod
    def create_adapter(cls, adapter_type: str, config: Dict[str, Any]) -> IDataTarget:
        """
        创建适配器实例
        
        Args:
            adapter_type: 适配器类型
            config: 适配器配置
            
        Returns:
            IDataTarget: 适配器实例
            
        Raises:
            ValueError: 不支持的适配器类型
        """
        if adapter_type not in cls._adapters:
            available = ', '.join(cls._adapters.keys())
            error_msg = f"不支持的适配器类型: {adapter_type}，可用类型: {available}"
            cls._logger.error(error_msg)
            raise ValueError(error_msg)
        
        adapter_class = cls._adapters[adapter_type]
        cls._logger.info(f"创建适配器实例: {adapter_type} -> {adapter_class.__name__}")
        
        try:
            adapter = adapter_class(config)
            cls._logger.info(f"适配器创建成功: {adapter_type}")
            return adapter
        except Exception as e:
            cls._logger.error(f"适配器创建失败: {adapter_type}, 错误: {e}")
            raise
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class: Type[IDataTarget]) -> None:
        """
        注册新的适配器类型
        
        Args:
            name: 适配器名称
            adapter_class: 适配器类
        """
        cls._adapters[name] = adapter_class
        cls._logger.info(f"注册适配器: {name} -> {adapter_class.__name__}")
    
    @classmethod
    def unregister_adapter(cls, name: str) -> bool:
        """
        注销适配器类型
        
        Args:
            name: 适配器名称
            
        Returns:
            bool: 是否成功注销
        """
        if name in cls._adapters:
            del cls._adapters[name]
            cls._logger.info(f"注销适配器: {name}")
            return True
        else:
            cls._logger.warning(f"尝试注销不存在的适配器: {name}")
            return False
    
    @classmethod
    def get_available_adapters(cls) -> list:
        """
        获取所有可用的适配器类型
        
        Returns:
            list: 适配器类型列表
        """
        return list(cls._adapters.keys())
    
    @classmethod
    def get_adapter_info(cls) -> Dict[str, Dict[str, Any]]:
        """
        获取所有适配器的信息
        
        Returns:
            Dict: 适配器信息字典
        """
        info = {}
        for name, adapter_class in cls._adapters.items():
            info[name] = {
                'class_name': adapter_class.__name__,
                'module': adapter_class.__module__,
                'doc': adapter_class.__doc__ or "无文档"
            }
        return info
    
    @classmethod
    def is_adapter_available(cls, adapter_type: str) -> bool:
        """
        检查适配器是否可用
        
        Args:
            adapter_type: 适配器类型
            
        Returns:
            bool: 是否可用
        """
        return adapter_type in cls._adapters
