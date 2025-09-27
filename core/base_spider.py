# -*- coding: utf-8 -*-
"""
基础爬虫类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
import json
from pathlib import Path


@dataclass
class SpiderConfig:
    """爬虫配置数据类"""
    name: str
    mode: str  # 'api' or 'browser'
    base_url: str
    headers: Optional[Dict] = None
    params: Optional[Dict] = None
    cookies_file: Optional[str] = None
    list_page: Optional[Dict] = None
    detail_page: Optional[Dict] = None
    pagination: Optional[Dict] = None
    delay: float = 1.0
    timeout: int = 30
    max_pages: int = 10
    max_total_items: int = 0  # 最大数据总量，0表示不限制
    proxy: Optional[str] = None
    user_agent: Optional[str] = None
    concurrent: int = 1  # 并发线程数
    retry_times: int = 3  # 重试次数
    custom_pagination: Optional[Dict] = None  # 自定义分页配置
    filters: Optional[Dict] = None  # 数据过滤配置
    output_format: str = 'json'  # 输出格式：json, csv, xlsx
    output_path: Optional[str] = None  # 输出路径

    @classmethod
    def from_json(cls, json_path: str) -> 'SpiderConfig':
        """从JSON文件加载配置"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)


class BaseSpider(ABC):
    """基础爬虫类"""
    
    def __init__(self, config: SpiderConfig):
        self.config = config
        self.results: List[Dict] = []
    
    @abstractmethod
    def crawl(self) -> List[Dict]:
        """执行爬取"""
        pass
    
    def validate_config(self) -> bool:
        """验证配置"""
        required_fields = ['name', 'mode', 'base_url']
        for field in required_fields:
            if not getattr(self.config, field):
                raise ValueError(f"缺少必需配置项: {field}")
        return True