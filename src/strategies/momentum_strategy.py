"""
动量策略

基于价格动量的交易策略。
"""

import backtrader as bt
import backtrader.indicators as btind
from .base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """动量策略
    
    当价格上涨时买入，下跌时卖出
    """
    
    params = (
        ('period', 20),           # 动量计算周期
        ('threshold', 0.02),       # 动量阈值
        ('printlog', True),         # 是否打印日志
    )
    
    def __init__(self):
        super().__init__()
        
        # 动量指标
        self.momentum = btind.SimpleMovingAverage(
            self.data.close, period=self.p.period
        )
        
        # 价格变化率
        self.rate_change = btind.PercentChange(
            self.data.close, period=self.p.period
        )
        
        self.log_data(f"动量策略初始化 - 周期: {self.p.period}, 阈值: {self.p.threshold}")
    
    def next(self):
        """
        策略主要逻辑
        """
        # 确保有足够的数据
        if len(self.data) < self.p.period + 1:
            return
        
        current_price = self.data.close[0]
        momentum_value = self.rate_change[0]
        
        # 获取当前持仓
        current_position = self.getposition()
        
        # 交易信号逻辑
        buy_signal = momentum_value > self.p.threshold
        sell_signal = momentum_value < -self.p.threshold
        
        # 买入逻辑
        if buy_signal and not current_position:
            # 计算买入数量
            cash = self.broker.getcash()
            size = (cash * 0.95) / current_price  # 使用95%的资金
            
            if size > 0:
                self.buy(size=size)
                self.log_data(f"买入信号 - 价格: {current_price:.2f}, "
                             f"动量: {momentum_value:.4f}, 数量: {size:.2f}")
        
        # 卖出逻辑
        elif sell_signal and current_position:
            self.sell(size=current_position.size)
            self.log_data(f"卖出信号 - 价格: {current_price:.2f}, "
                         f"动量: {momentum_value:.4f}, 数量: {current_position.size:.2f}")
        
        # 持仓管理逻辑
        elif current_position:
            # 止损逻辑：如果动量转负且持有多头，卖出
            if momentum_value < 0 and current_position.size > 0:
                self.sell(size=current_position.size)
                self.log_data(f"止损卖出 - 价格: {current_price:.2f}, "
                             f"动量: {momentum_value:.4f}")
            
            # 止盈逻辑：如果动量过高且持有多头，部分获利了结
            elif momentum_value > self.p.threshold * 2 and current_position.size > 0:
                # 卖出一半仓位
                sell_size = current_position.size * 0.5
                self.sell(size=sell_size)
                self.log_data(f"部分止盈 - 价格: {current_price:.2f}, "
                             f"动量: {momentum_value:.4f}, 卖出: {sell_size:.2f}")
    
    def stop(self):
        """
        策略结束时的处理
        """
        self.log_data("动量策略结束")
        
        # 输出最终统计
        stats = self.get_performance_stats()
        self.log_data(f"最终统计 - 总交易: {stats['total_trades']}, "
                     f"胜率: {stats['win_rate']:.1f}%")
        
        # 输出账户信息
        account = self.get_account_info()
        self.log_data(f"账户信息 - 现金: {account['cash']:.2f}, "
                     f"总价值: {account['value']:.2f}")
