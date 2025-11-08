"""
数据适配器模块

包含各种数据源的适配器实现。
"""

from .target_interface import IDataTarget
from .base_adapter import BaseAdapter
from .mock_adapter import MockAdapter
from .adapter_factory import AdapterFactory

__all__ = [
    'IDataTarget',
    'BaseAdapter',
    'MockAdapter',
    'AdapterFactory'
]
