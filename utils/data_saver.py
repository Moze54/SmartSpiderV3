# -*- coding: utf-8 -*-
"""
数据保存工具
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class DataSaver:
    """数据保存器"""
    
    def __init__(self, output_dir: str = 'results'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save(self, data: List[Dict], spider_name: str, filename: str = None) -> str:
        """保存数据
        
        Args:
            data: 要保存的数据
            spider_name: 爬虫名称
            filename: 自定义文件名（可选）
            
        Returns:
            str: 保存的文件路径
        """
        if not data:
            logger.warning("没有数据可保存")
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{spider_name}_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        # 格式化输出
        output = {
            'meta': {
                'spider_name': spider_name,
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_count': len(data)
            },
            'data': data
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存到: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            return ""
    
    def save_csv(self, data: List[Dict], spider_name: str, filename: str = None) -> str:
        """保存为CSV格式
        
        Args:
            data: 要保存的数据
            spider_name: 爬虫名称
            filename: 自定义文件名（可选）
            
        Returns:
            str: 保存的文件路径
        """
        if not data:
            logger.warning("没有数据可保存")
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{spider_name}_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        try:
            # 获取所有可能的字段
            all_fields = set()
            for item in data:
                all_fields.update(item.keys())
            
            fieldnames = sorted(all_fields)
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"CSV数据已保存到: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"保存CSV失败: {e}")
            return ""
    
    def preview(self, data: List[Dict], max_items: int = 5):
        """预览数据
        
        Args:
            data: 数据列表
            max_items: 显示的最大条数
        """
        if not data:
            print("📊 没有数据可预览")
            return
        
        print(f"\n📊 数据预览 (显示前 {min(max_items, len(data))} 条，共 {len(data)} 条):")
        print("-" * 80)
        
        for i, item in enumerate(data[:max_items], 1):
            print(f"{i}. ", end="")
            # 显示主要字段
            main_fields = ['title', 'name', 'content', 'text'][:3]
            shown = False
            
            for field in main_fields:
                if field in item and item[field]:
                    value = str(item[field])
                    if len(value) > 50:
                        value = value[:47] + "..."
                    print(f"{field}: {value}", end=" | ")
                    shown = True
            
            if not shown:
                # 显示前两个有值的字段
                displayed = 0
                for key, value in item.items():
                    if value and displayed < 2:
                        value_str = str(value)
                        if len(value_str) > 30:
                            value_str = value_str[:27] + "..."
                        print(f"{key}: {value_str}", end=" | ")
                        displayed += 1
            
            print()