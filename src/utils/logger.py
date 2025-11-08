"""
日志管理器

提供类似Java Logback的日志功能，支持同时输出到控制台和文件。
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


class Logger:
    """日志管理器，支持控制台和文件输出"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str, level: str = "INFO", 
                  log_file: Optional[str] = None, 
                  max_bytes: int = 10*1024*1024,  # 10MB
                  backup_count: int = 5) -> logging.Logger:
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: 日志文件路径，如果为None则不写入文件
            max_bytes: 日志文件最大字节数
            backup_count: 备份文件数量
            
        Returns:
            logging.Logger: 配置好的日志记录器
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 创建格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, level.upper()))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            # 文件处理器（如果指定了日志文件）
            if log_file:
                # 确保日志目录存在
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(getattr(logging, level.upper()))
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def setup_default_logger(cls, config: dict = None) -> logging.Logger:
        """
        设置默认日志记录器
        
        Args:
            config: 日志配置字典，包含level, file, max_size, backup_count等
            
        Returns:
            logging.Logger: 默认日志记录器
        """
        if config is None:
            config = {
                'level': 'INFO',
                'file': './logs/backtest.log',
                'max_size': '10MB',
                'backup_count': 5
            }
        
        # 解析文件大小
        max_size = 10 * 1024 * 1024  # 默认10MB
        if 'max_size' in config:
            size_str = config['max_size'].upper()
            if size_str.endswith('KB'):
                max_size = int(size_str[:-2]) * 1024
            elif size_str.endswith('MB'):
                max_size = int(size_str[:-2]) * 1024 * 1024
            elif size_str.endswith('GB'):
                max_size = int(size_str[:-2]) * 1024 * 1024 * 1024
        
        return cls.get_logger(
            name='backtrader_framework',
            level=config.get('level', 'INFO'),
            log_file=config.get('file'),
            max_bytes=max_size,
            backup_count=config.get('backup_count', 5)
        )


# 便捷函数
def get_logger(name: str = 'backtrader_framework') -> logging.Logger:
    """获取日志记录器的便捷函数"""
    return Logger.get_logger(name)


def setup_logging(config: dict = None) -> logging.Logger:
    """设置日志的便捷函数"""
    return Logger.setup_default_logger(config)
