"""
数据适配器测试用例
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_adapters.adapter_factory import AdapterFactory
from src.data_adapters.mock_adapter import MockAdapter


class TestAdapters(unittest.TestCase):
    """数据适配器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.factory = AdapterFactory()
    
    def test_get_available_adapters(self):
        """测试获取可用适配器列表"""
        adapters = self.factory.get_available_adapters()
        self.assertIsInstance(adapters, list)
        self.assertIn('mock', adapters)
        self.assertIn('binance', adapters)
        self.assertIn('coinbase', adapters)
    
    def test_get_adapter_info(self):
        """测试获取适配器信息"""
        info = self.factory.get_adapter_info()
        self.assertIsInstance(info, dict)
        self.assertIn('mock', info)
        self.assertIn('binance', info)
        self.assertIn('coinbase', info)
    
    def test_create_mock_adapter(self):
        """测试创建模拟适配器"""
        adapter = self.factory.create_adapter('mock', {})
        self.assertIsInstance(adapter, MockAdapter)
        
        # 测试获取模拟数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        df = adapter.get_data('BTCUSDT', start_date, end_date)
        self.assertFalse(df.empty)
        self.assertIn('open', df.columns)
        self.assertIn('high', df.columns)
        self.assertIn('low', df.columns)
        self.assertIn('close', df.columns)
        self.assertIn('volume', df.columns)
    
    def test_mock_adapter_validation(self):
        """测试模拟适配器验证功能"""
        adapter = MockAdapter()
        
        # 测试交易对验证 - MockAdapter接受任何非空符号
        self.assertTrue(adapter.validate_symbol('BTCUSDT'))
        self.assertTrue(adapter.validate_symbol('ETHUSDT'))
        self.assertTrue(adapter.validate_symbol('INVALID'))  # Mock适配器接受任何符号
        self.assertFalse(adapter.validate_symbol(''))  # 空字符串应该失败
        self.assertFalse(adapter.validate_symbol(None))  # None应该失败
        
        # 测试支持的时间间隔
        supported_intervals = adapter.get_supported_intervals()
        self.assertIn('1m', supported_intervals)
        self.assertIn('1h', supported_intervals)
        self.assertIn('1d', supported_intervals)
    
    def test_adapter_features(self):
        """测试适配器功能"""
        adapter = MockAdapter()
        
        # 测试获取支持的交易对
        symbols = adapter.get_available_symbols()
        self.assertIsInstance(symbols, list)
        self.assertIn('BTCUSDT', symbols)
        self.assertIn('ETHUSDT', symbols)
        
        # 测试获取支持的时间间隔
        intervals = adapter.get_supported_intervals()
        self.assertIsInstance(intervals, list)
        self.assertIn('1m', intervals)
        self.assertIn('1h', intervals)
        self.assertIn('1d', intervals)


if __name__ == '__main__':
    unittest.main()
