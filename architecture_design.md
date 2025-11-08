# Backtrader 回测项目架构设计文档

## 项目概述

本项目旨在构建一个基于 backtrader 的量化回测框架，具有高度的可扩展性和灵活性，支持多种数据源和策略的组合使用。

## 核心需求

1. **策略自定义**：用户可以轻松定义和实现自己的交易策略
2. **多数据源适配**：支持不同类型的数据源（CSV、API、数据库等）
3. **解耦架构**：策略和数据源之间无强依赖关系
4. **灵活组合**：不同数据源可以匹配不同策略
5. **可扩展性**：易于添加新的数据源和策略类型

## 整体架构设计

### 1. 分层架构

```
┌─────────────────────────────────────────┐
│              用户接口层                   │
├─────────────────────────────────────────┤
│              业务逻辑层                   │
│  ┌─────────────┐  ┌─────────────┐        │
│  │   策略管理器  │  │   数据管理器  │        │
│  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────┤
│              适配器层                    │
│  ┌─────────────┐  ┌─────────────┐        │
│  │  策略适配器   │  │  数据适配器   │        │
│  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────┤
│              基础设施层                   │
│  ┌─────────────┐  ┌─────────────┐        │
│  │  配置管理     │  │  日志管理     │        │
│  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────┘
```

### 2. 核心组件设计

#### 2.1 数据源适配器层 (DataAdapter)

**目标接口**：`IDataTarget`
- 定义统一的数据接口标准
- 提供标准化的数据格式

**适配器实现**：
- `CSVAdapter`: CSV文件适配器
- `YahooFinanceAdapter`: Yahoo Finance API适配器
- `CoinbaseAdapter`: Coinbase API适配器
- `BinanceAdapter`: Binance API适配器
- `DatabaseAdapter`: 数据库适配器

**适配器模式优势**：
- 每个API有独立的适配器，处理其特有的数据格式和接口
- 统一的输出格式，便于策略使用
- 易于添加新的数据源API
- 各适配器相互独立，互不影响

#### 2.2 策略抽象层 (Strategy)

**抽象基类**：`BaseStrategy`
- 继承自 backtrader.Strategy
- 定义策略生命周期接口
- 提供通用工具方法

**策略类型**：
- `MomentumStrategy`: 动量策略
- `MeanReversionStrategy`: 均值回归策略
- `ArbitrageStrategy`: 套利策略
- `CustomStrategy`: 用户自定义策略

#### 2.3 回测引擎 (BacktestEngine)

**核心功能**：
- 策略与数据源的动态组合
- 回测参数配置
- 结果分析和报告生成
- 性能指标计算

#### 2.4 配置管理 (ConfigManager)

**配置类型**：
- 数据源配置
- 策略参数配置
- 回测环境配置
- 输出配置

#### 2.5 工厂模式 (Factory)

**数据源工厂**：`DataSourceFactory`
- 根据配置创建对应的数据源实例

**策略工厂**：`StrategyFactory`
- 根据配置创建对应的策略实例

## 详细设计

### 3. 目录结构

```
backtrader_framework/
├── README.md
├── requirements.txt
├── setup.py
├── config/
│   ├── __init__.py
│   ├── config.yaml
│   └── settings.py
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py              # 回测引擎
│   │   ├── base_strategy.py       # 策略基类
│   │   └── base_data_source.py    # 数据源基类
│   ├── data_adapters/
│   │   ├── __init__.py
│   │   ├── target_interface.py    # 目标接口定义
│   │   ├── csv_adapter.py         # CSV文件适配器
│   │   ├── yahoo_finance_adapter.py # Yahoo Finance API适配器
│   │   ├── coinbase_adapter.py    # Coinbase API适配器
│   │   ├── binance_adapter.py     # Binance API适配器
│   │   ├── database_adapter.py    # 数据库适配器
│   │   └── adapter_factory.py     # 适配器工厂
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── momentum_strategy.py   # 动量策略
│   │   ├── mean_reversion.py      # 均值回归策略
│   │   └── factory.py             # 策略工厂
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config_manager.py      # 配置管理
│   │   ├── logger.py              # 日志管理
│   │   └── indicators.py          # 技术指标工具
│   └── analysis/
│       ├── __init__.py
│       ├── performance.py         # 性能分析
│       └── report.py              # 报告生成
├── examples/
│   ├── basic_backtest.py          # 基础回测示例
│   ├── custom_strategy_example.py # 自定义策略示例
│   └── multi_data_example.py      # 多数据源示例
├── tests/
│   ├── __init__.py
│   ├── test_data_sources.py       # 数据源测试
│   ├── test_strategies.py         # 策略测试
│   └── test_engine.py             # 引擎测试
└── docs/
    ├── api_reference.md           # API参考文档
    └── user_guide.md              # 用户指南
```

### 4. 核心接口设计

#### 4.1 适配器模式接口设计

**目标接口 (IDataTarget)**：
```python
from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any

class IDataTarget(ABC):
    """数据适配器目标接口，定义统一的数据格式标准"""
    
    @abstractmethod
    def get_data(self, symbol: str, start_date: datetime, end_date: datetime, **kwargs) -> pd.DataFrame:
        """获取标准化数据
        Args:
            symbol: 交易对代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
        
        Returns:
            pd.DataFrame: 标准格式的数据，包含列：open, high, low, close, volume
        """
        pass
    
    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """验证交易对是否有效"""
        pass
    
    @abstractmethod
    def get_supported_intervals(self) -> list:
        """获取支持的时间间隔"""
        pass
```

**适配器基类 (BaseAdapter)**：
```python
class BaseAdapter(IDataTarget):
    """适配器基类，提供通用功能"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._rate_limiter = None
    
    def _standardize_dataframe(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """标准化数据格式为backtrader要求的格式"""
        # 统一列名和数据格式
        standard_columns = ['open', 'high', 'low', 'close', 'volume']
        # 实现数据标准化逻辑
        pass
    
    def _handle_api_error(self, error: Exception) -> None:
        """处理API错误"""
        # 统一错误处理逻辑
        pass
```

**具体适配器示例**：
```python
class YahooFinanceAdapter(BaseAdapter):
    """Yahoo Finance API适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"
    
    def get_data(self, symbol: str, start_date: datetime, end_date: datetime, **kwargs) -> pd.DataFrame:
        """从Yahoo Finance获取数据"""
        # 实现Yahoo Finance API调用
        # 处理Yahoo Finance特有的数据格式
        # 调用_standardize_dataframe进行标准化
        pass
    
    def validate_symbol(self, symbol: str) -> bool:
        """验证Yahoo Finance的交易对格式"""
        pass
    
    def get_supported_intervals(self) -> list:
        """Yahoo Finance支持的时间间隔"""
        return ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']

class CoinbaseAdapter(BaseAdapter):
    """Coinbase API适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.secret_key = config.get('secret_key')
        self.base_url = "https://api.pro.coinbase.com/"
    
    def get_data(self, symbol: str, start_date: datetime, end_date: datetime, **kwargs) -> pd.DataFrame:
        """从Coinbase获取数据"""
        # 实现Coinbase API调用
        # 处理API签名认证
        # 处理Coinbase特有的数据格式
        pass
    
    def validate_symbol(self, symbol: str) -> bool:
        """验证Coinbase的交易对格式（如：BTC-USD）"""
        pass
    
    def get_supported_intervals(self) -> list:
        """Coinbase支持的时间间隔"""
        return ['1m', '5m', '15m', '60m', '1d']

class BinanceAdapter(BaseAdapter):
    """Binance API适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.secret_key = config.get('secret_key')
        self.base_url = "https://api.binance.com/api/v3/"
    
    def get_data(self, symbol: str, start_date: datetime, end_date: datetime, **kwargs) -> pd.DataFrame:
        """从Binance获取数据"""
        # 实现Binance API调用
        # 处理Binance特有的数据格式和签名
        pass
    
    def validate_symbol(self, symbol: str) -> bool:
        """验证Binance的交易对格式（如：BTCUSDT）"""
        pass
    
    def get_supported_intervals(self) -> list:
        """Binance支持的时间间隔"""
        return ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
```

**适配器工厂**：
```python
class AdapterFactory:
    """适配器工厂，根据配置创建对应的适配器实例"""
    
    _adapters = {
        'yahoo': YahooFinanceAdapter,
        'coinbase': CoinbaseAdapter,
        'binance': BinanceAdapter,
        'csv': CSVAdapter,
        'database': DatabaseAdapter,
    }
    
    @classmethod
    def create_adapter(cls, adapter_type: str, config: Dict[str, Any]) -> IDataTarget:
        """创建适配器实例"""
        if adapter_type not in cls._adapters:
            raise ValueError(f"不支持的适配器类型: {adapter_type}")
        
        adapter_class = cls._adapters[adapter_type]
        return adapter_class(config)
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class: type):
        """注册新的适配器类型"""
        cls._adapters[name] = adapter_class
    
    @classmethod
    def get_available_adapters(cls) -> list:
        """获取所有可用的适配器类型"""
        return list(cls._adapters.keys())
```

#### 4.2 策略接口

```python
class BaseStrategy(bt.Strategy):
    @abstractmethod
    def init(self):
        """策略初始化"""
        pass
    
    @abstractmethod
    def next(self):
        """策略逻辑"""
        pass
    
    def log_data(self):
        """日志记录"""
        pass
```

#### 4.3 回测引擎接口

```python
class BacktestEngine:
    def __init__(self, config: dict):
        self.config = config
        self.data_source = None
        self.strategy = None
    
    def set_data_source(self, source_type: str, **kwargs):
        """设置数据源"""
        pass
    
    def set_strategy(self, strategy_type: str, **kwargs):
        """设置策略"""
        pass
    
    def run_backtest(self) -> BacktestResult:
        """运行回测"""
        pass
    
    def generate_report(self) -> dict:
        """生成报告"""
        pass
```

### 5. 配置文件设计

#### 5.1 安全配置管理方案

为保护API密钥等敏感信息，采用环境变量 + .env文件的方案：

```yaml
# config/config.yaml - 安全配置文件（可提交到Git）
data_adapters:
  yahoo:
    enabled: true
    timeout: 30
    rate_limit: 100  # 每分钟请求数
  
  coinbase:
    enabled: true
    api_key: "${COINBASE_API_KEY}"  # 从环境变量读取
    secret_key: "${COINBASE_SECRET_KEY}"
    timeout: 30
    rate_limit: 10
  
  binance:
    enabled: true
    api_key: "${BINANCE_API_KEY}"
    secret_key: "${BINANCE_SECRET_KEY}"
    timeout: 30
    rate_limit: 20
  
  csv:
    enabled: true
    data_path: "./data/"
    date_format: "%Y-%m-%d"
  
  database:
    enabled: false
    connection_string: "${DATABASE_URL}"

strategies:
  momentum:
    period: 20
    threshold: 0.02
  
  mean_reversion:
    lookback: 30
    std_dev: 2
  
  custom:
    parameters:
      param1: value1
      param2: value2

backtest:
  initial_cash: 100000
  commission: 0.001
  slippage: 0.0001
  start_date: "2020-01-01"
  end_date: "2023-12-31"

logging:
  level: "INFO"
  file: "./logs/backtest.log"
  max_size: "10MB"
  backup_count: 5
```

```bash
# .env - 环境变量文件（不提交到Git）
COINBASE_API_KEY=your_actual_coinbase_api_key
COINBASE_SECRET_KEY=your_actual_coinbase_secret_key
BINANCE_API_KEY=your_actual_binance_api_key
BINANCE_SECRET_KEY=your_actual_binance_secret_key
DATABASE_URL=sqlite:///market_data.db
```

```
# .gitignore - Git忽略文件
# 环境变量文件
.env
.env.local
.env.production

# 日志文件
logs/
*.log

# 数据文件
data/*.csv
data/*.json

# Python缓存
__pycache__/
*.pyc
.pytest_cache/
.coverage

# IDE文件
.vscode/
.idea/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db
```

#### 5.2 配置加载机制

```python
# src/utils/config_manager.py
import os
import yaml
from typing import Dict, Any
from dotenv import load_dotenv

class ConfigManager:
    """配置管理器，支持环境变量替换"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '../../config/config.yaml')
        
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件并进行环境变量替换"""
        # 加载环境变量
        load_dotenv()  # 从.env文件加载
        
        # 读取配置文件
        with open(self.config_path, 'r', encoding='utf-8') as f:
            raw_config = f.read()
        
        # 替换环境变量
        processed_config = self._replace_env_vars(raw_config)
        
        # 解析YAML
        self.config = yaml.safe_load(processed_config)
    
    def _replace_env_vars(self, text: str) -> str:
        """替换文本中的环境变量引用 ${VAR_NAME}"""
        import re
        
        def replace_match(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))  # 如果环境变量不存在，保持原样
        
        # 匹配 ${VAR_NAME} 格式
        pattern = r'\$\{([^}]+)\}'
        return re.sub(pattern, replace_match, text)
    
    def get(self, key: str, default=None):
        """获取配置值，支持点号分隔的嵌套键"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_adapter_config(self, adapter_name: str) -> Dict[str, Any]:
        """获取特定适配器的配置"""
        return self.get(f'data_adapters.{adapter_name}', {})
    
    def get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """获取特定策略的配置"""
        return self.get(f'strategies.{strategy_name}', {})
    
    def validate_required_env_vars(self) -> bool:
        """验证必需的环境变量是否存在"""
        required_vars = []
        
        # 检查启用的适配器的必需环境变量
        adapters = self.get('data_adapters', {})
        for name, config in adapters.items():
            if config.get('enabled', False):
                if name == 'coinbase':
                    required_vars.extend(['COINBASE_API_KEY', 'COINBASE_SECRET_KEY'])
                elif name == 'binance':
                    required_vars.extend(['BINANCE_API_KEY', 'BINANCE_SECRET_KEY'])
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"缺少必需的环境变量: {', '.join(missing_vars)}")
            return False
        
        return True
```

#### 5.3 配置使用示例

```python
from src.utils.config_manager import ConfigManager

# 加载配置
config_manager = ConfigManager()

# 验证环境变量
if not config_manager.validate_required_env_vars():
    raise ValueError("配置验证失败，请检查环境变量设置")

# 获取适配器配置
coinbase_config = config_manager.get_adapter_config('coinbase')
binance_config = config_manager.get_adapter_config('binance')

# 获取策略配置
momentum_config = config_manager.get_strategy_config('momentum')

# 获取回测配置
initial_cash = config_manager.get('backtest.initial_cash', 100000)
```

#### 5.4 开发环境配置指南

1. **首次设置**：
   ```bash
   # 复制环境变量模板
   cp .env.example .env
   
   # 编辑.env文件，填入真实的API密钥
   nano .env
   ```

2. **环境变量模板** (`.env.example`)：
   ```bash
   # Coinbase API配置
   COINBASE_API_KEY=your_coinbase_api_key_here
   COINBASE_SECRET_KEY=your_coinbase_secret_key_here
   
   # Binance API配置
   BINANCE_API_KEY=your_binance_api_key_here
   BINANCE_SECRET_KEY=your_binance_secret_key_here
   
   # 数据库配置
   DATABASE_URL=sqlite:///market_data.db
   ```

3. **生产环境**：
   - 在CI/CD系统中设置环境变量
   - 在云平台（AWS/GCP/Azure）的密钥管理服务中存储敏感信息
   - 使用Kubernetes Secrets或其他密钥管理方案

### 6. 使用示例

#### 6.1 基础使用示例

```python
from src.core.engine import BacktestEngine
from src.utils.config_manager import ConfigManager

# 加载配置
config = ConfigManager.load_config("config/config.yaml")

# 创建回测引擎
engine = BacktestEngine(config)

# 设置数据源和策略
engine.set_data_adapter("yahoo", symbol="AAPL", start_date="2020-01-01", end_date="2023-12-31")
engine.set_strategy("momentum", period=20, threshold=0.02)

# 运行回测
result = engine.run_backtest()

# 生成报告
report = engine.generate_report()
print(f"总收益率: {result.total_return:.2%}")
print(f"夏普比率: {result.sharpe_ratio:.2f}")
```

#### 6.2 多数据源对比示例

```python
from src.core.engine import BacktestEngine
from src.data_adapters.adapter_factory import AdapterFactory
from src.utils.config_manager import ConfigManager

config = ConfigManager.load_config("config/config.yaml")

# 同一策略在不同数据源上的表现
symbols = ["BTC-USD", "ETH-USD"]
adapters = ["coinbase", "binance", "yahoo"]

for symbol in symbols:
    for adapter_type in adapters:
        engine = BacktestEngine(config)
        
        # 使用不同的数据适配器
        engine.set_data_adapter(adapter_type, symbol=symbol, 
                               start_date="2023-01-01", end_date="2023-12-31")
        engine.set_strategy("mean_reversion", lookback=20, std_dev=2)
        
        result = engine.run_backtest()
        print(f"{symbol} - {adapter_type}: 收益率 {result.total_return:.2%}")
```

#### 6.3 自定义适配器示例

```python
from src.data_adapters.target_interface import IDataTarget
from src.data_adapters.base_adapter import BaseAdapter
import pandas as pd
from datetime import datetime

class CustomExchangeAdapter(BaseAdapter):
    """自定义交易所API适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_endpoint = config.get('api_endpoint')
        self.auth_token = config.get('auth_token')
    
    def get_data(self, symbol: str, start_date: datetime, end_date: datetime, **kwargs) -> pd.DataFrame:
        """从自定义交易所获取数据"""
        # 实现自定义API调用逻辑
        # 处理该交易所特有的数据格式
        raw_data = self._fetch_from_api(symbol, start_date, end_date)
        return self._standardize_dataframe(raw_data)
    
    def validate_symbol(self, symbol: str) -> bool:
        """验证交易对格式"""
        # 实现该交易所的符号验证逻辑
        return bool(symbol and '/' in symbol)
    
    def get_supported_intervals(self) -> list:
        """获取支持的时间间隔"""
        return ['1m', '5m', '15m', '1h', '1d']

# 注册自定义适配器
AdapterFactory.register_adapter('custom_exchange', CustomExchangeAdapter)

# 使用自定义适配器
custom_config = {
    'api_endpoint': 'https://api.custom-exchange.com/v1/',
    'auth_token': 'your_auth_token'
}

engine = BacktestEngine(config)
engine.set_data_adapter("custom_exchange", symbol="BTC/USDT", 
                       start_date="2023-01-01", end_date="2023-12-31")
```

#### 6.4 策略组合示例

```python
# 多策略组合回测
strategies_config = [
    {"name": "momentum", "params": {"period": 10, "threshold": 0.01}},
    {"name": "mean_reversion", "params": {"lookback": 20, "std_dev": 1.5}},
    {"name": "arbitrage", "params": {"threshold": 0.005}}
]

results = {}

for strategy_config in strategies_config:
    engine = BacktestEngine(config)
    engine.set_data_adapter("binance", symbol="BTCUSDT", 
                           start_date="2023-01-01", end_date="2023-12-31")
    engine.set_strategy(strategy_config["name"], **strategy_config["params"])
    
    result = engine.run_backtest()
    results[strategy_config["name"]] = result

# 比较不同策略的表现
for strategy_name, result in results.items():
    print(f"{strategy_name}: 收益率 {result.total_return:.2%}, "
          f"夏普比率 {result.sharpe_ratio:.2f}, "
          f"最大回撤 {result.max_drawdown:.2%}")
```

## 关键设计原则

### 7.1 依赖注入 (Dependency Injection)
- 通过工厂模式创建对象实例
- 避免硬编码依赖关系
- 便于单元测试和模块替换

### 7.2 开闭原则 (Open/Closed Principle)
- 对扩展开放：易于添加新的数据源和策略
- 对修改封闭：不需要修改现有代码即可扩展功能

### 7.3 单一职责原则 (Single Responsibility Principle)
- 每个类只负责一个特定功能
- 数据源只负责数据获取和处理
- 策略只负责交易逻辑
- 引擎只负责协调和执行

### 7.4 接口隔离原则 (Interface Segregation Principle)
- 定义细粒度的接口
- 客户端只依赖需要的接口
- 避免接口污染

## 扩展性考虑

### 8.1 插件机制
- 支持动态加载策略插件
- 支持动态加载数据源插件
- 提供插件注册和管理机制

### 8.2 并行回测
- 支持多策略并行回测
- 支持多数据源并行处理
- 利用多进程/多线程提升性能

### 8.3 实时交易
- 预留实时交易接口
- 支持模拟交易和实盘交易切换
- 提供风险控制机制

## 风险控制

### 9.1 数据质量检查
- 数据完整性验证
- 异常值检测和处理
- 数据一致性检查

### 9.2 策略风险控制
- 最大回撤限制
- 持仓集中度控制
- 止损止盈机制

### 9.3 系统稳定性
- 异常处理和错误恢复
- 日志记录和监控
- 资源使用限制

## 性能优化

### 10.1 数据处理优化
- 使用向量化操作
- 数据缓存机制
- 增量数据更新

### 10.2 内存管理
- 大数据集分块处理
- 及时释放不需要的对象
- 内存使用监控

## 测试策略

### 11.1 单元测试
- 每个模块独立测试
- 模拟数据测试
- 边界条件测试

### 11.2 集成测试
- 端到端回测流程测试
- 多数据源组合测试
- 策略组合测试

### 11.3 性能测试
- 大数据量回测测试
- 并发回测测试
- 内存使用测试

---

## 下一步计划

1. **确认架构设计**：与用户讨论并确认架构设计
2. **实现核心框架**：按照设计实现基础框架
3. **开发示例模块**：实现基本的数据源和策略示例
4. **编写测试用例**：确保代码质量和稳定性
5. **完善文档**：提供详细的使用指南和API文档

请仔细审阅以上架构设计，如有任何建议或需要调整的地方，请告诉我，我们可以进一步讨论完善。
