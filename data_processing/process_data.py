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

# 固定随机种子，确保每次运行结果一致
np.random.seed(42)
if hasattr(pd, 'set_option'):
    pd.set_option('mode.chained_assignment', None)

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
        logger.info("读取整个CSV文件到内存")
        df = pd.read_csv(CSV_FILE)
        logger.info(f"CSV文件读取完成，共{len(df)}行")
        
        # 连接数据库
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 清空现有数据
        logger.info("清空现有事件、用户和购买数据")
        cursor.execute("DELETE FROM events")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM purchases")
        conn.commit()
        
        # 获取货币汇率数据
        cursor.execute("SELECT currency_code, rate_to_usd FROM currency_rates")
        currency_rates = dict(cursor.fetchall())
        
        # 初始化计数器
        total_rows = len(df)
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
        
        # 预处理数据
        logger.info("预处理数据...")
        # 填充空值
        df = df.fillna({
            'event_name': 'unknown_event',
            'country_code': 'unknown',
            'device_model': 'unknown_device',
            'event_revenue_currency': 'USD'
        })
        
        # 添加设备类别
        df['device_category'] = df['device_model'].apply(extract_device_category)
        
        # 处理日期和时间
        df['created_date'] = df['event_time'].apply(clean_date)
        df['event_time'] = df['event_time'].apply(clean_datetime)
        df['install_time'] = df.get('install_time', df['event_time']).apply(clean_datetime)
        
        # 确保install_time不晚于event_time
        for idx, row in df.iterrows():
            if pd.notna(row['event_time']) and pd.notna(row['install_time']):
                if row['install_time'] > row['event_time']:
                    df.at[idx, 'install_time'] = row['event_time']
        
        # 确保货币代码规范化
        df['event_revenue_currency'] = df['event_revenue_currency'].apply(clean_currency_code)
        
        # 计算USD收入 - 确保精确到小数点后4位以保持一致性
        def convert_to_usd(row):
            if pd.isna(row['event_revenue']) or not row['event_revenue']:
                return 0.0
            
            # 如果已经有USD收入，直接使用
            if 'event_revenue_usd' in row and row['event_revenue_usd']:
                return round(float(row['event_revenue_usd']), 4)
            
            # 使用汇率转换
            currency = row['event_revenue_currency']
            revenue = float(row['event_revenue'])
            
            rate = currency_rates.get(currency, 1.0)  # 默认为1.0
            return round(revenue * rate, 4)  # 确保精确到小数点后4位
        
        df['event_revenue_usd'] = df.apply(convert_to_usd, axis=1)
        
        # 提取事件参数
        df['event_params'] = df.apply(extract_event_params, axis=1)
        
        # 处理产品ID
        df['product_id'] = df.apply(extract_product_id, axis=1)
        
        # 开启事务
        conn.execute("BEGIN TRANSACTION")
        
        try:
            # 1. 处理用户数据
            logger.info("处理用户数据...")
            user_data = []
            unique_users = df['appsflyer_id'].dropna().unique()
            
            for user_id in unique_users:
                user_rows = df[df['appsflyer_id'] == user_id]
                
                first_seen_date = min(user_rows['created_date'].dropna())
                last_seen_date = max(user_rows['created_date'].dropna())
                
                # 获取用户的第一条记录，用于提取其他字段
                first_row = user_rows.iloc[0]
                
                user_data.append((
                    str(user_id),
                    ensure_str_or_none(first_seen_date),
                    ensure_str_or_none(last_seen_date),
                    str(first_row['country_code']) if not pd.isna(first_row['country_code']) else None,
                    str(first_row['device_model']) if not pd.isna(first_row['device_model']) else None,
                    str(first_row['device_category']) if not pd.isna(first_row['device_category']) else None,
                    str(first_row.get('platform', '')) if first_row.get('platform') and not pd.isna(first_row.get('platform')) else None,
                    str(first_row.get('media_source', '')) if first_row.get('media_source') and not pd.isna(first_row.get('media_source')) else None,
                    ensure_str_or_none(first_row['install_time'])
                ))
            
            # 批量插入用户数据
            cursor.executemany("""
            INSERT INTO users 
            (appsflyer_id, first_seen_date, last_seen_date, 
             country_code, device_model, device_category, 
             platform, media_source, install_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, user_data)
            
            inserted_users = len(user_data)
            logger.info(f"已插入 {inserted_users} 个用户")
            
            # 2. 插入事件数据
            logger.info("处理事件数据...")
            events_data = []
            
            for _, row in df.iterrows():
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
            
            # 批量插入事件数据
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
                inserted_events = len(events_data)
                logger.info(f"已插入 {inserted_events} 条事件数据")
            
            # 3. 处理购买数据
            logger.info("处理购买数据...")
            purchases_data = []
            
            # 仅处理购买事件
            purchase_df = df[df['event_name'] == 'af_purchase'].copy()
            purchase_df = purchase_df[purchase_df['event_revenue_usd'] > 0]
            
            # 创建唯一标识来防止重复
            if not purchase_df.empty:
                purchase_df['purchase_key'] = purchase_df.apply(
                    lambda r: f"{r['appsflyer_id']}_{r.get('order_id', '')}_{ensure_str_or_none(r['event_time'])}", 
                    axis=1
                )
                
                # 删除重复项
                purchase_df = purchase_df.drop_duplicates(subset=['purchase_key'])
                
                for _, row in purchase_df.iterrows():
                    purchases_data.append((
                        str(row['appsflyer_id']),
                        ensure_str_or_none(row['event_time']),
                        ensure_str_or_none(row['created_date']),
                        str(row['country_code']) if not pd.isna(row['country_code']) else None,
                        str(row['device_category']) if not pd.isna(row['device_category']) else None,
                        float(row['event_revenue_usd']) if not pd.isna(row['event_revenue_usd']) else 0.0,
                        str(row['product_id']) if not pd.isna(row['product_id']) else None,
                        str(row.get('order_id', '')) if row.get('order_id') and not pd.isna(row.get('order_id')) else None
                    ))
            
            # 批量插入购买数据
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
                inserted_purchases = len(purchases_data)
                logger.info(f"已插入 {inserted_purchases} 条购买数据")
            
            # 提交事务
            conn.commit()
            logger.info("数据处理完成并已提交到数据库")
            
        except Exception as e:
            # 回滚事务
            conn.rollback()
            logger.error(f"数据处理失败，已回滚: {e}")
            raise
        finally:
            # 关闭数据库连接
            conn.close()
        
        logger.info(f"CSV数据处理完成，共处理 {total_rows} 行数据")
        logger.info(f"统计结果: 插入用户 {inserted_users}, 事件 {inserted_events}, 购买 {inserted_purchases}")
        
    except Exception as e:
        logger.error(f"处理CSV数据时出错: {e}")
        raise

if __name__ == "__main__":
    process_csv_data() 