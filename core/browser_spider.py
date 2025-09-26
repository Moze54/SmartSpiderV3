# -*- coding: utf-8 -*-
"""
浏览器爬虫实现
"""

import time
from typing import Dict, List
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from .base_spider import BaseSpider, SpiderConfig
from utils.cookie_loader import CookieLoader
from utils.logger import get_logger

logger = get_logger(__name__)


class BrowserSpider(BaseSpider):
    """浏览器爬虫类"""
    
    def __init__(self, config: SpiderConfig):
        super().__init__(config)
        self.driver = None
    
    def _setup_driver(self):
        """设置浏览器驱动"""
        try:
            chrome_options = Options()
            
            # 基本配置
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 用户代理
            user_agent = self.config.user_agent or (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            # 无头模式（默认启用）
            if not logger.isEnabledFor(logger.DEBUG):
                chrome_options.add_argument('--headless')
            
            # 代理
            if self.config.proxy:
                chrome_options.add_argument(f'--proxy-server={self.config.proxy}')
            
            # 创建驱动
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 设置窗口大小
            self.driver.set_window_size(1920, 1080)
            
            logger.info("浏览器驱动初始化成功")
            
        except Exception as e:
            logger.error(f"初始化浏览器驱动失败: {e}")
            raise
    
    def load_cookies(self):
        """加载cookies"""
        if self.config.cookies_file and self.driver:
            cookie_loader = CookieLoader(self.config.cookies_file)
            cookies = cookie_loader.load()
            
            if cookies:
                # 先访问基础URL
                self.driver.get(self.config.base_url)
                time.sleep(2)
                
                # 添加cookies
                for cookie in cookies:
                    try:
                        # 过滤掉不安全的cookie字段
                        safe_cookie = {k: v for k, v in cookie.items() 
                                     if k in ['name', 'value', 'domain', 'path', 'secure', 'expiry']}
                        self.driver.add_cookie(safe_cookie)
                    except Exception as e:
                        logger.warning(f"添加cookie失败: {e}")
                
                # 刷新页面使cookie生效
                self.driver.refresh()
                time.sleep(2)
                logger.info("Cookies加载完成")
    
    def fetch_page(self, url: str) -> str:
        """获取页面HTML"""
        try:
            logger.debug(f"访问页面: {url}")
            self.driver.get(url)
            time.sleep(self.config.delay)
            
            # 等待特定元素加载
            if self.config.list_page and 'wait_selector' in self.config.list_page:
                WebDriverWait(self.driver, self.config.timeout).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.config.list_page['wait_selector'])
                    )
                )
            
            return self.driver.page_source
            
        except Exception as e:
            logger.error(f"获取页面失败 {url}: {e}")
            return ""
    
    def extract_list_data(self, html: str) -> List[Dict]:
        """提取列表页数据"""
        if not self.config.list_page or 'fields' not in self.config.list_page:
            logger.warning("未配置列表页字段")
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # 提取列表项
        item_selector = self.config.list_page.get('item_selector', '')
        if item_selector:
            items = soup.select(item_selector)
        else:
            items = [soup]
        
        logger.debug(f"找到 {len(items)} 个列表项")
        
        for item in items:
            record = {}
            for field_config in self.config.list_page['fields']:
                field_name = field_config['name']
                selector = field_config.get('selector', '')
                attribute = field_config.get('attribute', 'text')
                
                value = self._extract_value_from_element(item, selector, attribute)
                record[field_name] = value
            
            # 提取详情页URL
            if self.config.detail_page and 'url_selector' in self.config.list_page:
                detail_url_elem = item.select_one(self.config.list_page['url_selector'])
                if detail_url_elem and detail_url_elem.get('href'):
                    detail_url = urljoin(self.config.base_url, detail_url_elem['href'])
                    record['_detail_url'] = detail_url
            
            if record:
                results.append(record)
        
        return results
    
    def _extract_value_from_element(self, element, selector: str, attribute: str = 'text') -> str:
        """从HTML元素中提取值"""
        try:
            if selector:
                elem = element.select_one(selector)
                if not elem:
                    return ''
            else:
                elem = element
            
            if attribute == 'text':
                return elem.get_text(strip=True)
            elif attribute == 'html':
                return str(elem)
            else:
                return elem.get(attribute, '')
        except Exception as e:
            logger.error(f"提取元素值失败: {e}")
            return ''
    
    def crawl_detail_page(self, url: str) -> Dict:
        """爬取详情页"""
        try:
            html = self.fetch_page(url)
            detail_data = {}
            
            soup = BeautifulSoup(html, 'html.parser')
            
            if self.config.detail_page and 'fields' in self.config.detail_page:
                for field_config in self.config.detail_page['fields']:
                    field_name = field_config['name']
                    selector = field_config.get('selector', '')
                    attribute = field_config.get('attribute', 'text')
                    
                    value = self._extract_value_from_element(soup, selector, attribute)
                    detail_data[field_name] = value
            
            return detail_data
        except Exception as e:
            logger.error(f"爬取详情页失败 {url}: {e}")
            return {}
    
    def crawl(self) -> List[Dict]:
        """执行爬取"""
        logger.info(f"开始浏览器爬虫: {self.config.name}")
        self.validate_config()
        
        try:
            self._setup_driver()
            self.load_cookies()
            
            current_page = 1
            while current_page <= self.config.max_pages:
                logger.info(f"爬取第 {current_page} 页")
                
                # 构建URL
                url = self.config.base_url
                if current_page > 1 and self.config.pagination:
                    page_param = self.config.pagination.get('param', 'page')
                    separator = '&' if '?' in url else '?'
                    url = f"{url}{separator}{page_param}={current_page}"
                
                # 获取页面
                html = self.fetch_page(url)
                if not html:
                    break
                
                # 提取列表数据
                list_data = self.extract_list_data(html)
                if not list_data:
                    break
                
                # 处理详情页
                if self.config.detail_page:
                    for item in list_data:
                        if '_detail_url' in item:
                            detail_data = self.crawl_detail_page(item['_detail_url'])
                            item.update(detail_data)
                            del item['_detail_url']
                
                self.results.extend(list_data)
                
                # 检查是否还有下一页
                if not self._has_next_page(html, current_page):
                    break
                
                current_page += 1
                
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("浏览器驱动已关闭")
        
        logger.info(f"爬取完成，共获取 {len(self.results)} 条数据")
        return self.results
    
    def _has_next_page(self, html: str, current_page: int) -> bool:
        """检查是否还有下一页"""
        if not self.config.pagination:
            return False
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 检查下一页按钮是否存在
        next_selector = self.config.pagination.get('next_selector', '')
        if next_selector:
            next_btn = soup.select_one(next_selector)
            has_next = next_btn is not None and not next_btn.get('disabled')
            logger.debug(f"检查下一页按钮: {has_next}")
            return has_next
        
        return current_page < self.config.max_pages