"""
Backtrader 回测框架

一个基于 backtrader 的量化回测框架，支持多种数据源和策略的灵活组合。
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.engine import BacktestEngine
from .utils.config_manager import ConfigManager
from .data_adapters.adapter_factory import AdapterFactory

__all__ = [
    'BacktestEngine',
    'ConfigManager', 
    'AdapterFactory'
]
