<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import AppLayout from '../components/AppLayout.vue'
import { getOverview, getTimeline, getDeviceData } from '../api'
import type { OverviewData, TimelineItem } from '../api'
import * as echarts from 'echarts/core'
import { LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  LegendComponent
} from 'echarts/components'
import { LabelLayout, UniversalTransition } from 'echarts/features'
import { CanvasRenderer } from 'echarts/renderers'

// 注册必须的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  LegendComponent,
  LineChart,
  PieChart,
  LabelLayout,
  UniversalTransition,
  CanvasRenderer
])

// 日期选择
const selectedDate = ref(new Date())
const timeRange = ref('month')

// 概览数据
const overviewData = reactive<OverviewData>({
  user_count: 0,
  event_count: 0,
  device_count: 0,
  total_revenue: 0
})

// 指标趋势数据
const trends = reactive({
  user_count: { 
    day_on_day: 0,
    week_on_week: 0
  },
  event_count: {
    day_on_day: 0, 
    week_on_week: 0
  },
  device_count: {
    day_on_day: 0,
    week_on_week: 0
  },
  total_revenue: {
    day_on_day: 0,
    week_on_week: 0
  }
})

// 选中日期的数据
const selectedDateData = reactive({
  user_count: 0,
  event_count: 0,
  device_count: 0,
  revenue: 0
})

// 图表实例
const lineChartRef = ref(null)
const revenueChartRef = ref(null)
const deviceChartRef = ref(null)
let lineChart: echarts.ECharts | null = null
let revenueChart: echarts.ECharts | null = null
let deviceChart: echarts.ECharts | null = null

// 时间线数据
const timelineData = ref<TimelineItem[]>([])
const loading = ref(false)
const loadingOverview = ref(false)
const days = ref(30)

// 统计卡片为两行
const statCards = computed(() => [
  {
    title: '当日用户数',
    value: formatNumber(selectedDateData.user_count),
    icon: 'User',
    color: '#3498db',
    trends: {
      day: { value: trends.user_count.day_on_day, label: '较同比' },
      week: { value: trends.user_count.week_on_week, label: '较环比' }
    }
  },
  {
    title: '当日事件数',
    value: formatNumber(selectedDateData.event_count),
    icon: 'Bell',
    color: '#9b59b6',
    trends: {
      day: { value: trends.event_count.day_on_day, label: '较同比' },
      week: { value: trends.event_count.week_on_week, label: '较环比' }
    }
  },
  {
    title: '当日设备数',
    value: formatNumber(selectedDateData.device_count),
    icon: 'Monitor',
    color: '#e67e22',
    trends: {
      day: { value: trends.device_count.day_on_day, label: '较同比' },
      week: { value: trends.device_count.week_on_week, label: '较环比' }
    }
  },
  {
    title: '当日收入',
    value: formatCurrency(selectedDateData.revenue),
    icon: 'Money',
    color: '#27ae60',
    trends: {
      day: { value: trends.total_revenue.day_on_day, label: '较同比' },
      week: { value: trends.total_revenue.week_on_week, label: '较环比' }
    }
  }
])

// 日期选择器的禁用日期函数
const disabledDate = (time: Date) => {
  return time.getTime() > Date.now();
}

// 格式化日期为YYYY-MM-DD
const formatDate = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 格式化日期为YYYY-MM-DD 或 "今天"
const formatDateOrToday = (date: Date): string => {
  const today = new Date();
  
  // 检查是否为今天
  if (date.getFullYear() === today.getFullYear() &&
      date.getMonth() === today.getMonth() &&
      date.getDate() === today.getDate()) {
    return "今天";
  } else {
    return formatDate(date);
  }
}

// 根据选择的日期更新卡片数据
const updateCardsBySelectedDate = (date: string) => {
  // 查找选中日期的数据
  const dateData = timelineData.value.find(item => item.date === date);
  
  if (dateData) {
    // 更新选中日期的数据
    selectedDateData.user_count = dateData.user_count;
    selectedDateData.event_count = dateData.event_count;
    selectedDateData.revenue = dateData.revenue;
    
    // 使用日期数据中的设备数，而不是概览数据中的总设备数
    selectedDateData.device_count = dateData.device_count;
    
    // 计算选中日期的同比和环比数据
    
    // 选中日期的信息
    const selectedDateObj = new Date(date);
    const selectedMonth = selectedDateObj.getMonth(); // 0-11
    const selectedDay = selectedDateObj.getDate(); // 1-31
    const selectedYear = selectedDateObj.getFullYear();
    
    // 去年同日的日期 - 确保是同一月同一天
    const lastYearDate = `${selectedYear - 1}-${String(selectedMonth + 1).padStart(2, '0')}-${String(selectedDay).padStart(2, '0')}`;
    
    // 上月同日的日期
    let lastMonthYear = selectedYear;
    let lastMonth = selectedMonth - 1;
    
    // 处理跨年的情况
    if (lastMonth < 0) {
      lastMonth = 11; // 12月
      lastMonthYear = selectedYear - 1;
    }
    
    // 处理月份天数不同的情况（如31日）
    let lastMonthDay = selectedDay;
    const daysInLastMonth = new Date(lastMonthYear, lastMonth + 1, 0).getDate();
    if (lastMonthDay > daysInLastMonth) {
      lastMonthDay = daysInLastMonth; // 如果上个月没有这一天，则使用上个月的最后一天
    }
    
    const lastMonthDate = `${lastMonthYear}-${String(lastMonth + 1).padStart(2, '0')}-${String(lastMonthDay).padStart(2, '0')}`;
    
    // 查找去年同日的数据（精确匹配）
    const lastYearData = timelineData.value.find(item => item.date === lastYearDate) 
      || { user_count: 0, event_count: 0, revenue: 0, device_count: 0 };
    
    // 查找上月同日的数据（精确匹配）
    const lastMonthData = timelineData.value.find(item => item.date === lastMonthDate)
      || { user_count: 0, event_count: 0, revenue: 0, device_count: 0 };
    
    console.log(`比较日期: 当前=${date}, 去年同日=${lastYearDate}, 上月同日=${lastMonthDate}`);
    
    // 计算同比（与去年同期比较）- 确保是同一月同一天
    if (lastYearData.user_count > 0) {
      trends.user_count.day_on_day = parseFloat(((dateData.user_count - lastYearData.user_count) / lastYearData.user_count * 100).toFixed(1));
    } else {
      trends.user_count.day_on_day = 0;
    }
    
    if (lastYearData.event_count > 0) {
      trends.event_count.day_on_day = parseFloat(((dateData.event_count - lastYearData.event_count) / lastYearData.event_count * 100).toFixed(1));
    } else {
      trends.event_count.day_on_day = 0;
    }
    
    if (lastYearData.revenue > 0) {
      trends.total_revenue.day_on_day = parseFloat(((dateData.revenue - lastYearData.revenue) / lastYearData.revenue * 100).toFixed(1));
    } else {
      trends.total_revenue.day_on_day = 0;
    }
    
    // 计算设备数的同比
    if (lastYearData.device_count > 0) {
      trends.device_count.day_on_day = parseFloat(((dateData.device_count - lastYearData.device_count) / lastYearData.device_count * 100).toFixed(1));
    } else {
      trends.device_count.day_on_day = 0;
    }
    
    // 计算环比（与上个月比较）- 确保是上月同一天
    if (lastMonthData.user_count > 0) {
      trends.user_count.week_on_week = parseFloat(((dateData.user_count - lastMonthData.user_count) / lastMonthData.user_count * 100).toFixed(1));
    } else {
      trends.user_count.week_on_week = 0;
    }
    
    if (lastMonthData.event_count > 0) {
      trends.event_count.week_on_week = parseFloat(((dateData.event_count - lastMonthData.event_count) / lastMonthData.event_count * 100).toFixed(1));
    } else {
      trends.event_count.week_on_week = 0;
    }
    
    if (lastMonthData.revenue > 0) {
      trends.total_revenue.week_on_week = parseFloat(((dateData.revenue - lastMonthData.revenue) / lastMonthData.revenue * 100).toFixed(1));
    } else {
      trends.total_revenue.week_on_week = 0;
    }
    
    // 计算设备数的环比
    if (lastMonthData.device_count > 0) {
      trends.device_count.week_on_week = parseFloat(((dateData.device_count - lastMonthData.device_count) / lastMonthData.device_count * 100).toFixed(1));
    } else {
      trends.device_count.week_on_week = 0;
    }
  } else {
    // 如果找不到对应日期的数据，置为0
    selectedDateData.user_count = 0;
    selectedDateData.event_count = 0;
    selectedDateData.device_count = 0;
    selectedDateData.revenue = 0;
    
    // 同时重置趋势数据
    trends.user_count.day_on_day = 0;
    trends.user_count.week_on_week = 0;
    trends.event_count.day_on_day = 0;
    trends.event_count.week_on_week = 0;
    trends.device_count.day_on_day = 0;
    trends.device_count.week_on_week = 0;
    trends.total_revenue.day_on_day = 0;
    trends.total_revenue.week_on_week = 0;
  }
}

// 加载概览数据
const loadOverviewData = async (date: string = formatDate(selectedDate.value)) => {
  loadingOverview.value = true
  try {
    const response = await getOverview()
    if (response && response.status === 'success') {
      Object.assign(overviewData, response.data)
      
      // 更新选中日期的卡片数据
      updateCardsBySelectedDate(date)
      
      // 已在updateCardsBySelectedDate中计算同比和环比，不需要在这里重复计算
      
      // 在数据加载后初始化图表
      initCharts()
    } else if (response) {
      ElMessage.warning(response.message || '获取概览数据格式不正确')
    }
  } catch (error) {
    console.error('获取概览数据出错', error)
    ElMessage.error('获取概览数据出错，将显示默认值')
    Object.assign(overviewData, {
      user_count: 0,
      event_count: 0,
      device_count: 0,
      total_revenue: 0
    })
    
    // 重置选中日期的数据
    Object.assign(selectedDateData, {
      user_count: 0,
      event_count: 0,
      device_count: 0,
      revenue: 0
    })
    
    // 重置趋势数据
    Object.assign(trends, {
      user_count: { day_on_day: 0, week_on_week: 0 },
      event_count: { day_on_day: 0, week_on_week: 0 },
      device_count: { day_on_day: 0, week_on_week: 0 },
      total_revenue: { day_on_day: 0, week_on_week: 0 }
    })
  } finally {
    loadingOverview.value = false
  }
}

// 加载时间线数据
const loadTimelineData = async () => {
  loading.value = true
  try {
    // 使用选择的日期作为结束日期，而不是当前日期
    const endDate = new Date(selectedDate.value) // 所选日期
    const startDate = new Date(selectedDate.value)
    startDate.setDate(endDate.getDate() - days.value + 1) // 往前推days.value天
    
    // 格式化日期为YYYY-MM-DD（用于显示）
    const endDateDisplay = formatDateOrToday(endDate)
    const startDateDisplay = formatDateOrToday(startDate)
    
    // 格式化日期为YYYY-MM-DD（用于API调用）
    const endDateStr = formatDate(endDate)
    const startDateStr = formatDate(startDate)
    
    // 使用日期范围参数加载数据
    const dateRangeParam = `${startDateStr}|${endDateStr}`
    
    const response = await getTimeline(days.value, dateRangeParam)
    if (response && response.status === 'success') {
      // 获取返回的数据
      const apiData = response.data.items || []
      
      // 创建日期填充后的数据结构
      const filledData = []
      
      // 为每一天创建日期对象，从最早的日期开始
      for (let i = days.value - 1; i >= 0; i--) {
        const currentDate = new Date(endDate)
        currentDate.setDate(endDate.getDate() - i)
        // 对于表格显示使用格式化的日期
        const dateStr = formatDate(currentDate)
        
        // 查找该日期的数据
        const dayData = apiData.find(item => item.date === dateStr)
        
        if (dayData) {
          // 如果有数据，使用API返回的数据
          filledData.push(dayData)
        } else {
          // 如果没有数据，使用空数据填充
          filledData.push({
            date: dateStr,
            user_count: 0,
            event_count: 0,
            revenue: 0,
            device_count: 0
          })
        }
      }
      
      // 数据已经是从早到晚排序的
      timelineData.value = filledData
      
      // 更新所有图表
      updateTimelineChart()
      updateRevenueChart()
      updateDeviceChart()
      
      // 加载时间线数据后，更新选中日期的卡片数据
      updateCardsBySelectedDate(formatDate(selectedDate.value))
    } else if (response) {
      ElMessage.warning(response.message || '获取时间线数据格式不正确')
      timelineData.value = []
    } else {
      timelineData.value = []
    }
  } catch (error) {
    console.error('获取时间线数据出错', error)
    ElMessage.error('获取时间线数据出错，将显示空列表')
    timelineData.value = []
  } finally {
    loading.value = false
  }
}

// 格式化数字
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

// 格式化金额
const formatCurrency = (amount: number) => {
  return `$${amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

// 格式化百分比
const formatPercentage = (value: number) => {
  const prefix = value >= 0 ? '+' : ''
  return `${prefix}${value}%`
}

// 日期变化处理
const handleDateChange = (date: Date) => {
  selectedDate.value = date
  const formattedDate = formatDate(date)
  
  // 重新加载时间线数据，这会自动更新图表
  loadTimelineData().then(() => {
    // 根据选择的日期更新卡片数据
    updateCardsBySelectedDate(formattedDate)
    
    // 加载概览数据（仍然需要加载以更新其他图表）
    loadOverviewData(formattedDate)
    
    // 确保收入和设备图表也更新
    updateRevenueChart()
    updateDeviceChart()
  })
}

// 初始化图表
const initCharts = () => {
  // 在下一个渲染周期初始化图表
  setTimeout(() => {
    if (lineChartRef.value) {
      lineChart = echarts.init(lineChartRef.value, null, { renderer: 'canvas' })
      updateTimelineChart()
    }
    
    if (revenueChartRef.value) {
      revenueChart = echarts.init(revenueChartRef.value, null, { renderer: 'canvas' })
      updateRevenueChart()
    }
    
    if (deviceChartRef.value) {
      deviceChart = echarts.init(deviceChartRef.value, null, { renderer: 'canvas' })
      updateDeviceChart()
    }
  }, 100) // 延长时间以确保DOM已经完全渲染
}

// 更新时间线图表
const updateTimelineChart = () => {
  if (!lineChart || timelineData.value.length === 0) return
  
  const dates = timelineData.value.map(item => item.date)
  const users = timelineData.value.map(item => item.user_count)
  const events = timelineData.value.map(item => item.event_count)
  const revenues = timelineData.value.map(item => item.revenue)
  const devices = timelineData.value.map(item => item.device_count)
  
  const option = {
    title: {
      text: '多维度指标对比',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params: any) {
        const date = params[0].axisValue
        let res = `<div style="font-weight:bold;margin-bottom:5px;">${date}</div>`
        
        params.forEach((param: any) => {
          let value = param.value
          if (param.seriesName === '收入') {
            value = '$' + value.toLocaleString(undefined, { 
              minimumFractionDigits: 2, 
              maximumFractionDigits: 2 
            })
          } else {
            value = value.toLocaleString()
          }
          
          res += `<div style="margin: 3px 0">
            <span style="display:inline-block;margin-right:5px;border-radius:50%;width:10px;height:10px;background-color:${param.color};"></span>
            <span>${param.seriesName}: ${value}</span>
          </div>`
        })
        
        return res
      }
    },
    legend: {
      data: ['用户数', '事件数', '设备数', '收入'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: [
      {
        type: 'value',
        name: '数量',
        position: 'left',
        axisLine: {
          show: true,
          lineStyle: {
            color: '#5470c6'
          }
        },
        axisLabel: {
          formatter: '{value}'
        }
      },
      {
        type: 'value',
        name: '收入($)',
        position: 'right',
        axisLine: {
          show: true,
          lineStyle: {
            color: '#91cc75'
          }
        },
        axisLabel: {
          formatter: '${value}'
        }
      }
    ],
    series: [
      {
        name: '用户数',
        type: 'line',
        smooth: true,
        emphasis: {
          focus: 'series'
        },
        data: users,
        itemStyle: {
          color: '#3498db'
        }
      },
      {
        name: '事件数',
        type: 'line',
        smooth: true,
        emphasis: {
          focus: 'series'
        },
        data: events,
        itemStyle: {
          color: '#9b59b6'
        }
      },
      {
        name: '设备数',
        type: 'line',
        smooth: true,
        emphasis: {
          focus: 'series'
        },
        data: devices,
        itemStyle: {
          color: '#e67e22'
        }
      },
      {
        name: '收入',
        type: 'line',
        yAxisIndex: 1,
        smooth: true,
        emphasis: {
          focus: 'series'
        },
        data: revenues,
        itemStyle: {
          color: '#27ae60'
        },
        areaStyle: {
          opacity: 0.2
        }
      }
    ]
  }
  
  lineChart.setOption(option)
  
  // 同时更新收入和设备图表
  updateRevenueChart()
  updateDeviceChart()
}

// 更新收入趋势图
const updateRevenueChart = () => {
  if (!revenueChart || timelineData.value.length === 0) return
  
  // 根据选择的时间范围确定要显示的天数
  let daysToShow = 7; // 默认为7天
  
  if (timeRange.value === 'month') {
    daysToShow = 30;
  } else if (timeRange.value === 'quarter') {
    daysToShow = 90;
  }
  
  // 确保不超过实际数据数量
  daysToShow = Math.min(daysToShow, timelineData.value.length);
  
  // 根据时间范围获取最新的N天数据
  const recentData = timelineData.value.slice(-daysToShow);
  
  const dates = recentData.map(item => item.date);
  const revenues = recentData.map(item => item.revenue);
  
  // 根据时间范围设置标题
  let titleText = '';
  if (timeRange.value === 'week') {
    titleText = '周收入分析';
  } else if (timeRange.value === 'month') {
    titleText = '月度收入表现';
  } else if (timeRange.value === 'quarter') {
    titleText = '季度收入概览';
  }
  
  const revenueOption = {
    title: {
      text: titleText,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params: any) {
        const date = params[0].axisValue
        return `${date}: $${params[0].value.toFixed(2)}`
      }
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: daysToShow > 15 ? 45 : 0 // 数据多时倾斜显示
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '${value}'
      }
    },
    series: [{
      data: revenues,
      type: 'line',
      smooth: true,
      areaStyle: {
        opacity: 0.3
      },
      itemStyle: {
        color: '#27ae60'
      }
    }]
  }
  
  revenueChart.setOption(revenueOption)
}

// 更新设备趋势图
const updateDeviceChart = () => {
  if (!deviceChart || timelineData.value.length === 0) return
  
  // 根据选择的时间范围确定要显示的天数
  let daysToShow = 7; // 默认为7天
  
  if (timeRange.value === 'month') {
    daysToShow = 30;
  } else if (timeRange.value === 'quarter') {
    daysToShow = 90;
  }
  
  // 确保不超过实际数据数量
  daysToShow = Math.min(daysToShow, timelineData.value.length);
  
  // 根据时间范围获取最新的N天数据
  const recentData = timelineData.value.slice(-daysToShow);
  
  const dates = recentData.map(item => item.date);
  const deviceCounts = recentData.map(item => item.device_count || 0);
  
  // 根据时间范围设置标题
  let titleText = '';
  if (timeRange.value === 'week') {
    titleText = '周设备活跃统计';
  } else if (timeRange.value === 'month') {
    titleText = '月度设备分布';
  } else if (timeRange.value === 'quarter') {
    titleText = '季度设备变化';
  }
  
  const deviceOption = {
    title: {
      text: titleText,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params: any) {
        const date = params[0].axisValue
        return `${date}: ${params[0].value} 台设备`
      }
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: daysToShow > 15 ? 45 : 0 // 数据多时倾斜显示
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: deviceCounts,
      type: 'line',
      smooth: true,
      areaStyle: {
        opacity: 0.3
      },
      itemStyle: {
        color: '#3498db'
      }
    }]
  }
  
  deviceChart.setOption(deviceOption)
}

// 时间范围变化
const handleTimeRangeChange = () => {
  switch (timeRange.value) {
    case 'week':
      days.value = 7
      break
    case 'month':
      days.value = 30
      break
    case 'quarter':
      days.value = 90
      break
  }
  loadTimelineData().then(() => {
    // 更新收入趋势图和设备趋势图
    updateRevenueChart()
    updateDeviceChart()
  })
}

// 窗口大小变化时重新绘制图表
const handleResize = () => {
  lineChart?.resize()
  revenueChart?.resize()
  deviceChart?.resize()
}

// 初始加载数据
onMounted(() => {
  // 先加载时间线数据，再加载概览数据
  loadTimelineData().then(() => {
    loadOverviewData()
  })
  window.addEventListener('resize', handleResize)
})

// 组件卸载时移除事件监听
const onUnmounted = () => {
  window.removeEventListener('resize', handleResize)
  // 销毁图表实例
  lineChart?.dispose()
  revenueChart?.dispose()
  deviceChart?.dispose()
}
</script>

<template>
  <AppLayout>
    <div class="dashboard">
      <!-- 顶部信息栏 -->
      <div class="dashboard-header">
        <div class="dashboard-title">
          <h1>数据分析仪表盘</h1>
          <span class="dashboard-subtitle">实时监控业务核心指标</span>
        </div>
        
        <div class="dashboard-actions">
          <el-date-picker
            v-model="selectedDate"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            class="date-picker"
            @change="handleDateChange"
            :disabled-date="disabledDate"
          />
          
          <el-radio-group v-model="timeRange" class="time-range-selector" @change="handleTimeRangeChange">
            <el-radio-button value="week">周</el-radio-button>
            <el-radio-button value="month">月</el-radio-button>
            <el-radio-button value="quarter">季度</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      
      <!-- 统计卡片 -->
      <div class="stat-cards" v-loading="loadingOverview">
        <div 
          v-for="(card, index) in statCards" 
          :key="index" 
          class="stat-card"
          :style="{borderTopColor: card.color}"
        >
          <div class="stat-card-header">
            <div class="stat-card-icon" :style="{backgroundColor: card.color}">
              <el-icon><component :is="card.icon" /></el-icon>
            </div>
            <div class="stat-card-title">{{ card.title }}</div>
          </div>
          
          <div class="stat-card-value">{{ card.value }}</div>
          
          <div class="stat-card-footer">
            <div class="trend-item">
              <span class="trend-label">{{ card.trends.day.label }}</span>
              <span class="trend-value" :class="card.trends.day.value >= 0 ? 'up' : 'down'">
                {{ formatPercentage(card.trends.day.value) }}
              </span>
            </div>
            <div class="trend-item">
              <span class="trend-label">{{ card.trends.week.label }}</span>
              <span class="trend-value" :class="card.trends.week.value >= 0 ? 'up' : 'down'">
                {{ formatPercentage(card.trends.week.value) }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 图表区域 -->
      <div class="chart-section">
        <!-- 时间线趋势图 -->
        <div class="chart-container main-chart" v-loading="loading">
          <div class="chart-header">
            <h3>多维度数据指标实时监控</h3>
          </div>
          <div ref="lineChartRef" class="chart"></div>
        </div>
        
        <div class="chart-row">
          <!-- 收入趋势图 -->
          <div class="chart-container half-chart">
            <div class="chart-header">
              <h3>业务收入动态表现</h3>
            </div>
            <div ref="revenueChartRef" class="chart"></div>
          </div>
          
          <!-- 用户设备分布图 -->
          <div class="chart-container half-chart">
            <div class="chart-header">
              <h3>设备活跃度分析</h3>
            </div>
            <div ref="deviceChartRef" class="chart"></div>
          </div>
        </div>
      </div>
      
      <!-- 数据表格 -->
      <div class="data-table-section">
        <div class="table-header">
          <h3>详情数据</h3>
          <el-select 
            v-model="days" 
            placeholder="选择时间范围" 
            @change="loadTimelineData"
            class="days-select"
          >
            <el-option label="最近7天" :value="7" />
            <el-option label="最近30天" :value="30" />
            <el-option label="最近90天" :value="90" />
          </el-select>
        </div>
        
        <el-table
          :data="[...timelineData].reverse()"
          stripe
          border
          v-loading="loading"
          class="data-table"
        >
          <el-table-column prop="date" label="日期" min-width="100" />
          <el-table-column prop="user_count" label="用户数" min-width="100">
            <template #default="scope">
              {{ formatNumber(scope.row.user_count) }}
            </template>
          </el-table-column>
          <el-table-column prop="event_count" label="事件数" min-width="100">
            <template #default="scope">
              {{ formatNumber(scope.row.event_count) }}
            </template>
          </el-table-column>
          <el-table-column label="设备数" min-width="100">
            <template #default="scope">
              {{ formatNumber(scope.row.device_count) }}
            </template>
          </el-table-column>
          <el-table-column prop="revenue" label="收入" min-width="120">
            <template #default="scope">
              {{ formatCurrency(scope.row.revenue) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.dashboard {
  width: 100%;
  padding: 0;
  background-color: #f9fafc;
  min-width: 100%;
  max-width: 100%;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e6e6e6;
  width: 100%;
}

.dashboard-title {
  display: flex;
  flex-direction: column;
}

.dashboard-title h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.dashboard-subtitle {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.dashboard-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.date-picker {
  width: 180px;
}

.time-range-selector {
  margin-left: 10px;
}

/* 统计卡片 */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.stat-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border-top: 3px solid #dcdfe6;
  display: flex;
  flex-direction: column;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.stat-card-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.stat-card-icon {
  width: 35px;
  height: 35px;
  border-radius: 8px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.stat-card-title {
  font-size: 16px;
  font-weight: 500;
  color: #606266;
}

.stat-card-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
}

.stat-card-footer {
  display: flex;
  justify-content: space-between;
  margin-top: auto;
}

.trend-item {
  display: flex;
  flex-direction: column;
}

.trend-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 2px;
}

.trend-value {
  font-size: 14px;
  font-weight: 500;
}

.trend-value.up {
  color: #f56c6c;
}

.trend-value.down {
  color: #67c23a;
}

/* 图表区域 */
.chart-section {
  margin-bottom: 25px;
}

.chart-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
  width: 100%;
}

.chart-header {
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
}

.chart-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.chart {
  height: 350px;
  width: 100%;
  padding: 10px;
}

.main-chart .chart {
  height: 400px;
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  width: 100%;
}

.half-chart .chart {
  height: 300px;
}

/* 数据表格 */
.data-table-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 0;
  margin-bottom: 20px;
  width: 100%;
  overflow-x: auto;
}

.table-header {
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: nowrap;
}

.table-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
}

.data-table {
  width: 100%;
}

.days-select {
  min-width: 120px;
  width: auto;
  margin-left: 10px;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .stat-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart-row {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .dashboard-actions {
    margin-top: 15px;
    width: 100%;
    justify-content: space-between;
  }
  
  .stat-cards {
    grid-template-columns: 1fr;
  }
  
  .date-picker {
    width: 140px;
  }
}
</style> 