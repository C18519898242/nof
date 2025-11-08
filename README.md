# Backtrader 回测框架

一个基于 backtrader 的量化回测框架，支持多种数据源和策略的灵活组合。

## 项目特点

- 🏗️ **优雅架构**: 采用适配器模式，数据源和策略完全解耦
- 🔌 **插件化设计**: 支持动态注册新的数据适配器和策略
- 🔧 **配置驱动**: 支持YAML配置文件和环境变量
- 📊 **丰富指标**: 内置多种性能分析和风险指标
- 📝 **完整日志**: 支持多级别日志，同时输出到控制台和文件
- 🔒 **安全配置**: 敏感信息通过环境变量管理，支持.env文件

## 项目结构

```
nof/
├── src/                          # 源代码目录
│   ├── core/                     # 核心模块
│   │   ├── engine.py            # 回测引擎
│   │   ├── base_strategy.py     # 策略基类
│   │   └── base_data_source.py  # 数据源基类
│   ├── data_adapters/            # 数据适配器
│   │   ├── target_interface.py  # 目标接口
│   │   ├── base_adapter.py      # 适配器基类
│   │   ├── mock_adapter.py      # Mock适配器（示例）
│   │   └── adapter_factory.py   # 适配器工厂
│   ├── strategies/               # 策略实现
│   │   ├── base_strategy.py     # 策略基类
│   │   ├── momentum_strategy.py # 动量策略（示例）
│   │   └── factory.py           # 策略工厂
│   ├── analysis/                 # 分析模块
│   │   ├── performance.py       # 性能分析
│   │   └── report.py            # 报告生成
│   └── utils/                    # 工具模块
│       ├── config_manager.py    # 配置管理
│       └── logger.py            # 日志管理
├── config/                       # 配置文件
│   └── config.yaml              # 主配置文件
├── examples/                     # 示例代码
│   └── basic_backtest.py        # 基础回测示例
├── tests/                        # 测试代码
├── docs/                         # 文档
├── logs/                         # 日志目录
├── data/                         # 数据目录
└── requirements.txt              # 依赖包列表
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd nof

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

创建 `.env` 文件（可选，用于敏感信息）：

```bash
# Coinbase配置
COINBASE_API_KEY=your_coinbase_api_key
COINBASE_SECRET_KEY=your_coinbase_secret_key

# Binance配置
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 3. 运行示例

```bash
# 运行基础回测示例
python examples/basic_backtest.py
```

## 使用指南

### 基本用法

```python
from src.core.engine import BacktestEngine
from src.utils.config_manager import ConfigManager
from datetime import datetime, timedelta

# 创建回测引擎
config_manager = ConfigManager()
engine = BacktestEngine(config_manager.config)

# 设置数据适配器
engine.set_data_adapter('mock')

# 设置策略
engine.set_strategy('momentum', period=20, threshold=0.02)

# 设置时间范围
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

# 加载数据并运行回测
engine.load_data('AAPL', start_date, end_date)
result = engine.run_backtest()

# 生成报告
report = engine.generate_report()
print(report)
```

### 自定义策略

```python
from src.strategies.base_strategy import BaseStrategy
import backtrader as bt

class MyStrategy(BaseStrategy):
    params = (
        ('period', 20),
    )
    
    def __init__(self):
        super().__init__()
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.period)
    
    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.sell()

# 注册策略
from src.strategies.factory import StrategyFactory
StrategyFactory.register_strategy('my_strategy', MyStrategy)

# 使用自定义策略
engine.set_strategy('my_strategy', period=15)
```

### 自定义数据适配器

```python
from src.data_adapters.base_adapter import BaseAdapter
import pandas as pd

class MyAdapter(BaseAdapter):
    def get_data(self, symbol, start_date, end_date, **kwargs):
        # 实现数据获取逻辑
        data = pd.DataFrame(...)  # 你的数据
        return self._standardize_dataframe(data)
    
    def validate_symbol(self, symbol):
        return True
    
    def get_supported_intervals(self):
        return ['1d', '1h']

# 注册适配器
from src.data_adapters.adapter_factory import AdapterFactory
AdapterFactory.register_adapter('my_adapter', MyAdapter)

# 使用自定义适配器
engine.set_data_adapter('my_adapter')
```

## 配置说明

### 主配置文件 (config/config.yaml)

```yaml
# 数据适配器配置
data_adapters:
  mock:
    enabled: true
  coinbase:
    enabled: false
    api_key: "${COINBASE_API_KEY}"
    secret_key: "${COINBASE_SECRET_KEY}"

# 策略配置
strategies:
  momentum:
    period: 20
    threshold: 0.02

# 回测配置
backtest:
  initial_cash: 100000
  commission: 0.001
  slippage: 0.0001

# 日志配置
logging:
  level: "INFO"
  file: "./logs/backtest.log"
  max_size: "10MB"
  backup_count: 5
```

### 环境变量支持

配置文件支持 `${VAR_NAME}` 格式的环境变量替换：

```yaml
coinbase:
  api_key: "${COINBASE_API_KEY}"  # 将从环境变量中读取
```

## 核心组件

### 1. 回测引擎 (BacktestEngine)
- 协调数据适配器和策略
- 管理回测生命周期
- 提供结果分析和报告

### 2. 数据适配器 (Data Adapters)
- 统一的数据接口
- 支持多种数据源
- 自动数据标准化

### 3. 策略工厂 (Strategy Factory)
- 策略的创建和管理
- 支持动态注册
- 参数验证

### 4. 配置管理 (Config Manager)
- YAML配置文件支持
- 环境变量替换
- 配置验证

### 5. 日志系统 (Logger)
- 多级别日志
- 文件和控制台双输出
- 日志轮转支持

## 扩展开发

### 添加新数据源

1. 继承 `BaseAdapter` 类
2. 实现必要的方法
3. 注册到 `AdapterFactory`

### 添加新策略

1. 继承 `BaseStrategy` 类
2. 实现交易逻辑
3. 注册到 `StrategyFactory`

### 添加新分析器

1. 在 `analysis` 模块中实现
2. 集成到 `BacktestEngine`
3. 更新报告格式

## 最佳实践

1. **数据安全**: 敏感信息使用环境变量
2. **错误处理**: 适当使用try-catch和日志
3. **性能优化**: 注意数据加载和处理效率
4. **测试覆盖**: 为新功能编写测试
5. **文档更新**: 及时更新相关文档

## 常见问题

### Q: 如何添加新的数据源？
A: 继承 `BaseAdapter` 并实现必要方法，然后注册到工厂。

### Q: 策略如何传递参数？
A: 通过配置文件或在 `set_strategy` 方法中传递参数。

### Q: 如何处理大量数据？
A: 使用分批加载和缓存机制，避免内存溢出。

### Q: 如何自定义报告格式？
A: 修改 `analysis/report.py` 中的报告生成逻辑。

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 文档: [Documentation]
