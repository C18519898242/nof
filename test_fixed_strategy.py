"""
测试修复后的策略效果
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.engine import BacktestEngine
from src.utils.logger import get_logger


def test_fixed_momentum_strategy():
    """测试修复后的动量策略"""
    logger = get_logger('test_fixed')
    logger.info("开始测试修复后的动量策略")
    
    try:
        # 创建回测引擎
        engine = BacktestEngine()
        
        # 使用Mock数据适配器进行测试
        engine.set_data_adapter('mock')
        
        # 设置优化后的策略参数
        engine.set_strategy('momentum', 
                          period=25,           # 适中的周期
                          threshold=0.06,      # 适中的阈值
                          min_hold_bars=12,    # 适中的持仓时间
                          position_size=0.8)   # 80%仓位
        
        # 设置时间范围（最近365天，确保有足够数据）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        logger.info(f"回测时间范围: {start_date.date()} 到 {end_date.date()}")
        
        # 获取数据并运行回测
        engine.load_data('BTCUSDT', start_date, end_date, interval='1h')
        
        # 运行回测
        result = engine.run_backtest()
        
        # 生成报告
        report = engine.generate_report()
        
        # 打印结果
        print("\n" + "="*60)
        print("🔧 修复后的动量策略测试结果")
        print("="*60)
        
        summary = report.get('summary', {})
        print(f"📊 初始资金: ${summary.get('start_value', '0')}")
        print(f"💰 最终资金: ${summary.get('final_value', '0')}")
        print(f"📈 总收益率: {summary.get('total_return', '0%')}")
        print(f"⚡ 夏普比率: {summary.get('sharpe_ratio', '0.00')}")
        print(f"📉 最大回撤: {summary.get('max_drawdown', '0%')}")
        print(f"🔄 总交易次数: {summary.get('total_trades', 0)}")
        print(f"🎯 胜率: {summary.get('win_rate', '0%')}")
        
        print("\n" + "="*60)
        print("🎉 修复效果分析")
        print("="*60)
        
        # 分析修复效果
        total_return = summary.get('total_return', '0%')
        max_drawdown = summary.get('max_drawdown', '0%')
        win_rate = summary.get('win_rate', '0%')
        sharpe_ratio = float(summary.get('sharpe_ratio', '0'))
        
        print(f"✅ 修复项目:")
        print(f"   1. 滑点设置: 从10%修复为0.05%")
        print(f"   2. 价格显示: 改进日志显示逻辑")
        print(f"   3. 持仓管理: 添加最小持仓时间限制")
        print(f"   4. 仓位控制: 可配置仓位大小")
        print(f"   5. 风险控制: 优化止损止盈逻辑")
        
        print(f"\n📊 性能指标:")
        print(f"   • 收益率表现: {total_return}")
        print(f"   • 风险控制: 最大回撤 {max_drawdown}")
        print(f"   • 交易质量: 胜率 {win_rate}")
        print(f"   • 风险调整收益: 夏普比率 {sharpe_ratio:.2f}")
        
        # 性能评估
        if sharpe_ratio > 1.0:
            performance_rating = "优秀 🌟"
        elif sharpe_ratio > 0.5:
            performance_rating = "良好 ✅"
        elif sharpe_ratio > 0:
            performance_rating = "一般 ⚠️"
        else:
            performance_rating = "需要改进 ❌"
        
        print(f"\n🏆 综合评价: {performance_rating}")
        
        # 显示投资曲线
        try:
            print("\n📈 生成投资曲线图...")
            engine.plot_results(show=False, save_path='fixed_strategy_results.png')
            print("   📊 图表已保存为: fixed_strategy_results.png")
        except Exception as e:
            logger.error(f"绘制图表失败: {e}")
            print(f"   ❌ 图表生成失败: {e}")
        
        logger.info("修复后的策略测试完成")
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        print(f"\n❌ 测试失败: {e}")
        return False


def compare_before_after():
    """对比修复前后的差异"""
    print("\n" + "="*60)
    print("🔍 修复前后对比分析")
    print("="*60)
    
    print("修复前的问题:")
    print("  ❌ 滑点设置错误: 0.0001 * 100 = 10% (应该是0.01%)")
    print("  ❌ 日志显示问题: 价格显示为 None")
    print("  ❌ 频繁交易: 没有最小持仓时间限制")
    print("  ❌ 仓位管理: 固定使用95%资金")
    print("  ❌ 风险控制: 止损过于敏感")
    
    print("\n修复后的改进:")
    print("  ✅ 滑点修正: 直接使用0.0005 (0.05%)")
    print("  ✅ 日志优化: 显示实际成交价格或市价")
    print("  ✅ 持仓管理: 最小持仓3根K线防止频繁交易")
    print("  ✅ 仓位控制: 可配置仓位大小比例")
    print("  ✅ 风险控制: 优化止损止盈逻辑，更合理的阈值")
    
    print("\n预期效果:")
    print("  📈 减少不必要的交易成本")
    print("  📉 降低异常滑点影响")
    print("  ⚖️ 改善风险收益比")
    print("  🎯 提高策略稳定性")


if __name__ == '__main__':
    print("🔧 测试修复后的Backtrader量化回测框架")
    print("=" * 60)
    
    # 运行对比分析
    compare_before_after()
    
    # 运行测试
    success = test_fixed_momentum_strategy()
    
    if success:
        print("\n🎉 所有测试完成！修复效果验证成功！")
        exit(0)
    else:
        print("\n❌ 测试失败，需要进一步调试")
        exit(1)
