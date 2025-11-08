"""
配置管理器

支持环境变量替换和安全配置加载。
"""

import os
import yaml
import re
from typing import Dict, Any
from dotenv import load_dotenv
from .logger import get_logger


class ConfigManager:
    """配置管理器，支持环境变量替换"""
    
    def __init__(self, config_path: str = None):
        self.logger = get_logger('ConfigManager')
        
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '../../config/config.yaml')
        
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件并进行环境变量替换"""
        try:
            # 加载环境变量
            load_dotenv()  # 从.env文件加载
            self.logger.info("环境变量加载完成")
            
            # 读取配置文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw_config = f.read()
            
            # 替换环境变量
            processed_config = self._replace_env_vars(raw_config)
            
            # 解析YAML
            self.config = yaml.safe_load(processed_config)
            self.logger.info(f"配置文件加载成功: {self.config_path}")
            
        except FileNotFoundError:
            self.logger.error(f"配置文件未找到: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"YAML解析错误: {e}")
            raise
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            raise
    
    def _replace_env_vars(self, text: str) -> str:
        """替换文本中的环境变量引用 ${VAR_NAME}"""
        def replace_match(match):
            var_name = match.group(1)
            env_value = os.getenv(var_name)
            if env_value is None:
                self.logger.warning(f"环境变量未设置: {var_name}")
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
        config = self.get(f'data_adapters.{adapter_name}', {})
        if not config:
            self.logger.warning(f"适配器配置未找到: {adapter_name}")
        return config
    
    def get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """获取特定策略的配置"""
        config = self.get(f'strategies.{strategy_name}', {})
        if not config:
            self.logger.warning(f"策略配置未找到: {strategy_name}")
        return config
    
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
                elif name == 'yahoo':
                    # Yahoo Finance通常不需要API密钥
                    pass
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            self.logger.error(f"缺少必需的环境变量: {', '.join(missing_vars)}")
            return False
        
        self.logger.info("所有必需的环境变量都已设置")
        return True
