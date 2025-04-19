#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据处理主脚本
整合所有数据处理步骤，包括创建数据库、处理数据和计算LTV
"""

import os
import sys
import logging
import time
import sqlite3
from pathlib import Path

# 确保当前目录在导入路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入处理模块
from data_processing.create_database import create_database
from data_processing.process_data import process_csv_data
from data_processing.calculate_ltv import calculate_ltv, generate_daily_stats

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# 数据库文件路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(ROOT_DIR, 'database')
DB_FILE = os.path.join(DB_DIR, 'app.db')

def reset_database():
    """重置数据库，完全删除并重新创建数据库文件"""
    logger.info("重置数据库...")
    
    # 如果数据库文件存在，先删除它
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            logger.info(f"已删除现有数据库文件: {DB_FILE}")
        except Exception as e:
            logger.error(f"删除数据库文件失败: {e}")
            raise
    
    # 确保数据库目录存在
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
        logger.info(f"创建数据库目录: {DB_DIR}")
    
    logger.info("数据库重置完成")

def main():
    """执行所有数据处理步骤"""
    start_time = time.time()
    
    try:
        # 步骤0: 重置数据库（删除现有数据库文件）
        logger.info("步骤0: 重置数据库")
        reset_database()
        
        # 步骤1: 创建数据库
        logger.info("步骤1: 创建数据库")
        create_database()
        
        # 步骤2: 处理CSV数据
        logger.info("步骤2: 处理CSV数据")
        process_csv_data()
        
        # 步骤3: 计算用户LTV
        logger.info("步骤3: 计算用户LTV")
        calculate_ltv()
        
        # 步骤4: 生成汇总统计数据
        logger.info("步骤4: 生成汇总统计数据")
        generate_daily_stats()
        
        # 验证数据一致性
        logger.info("验证数据一致性...")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM purchases")
        purchase_count = cursor.fetchone()[0]
        conn.close()
        
        logger.info(f"数据验证结果: 事件数={event_count}, 用户数={user_count}, 购买数={purchase_count}")
        
        # 计算总耗时
        elapsed_time = time.time() - start_time
        logger.info(f"数据处理完成! 总耗时: {elapsed_time:.2f} 秒")
        
    except Exception as e:
        logger.error(f"数据处理过程中出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 