# -*- coding: utf-8 -*-
"""
爬虫管理器 - 支持多项目同时运行
"""

import os
import json
import time
import concurrent.futures
from typing import Dict, List, Optional
from pathlib import Path
import threading

from .base_spider import SpiderConfig
from .spider_factory import SpiderFactory
from utils.logger import get_logger

logger = get_logger(__name__)


class SpiderManager:
    """爬虫管理器类"""

    def __init__(self, config_dir: str = "configs", output_dir: str = "output"):
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.running_spiders = {}
        self.results = {}

    def list_configs(self) -> List[str]:
        """列出所有配置文件"""
        configs = []
        for file in self.config_dir.glob("*.json"):
            configs.append(file.stem)
        return configs

    def run_single_spider(self, config_name: str, save_results: bool = True) -> Dict:
        """运行单个爬虫"""
        try:
            config_path = self.config_dir / f"{config_name}.json"
            if not config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {config_path}")

            logger.info(f"开始运行爬虫: {config_name}")
            spider = SpiderFactory.create_spider(str(config_path))

            # 设置输出路径
            if not spider.config.output_path:
                spider.config.output_path = str(self.output_dir / f"{config_name}_{int(time.time())}")

            # 运行爬虫
            results = spider.crawl()

            # 保存结果
            if save_results:
                self._save_results(results, spider.config)

            logger.info(f"爬虫 {config_name} 完成，共获取 {len(results)} 条数据")

            return {
                "config_name": config_name,
                "status": "success",
                "data_count": len(results),
                "results": results,
                "output_path": spider.config.output_path
            }

        except Exception as e:
            logger.error(f"爬虫 {config_name} 运行失败: {e}")
            return {
                "config_name": config_name,
                "status": "failed",
                "error": str(e),
                "data_count": 0,
                "results": []
            }

    def run_multiple_spiders(self, config_names: List[str], max_workers: int = 3,
                           save_results: bool = True) -> Dict[str, Dict]:
        """并行运行多个爬虫"""
        logger.info(f"开始并行运行 {len(config_names)} 个爬虫")

        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_config = {
                executor.submit(self.run_single_spider, config_name, save_results): config_name
                for config_name in config_names
            }

            for future in concurrent.futures.as_completed(future_to_config):
                config_name = future_to_config[future]
                try:
                    result = future.result()
                    results[config_name] = result
                except Exception as e:
                    logger.error(f"爬虫 {config_name} 运行时异常: {e}")
                    results[config_name] = {
                        "config_name": config_name,
                        "status": "failed",
                        "error": str(e),
                        "data_count": 0,
                        "results": []
                    }

        logger.info(f"所有爬虫运行完成")
        return results

    def run_all_spiders(self, save_results: bool = True) -> Dict[str, Dict]:
        """运行所有配置的爬虫"""
        configs = self.list_configs()
        if not configs:
            logger.warning("未找到任何配置文件")
            return {}

        return self.run_multiple_spiders(configs, save_results=save_results)

    def create_config_template(self, name: str, template_type: str = "jd") -> str:
        """创建配置文件模板"""
        templates = {
            "jd": {
                "name": name,
                "mode": "browser",
                "base_url": "https://search.jd.com/Search?keyword=iPhone16&enc=utf-8",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "delay": 2.0,
                "timeout": 30,
                "max_pages": 20,
                "max_total_items": 200,
                "concurrent": 3,
                "list_page": {
                    "item_selector": "#J_goodsList .gl-item",
                    "wait_selector": ".gl-item",
                    "fields": [
                        {"name": "title", "selector": ".p-name a em", "attribute": "text"},
                        {"name": "price", "selector": ".p-price .J_price", "attribute": "text"},
                        {"name": "shop", "selector": ".p-shop a", "attribute": "text"},
                        {"name": "url", "selector": ".p-name a", "attribute": "href"},
                        {"name": "image", "selector": ".p-img img", "attribute": "src"}
                    ]
                },
                "detail_page": {
                    "enabled": True,
                    "url_field": "url",
                    "fields": [
                        {"name": "brand", "selector": ".parameter2 li:contains('品牌')", "attribute": "text"},
                        {"name": "model", "selector": ".parameter2 li:contains('型号')", "attribute": "text"},
                        {"name": "color", "selector": ".parameter2 li:contains('颜色')", "attribute": "text"},
                        {"name": "storage", "selector": ".parameter2 li:contains('存储容量')", "attribute": "text"},
                        {"name": "screen_size", "selector": ".parameter2 li:contains('屏幕尺寸')", "attribute": "text"},
                        {"name": "description", "selector": ".detail", "attribute": "text"}
                    ]
                },
                "pagination": {
                    "type": "url",
                    "param": "page"
                },
                "custom_pagination": {
                    "type": "dynamic_scroll"
                },
                "output_format": "json",
                "output_path": f"output/{name}.json"
            },
            "xiaohongshu": {
                "name": name,
                "mode": "browser",
                "base_url": "https://www.xiaohongshu.com/search_result",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "delay": 3.0,
                "timeout": 30,
                "max_pages": 10,
                "max_total_items": 100,
                "concurrent": 1,
                "list_page": {
                    "item_selector": ".note-item",
                    "wait_selector": ".note-item",
                    "fields": [
                        {"name": "title", "selector": ".title", "attribute": "text"},
                        {"name": "author", "selector": ".author", "attribute": "text"},
                        {"name": "likes", "selector": ".like", "attribute": "text"},
                        {"name": "url", "selector": "a", "attribute": "href"}
                    ]
                },
                "detail_page": {
                    "enabled": True,
                    "url_field": "url",
                    "fields": [
                        {"name": "content", "selector": ".content", "attribute": "text"},
                        {"name": "images", "selector": ".image", "attribute": "src"}
                    ]
                },
                "custom_pagination": {
                    "type": "xiaohongshu",
                    "loading_selector": ".loading",
                    "scroll_pause_time": 3,
                    "max_scroll_attempts": 50
                },
                "output_format": "json",
                "output_path": f"output/{name}.json"
            }
        }

        if template_type not in templates:
            raise ValueError(f"不支持的模板类型: {template_type}")

        config = templates[template_type]
        config_path = self.config_dir / f"{name}.json"

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        logger.info(f"已创建配置文件: {config_path}")
        return str(config_path)

    def _save_results(self, results: List[Dict], config: SpiderConfig):
        """保存结果到文件"""
        try:
            output_path = Path(config.output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if config.output_format == 'json':
                with open(f"{output_path}.json", 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            elif config.output_format == 'csv':
                import pandas as pd
                df = pd.DataFrame(results)
                df.to_csv(f"{output_path}.csv", index=False, encoding='utf-8-sig')
            elif config.output_format == 'xlsx':
                import pandas as pd
                df = pd.DataFrame(results)
                df.to_excel(f"{output_path}.xlsx", index=False)

            logger.info(f"结果已保存到: {output_path}")

        except Exception as e:
            logger.error(f"保存结果失败: {e}")

    def get_spider_status(self, config_name: str) -> Optional[Dict]:
        """获取爬虫状态"""
        return self.running_spiders.get(config_name)

    def stop_spider(self, config_name: str):
        """停止正在运行的爬虫"""
        if config_name in self.running_spiders:
            # 这里可以添加停止逻辑
            logger.info(f"停止爬虫: {config_name}")
            del self.running_spiders[config_name]