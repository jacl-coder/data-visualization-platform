/**
 * API缓存系统
 * 用于缓存API请求结果，避免频繁请求同一数据
 */

// 缓存项结构
export interface CacheItem<T> {
  data: T;
  timestamp: number;
  expiry: number; // 缓存过期时间（毫秒）
}

/**
 * API缓存类
 */
export class ApiCache {
  private cache: Record<string, CacheItem<any>> = {};
  
  /**
   * 设置缓存
   * @param key 缓存键
   * @param data 缓存数据
   * @param expiry 过期时间（毫秒），默认1分钟
   */
  set<T>(key: string, data: T, expiry: number = 60000): void {
    this.cache[key] = {
      data,
      timestamp: Date.now(),
      expiry
    };
  }
  
  /**
   * 获取缓存
   * @param key 缓存键
   * @returns 缓存数据，如果不存在或已过期则返回null
   */
  get<T>(key: string): T | null {
    const item = this.cache[key];
    
    if (!item) {
      return null;
    }
    
    // 检查缓存是否过期
    if (Date.now() - item.timestamp > item.expiry) {
      // 删除过期缓存
      delete this.cache[key];
      return null;
    }
    
    return item.data as T;
  }
  
  /**
   * 清除缓存
   * @param key 可选，指定缓存键，不提供则清除所有缓存
   */
  clear(key?: string): void {
    if (key) {
      delete this.cache[key];
    } else {
      this.cache = {};
    }
  }
  
  /**
   * 生成缓存键
   * @param url 请求URL
   * @param params 可选，请求参数
   * @returns 缓存键
   */
  static generateKey(url: string, params?: Record<string, any>): string {
    if (!params) {
      return url;
    }
    
    // 将参数按键排序并序列化
    const sortedParams = Object.keys(params)
      .sort()
      .map(key => `${key}=${params[key]}`)
      .join('&');
      
    return `${url}?${sortedParams}`;
  }
}

// 创建并导出缓存实例
export const apiCache = new ApiCache();

export default apiCache; 