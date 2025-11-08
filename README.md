# Backtest Framework

基于Backtrader的量化回测框架，支持多数据源和自定义策略。

## 特性

- 🔄 **多数据源支持**: 支持Mock、币安、Coinbase等数据源
- 🎯 **策略解耦**: 策略与数据源完全解耦，可自由组合
- 🔧 **配置驱动**: 通过配置文件管理所有参数
- 📊 **可视化回测**: 内置图表展示和报告生成
- 🧪 **易于测试**: 完整的测试用例和模拟数据
- 🔐 **安全配置**: 支持环境变量和配置文件的安全管理

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd nof

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

复制环境变量模板：
```bash
cp .env.example .env
# 编辑 .env 文件，添加你的API密钥
```

### 3. 运行示例

```bash
# 运行基础回测示例
python examples/basic_backtest.py

# 运行币安回测示例（需要代理）
python examples/binance_backtest.py

# 运行Coinbase回测示例
python examples/coinbase_backtest.py
```

## 项目结构

```
nof/
├── src/                          # 源代码目录
│   ├── core/                     # 核心引擎
│   │   ├── __init__.py
│   │   └── engine.py             # 回测引擎
│   ├── data_adapters/            # 数据适配器
│   │   ├── __init__.py
│   │   ├── base_adapter.py       # 适配器基类
│   │   ├── mock_adapter.py       # 模拟数据适配器
│   │   ├── binance_adapter.py    # 币安适配器
│   │   ├── coinbase_adapter.py   # Coinbase适配器
│   │   ├── adapter_factory.py    # 适配器工厂
│   │   └── target_interface.py   # 目标接口定义
│   ├── strategies/                # 策略模块
│   │   ├── __init__.py
│   │   ├── base_strategy.py      # 策略基类
│   │   ├── momentum_strategy.py  # 动量策略
│   │   └── factory.py            # 策略工厂
│   ├── utils/                     # 工具模块
│   │   ├── __init__.py
│   │   ├── logger.py             # 日志工具
│   │   └── config_manager.py     # 配置管理
│   └── analysis/                  # 分析模块
│       └── __init__.py
├── examples/                     # 示例代码
│   ├── basic_backtest.py         # 基础回测示例
│   ├── binance_backtest.py       # 币安回测示例
│   └── coinbase_backtest.py      # Coinbase回测示例
├── config/                       # 配置文件
│   └── config.yaml              # 主配置文件
├── tests/                        # 测试代码
│   └── test_adapters.py         # 适配器测试
├── docs/                         # 文档
│   └── user_guide.md             # 用户指南
├── requirements.txt              # 依赖包列表
├── .env.example                 # 环境变量模板
└── README.md                    # 项目说明
```

## 使用示例

### 基本用法

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

# 绘制图表
engine.plot_results(show=True)
```

### 使用真实数据

```python
# 使用币安数据（需要代理）
engine.set_data_adapter('binance', proxy='127.0.0.1:1008', testnet=True)

# 使用Coinbase数据
engine.set_data_adapter('coinbase', api_key='your_key', secret_key='your_secret')
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
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.period)
    
    def next(self):
        if not self.position:
            if self.data.close > self.sma:
                self.buy(size=self.calculate_position_size())
        else:
            if self.data.close < self.sma:
                self.sell(size=self.position.size)

# 注册策略
from src.strategies.factory import StrategyFactory
StrategyFactory.register_strategy('my_strategy', MyStrategy)

# 使用策略
engine.set_strategy('my_strategy', period=20)
```

## 架构设计

### 核心原则

1. **松耦合**: 策略与数据源完全解耦，可自由组合
2. **可扩展**: 易于添加新的数据源和策略
3. **配置驱动**: 通过配置文件管理所有参数
4. **测试友好**: 内置模拟数据和完整测试用例

### 组件关系

```
BacktestEngine (回测引擎)
    ├── DataAdapter (数据适配器)
    │   ├── MockAdapter (模拟数据)
    │   ├── BinanceAdapter (币安数据)
    │   └── CoinbaseAdapter (Coinbase数据)
    └── Strategy (策略)
        ├── MomentumStrategy (动量策略)
        └── CustomStrategy (自定义策略)
```

## 配置管理

### 环境变量

创建 `.env` 文件：

```bash
# API密钥
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
COINBASE_API_KEY=your_coinbase_api_key
COINBASE_SECRET_KEY=your_coinbase_secret_key

# 数据库（可选）
DATABASE_URL=postgresql://user:password@localhost:5432/backtest
```

### 配置文件

在 `config/config.yaml` 中配置：

```yaml
app:
  name: "Backtest Framework"
  version: "1.0.0"

backtest:
  initial_cash: 100000
  commission: 0.001
  slippage: 0.0001

data_adapters:
  binance:
    testnet: false
    proxy: "127.0.0.1:1008"
  coinbase:
    sandbox: true

strategies:
  momentum:
    period: 15
    threshold: 0.02
```

## 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_adapters.py -v
```

## 数据源说明

### 1. Mock适配器
- **用途**: 测试和开发
- **特点**: 生成模拟OHLCV数据
- **配置**: 无需额外配置

### 2. 币安适配器
- **用途**: 获取币安真实数据
- **特点**: 支持现货和期货数据
- **配置**: 需要API密钥或代理

### 3. Coinbase适配器
- **用途**: 获取Coinbase数据
- **特点**: 支持多种交易对
- **配置**: 需要API密钥

## 策略开发

### 内置策略

1. **动量策略**: 基于价格动量的交易策略
2. **扩展策略**: 持续添加中

### 自定义策略

1. 继承 `BaseStrategy` 类
2. 实现策略逻辑
3. 在 `StrategyFactory` 中注册
4. 配置参数和使用

## 实际运行示例

### Mock数据回测结果

```
==================================================
回测结果
==================================================
初始资金: $100000.00
最终资金: $98567.23
总收益率: -1.43%
夏普比率: -0.15
最大回撤: 2.34%
总交易次数: 45
胜率: 42.2%
```

### 币安数据回测结果

```
==================================================
币安回测结果
==================================================
初始资金: $100000.00
最终资金: $52073.88
总收益率: -47.93%
夏普比率: -0.21
最大回撤: 49.23%
总交易次数: 82
胜率: 26.8%
```

## 扩展开发

### 添加新数据源

1. 继承 `BaseAdapter` 类
2. 实现必要方法：
   - `get_data()`: 获取数据
   - `validate_symbol()`: 验证交易对
   - `get_supported_intervals()`: 获取支持的时间间隔
3. 在 `AdapterFactory` 中注册

### 添加新策略

1. 继承 `BaseStrategy` 类
2. 实现交易逻辑：
   - `next()`: 主要交易逻辑
   - `notify_order()`: 订单通知
   - `notify_trade()`: 交易通知
3. 在 `StrategyFactory` 中注册

## 常见问题

### Q: 如何添加新的数据适配器？

A: 1. 继承BaseAdapter类 2. 实现必要方法 3. 在AdapterFactory中注册

### Q: 如何优化策略参数？

A: 1. 使用网格搜索 2. 实现参数优化器 3. 考虑交叉验证

### Q: 如何处理大量数据？

A: 1. 使用数据分批加载 2. 实现数据缓存 3. 考虑使用数据库

### Q: 如何实时交易？

A: 当前版本专注于回测，实时交易功能在开发中

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 文档

- [用户指南](docs/user_guide.md) - 详细使用说明
- [架构设计](architecture_design.md) - 系统架构文档
- [示例代码](examples/) - 各种使用示例

## 更新日志

### v1.0.0
- 初始版本发布
- 支持Mock、币安、Coinbase数据源
- 实现动量策略
- 完整的配置管理系统
- 测试用例和文档
- 投资曲线可视化功能

## 联系方式

- 项目主页: [GitHub Repository]
- 文档: [Documentation]
- 问题反馈: [Issues]
