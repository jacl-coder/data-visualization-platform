# 数据分析与可视化平台

## 项目概述
本项目是一个基于Web的数据分析与可视化平台，专注于处理和展示用户行为与收入数据。通过处理原始CSV数据，计算用户LTV(Life Time Value)，并以直观的方式展示各种维度的统计指标，帮助业务决策者更好地理解数据。

## 特性
- 数据概览面板：展示用户数、事件数、设备数等关键指标
- 多维度数据分析：按国家、设备、时间等维度进行数据分析
- 用户LTV计算：基于af_purchase事件的用户生命周期价值计算
- 交互式图表：直观展示数据趋势和分布情况
- 详细数据表格：支持按日期查询详细数据

## 技术栈
### 前端
- **框架**：Vue 3
- **UI库**：Element Plus
- **图表库**：ECharts 5
- **状态管理**：Pinia
- **路由**：Vue Router 4
- **HTTP客户端**：Axios
- **构建工具**：Vite

### 后端
- **语言**：C++
- **Web框架**：Crow (或 Drogon/Oat++)
- **数据库交互**：SQLite C++ API (或 SQLiteCpp)

### 数据处理
- **语言**：Python 3.9+
- **数据分析库**：
  - pandas 2.2.3
  - numpy 2.0.2
  - matplotlib 3.9.4
  - seaborn 0.13.2
- **数据库**：SQLite 3.45.3

### 部署
- Shell 脚本

## 项目结构
```
data-visualization-platform/
├── backend/                       # C++后端
│   ├── src/                       # 源代码
│   │   ├── main.cpp               # 主程序入口
│   │   ├── ApiServer.cpp          # API服务器实现
│   │   └── DatabaseManager.cpp    # 数据库管理器实现
│   ├── include/                   # 头文件
│   │   ├── ApiServer.h            # API服务器声明
│   │   └── DatabaseManager.h      # 数据库管理器声明
│   ├── libs/                      # 第三方库
│   │   ├── crow/                  # Crow HTTP框架
│   │   └── nlohmann/              # JSON库
│   ├── build/                     # 构建目录
│   └── CMakeLists.txt             # CMake构建配置
├── frontend/                      # Vue 3前端
│   ├── src/                       # 源代码
│   │   ├── assets/                # 静态资源
│   │   │   ├── main.css           # 主样式文件
│   │   │   └── base.css           # 基础样式文件
│   │   ├── components/            # 可复用组件（暂无组件）
│   │   ├── api/                   # API服务
│   │   ├── stores/                # Pinia状态仓库（暂无状态）
│   │   ├── router/                # Vue Router配置
│   │   │   └── index.ts           # 路由配置文件
│   │   ├── views/                 # 页面视图（暂无视图）
│   │   ├── App.vue                # 应用入口组件
│   │   └── main.ts                # 应用初始化
│   ├── public/                    # 公共文件
│   │   └── favicon.ico            # 网站图标
│   ├── index.html                 # HTML入口文件
│   ├── package.json               # npm配置文件
│   ├── tsconfig.json              # TypeScript配置
│   ├── tsconfig.app.json          # 应用TypeScript配置
│   ├── tsconfig.node.json         # Node环境TypeScript配置
│   ├── env.d.ts                   # 环境类型声明
│   ├── eslint.config.ts           # ESLint配置
│   ├── vite.config.ts             # Vite构建配置
│   └── .gitignore                 # Git忽略配置
├── data_processing/               # Python数据处理
│   ├── main.py                    # 主处理脚本
│   ├── process_data.py            # CSV数据处理与导入
│   ├── create_database.py         # 数据库创建
│   ├── calculate_ltv.py           # LTV计算
│   └── requirements.txt           # Python依赖
├── database/                      # 数据库文件
│   └── app.db                     # SQLite数据库
├── scripts/                       # 部署脚本（待开发）
├── 后端考核/                      # 原始数据和需求
│   ├── test.csv                   # 测试数据集
│   ├── 题目说明.txt               # 项目需求说明
│   ├── 源数据说明.txt             # 数据字段说明
│   ├── 首页.png                   # UI设计参考
│   └── 详情.png                   # UI设计参考
├── README.md                      # 项目说明文档
└── PROJECT_PROGRESS.md            # 项目进度文档
```

## 安装与使用

### 环境要求
- Python 3.9+（已在 Python 3.9.21 上测试）
- Node.js 14+（已在 Node.js 18.19.1 上测试）
- npm 9.2.0+
- C++ 编译器（支持C++17，已在 GCC 13.3.0 上测试）
- CMake 3.20+（已在 CMake 3.28.3 上测试）
- SQLite 3.35+（已在 SQLite 3.45.3 上测试）

### 已测试环境
- 操作系统：Ubuntu Linux（内核 6.11.0）
- Python：3.9.21
- Node.js：18.19.1
- npm：9.2.0
- GCC：13.3.0
- CMake：3.28.3
- SQLite：3.45.3

### 快速开始

1. 克隆仓库
```bash
git clone https://github.com/yourusername/data-visualization-platform.git
cd data-visualization-platform
```

2. 创建Python虚拟环境（推荐）
```bash
# 使用conda创建虚拟环境
conda create -n data_viz python=3.9
conda activate data_viz

# 或使用venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装Python依赖
```bash
# 安装指定版本的依赖（推荐）
pip install -r data_processing/requirements.txt

# 如果遇到版本兼容性问题，可以尝试安装兼容版本
# pip install pandas numpy matplotlib seaborn
```

4. 数据处理与数据库生成
```bash
# 运行主处理脚本，一次完成所有数据处理步骤
python data_processing/main.py

# 或分步执行
python data_processing/create_database.py    # 创建数据库结构
python data_processing/process_data.py       # 处理CSV数据
python data_processing/calculate_ltv.py      # 计算LTV
```

5. 一键安装与启动（后续步骤）
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

该脚本会自动执行以下操作：
- 安装所需依赖
- 处理CSV数据并导入SQLite（如果尚未完成）
- 编译C++后端
- 安装前端依赖并构建
- 启动后端和前端服务
- 打开浏览器访问应用

### 数据处理详解

数据处理模块已经完成，它执行以下操作：

1. **创建数据库结构**：创建包含用户、事件、购买和统计数据的表结构
2. **数据预处理**：处理CSV文件中的字段，包括：
   - 日期时间格式化
   - 设备类别提取
   - 货币转换为USD
   - 事件参数提取
3. **用户LTV计算**：基于购买事件计算用户的：
   - 1天、7天、14天、30天、60天、90天LTV
   - 总LTV和购买次数
4. **统计数据生成**：生成多个维度的汇总数据：
   - 日期维度（用户数、事件数、收入等）
   - 国家维度
   - 设备维度

### 手动安装

1. 安装依赖
```bash
# 安装Python依赖
pip install -r data_processing/requirements.txt

# 安装前端依赖
cd frontend
npm install
cd ..

# 编译后端
cd backend
mkdir -p build && cd build
cmake ..
make
cd ../..
```

2. 启动服务
```bash
# 启动后端服务
cd backend/build
./data_visualization_backend

# 启动前端开发服务器 (在新的终端窗口)
cd frontend
npm run dev
```

3. 访问应用
打开浏览器访问 http://localhost:5173

## 数据库设计
系统使用SQLite数据库，主要包含以下表：

### 事件表 (events)
存储从CSV导入的原始事件数据。
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appsflyer_id TEXT NOT NULL,                -- 用户ID
    event_name TEXT NOT NULL,                  -- 事件名称
    event_value TEXT,                          -- 事件值
    created_date DATE NOT NULL,                -- 事件日期
    event_time DATETIME,                       -- 事件时间
    country_code TEXT,                         -- 国家代码
    device_model TEXT,                         -- 设备型号
    device_category TEXT,                      -- 设备类别(mobile_phone, tablet等)
    app_id TEXT,                               -- 应用ID
    platform TEXT,                             -- 平台(android, ios等)
    media_source TEXT,                         -- 媒体来源
    event_revenue REAL,                        -- 原始收入金额
    event_revenue_currency TEXT,               -- 收入货币类型
    event_revenue_usd REAL,                    -- 统一为USD的收入
    event_params TEXT,                         -- 事件参数(JSON格式)
    install_time DATETIME                      -- 安装时间
);
```

### 用户表 (users)
存储用户的基本信息。
```sql
CREATE TABLE users (
    appsflyer_id TEXT PRIMARY KEY,             -- 用户ID
    first_seen_date DATE NOT NULL,             -- 首次出现日期
    last_seen_date DATE NOT NULL,              -- 最后出现日期
    country_code TEXT,                         -- 国家代码
    device_model TEXT,                         -- 设备型号
    device_category TEXT,                      -- 设备类别
    platform TEXT,                             -- 平台
    media_source TEXT,                         -- 用户来源
    install_time DATETIME                      -- 安装时间
);
```

### 购买表 (purchases)
专门存储购买事件数据，优化LTV计算。
```sql
CREATE TABLE purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appsflyer_id TEXT NOT NULL,                -- 用户ID
    purchase_time DATETIME NOT NULL,           -- 购买时间
    created_date DATE NOT NULL,                -- 购买日期
    country_code TEXT,                         -- 国家代码
    device_category TEXT,                      -- 设备类别
    event_revenue_usd REAL NOT NULL,           -- USD收入金额
    product_id TEXT,                           -- 产品ID
    order_id TEXT,                             -- 订单ID
    FOREIGN KEY (appsflyer_id) REFERENCES users(appsflyer_id)
);
```

### 用户LTV表 (user_ltv)
存储计算好的用户LTV(生命周期价值)数据。
```sql
CREATE TABLE user_ltv (
    appsflyer_id TEXT PRIMARY KEY,              -- 用户ID
    first_purchase_date DATE,                   -- 首次购买日期
    ltv_1d REAL DEFAULT 0,                      -- 1天LTV
    ltv_7d REAL DEFAULT 0,                      -- 7天LTV
    ltv_14d REAL DEFAULT 0,                     -- 14天LTV
    ltv_30d REAL DEFAULT 0,                     -- 30天LTV
    ltv_60d REAL DEFAULT 0,                     -- 60天LTV
    ltv_90d REAL DEFAULT 0,                     -- 90天LTV
    ltv_total REAL DEFAULT 0,                   -- 总LTV
    purchase_count INTEGER DEFAULT 0,           -- 购买次数
    last_purchase_date DATE,                    -- 最后购买日期
    FOREIGN KEY (appsflyer_id) REFERENCES users(appsflyer_id)
);
```

### 每日统计表 (daily_stats)
按日期汇总的统计数据。
```sql
CREATE TABLE daily_stats (
    stat_date DATE PRIMARY KEY,                 -- 统计日期
    user_count INTEGER DEFAULT 0,               -- 用户数
    new_user_count INTEGER DEFAULT 0,           -- 新用户数
    event_count INTEGER DEFAULT 0,              -- 事件数
    purchase_count INTEGER DEFAULT 0,           -- 购买数
    revenue_usd REAL DEFAULT 0,                 -- USD收入
    device_count INTEGER DEFAULT 0,             -- 设备数量
    country_count INTEGER DEFAULT 0             -- 国家数量
);
```

### 国家维度统计表 (country_stats)
按国家分组的统计数据。
```sql
CREATE TABLE country_stats (
    stat_date DATE NOT NULL,                    -- 统计日期
    country_code TEXT NOT NULL,                 -- 国家代码
    user_count INTEGER DEFAULT 0,               -- 用户数
    event_count INTEGER DEFAULT 0,              -- 事件数
    revenue_usd REAL DEFAULT 0,                 -- USD收入
    PRIMARY KEY (stat_date, country_code)
);
```

### 设备维度统计表 (device_stats)
按设备类型分组的统计数据。
```sql
CREATE TABLE device_stats (
    stat_date DATE NOT NULL,                    -- 统计日期
    device_category TEXT NOT NULL,              -- 设备类别
    user_count INTEGER DEFAULT 0,               -- 用户数
    event_count INTEGER DEFAULT 0,              -- 事件数
    revenue_usd REAL DEFAULT 0,                 -- USD收入
    PRIMARY KEY (stat_date, device_category)
);
```

### 货币转换表 (currency_rates)
存储各种货币对USD的转换率。
```sql
CREATE TABLE currency_rates (
    currency_code TEXT PRIMARY KEY,             -- 货币代码
    rate_to_usd REAL NOT NULL,                  -- 对USD的汇率
    last_updated DATETIME NOT NULL              -- 最后更新时间
);
```

### 索引优化
为提高查询性能，数据库中创建了以下索引：
- 事件表：创建日期、用户ID、事件名称、国家/设备组合的索引
- 用户表：国家/设备组合、首次出现日期的索引
- 购买表：用户ID、创建日期、国家/设备组合的索引
- 统计表：日期索引

## API接口
后端提供以下REST API接口，所有接口均返回统一的JSON响应格式：

### 统一响应格式
所有API响应都使用以下统一格式：
```json
{
  "status": "success",  // 或 "error"
  "code": 200,          // HTTP状态码
  "message": "操作成功", // 人类可读的消息
  "data": {             // 实际数据内容
    // 数据对象或数组
  }
}
```

对于返回数组的接口，data字段包含以下结构：
```json
{
  "items": [],    // 实际数据数组
  "total": 0      // 数组项目总数
}
```

当发生错误时，响应格式如下：
```json
{
  "status": "error",
  "code": 500,          // 错误代码
  "message": "错误信息",
  "data": null
}
```

### 根路径 (/)
```
GET /
返回API服务器信息，用于检查服务器是否正常运行。
```
示例响应：
```json
{
  "status": "success",
  "code": 200,
  "message": "API服务器运行正常",
  "data": "Data Visualization API Server"
}
```

### 数据概览 (/api/overview)
```
GET /api/overview
返回整体统计数据，包括用户数、事件数、设备数和总收入。
```
示例响应：
```json
{
  "status": "success",
  "code": 200,
  "message": "概览数据获取成功",
  "data": {
    "user_count": 83,
    "event_count": 491,
    "device_count": 11,
    "total_revenue": 13242.27
  }
}
```

### 时间维度数据 (/api/timeline)
```
GET /api/timeline?days=30
返回最近N天的时间序列数据，包括每天的用户数、事件数和收入。
```
参数:
- `days`: 可选，要返回的天数，默认30天

示例响应：
```json
{
  "status": "success",
  "code": 200,
  "message": "时间线数据获取成功",
  "data": {
    "items": [
      {"date": "2025-04-10", "event_count": 1, "revenue": 5.99, "user_count": 1},
      // 更多日期数据...
    ],
    "total": 30
  }
}
```

### 国家维度数据 (/api/country)
```
GET /api/country
返回按国家分组的统计数据，包括用户数和收入，按收入降序排列。
```
示例响应：
```json
{
  "status": "success",
  "code": 200,
  "message": "国家维度数据获取成功",
  "data": {
    "items": [
      {"country": "HK", "revenue": 3367.31, "users": 32},
      // 更多国家数据...
    ],
    "total": 14
  }
}
```

### 设备维度数据 (/api/device)
```
GET /api/device
返回按设备分组的统计数据，包括用户数和收入，按收入降序排列。
```
示例响应：
```json
{
  "status": "success",
  "code": 200,
  "message": "设备维度数据获取成功",
  "data": {
    "items": [
      {"device": "samsung", "revenue": 9886.38, "users": 79},
      // 更多设备数据...
    ],
    "total": 11
  }
}
```

### 详细数据 (/api/details)
```
GET /api/details?date=YYYY-MM-DD
返回指定日期的详细数据，包括国家和设备维度的用户分布。
```
参数:
- `date`: 必填，指定查询的日期，格式为YYYY-MM-DD

返回值说明:
- 当指定日期没有数据时，`total_revenue`将返回0，`countries`和`devices`将返回空数组
- 所有数值型字段保证不会返回NULL，空值将默认为0
- 当指定日期无效或缺少时，将返回500错误

示例响应：
```json
{
  "status": "success",
  "code": 200,
  "message": "日期详情数据获取成功",
  "data": {
    "date": "2025-04-09",
    "total_revenue": 5.99,
    "countries": [
      {"country": "US", "users": 1}
    ],
    "devices": [
      {"device": "tcl", "users": 1}
    ]
  }
}
```

### 跨域资源共享 (CORS) 支持
所有API端点都支持跨域资源共享，允许从任何源发起请求。支持的HTTP方法包括GET、POST、PUT、DELETE和OPTIONS。响应头中包含以下CORS相关设置：

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept, Authorization
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400
```

## 许可证
MIT 