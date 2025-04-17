// 将数字格式化为千分位
export const formatNumber = (num: number | string): string => {
  if (num === undefined || num === null) return '0';
  const numValue = typeof num === 'string' ? parseFloat(num) : num;
  return numValue.toLocaleString('zh-CN');
};

// 将数字格式化为货币形式（USD）
export const formatCurrency = (num: number | string): string => {
  if (num === undefined || num === null) return '$0.00';
  const numValue = typeof num === 'string' ? parseFloat(num) : num;
  return '$' + numValue.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

// 格式化百分比
export const formatPercent = (num: number | string, digits: number = 2): string => {
  if (num === undefined || num === null) return '0%';
  const numValue = typeof num === 'string' ? parseFloat(num) : num;
  return numValue.toLocaleString('zh-CN', {
    style: 'percent',
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
};

// 将秒转换为时分秒格式
export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;

  return [
    hours.toString().padStart(2, '0'),
    minutes.toString().padStart(2, '0'),
    remainingSeconds.toString().padStart(2, '0'),
  ].join(':');
};

// 计算同比增长率
export const calculateGrowthRate = (current: number, previous: number): number => {
  if (!previous) return 0;
  return (current - previous) / previous;
};

export default {
  formatNumber,
  formatCurrency,
  formatPercent,
  formatDuration,
  calculateGrowthRate,
}; 