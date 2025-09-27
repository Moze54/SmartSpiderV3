# SmartSpider V3 - 使用教程

本教程将带您从零开始学习如何使用SmartSpider V3，包括环境配置、创建第一个爬虫、高级功能使用等。

## 📚 目录

1. [环境准备](#环境准备)
2. [快速上手](#快速上手)
3. [创建第一个爬虫](#创建第一个爬虫)
4. [Cookie配置](#Cookie配置)
5. [选择器调试](#选择器调试)
6. [高级功能](#高级功能)
7. [故障排除](#故障排除)
8. [实战案例](#实战案例)

## 🔧 环境准备

### 1. 系统要求

- **Python版本**: 3.10或更高版本
- **操作系统**: Windows 10/11, macOS, Linux
- **网络**: 稳定的互联网连接

### 2. 安装步骤

#### Windows系统

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/SmartSpiderV3.git
cd SmartSpiderV3

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证安装
python --version
python -c "import requests; print('依赖安装成功')"
```

#### macOS/Linux系统

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/SmartSpiderV3.git
cd SmartSpiderV3

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证安装
python3 --version
python3 -c "import requests; print('依赖安装成功')"
```

#### 使用uv（推荐）

```bash
# 1. 安装uv
curl -Ls https://astral.sh/uv/install.sh | sh

# 2. 同步依赖
uv sync

# 3. 运行项目
uv run python main.py --help
```

### 3. 浏览器驱动安装

#### Chrome浏览器

1. 查看Chrome版本：打开Chrome → 设置 → 关于Chrome
2. 下载对应版本的ChromeDriver：[ChromeDriver下载](https://chromedriver.chromium.org/downloads)
3. 将chromedriver添加到系统PATH

#### 验证驱动

```bash
# 测试ChromeDriver
chromedriver --version

# 测试Selenium
python -c "from selenium import webdriver; print('Selenium可用')"
```

## 🚀 快速上手

### 1. 运行内置示例

```bash
# 爬取知乎热榜
cd SmartSpiderV3
python main.py -c configs/zhihu_hot.json -v

# 爬取微博热搜
python main.py -c configs/weibo_hot_search_browser.json -v
```

### 2. 查看结果

```bash
# 查看爬取结果
ls results/
cat results/zhihu_hot_list_*.json | head -20

# 查看日志
tail -f logs/spider.log
```

## 🎯 创建第一个爬虫

### 1. 选择目标网站

以爬取**豆瓣电影Top250**为例：

### 2. 分析网站结构

1. 打开豆瓣电影Top250：https://movie.douban.com/top250
2. 按F12打开开发者工具
3. 分析页面结构：
   - 电影列表：`.item`
   - 电影名称：`.title`
   - 评分：`.rating_num`
   - 评价人数：`.star span:nth-child(4)`
   - 链接：`.pic a`

### 3. 创建配置文件

创建文件 `configs/douban_top250.json`：

```json
{
  "name": "douban_top250",
  "mode": "browser",
  "base_url": "https://movie.douban.com",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "headers": {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
  },
  "timeout": 30,
  "delay": 2,
  "max_pages": 10,
  "pagination": {
    "enabled": true,
    "page_param": "start",
    "page_size": 25,
    "max_pages": 10
  },
  "list_page": {
    "url_template": "https://movie.douban.com/top250?start={start}",
    "item_selector": ".item",
    "wait_selector": ".item",
    "fields": [
      {
        "name": "rank",
        "selector": ".pic em",
        "attribute": "text"
      },
      {
        "name": "title",
        "selector": ".title",
        "attribute": "text"
      },
      {
        "name": "rating",
        "selector": ".rating_num",
        "attribute": "text"
      },
      {
        "name": "review_count",
        "selector": ".star span:last-child",
        "attribute": "text"
      },
      {
        "name": "url",
        "selector": ".pic a",
        "attribute": "href"
      },
      {
        "name": "image_url",
        "selector": ".pic img",
        "attribute": "src"
      }
    ]
  }
}
```

### 4. 运行爬虫

```bash
# 运行爬虫
python main.py -c configs/douban_top250.json -v

# 指定输出文件
python main.py -c configs/douban_top250.json -o douban_results.json
```

### 5. 查看结果

```bash
# 查看爬取结果
cat results/douban_top250_*.json | jq '.[] | {rank, title, rating}'

# 统计结果数量
jq '. | length' results/douban_top250_*.json
```

## 🍪 Cookie配置教程

### 1. 何时需要Cookie

需要Cookie的情况：
- 登录后才能访问的内容
- 个性化推荐内容
- 反爬机制较强的网站
- 需要用户认证的功能

### 2. 获取Cookie的详细步骤

#### 方法1：浏览器开发者工具

**Chrome浏览器：**

1. 打开目标网站（如知乎）
2. 登录您的账号
3. 按F12打开开发者工具
4. 切换到Application/Storage标签
5. 点击Cookies -> https://www.zhihu.com
6. 右键点击任意cookie，选择"Copy all"
7. 粘贴到 `zhihu_cookies.json` 文件中

**具体操作：**

```json
[
  {
    "name": "z_c0",
    "value": "你的z_c0值",
    "domain": ".zhihu.com",
    "path": "/"
  },
  {
    "name": "_xsrf",
    "value": "你的_xsrf值",
    "domain": ".zhihu.com",
    "path": "/"
  }
]
```

#### 方法2：使用浏览器插件

**安装EditThisCookie插件：**

1. Chrome网上应用店搜索"EditThisCookie"
2. 安装插件
3. 打开目标网站并登录
4. 点击插件图标
5. 点击"导出"按钮
6. 保存为JSON文件

#### 方法3：使用开发者工具控制台

```javascript
// 在浏览器控制台执行
(function(){
    var cookies = document.cookie.split(';');
    var cookieArray = [];
    cookies.forEach(function(cookie) {
        var parts = cookie.trim().split('=');
        cookieArray.push({
            name: parts[0],
            value: parts[1],
            domain: window.location.hostname,
            path: '/'
        });
    });
    console.log(JSON.stringify(cookieArray, null, 2));
})();
```

### 3. 验证Cookie有效性

```bash
# 检查Cookie
python main.py -c configs/zhihu_hot.json --check-cookies

# 输出示例
# [INFO] 当前cookies数量: 15
# [INFO] Cookie: z_c0=Mi4xR3h... (有效的Cookie信息)
```

## 🔍 选择器调试指南

### 1. 使用浏览器开发者工具

#### 步骤1：打开开发者工具
- Windows: F12 或 Ctrl+Shift+I
- macOS: Cmd+Option+I

#### 步骤2：使用Elements面板
1. 右键点击要爬取的内容
2. 选择"检查"或"Inspect"
3. 在Elements面板中查看HTML结构

#### 步骤3：测试选择器
在Console面板中输入：

```javascript
// 测试CSS选择器
document.querySelector('.HotItem-title')

// 测试多个元素
document.querySelectorAll('.HotItem')

// 获取文本内容
document.querySelector('.HotItem-title').textContent

// 获取属性
document.querySelector('.HotItem-title a').href
```

### 2. 选择器调试工具

#### Python调试脚本

创建 `debug_selector.py`：

```python
#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def debug_with_requests(url, selector):
    """使用requests调试选择器"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    elements = soup.select(selector)
    print(f"选择器: {selector}")
    print(f"找到元素数量: {len(elements)}")

    for i, element in enumerate(elements[:3]):
        print(f"元素 {i+1}:")
        print(f"  文本: {element.get_text().strip()}")
        print(f"  HTML: {str(element)[:100]}...")

    return elements

def debug_with_selenium(url, selector):
    """使用Selenium调试选择器"""
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(3)  # 等待页面加载

        elements = driver.find_elements_by_css_selector(selector)
        print(f"选择器: {selector}")
        print(f"找到元素数量: {len(elements)}")

        for i, element in enumerate(elements[:3]):
            print(f"元素 {i+1}:")
            print(f"  文本: {element.text}")
            print(f"  属性: {element.get_attribute('class')}")

    finally:
        driver.quit()

# 使用示例
if __name__ == "__main__":
    url = "https://www.zhihu.com/hot"
    selector = ".HotItem-title"

    print("=== 调试知乎热榜选择器 ===")
    debug_with_selenium(url, selector)
```

### 3. 常见选择器问题

#### 问题1：选择器找不到元素

**解决方案：**
1. 检查选择器语法是否正确
2. 确认元素是否存在于页面中
3. 等待页面完全加载
4. 检查是否有iframe嵌套

#### 问题2：动态内容加载

**解决方案：**
```json
{
  "list_page": {
    "wait_selector": ".loading-spinner",
    "wait_time": 5
  }
}
```

#### 问题3：选择器不稳定

**解决方案：**
- 使用多个备用选择器
- 使用更稳定的属性选择器
- 使用相对路径选择器

## 🚀 高级功能使用

### 1. 分页爬取

#### 示例：爬取多页商品

创建 `configs/jd_products.json`：

```json
{
  "name": "jd_products",
  "mode": "browser",
  "base_url": "https://search.jd.com",
  "timeout": 30,
  "delay": 3,
  "max_pages": 5,
  "pagination": {
    "enabled": true,
    "type": "param",
    "page_param": "page",
    "start_page": 1,
    "page_size": 60
  },
  "list_page": {
    "url_template": "https://search.jd.com/Search?keyword=手机&page={page}",
    "item_selector": ".gl-item",
    "wait_selector": ".gl-item",
    "fields": [
      {"name": "title", "selector": ".p-name em", "attribute": "text"},
      {"name": "price", "selector": ".p-price i", "attribute": "text"},
      {"name": "shop", "selector": ".p-shop a", "attribute": "text"},
      {"name": "url", "selector": ".p-name a", "attribute": "href"},
      {"name": "image", "selector": ".p-img img", "attribute": "src"}
    ]
  }
}
```

### 2. 详情页爬取

#### 示例：爬取详情信息

创建 `configs/news_detail.json`：

```json
{
  "name": "news_detail",
  "mode": "browser",
  "base_url": "https://news.example.com",
  "timeout": 30,
  "delay": 2,
  "list_page": {
    "item_selector": ".news-item",
    "fields": [
      {"name": "title", "selector": ".title", "attribute": "text"},
      {"name": "summary", "selector": ".summary", "attribute": "text"},
      {"name": "url", "selector": "a.title-link", "attribute": "href"}
    ]
  },
  "detail_page": {
    "enabled": true,
    "url_field": "url",
    "fields": [
      {"name": "content", "selector": ".article-content", "attribute": "text"},
      {"name": "author", "selector": ".author-name", "attribute": "text"},
      {"name": "publish_time", "selector": ".publish-time", "attribute": "text"},
      {"name": "tags", "selector": ".article-tags a", "attribute": "text"},
      {"name": "read_count", "selector": ".read-count", "attribute": "text"}
    ]
  }
}
```

### 3. 代理配置

#### 创建代理配置

创建 `configs/proxy_config.json`：

```json
{
  "name": "proxy_spider",
  "mode": "browser",
  "base_url": "https://httpbin.org",
  "proxy": {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
  },
  "timeout": 30,
  "list_page": {
    "url_template": "https://httpbin.org/ip",
    "item_selector": "body",
    "fields": [
      {"name": "ip", "selector": "pre", "attribute": "text"}
    ]
  }
}
```

### 4. 数据导出格式

#### 自定义输出格式

```bash
# 导出为CSV格式（使用jq工具）
jq -r 'map({rank, title, rating}) | (map(keys) | add | unique) as $cols | map(. as $row | $cols | map($row[.])) as $rows | $cols, $rows[] | @csv' results/douban_top250_*.json

# 导出为Excel格式（使用Python脚本）
python scripts/export_excel.py results/douban_top250_*.json output.xlsx
```

## 🔧 故障排除

### 1. 常见问题列表

| 问题描述 | 可能原因 | 解决方案 |
|----------|----------|----------|
| 找不到元素 | 选择器错误 | 使用浏览器验证选择器 |
| 页面加载超时 | 网络问题 | 增加timeout值 |
| 登录失败 | Cookie失效 | 重新获取Cookie |
| 数据为空 | 反爬机制 | 添加User-Agent和延迟 |
| 内存不足 | 数据量太大 | 分批处理或减少页数 |

### 2. 调试模式

#### 启用详细日志

```bash
# 开启详细日志
python main.py -c config.json -v

# 调试特定模块
python -m pdb main.py -c config.json
```

#### 日志分析

```bash
# 查看错误日志
grep ERROR logs/spider.log

# 查看爬取统计
grep "爬取完成" logs/spider.log

# 实时监控日志
tail -f logs/spider.log | grep -E "(ERROR|WARNING)"
```

### 3. 性能优化

#### 优化配置参数

```json
{
  "timeout": 15,
  "delay": 1,
  "max_pages": 3,
  "concurrent_requests": 5,
  "cache_enabled": true,
  "headless": true
}
```

#### 系统级优化

```bash
# 增加系统文件描述符限制
ulimit -n 65536

# 优化Chrome参数
export CHROME_OPTIONS="--no-sandbox --disable-dev-shm-usage --disable-gpu"
```

## 📊 实战案例

### 案例1：爬取知乎用户动态

#### 目标
爬取知乎用户最近回答的问题

#### 步骤

1. **分析页面结构**
   - 用户主页：`https://www.zhihu.com/people/{username}/answers`
   - 回答列表：`.ContentItem.AnswerItem`
   - 回答内容：`.RichContent`

2. **创建配置文件**

创建 `configs/zhihu_user_answers.json`：

```json
{
  "name": "zhihu_user_answers",
  "mode": "browser",
  "base_url": "https://www.zhihu.com",
  "cookies_file": "zhihu_cookies.json",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
  "timeout": 30,
  "delay": 3,
  "max_pages": 5,
  "list_page": {
    "url_template": "https://www.zhihu.com/people/{username}/answers?page={page}",
    "item_selector": ".ContentItem.AnswerItem",
    "wait_selector": ".ContentItem.AnswerItem",
    "fields": [
      {
        "name": "question",
        "selector": ".QuestionItem-title",
        "attribute": "text"
      },
      {
        "name": "answer_url",
        "selector": ".AnswerItem-meta a",
        "attribute": "href"
      },
      {
        "name": "vote_count",
        "selector": ".VoteButton--up",
        "attribute": "text"
      },
      {
        "name": "create_time",
        "selector": ".ContentItem-time",
        "attribute": "text"
      }
    ]
  },
  "detail_page": {
    "enabled": true,
    "url_field": "answer_url",
    "fields": [
      {
        "name": "content",
        "selector": ".RichContent-inner",
        "attribute": "text"
      },
      {
        "name": "comment_count",
        "selector": ".Button--plain",
        "attribute": "text"
      }
    ]
  }
}
```

3. **运行爬虫**

```bash
# 替换{username}为实际用户名
python main.py -c configs/zhihu_user_answers.json -v
```

### 案例2：爬取微博热搜

#### 目标
爬取微博实时热搜榜

#### 配置文件

创建 `configs/weibo_trending.json`：

```json
{
  "name": "weibo_trending",
  "mode": "browser",
  "base_url": "https://s.weibo.com",
  "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)...",
  "headers": {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9"
  },
  "timeout": 30,
  "delay": 2,
  "max_pages": 1,
  "list_page": {
    "url_template": "https://s.weibo.com/top/summary",
    "item_selector": "#pl_top_realtimehot table tbody tr",
    "wait_selector": "#pl_top_realtimehot",
    "fields": [
      {
        "name": "rank",
        "selector": "td.td-01",
        "attribute": "text"
      },
      {
        "name": "keyword",
        "selector": "td.td-02 a",
        "attribute": "text"
      },
      {
        "name": "url",
        "selector": "td.td-02 a",
        "attribute": "href"
      },
      {
        "name": "hot_value",
        "selector": "td.td-02 span",
        "attribute": "text"
      },
      {
        "name": "tag",
        "selector": "td.td-03 i",
        "attribute": "class"
      }
    ]
  }
}
```

### 案例3：爬取商品信息

#### 目标
爬取淘宝商品信息

#### 注意事项
- 淘宝反爬较强，需要特殊处理
- 建议使用搜索页面而非首页

#### 配置文件

创建 `configs/taobao_products.json`：

```json
{
  "name": "taobao_products",
  "mode": "browser",
  "base_url": "https://s.taobao.com",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
  "headers": {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9"
  },
  "timeout": 30,
  "delay": 5,
  "max_pages": 3,
  "pagination": {
    "enabled": true,
    "page_param": "s",
    "start_page": 0,
    "page_size": 44
  },
  "list_page": {
    "url_template": "https://s.taobao.com/search?q=手机&s={start}",
    "item_selector": ".item.J_MouserOnverReq",
    "wait_selector": ".item.J_MouserOnverReq",
    "fields": [
      {
        "name": "title",
        "selector": ".title a",
        "attribute": "text"
      },
      {
        "name": "price",
        "selector": ".price .num",
        "attribute": "text"
      },
      {
        "name": "shop",
        "selector": ".shop a",
        "attribute": "text"
      },
      {
        "name": "sales",
        "selector": ".deal-cnt",
        "attribute": "text"
      },
      {
        "name": "location",
        "selector": ".location",
        "attribute": "text"
      }
    ]
  }
}
```

## 🎉 总结

通过以上教程，您已经学会了：

1. ✅ 环境配置和依赖安装
2. ✅ 创建和运行基础爬虫
3. ✅ Cookie配置和验证
4. ✅ 选择器调试技巧
5. ✅ 分页和详情页爬取
6. ✅ 代理和反爬配置
7. ✅ 故障排除和性能优化

### 下一步学习

- 阅读 [CONFIG_GUIDE.md](CONFIG_GUIDE.md) 了解详细配置
- 查看项目示例配置
- 尝试爬取您感兴趣的网站
- 参与项目贡献和优化

### 获取帮助

- 📖 查看完整配置文档：[CONFIG_GUIDE.md](CONFIG_GUIDE.md)
- 🐛 报告问题：提交GitHub Issue
- 💬 讨论交流：加入项目讨论组
- 📧 联系维护者：通过GitHub联系

---

**祝您爬取愉快！记得遵守网站的robots.txt规则和法律法规。**