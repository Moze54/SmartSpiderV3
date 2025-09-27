# SmartSpider 配置文档

## 📋 概述

SmartSpider 使用 JSON 配置文件定义爬虫行为。配置文件包含基础设置、页面解析规则、分页策略、输出格式等关键信息。

## 🔧 基础配置结构

### 1. 基础信息配置

| 配置项 | 类型 | 必填 | 默认值 | 说明 | 示例 |
|--------|------|------|--------|------|------|
| `name` | string | ✅ | - | 爬虫名称，用于标识和输出文件名 | `"京东商品爬虫"` |
| `mode` | string | ✅ | "browser" | 爬虫模式："browser"(浏览器) 或 "api"(接口) | `"browser"` |
| `base_url` | string | ✅ | - | 起始爬取URL | `"https://search.jd.com/Search?keyword=手机"` |
| `user_agent` | string | ❌ | Chrome UA | 浏览器用户代理 | `"Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."` |
| `delay` | number | ❌ | 2 | 请求间隔时间(秒) | `2.5` |
| `timeout` | number | ❌ | 30 | 页面加载超时(秒) | `30` |
| `max_pages` | number | ❌ | 5 | 最大爬取页数 | `3` |
| `max_total_items` | number | ❌ | 100 | 最大爬取数据条数 | `50` |
| `concurrent` | number | ❌ | 1 | 并发线程数 | `3` |
| `retry_times` | number | ❌ | 3 | 重试次数 | `2` |
| `cookies_file` | string | ❌ | - | Cookie文件路径 | `"cookies/jd.json"` |
| `proxy` | string | ❌ | - | 代理服务器地址 | `"http://127.0.0.1:8080"` |

### 2. 列表页配置 (`list_page`)

#### 2.1 基础选择器配置

| 配置项 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `item_selector` | string | ✅ | 列表项CSS选择器 | `"#J_goodsList .gl-item"` |
| `wait_selector` | string | ✅ | 等待加载完成的CSS选择器 | `".gl-item"` |
| `url_selector` | string | ❌ | 详情页链接选择器 | `".p-name a"` |

#### 2.2 字段配置 (`fields`)

每个字段是一个对象，包含以下属性：

| 配置项 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `name` | string | ✅ | 字段名称 | `"title"` |
| `selector` | string | ✅ | CSS选择器 | `".p-name a em"` |
| `attribute` | string | ✅ | 提取属性："text", "html", 或属性名 | `"text"` |

#### 2.3 字段配置示例

```json
{
  "list_page": {
    "item_selector": ".product-item",
    "wait_selector": ".product-item",
    "fields": [
      {
        "name": "title",
        "selector": ".product-title",
        "attribute": "text"
      },
      {
        "name": "price",
        "selector": ".product-price",
        "attribute": "text"
      },
      {
        "name": "image_url",
        "selector": ".product-image img",
        "attribute": "src"
      },
      {
        "name": "product_url",
        "selector": ".product-link",
        "attribute": "href"
      }
    ]
  }
}
```

### 3. 详情页配置 (`detail_page`)

| 配置项 | 类型 | 必填 | 默认值 | 说明 | 示例 |
|--------|------|------|--------|------|------|
| `enabled` | boolean | ✅ | false | 是否启用详情页爬取 | `true` |
| `url_field` | string | ❌ | - | 从列表数据中获取详情页URL的字段名 | `"product_url"` |
| `fields` | array | ❌ | [] | 详情页字段配置（同list_page.fields） | 见示例 |

#### 详情页配置示例

```json
{
  "detail_page": {
    "enabled": true,
    "url_field": "product_url",
    "fields": [
      {
        "name": "brand",
        "selector": "#brand",
        "attribute": "text"
      },
      {
        "name": "description",
        "selector": ".product-description",
        "attribute": "html"
      },
      {
        "name": "specifications",
        "selector": "#spec-table",
        "attribute": "text"
      }
    ]
  }
}
```

### 4. 分页配置 (`pagination`)

#### 4.1 URL分页模式

| 配置项 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `type` | string | ✅ | 分页类型："url" | `"url"` |
| `param` | string | ✅ | URL参数名 | `"page"` |
| `page_size` | string | ❌ | 每页数量参数 | `"page_size"` |

```json
{
  "pagination": {
    "type": "url",
    "param": "page",
    "page_size": "s"
  }
}
```

#### 4.2 自定义分页配置 (`custom_pagination`)

支持多种特殊分页模式：

##### 动态滚动分页

| 配置项 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `type` | string | ✅ | - | 设为 "dynamic_scroll" |
| `scroll_pause_time` | number | ❌ | 2 | 滚动间隔时间(秒) |
| `max_scroll_attempts` | number | ❌ | 50 | 最大滚动次数 |

```json
{
  "custom_pagination": {
    "type": "dynamic_scroll",
    "scroll_pause_time": 3,
    "max_scroll_attempts": 30
  }
}
```

##### 小红书分页

| 配置项 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `type` | string | ✅ | - | 设为 "xiaohongshu" |
| `loading_selector` | string | ❌ | - | 加载中指示器选择器 |

```json
{
  "custom_pagination": {
    "type": "xiaohongshu",
    "loading_selector": ".loading-spinner"
  }
}
```

##### 点击加载更多

| 配置项 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `type` | string | ✅ | - | 设为 "click_more" |
| `load_more_selector` | string | ✅ | - | "加载更多"按钮选择器 |
| `max_clicks` | number | ❌ | 100 | 最大点击次数 |

### 5. 过滤配置 (`filters`)

| 配置项 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `price_range` | object | ❌ | 价格范围过滤 | 见示例 |
| `exclude_keywords` | array | ❌ | 排除关键词列表 | `["二手", "配件"]` |
| `include_keywords` | array | ❌ | 必须包含关键词 | `["正品", "官方"]` |

```json
{
  "filters": {
    "price_range": {
      "min": 0,
      "max": 5000
    },
    "exclude_keywords": ["二手", "配件", "山寨"],
    "include_keywords": ["正品", "官方", "旗舰店"]
  }
}
```

### 6. 输出配置

| 配置项 | 类型 | 必填 | 默认值 | 说明 | 示例 |
|--------|------|------|--------|------|------|
| `output_format` | string | ❌ | "json" | 输出格式："json", "csv", "xlsx" | `"json"` |
| `output_path` | string | ❌ | "output" | 输出文件路径 | `"output/jd_products"` |

## 🛠️ 配置模板

### 模板1：基础电商爬虫

```json
{
  "name": "基础电商爬虫模板",
  "mode": "browser",
  "base_url": "https://example-shop.com/search?q=商品关键词",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "delay": 2,
  "timeout": 30,
  "max_pages": 3,
  "max_total_items": 50,
  "concurrent": 1,
  "retry_times": 3,
  "cookies_file": "cookies.json",
  "list_page": {
    "item_selector": ".product-item",
    "wait_selector": ".product-item",
    "fields": [
      {"name": "title", "selector": ".product-title", "attribute": "text"},
      {"name": "price", "selector": ".product-price", "attribute": "text"},
      {"name": "shop", "selector": ".shop-name", "attribute": "text"},
      {"name": "url", "selector": ".product-link", "attribute": "href"}
    ]
  },
  "output_format": "json",
  "output_path": "output/products"
}
```

### 模板2：京东商品爬虫

```json
{
  "name": "京东商品爬虫",
  "mode": "browser",
  "base_url": "https://search.jd.com/Search?keyword=iPhone16&enc=utf-8",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
  "delay": 2.5,
  "timeout": 30,
  "max_pages": 3,
  "max_total_items": 30,
  "concurrent": 1,
  "retry_times": 3,
  "cookies_file": "jingdong.json",
  "list_page": {
    "item_selector": ".gl-item",
    "wait_selector": ".gl-item",
    "fields": [
      {"name": "title", "selector": ".p-name a em", "attribute": "text"},
      {"name": "price", "selector": ".p-price .J_price", "attribute": "text"},
      {"name": "shop", "selector": ".p-shop a", "attribute": "text"},
      {"name": "product_url", "selector": ".p-name a", "attribute": "href"},
      {"name": "image_url", "selector": ".p-img img", "attribute": "data-lazy-img"},
      {"name": "comments", "selector": ".p-commit strong", "attribute": "text"}
    ]
  },
  "detail_page": {
    "enabled": true,
    "url_field": "product_url",
    "fields": [
      {"name": "brand", "selector": "#parameter-brand li", "attribute": "text"},
      {"name": "specifications", "selector": "#parameter2", "attribute": "text"},
      {"name": "description", "selector": ".detail .tab-con", "attribute": "text"}
    ]
  },
  "custom_pagination": {
    "type": "dynamic_scroll",
    "scroll_pause_time": 3,
    "max_scroll_attempts": 20
  },
  "filters": {
    "price_range": {"min": 0, "max": 20000},
    "exclude_keywords": ["配件", "壳", "膜"]
  },
  "output_format": "json",
  "output_path": "output/jd_iphone16"
}
```

### 模板3：小红书笔记爬虫

```json
{
  "name": "小红书笔记爬虫",
  "mode": "browser",
  "base_url": "https://www.xiaohongshu.com/search_result?keyword=美妆",
  "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
  "delay": 4,
  "timeout": 30,
  "max_pages": 2,
  "max_total_items": 20,
  "concurrent": 1,
  "list_page": {
    "item_selector": ".note-item",
    "wait_selector": ".note-item",
    "fields": [
      {"name": "title", "selector": ".title", "attribute": "text"},
      {"name": "author", "selector": ".author-name", "attribute": "text"},
      {"name": "likes", "selector": ".like-count", "attribute": "text"},
      {"name": "note_url", "selector": ".note-link", "attribute": "href"}
    ]
  },
  "custom_pagination": {
    "type": "xiaohongshu",
    "loading_selector": ".loading-spinner"
  },
  "output_format": "json",
  "output_path": "output/xiaohongshu_notes"
}
```

### 模板4：并发爬虫配置

```json
{
  "name": "并发电商爬虫",
  "mode": "browser",
  "base_url": "https://example-shop.com/search?q=商品关键词",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "delay": 1.5,
  "timeout": 25,
  "max_pages": 5,
  "max_total_items": 100,
  "concurrent": 3,
  "retry_times": 2,
  "cookies_file": "cookies.json",
  "list_page": {
    "item_selector": ".product-item",
    "wait_selector": ".product-item",
    "fields": [
      {"name": "title", "selector": ".product-title", "attribute": "text"},
      {"name": "price", "selector": ".product-price", "attribute": "text"},
      {"name": "url", "selector": ".product-link", "attribute": "href"}
    ]
  },
  "pagination": {
    "type": "url",
    "param": "page"
  },
  "output_format": "json",
  "output_path": "output/concurrent_products"
}
```

## 🔍 CSS选择器指南

### 常用选择器示例

| 目标元素 | CSS选择器示例 | 说明 |
|----------|---------------|------|
| ID选择器 | `#product-title` | 选择ID为product-title的元素 |
| 类选择器 | `.product-price` | 选择class包含product-price的元素 |
| 属性选择器 | `img[data-src]` | 选择有data-src属性的img元素 |
| 后代选择器 | `.product .title` | 选择class为product元素内的.title |
| 子选择器 | `.product > .title` | 选择.product的直接子元素.title |
| 相邻兄弟 | `.price + .currency` | 选择紧接在.price后的.currency |
| 通用兄弟 | `.price ~ .info` | 选择.price后的所有.info兄弟元素 |

### 实际应用示例

```json
{
  "fields": [
    {
      "name": "商品标题",
      "selector": "#J_goodsList .gl-item .p-name a em",
      "attribute": "text"
    },
    {
      "name": "商品图片",
      "selector": ".gl-item .p-img img[data-lazy-img]",
      "attribute": "data-lazy-img"
    },
    {
      "name": "商品链接",
      "selector": ".gl-item .p-name a[href]",
      "attribute": "href"
    },
    {
      "name": "店铺名称",
      "selector": ".gl-item .p-shop a",
      "attribute": "text"
    }
  ]
}
```

## ⚡ 性能优化建议

### 1. 合理设置延迟
```json
{
  "delay": 2.0,  // 普通网站
  "delay": 3.5,  // 反爬严格的网站
  "delay": 1.0   // 本地测试
}
```

### 2. 并发设置
```json
{
  "concurrent": 1,   // 单线程，最稳定
  "concurrent": 3,   // 中等并发
  "concurrent": 5    // 高并发，需要更多资源
}
```

### 3. 超时设置
```json
{
  "timeout": 15,  // 快速响应
  "timeout": 30,  // 标准设置
  "timeout": 60   // 慢速网站
}
```

## 🛠️ 调试技巧

### 1. 验证选择器
使用浏览器开发者工具验证CSS选择器：
1. 打开浏览器开发者工具 (F12)
2. 切换到Elements/元素标签
3. 使用Ctrl+F搜索选择器
4. 确认选择器能正确匹配目标元素

### 2. 测试配置
```bash
# 测试单条配置
python main.py -c configs/test_config.json

# 检查cookies
python main.py -c configs/config.json --check-cookies

# 使用详细日志
python main.py -c configs/config.json -v
```

### 3. 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 获取不到数据 | 选择器错误 | 使用浏览器开发者工具验证选择器 |
| 登录失败 | Cookie无效 | 重新获取有效的Cookie文件 |
| 页面加载慢 | 超时设置短 | 增加timeout值 |
| 被反爬拦截 | 请求频率高 | 增加delay，使用代理 |

## 📁 文件结构示例

```
SmartSpiderV3/
├── configs/
│   ├── jd_iphone16.json          # 京东iPhone16爬虫
│   ├── jd_iphone16_simple.json   # 京东简化版
│   ├── xiaohongshu_notes.json    # 小红书笔记
│   └── test_reliable.json        # 测试配置
├── cookies/
│   ├── jingdong.json            # 京东Cookie
│   └── taobao.json              # 淘宝Cookie
├── output/
│   ├── jd_iphone16_20241201_143022.json
│   └── xiaohongshu_20241201_143500.json
└── logs/
    └── spider_20241201.log
```

## 🎯 最佳实践

1. **从小规模开始测试**：先用少量数据测试配置正确性
2. **逐步增加复杂度**：先爬取列表页，再添加详情页
3. **合理设置延迟**：避免过快的请求触发反爬
4. **定期更新选择器**：网站改版时需要更新CSS选择器
5. **使用Cookie保持会话**：登录状态的网站需要提供Cookie文件
6. **监控日志输出**：及时发现问题并调整配置