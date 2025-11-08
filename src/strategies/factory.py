"""
策略工厂

根据配置创建对应的策略实例。
"""

from typing import Dict, Any, Type
from .base_strategy import BaseStrategy
from .momentum_strategy import MomentumStrategy
from ..utils.logger import get_logger


class StrategyFactory:
    """策略工厂，根据配置创建对应的策略实例"""
    
    _strategies: Dict[str, Type[BaseStrategy]] = {
        'momentum': MomentumStrategy,
        # 未来的策略将在这里注册
        # 'mean_reversion': MeanReversionStrategy,
        # 'arbitrage': ArbitrageStrategy,
        # 'custom': CustomStrategy,
    }
    
    _logger = get_logger('StrategyFactory')
    
    @classmethod
    def create_strategy(cls, strategy_type: str, **params) -> BaseStrategy:
        """
        创建策略实例
        
        Args:
            strategy_type: 策略类型
            **params: 策略参数
            
        Returns:
            BaseStrategy: 策略实例
            
        Raises:
            ValueError: 不支持的策略类型
        """
        if strategy_type not in cls._strategies:
            available = ', '.join(cls._strategies.keys())
            error_msg = f"不支持的策略类型: {strategy_type}，可用类型: {available}"
            cls._logger.error(error_msg)
            raise ValueError(error_msg)
        
        strategy_class = cls._strategies[strategy_type]
        cls._logger.info(f"创建策略实例: {strategy_type} -> {strategy_class.__name__}")
        
        try:
            # 直接返回策略类，让backtrader处理参数
            strategy = strategy_class
            cls._logger.info(f"策略创建成功: {strategy_type}")
            return strategy
            
        except Exception as e:
            cls._logger.error(f"策略创建失败: {strategy_type}, 错误: {e}")
            raise
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[BaseStrategy]) -> None:
        """
        注册新的策略类型
        
        Args:
            name: 策略名称
            strategy_class: 策略类
        """
        cls._strategies[name] = strategy_class
        cls._logger.info(f"注册策略: {name} -> {strategy_class.__name__}")
    
    @classmethod
    def unregister_strategy(cls, name: str) -> bool:
        """
        注销策略类型
        
        Args:
            name: 策略名称
            
        Returns:
            bool: 是否成功注销
        """
        if name in cls._strategies:
            del cls._strategies[name]
            cls._logger.info(f"注销策略: {name}")
            return True
        else:
            cls._logger.warning(f"尝试注销不存在的策略: {name}")
            return False
    
    @classmethod
    def get_available_strategies(cls) -> list:
        """
        获取所有可用的策略类型
        
        Returns:
            list: 策略类型列表
        """
        return list(cls._strategies.keys())
    
    @classmethod
    def get_strategy_info(cls) -> Dict[str, Dict[str, Any]]:
        """
        获取所有策略的信息
        
        Returns:
            Dict: 策略信息字典
        """
        info = {}
        for name, strategy_class in cls._strategies.items():
            info[name] = {
                'class_name': strategy_class.__name__,
                'module': strategy_class.__module__,
                'doc': strategy_class.__doc__ or "无文档",
                'params': getattr(strategy_class, 'params', ())
            }
        return info
    
    @classmethod
    def is_strategy_available(cls, strategy_type: str) -> bool:
        """
        检查策略是否可用
        
        Args:
            strategy_type: 策略类型
            
        Returns:
            bool: 是否可用
        """
        return strategy_type in cls._strategies
    
    @classmethod
    def get_strategy_params(cls, strategy_type: str) -> tuple:
        """
        获取策略的默认参数
        
        Args:
            strategy_type: 策略类型
            
        Returns:
            tuple: 策略参数元组
        """
        if strategy_type not in cls._strategies:
            return ()
        
        strategy_class = cls._strategies[strategy_type]
        return getattr(strategy_class, 'params', ())
    
    @classmethod
    def validate_strategy_params(cls, strategy_type: str, params: Dict[str, Any]) -> bool:
        """
        验证策略参数
        
        Args:
            strategy_type: 策略类型
            params: 参数字典
            
        Returns:
            bool: 参数是否有效
        """
        if strategy_type not in cls._strategies:
            return False
        
        default_params = cls.get_strategy_params(strategy_type)
        default_param_names = [param[0] for param in default_params]
        
        # 检查是否有未知参数
        for param_name in params.keys():
            if param_name not in default_param_names:
                cls._logger.warning(f"未知参数: {param_name}")
                return False
        
        return True
