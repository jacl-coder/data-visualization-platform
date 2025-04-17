<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts/core'
import { PieChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import AppLayout from '../components/AppLayout.vue'
import { getCountryData, getDeviceData, getTimeline, getDetailsData } from '../api'
import type { CountryItem, DeviceItem, TimelineItem, DetailsData } from '../api'

// 注册ECharts组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  PieChart,
  LineChart,
  CanvasRenderer
])

// 日期范围选择
const dateRange = ref([new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), new Date()])

// 数据加载状态
const loadingCountry = ref(false)
const loadingDevice = ref(false)
const loadingTimeline = ref(false)
const loadingDetails = ref(false)

// 数据存储
const countryData = ref<CountryItem[]>([])
const deviceData = ref<DeviceItem[]>([])
const timelineData = ref<TimelineItem[]>([])
const detailsData = ref<DetailsData | null>(null)

// 图表引用
const countryChartRef = ref<HTMLElement | null>(null)
const deviceChartRef = ref<HTMLElement | null>(null)
const timelineChartRef = ref<HTMLElement | null>(null)
let countryChart: echarts.ECharts | null = null
let deviceChart: echarts.ECharts | null = null
let timelineChart: echarts.ECharts | null = null

// 加载国家数据
const loadCountryData = async () => {
  loadingCountry.value = true
  try {
    const response = await getCountryData()
    if (response && response.status === 'success') {
      countryData.value = response.data.items || []
      renderCountryChart()
    } else {
      ElMessage.warning(response?.message || '获取国家数据格式不正确')
      countryData.value = []
    }
  } catch (error) {
    console.error('获取国家数据出错', error)
    ElMessage.error('获取国家数据出错，将显示空列表')
    countryData.value = []
  } finally {
    loadingCountry.value = false
  }
}

// 加载设备数据
const loadDeviceData = async () => {
  loadingDevice.value = true
  try {
    const response = await getDeviceData()
    if (response && response.status === 'success') {
      deviceData.value = response.data.items || []
      renderDeviceChart()
    } else {
      ElMessage.warning(response?.message || '获取设备数据格式不正确')
      deviceData.value = []
    }
  } catch (error) {
    console.error('获取设备数据出错', error)
    ElMessage.error('获取设备数据出错，将显示空列表')
    deviceData.value = []
  } finally {
    loadingDevice.value = false
  }
}

// 加载时间线数据
const loadTimelineData = async () => {
  loadingTimeline.value = true
  try {
    const response = await getTimeline(30)
    if (response && response.status === 'success') {
      timelineData.value = response.data.items || []
      renderTimelineChart()
    } else {
      ElMessage.warning(response?.message || '获取时间线数据格式不正确')
      timelineData.value = []
    }
  } catch (error) {
    console.error('获取时间线数据出错', error)
    ElMessage.error('获取时间线数据出错，将显示空列表')
    timelineData.value = []
  } finally {
    loadingTimeline.value = false
  }
}

// 加载详情数据
const loadDetailsData = async (date: string) => {
  loadingDetails.value = true
  try {
    const response = await getDetailsData(date)
    if (response && response.status === 'success') {
      detailsData.value = response.data
    } else {
      ElMessage.warning(response?.message || '获取详情数据格式不正确')
      detailsData.value = createEmptyDetailsData(date)
    }
  } catch (error) {
    console.error('获取详情数据出错', error)
    ElMessage.error('获取详情数据出错，将显示默认值')
    detailsData.value = createEmptyDetailsData(date)
  } finally {
    loadingDetails.value = false
  }
}

// 创建空的详情数据
const createEmptyDetailsData = (date: string): DetailsData => {
  return {
    date: date,
    total_revenue: 0,
    countries: [],
    devices: []
  }
}

// 渲染国家维度饼图
const renderCountryChart = () => {
  if (!countryChartRef.value) return
  
  if (!countryChart) {
    countryChart = echarts.init(countryChartRef.value)
  }

  const data = countryData.value.map(item => ({
    name: item.country,
    value: item.users
  }))
  
  const option = {
    title: {
      text: '国家用户占比',
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
        name: '国家分布',
        type: 'pie',
        radius: '60%',
        center: ['50%', '60%'],
        data: data.length > 0 ? data : [{ name: '无数据', value: 1 }],
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
  
  countryChart.setOption(option)
}

// 渲染设备维度饼图
const renderDeviceChart = () => {
  if (!deviceChartRef.value) return
  
  if (!deviceChart) {
    deviceChart = echarts.init(deviceChartRef.value)
  }

  const data = deviceData.value.map(item => ({
    name: item.device,
    value: item.users
  }))
  
  const option = {
    title: {
      text: '设备用户占比',
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
        radius: '60%',
        center: ['50%', '60%'],
        data: data.length > 0 ? data : [{ name: '无数据', value: 1 }],
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
  
  deviceChart.setOption(option)
}

// 渲染时间线图表
const renderTimelineChart = () => {
  if (!timelineChartRef.value) return
  
  if (!timelineChart) {
    timelineChart = echarts.init(timelineChartRef.value)
  }

  const dates = timelineData.value.map(item => item.date).reverse()
  const users = timelineData.value.map(item => item.user_count).reverse()
  const revenues = timelineData.value.map(item => item.revenue).reverse()
  
  const option = {
    title: {
      text: '用户和收入趋势'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: ['用户数', '收入']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: dates.length > 0 ? dates : ['无数据']
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '用户数',
        position: 'left'
      },
      {
        type: 'value',
        name: '收入($)',
        position: 'right'
      }
    ],
    series: [
      {
        name: '用户数',
        type: 'line',
        data: users.length > 0 ? users : [0],
        yAxisIndex: 0,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#409EFF'
        },
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '收入',
        type: 'line',
        data: revenues.length > 0 ? revenues : [0],
        yAxisIndex: 1,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#303133'
        },
        itemStyle: {
          color: '#303133'
        }
      }
    ]
  }
  
  timelineChart.setOption(option)
}

// 日期范围变化处理
const handleDateRangeChange = (range: [Date, Date]) => {
  dateRange.value = range
  // 可以根据日期范围重新加载数据
}

// 格式化数字
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

// 格式化金额
const formatCurrency = (amount: number) => {
  return `$${amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

// 当前日期
const currentDate = computed(() => {
  const today = new Date()
  return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
})

// 初始加载
onMounted(() => {
  loadCountryData()
  loadDeviceData()
  loadTimelineData()
  loadDetailsData(currentDate.value)
  
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
const handleResize = () => {
  countryChart?.resize()
  deviceChart?.resize()
  timelineChart?.resize()
}
</script>

<template>
  <AppLayout>
    <div class="details-view">
      <!-- 国家和设备数据 -->
      <div class="data-section">
        <!-- 国家数据 -->
        <div class="country-section">
          <div class="section-header">
            <h2>国家数据分析</h2>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              @change="handleDateRangeChange"
            />
          </div>
          
          <div class="data-content">
            <div class="data-table">
              <el-table
                :data="countryData.slice(0, 10)"
                stripe
                border
                v-loading="loadingCountry"
                style="width: 100%"
              >
                <el-table-column prop="country" label="国家" width="120" />
                <el-table-column prop="users" label="用户数" width="120">
                  <template #default="scope">
                    {{ formatNumber(scope.row.users) }}
                  </template>
                </el-table-column>
                <el-table-column prop="revenue" label="收入">
                  <template #default="scope">
                    {{ formatCurrency(scope.row.revenue) }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="data-chart" ref="countryChartRef"></div>
          </div>
        </div>
        
        <!-- 设备数据 -->
        <div class="device-section">
          <div class="section-header">
            <h2>设备数据分析</h2>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              @change="handleDateRangeChange"
            />
          </div>
          
          <div class="data-content">
            <div class="data-table">
              <el-table
                :data="deviceData"
                stripe
                border
                v-loading="loadingDevice"
                style="width: 100%"
              >
                <el-table-column prop="device" label="设备" width="120" />
                <el-table-column prop="users" label="用户数" width="120">
                  <template #default="scope">
                    {{ formatNumber(scope.row.users) }}
                  </template>
                </el-table-column>
                <el-table-column prop="revenue" label="收入">
                  <template #default="scope">
                    {{ formatCurrency(scope.row.revenue) }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="data-chart" ref="deviceChartRef"></div>
          </div>
        </div>
      </div>
      
      <!-- 时间序列图表 -->
      <div class="timeline-section">
        <div class="section-header">
          <h2>日期统计</h2>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            @change="handleDateRangeChange"
          />
        </div>
        
        <div class="timeline-chart" ref="timelineChartRef"></div>
      </div>
      
      <!-- 详细数据表格 -->
      <div class="details-section">
        <div class="section-header">
          <h2>详细数据</h2>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            @change="handleDateRangeChange"
          />
        </div>
        
        <el-table
          :data="timelineData"
          stripe
          border
          v-loading="loadingDetails"
          style="width: 100%"
        >
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="user_count" label="用户数" width="120">
            <template #default="scope">
              {{ formatNumber(scope.row.user_count) }}
            </template>
          </el-table-column>
          <el-table-column prop="event_count" label="事件数" width="120">
            <template #default="scope">
              {{ formatNumber(scope.row.event_count) }}
            </template>
          </el-table-column>
          <el-table-column prop="revenue" label="收入" width="150">
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
.details-view {
  width: 100%;
}

.data-section {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px;
}

.country-section,
.device-section {
  flex: 1;
  min-width: 580px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.data-content {
  display: flex;
  flex-direction: column;
}

.data-table {
  margin-bottom: 20px;
}

.data-chart {
  height: 300px;
  width: 100%;
}

.timeline-section {
  margin-bottom: 30px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.timeline-chart {
  height: 400px;
  width: 100%;
}

.details-section {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

@media (max-width: 1200px) {
  .country-section,
  .device-section {
    min-width: 100%;
  }
}
</style> 