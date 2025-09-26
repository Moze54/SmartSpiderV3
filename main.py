#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SmartSpider 主入口
使用方法: python main.py -c config/zhihu_hot.json
"""

import argparse
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.spider_factory import SpiderFactory
from utils.logger import setup_logger
from utils.data_saver import DataSaver

def main():
    parser = argparse.ArgumentParser(description='SmartSpider - JSON驱动的智能爬虫')
    parser.add_argument('-c', '--config', required=True, help='配置文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（可选）')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细日志')
    parser.add_argument('--check-cookies', action='store_true', help='只检查cookies不爬取')
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logger(verbose=args.verbose)
    
    try:
        # 检查配置文件
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(f"配置文件不存在: {config_path}")
            return 1
        
        # 创建爬虫
        logger.info(f"🚀 启动爬虫，配置文件: {config_path}")
        spider = SpiderFactory.create_spider(str(config_path))
        
        # 如果是cookie检查模式
        if args.check_cookies:
            logger.info("🔍 Cookie检查模式")
            if hasattr(spider, 'session'):
                cookies = spider.session.cookies
                logger.info(f"当前cookies数量: {len(cookies)}")
                for cookie in cookies:
                    logger.info(f"Cookie: {cookie.name}={cookie.value[:30]}...")
            return 0
        
        # 运行爬虫
        logger.info("🕷️  开始爬取数据...")
        results = spider.crawl()
        
        if results:
            logger.info(f"✅ 爬取完成! 共获取 {len(results)} 条数据")
            
            # 检查结果质量
            if results and len(results[0]) <= 2:  # 如果字段很少，可能是登录失败
                logger.warning("⚠️  获取的字段较少，可能登录未成功")
            
            # 保存结果
            saver = DataSaver()
            output_file = saver.save(results, spider.config.name, args.output)
            logger.info(f"💾 数据已保存到: {output_file}")
            
            # 显示预览
            saver.preview(results)
        else:
            logger.warning("⚠️  未获取到任何数据")
            logger.info("💡 建议: 检查cookie文件是否有效，或增加--check-cookies参数查看cookies")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("🛑 用户中断爬取")
        return 1
    except Exception as e:
        logger.error(f"❌ 爬取失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())