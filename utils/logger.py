# -*- coding: utf-8 -*-
"""
日志工具
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = 'smart_spider', level: int = None, verbose: bool = False) -> logging.Logger:
    """设置日志
    
    Args:
        name: 日志名称
        level: 日志级别
        verbose: 是否详细日志
        
    Returns:
        logging.Logger: 日志实例
    """
    if level is None:
        level = logging.DEBUG if verbose else logging.INFO
    
    # 创建日志目录
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # 日志文件名
    log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # 配置日志
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """获取日志实例
    
    Args:
        name: 模块名称，默认使用当前模块名
        
    Returns:
        logging.Logger: 日志实例
    """
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals['__name__']
    return logging.getLogger(name)