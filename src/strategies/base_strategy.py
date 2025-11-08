"""
策略基类

继承自backtrader.Strategy的基类，提供通用功能。
"""

import backtrader as bt
from ..utils.logger import get_logger


class BaseStrategy(bt.Strategy):
    """策略基类，继承自backtrader.Strategy"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
        
        # 策略状态
        self._position_open = False
        self._entry_price = None
        self._last_order = None
        
        # 性能统计
        self._trades_count = 0
        self._winning_trades = 0
        self._losing_trades = 0
    
    def log_data(self, msg: str, level: str = "INFO"):
        """
        记录策略日志
        
        Args:
            msg: 日志消息
            level: 日志级别
        """
        log_msg = f"[{self.datas[0]._name}] {msg}"
        
        if level.upper() == "DEBUG":
            self.logger.debug(log_msg)
        elif level.upper() == "INFO":
            self.logger.info(log_msg)
        elif level.upper() == "WARNING":
            self.logger.warning(log_msg)
        elif level.upper() == "ERROR":
            self.logger.error(log_msg)
        else:
            self.logger.info(log_msg)
    
    def notify_order(self, order):
        """
        订单状态通知
        
        Args:
            order: 订单对象
        """
        if order.status in [order.Submitted, order.Accepted]:
            if order.isbuy():
                self.log_data(f"买单提交/接受: {order.size} @ {order.price}")
            else:
                self.log_data(f"卖单提交/接受: {order.size} @ {order.price}")
        
        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log_data(f"买单成交: {order.size} @ {order.price}")
                self._position_open = True
                self._entry_price = order.price
            else:
                self.log_data(f"卖单成交: {order.size} @ {order.price}")
                self._position_open = False
                self._entry_price = None
                
            # 更新交易统计
            self._trades_count += 1
            # 这里可以添加盈亏统计逻辑
            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if order.isbuy():
                self.log_data(f"买单取消/拒绝: {order.size} @ {order.price}", "WARNING")
            else:
                self.log_data(f"卖单取消/拒绝: {order.size} @ {order.price}", "WARNING")
        
        self._last_order = order
    
    def notify_trade(self, trade):
        """
        交易通知
        
        Args:
            trade: 交易对象
        """
        if not trade.isclosed:
            return
        
        if trade.pnl > 0:
            self.log_data(f"盈利交易: {trade.pnl:.2f}")
            self._winning_trades += 1
        else:
            self.log_data(f"亏损交易: {trade.pnl:.2f}")
            self._losing_trades += 1
        
        self.log_data(f"交易统计 - 总计: {self._trades_count}, "
                     f"盈利: {self._winning_trades}, 亏损: {self._losing_trades}")
    
    def notify_data(self, data, status, *args, **kwargs):
        """
        数据状态通知
        
        Args:
            data: 数据对象
            status: 状态
            *args: 其他参数
            **kwargs: 其他关键字参数
        """
        if status == data.LIVE:
            self.log_data(f"数据开始更新: {data._name}")
        elif status == data.DELAYED:
            self.log_data(f"数据延迟: {data._name}", "WARNING")
        elif status == data.DISCONNECTED:
            self.log_data(f"数据断开: {data._name}", "ERROR")
    
    def get_position_info(self) -> dict:
        """
        获取当前持仓信息
        
        Returns:
            dict: 持仓信息
        """
        if not self.position:
            return {
                'size': 0,
                'price': 0,
                'value': 0,
                'pnl': 0,
                'pnl_comm': 0
            }
        
        return {
            'size': self.position.size,
            'price': self.position.price,
            'value': self.position.value,
            'pnl': self.position.pnl,
            'pnl_comm': self.position.pnlcomm
        }
    
    def get_account_info(self) -> dict:
        """
        获取账户信息
        
        Returns:
            dict: 账户信息
        """
        try:
            return {
                'cash': self.broker.getcash(),
                'value': self.broker.getvalue(),
                'leverage': getattr(self.broker, 'getleverage', lambda: 1)(),
                'margin': getattr(self.broker, 'getmargin', lambda: 0)(),
                'margin_free': getattr(self.broker, 'getmarginavailable', lambda: 0)()
            }
        except Exception as e:
            self.log_data(f"获取账户信息失败: {e}", "WARNING")
            return {
                'cash': self.broker.getcash(),
                'value': self.broker.getvalue(),
                'leverage': 1,
                'margin': 0,
                'margin_free': 0
            }
    
    def get_performance_stats(self) -> dict:
        """
        获取策略性能统计
        
        Returns:
            dict: 性能统计
        """
        win_rate = 0
        if self._trades_count > 0:
            win_rate = (self._winning_trades / self._trades_count) * 100
        
        return {
            'total_trades': self._trades_count,
            'winning_trades': self._winning_trades,
            'losing_trades': self._losing_trades,
            'win_rate': win_rate,
            'is_position_open': self._position_open,
            'entry_price': self._entry_price
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self._trades_count = 0
        self._winning_trades = 0
        self._losing_trades = 0
        self._position_open = False
        self._entry_price = None
        self._last_order = None
        self.log_data("统计信息已重置")
