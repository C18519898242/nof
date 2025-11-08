# 用户使用指南

## 目录
1. [快速开始](#快速开始)
2. [数据适配器](#数据适配器)
3. [策略开发](#策略开发)
4. [回测引擎](#回测引擎)
5. [配置管理](#配置管理)
6. [示例代码](#示例代码)

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 基本使用

```python
from src.core.engine import BacktestEngine
from datetime import datetime, timedelta

# 创建回测引擎
engine = BacktestEngine()

# 设置数据适配器
engine.set_data_adapter('mock')

# 设置策略
engine.set_strategy('momentum', period=15, threshold=0.02)

# 设置时间范围
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

# 加载数据
engine.load_data('BTCUSDT', start_date, end_date)

# 运行回测
result = engine.run_backtest()

# 生成报告
report = engine.generate_report()
print(report)
```

## 数据适配器

### 可用适配器

#### 1. Mock适配器
用于测试和开发，生成模拟数据。

```python
engine.set_data_adapter('mock')
```

#### 2. 币安适配器
连接币安API获取真实数据。

```python
# 使用代理（推荐）
engine.set_data_adapter('binance', 
    proxy='127.0.0.1:1008',
    testnet=True  # 使用测试网
)

# 使用API密钥
engine.set_data_adapter('binance',
    api_key='your_api_key',
    secret_key='your_secret_key'
)
```

#### 3. Coinbase适配器
连接Coinbase API获取数据。

```python
engine.set_data_adapter('coinbase',
    api_key='your_api_key',
    secret_key='your_secret_key'
)
```

### 配置文件设置

在 `config/config.yaml` 中配置适配器：

```yaml
data_adapters:
  binance:
    api_key: ${BINANCE_API_KEY}
    secret_key: ${BINANCE_SECRET_KEY}
    testnet: false
    proxy: "127.0.0.1:1008"
    rate_limit_delay: 0.1
  
  coinbase:
    api_key: ${COINBASE_API_KEY}
    secret_key: ${COINBASE_SECRET_KEY}
    sandbox: true
```

## 策略开发

### 内置策略

#### 动量策略

```python
engine.set_strategy('momentum', 
    period=15,      # 动量计算周期
    threshold=0.02,  # 交易阈值
    position_size=0.1 # 仓位大小
)
```

### 自定义策略

1. 继承BaseStrategy类：

```python
from src.strategies.base_strategy import BaseStrategy
import backtrader as bt

class MyStrategy(BaseStrategy):
    params = (
        ('period', 20),
        ('threshold', 0.02),
    )
    
    def __init__(self):
        super().__init__()
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.period
        )
    
    def next(self):
        if not self.position:
            if self.data.close > self.sma:
                self.buy(size=self.calculate_position_size())
        else:
            if self.data.close < self.sma:
                self.sell(size=self.position.size)
```

2. 注册策略：

```python
from src.strategies.factory import StrategyFactory

StrategyFactory.register_strategy('my_strategy', MyStrategy)
```

3. 使用策略：

```python
engine.set_strategy('my_strategy', period=20, threshold=0.02)
```

## 回测引擎

### 基本配置

```python
from src.core.engine import BacktestEngine

# 自定义配置
config = {
    'backtest': {
        'initial_cash': 100000,
        'commission': 0.001,
        'slippage': 0.0001
    }
}

engine = BacktestEngine(config)
```

### 运行回测

```python
# 加载数据
engine.load_data('BTCUSDT', start_date, end_date, interval='1h')

# 运行回测
result = engine.run_backtest()

# 获取结果
print(f"总收益率: {result.total_return:.2%}")
print(f"夏普比率: {result.sharpe_ratio:.2f}")
print(f"最大回撤: {result.max_drawdown:.2%}")
print(f"胜率: {result.win_rate:.1f}%")
```

### 生成报告

```python
# 详细报告
report = engine.generate_report()

# 打印摘要
summary = report['summary']
print(f"初始资金: ${summary['start_value']}")
print(f"最终资金: ${summary['final_value']}")
print(f"总收益率: {summary['total_return']}")
print(f"夏普比率: {summary['sharpe_ratio']}")
print(f"最大回撤: {summary['max_drawdown']}")
print(f"总交易次数: {summary['total_trades']}")
print(f"胜率: {summary['win_rate']}")
```

### 绘制图表

```python
# 显示图表
engine.plot_results(show=True)

# 保存图表
engine.plot_results(save_path='backtest_results.png')
```

## 配置管理

### 环境变量

创建 `.env` 文件：

```bash
# 币安API
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key

# Coinbase API
COINBASE_API_KEY=your_coinbase_api_key
COINBASE_SECRET_KEY=your_coinbase_secret_key

# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/backtest
```

### 配置文件结构

```yaml
# config/config.yaml
app:
  name: "Backtest Framework"
  version: "1.0.0"
  debug: false

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

backtest:
  initial_cash: 100000
  commission: 0.001
  slippage: 0.0001

data_adapters:
  mock:
    enabled: true
  
  binance:
    api_key: ${BINANCE_API_KEY}
    secret_key: ${BINANCE_SECRET_KEY}
    testnet: false
    proxy: ""
    rate_limit_delay: 0.1

strategies:
  momentum:
    period: 15
    threshold: 0.02
    position_size: 0.1
```

## 示例代码

### 完整回测示例

```python
import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.engine import BacktestEngine

def main():
    """完整回测示例"""
    
    # 创建引擎
    engine = BacktestEngine()
    
    # 设置币安适配器
    engine.set_data_adapter('binance', 
        proxy='127.0.0.1:1008',
        testnet=True
    )
    
    # 设置动量策略
    engine.set_strategy('momentum', 
        period=15, 
        threshold=0.02
    )
    
    # 设置时间范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    try:
        # 加载数据
        engine.load_data('BTCUSDT', start_date, end_date, interval='1h')
        
        # 运行回测
        result = engine.run_backtest()
        
        # 生成报告
        report = engine.generate_report()
        
        # 打印结果
        print("=" * 50)
        print("回测结果")
        print("=" * 50)
        
        summary = report.get('summary', {})
        print(f"初始资金: ${summary.get('start_value', '0')}")
        print(f"最终资金: ${summary.get('final_value', '0')}")
        print(f"总收益率: {summary.get('total_return', '0%')}")
        print(f"夏普比率: {summary.get('sharpe_ratio', '0.00')}")
        print(f"最大回撤: {summary.get('max_drawdown', '0%')}")
        print(f"总交易次数: {summary.get('total_trades', 0)}")
        print(f"胜率: {summary.get('win_rate', '0%')}")
        
        # 显示图表
        engine.plot_results(show=True)
        
    except Exception as e:
        print(f"回测失败: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
```

### 多数据源对比

```python
from src.core.engine import BacktestEngine

def compare_data_sources():
    """对比不同数据源"""
    
    symbols = ['BTCUSDT']
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    
    sources = ['mock', 'binance']
    
    for source in sources:
        print(f"\n=== {source.upper()} 数据源 ===")
        
        engine = BacktestEngine()
        engine.set_data_adapter(source)
        engine.set_strategy('momentum', period=10, threshold=0.01)
        
        try:
            engine.load_data('BTCUSDT', start_date, end_date)
            result = engine.run_backtest()
            report = engine.generate_report()
            
            summary = report['summary']
            print(f"收益率: {summary['total_return']}")
            print(f"夏普比率: {summary['sharpe_ratio']}")
            print(f"最大回撤: {summary['max_drawdown']}")
            
        except Exception as e:
            print(f"错误: {e}")

if __name__ == '__main__':
    compare_data_sources()
```

## 常见问题

### Q: 如何添加新的数据适配器？

A: 1. 继承BaseAdapter类 2. 实现必要方法 3. 在AdapterFactory中注册

### Q: 如何优化策略参数？

A: 1. 使用网格搜索 2. 实现参数优化器 3. 考虑交叉验证

### Q: 如何处理大量数据？

A: 1. 使用数据分批加载 2. 实现数据缓存 3. 考虑使用数据库

### Q: 如何实时交易？

A: 当前版本专注于回测，实时交易功能在开发中

## 扩展开发

### 添加新功能

1. **新指标**: 在analysis模块中添加技术指标
2. **新策略**: 继承BaseStrategy类实现
3. **新适配器**: 继承BaseAdapter类实现
4. **新分析器**: 扩展回测结果分析

### 贡献指南

1. Fork项目
2. 创建功能分支
3. 编写测试用例
4. 提交Pull Request

## 联系支持

- 文档: `docs/` 目录
- 示例: `examples/` 目录
- 测试: `tests/` 目录
- 配置: `config/` 目录
