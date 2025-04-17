import axios from 'axios';

// 设置API基础URL
const API_BASE_URL = ''; // 使用相对路径，通过代理访问后端

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 响应拦截器处理统一的响应格式
api.interceptors.response.use(
  (response) => {
    // 后端返回的统一结构: { status, code, message, data }
    const { data } = response;
    if (data.status === 'success') {
      return data.data;
    }
    return Promise.reject(new Error(data.message || '请求错误'));
  },
  (error) => {
    return Promise.reject(error);
  }
);

// API接口定义
export interface OverviewData {
  user_count: number;
  event_count: number;
  device_count: number;
  total_revenue: number;
}

export interface TimelineItem {
  date: string;
  user_count: number;
  event_count: number;
  revenue: number;
}

export interface TimelineData {
  items: TimelineItem[];
  total: number;
}

export interface CountryItem {
  country: string;
  users: number;
  revenue: number;
}

export interface CountryData {
  items: CountryItem[];
  total: number;
}

export interface DeviceItem {
  device: string;
  users: number;
  revenue: number;
}

export interface DeviceData {
  items: DeviceItem[];
  total: number;
}

export interface DetailData {
  date: string;
  total_revenue: number;
  countries: { country: string; users: number }[];
  devices: { device: string; users: number }[];
}

// API请求函数
export const getOverview = async (): Promise<OverviewData> => {
  const response = await api.get<any, OverviewData>('/api/overview');
  return response;
};

export const getTimeline = async (days: number = 30): Promise<TimelineData> => {
  const response = await api.get<any, TimelineData>(`/api/timeline?days=${days}`);
  return response;
};

export const getCountryData = async (): Promise<CountryData> => {
  const response = await api.get<any, CountryData>('/api/country');
  return response;
};

export const getDeviceData = async (): Promise<DeviceData> => {
  const response = await api.get<any, DeviceData>('/api/device');
  return response;
};

export const getDetailData = async (date: string): Promise<DetailData> => {
  const response = await api.get<any, DetailData>(`/api/details?date=${date}`);
  return response;
};

export default api; 