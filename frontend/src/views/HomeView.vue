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
const timeRange = ref('week')

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

// 图表实例
const lineChartRef = ref(null)
const revenueChartRef = ref(null)
const usersChartRef = ref(null)
let lineChart: echarts.ECharts | null = null
let revenueChart: echarts.ECharts | null = null
let usersChart: echarts.ECharts | null = null

// 时间线数据
const timelineData = ref<TimelineItem[]>([])
const loading = ref(false)
const loadingOverview = ref(false)
const days = ref(30)

// 统计卡片为两行
const statCards = computed(() => [
  {
    title: '总用户数',
    value: formatNumber(overviewData.user_count),
    icon: 'User',
    color: '#3498db',
    trends: {
      day: { value: trends.user_count.day_on_day, label: '较同比' },
      week: { value: trends.user_count.week_on_week, label: '较环比' }
    }
  },
  {
    title: '总事件数',
    value: formatNumber(overviewData.event_count),
    icon: 'Bell',
    color: '#9b59b6',
    trends: {
      day: { value: trends.event_count.day_on_day, label: '较同比' },
      week: { value: trends.event_count.week_on_week, label: '较环比' }
    }
  },
  {
    title: '设备数量',
    value: formatNumber(overviewData.device_count),
    icon: 'Monitor',
    color: '#e67e22',
    trends: {
      day: { value: trends.device_count.day_on_day, label: '较同比' },
      week: { value: trends.device_count.week_on_week, label: '较环比' }
    }
  },
  {
    title: '总收入',
    value: formatCurrency(overviewData.total_revenue),
    icon: 'Money',
    color: '#27ae60',
    trends: {
      day: { value: trends.total_revenue.day_on_day, label: '较同比' },
      week: { value: trends.total_revenue.week_on_week, label: '较环比' }
    }
  }
])

// 格式化日期为YYYY-MM-DD
const formatDate = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 加载概览数据
const loadOverviewData = async (date: string = formatDate(selectedDate.value)) => {
  loadingOverview.value = true
  try {
    const response = await getOverview()
    if (response && response.status === 'success') {
      Object.assign(overviewData, response.data)
      
      // 计算实际趋势数据，使用时间序列数据计算同比和环比
      // 注意：同比是与去年同期比较，环比是与上个月比较
      
      // 获取当前数据、上月数据和去年同期数据
      const currentData = timelineData.value[0] || { user_count: 0, event_count: 0, revenue: 0 }
      
      // 查找上个月同一天的数据（约30天前）
      const lastMonthIndex = timelineData.value.findIndex(item => {
        const itemDate = new Date(item.date)
        const currentDate = new Date(currentData.date)
        const dayDiff = Math.floor((currentDate.getTime() - itemDate.getTime()) / (1000 * 60 * 60 * 24))
        return dayDiff >= 28 && dayDiff <= 31 // 大约一个月的时间差
      })
      
      // 查找去年同期的数据（约365天前）
      const lastYearIndex = timelineData.value.findIndex(item => {
        const itemDate = new Date(item.date)
        const currentDate = new Date(currentData.date)
        const dayDiff = Math.floor((currentDate.getTime() - itemDate.getTime()) / (1000 * 60 * 60 * 24))
        return dayDiff >= 360 && dayDiff <= 370 // 大约一年的时间差
      })
      
      const lastMonthData = lastMonthIndex !== -1 ? timelineData.value[lastMonthIndex] : { user_count: 0, event_count: 0, revenue: 0 }
      const lastYearData = lastYearIndex !== -1 ? timelineData.value[lastYearIndex] : { user_count: 0, event_count: 0, revenue: 0 }
      
      // 计算同比（与去年同期比较）
      if (lastYearData.user_count > 0) {
        trends.user_count.day_on_day = parseFloat(((currentData.user_count - lastYearData.user_count) / lastYearData.user_count * 100).toFixed(1))
      }
      if (lastYearData.event_count > 0) {
        trends.event_count.day_on_day = parseFloat(((currentData.event_count - lastYearData.event_count) / lastYearData.event_count * 100).toFixed(1))
      }
      if (lastYearData.revenue > 0) {
        trends.total_revenue.day_on_day = parseFloat(((currentData.revenue - lastYearData.revenue) / lastYearData.revenue * 100).toFixed(1))
      }
      
      // 计算环比（与上个月比较）
      if (lastMonthData.user_count > 0) {
        trends.user_count.week_on_week = parseFloat(((currentData.user_count - lastMonthData.user_count) / lastMonthData.user_count * 100).toFixed(1))
      }
      if (lastMonthData.event_count > 0) {
        trends.event_count.week_on_week = parseFloat(((currentData.event_count - lastMonthData.event_count) / lastMonthData.event_count * 100).toFixed(1))
      }
      if (lastMonthData.revenue > 0) {
        trends.total_revenue.week_on_week = parseFloat(((currentData.revenue - lastMonthData.revenue) / lastMonthData.revenue * 100).toFixed(1))
      }

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
  } finally {
    loadingOverview.value = false
  }
}

// 加载时间线数据
const loadTimelineData = async () => {
  loading.value = true
  try {
    const response = await getTimeline(days.value)
    if (response && response.status === 'success') {
      timelineData.value = response.data.items || []
      updateTimelineChart()
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
  loadOverviewData(formattedDate)
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
    
    if (usersChartRef.value) {
      usersChart = echarts.init(usersChartRef.value, null, { renderer: 'canvas' })
      updateDeviceChart()
    }
  }, 100) // 延长时间以确保DOM已经完全渲染
}

// 更新时间线图表
const updateTimelineChart = () => {
  if (!lineChart || timelineData.value.length === 0) return
  
  const dates = timelineData.value.map(item => item.date).reverse()
  const users = timelineData.value.map(item => item.user_count).reverse()
  const events = timelineData.value.map(item => item.event_count).reverse()
  const revenues = timelineData.value.map(item => item.revenue).reverse()
  
  const option = {
    title: {
      text: '时间线趋势',
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
      data: ['用户数', '事件数', '收入'],
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
        data: users
      },
      {
        name: '事件数',
        type: 'line',
        smooth: true,
        emphasis: {
          focus: 'series'
        },
        data: events
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
          color: '#91cc75'
        },
        areaStyle: {
          opacity: 0.2
        }
      }
    ]
  }
  
  lineChart.setOption(option)
}

// 更新收入趋势图
const updateRevenueChart = () => {
  if (!revenueChart || timelineData.value.length === 0) return
  
  // 提取最近7天的数据
  const recentData = [...timelineData.value].slice(0, 7).reverse()
  const dates = recentData.map(item => item.date)
  const revenues = recentData.map(item => item.revenue)
  
  const revenueOption = {
    title: {
      text: '近7天收入趋势',
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
      data: dates
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

// 更新设备分布图
const updateDeviceChart = async () => {
  if (!usersChart) return
  
  // 加载设备数据
  try {
    const response = await getDeviceData()
    if (response && response.status === 'success') {
      const deviceData = response.data.items || []
      
      // 准备饼图数据
      const pieData = deviceData.map(item => ({
        name: item.device,
        value: item.users
      }))
      
      const usersOption = {
        title: {
          text: '用户设备分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          type: 'scroll',
          pageIconSize: 12,
          pageTextStyle: {
            color: '#888'
          }
        },
        series: [
          {
            name: '设备分布',
            type: 'pie',
            radius: '50%',
            data: pieData,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              formatter: '{b}: {d}%'
            }
          }
        ]
      }
      
      usersChart.setOption(usersOption)
    }
  } catch (error) {
    console.error('获取设备数据失败', error)
    ElMessage.error('获取设备数据失败，将显示默认值')
    
    // 使用默认数据
    const defaultOption = {
      title: {
        text: '用户设备分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '设备分布',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 1048, name: 'Mobile' },
            { value: 735, name: 'Tablet' },
            { value: 580, name: 'Desktop' },
            { value: 484, name: 'Smart TV' },
            { value: 300, name: 'Others' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    
    usersChart.setOption(defaultOption)
  }
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
    // 更新收入趋势图
    updateRevenueChart()
  })
}

// 窗口大小变化时重新绘制图表
const handleResize = () => {
  lineChart?.resize()
  revenueChart?.resize()
  usersChart?.resize()
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
  usersChart?.dispose()
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
            <h3>时间线数据趋势</h3>
          </div>
          <div ref="lineChartRef" class="chart"></div>
        </div>
        
        <div class="chart-row">
          <!-- 收入趋势图 -->
          <div class="chart-container half-chart">
            <div class="chart-header">
              <h3>收入趋势</h3>
            </div>
            <div ref="revenueChartRef" class="chart"></div>
          </div>
          
          <!-- 用户设备分布图 -->
          <div class="chart-container half-chart">
            <div class="chart-header">
              <h3>用户设备分布</h3>
            </div>
            <div ref="usersChartRef" class="chart"></div>
          </div>
        </div>
      </div>
      
      <!-- 数据表格 -->
      <div class="data-table-section">
        <div class="table-header">
          <h3>详细数据</h3>
          <el-select v-model="days" placeholder="选择时间范围" @change="loadTimelineData">
            <el-option label="最近7天" :value="7" />
            <el-option label="最近30天" :value="30" />
            <el-option label="最近90天" :value="90" />
          </el-select>
        </div>
        
        <el-table
          :data="timelineData"
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
}

.table-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.data-table {
  width: 100%;
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