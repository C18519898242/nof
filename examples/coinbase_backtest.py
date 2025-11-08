"""
Coinbase数据适配器示例

演示如何使用Coinbase适配器进行回测
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.engine import BacktestEngine
from src.utils.logger import get_logger
from src.utils.config_manager import ConfigManager


def main():
    """主函数"""
    logger = get_logger('coinbase_example')
    logger.info("开始Coinbase回测示例")
    
    try:
        # 创建回测引擎
        engine = BacktestEngine()
        
        # 设置Coinbase数据适配器
        engine.set_data_adapter('coinbase')
        
        # 设置策略
        engine.set_strategy('momentum', period=15, threshold=0.02)
        
        # 设置时间范围（最近30天）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # 获取数据并运行回测
        logger.info(f"回测时间范围: {start_date.date()} 到 {end_date.date()}")
        
        # 使用BTC-USD交易对
        engine.load_data('BTC-USD', start_date, end_date, granularity='hour')
        
        # 运行回测
        result = engine.run_backtest()
        
        # 生成报告
        report = engine.generate_report()
        
        # 打印结果
        print("\n" + "="*50)
        print("Coinbase回测结果")
        print("="*50)
        
        summary = report.get('summary', {})
        print(f"初始资金: ${summary.get('start_value', '0')}")
        print(f"最终资金: ${summary.get('final_value', '0')}")
        print(f"总收益率: {summary.get('total_return', '0%')}")
        print(f"夏普比率: {summary.get('sharpe_ratio', '0.00')}")
        print(f"最大回撤: {summary.get('max_drawdown', '0%')}")
        print(f"总交易次数: {summary.get('total_trades', 0)}")
        print(f"胜率: {summary.get('win_rate', '0%')}")
        
        print("\n" + "="*50)
        print("性能指标")
        print("="*50)
        
        performance = report.get('performance', {})
        print(f"年化收益率: {performance.get('annual_return', '0%')}")
        print(f"月化收益率: {performance.get('monthly_return', '0%')}")
        print(f"日收益率: {performance.get('daily_return', '0%')}")
        
        print("\n" + "="*50)
        print("风险指标")
        print("="*50)
        
        risk_metrics = report.get('risk_metrics', {})
        print(f"最大回撤: {risk_metrics.get('max_drawdown', '0%')}")
        print(f"夏普比率: {risk_metrics.get('sharpe_ratio', '0.00')}")
        print(f"波动率: {risk_metrics.get('volatility', 'N/A')}")
        
        logger.info("Coinbase回测示例完成")
        
    except Exception as e:
        logger.error(f"Coinbase回测示例失败: {e}")
        print(f"\n错误: {e}")
        print("\n提示:")
        print("1. 确保已设置COINBASE_API_KEY和COINBASE_SECRET_KEY环境变量")
        print("2. 检查网络连接")
        print("3. 验证交易对符号格式（例如: BTC-USD, ETH-USD）")
        return 1
    
    return 0


def test_adapter_info():
    """测试适配器信息"""
    logger = get_logger('adapter_test')
    
    try:
        from src.data_adapters.adapter_factory import AdapterFactory
        
        # 测试获取可用适配器
        adapters = AdapterFactory.get_available_adapters()
        logger.info(f"可用适配器: {adapters}")
        
        # 测试获取适配器信息
        adapter_info = AdapterFactory.get_adapter_info()
        logger.info(f"适配器信息: {adapter_info}")
        
        # 创建Coinbase适配器实例
        config = {
            'api_key': 'test_key',
            'api_secret': 'test_secret',
            'sandbox': True
        }
        
        adapter = AdapterFactory.create_adapter('coinbase', config)
        info = adapter.get_adapter_info()
        
        print("\n" + "="*50)
        print("Coinbase适配器信息")
        print("="*50)
        print(f"名称: {info['name']}")
        print(f"版本: {info['version']}")
        print(f"描述: {info['description']}")
        print(f"支持时间框架: {', '.join(info['supported_timeframes'])}")
        print(f"需要认证: {info['requires_auth']}")
        print(f"支持沙盒: {info['sandbox_supported']}")
        print(f"速率限制: {info['rate_limits']}")
        
        # 测试交易对验证
        test_symbols = ['BTC-USD', 'ETH-USD', 'INVALID']
        for symbol in test_symbols:
            is_valid = adapter.validate_symbol(symbol)
            print(f"交易对 {symbol}: {'有效' if is_valid else '无效'}")
        
        # 测试获取可用交易对
        try:
            available_symbols = adapter.get_available_symbols()
            print(f"\n可用交易对数量: {len(available_symbols)}")
            print("前10个交易对:", available_symbols[:10])
        except Exception as e:
            print(f"获取交易对列表失败: {e}")
        
    except Exception as e:
        logger.error(f"适配器测试失败: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    print("选择操作:")
    print("1. 运行Coinbase回测示例")
    print("2. 测试适配器信息")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == '1':
        exit(main())
    elif choice == '2':
        exit(test_adapter_info())
    else:
        print("无效选择")
        exit(1)
