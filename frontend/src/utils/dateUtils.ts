import dayjs from 'dayjs';

// 格式化日期为YYYY-MM-DD
export const formatDate = (date: Date | string | null): string => {
  if (!date) return '';
  return dayjs(date).format('YYYY-MM-DD');
};

// 获取当前日期
export const getCurrentDate = (): string => {
  return formatDate(new Date());
};

// 获取N天前的日期
export const getDateBefore = (days: number): string => {
  return formatDate(dayjs().subtract(days, 'day').toDate());
};

// 日期范围字符串转换为[startDate, endDate]
export const parseRangeString = (rangeStr: string): [string, string] => {
  const [start, end] = rangeStr.split(' - ');
  return [start, end || start];
};

// 检查日期是否有效
export const isValidDate = (dateStr: string): boolean => {
  return dayjs(dateStr, 'YYYY-MM-DD').isValid();
};

// 计算两个日期之间的天数
export const daysBetween = (startDate: string, endDate: string): number => {
  const start = dayjs(startDate);
  const end = dayjs(endDate);
  return end.diff(start, 'day');
};

// 获取最近N天的日期列表
export const getRecentDates = (days: number): string[] => {
  const result = [];
  for (let i = 0; i < days; i++) {
    result.push(formatDate(dayjs().subtract(i, 'day').toDate()));
  }
  return result;
};

export default {
  formatDate,
  getCurrentDate,
  getDateBefore,
  parseRangeString,
  isValidDate,
  daysBetween,
  getRecentDates,
}; 