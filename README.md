# SmartSpider V3 - JSON驱动的智能爬虫框架

SmartSpider V3 是一个高度可配置的爬虫框架，通过 JSON 配置文件驱动，支持浏览器模式和 API 模式，无需编写代码即可快速实现各种网站的爬取需求。

## 🚀 功能特点

- **JSON驱动**: 通过简单的JSON配置文件定义爬取规则
- **双模式支持**: 支持浏览器模式（Selenium）和API模式（Requests）
- **智能等待**: 自动等待页面加载完成，支持动态内容爬取
- **数据导出**: 自动保存为JSON文件，支持自定义输出路径
- **Cookie管理**: 支持Cookie持久化和自动加载
- **错误处理**: 完善的异常捕获和重试机制
- **日志系统**: 详细的日志记录，便于调试和监控
- **代理支持**: 支持配置代理服务器

## 📋 项目结构

```
SmartSpiderV3/
├── main.py              # 主入口文件
├── core/                # 核心模块
│   ├── base_spider.py   # 爬虫基类
│   ├── spider_factory.py # 爬虫工厂
│   ├── api_spider.py    # API模式爬虫
│   └── browser_spider.py # 浏览器模式爬虫
├── utils/               # 工具模块
│   ├── logger.py        # 日志配置
│   ├── data_saver.py    # 数据保存
│   └── cookie_loader.py # Cookie加载
├── configs/             # 配置文件目录
│   ├── zhihu_hot.json   # 知乎热榜配置
│   └── weibo_hot_search_browser.json # 微博热搜配置
├── results/             # 爬取结果保存目录
└── logs/               # 日志文件目录
```

## 🔧 安装依赖

### 使用 pip
```bash
pip install -r requirements.txt
```

### 使用 uv (推荐)
```bash
uv sync
```

### 依赖列表
- beautifulsoup4>=4.11.0 - HTML解析
- lxml>=4.9.0 - XML/HTML解析器
- requests>=2.28.0 - HTTP请求库
- selenium>=4.0.0 - 浏览器自动化

## 🎯 快速开始

### 1. 基本使用

```bash
# 爬取知乎热榜
python main.py -c configs/zhihu_hot.json

# 爬取微博热搜
python main.py -c configs/weibo_hot_search_browser.json
```

### 2. 高级选项

```bash
# 指定输出文件
python main.py -c configs/zhihu_hot.json -o my_results.json

# 开启详细日志
python main.py -c configs/zhihu_hot.json -v

# 只检查cookies
python main.py -c configs/zhihu_hot.json --check-cookies
```

## 📖 配置教程

SmartSpider 通过 JSON 配置文件定义爬取规则，支持以下配置模式：

### 1. 浏览器模式配置

适用于需要JavaScript渲染的动态网站：

```json
{
  "name": "爬虫名称",
  "mode": "browser",
  "base_url": "基础URL",
  "user_agent": "自定义User-Agent",
  "headers": {
    "Accept": "text/html,application/xhtml+xml...",
    "Accept-Language": "zh-CN,zh;q=0.9"
  },
  "cookies_file": "cookie文件路径（可选）",
  "timeout": 30,
  "delay": 2,
  "max_pages": 1,
  "list_page": {
    "item_selector": ".列表项选择器",
    "wait_selector": ".等待元素选择器",
    "fields": [
      {
        "name": "字段名称",
        "selector": ".元素选择器",
        "attribute": "text"
      }
    ]
  }
}
```

### 2. API模式配置

适用于提供API接口的网站：

```json
{
  "name": "爬虫名称",
  "mode": "api",
  "base_url": "API基础URL",
  "headers": {
    "Content-Type": "application/json"
  },
  "list_page": {
    "url_template": "API地址模板",
    "container_selector": "数据容器选择器",
    "item_selectors": {
      "字段名": "选择器"
    }
  }
}
```

## 📊 配置字段详解

### 基础配置字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| name | string | 是 | 爬虫名称，用于保存结果文件 |
| mode | string | 是 | 爬虫模式："browser" 或 "api" |
| base_url | string | 是 | 基础URL |
| user_agent | string | 否 | 自定义User-Agent |
| headers | object | 否 | 请求头配置 |
| cookies_file | string | 否 | Cookie文件路径 |
| timeout | number | 否 | 超时时间（秒），默认30 |
| delay | number | 否 | 请求延迟（秒），默认2 |
| max_pages | number | 否 | 最大页数，默认1 |
| proxy | string | 否 | 代理服务器配置 |

### 浏览器模式专用字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| list_page.item_selector | string | 列表项CSS选择器 |
| list_page.wait_selector | string | 等待元素CSS选择器 |
| list_page.fields | array | 字段提取规则 |
| detail_page | object | 详情页配置（可选） |

### 字段提取规则

| 字段名 | 类型 | 说明 |
|--------|------|------|
| name | string | 字段名称 |
| selector | string | CSS选择器 |
| attribute | string | 提取属性："text"、"href"、"src"等 |

### API模式专用字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| list_page.url_template | string | API地址模板 |
| list_page.container_selector | string | 数据容器选择器 |
| list_page.item_selectors | object | 字段选择器映射 |

## 📝 使用示例

### 示例1：知乎热榜爬取

```json
{
  "name": "zhihu_hot_list",
  "mode": "browser",
  "base_url": "https://www.zhihu.com/hot",
  "cookies_file": "zhihu_cookies.json",
  "list_page": {
    "item_selector": ".HotItem",
    "wait_selector": ".HotItem",
    "fields": [
      {"name": "rank", "selector": ".HotItem-rank", "attribute": "text"},
      {"name": "title", "selector": ".HotItem-title", "attribute": "text"},
      {"name": "excerpt", "selector": ".HotItem-excerpt", "attribute": "text"},
      {"name": "hot_score", "selector": ".HotItem-metrics", "attribute": "text"}
    ]
  }
}
```

### 示例2：微博热搜爬取

```json
{
  "name": "weibo_hot_search",
  "mode": "browser",
  "base_url": "https://s.weibo.com/top/summary",
  "list_page": {
    "container_selector": "#pl_top_realtimehot table tbody tr",
    "item_selectors": {
      "rank": "td.td-01",
      "title": "td.td-02 a",
      "url": "td.td-02 a",
      "hot_value": "td.td-02 span"
    }
  }
}
```

## 🔍 Cookie管理

### 获取Cookie

1. 手动获取：
   - 使用浏览器访问目标网站
   - 登录账号
   - 打开开发者工具（F12）
   - 在Application/Storage标签中找到Cookies
   - 导出为JSON格式

2. 使用浏览器插件：
   - 安装"EditThisCookie"等插件
   - 导出cookies为JSON格式

### Cookie文件格式

```json
[
  {
    "name": "login_token",
    "value": "your_token_here",
    "domain": ".zhihu.com"
  }
]
```

## 📁 输出格式

爬取结果自动保存为JSON文件，格式如下：

```json
[
  {
    "rank": "1",
    "title": "热门话题标题",
    "hot_score": "100万",
    "timestamp": "2024-01-01 12:00:00"
  }
]
```

文件命名规则：`{name}_{timestamp}.json`

## 🛠️ 高级功能

### 1. 分页爬取

支持自动分页爬取，配置`max_pages`和分页选择器：

```json
{
  "pagination": {
    "next_page_selector": ".next-page",
    "page_param": "page"
  }
}
```

### 2. 详情页爬取

支持先爬列表页，再爬详情页：

```json
{
  "detail_page": {
    "url_template": "https://example.com/item/{id}",
    "fields": [
      {"name": "content", "selector": ".content", "attribute": "text"}
    ]
  }
}
```

### 3. 代理配置

支持HTTP/HTTPS代理：

```json
{
  "proxy": {
    "http": "http://proxy.example.com:8080",
    "https": "https://proxy.example.com:8080"
  }
}
```

## 🐛 常见问题

### Q: 爬取结果为空？
A: 检查以下几点：
- Cookie是否有效（使用`--check-cookies`检查）
- 选择器是否正确
- 网络连接是否正常
- 是否被反爬（增加delay，更换User-Agent）

### Q: 浏览器模式启动慢？
A: 这是正常的，浏览器模式需要启动Chrome/Firefox。可以考虑：
- 使用API模式（如果网站支持）
- 使用无头模式（默认已启用）

### Q: 如何调试选择器？
A: 使用浏览器开发者工具：
1. 打开目标网页
2. 按F12打开开发者工具
3. 在Elements标签中使用选择器验证
4. 在Console中使用`document.querySelector()`测试

## 🔧 扩展开发

### 添加新的爬虫模式

1. 继承`BaseSpider`类：

```python
from core.base_spider import BaseSpider

class CustomSpider(BaseSpider):
    def crawl(self):
        # 实现爬取逻辑
        pass
```

2. 在`SpiderFactory`中注册：

```python
def create_spider(config_path):
    config = self.load_config(config_path)
    if config.mode == 'custom':
        return CustomSpider(config)
    # ... 其他模式
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

如有问题，请在GitHub Issues中提出。

---

**SmartSpider V3** - 让爬虫开发变得简单！

## 📚 相关文档

- [详细配置指南](CONFIG_GUIDE.md) - JSON配置的完整说明
- [使用教程](TUTORIAL.md) - 从零开始的完整教程