# -*- coding: utf-8 -*-
"""
爬虫工厂 - 根据配置创建相应的爬虫实例
"""

from .base_spider import SpiderConfig
from .api_spider import ApiSpider
from .browser_spider import BrowserSpider
from .concurrent_spider import ConcurrentBrowserSpider
from utils.logger import get_logger

logger = get_logger(__name__)


class SpiderFactory:
    """爬虫工厂类"""
    
    @staticmethod
    def create_spider(config_path: str):
        """根据配置文件创建爬虫实例
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            BaseSpider: 爬虫实例
            
        Raises:
            ValueError: 配置错误
            FileNotFoundError: 配置文件不存在
        """
        try:
            # 加载配置
            config = SpiderConfig.from_json(config_path)
            
            logger.info(f"创建爬虫: {config.name} (模式: {config.mode})")
            
            # 根据模式创建相应的爬虫
            if config.mode == 'api':
                return ApiSpider(config)
            elif config.mode == 'browser':
                # 如果配置了并发数大于1，使用并发爬虫
                if getattr(config, 'concurrent', 1) > 1:
                    return ConcurrentBrowserSpider(config)
                else:
                    return BrowserSpider(config)
            else:
                raise ValueError(f"不支持的爬虫模式: {config.mode}")
                
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {config_path}")
            raise
        except Exception as e:
            logger.error(f"创建爬虫失败: {e}")
            raise