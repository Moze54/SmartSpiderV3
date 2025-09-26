# -*- coding: utf-8 -*-
"""
Cookie加载工具 - 增强版
"""

import json
from pathlib import Path
from typing import List, Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class CookieLoader:
    """Cookie加载器"""
    
    def __init__(self, cookie_file: str):
        self.cookie_file = Path(cookie_file)
    
    def load(self) -> List[Dict]:
        """加载cookie文件
        
        Returns:
            List[Dict]: 格式化的cookie列表
        """
        if not self.cookie_file.exists():
            logger.warning(f"Cookie文件不存在: {self.cookie_file}")
            return []
        
        try:
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            logger.info(f"加载cookie文件: {self.cookie_file}")
            logger.info(f"原始cookie数量: {len(cookies)}")
            
            # 转换cookies格式
            formatted_cookies = []
            for i, cookie in enumerate(cookies):
                if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                    formatted_cookie = {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie.get('domain', ''),
                        'path': cookie.get('path', '/'),
                        'secure': cookie.get('secure', False),
                        'httpOnly': cookie.get('httpOnly', False)
                    }
                    
                    # 处理过期时间
                    if 'expirationDate' in cookie:
                        formatted_cookie['expiry'] = int(cookie['expirationDate'])
                    
                    formatted_cookies.append(formatted_cookie)
                    
                    # 记录主要cookie
                    if cookie['name'] in ['z_c0', '_xsrf', 'd_c0']:
                        logger.info(f"关键cookie: {cookie['name']}={cookie['value'][:20]}...")
            
            logger.info(f"有效cookie数量: {len(formatted_cookies)}")
            return formatted_cookies
            
        except json.JSONDecodeError as e:
            logger.error(f"Cookie文件格式错误: {e}")
            # 尝试读取为文本文件查看内容
            try:
                with open(self.cookie_file, 'r', encoding='utf-8') as f:
                    content = f.read()[:200]
                logger.error(f"文件内容预览: {content}")
            except:
                pass
            return []
        except Exception as e:
            logger.error(f"加载cookie失败: {e}")
            return []
    
    def validate_cookies(self, cookies: List[Dict]) -> bool:
        """验证cookies是否有效
        
        Returns:
            bool: 是否包含关键cookie
        """
        if not cookies:
            return False
        
        # 检查知乎关键cookie
        required_cookies = ['z_c0', '_xsrf', 'd_c0']
        cookie_names = [cookie['name'] for cookie in cookies]
        
        has_key_cookies = any(name in cookie_names for name in required_cookies)
        if has_key_cookies:
            logger.info("检测到关键cookie，可能已登录")
        else:
            logger.warning("未检测到关键cookie，可能未登录")
        
        return has_key_cookies