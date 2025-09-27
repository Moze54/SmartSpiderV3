# -*- coding: utf-8 -*-
"""
浏览器爬虫实现
"""

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

            # 无头模式
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')

            # 反检测配置
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
            chrome_options.add_argument('--disable-accelerated-2d-canvas')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--no-default-browser-check')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-sync')
            chrome_options.add_argument('--disable-webgl')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--disable-background-networking')
            chrome_options.add_argument('--disable-component-update')
            chrome_options.add_argument('--disable-background-downloads')
            chrome_options.add_argument('--disable-component-extensions-with-background-pages')
            chrome_options.add_argument('--disable-extensions-http-throttling')

            # 高级反检测配置
            chrome_options.add_argument('--disable-bundled-ppapi-flash')
            chrome_options.add_argument('--disable-plugins-discovery')
            chrome_options.add_argument('--disable-webrtc')
            chrome_options.add_argument('--disable-client-side-phishing-detection')
            chrome_options.add_argument('--disable-component-extensions-with-background-pages')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-extensions-file-access-check')
            chrome_options.add_argument('--disable-extensions-http-throttling')
            chrome_options.add_argument('--disable-ipc-flooding-protection')
            chrome_options.add_argument('--disable-prompt-on-repost')
            chrome_options.add_argument('--disable-renderer-accessibility')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--enable-automation')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.add_argument('--ignore-urlfetcher-cert-requests')
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_argument('--silent-debugger-extension-api')
            chrome_options.add_argument('--test-type=webdriver')
            chrome_options.add_argument('--window-size=1920,1080')

            # 用户数据目录 - 保持会话 (使用临时目录)
            chrome_options.add_argument('--user-data-dir=C:/temp/chrome-user-data')
            chrome_options.add_argument('--profile-directory=Default')
            chrome_options.add_argument('--remote-debugging-port=0')

            # 用户代理
            user_agent = self.config.user_agent or (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
            )
            chrome_options.add_argument(f'--user-agent={user_agent}')

            # 代理
            if self.config.proxy:
                chrome_options.add_argument(f'--proxy-server={self.config.proxy}')

            # 创建驱动
            self.driver = webdriver.Chrome(options=chrome_options)

            # 执行反检测脚本
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en-US', 'en']})")
            self.driver.execute_script("Object.defineProperty(navigator, 'mimeTypes', {get: () => [1,2,3,4,5]})")

            # 设置窗口大小和位置
            self.driver.set_window_size(1920, 1080)
            self.driver.set_window_position(0, 0)

            # 设置页面加载超时
            self.driver.set_page_load_timeout(self.config.timeout)

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
                # 先访问基础域名以设置cookie
                domain = ".jd.com"
                if "jd.com" in self.config.base_url:
                    self.driver.get("https://www.jd.com")
                else:
                    self.driver.get(self.config.base_url)

                time.sleep(3)

                # 添加cookies前先清空现有cookies
                self.driver.delete_all_cookies()

                # 添加cookies
                jd_cookies_added = 0
                for cookie in cookies:
                    try:
                        # 过滤掉不安全的cookie字段并转换格式
                        safe_cookie = {}
                        for k, v in cookie.items():
                            if k in ['name', 'value', 'domain', 'path', 'secure']:
                                safe_cookie[k] = v
                            elif k == 'expirationDate':
                                safe_cookie['expiry'] = int(v)

                        # 确保domain格式正确
                        if 'domain' not in safe_cookie:
                            safe_cookie['domain'] = domain

                        # 确保path存在
                        if 'path' not in safe_cookie:
                            safe_cookie['path'] = '/'

                        self.driver.add_cookie(safe_cookie)
                        jd_cookies_added += 1

                    except Exception as e:
                        logger.warning(f"添加cookie失败: {e}")

                logger.info(f"成功添加 {jd_cookies_added} 个cookies")

                # 等待一下让cookies生效
                time.sleep(2)

                # 重新访问目标页面
                self.driver.get(self.config.base_url)
                time.sleep(3)

                # 验证登录状态
                current_url = self.driver.current_url
                if "login" in current_url.lower() or "passport" in current_url.lower():
                    logger.warning("检测到重定向到登录页面，cookie可能无效")
                else:
                    logger.info("Cookie验证成功，当前页面: {}".format(current_url))

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

        # 获取总量控制
        max_total_items = self.config.max_total_items or 0

        try:
            self._setup_driver()
            self.load_cookies()

            # 检查分页类型
            pagination_type = self.config.pagination.get('type', 'url') if self.config.pagination else 'url'
            custom_type = self.config.custom_pagination.get('type', '') if self.config.custom_pagination else ''

            if custom_type == 'xiaohongshu':
                # 小红书特殊分页
                self.results = self._crawl_xiaohongshu(max_total_items)
            elif custom_type == 'dynamic_scroll':
                # 动态滚动分页
                self.results = self._crawl_dynamic_scroll(max_total_items)
            elif pagination_type == 'scroll':
                # 滚动分页模式
                self.results = self._crawl_with_scroll(max_total_items)
            elif pagination_type == 'click':
                # 点击加载更多模式
                self.results = self._crawl_with_click_more(max_total_items)
            else:
                # 传统URL分页模式
                self.results = self._crawl_with_url_pagination(max_total_items)

        finally:
            if self.driver:
                self.driver.quit()
                logger.info("浏览器驱动已关闭")

        logger.info(f"爬取完成，共获取 {len(self.results)} 条数据")
        return self.results

    def _crawl_with_scroll(self, max_total_items: int = 0) -> List[Dict]:
        """滚动分页爬取"""
        url = self.config.base_url
        logger.info(f"开始滚动分页爬取: {url}")

        self.driver.get(url)
        time.sleep(3)

        all_results = []
        scroll_attempts = 0
        max_scroll_attempts = self.config.pagination.get('max_scroll_attempts', 50) if self.config.pagination else 50

        while scroll_attempts < max_scroll_attempts:
            # 获取当前页面内容
            html = self.driver.page_source
            current_data = self.extract_list_data(html)

            # 过滤已爬取的数据
            new_data = []
            for item in current_data:
                if not self._is_duplicate(item, all_results):
                    new_data.append(item)

            # 处理详情页
            if self.config.detail_page:
                new_data = self._process_detail_pages(new_data)

            all_results.extend(new_data)

            # 检查是否达到总量
            if max_total_items > 0 and len(all_results) >= max_total_items:
                logger.info(f"已达到最大数据量 {max_total_items}")
                return all_results[:max_total_items]

            # 检查是否还有新数据
            if len(new_data) == 0:
                logger.info("没有新数据了，停止爬取")
                break

            # 滚动到页面底部
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.config.delay)

            # 等待新内容加载
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.body.scrollHeight") > last_height
            )

            scroll_attempts += 1
            logger.info(f"已滚动 {scroll_attempts} 次，当前数据量: {len(all_results)}")

        return all_results

    def _crawl_xiaohongshu(self, max_total_items: int = 0) -> List[Dict]:
        """小红书特殊分页爬取"""
        url = self.config.base_url
        logger.info(f"开始小红书分页爬取: {url}")

        self.driver.get(url)
        time.sleep(5)  # 小红书加载较慢

        all_results = []
        last_item_count = 0
        no_new_count = 0
        max_no_new_attempts = 5

        while no_new_count < max_no_new_attempts:
            # 获取当前页面内容
            html = self.driver.page_source
            current_data = self.extract_list_data(html)

            # 过滤已爬取的数据
            new_data = []
            for item in current_data:
                if not self._is_duplicate(item, all_results):
                    new_data.append(item)

            # 处理详情页
            if self.config.detail_page:
                new_data = self._process_detail_pages(new_data)

            all_results.extend(new_data)

            # 检查是否达到总量
            if max_total_items > 0 and len(all_results) >= max_total_items:
                logger.info(f"已达到最大数据量 {max_total_items}")
                return all_results[:max_total_items]

            # 检查是否还有新数据
            if len(new_data) == 0:
                no_new_count += 1
                logger.info(f"第 {no_new_count} 次未获取到新数据")
            else:
                no_new_count = 0  # 重置计数器
                logger.info(f"获取到 {len(new_data)} 条新数据，总量: {len(all_results)}")

            # 小红书特殊滚动逻辑
            if no_new_count < max_no_new_attempts:
                # 模拟用户行为，先向上滚动一点，再向下滚动
                self.driver.execute_script("window.scrollBy(0, -300);")
                time.sleep(1)

                # 滚动到页面底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(self.config.delay * 2)  # 小红书需要更长的等待时间

                # 检查是否有加载提示
                try:
                    loading_selector = self.config.custom_pagination.get('loading_selector', '')
                    if loading_selector:
                        WebDriverWait(self.driver, 10).until(
                            EC.invisibility_of_element_located((By.CSS_SELECTOR, loading_selector))
                        )
                except:
                    pass

        logger.info(f"小红书爬取完成，共获取 {len(all_results)} 条数据")
        return all_results

    def _crawl_dynamic_scroll(self, max_total_items: int = 0) -> List[Dict]:
        """动态滚动分页爬取"""
        url = self.config.base_url
        logger.info(f"开始动态滚动分页爬取: {url}")

        self.driver.get(url)
        time.sleep(3)

        all_results = []
        scroll_pause_time = self.config.custom_pagination.get('scroll_pause_time', 2) if self.config.custom_pagination else 2
        max_scroll_attempts = self.config.custom_pagination.get('max_scroll_attempts', 100) if self.config.custom_pagination else 100

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for attempt in range(max_scroll_attempts):
            # 获取当前页面内容
            html = self.driver.page_source
            current_data = self.extract_list_data(html)

            # 过滤已爬取的数据
            new_data = []
            for item in current_data:
                if not self._is_duplicate(item, all_results):
                    new_data.append(item)

            # 处理详情页
            if self.config.detail_page:
                new_data = self._process_detail_pages(new_data)

            all_results.extend(new_data)

            # 检查是否达到总量
            if max_total_items > 0 and len(all_results) >= max_total_items:
                logger.info(f"已达到最大数据量 {max_total_items}")
                return all_results[:max_total_items]

            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)

            # 检查页面高度是否变化
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                logger.info("页面高度未变化，可能已到达底部")
                break

            last_height = new_height
            logger.info(f"已滚动 {attempt + 1} 次，当前数据量: {len(all_results)}")

        return all_results

    def _crawl_with_click_more(self, max_total_items: int = 0) -> List[Dict]:
        """点击加载更多模式"""
        url = self.config.base_url
        logger.info(f"开始点击加载更多爬取: {url}")

        self.driver.get(url)
        time.sleep(3)

        all_results = []
        max_clicks = self.config.pagination.get('max_clicks', 100) if self.config.pagination else 100

        for click_attempt in range(max_clicks):
            # 获取当前页面内容
            html = self.driver.page_source
            current_data = self.extract_list_data(html)

            # 过滤已爬取的数据
            new_data = []
            for item in current_data:
                if not self._is_duplicate(item, all_results):
                    new_data.append(item)

            # 处理详情页
            if self.config.detail_page:
                new_data = self._process_detail_pages(new_data)

            all_results.extend(new_data)

            # 检查是否达到总量
            if max_total_items > 0 and len(all_results) >= max_total_items:
                logger.info(f"已达到最大数据量 {max_total_items}")
                return all_results[:max_total_items]

            # 查找加载更多按钮
            load_more_selector = self.config.pagination.get('load_more_selector', '')
            if not load_more_selector:
                logger.warning("未配置加载更多按钮选择器")
                break

            try:
                load_more_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, load_more_selector))
                )
                self.driver.execute_script("arguments[0].click();", load_more_btn)
                time.sleep(self.config.delay)
                logger.info(f"已点击加载更多 {click_attempt + 1} 次，当前数据量: {len(all_results)}")
            except Exception as e:
                logger.info("没有更多数据或按钮不可点击，停止爬取")
                break

        return all_results

    def _crawl_with_url_pagination(self, max_total_items: int = 0) -> List[Dict]:
        """URL分页模式"""
        current_page = 1
        all_results = []

        while True:
            if max_total_items > 0 and len(all_results) >= max_total_items:
                logger.info(f"已达到最大数据量 {max_total_items}")
                return all_results[:max_total_items]

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
            list_data = self._process_detail_pages(list_data)

            # 过滤重复数据
            new_data = []
            for item in list_data:
                if not self._is_duplicate(item, all_results):
                    new_data.append(item)

            all_results.extend(new_data)

            # 检查是否还有下一页
            if not self._has_next_page(html, current_page) or current_page >= self.config.max_pages:
                break

            current_page += 1

        return all_results

    def _process_detail_pages(self, items: List[Dict]) -> List[Dict]:
        """处理详情页"""
        if not self.config.detail_page or not self.config.detail_page.get('enabled', False):
            return items

        processed_items = []

        for item in items:
            if '_detail_url' in item:
                detail_url = item['_detail_url']
                detail_data = self.crawl_detail_page(detail_url)
                item.update(detail_data)
                del item['_detail_url']
            elif self.config.detail_page.get('url_field'):
                # 从配置字段中获取详情页URL
                url_field = self.config.detail_page['url_field']
                if url_field in item and item[url_field]:
                    detail_url = urljoin(self.config.base_url, item[url_field])
                    detail_data = self.crawl_detail_page(detail_url)
                    item.update(detail_data)

            processed_items.append(item)

        return processed_items

    def _is_duplicate(self, item: Dict, existing_items: List[Dict]) -> bool:
        """检查是否为重复数据"""
        # 使用URL或标题作为唯一标识
        unique_key = item.get('url') or item.get('title') or str(item)

        for existing in existing_items:
            existing_key = existing.get('url') or existing.get('title') or str(existing)
            if unique_key == existing_key:
                return True

        return False
    
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