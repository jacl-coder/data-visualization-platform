#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据处理脚本
用于处理CSV数据并导入到SQLite数据库
"""

import os
import json
import sqlite3
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据文件路径
CSV_FILE = os.path.join(ROOT_DIR, '后端考核', 'test.csv')

# 数据库文件路径
DB_DIR = os.path.join(ROOT_DIR, 'database')
DB_FILE = os.path.join(DB_DIR, 'app.db')

def extract_device_category(device_model):
    """从设备型号中提取设备类别"""
    if not device_model or pd.isna(device_model):
        return 'unknown_device_category'
    
    # 检查设备类别
    device_model = str(device_model).lower()
    if 'tablet' in device_model:
        return 'tablet'
    elif 'pad' in device_model:
        return 'tablet'
    elif 'mobile' in device_model:
        return 'mobile_phone'
    elif 'phone' in device_model:
        return 'mobile_phone'
    else:
        return device_model.split('::')[0] if '::' in device_model else 'mobile_phone'

def clean_datetime(dt_str):
    """清洗并标准化日期时间格式"""
    if pd.isna(dt_str) or not dt_str:
        return None
    
    try:
        # 尝试多种日期格式
        formats = [
            '%Y-%m-%d %H:%M:%S.%f%z',  # 带毫秒和时区
            '%Y-%m-%d %H:%M:%S.%f',     # 带毫秒
            '%Y-%m-%d %H:%M:%S%z',      # 带时区
            '%Y-%m-%d %H:%M:%S',        # 基本格式
            '%Y-%m-%d',                 # 仅日期
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(dt_str), fmt)
            except ValueError:
                continue
        
        # 如果是Unix时间戳（秒）
        if isinstance(dt_str, (int, float)) or str(dt_str).isdigit():
            return datetime.fromtimestamp(float(dt_str))
        
        raise ValueError(f"无法解析日期时间: {dt_str}")
    except Exception as e:
        logger.warning(f"日期时间解析失败 '{dt_str}': {e}")
        return None

def clean_date(date_str):
    """清洗并标准化日期格式"""
    if pd.isna(date_str) or not date_str:
        return None
    
    try:
        dt = clean_datetime(date_str)
        return dt.date() if dt else None
    except Exception as e:
        logger.warning(f"日期解析失败 '{date_str}': {e}")
        return None

def clean_currency_code(code):
    """清洗货币代码"""
    if pd.isna(code) or not code:
        return 'USD'  # 默认使用USD
    return str(code).upper()

def extract_event_params(row):
    """从事件值中提取事件参数"""
    event_value = row.get('event_value', '')
    
    # 如果event_value是JSON格式
    if event_value and isinstance(event_value, str) and (event_value.startswith('{') or event_value.startswith('{')):
        try:
            return event_value
        except Exception as e:
            logger.warning(f"事件值JSON解析失败: {e}")
    
    # 检查event_params字段
    params = {}
    for col in row.keys():
        if 'params' in col and row[col]:
            try:
                params[col] = row[col]
            except Exception:
                pass
    
    return json.dumps(params) if params else None

def extract_product_id(row):
    """从事件参数中提取产品ID"""
    event_value = row.get('event_value', '')
    
    try:
        # 尝试解析JSON格式的事件值
        if event_value and isinstance(event_value, str) and (event_value.startswith('{') or event_value.startswith('{')):
            data = json.loads(event_value)
            if 'af_content_id' in data:
                return data['af_content_id']
    except Exception:
        pass
    
    # 检查事件参数字段
    for col in ['af_content_id', 'product_id', 'sku']:
        if col in row and row[col]:
            return row[col]
    
    return None

def process_csv_data():
    """处理CSV数据"""
    try:
        # 检查数据库是否存在
        if not os.path.exists(DB_FILE):
            logger.error(f"数据库文件不存在: {DB_FILE}")
            logger.info("请先运行 create_database.py 创建数据库")
            return
        
        # 检查CSV文件是否存在
        if not os.path.exists(CSV_FILE):
            logger.error(f"CSV文件不存在: {CSV_FILE}")
            return
        
        logger.info(f"开始处理CSV数据: {CSV_FILE}")
        
        # 读取CSV数据
        # 由于文件可能较大，使用分块读取
        chunk_size = 10000  # 每次读取的行数
        
        # 连接数据库
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 获取货币汇率数据
        cursor.execute("SELECT currency_code, rate_to_usd FROM currency_rates")
        currency_rates = dict(cursor.fetchall())
        
        # 初始化计数器
        total_rows = 0
        inserted_events = 0
        inserted_users = 0
        inserted_purchases = 0
        
        # 辅助函数：确保日期时间对象转换为字符串
        def ensure_str_or_none(val):
            if val is None or pd.isna(val):
                return None
            elif isinstance(val, (datetime, pd.Timestamp)):
                return val.strftime('%Y-%m-%d %H:%M:%S')
            else:
                return str(val)
        
        # 分块处理CSV
        for chunk_num, chunk in enumerate(pd.read_csv(CSV_FILE, chunksize=chunk_size)):
            logger.info(f"处理数据块 {chunk_num+1}, 行数: {len(chunk)}")
            total_rows += len(chunk)
            
            # 预处理数据
            # 填充空值
            chunk = chunk.fillna({
                'event_name': 'unknown_event',
                'country_code': 'unknown',
                'device_model': 'unknown_device',
                'event_revenue_currency': 'USD'
            })
            
            # 添加设备类别
            chunk['device_category'] = chunk['device_model'].apply(extract_device_category)
            
            # 处理日期时间
            chunk['created_date'] = chunk['created_date'].apply(clean_date)
            chunk['event_time'] = chunk['event_time'].apply(clean_datetime)
            chunk['install_time'] = chunk['install_time'].apply(clean_datetime)
            
            # 统一货币
            chunk['event_revenue_currency'] = chunk['event_revenue_currency'].apply(clean_currency_code)
            
            # 计算USD收入
            def convert_to_usd(row):
                if pd.isna(row['event_revenue']) or not row['event_revenue']:
                    return 0.0
                
                # 如果已经有USD收入，直接使用
                if 'event_revenue_usd' in row and row['event_revenue_usd']:
                    return float(row['event_revenue_usd'])
                
                # 使用汇率转换
                currency = row['event_revenue_currency']
                revenue = float(row['event_revenue'])
                
                rate = currency_rates.get(currency, 1.0)  # 默认为1.0
                return revenue * rate
            
            chunk['event_revenue_usd'] = chunk.apply(convert_to_usd, axis=1)
            
            # 提取事件参数
            chunk['event_params'] = chunk.apply(extract_event_params, axis=1)
            
            # 处理产品ID
            chunk['product_id'] = chunk.apply(extract_product_id, axis=1)
            
            # 开启事务
            conn.execute("BEGIN TRANSACTION")
            
            try:
                # 1. 插入用户数据
                users_data = []
                # 跟踪此批次中已处理的用户ID，避免重复
                processed_user_ids = set()
                inserted_batch_users = 0
                
                for _, row in chunk.iterrows():
                    appsflyer_id = row['appsflyer_id']
                    if pd.isna(appsflyer_id) or not appsflyer_id:
                        continue
                    
                    appsflyer_id = str(appsflyer_id)
                    
                    # 如果此用户ID已在当前批次处理，则跳过
                    if appsflyer_id in processed_user_ids:
                        continue
                    
                    # 将此用户ID添加到已处理集合
                    processed_user_ids.add(appsflyer_id)
                    
                    # 检查用户是否已存在于数据库
                    cursor.execute("SELECT 1 FROM users WHERE appsflyer_id = ?", (appsflyer_id,))
                    if cursor.fetchone():
                        # 更新用户最后一次出现日期
                        cursor.execute(
                            "UPDATE users SET last_seen_date = MAX(last_seen_date, ?) WHERE appsflyer_id = ?",
                            (ensure_str_or_none(row['created_date']), appsflyer_id)
                        )
                    else:
                        # 插入新用户，确保所有值都是SQLite支持的类型
                        first_seen_date = ensure_str_or_none(row['created_date'])
                        last_seen_date = ensure_str_or_none(row['created_date'])
                        country_code = str(row['country_code']) if not pd.isna(row['country_code']) else None
                        device_model = str(row['device_model']) if not pd.isna(row['device_model']) else None
                        device_category = str(row['device_category']) if not pd.isna(row['device_category']) else None
                        platform = str(row.get('platform', '')) if row.get('platform') and not pd.isna(row.get('platform')) else None
                        media_source = str(row.get('media_source', '')) if row.get('media_source') and not pd.isna(row.get('media_source')) else None
                        install_time = ensure_str_or_none(row['install_time'])
                        
                        # 立即插入用户数据，确保满足外键约束
                        cursor.execute("""
                        INSERT OR REPLACE INTO users 
                        (appsflyer_id, first_seen_date, last_seen_date, 
                         country_code, device_model, device_category, 
                         platform, media_source, install_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            appsflyer_id,
                            first_seen_date,
                            last_seen_date,
                            country_code,
                            device_model,
                            device_category,
                            platform,
                            media_source,
                            install_time
                        ))
                        inserted_batch_users += 1
                
                inserted_users += inserted_batch_users
                logger.info(f"已插入/更新 {inserted_batch_users} 个用户")
                
                # 2. 插入事件数据
                events_data = []
                for _, row in chunk.iterrows():
                    appsflyer_id = row['appsflyer_id']
                    if pd.isna(appsflyer_id) or not appsflyer_id:
                        continue
                    
                    # 确保所有值都是SQLite支持的类型
                    event_name = str(row['event_name']) if not pd.isna(row['event_name']) else 'unknown_event'
                    event_value = str(row.get('event_value', '')) if row.get('event_value') and not pd.isna(row.get('event_value')) else None
                    created_date = ensure_str_or_none(row['created_date'])
                    event_time = ensure_str_or_none(row['event_time'])
                    country_code = str(row['country_code']) if not pd.isna(row['country_code']) else None
                    device_model = str(row['device_model']) if not pd.isna(row['device_model']) else None
                    device_category = str(row['device_category']) if not pd.isna(row['device_category']) else None
                    app_id = str(row.get('app_id', '')) if row.get('app_id') and not pd.isna(row.get('app_id')) else None
                    platform = str(row.get('platform', '')) if row.get('platform') and not pd.isna(row.get('platform')) else None
                    media_source = str(row.get('media_source', '')) if row.get('media_source') and not pd.isna(row.get('media_source')) else None
                    event_revenue = float(row.get('event_revenue', 0.0)) if row.get('event_revenue') and not pd.isna(row.get('event_revenue')) else 0.0
                    event_revenue_currency = str(row['event_revenue_currency']) if not pd.isna(row['event_revenue_currency']) else 'USD'
                    event_revenue_usd = float(row['event_revenue_usd']) if not pd.isna(row['event_revenue_usd']) else 0.0
                    event_params = str(row['event_params']) if not pd.isna(row['event_params']) else None
                    install_time = ensure_str_or_none(row['install_time'])
                    
                    events_data.append((
                        str(appsflyer_id),
                        event_name,
                        event_value,
                        created_date,
                        event_time,
                        country_code,
                        device_model,
                        device_category,
                        app_id,
                        platform,
                        media_source,
                        event_revenue,
                        event_revenue_currency,
                        event_revenue_usd,
                        event_params,
                        install_time
                    ))
                
                if events_data:
                    cursor.executemany(
                        """
                        INSERT INTO events 
                        (appsflyer_id, event_name, event_value, 
                         created_date, event_time, country_code, 
                         device_model, device_category, app_id, 
                         platform, media_source, event_revenue, 
                         event_revenue_currency, event_revenue_usd, 
                         event_params, install_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        events_data
                    )
                    inserted_events += len(events_data)
                
                # 3. 插入购买事件数据
                purchases_data = []
                # 跟踪此批次已处理的购买记录，避免重复插入
                processed_purchases = set()
                
                for _, row in chunk.iterrows():
                    appsflyer_id = row['appsflyer_id']
                    if (pd.isna(appsflyer_id) or not appsflyer_id or 
                        row['event_name'] != 'af_purchase' or 
                        not row['event_revenue_usd']):
                        continue
                    
                    # 确保所有值都是SQLite支持的类型
                    purchase_time = ensure_str_or_none(row['event_time'])
                    created_date = ensure_str_or_none(row['created_date'])
                    country_code = str(row['country_code']) if not pd.isna(row['country_code']) else None
                    device_category = str(row['device_category']) if not pd.isna(row['device_category']) else None
                    event_revenue_usd = float(row['event_revenue_usd']) if not pd.isna(row['event_revenue_usd']) else 0.0
                    product_id = str(row['product_id']) if not pd.isna(row['product_id']) else None
                    order_id = str(row.get('order_id', '')) if row.get('order_id') and not pd.isna(row.get('order_id')) else None
                    
                    # 创建一个唯一键，用于检测重复
                    # 使用用户ID+订单ID+购买时间的组合作为唯一标识
                    purchase_key = (str(appsflyer_id), order_id, purchase_time)
                    
                    # 如果这个购买记录已经处理过，则跳过
                    if purchase_key in processed_purchases:
                        continue
                    
                    # 将此购买记录添加到已处理集合
                    processed_purchases.add(purchase_key)
                    
                    purchases_data.append((
                        str(appsflyer_id),   # 确保是字符串
                        purchase_time,        # 确保是字符串格式的日期时间
                        created_date,         # 确保是字符串格式的日期
                        country_code,         # 可能是None
                        device_category,      # 可能是None
                        event_revenue_usd,    # 确保是浮点数
                        product_id,           # 可能是None
                        order_id              # 可能是None
                    ))
                
                if purchases_data:
                    cursor.executemany(
                        """
                        INSERT INTO purchases 
                        (appsflyer_id, purchase_time, created_date, 
                         country_code, device_category, event_revenue_usd, 
                         product_id, order_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        purchases_data
                    )
                    inserted_purchases += len(purchases_data)
                
                # 提交事务
                conn.commit()
                
            except Exception as e:
                # 回滚事务
                conn.rollback()
                logger.error(f"处理数据块 {chunk_num+1} 时出错: {e}")
                raise
        
        logger.info(f"数据处理完成, 总行数: {total_rows}")
        logger.info(f"插入用户数: {inserted_users}")
        logger.info(f"插入事件数: {inserted_events}")
        logger.info(f"插入购买事件数: {inserted_purchases}")
        
    except Exception as e:
        logger.error(f"数据处理失败: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    process_csv_data() 