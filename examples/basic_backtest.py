"""
基础回测示例

演示如何使用回测框架进行基本的回测。
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.engine import BacktestEngine
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logging


def main():
    """主函数"""
    # 设置日志
    logging_config = {
        'level': 'INFO',
        'file': './logs/example_backtest.log'
    }
    logger = setup_logging(logging_config)
    logger.info("开始基础回测示例")
    
    try:
        # 加载配置
        config_manager = ConfigManager()
        
        # 创建回测引擎
        engine = BacktestEngine(config_manager.config)
        
        # 设置数据适配器（使用Mock适配器进行演示）
        engine.set_data_adapter('mock')
        
        # 设置策略
        engine.set_strategy('momentum', period=15, threshold=0.03)
        
        # 设置回测时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # 最近一年的数据
        
        # 加载数据
        engine.load_data('AAPL', start_date, end_date)
        
        # 运行回测
        result = engine.run_backtest()
        
        # 生成报告
        report = engine.generate_report()
        
        # 打印结果
        print("\n" + "="*50)
        print("回测结果")
        print("="*50)
        
        summary = report.get('summary', {})
        print(f"初始资金: ${summary.get('start_value', '0.00')}")
        print(f"最终资金: ${summary.get('final_value', '0.00')}")
        print(f"总收益率: {summary.get('total_return', '0.00%')}")
        print(f"夏普比率: {summary.get('sharpe_ratio', '0.00')}")
        print(f"最大回撤: {summary.get('max_drawdown', '0.00%')}")
        print(f"总交易次数: {summary.get('total_trades', 0)}")
        print(f"胜率: {summary.get('win_rate', '0.00%')}")
        
        print("\n" + "="*50)
        print("性能指标")
        print("="*50)
        
        performance = report.get('performance', {})
        print(f"年化收益率: {performance.get('annual_return', '0.00%')}")
        print(f"月化收益率: {performance.get('monthly_return', '0.00%')}")
        print(f"日收益率: {performance.get('daily_return', '0.00%')}")
        
        print("\n" + "="*50)
        print("风险指标")
        print("="*50)
        
        risk_metrics = report.get('risk_metrics', {})
        print(f"最大回撤: {risk_metrics.get('max_drawdown', '0.00%')}")
        print(f"夏普比率: {risk_metrics.get('sharpe_ratio', '0.00')}")
        print(f"波动率: {risk_metrics.get('volatility', 'N/A')}")
        
        logger.info("基础回测示例完成")
        
    except Exception as e:
        logger.error(f"回测示例失败: {e}")
        print(f"错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
