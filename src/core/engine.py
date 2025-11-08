"""
回测引擎

核心回测引擎，协调数据适配器和策略。
"""

import backtrader as bt
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
from ..utils.logger import get_logger
from ..utils.config_manager import ConfigManager
from ..data_adapters.adapter_factory import AdapterFactory
from ..strategies.factory import StrategyFactory


class BacktestResult:
    """回测结果类"""
    
    def __init__(self):
        self.total_return = 0.0
        self.sharpe_ratio = 0.0
        self.max_drawdown = 0.0
        self.total_trades = 0
        self.win_rate = 0.0
        self.final_value = 0.0
        self.start_value = 0.0


class BacktestEngine:
    """回测引擎
    
    负责协调数据适配器和策略，执行回测
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            # 使用默认配置
            config_manager = ConfigManager()
            config = config_manager.config
        
        self.config = config
        self.logger = get_logger('BacktestEngine')
        
        # 初始化组件
        self.data_adapter = None
        self.strategy = None
        self.cerebro = None
        
        # 回测结果
        self.result = BacktestResult()
        
        self.logger.info("回测引擎初始化完成")
    
    def set_data_adapter(self, adapter_type: str, **kwargs) -> None:
        """
        设置数据适配器
        
        Args:
            adapter_type: 适配器类型
            **kwargs: 适配器参数
        """
        try:
            # 获取适配器配置
            adapter_config = self.config.get('data_adapters', {}).get(adapter_type, {})
            adapter_config.update(kwargs)
            
            # 创建适配器实例
            self.data_adapter = AdapterFactory.create_adapter(adapter_type, adapter_config)
            self.logger.info(f"数据适配器设置成功: {adapter_type}")
            
        except Exception as e:
            self.logger.error(f"数据适配器设置失败: {e}")
            raise
    
    def set_strategy(self, strategy_type: str, **params) -> None:
        """
        设置策略
        
        Args:
            strategy_type: 策略类型
            **params: 策略参数
        """
        try:
            # 获取策略配置
            strategy_config = self.config.get('strategies', {}).get(strategy_type, {})
            strategy_config.update(params)
            
            # 创建策略类
            strategy_class = StrategyFactory.create_strategy(strategy_type)
            
            # 存储策略类和参数
            self.strategy = strategy_class
            self.strategy_params = strategy_config
            
            self.logger.info(f"策略设置成功: {strategy_type}")
            
        except Exception as e:
            self.logger.error(f"策略设置失败: {e}")
            raise
    
    def setup_cerebro(self) -> None:
        """设置Cerebro引擎"""
        self.cerebro = bt.Cerebro()
        
        # 添加策略
        if self.strategy:
            strategy_params = getattr(self, 'strategy_params', {})
            self.cerebro.addstrategy(self.strategy, **strategy_params)
            self.logger.info(f"策略已添加到Cerebro，参数: {strategy_params}")
        else:
            self.logger.warning("未设置策略")
        
        # 设置初始资金
        initial_cash = self.config.get('backtest', {}).get('initial_cash', 100000)
        self.cerebro.broker.setcash(initial_cash)
        self.logger.info(f"初始资金设置: {initial_cash}")
        
        # 设置手续费
        commission = self.config.get('backtest', {}).get('commission', 0.001)
        self.cerebro.broker.setcommission(commission=commission)
        self.logger.info(f"手续费设置: {commission}")
        
        # 设置滑点
        slippage = self.config.get('backtest', {}).get('slippage', 0.0001)
        # cerebro的slippage设置需要特殊处理
        self.cerebro.broker.set_slippage_perc(slippage * 100)
        self.logger.info(f"滑点设置: {slippage}")
        
        # 添加分析器
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        self.logger.info("Cerebro引擎设置完成")
    
    def load_data(self, symbol: str, start_date: datetime, end_date: datetime, **kwargs) -> None:
        """
        加载数据
        
        Args:
            symbol: 交易对代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
        """
        if not self.data_adapter:
            raise ValueError("未设置数据适配器")
        
        # 确保Cerebro已初始化
        if not self.cerebro:
            self.setup_cerebro()
        
        try:
            # 获取数据
            data_df = self.data_adapter.get_data(symbol, start_date, end_date, **kwargs)
            self.logger.info(f"数据加载成功: {len(data_df)} 条记录")
            
            # 转换为backtrader数据格式
            data = bt.feeds.PandasData(
                dataname=data_df,
                fromdate=start_date,
                todate=end_date,
                name=symbol
            )
            
            # 添加到Cerebro
            self.cerebro.adddata(data)
            self.logger.info(f"数据已添加到Cerebro: {symbol}")
            
        except Exception as e:
            self.logger.error(f"数据加载失败: {e}")
            raise
    
    def run_backtest(self) -> BacktestResult:
        """
        运行回测
        
        Returns:
            BacktestResult: 回测结果
        """
        if not self.cerebro:
            self.setup_cerebro()
        
        try:
            self.logger.info("开始运行回测")
            
            # 记录初始值
            start_value = self.cerebro.broker.getvalue()
            self.result.start_value = start_value
            
            # 运行回测
            strategies = self.cerebro.run()
            
            # 记录最终值
            final_value = self.cerebro.broker.getvalue()
            self.result.final_value = final_value
            
            # 计算收益率
            self.result.total_return = (final_value - start_value) / start_value
            
            # 提取分析结果
            if strategies and len(strategies) > 0:
                strategy = strategies[0]
                
                # 获取分析器结果
                if hasattr(strategy.analyzers, 'sharpe'):
                    sharpe = strategy.analyzers.sharpe.get_analysis()
                    self.result.sharpe_ratio = sharpe.get('sharperatio', 0.0)
                
                if hasattr(strategy.analyzers, 'drawdown'):
                    drawdown = strategy.analyzers.drawdown.get_analysis()
                    self.result.max_drawdown = drawdown.get('max', {}).get('drawdown', 0.0)
                
                if hasattr(strategy.analyzers, 'trades'):
                    trades = strategy.analyzers.trades.get_analysis()
                    total_trades = trades.get('total', {}).get('closed', 0)
                    won_trades = trades.get('won', {}).get('total', 0)
                    
                    self.result.total_trades = total_trades
                    if total_trades > 0:
                        self.result.win_rate = (won_trades / total_trades) * 100
            
            self.logger.info("回测运行完成")
            self.logger.info(f"总收益率: {self.result.total_return:.2%}")
            self.logger.info(f"夏普比率: {self.result.sharpe_ratio:.2f}")
            self.logger.info(f"最大回撤: {self.result.max_drawdown:.2%}")
            self.logger.info(f"总交易次数: {self.result.total_trades}")
            self.logger.info(f"胜率: {self.result.win_rate:.1f}%")
            
            return self.result
            
        except Exception as e:
            self.logger.error(f"回测运行失败: {e}")
            raise
    
    def generate_report(self) -> Dict[str, Any]:
        """
        生成回测报告
        
        Returns:
            Dict[str, Any]: 报告数据
        """
        if not self.result or self.result.final_value == 0:
            self.logger.warning("没有可用的回测结果")
            return {}
        
        report = {
            'summary': {
                'start_value': self.result.start_value,
                'final_value': self.result.final_value,
                'total_return': f"{self.result.total_return:.2%}",
                'sharpe_ratio': f"{self.result.sharpe_ratio:.2f}",
                'max_drawdown': f"{self.result.max_drawdown:.2%}",
                'total_trades': self.result.total_trades,
                'win_rate': f"{self.result.win_rate:.1f}%"
            },
            'performance': {
                'annual_return': f"{self.result.total_return * 252:.2%}",  # 假设年化
                'monthly_return': f"{self.result.total_return * 21:.2%}",  # 假设月化
                'daily_return': f"{self.result.total_return / 252:.2%}"
            },
            'risk_metrics': {
                'max_drawdown': f"{self.result.max_drawdown:.2%}",
                'sharpe_ratio': f"{self.result.sharpe_ratio:.2f}",
                'volatility': 'N/A'  # 需要额外计算
            }
        }
        
        self.logger.info("回测报告生成完成")
        return report
    
    def plot_results(self, show: bool = True, save_path: str = None) -> None:
        """
        绘制回测结果
        
        Args:
            show: 是否显示图表
            save_path: 保存路径
        """
        if not self.cerebro:
            self.logger.warning("没有可用的回测结果")
            return
        
        try:
            # 设置图表样式
            plt.style.use('seaborn-v0_8')
            
            # 绘制图表
            fig = self.cerebro.plot(style='candlestick', 
                                 barup='green', 
                                 bardown='red',
                                 volume=True,
                                 figsize=(15, 8))
            
            if save_path:
                fig[0][0].savefig(save_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"图表已保存: {save_path}")
            
            if show:
                import matplotlib.pyplot as plt
                plt.show()
            
        except Exception as e:
            self.logger.error(f"图表绘制失败: {e}")
    
    def get_strategy_instance(self):
        """获取策略实例"""
        return self.strategy
    
    def reset(self) -> None:
        """重置引擎状态"""
        self.data_adapter = None
        self.strategy = None
        self.cerebro = None
        self.result = BacktestResult()
        self.logger.info("回测引擎已重置")
