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
        ('min_hold_bars', 5),     # 最小持仓K线数量，防止频繁交易
        ('position_size', 0.95),  # 仓位大小比例
        ('printlog', True),       # 是否打印日志
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
        
        # 持仓管理
        self.order = None
        self.buy_bar = None  # 买入时的K线索引
        self.hold_bars = 0  # 已持仓的K线数量
        
        self.log_data(f"动量策略初始化 - 周期: {self.p.period}, 阈值: {self.p.threshold}, "
                     f"最小持仓: {self.p.min_hold_bars}根K线")
    
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
        
        # 更新持仓计数
        if current_position:
            if self.buy_bar is not None:
                self.hold_bars = len(self.data) - self.buy_bar
            else:
                # 如果有持仓但没有记录买入时间，设置当前时间
                self.buy_bar = len(self.data)
                self.hold_bars = 0
        else:
            self.buy_bar = None
            self.hold_bars = 0
        
        # 交易信号逻辑
        buy_signal = momentum_value > self.p.threshold
        sell_signal = momentum_value < -self.p.threshold
        
        # 调试信息：每10条记录输出一次
        if len(self.data) % 10 == 0:
            self.log_data(f"调试 - K线{len(self.data)}: 价格{current_price:.2f}, "
                         f"动量{momentum_value:.6f}, 阈值±{self.p.threshold}, "
                         f"持仓{'有' if current_position else '无'}, 持仓时间{self.hold_bars}")
        
        # 买入逻辑
        if buy_signal and not current_position:
            # 计算买入数量
            cash = self.broker.getcash()
            size = (cash * self.p.position_size) / current_price
            
            if size > 0:
                self.order = self.buy(size=size)
                self.log_data(f"🟢 买入信号 - 价格: {current_price:.2f}, "
                             f"动量: {momentum_value:.6f}, 数量: {size:.6f}")
        
        # 卖出逻辑 - 需要满足最小持仓时间
        elif sell_signal and current_position and self.hold_bars >= self.p.min_hold_bars:
            self.order = self.sell(size=current_position.size)
            self.log_data(f"🔴 卖出信号 - 价格: {current_price:.2f}, "
                         f"动量: {momentum_value:.6f}, 持仓{self.hold_bars}根K线, "
                         f"数量: {current_position.size:.6f}")
        
        # 持仓管理逻辑
        elif current_position and current_position.size > 0:
            # 止损逻辑：如果动量转负且满足最小持仓时间
            if momentum_value < 0 and self.hold_bars >= self.p.min_hold_bars:
                self.order = self.sell(size=current_position.size)
                self.log_data(f"⚠️ 止损卖出 - 价格: {current_price:.2f}, "
                             f"动量: {momentum_value:.6f}, 持仓{self.hold_bars}根K线, "
                             f"数量: {current_position.size:.6f}")
            
            # 止盈逻辑：如果动量过高且持有多头，全部卖出
            elif momentum_value > self.p.threshold * 3:
                # 全部卖出
                sell_size = current_position.size
                if sell_size > 0:  # 确保有足够的仓位可卖
                    self.order = self.sell(size=sell_size)
                    self.log_data(f"💰 止盈卖出 - 价格: {current_price:.2f}, "
                                 f"动量: {momentum_value:.6f}, 卖出: {sell_size:.6f}")
    
    def notify_order(self, order):
        """订单状态通知"""
        super().notify_order(order)
        
        if order.status in [order.Completed]:
            if order.isbuy():
                # 买入完成，记录买入时间
                self.buy_bar = len(self.data)
                self.hold_bars = 0
                self.log_data(f"买入完成，开始持仓计时")
            else:
                # 卖出完成，重置持仓状态
                self.buy_bar = None
                self.hold_bars = 0
                self.log_data(f"卖出完成，持仓结束")
    
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
