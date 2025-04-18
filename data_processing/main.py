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

def main():
    """执行所有数据处理步骤"""
    start_time = time.time()
    
    try:
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
        
        # 计算总耗时
        elapsed_time = time.time() - start_time
        logger.info(f"数据处理完成! 总耗时: {elapsed_time:.2f} 秒")
        
    except Exception as e:
        logger.error(f"数据处理过程中出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 