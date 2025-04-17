import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8080', // 默认连接到本地后端服务
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false // 关闭跨域请求时携带凭证
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 确保headers对象存在
    config.headers = config.headers || {}
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
  error => {
    if (error.response) {
      // 服务器返回了错误状态码
      console.error('响应错误:', error.response.status, error.response.data)
    } else if (error.request) {
      // 请求发送了，但没有收到响应
      console.error('未收到响应:', error.request)
    } else {
      // 请求配置有误
      console.error('请求配置错误:', error.message)
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

/**
 * 获取服务器状态
 */
export const getServerStatus = async (): Promise<ApiResponse<string>> => {
  try {
    const response = await apiClient.get<ApiResponse<string>>('/')
    return response.data
  } catch (error) {
    console.error('获取服务器状态失败:', error)
    throw error
  }
}

/**
 * 获取概览数据
 */
export const getOverview = async (): Promise<ApiResponse<OverviewData>> => {
  try {
    const response = await apiClient.get<ApiResponse<OverviewData>>('/api/overview')
    return response.data
  } catch (error) {
    console.error('获取概览数据失败:', error)
    throw error
  }
}

/**
 * 获取时间线数据
 * @param days 天数，默认30天
 */
export const getTimeline = async (days: number = 30): Promise<ApiResponse<ListResponse<TimelineItem>>> => {
  try {
    const response = await apiClient.get<ApiResponse<ListResponse<TimelineItem>>>(`/api/timeline?days=${days}`)
    return response.data
  } catch (error) {
    console.error('获取时间线数据失败:', error)
    throw error
  }
}

/**
 * 获取国家维度数据
 */
export const getCountryData = async (): Promise<ApiResponse<ListResponse<CountryItem>>> => {
  try {
    const response = await apiClient.get<ApiResponse<ListResponse<CountryItem>>>('/api/country')
    return response.data
  } catch (error) {
    console.error('获取国家数据失败:', error)
    throw error
  }
}

/**
 * 获取设备维度数据
 */
export const getDeviceData = async (): Promise<ApiResponse<ListResponse<DeviceItem>>> => {
  try {
    const response = await apiClient.get<ApiResponse<ListResponse<DeviceItem>>>('/api/device')
    return response.data
  } catch (error) {
    console.error('获取设备数据失败:', error)
    throw error
  }
}

/**
 * 获取指定日期的详细数据
 * @param date 日期，格式为YYYY-MM-DD
 */
export const getDetailsData = async (date: string): Promise<ApiResponse<DetailsData>> => {
  try {
    const response = await apiClient.get<ApiResponse<DetailsData>>(`/api/details?date=${date}`)
    return response.data
  } catch (error) {
    console.error('获取详情数据失败:', error)
    throw error
  }
}

export default {
  getServerStatus,
  getOverview,
  getTimeline,
  getCountryData,
  getDeviceData,
  getDetailsData
} 