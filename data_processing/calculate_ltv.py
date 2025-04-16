#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LTV计算脚本
基于af_purchase事件计算用户的终身价值(Life Time Value)
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
from collections import defaultdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据库文件路径
DB_DIR = os.path.join(ROOT_DIR, 'database')
DB_FILE = os.path.join(DB_DIR, 'app.db')

def calculate_ltv():
    """计算用户LTV并更新数据库"""
    try:
        # 检查数据库是否存在
        if not os.path.exists(DB_FILE):
            logger.error(f"数据库文件不存在: {DB_FILE}")
            logger.info("请先运行 create_database.py 创建数据库")
            return
        
        logger.info("开始计算用户LTV")
        
        # 连接数据库
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  # 使用命名行
        cursor = conn.cursor()
        
        # 检查是否有purchase数据
        cursor.execute("SELECT COUNT(*) FROM purchases")
        purchase_count = cursor.fetchone()[0]
        
        if purchase_count == 0:
            logger.warning("没有找到购买数据，请先处理CSV数据")
            return
        
        logger.info(f"找到 {purchase_count} 条购买记录")
        
        # 获取所有用户的首次购买日期
        cursor.execute("""
        SELECT appsflyer_id, MIN(created_date) as first_purchase_date
        FROM purchases
        GROUP BY appsflyer_id
        """)
        
        user_first_purchase = {row['appsflyer_id']: row['first_purchase_date'] for row in cursor.fetchall()}
        
        # 获取用户所有购买记录，按时间排序
        cursor.execute("""
        SELECT appsflyer_id, created_date, event_revenue_usd
        FROM purchases
        ORDER BY appsflyer_id, created_date
        """)
        
        # 用户购买记录
        user_purchases = defaultdict(list)
        
        for row in cursor.fetchall():
            appsflyer_id = row['appsflyer_id']
            created_date = datetime.strptime(row['created_date'], '%Y-%m-%d').date()
            revenue = row['event_revenue_usd']
            
            user_purchases[appsflyer_id].append((created_date, revenue))
        
        # 计算LTV
        ltv_data = []
        
        for appsflyer_id, purchases in user_purchases.items():
            first_purchase_date = datetime.strptime(user_first_purchase[appsflyer_id], '%Y-%m-%d').date()
            last_purchase_date = purchases[-1][0]
            
            # 初始化各时间窗口的LTV
            ltv_1d = 0.0
            ltv_7d = 0.0
            ltv_14d = 0.0
            ltv_30d = 0.0
            ltv_60d = 0.0
            ltv_90d = 0.0
            ltv_total = 0.0
            
            # 计算每个时间窗口的LTV
            for purchase_date, revenue in purchases:
                days_diff = (purchase_date - first_purchase_date).days
                
                ltv_total += revenue
                
                if days_diff <= 0:  # 包括首次购买当天
                    ltv_1d += revenue
                
                if days_diff <= 6:  # 7天内（含首次购买当天）
                    ltv_7d += revenue
                
                if days_diff <= 13:  # 14天内
                    ltv_14d += revenue
                
                if days_diff <= 29:  # 30天内
                    ltv_30d += revenue
                
                if days_diff <= 59:  # 60天内
                    ltv_60d += revenue
                
                if days_diff <= 89:  # 90天内
                    ltv_90d += revenue
            
            # 添加到批量更新数据
            ltv_data.append((
                appsflyer_id,
                user_first_purchase[appsflyer_id],
                ltv_1d,
                ltv_7d,
                ltv_14d,
                ltv_30d,
                ltv_60d,
                ltv_90d,
                ltv_total,
                len(purchases),
                str(last_purchase_date)
            ))
        
        # 开始事务
        conn.execute("BEGIN TRANSACTION")
        
        try:
            # 删除现有LTV数据
            cursor.execute("DELETE FROM user_ltv")
            
            # 插入新计算的LTV数据
            cursor.executemany("""
            INSERT INTO user_ltv (
                appsflyer_id, first_purchase_date, ltv_1d, 
                ltv_7d, ltv_14d, ltv_30d, ltv_60d, ltv_90d, 
                ltv_total, purchase_count, last_purchase_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ltv_data)
            
            # 提交事务
            conn.commit()
            
            logger.info(f"已成功计算并更新 {len(ltv_data)} 个用户的LTV数据")
            
        except Exception as e:
            # 回滚事务
            conn.rollback()
            logger.error(f"LTV计算失败: {e}")
            raise
        
    except Exception as e:
        logger.error(f"LTV计算过程出错: {e}")
        raise
    finally:
        if conn:
            conn.close()

def generate_daily_stats():
    """生成每日统计数据"""
    try:
        # 检查数据库是否存在
        if not os.path.exists(DB_FILE):
            logger.error(f"数据库文件不存在: {DB_FILE}")
            return
        
        logger.info("开始生成每日统计数据")
        
        # 连接数据库
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 开始事务
        conn.execute("BEGIN TRANSACTION")
        
        try:
            # 清空现有统计数据
            cursor.execute("DELETE FROM daily_stats")
            cursor.execute("DELETE FROM country_stats")
            cursor.execute("DELETE FROM device_stats")
            
            # 计算每日基本统计数据
            cursor.execute("""
            INSERT INTO daily_stats (
                stat_date, user_count, new_user_count, event_count, 
                purchase_count, revenue_usd, device_count, country_count
            )
            SELECT 
                e.created_date,
                COUNT(DISTINCT e.appsflyer_id) as user_count,
                COUNT(DISTINCT CASE WHEN u.first_seen_date = e.created_date THEN u.appsflyer_id END) as new_user_count,
                COUNT(*) as event_count,
                COUNT(CASE WHEN e.event_name = 'af_purchase' THEN 1 END) as purchase_count,
                SUM(CASE WHEN e.event_name = 'af_purchase' THEN e.event_revenue_usd ELSE 0 END) as revenue_usd,
                COUNT(DISTINCT e.device_category) as device_count,
                COUNT(DISTINCT e.country_code) as country_count
            FROM 
                events e
            LEFT JOIN 
                users u ON e.appsflyer_id = u.appsflyer_id
            GROUP BY 
                e.created_date
            ORDER BY 
                e.created_date
            """)
            
            # 计算国家维度统计数据
            cursor.execute("""
            INSERT INTO country_stats (
                stat_date, country_code, user_count, event_count, revenue_usd
            )
            SELECT 
                e.created_date,
                e.country_code,
                COUNT(DISTINCT e.appsflyer_id) as user_count,
                COUNT(*) as event_count,
                SUM(CASE WHEN e.event_name = 'af_purchase' THEN e.event_revenue_usd ELSE 0 END) as revenue_usd
            FROM 
                events e
            GROUP BY 
                e.created_date, e.country_code
            ORDER BY 
                e.created_date, e.country_code
            """)
            
            # 计算设备维度统计数据
            cursor.execute("""
            INSERT INTO device_stats (
                stat_date, device_category, user_count, event_count, revenue_usd
            )
            SELECT 
                e.created_date,
                e.device_category,
                COUNT(DISTINCT e.appsflyer_id) as user_count,
                COUNT(*) as event_count,
                SUM(CASE WHEN e.event_name = 'af_purchase' THEN e.event_revenue_usd ELSE 0 END) as revenue_usd
            FROM 
                events e
            GROUP BY 
                e.created_date, e.device_category
            ORDER BY 
                e.created_date, e.device_category
            """)
            
            # 提交事务
            conn.commit()
            
            # 获取统计结果
            cursor.execute("SELECT COUNT(*) FROM daily_stats")
            daily_stats_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM country_stats")
            country_stats_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM device_stats")
            device_stats_count = cursor.fetchone()[0]
            
            logger.info(f"已生成 {daily_stats_count} 条每日统计数据")
            logger.info(f"已生成 {country_stats_count} 条国家统计数据")
            logger.info(f"已生成 {device_stats_count} 条设备统计数据")
            
        except Exception as e:
            # 回滚事务
            conn.rollback()
            logger.error(f"生成统计数据失败: {e}")
            raise
        
    except Exception as e:
        logger.error(f"统计数据生成过程出错: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    calculate_ltv()
    generate_daily_stats() 