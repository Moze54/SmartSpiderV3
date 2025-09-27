# SmartSpider V3 - JSON配置详细指南

本指南详细介绍了SmartSpider V3的JSON配置文件格式，包含所有可用字段、配置示例和最佳实践。

## 📋 配置文件结构

SmartSpider的配置文件采用JSON格式，分为**基础配置**和**模式专用配置**两大类。

## 🔧 基础配置详解

### 1. 通用字段

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `name` | string | ✅ | - | 爬虫名称，用于生成输出文件名 |
| `mode` | string | ✅ | - | 爬取模式："browser" 或 "api" |
| `base_url` | string | ✅ | - | 网站的基础URL |
| `user_agent` | string | ❌ | 默认UA | 自定义User-Agent字符串 |
| `headers` | object | ❌ | {} | 自定义请求头 |
| `cookies_file` | string | ❌ | null | Cookie文件路径 |
| `timeout` | number | ❌ | 30 | 请求超时时间（秒） |
| `delay` | number | ❌ | 2 | 请求间隔延迟（秒） |
| `max_pages` | number | ❌ | 1 | 最大爬取页数 |
| `proxy` | object/string | ❌ | null | 代理配置 |

### 2. 基础配置示例

```json
{
  "name": "example_spider",
  "mode": "browser",
  "base_url": "https://example.com",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
  "headers": {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
  },
  "cookies_file": "cookies.json",
  "timeout": 30,
  "delay": 3,
  "max_pages": 5
}
```

## 🌐 浏览器模式配置

### 1. 字段结构

```json
{
  "list_page": {
    "url_template": "可选的URL模板",
    "item_selector": "列表项CSS选择器",
    "wait_selector": "等待加载的选择器",
    "fields": [
      {
        "name": "字段名",
        "selector": "CSS选择器",
        "attribute": "text|href|src|...",
        "transform": "可选的转换函数"
      }
    ]
  },
  "detail_page": {
    "enabled": true,
    "url_template": "详情页URL模板",
    "fields": [...]
  },
  "pagination": {
    "enabled": true,
    "next_page_selector": "下一页按钮选择器",
    "page_param": "页码参数名"
  }
}
```

### 2. 字段提取详解

#### 字段提取规则

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | string | ✅ | 字段名称，用于输出数据中的键名 |
| `selector` | string | ✅ | CSS选择器，用于定位元素 |
| `attribute` | string | ✅ | 提取的属性类型 |
| `transform` | string | ❌ | 数据转换函数 |

#### 支持的属性类型

| 属性值 | 说明 | 示例 |
|--------|------|------|
| `"text"` | 提取元素的文本内容 | `<div>内容</div>` → "内容" |
| `"href"` | 提取链接地址 | `<a href="/path">链接</a>` → "/path" |
| `"src"` | 提取图片地址 | `<img src="image.jpg">` → "image.jpg" |
| `"html"` | 提取HTML内容 | `<div><span>内容</span></div>` → `<span>内容</span>` |
| `"data-*"` | 提取data属性 | `<div data-id="123">` → "123" |

### 3. 浏览器模式完整示例

#### 知乎热榜配置

```json
{
  "name": "zhihu_hot_list",
  "mode": "browser",
  "base_url": "https://www.zhihu.com/hot",
  "cookies_file": "zhihu_cookies.json",
  "timeout": 30,
  "delay": 2,
  "max_pages": 1,
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
  },
  "list_page": {
    "url_template": "https://www.zhihu.com/hot",
    "item_selector": ".HotItem",
    "wait_selector": ".HotItem-content",
    "fields": [
      {
        "name": "rank",
        "selector": ".HotItem-rank",
        "attribute": "text",
        "transform": "trim"
      },
      {
        "name": "title",
        "selector": ".HotItem-title",
        "attribute": "text",
        "transform": "trim"
      },
      {
        "name": "excerpt",
        "selector": ".HotItem-excerpt",
        "attribute": "text",
        "transform": "trim"
      },
      {
        "name": "hot_score",
        "selector": ".HotItem-metrics",
        "attribute": "text",
        "transform": "trim"
      },
      {
        "name": "url",
        "selector": ".HotItem-title a",
        "attribute": "href",
        "transform": "absolute_url"
      }
    ]
  },
  "detail_page": {
    "enabled": false,
    "url_template": "https://www.zhihu.com/question/{id}",
    "fields": [
      {
        "name": "question_title",
        "selector": ".QuestionHeader-title",
        "attribute": "text"
      },
      {
        "name": "question_detail",
        "selector": ".QuestionHeader-detail",
        "attribute": "text"
      },
      {
        "name": "answer_count",
        "selector": ".QuestionHeader-answer-count",
        "attribute": "text"
      }
    ]
  }
}
```

#### 微博热搜配置

```json
{
  "name": "weibo_hot_search",
  "mode": "browser",
  "base_url": "https://s.weibo.com/top/summary",
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
  },
  "timeout": 30,
  "delay": 3,
  "max_pages": 1,
  "list_page": {
    "url_template": "https://s.weibo.com/top/summary",
    "item_selector": "#pl_top_realtimehot table tbody tr",
    "wait_selector": "#pl_top_realtimehot",
    "fields": [
      {
        "name": "rank",
        "selector": "td.td-01",
        "attribute": "text",
        "transform": "trim"
      },
      {
        "name": "title",
        "selector": "td.td-02 a",
        "attribute": "text",
        "transform": "trim"
      },
      {
        "name": "url",
        "selector": "td.td-02 a",
        "attribute": "href",
        "transform": "absolute_url"
      },
      {
        "name": "hot_value",
        "selector": "td.td-02 span",
        "attribute": "text",
        "transform": "trim"
      },
      {
        "name": "icon",
        "selector": "td.td-03 i",
        "attribute": "class",
        "transform": "trim"
      }
    ]
  }
}
```

## 🚀 API模式配置

### 1. 字段结构

```json
{
  "list_page": {
    "url_template": "API地址模板",
    "container_selector": "数据容器选择器",
    "item_selectors": {
      "字段名": "数据路径选择器"
    }
  }
}
```

### 2. API模式示例

假设有一个API接口返回如下数据：

```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 123,
        "title": "新闻标题",
        "url": "/news/123",
        "publish_time": "2024-01-01 12:00:00"
      }
    ]
  }
}
```

对应的配置文件：

```json
{
  "name": "news_api",
  "mode": "api",
  "base_url": "https://api.example.com",
  "headers": {
    "Content-Type": "application/json",
    "User-Agent": "SmartSpider/1.0"
  },
  "timeout": 10,
  "delay": 1,
  "max_pages": 10,
  "list_page": {
    "url_template": "https://api.example.com/news?page={page}",
    "container_selector": "data.list",
    "item_selectors": {
      "id": "id",
      "title": "title",
      "url": "url",
      "publish_time": "publish_time"
    }
  }
}
```

## 🔄 分页配置详解

### 1. 分页类型

#### URL参数分页

```json
{
  "pagination": {
    "type": "param",
    "page_param": "page",
    "start_page": 1,
    "page_size": 20
  }
}
```

#### 链接点击分页

```json
{
  "pagination": {
    "type": "click",
    "next_page_selector": ".pagination .next",
    "max_pages": 5
  }
}
```

### 2. 分页配置示例

```json
{
  "pagination": {
    "enabled": true,
    "type": "param",
    "page_param": "page",
    "start_page": 1,
    "max_pages": 10,
    "page_size": 20,
    "delay": 2
  }
}
```

## 🔍 选择器详解

### 1. CSS选择器语法

| 选择器 | 说明 | 示例 |
|--------|------|------|
| `#id` | ID选择器 | `#content` |
| `.class` | 类选择器 | `.item-title` |
| `tag` | 标签选择器 | `div`, `a`, `span` |
| `[attribute]` | 属性选择器 | `[data-id]`, `a[href]` |
| `parent > child` | 子选择器 | `ul > li` |
| `ancestor descendant` | 后代选择器 | `.list .item` |

### 2. 复杂选择器示例

```json
{
  "fields": [
    {
      "name": "username",
      "selector": ".user-info .username a",
      "attribute": "text"
    },
    {
      "name": "user_id",
      "selector": ".user-card[data-user-id]",
      "attribute": "data-user-id"
    },
    {
      "name": "avatar_url",
      "selector": ".avatar img",
      "attribute": "src"
    }
  ]
}
```

## 🍪 Cookie配置详解

### 1. Cookie文件格式

```json
[
  {
    "name": "session_id",
    "value": "abc123def456",
    "domain": ".example.com",
    "path": "/",
    "expires": 1735689600
  },
  {
    "name": "user_token",
    "value": "xyz789uvw012",
    "domain": ".example.com",
    "path": "/"
  }
]
```

### 2. 获取Cookie的方法

#### 方法1：浏览器开发者工具
1. 打开目标网站并登录
2. 按F12打开开发者工具
3. 切换到Application/Storage标签
4. 选择Cookies -> 目标域名
5. 复制所有cookie信息

#### 方法2：浏览器插件
- EditThisCookie (Chrome)
- Cookie-Editor (Firefox)
- 导出为JSON格式

#### 方法3：手动创建
```json
[
  {
    "name": "login_token",
    "value": "your_login_token_here",
    "domain": ".zhihu.com"
  }
]
```

## 🌐 代理配置详解

### 1. HTTP代理

```json
{
  "proxy": {
    "http": "http://proxy.example.com:8080",
    "https": "https://proxy.example.com:8080"
  }
}
```

### 2. 带认证的代理

```json
{
  "proxy": {
    "http": "http://username:password@proxy.example.com:8080",
    "https": "https://username:password@proxy.example.com:8080"
  }
}
```

### 3. SOCKS代理

```json
{
  "proxy": {
    "http": "socks5://user:pass@host:port",
    "https": "socks5://user:pass@host:port"
  }
}
```

## 🛡️ 反反爬配置

### 1. 随机延迟

```json
{
  "delay": {
    "min": 2,
    "max": 5,
    "type": "random"
  }
}
```

### 2. 随机User-Agent

```json
{
  "user_agent": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)..."
  ]
}
```

### 3. 请求头伪装

```json
{
  "headers": {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
  }
}
```

## 📊 高级功能配置

### 1. 详情页爬取

```json
{
  "detail_page": {
    "enabled": true,
    "url_field": "url",
    "url_template": "https://example.com/item/{id}",
    "fields": [
      {
        "name": "content",
        "selector": ".article-content",
        "attribute": "text"
      },
      {
        "name": "author",
        "selector": ".author-name",
        "attribute": "text"
      },
      {
        "name": "publish_time",
        "selector": ".publish-time",
        "attribute": "text"
      }
    ]
  }
}
```

### 2. 数据清洗配置

```json
{
  "data_cleaning": {
    "remove_whitespace": true,
    "remove_html_tags": false,
    "date_format": "YYYY-MM-DD HH:MM:SS",
    "number_format": "integer"
  }
}
```

## 🎯 配置验证工具

### 1. 使用命令行验证

```bash
# 验证配置文件格式
python -m json.tool config.json

# 检查配置文件
python main.py -c config.json --check-cookies
```

### 2. 配置模板生成器

```bash
# 生成浏览器模式模板
python -c "
import json
config = {
  'name': 'my_spider',
  'mode': 'browser',
  'base_url': 'https://example.com',
  'list_page': {
    'item_selector': '.item',
    'fields': [
      {'name': 'title', 'selector': '.title', 'attribute': 'text'}
    ]
  }
}
print(json.dumps(config, indent=2, ensure_ascii=False))
"
```

## 📝 最佳实践

### 1. 配置命名规范
- 使用小写字母和下划线
- 描述性名称：zhihu_hot_list, weibo_trending
- 避免特殊字符和空格

### 2. 选择器优化
- 使用稳定的class或id选择器
- 避免使用nth-child等易变选择器
- 优先使用语义化选择器

### 3. 错误处理
- 设置合理的超时时间
- 添加适当的延迟
- 使用try-catch处理异常

### 4. 数据验证
- 验证必要字段是否存在
- 检查数据格式是否正确
- 记录错误日志

## 🐛 常见配置错误

### 1. JSON格式错误
```json
// ❌ 错误：缺少逗号
{
  "name": "test"
  "mode": "browser"
}

// ✅ 正确
{
  "name": "test",
  "mode": "browser"
}
```

### 2. 选择器错误
```json
// ❌ 错误：选择器不存在
{
  "selector": ".non-existent-class"
}

// ✅ 正确：使用浏览器验证选择器
{
  "selector": ".hot-list-item"
}
```

### 3. 路径错误
```json
// ❌ 错误：相对路径
{
  "cookies_file": "./cookies.json"
}

// ✅ 正确：绝对路径或项目根目录
{
  "cookies_file": "cookies.json"
}
```

## 📚 配置示例库

### 1. 新闻网站

```json
{
  "name": "news_spider",
  "mode": "browser",
  "base_url": "https://news.example.com",
  "list_page": {
    "item_selector": ".news-item",
    "fields": [
      {"name": "title", "selector": ".title", "attribute": "text"},
      {"name": "summary", "selector": ".summary", "attribute": "text"},
      {"name": "url", "selector": "a.title-link", "attribute": "href"},
      {"name": "publish_time", "selector": ".time", "attribute": "text"},
      {"name": "author", "selector": ".author", "attribute": "text"}
    ]
  }
}
```

### 2. 电商商品

```json
{
  "name": "product_spider",
  "mode": "browser",
  "base_url": "https://shop.example.com",
  "list_page": {
    "item_selector": ".product-item",
    "fields": [
      {"name": "name", "selector": ".product-name", "attribute": "text"},
      {"name": "price", "selector": ".price", "attribute": "text"},
      {"name": "image", "selector": ".product-image img", "attribute": "src"},
      {"name": "url", "selector": ".product-link", "attribute": "href"},
      {"name": "rating", "selector": ".rating", "attribute": "text"}
    ]
  }
}
```

### 3. 社交媒体

```json
{
  "name": "social_media_spider",
  "mode": "browser",
  "base_url": "https://social.example.com",
  "cookies_file": "social_cookies.json",
  "list_page": {
    "item_selector": ".post-item",
    "fields": [
      {"name": "author", "selector": ".author-name", "attribute": "text"},
      {"name": "content", "selector": ".post-content", "attribute": "text"},
      {"name": "likes", "selector": ".like-count", "attribute": "text"},
      {"name": "shares", "selector": ".share-count", "attribute": "text"},
      {"name": "timestamp", "selector": ".post-time", "attribute": "text"}
    ]
  }
}
```

## 🔧 调试工具

### 1. 选择器测试工具

```python
# test_selector.py
from bs4 import BeautifulSoup
import requests

url = "https://example.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 测试选择器
selectors = [
    ".title",
    ".content",
    ".author"
]

for selector in selectors:
    elements = soup.select(selector)
    print(f"{selector}: {len(elements)} elements found")
    if elements:
        print(f"First element: {elements[0].text[:50]}...")
```

### 2. 配置验证脚本

```python
# validate_config.py
import json
import jsonschema

schema = {
    "type": "object",
    "required": ["name", "mode", "base_url", "list_page"],
    "properties": {
        "name": {"type": "string"},
        "mode": {"type": "string", "enum": ["browser", "api"]},
        "base_url": {"type": "string"},
        "list_page": {"type": "object"}
    }
}

def validate_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    try:
        jsonschema.validate(config, schema)
        print("✅ 配置验证通过")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ 配置验证失败: {e}")
        return False

# 使用示例
validate_config('config.json')
```

---

通过本指南，您应该能够创建和配置适用于各种网站的SmartSpider配置文件。如需更多帮助，请参考项目README或提交Issue。