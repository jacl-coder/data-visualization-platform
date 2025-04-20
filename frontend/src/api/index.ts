import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import apiCache, { ApiCache } from './cache'

// 扩展Axios配置类型，添加重试计数属性
interface CustomRequestConfig extends InternalAxiosRequestConfig {
  retryCount?: number
}

// 最大重试次数
const MAX_RETRIES = 2
// 重试延迟（毫秒）
const RETRY_DELAY = 1000

// 判断API基础路径
const getBaseUrl = (): string => {
  // 优先使用环境变量中定义的API基础路径（如果存在）
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL as string;
  }
  
  // 如果是开发环境，直接连接到本地后端
  if (import.meta.env.DEV) {
    return 'http://localhost:40001';
  }
  
  // 生产环境使用空字符串，API路径已经包含/api前缀
  return '';
}

// 创建axios实例
const apiClient = axios.create({
  baseURL: getBaseUrl(),
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false // 关闭跨域请求时携带凭证
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 确保headers对象存在
    config.headers = config.headers || {};
    
    // 添加请求重试计数器
    (config as CustomRequestConfig).retryCount = 0;
    
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    return response
  },
  async (error: AxiosError) => {
    const config = error.config as CustomRequestConfig
    
    // 如果配置了重试，并且重试次数小于最大次数，并且错误是网络错误或5xx错误
    if (
      config &&
      config.retryCount !== undefined &&
      config.retryCount < MAX_RETRIES &&
      (error.code === 'ECONNABORTED' || 
       error.code === 'ERR_NETWORK' ||
       (error.response && error.response.status >= 500))
    ) {
      // 增加重试计数
      config.retryCount += 1
      
      // 显示正在重试的消息
      ElMessage.info(`网络请求失败，正在尝试重新连接 (${config.retryCount}/${MAX_RETRIES})...`)
      
      // 延迟一段时间后重试
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(apiClient(config))
        }, RETRY_DELAY)
      })
    }
    
    // 处理错误信息
    if (error.response) {
      // 服务器返回了错误状态码
      console.error('响应错误:', error.response.status, error.response.data)
      
      // 根据状态码处理不同错误
      switch (error.response.status) {
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 400:
          ElMessage.error('请求参数有误')
          break
        case 401:
          ElMessage.error('未授权，请重新登录')
          break
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(`请求失败 (${error.response.status})`)
      }
    } else if (error.request) {
      // 请求发送了，但没有收到响应
      console.error('未收到响应:', error.request)
      ElMessage.error('无法连接到服务器，请检查网络连接')
    } else {
      // 请求配置有误
      console.error('请求配置错误:', error.message)
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

// 响应结构类型
export interface ApiResponse<T> {
  status: 'success' | 'error'
  code: number
  message: string
  data: T
}

// 数据列表响应类型
export interface ListResponse<T> {
  items: T[]
  total: number
}

// 概览数据类型
export interface OverviewData {
  user_count: number
  event_count: number
  device_count: number
  total_revenue: number
}

// 时间线数据类型
export interface TimelineItem {
  date: string
  user_count: number
  event_count: number
  revenue: number
  device_count: number
}

// 国家统计数据类型
export interface CountryItem {
  country: string
  users: number
  revenue: number
}

// 设备统计数据类型
export interface DeviceItem {
  device: string
  users: number
  revenue: number
}

// 详情数据类型
export interface DetailsData {
  date: string
  total_revenue: number
  countries: { country: string; users: number }[]
  devices: { device: string; users: number }[]
}

// LTV概览数据类型
export interface LtvOverviewData {
  avg_ltv_1d: number
  avg_ltv_7d: number
  avg_ltv_14d: number
  avg_ltv_30d: number
  avg_ltv_60d: number
  avg_ltv_90d: number
  avg_ltv_total: number
  total_ltv: number
  user_count: number
  avg_purchases: number
}

// LTV数据项类型（按用户）
export interface LtvUserItem {
  appsflyer_id: string
  first_purchase_date: string
  ltv_1d: number
  ltv_7d: number
  ltv_14d: number
  ltv_30d: number
  ltv_60d: number
  ltv_90d: number
  ltv_total: number
  purchase_count: number
}

// LTV数据项类型（按国家分组）
export interface LtvCountryItem {
  country: string
  user_count: number
  ltv_value: number
}

// LTV数据项类型（按设备分组）
export interface LtvDeviceItem {
  device: string
  user_count: number
  ltv_value: number
}

// LTV数据项类型（按日期分组）
export interface LtvDateItem {
  date: string
  user_count: number
  avg_ltv: number
  total_ltv: number
}

// LTV数据响应类型（泛型）
export interface LtvResponse<T> {
  items: T[]
  total: number
  window: string
  groupBy: string
}

/**
 * 统一的API请求函数，带错误处理和缓存机制
 * @param requestFn 请求函数
 * @param cacheKey 缓存键
 * @param cacheExpiry 缓存过期时间（毫秒）
 * @param loadingState 加载状态引用
 * @param errorMessage 错误消息
 */
export const safeApiCall = async <T>(
  requestFn: () => Promise<T>,
  cacheKey?: string,
  cacheExpiry?: number,
  loadingState?: { value: boolean }, 
  errorMessage = '请求失败'
): Promise<T | null> => {
  try {
    // 如果提供了缓存键，先尝试从缓存获取数据
    if (cacheKey) {
      const cachedData = apiCache.get<T>(cacheKey);
      if (cachedData) {
        if (loadingState) {
          loadingState.value = false;
        }
        return cachedData;
      }
    }
    
    // 如果缓存中没有数据，执行请求函数
    const data = await requestFn();
    
    // 如果提供了缓存键，将响应数据存入缓存
    if (cacheKey && data) {
      apiCache.set(cacheKey, data, cacheExpiry);
    }
    
    return data;
  } catch (error) {
    console.error(errorMessage, error);
    // 错误已经在拦截器中处理过，这里不需要再显示消息
    return null;
  } finally {
    if (loadingState) {
      loadingState.value = false;
    }
  }
}

/**
 * 获取服务器状态
 */
export const getServerStatus = async (): Promise<ApiResponse<string> | null> => {
  return safeApiCall(
    async () => {
      const response = await apiClient.get<ApiResponse<string>>(import.meta.env.DEV ? '/' : '')
      return response.data
    },
    'server_status',
    60000, // 1分钟缓存
    undefined,
    '获取服务器状态失败'
  )
}

/**
 * 获取概览数据
 * @param loadingState 可选的加载状态ref
 */
export const getOverview = async (loadingState?: { value: boolean }): Promise<ApiResponse<OverviewData> | null> => {
  if (loadingState) loadingState.value = true;
  
  return safeApiCall(
    async () => {
      const response = await apiClient.get<ApiResponse<OverviewData>>('/api/overview')
      return response.data
    },
    'overview',
    30000, // 30秒缓存
    loadingState,
    '获取概览数据失败'
  )
}

/**
 * 获取时间线数据
 * @param days 天数，默认30天
 * @param dateRange 可选的日期范围，格式为startDate|endDate
 * @param loadingState 可选的加载状态ref
 */
export const getTimeline = async (
  days: number = 30, 
  dateRange?: string,
  loadingState?: { value: boolean }
): Promise<ApiResponse<ListResponse<TimelineItem>> | null> => {
  if (loadingState) loadingState.value = true;
  
  const cacheKey = dateRange 
    ? ApiCache.generateKey('/api/timeline', { dateRange })
    : ApiCache.generateKey('/api/timeline', { days });
  
  return safeApiCall(
    async () => {
      const url = dateRange 
        ? `/api/timeline?dateRange=${dateRange}`
        : `/api/timeline?days=${days}`;
        
      const response = await apiClient.get<ApiResponse<ListResponse<TimelineItem>>>(url);
      return response.data;
    },
    cacheKey,
    60000, // 1分钟缓存
    loadingState,
    '获取时间线数据失败'
  );
}

/**
 * 获取国家维度数据
 * @param date 可选的日期参数，格式为YYYY-MM-DD
 * @param loadingState 可选的加载状态ref
 */
export const getCountryData = async (date?: string, loadingState?: { value: boolean }): Promise<ApiResponse<ListResponse<CountryItem>> | null> => {
  if (loadingState) loadingState.value = true;
  
  const cacheKey = date ? `country_data_${date}` : 'country_data';
  
  return safeApiCall(
    async () => {
      const url = date ? `/api/country?date=${date}` : '/api/country';
      const response = await apiClient.get<ApiResponse<ListResponse<CountryItem>>>(url);
      return response.data;
    },
    cacheKey,
    300000, // 5分钟缓存
    loadingState,
    '获取国家数据失败'
  );
}

/**
 * 获取设备维度数据
 * @param date 可选的日期参数，格式为YYYY-MM-DD
 * @param loadingState 可选的加载状态ref
 */
export const getDeviceData = async (date?: string, loadingState?: { value: boolean }): Promise<ApiResponse<ListResponse<DeviceItem>> | null> => {
  if (loadingState) loadingState.value = true;
  
  const cacheKey = date ? `device_data_${date}` : 'device_data';
  
  return safeApiCall(
    async () => {
      const url = date ? `/api/device?date=${date}` : '/api/device';
      const response = await apiClient.get<ApiResponse<ListResponse<DeviceItem>>>(url);
      return response.data;
    },
    cacheKey,
    300000, // 5分钟缓存
    loadingState,
    '获取设备数据失败'
  );
}

/**
 * 获取指定日期的详细数据
 * @param date 日期，格式为YYYY-MM-DD
 * @param loadingState 可选的加载状态ref
 */
export const getDetailsData = async (date: string, loadingState?: { value: boolean }): Promise<ApiResponse<DetailsData> | null> => {
  if (loadingState) loadingState.value = true;
  
  return safeApiCall(
    async () => {
      const response = await apiClient.get<ApiResponse<DetailsData>>(`/api/details?date=${date}`)
      return response.data
    },
    ApiCache.generateKey('/api/details', { date }),
    300000, // 5分钟缓存
    loadingState,
    '获取详情数据失败'
  )
}

/**
 * 获取LTV概览数据
 * @param loadingState 可选的加载状态ref
 */
export const getLtvOverview = async (loadingState?: { value: boolean }): Promise<ApiResponse<LtvOverviewData> | null> => {
  if (loadingState) loadingState.value = true;
  
  return safeApiCall(
    async () => {
      const response = await apiClient.get<ApiResponse<LtvOverviewData>>('/api/ltv/overview')
      return response.data
    },
    'ltv_overview',
    300000, // 5分钟缓存
    loadingState,
    'LTV概览数据获取失败'
  )
}

/**
 * 获取LTV详细数据
 * @param groupBy 分组方式: country/device/date/undefined(默认按用户返回)
 * @param window 时间窗口: 1d/7d/14d/30d/60d/90d/total
 * @param loadingState 可选的加载状态ref
 */
export const getLtvData = async <T>(
  groupBy?: string,
  window: string = 'total',
  loadingState?: { value: boolean }
): Promise<ApiResponse<LtvResponse<T>> | null> => {
  if (loadingState) loadingState.value = true;
  
  const queryParams = new URLSearchParams();
  if (groupBy) queryParams.append('groupBy', groupBy);
  if (window) queryParams.append('window', window);
  
  const url = `/api/ltv?${queryParams.toString()}`;
  const cacheKey = `ltv_${groupBy || 'user'}_${window}`;
  
  return safeApiCall(
    async () => {
      const response = await apiClient.get<ApiResponse<LtvResponse<T>>>(url);
      return response.data;
    },
    cacheKey,
    300000, // 5分钟缓存
    loadingState,
    'LTV数据获取失败'
  );
}

/**
 * 清除API缓存
 * @param key 可选，指定缓存键，如果不提供则清除所有缓存
 */
export const clearApiCache = (key?: string): void => {
  apiCache.clear(key);
}

export default {
  getServerStatus,
  getOverview,
  getTimeline,
  getCountryData,
  getDeviceData,
  getDetailsData,
  getLtvOverview,
  getLtvData,
  clearApiCache,
  safeApiCall
} 