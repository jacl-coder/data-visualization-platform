<script setup lang="ts">
import { ref, onMounted, computed, watchEffect, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  ToolboxComponent,
  DataZoomComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import AppLayout from '../components/AppLayout.vue'
import { getLtvOverview, getLtvData } from '../api'
import type { LtvOverviewData, LtvCountryItem, LtvDeviceItem, LtvDateItem } from '../api'
import { useViewStateStore } from '../stores/viewState'

// 获取视图状态存储
const viewStateStore = useViewStateStore()

// 注册ECharts组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  ToolboxComponent,
  DataZoomComponent,
  BarChart,
  LineChart,
  PieChart,
  CanvasRenderer
])

// 数据加载状态
const loadingOverview = ref(false)
const loadingCountryLtv = ref(false)
const loadingDeviceLtv = ref(false)
const loadingDateLtv = ref(false)

// 数据存储
const overviewData = ref<LtvOverviewData | null>(null)
const countryLtvData = ref<LtvCountryItem[]>([])
const deviceLtvData = ref<LtvDeviceItem[]>([])
const dateLtvData = ref<LtvDateItem[]>([])

// 图表引用
const ltvComparisonChartRef = ref<HTMLElement | null>(null)
const countryLtvChartRef = ref<HTMLElement | null>(null)
const deviceLtvChartRef = ref<HTMLElement | null>(null)
const dateLtvChartRef = ref<HTMLElement | null>(null)

// 图表实例
let ltvComparisonChart: echarts.ECharts | null = null
let countryLtvChart: echarts.ECharts | null = null
let deviceLtvChart: echarts.ECharts | null = null
let dateLtvChart: echarts.ECharts | null = null

// 当前选择的时间窗口
const selectedWindow = ref(viewStateStore.ltvViewState.window || 'total')
const windowOptions = [
  { value: '1d', label: '1天' },
  { value: '7d', label: '7天' },
  { value: '14d', label: '14天' },
  { value: '30d', label: '30天' },
  { value: '60d', label: '60天' },
  { value: '90d', label: '90天' },
  { value: 'total', label: '总计' }
]

// 格式化金额
const formatCurrency = (value: number): string => {
  return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

// 格式化数字
const formatNumber = (value: number): string => {
  return value.toLocaleString()
}

// 获取数据
const loadData = async () => {
  try {
    // 加载LTV概览数据
    const overviewResponse = await getLtvOverview(loadingOverview)
    if (overviewResponse && overviewResponse.status === 'success') {
      overviewData.value = overviewResponse.data
      renderLtvComparisonChart()
    }
    
    // 加载按国家分组的LTV数据
    const countryResponse = await getLtvData<LtvCountryItem>('country', selectedWindow.value, loadingCountryLtv)
    if (countryResponse && countryResponse.status === 'success') {
      countryLtvData.value = countryResponse.data.items
      renderCountryLtvChart()
    }
    
    // 加载按设备分组的LTV数据
    const deviceResponse = await getLtvData<LtvDeviceItem>('device', selectedWindow.value, loadingDeviceLtv)
    if (deviceResponse && deviceResponse.status === 'success') {
      deviceLtvData.value = deviceResponse.data.items
      renderDeviceLtvChart()
    }
    
    // 加载按日期分组的LTV数据
    const dateResponse = await getLtvData<LtvDateItem>('date', selectedWindow.value, loadingDateLtv)
    if (dateResponse && dateResponse.status === 'success') {
      dateLtvData.value = dateResponse.data.items
      renderDateLtvChart()
    }
  } catch (error) {
    console.error('加载LTV数据出错:', error)
    ElMessage.error('加载LTV数据出错')
  }
}

// 监听选择的时间窗口变化，保存到状态存储
watch(selectedWindow, (newWindow) => {
  viewStateStore.updateLtvViewState({
    window: newWindow
  })
})

// 监听选择的时间窗口变化
watchEffect(() => {
  if (selectedWindow.value) {
    loadData()
  }
})

// 渲染LTV时间窗口对比图表
const renderLtvComparisonChart = () => {
  if (!ltvComparisonChartRef.value || !overviewData.value) return
  
  if (!ltvComparisonChart) {
    ltvComparisonChart = echarts.init(ltvComparisonChartRef.value)
  }
  
  const data = overviewData.value
  const windowLabels = ['1天', '7天', '14天', '30天', '60天', '90天', '总计']
  const ltvValues = [
    data.avg_ltv_1d,
    data.avg_ltv_7d,
    data.avg_ltv_14d,
    data.avg_ltv_30d,
    data.avg_ltv_60d,
    data.avg_ltv_90d,
    data.avg_ltv_total
  ]
  
  const option = {
    title: {
      text: '平均用户LTV时间窗口对比',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params: any) {
        return `${params[0].name}: ${formatCurrency(params[0].value)}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: windowLabels
    },
    yAxis: {
      type: 'value',
      name: '平均LTV',
      axisLabel: {
        formatter: (value: number) => `$${value}`
      }
    },
    series: [
      {
        name: '平均LTV',
        type: 'bar',
        data: ltvValues,
        itemStyle: {
          color: function(params: any) {
            // 使用渐变色展示不同时间窗口的LTV
            const colorList = [
              '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452'
            ]
            return colorList[params.dataIndex % colorList.length]
          }
        },
        label: {
          show: true,
          position: 'top',
          formatter: (params: any) => formatCurrency(params.value)
        }
      }
    ]
  }
  
  ltvComparisonChart.setOption(option)
}

// 渲染国家LTV图表
const renderCountryLtvChart = () => {
  if (!countryLtvChartRef.value || countryLtvData.value.length === 0) return
  
  if (!countryLtvChart) {
    countryLtvChart = echarts.init(countryLtvChartRef.value)
  }
  
  // 仅取前10个国家，其余归类为"其他"
  const topCountries = countryLtvData.value.slice(0, 10)
  
  const option = {
    title: {
      text: `国家维度用户LTV分析 (${getWindowLabel(selectedWindow.value)})`,
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params: any) {
        const data = params.data
        return `${params.name}<br/>用户数: ${formatNumber(data.user_count)}<br/>LTV: ${formatCurrency(data.value)}`
      }
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 10,
      top: 'center',
      selected: {}
    },
    series: [
      {
        name: '国家LTV',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '55%'],
        itemStyle: {
          borderRadius: 6,
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: function(params: any) {
            return `${params.name}\n${formatCurrency(params.value)} (${params.percent}%)`
          }
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        data: topCountries.map(item => ({
          name: item.country,
          value: item.ltv_value,
          user_count: item.user_count
        }))
      }
    ]
  }
  
  countryLtvChart.setOption(option)
}

// 渲染设备LTV图表
const renderDeviceLtvChart = () => {
  if (!deviceLtvChartRef.value || deviceLtvData.value.length === 0) return
  
  if (!deviceLtvChart) {
    deviceLtvChart = echarts.init(deviceLtvChartRef.value)
  }
  
  // 准备设备维度的数据
  const deviceNames = deviceLtvData.value.map(item => item.device)
  const ltvValues = deviceLtvData.value.map(item => item.ltv_value)
  const userCounts = deviceLtvData.value.map(item => item.user_count)
  
  const option = {
    title: {
      text: `设备维度用户LTV分析 (${getWindowLabel(selectedWindow.value)})`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params: any) {
        const ltv = params[0].value
        const users = params[1].value
        return `${params[0].name}<br/>LTV: ${formatCurrency(ltv)}<br/>用户数: ${formatNumber(users)}`
      }
    },
    legend: {
      data: ['LTV值', '用户数'],
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
      data: deviceNames,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: [
      {
        type: 'value',
        name: 'LTV值',
        position: 'left',
        axisLabel: {
          formatter: (value: number) => `$${value}`
        }
      },
      {
        type: 'value',
        name: '用户数',
        position: 'right'
      }
    ],
    series: [
      {
        name: 'LTV值',
        type: 'bar',
        data: ltvValues,
        itemStyle: {
          color: '#5470c6'
        }
      },
      {
        name: '用户数',
        type: 'line',
        yAxisIndex: 1,
        data: userCounts,
        itemStyle: {
          color: '#91cc75'
        },
        symbol: 'circle',
        symbolSize: 8,
        smooth: true
      }
    ]
  }
  
  deviceLtvChart.setOption(option)
}

// 渲染日期LTV趋势图表
const renderDateLtvChart = () => {
  if (!dateLtvChartRef.value || dateLtvData.value.length === 0) return
  
  if (!dateLtvChart) {
    dateLtvChart = echarts.init(dateLtvChartRef.value)
  }
  
  // 按日期升序排序
  const sortedData = [...dateLtvData.value].sort((a, b) => 
    new Date(a.date).getTime() - new Date(b.date).getTime()
  )
  
  const dates = sortedData.map(item => item.date)
  const avgLtvs = sortedData.map(item => item.avg_ltv)
  const totalLtvs = sortedData.map(item => item.total_ltv)
  const userCounts = sortedData.map(item => item.user_count)
  
  const option = {
    title: {
      text: `LTV随时间变化趋势 (${getWindowLabel(selectedWindow.value)})`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params: any) {
        const date = params[0].axisValue
        const avgLtv = params.find((p: any) => p.seriesName === '平均LTV')?.value || 0
        const totalLtv = params.find((p: any) => p.seriesName === '总LTV')?.value || 0
        const users = params.find((p: any) => p.seriesName === '用户数')?.value || 0
        
        return `${date}<br/>
                平均LTV: ${formatCurrency(avgLtv)}<br/>
                总LTV: ${formatCurrency(totalLtv)}<br/>
                用户数: ${formatNumber(users)}`
      }
    },
    legend: {
      data: ['平均LTV', '总LTV', '用户数'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '15%',
      containLabel: true
    },
    toolbox: {
      feature: {
        saveAsImage: { title: '保存为图片' },
        restore: { title: '还原' }
      },
      right: 5,
      bottom: 10
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        start: 0,
        end: 100
      }
    ],
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        interval: 'auto',
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: 'LTV值',
        position: 'left',
        axisLabel: {
          formatter: (value: number) => `$${value}`
        }
      },
      {
        type: 'value',
        name: '用户数',
        position: 'right'
      }
    ],
    series: [
      {
        name: '平均LTV',
        type: 'line',
        data: avgLtvs,
        itemStyle: {
          color: '#5470c6'
        },
        smooth: true
      },
      {
        name: '总LTV',
        type: 'line',
        data: totalLtvs,
        itemStyle: {
          color: '#91cc75'
        },
        smooth: true
      },
      {
        name: '用户数',
        type: 'bar',
        yAxisIndex: 1,
        data: userCounts,
        itemStyle: {
          color: '#fac858'
        }
      }
    ]
  }
  
  dateLtvChart.setOption(option)
  
  // 保存初始选项，以便还原时使用
  const savedInitialOption = {...option}
  
  // 添加还原事件处理
  dateLtvChart.off('restore')
  dateLtvChart.on('restore', () => {
    // 只有当图表实例存在时才还原
    if (dateLtvChart) {
      // 还原到初始状态
      dateLtvChart.setOption(savedInitialOption, true)
      ElMessage.success('图表已还原至初始状态')
    }
  })
}

// 获取时间窗口的显示标签
const getWindowLabel = (window: string): string => {
  const option = windowOptions.find(opt => opt.value === window)
  return option ? option.label : '总计'
}

// 当窗口大小改变时，调整图表大小
window.addEventListener('resize', () => {
  ltvComparisonChart?.resize()
  countryLtvChart?.resize()
  deviceLtvChart?.resize()
  dateLtvChart?.resize()
})

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})

// LTV概览卡片数据计算
const userCount = computed(() => overviewData.value?.user_count || 0)
const totalLtv = computed(() => overviewData.value?.total_ltv || 0)
const avgLtv = computed(() => overviewData.value?.avg_ltv_total || 0)
const avgPurchases = computed(() => overviewData.value?.avg_purchases || 0)
</script>

<template>
  <AppLayout>
    <div class="ltv-view">
      <div class="view-header">
        <h1>用户生命周期价值(LTV)分析</h1>
        <div class="window-selector">
          <span>LTV窗口:</span>
          <el-select 
            v-model="selectedWindow" 
            placeholder="选择时间窗口"
            class="window-select"
          >
            <el-option
              v-for="item in windowOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </div>
      </div>
      
      <!-- LTV概览卡片 -->
      <div class="overview-cards" v-loading="loadingOverview">
        <el-card class="overview-card">
          <template #header>
            <div class="card-header">
              <span>用户总数</span>
            </div>
          </template>
          <div class="card-content">
            <span class="card-value">{{ formatNumber(userCount) }}</span>
            <span class="card-label">付费用户</span>
          </div>
        </el-card>
        
        <el-card class="overview-card">
          <template #header>
            <div class="card-header">
              <span>总LTV</span>
            </div>
          </template>
          <div class="card-content">
            <span class="card-value">{{ formatCurrency(totalLtv) }}</span>
            <span class="card-label">累计收入</span>
          </div>
        </el-card>
        
        <el-card class="overview-card">
          <template #header>
            <div class="card-header">
              <span>平均LTV</span>
            </div>
          </template>
          <div class="card-content">
            <span class="card-value">{{ formatCurrency(avgLtv) }}</span>
            <span class="card-label">每用户平均</span>
          </div>
        </el-card>
        
        <el-card class="overview-card">
          <template #header>
            <div class="card-header">
              <span>平均购买次数</span>
            </div>
          </template>
          <div class="card-content">
            <span class="card-value">{{ avgPurchases.toFixed(2) }}</span>
            <span class="card-label">次/用户</span>
          </div>
        </el-card>
      </div>
      
      <!-- LTV图表区域 -->
      <div class="chart-section">
        <!-- LTV时间窗口对比 -->
        <div class="chart-container full-width-chart" v-loading="loadingOverview">
          <div ref="ltvComparisonChartRef" class="chart"></div>
        </div>
        
        <div class="chart-row">
          <!-- 国家维度LTV对比 -->
          <div class="chart-container half-chart" v-loading="loadingCountryLtv">
            <div ref="countryLtvChartRef" class="chart"></div>
          </div>
          
          <!-- 设备维度LTV对比 -->
          <div class="chart-container half-chart" v-loading="loadingDeviceLtv">
            <div ref="deviceLtvChartRef" class="chart"></div>
          </div>
        </div>
        
        <!-- 时间趋势LTV图表 -->
        <div class="chart-container full-width-chart" v-loading="loadingDateLtv">
          <div ref="dateLtvChartRef" class="chart"></div>
        </div>
      </div>
      
      <!-- LTV详细数据表格 -->
      <div class="data-tables">
        <div class="table-section">
          <h3>国家维度LTV明细 ({{ getWindowLabel(selectedWindow) }})</h3>
          <el-table
            :data="countryLtvData"
            stripe
            border
            v-loading="loadingCountryLtv"
            class="data-table"
            :default-sort="{ prop: 'ltv_value', order: 'descending' }"
          >
            <el-table-column prop="country" label="国家" min-width="100" sortable />
            <el-table-column prop="user_count" label="用户数" min-width="100" sortable>
              <template #default="scope">
                {{ formatNumber(scope.row.user_count) }}
              </template>
            </el-table-column>
            <el-table-column prop="ltv_value" label="LTV值" min-width="120" sortable>
              <template #default="scope">
                {{ formatCurrency(scope.row.ltv_value) }}
              </template>
            </el-table-column>
            <el-table-column label="人均LTV" min-width="120">
              <template #default="scope">
                {{ formatCurrency(scope.row.ltv_value / scope.row.user_count) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div class="table-section">
          <h3>设备维度LTV明细 ({{ getWindowLabel(selectedWindow) }})</h3>
          <el-table
            :data="deviceLtvData"
            stripe
            border
            v-loading="loadingDeviceLtv"
            class="data-table"
            :default-sort="{ prop: 'ltv_value', order: 'descending' }"
          >
            <el-table-column prop="device" label="设备" min-width="100" sortable />
            <el-table-column prop="user_count" label="用户数" min-width="100" sortable>
              <template #default="scope">
                {{ formatNumber(scope.row.user_count) }}
              </template>
            </el-table-column>
            <el-table-column prop="ltv_value" label="LTV值" min-width="120" sortable>
              <template #default="scope">
                {{ formatCurrency(scope.row.ltv_value) }}
              </template>
            </el-table-column>
            <el-table-column label="人均LTV" min-width="120">
              <template #default="scope">
                {{ formatCurrency(scope.row.ltv_value / scope.row.user_count) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.ltv-view {
  width: 100%;
  padding: 0;
  background-color: #f9fafc;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e6e6e6;
}

.view-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.window-selector {
  display: flex;
  align-items: center;
}

.window-selector span {
  margin-right: 10px;
  color: #606266;
}

.window-select {
  width: 120px;
}

.overview-cards {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 30px;
}

.overview-card {
  flex: 1;
  min-width: 200px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.card-header {
  font-size: 16px;
  color: #606266;
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0;
}

.card-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.card-label {
  font-size: 14px;
  color: #909399;
}

.chart-section {
  margin-bottom: 30px;
}

.chart-container {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 15px;
  margin-bottom: 20px;
}

.chart {
  height: 350px;
  width: 100%;
}

.chart-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.half-chart {
  flex: 1;
  min-width: 0;
}

.full-width-chart {
  width: 100%;
}

.data-tables {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.table-section {
  margin-bottom: 30px;
}

.table-section h3 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.data-table {
  width: 100%;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .overview-cards {
    flex-direction: column;
  }
  
  .chart-row {
    flex-direction: column;
  }
  
  .half-chart {
    width: 100%;
  }
}
</style> 