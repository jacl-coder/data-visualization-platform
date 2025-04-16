#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库创建脚本
用于创建SQLite数据库和所有必要的表结构
"""

import os
import sqlite3
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据库目录和文件
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database')
DB_FILE = os.path.join(DB_DIR, 'app.db')

# 确保数据库目录存在
os.makedirs(DB_DIR, exist_ok=True)

# 创建表的SQL语句
CREATE_TABLES_SQL = """
-- 事件表，存储所有原始事件数据
CREATE TABLE IF NOT EXISTS events (
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

-- 用户表，存储用户基本信息
CREATE TABLE IF NOT EXISTS users (
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

-- 购买事件表，专门用于存储购买事件，优化LTV计算
CREATE TABLE IF NOT EXISTS purchases (
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

-- 用户LTV表，存储计算好的用户终身价值数据
CREATE TABLE IF NOT EXISTS user_ltv (
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

-- 日报表，按日汇总的统计数据
CREATE TABLE IF NOT EXISTS daily_stats (
    stat_date DATE PRIMARY KEY,                 -- 统计日期
    user_count INTEGER DEFAULT 0,               -- 用户数
    new_user_count INTEGER DEFAULT 0,           -- 新用户数
    event_count INTEGER DEFAULT 0,              -- 事件数
    purchase_count INTEGER DEFAULT 0,           -- 购买数
    revenue_usd REAL DEFAULT 0,                 -- USD收入
    device_count INTEGER DEFAULT 0,             -- 设备数量
    country_count INTEGER DEFAULT 0             -- 国家数量
);

-- 国家维度统计表
CREATE TABLE IF NOT EXISTS country_stats (
    stat_date DATE NOT NULL,                    -- 统计日期
    country_code TEXT NOT NULL,                 -- 国家代码
    user_count INTEGER DEFAULT 0,               -- 用户数
    event_count INTEGER DEFAULT 0,              -- 事件数
    revenue_usd REAL DEFAULT 0,                 -- USD收入
    PRIMARY KEY (stat_date, country_code)
);

-- 设备维度统计表
CREATE TABLE IF NOT EXISTS device_stats (
    stat_date DATE NOT NULL,                    -- 统计日期
    device_category TEXT NOT NULL,              -- 设备类别
    user_count INTEGER DEFAULT 0,               -- 用户数
    event_count INTEGER DEFAULT 0,              -- 事件数
    revenue_usd REAL DEFAULT 0,                 -- USD收入
    PRIMARY KEY (stat_date, device_category)
);

-- 货币转换表，用于存储各种货币对USD的转换率
CREATE TABLE IF NOT EXISTS currency_rates (
    currency_code TEXT PRIMARY KEY,             -- 货币代码
    rate_to_usd REAL NOT NULL,                  -- 对USD的汇率
    last_updated DATETIME NOT NULL              -- 最后更新时间
);
"""

# 创建索引的SQL语句
CREATE_INDEXES_SQL = """
-- 事件表索引
CREATE INDEX IF NOT EXISTS idx_events_created_date ON events(created_date);
CREATE INDEX IF NOT EXISTS idx_events_appsflyer_id ON events(appsflyer_id);
CREATE INDEX IF NOT EXISTS idx_events_event_name ON events(event_name);
CREATE INDEX IF NOT EXISTS idx_events_country_device ON events(country_code, device_category);

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_country_device ON users(country_code, device_category);
CREATE INDEX IF NOT EXISTS idx_users_first_seen ON users(first_seen_date);

-- 购买表索引
CREATE INDEX IF NOT EXISTS idx_purchases_user ON purchases(appsflyer_id);
CREATE INDEX IF NOT EXISTS idx_purchases_date ON purchases(created_date);
CREATE INDEX IF NOT EXISTS idx_purchases_country_device ON purchases(country_code, device_category);

-- 统计表索引
CREATE INDEX IF NOT EXISTS idx_country_stats_date ON country_stats(stat_date);
CREATE INDEX IF NOT EXISTS idx_device_stats_date ON device_stats(stat_date);
"""

# 初始货币汇率数据
CURRENCY_RATES = [
    ('USD', 1.0),
    ('EUR', 1.1),
    ('JPY', 0.0091),
    ('GBP', 1.3),
    ('AUD', 0.75),
    ('CAD', 0.78),
    ('CNY', 0.15),
    ('HKD', 0.13),
    ('TWD', 0.036),
    ('KRW', 0.00084),
    ('INR', 0.014),
    ('SGD', 0.74),
    ('MYR', 0.24),
    ('THB', 0.031),
    ('IDR', 0.000071),
    ('PHP', 0.020),
    ('VND', 0.000044)
]

def create_database():
    """创建SQLite数据库和所有必要的表结构"""
    try:
        # 连接到数据库（如果不存在则创建）
        logger.info(f"正在创建数据库: {DB_FILE}")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 启用外键约束
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # 创建表
        logger.info("创建数据库表")
        cursor.executescript(CREATE_TABLES_SQL)
        
        # 创建索引
        logger.info("创建数据库索引")
        cursor.executescript(CREATE_INDEXES_SQL)
        
        # 插入初始货币汇率数据
        logger.info("初始化货币汇率数据")
        now = datetime.now().isoformat()
        for currency, rate in CURRENCY_RATES:
            cursor.execute(
                "INSERT OR REPLACE INTO currency_rates (currency_code, rate_to_usd, last_updated) VALUES (?, ?, ?)",
                (currency, rate, now)
            )
        
        # 提交事务
        conn.commit()
        logger.info("数据库创建成功")
        
    except sqlite3.Error as e:
        logger.error(f"数据库创建失败: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()
    logger.info(f"数据库文件位置: {DB_FILE}") 