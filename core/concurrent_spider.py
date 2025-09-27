# -*- coding: utf-8 -*-
"""
多线程爬虫实现
"""

import concurrent.futures
import threading
import time
from typing import Dict, List
from urllib.parse import urljoin

import logging
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


class ConcurrentBrowserSpider(BaseSpider):
    """多线程浏览器爬虫类"""

    def __init__(self, config: SpiderConfig):
        super().__init__(config)
        self.thread_local_storage = threading.local()
        self.results_lock = threading.Lock()
        self.all_results = []

    def _create_driver_instance(self) -> webdriver.Chrome:
        """创建单个浏览器实例"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            chrome_options.add_argument('--disable-setuid-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-accelerated-2d-canvas')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--no-default-browser-check')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-sync')
            chrome_options.add_argument('--disable-webgl')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--disable-javascript')
            chrome_options.add_argument('--disable-java')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-background-networking')
            chrome_options.add_argument('--disable-component-update')
            chrome_options.add_argument('--disable-background-downloads')
            chrome_options.add_argument('--disable-component-extensions-with-background-pages')
            chrome_options.add_argument('--disable-extensions-http-throttling')

            # 添加随机端口避免冲突
            chrome_options.add_argument('--remote-debugging-port=0')

            user_agent = self.config.user_agent or (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            chrome_options.add_argument(f'--user-agent={user_agent}')

            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.set_window_size(1920, 1080)

            # 设置页面加载超时
            driver.set_page_load_timeout(self.config.timeout)

            return driver
        except Exception as e:
            logger.error(f"创建浏览器实例失败: {e}")
            raise

    def _get_driver(self) -> webdriver.Chrome:
        """获取线程本地驱动"""
        if not hasattr(self.thread_local_storage, 'driver'):
            self.thread_local_storage.driver = self._create_driver_instance()

            # 加载cookies
            if self.config.cookies_file:
                cookie_loader = CookieLoader(self.config.cookies_file)
                cookies = cookie_loader.load()
                if cookies:
                    self.thread_local_storage.driver.get(self.config.base_url)
                    time.sleep(2)
                    for cookie in cookies:
                        try:
                            safe_cookie = {k: v for k, v in cookie.items()
                                         if k in ['name', 'value', 'domain', 'path', 'secure', 'expiry']}
                            self.thread_local_storage.driver.add_cookie(safe_cookie)
                        except Exception as e:
                            logger.warning(f"添加cookie失败: {e}")
                    self.thread_local_storage.driver.refresh()
                    time.sleep(2)

        return self.thread_local_storage.driver

    def _close_driver(self):
        """关闭线程本地驱动"""
        if hasattr(self.thread_local_storage, 'driver'):
            self.thread_local_storage.driver.quit()
            del self.thread_local_storage.driver

    def _fetch_page_with_driver(self, url: str) -> str:
        """使用线程本地驱动获取页面"""
        driver = self._get_driver()
        try:
            logger.debug(f"线程 {threading.current_thread().name} 访问页面: {url}")
            driver.get(url)
            time.sleep(self.config.delay)

            # 等待特定元素加载
            if self.config.list_page and 'wait_selector' in self.config.list_page:
                WebDriverWait(driver, self.config.timeout).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.config.list_page['wait_selector'])
                    )
                )

            return driver.page_source
        except Exception as e:
            logger.error(f"获取页面失败 {url}: {e}")
            return ""

    def _extract_data_from_html(self, html: str, item_index: int) -> Dict:
        """从HTML提取单个商品数据"""
        soup = BeautifulSoup(html, 'html.parser')

        if not self.config.list_page or 'fields' not in self.config.list_page:
            return {}

        # 获取所有商品项
        item_selector = self.config.list_page.get('item_selector', '')
        items = soup.select(item_selector)

        if item_index >= len(items):
            return {}

        item = items[item_index]
        record = {}

        for field_config in self.config.list_page['fields']:
            field_name = field_config['name']
            selector = field_config.get('selector', '')
            attribute = field_config.get('attribute', 'text')

            value = self._extract_value_from_element(item, selector, attribute)
            record[field_name] = value

        # 提取详情页URL
        if self.config.detail_page:
            url_field = self.config.detail_page.get('url_field', 'url')
            url_selector = None

            # 查找详情页URL选择器
            for field_config in self.config.list_page['fields']:
                if field_config['name'] == url_field:
                    url_selector = field_config.get('selector', '')
                    break

            if url_selector:
                url_elem = item.select_one(url_selector)
                if url_elem and url_elem.get('href'):
                    detail_url = urljoin(self.config.base_url, url_elem['href'])
                    record['_detail_url'] = detail_url

        return record

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

    def _crawl_detail_page(self, detail_url: str) -> Dict:
        """爬取详情页"""
        if not self.config.detail_page or not self.config.detail_page.get('enabled', False):
            return {}

        try:
            driver = self._get_driver()
            driver.get(detail_url)
            time.sleep(self.config.delay * 2)  # 详情页等待更长时间

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            detail_data = {}
            if 'fields' in self.config.detail_page:
                for field_config in self.config.detail_page['fields']:
                    field_name = field_config['name']
                    selector = field_config.get('selector', '')
                    attribute = field_config.get('attribute', 'text')

                    value = self._extract_value_from_element(soup, selector, attribute)
                    detail_data[field_name] = value

            return detail_data
        except Exception as e:
            logger.error(f"爬取详情页失败 {detail_url}: {e}")
            return {}

    def _crawl_single_page(self, page_info: Dict) -> List[Dict]:
        """爬取单个页面"""
        page_num = page_info.get('page', 1)
        url = page_info.get('url', self.config.base_url)
        max_per_page = page_info.get('max_per_page', 50)

        logger.info(f"线程 {threading.current_thread().name} 处理第 {page_num} 页")

        try:
            html = self._fetch_page_with_driver(url)
            if not html:
                return []

            soup = BeautifulSoup(html, 'html.parser')

            # 获取所有商品项
            item_selector = self.config.list_page.get('item_selector', '')
            items = soup.select(item_selector)

            if not items:
                logger.warning(f"第 {page_num} 页未找到商品项")
                return []

            logger.info(f"第 {page_num} 页找到 {len(items)} 个商品项")

            page_results = []
            for i, item in enumerate(items):
                if max_per_page > 0 and i >= max_per_page:
                    break

                record = {}
                for field_config in self.config.list_page['fields']:
                    field_name = field_config['name']
                    selector = field_config.get('selector', '')
                    attribute = field_config.get('attribute', 'text')

                    value = self._extract_value_from_element(item, selector, attribute)
                    record[field_name] = value

                # 提取详情页URL
                if self.config.detail_page and self.config.detail_page.get('enabled', False):
                    url_field = self.config.detail_page.get('url_field', 'product_url')
                    url_selector = None

                    for field_config in self.config.list_page['fields']:
                        if field_config['name'] == url_field:
                            url_selector = field_config.get('selector', '')
                            break

                    if url_selector:
                        url_elem = item.select_one(url_selector)
                        if url_elem and url_elem.get('href'):
                            detail_url = urljoin(self.config.base_url, url_elem['href'])
                            record['_detail_url'] = detail_url

                page_results.append(record)

            return page_results

        except Exception as e:
            logger.error(f"线程 {threading.current_thread().name} 处理第 {page_num} 页失败: {e}")
            return []

    def crawl(self) -> List[Dict]:
        """执行多线程爬取"""
        logger.info(f"开始多线程浏览器爬虫: {self.config.name}")
        self.validate_config()

        try:
            max_total_items = self.config.max_total_items or 0
            concurrent_workers = min(self.config.concurrent, 10)  # 限制最大并发数

            # 准备页面列表
            pages = []
            for page_num in range(1, self.config.max_pages + 1):
                url = self.config.base_url
                if page_num > 1 and self.config.pagination:
                    page_param = self.config.pagination.get('param', 'page')
                    separator = '&' if '?' in url else '?'
                    url = f"{url}{separator}{page_param}={page_num}"

                max_per_page = max_total_items // self.config.max_pages if max_total_items > 0 else 0
                pages.append({
                    'page': page_num,
                    'url': url,
                    'max_per_page': max_per_page
                })

            # 使用线程池执行爬取
            all_results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
                future_to_page = {executor.submit(self._crawl_single_page, page): page for page in pages}

                for future in concurrent.futures.as_completed(future_to_page):
                    page = future_to_page[future]
                    try:
                        page_results = future.result()
                        with self.results_lock:
                            all_results.extend(page_results)

                            # 检查是否达到总量
                            if max_total_items > 0 and len(all_results) >= max_total_items:
                                logger.info(f"已达到最大数据量 {max_total_items}")
                                break
                    except Exception as e:
                        logger.error(f"处理页面 {page['page']} 失败: {e}")

            # 去重
            seen = set()
            unique_results = []
            for item in all_results:
                key = str(item.get('url', '')) + str(item.get('title', ''))
                if key not in seen:
                    seen.add(key)
                    unique_results.append(item)

            if max_total_items > 0:
                unique_results = unique_results[:max_total_items]

            logger.info(f"多线程爬取完成，共获取 {len(unique_results)} 条数据")
            return unique_results

        finally:
            # 关闭所有线程本地驱动
            self._close_driver()

    def __del__(self):
        """析构函数，确保资源清理"""
        self._close_driver()