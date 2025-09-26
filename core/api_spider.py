# -*- coding: utf-8 -*-
"""
API爬虫实现
"""

import requests
import time
from typing import Dict, List, Union
from urllib.parse import urljoin
import json 
from .base_spider import BaseSpider, SpiderConfig
from utils.cookie_loader import CookieLoader
from utils.logger import get_logger

logger = get_logger(__name__)


class ApiSpider(BaseSpider):
    """API爬虫类"""
    
    def __init__(self, config: SpiderConfig):
        super().__init__(config)
        self.session = requests.Session()
        self._setup_session()


    def _setup_session(self):
        """设置请求会话"""
        # 默认请求头
        default_headers = {
            'User-Agent': self.config.user_agent or (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'x-requested-with': 'fetch'
        }

        # 更新自定义请求头
        if self.config.headers:
            default_headers.update(self.config.headers)

        self.session.headers.update(default_headers)

        # 确保正确处理压缩内容
        self.session.headers['Accept-Encoding'] = 'gzip, deflate, br'

        # 设置代理
        if self.config.proxy:
            self.session.proxies = {'http': self.config.proxy, 'https': self.config.proxy}

        # 加载cookies
        if self.config.cookies_file:
            cookie_loader = CookieLoader(self.config.cookies_file)
            cookies = cookie_loader.load()
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
    
    def fetch_page(self, url: str, params: Dict = None) -> Dict:
        """获取页面数据 - 增强调试版"""
        try:
            logger.info(f"请求URL: {url}")
            if params:
                logger.debug(f"请求参数: {params}")

            # 记录请求前的cookies
            logger.info(f"请求前cookies: {len(self.session.cookies)} 个")
            for cookie in self.session.cookies:
                if cookie.name in ['z_c0', '_xsrf']:
                    logger.info(f"请求前cookie: {cookie.name}={cookie.value[:20]}...")
            
            response = self.session.get(
                url,
                params=params or self.config.params,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            # 记录响应状态
            logger.info(f"响应状态: {response.status_code}")
            logger.info(f"响应头Content-Type: {response.headers.get('content-type', 'unknown')}")
            logger.info(f"响应内容长度: {len(response.text)} 字符")

            # 尝试解析JSON
            try:
                json_data = response.json()
                logger.info(f"成功解析JSON，数据类型: {type(json_data)}")
                if isinstance(json_data, dict):
                    logger.info(f"JSON数据keys: {list(json_data.keys())}")

                # 检查知乎特定的错误响应
                if isinstance(json_data, dict):
                    if 'error' in json_data:
                        logger.error(f"API错误: {json_data['error']}")
                        return {}
                    if json_data.get('code') != 200 and 'code' in json_data:
                        logger.error(f"业务错误码: {json_data.get('code')}, 消息: {json_data.get('message', '')}")
                        return {}

                return json_data

            except ValueError as e:
                logger.error(f"响应不是有效的JSON格式: {e}")
                logger.error(f"响应内容预览: {response.text[:500]}...")
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败 {url}: {e}")
            return {}
    
    def extract_list_data(self, data: Dict) -> List[Dict]:
        """提取列表页数据 - 适配新结构"""
        if not self.config.list_page or 'fields' not in self.config.list_page:
            logger.warning("未配置列表页字段")
            return []

        results = []
        items = data

        # 获取数据列表
        list_selector = self.config.list_page.get('list_selector', '')
        if list_selector:
            for path in list_selector.split('.'):
                if isinstance(items, dict) and path in items:
                    items = items[path]
                else:
                    items = []
                    break

        if not isinstance(items, list):
            items = [items] if items else []

        logger.info(f"提取到 {len(items)} 个列表项")

        # 调试：打印响应结构
        if data and isinstance(data, dict):
            logger.info(f"响应数据keys: {list(data.keys())}")
            if 'data' in data:
                logger.info(f"data字段类型: {type(data['data'])}")
                if isinstance(data['data'], list) and len(data['data']) > 0:
                    logger.info(f"第一条数据keys: {list(data['data'][0].keys())}")

        # 提取字段
        fields = self.config.list_page.get('fields', [])
        for i, item in enumerate(items):
            record = {}

            for field_config in fields:
                field_name = field_config['name']
                selector = field_config.get('selector', '')

                value = self._extract_value(item, selector)
                record[field_name] = value

                # 调试：记录提取结果
                if value:
                    logger.debug(f"  提取字段 '{field_name}' = '{value[:50]}...'")
                else:
                    logger.debug(f"  字段 '{field_name}' 提取为空")

            if record:
                results.append(record)
                logger.debug(f"记录 {i+1}: {list(record.keys())}")

        return results
    
    def _extract_value(self, data: Union[Dict, str], selector: str) -> str:
        """从数据中提取值 - 最终修复版"""
        if not selector:
            return ''
        
        if isinstance(data, dict):
            # 支持点语法访问嵌套字段
            keys = selector.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return ''
            
            # 处理不同类型的值
            if value is None:
                return ''
            elif isinstance(value, (str, int, float)):
                return str(value)
            elif isinstance(value, dict):
                # 如果值是dict，尝试获取text字段（知乎的新格式）
                if 'text' in value:
                    return str(value['text'])
                else:
                    return json.dumps(value, ensure_ascii=False)[:100]
            elif isinstance(value, list):
                return ','.join(map(str, value))
            else:
                return str(value)
        
        return ''
    
    def crawl_detail_page(self, url: str) -> Dict:
        """爬取详情页"""
        try:
            data = self.fetch_page(url)
            detail_data = {}
            
            if self.config.detail_page and 'fields' in self.config.detail_page:
                for field_config in self.config.detail_page['fields']:
                    field_name = field_config['name']
                    selector = field_config.get('selector', '')
                    attribute = field_config.get('attribute', 'text')
                    
                    value = self._extract_value(data, selector, attribute)
                    detail_data[field_name] = value
            
            return detail_data
        except Exception as e:
            logger.error(f"爬取详情页失败 {url}: {e}")
            return {}
    
    def crawl(self) -> List[Dict]:
        """执行爬取"""
        logger.info(f"开始API爬虫: {self.config.name}")
        self.validate_config()
        
        current_page = 1
        while current_page <= self.config.max_pages:
            logger.info(f"爬取第 {current_page} 页")
            
            # 构建请求参数
            params = self.config.params.copy() if self.config.params else {}
            if self.config.pagination:
                page_param = self.config.pagination.get('param', 'page')
                page_size_param = self.config.pagination.get('size_param', 'size')
                page_size = self.config.pagination.get('size', 20)
                
                params[page_param] = current_page
                if page_size_param:
                    params[page_size_param] = page_size
            
            # 获取数据
            url = self.config.base_url
            data = self.fetch_page(url, params)
            
            if not data:
                break
            
            # 提取列表数据
            list_data = self.extract_list_data(data)
            if not list_data:
                break
            
            # 处理详情页
            if self.config.detail_page:
                for item in list_data:
                    if '_detail_url' in item:
                        detail_data = self.crawl_detail_page(item['_detail_url'])
                        item.update(detail_data)
                        del item['_detail_url']  # 删除临时字段
            
            self.results.extend(list_data)
            
            # 检查是否还有下一页
            if not self._has_next_page(data, current_page):
                break
            
            current_page += 1
            time.sleep(self.config.delay)
        
        logger.info(f"爬取完成，共获取 {len(self.results)} 条数据")
        return self.results
    
    def _has_next_page(self, data: Dict, current_page: int) -> bool:
        """检查是否还有下一页"""
        if not self.config.pagination:
            return False
        
        # 简单的分页逻辑，可以根据实际情况调整
        return len(self.extract_list_data(data)) > 0