<script setup lang="ts">
import { ref, onMounted, computed, watch, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts/core'
import { PieChart, LineChart, BarChart } from 'echarts/charts'
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
import { getCountryData, getDeviceData, getTimeline, getDetailsData, clearApiCache } from '../api'
import type { CountryItem, DeviceItem, TimelineItem, DetailsData } from '../api'

// 注册ECharts组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  ToolboxComponent,
  DataZoomComponent,
  PieChart,
  LineChart,
  BarChart,
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

// 格式化日期为YYYY-MM-DD
const formatDate = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 为兼容性保留此引用，但实际使用日期范围
const selectedDate = ref(formatDate(new Date()))

// 日期范围快捷选项
const dateRangeShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    }
  }
]

// 加载国家数据
const loadCountryData = async (date?: string) => {
  try {
    const response = await getCountryData(date, loadingCountry)
    if (response && response.status === 'success') {
      countryData.value = response.data.items || []
      renderCountryChart()
    } else if (response) {
      ElMessage.warning(response.message || '获取国家数据格式不正确')
      countryData.value = []
    } else {
      // API已经在内部处理了错误，这里不需要再显示消息
      countryData.value = []
    }
  } catch (error) {
    console.error('获取国家数据出错', error)
    ElMessage.error('获取国家数据出错，将显示空列表')
    countryData.value = []
  }
}

// 加载设备数据
const loadDeviceData = async (date?: string) => {
  try {
    const response = await getDeviceData(date, loadingDevice)
    if (response && response.status === 'success') {
      deviceData.value = response.data.items || []
      renderDeviceChart()
    } else if (response) {
      ElMessage.warning(response.message || '获取设备数据格式不正确')
      deviceData.value = []
    } else {
      // API已经在内部处理了错误，这里不需要再显示消息
      deviceData.value = []
    }
  } catch (error) {
    console.error('获取设备数据出错', error)
    ElMessage.error('获取设备数据出错，将显示空列表')
    deviceData.value = []
  }
}

// 加载时间线数据
const loadTimelineData = async () => {
  try {
    // 获取日期范围
    const start = formatDate(dateRange.value[0])
    const end = formatDate(dateRange.value[1])
    
    // 使用日期范围参数加载数据
    const dateRangeParam = `${start}|${end}`
    
    const response = await getTimeline(30, dateRangeParam, loadingTimeline)
    if (response && response.status === 'success') {
      timelineData.value = response.data.items || []
      renderTimelineChart()
    } else if (response) {
      ElMessage.warning(response.message || '获取时间线数据格式不正确')
      timelineData.value = []
    } else {
      // API已经在内部处理了错误，这里不需要再显示消息
      timelineData.value = []
    }
  } catch (error) {
    console.error('获取时间线数据出错', error)
    ElMessage.error('获取时间线数据出错，将显示空列表')
    timelineData.value = []
  }
}

// 加载详情数据
const loadDetailsData = async (date: string) => {
  try {
    const response = await getDetailsData(date, loadingDetails)
    if (response && response.status === 'success') {
      detailsData.value = response.data
    } else if (response) {
      ElMessage.warning(response.message || '获取详情数据格式不正确')
      detailsData.value = createEmptyDetailsData(date)
    } else {
      // API已经在内部处理了错误，这里不需要再显示消息
      detailsData.value = createEmptyDetailsData(date)
    }
  } catch (error) {
    console.error('获取详情数据出错', error)
    ElMessage.error('获取详情数据出错，将显示默认值')
    detailsData.value = createEmptyDetailsData(date)
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

// 加载日期范围的详细数据
const loadDetailsDataForRange = async (startDate: string, endDate: string) => {
  try {
    // 先加载日期范围的最后一天数据作为主要详情数据
    const response = await getDetailsData(endDate, loadingDetails)
    
    if (response && response.status === 'success') {
      detailsData.value = response.data
      
      // 修改数据的标题，指明这是日期范围的数据
      if (startDate !== endDate) {
        detailsData.value.date = `${startDate} 至 ${endDate}`;
      }
      
    } else if (response) {
      ElMessage.warning(response.message || '获取详情数据格式不正确')
      detailsData.value = createEmptyDetailsData(`${startDate} 至 ${endDate}`)
    } else {
      detailsData.value = createEmptyDetailsData(`${startDate} 至 ${endDate}`)
    }
  } catch (error) {
    console.error('获取详情数据出错', error)
    ElMessage.error('获取详情数据出错，将显示默认值')
    detailsData.value = createEmptyDetailsData(`${startDate} 至 ${endDate}`)
  }
}

// 渲染国家维度饼图
const renderCountryChart = async () => {
  // 确保DOM元素已加载
  await nextTick()
  
  if (!countryChartRef.value) {
    console.warn('Country chart DOM element not found')
    return
  }
  
  if (!countryChart) {
    countryChart = echarts.init(countryChartRef.value)
  }

  // 提取前10个国家数据，其余归为"其他"类别
  const topData = countryData.value.slice(0, 8)
  let otherUsers = 0
  let otherRevenue = 0
  
  if (countryData.value.length > 8) {
    countryData.value.slice(8).forEach(item => {
      otherUsers += item.users
      otherRevenue += item.revenue
    })
    
    // 添加"其他"类别
    if (otherUsers > 0) {
      topData.push({
        country: '其他',
        users: otherUsers,
        revenue: otherRevenue
      })
    }
  }

  // 准备饼图数据
  const data = topData.map(item => ({
    name: item.country,
    value: item.users,
    revenue: item.revenue
  }))
  
  const option = {
    title: {
      text: '国家用户占比',
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const item = params.data
        return `${params.name}<br/>
                用户数: ${formatNumber(item.value)} (${params.percent}%)<br/>
                收入: ${formatCurrency(item.revenue)}`
      }
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 10,
      top: 'center',
      pageIconSize: 12,
      pageTextStyle: {
        color: '#888'
      }
    },
    series: [
      {
        name: '国家分布',
        type: 'pie',
        radius: ['40%', '70%'], // 使用环形饼图
        center: ['40%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center',
          formatter: '{b}: {d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        labelLine: {
          show: false
        },
        data: data.length > 0 ? data : [{ name: '无数据', value: 1 }]
      }
    ]
  }
  
  countryChart.setOption(option)
  
  // 添加点击事件
  countryChart.off('click')
  countryChart.on('click', (params: any) => {
    if (params.name !== '无数据' && params.name !== '其他') {
      ElMessage.info(`点击了 ${params.name}，可以在此添加详细数据查看功能`)
    }
  })
}

// 渲染设备维度饼图
const renderDeviceChart = async () => {
  // 确保DOM元素已加载
  await nextTick()
  
  if (!deviceChartRef.value) {
    console.warn('Device chart DOM element not found')
    return
  }
  
  if (!deviceChart) {
    deviceChart = echarts.init(deviceChartRef.value)
  }

  // 对设备数据进行处理，确保不会显示太多类别
  const topData = deviceData.value.slice(0, 6)
  let otherUsers = 0
  let otherRevenue = 0
  
  if (deviceData.value.length > 6) {
    deviceData.value.slice(6).forEach(item => {
      otherUsers += item.users
      otherRevenue += item.revenue
    })
    
    // 添加"其他"类别
    if (otherUsers > 0) {
      topData.push({
        device: '其他',
        users: otherUsers,
        revenue: otherRevenue
      })
    }
  }

  // 准备饼图数据，使用不同的颜色方案
  const data = topData.map(item => ({
    name: item.device,
    value: item.users,
    revenue: item.revenue
  }))
  
  // 设置颜色方案，区别于国家图表
  const colorPalette = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452']
  
  const option = {
    title: {
      text: '设备用户占比',
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const item = params.data
        return `${params.name}<br/>
                用户数: ${formatNumber(item.value)} (${params.percent}%)<br/>
                收入: ${formatCurrency(item.revenue)}`
      }
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 10,
      top: 'center',
      pageIconSize: 12,
      pageTextStyle: {
        color: '#888'
      }
    },
    color: colorPalette,
    series: [
      {
        name: '设备分布',
        type: 'pie',
        radius: '60%',
        center: ['40%', '50%'],
        roseType: 'radius', // 使用南丁格尔玫瑰图展示不同
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          formatter: '{b}: {d}%',
          show: deviceData.value.length <= 6 // 只在数据较少时显示标签
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        data: data.length > 0 ? data : [{ name: '无数据', value: 1 }]
      }
    ]
  }
  
  deviceChart.setOption(option)
  
  // 添加点击事件
  deviceChart.off('click')
  deviceChart.on('click', (params: any) => {
    if (params.name !== '无数据' && params.name !== '其他') {
      ElMessage.info(`点击了设备: ${params.name}，用户数: ${formatNumber(params.data.value)}`)
    }
  })
}

// 渲染时间线图表
const renderTimelineChart = async () => {
  // 确保DOM元素已加载
  await nextTick()
  
  if (!timelineChartRef.value) {
    console.warn('Timeline chart DOM element not found')
    return
  }
  
  if (!timelineChart) {
    timelineChart = echarts.init(timelineChartRef.value)
  }

  // 创建一个完整的日期范围数组，包含所有日期
  const startDate = new Date(dateRange.value[0])
  const endDate = new Date(dateRange.value[1])
  const dateArray = []
  const currentDate = new Date(startDate)
  
  // 为日期范围内的每一天创建一个日期
  while (currentDate <= endDate) {
    dateArray.push(formatDate(new Date(currentDate)))
    currentDate.setDate(currentDate.getDate() + 1)
  }
  
  // 创建一个Map来存储已有的数据
  const dataMap = new Map()
  timelineData.value.forEach(item => {
    dataMap.set(item.date, item)
  })
  
  // 填充所有日期的数据点，对于没有数据的日期使用0
  const filledData = dateArray.map(date => {
    return dataMap.get(date) || {
      date,
      user_count: 0,
      event_count: 0,
      revenue: 0,
      device_count: 0
    }
  })
  
  // 反转数据顺序使其按时间正序排列
  const sortedData = [...filledData].sort((a, b) => 
    new Date(a.date).getTime() - new Date(b.date).getTime()
  )
  
  // 提取数据
  const dates = sortedData.map(item => item.date)
  const users = sortedData.map(item => item.user_count)
  const revenues = sortedData.map(item => item.revenue)
  
  // 计算用户增长率数据
  const userGrowth = []
  for (let i = 1; i < users.length; i++) {
    if (users[i-1] === 0) {
      userGrowth.push(0)
    } else {
      const growthRate = ((users[i] - users[i-1]) / users[i-1] * 100).toFixed(2)
      userGrowth.push(parseFloat(growthRate))
    }
  }
  
  // 第一天无增长率数据
  userGrowth.unshift(0)
  
  const option = {
    title: {
      text: '用户和收入时间趋势',
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      },
      formatter: function(params: any[]) {
        let result = `<div style="font-weight:bold;margin-bottom:5px;">${params[0].axisValue}</div>`
        
        params.forEach(param => {
          let value = param.value
          let unit = ''
          let color = param.color
          
          // 根据不同的数据类型设置不同的格式
          if (param.seriesName === '收入') {
            value = formatCurrency(value)
          } else if (param.seriesName === '用户数') {
            value = formatNumber(value)
            unit = '人'
          } else if (param.seriesName === '用户增长率') {
            value = `${value}%`
          }
          
          result += `<div style="display:flex;justify-content:space-between;align-items:center;margin:3px 0">
                     <span style="display:inline-block;margin-right:5px;
                     border-radius:50%;width:10px;height:10px;background-color:${color};"></span>
                     <span style="flex-grow:1">${param.seriesName}:</span>
                     <span style="font-weight:bold">${value}${unit}</span>
                    </div>`
        })
        
        return result
      }
    },
    legend: {
      data: ['用户数', '收入', '用户增长率'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    toolbox: {
      feature: {
        saveAsImage: { title: '保存为图片' },
        restore: { title: '还原' }
      },
      right: 25,
      bottom: 12
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
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: dates.length > 0 ? dates : ['无数据'],
        axisLabel: {
          rotate: dates.length > 15 ? 45 : 0 // 日期多时倾斜显示
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '用户数',
        position: 'left',
        axisLine: {
          show: true,
          lineStyle: {
            color: '#409EFF'
          }
        },
        axisLabel: {
          formatter: '{value}'
        },
        splitLine: {
          show: true,
          lineStyle: {
            type: 'dashed'
          }
        }
      },
      {
        type: 'value',
        name: '收入($)',
        position: 'right',
        axisLine: {
          show: true,
          lineStyle: {
            color: '#303133'
          }
        },
        axisLabel: {
          formatter: '${value}'
        },
        splitLine: {
          show: false
        }
      },
      {
        type: 'value',
        name: '增长率(%)',
        position: 'right',
        offset: 80,
        axisLine: {
          show: true,
          lineStyle: {
            color: '#67C23A'
          }
        },
        axisLabel: {
          formatter: '{value}%'
        },
        splitLine: {
          show: false
        }
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
          width: 3,
          color: '#409EFF'
        },
        itemStyle: {
          color: '#409EFF'
        },
        symbol: 'circle',
        symbolSize: 6,
        markPoint: {
          data: [
            { type: 'max', name: '最大值' },
            { type: 'min', name: '最小值' }
          ]
        }
      },
      {
        name: '收入',
        type: 'line',
        data: revenues.length > 0 ? revenues : [0],
        yAxisIndex: 1,
        smooth: true,
        lineStyle: {
          width: 3,
          color: '#303133'
        },
        itemStyle: {
          color: '#303133'
        },
        symbol: 'circle',
        symbolSize: 6
      },
      {
        name: '用户增长率',
        type: 'bar',
        data: userGrowth,
        yAxisIndex: 2,
        barWidth: 10,
        itemStyle: {
          color: (params: any) => {
            // 正值为绿色，负值为红色
            return params.value >= 0 ? '#67C23A' : '#F56C6C';
          }
        }
      }
    ]
  }
  
  timelineChart.setOption(option)
  
  // 添加点击事件
  timelineChart.off('click')
  timelineChart.on('click', (params: any) => {
    // 点击日期条形图时，自动选择该日期
    if (params.componentType === 'xAxis') {
      const date = params.value
      if (date && date !== '无数据') {
        selectedDate.value = date
        // 设置日期范围，使用选中日期作为开始和结束
        const selectedDateObj = new Date(date)
        
        // 更新日期范围
        dateRange.value = [selectedDateObj, selectedDateObj]
        
        // 加载选定日期的数据
        const formattedDate = formatDate(selectedDateObj)
        
        // 显示加载中提示
        const loading = ElMessage.info({
          message: '加载数据中...',
          duration: 0
        })
        
        // 并行加载数据
        Promise.all([
          loadCountryData(formattedDate),
          loadDeviceData(formattedDate),
          loadTimelineData(),
          loadDetailsDataForRange(formattedDate, formattedDate)
        ]).then(() => {
          loading.close()
          ElMessage.success(`已切换到 ${formattedDate} 数据`)
        }).catch(() => {
          loading.close()
          ElMessage.error('数据加载失败')
        })
        
        ElMessage.info(`已选择日期: ${date}`)
      }
    }
  })
}

// 日期范围变化处理
const handleDateRangeChange = async (range: [Date, Date]) => {
  if (!range || range.length !== 2) return
  
  dateRange.value = range
  
  // 根据选定的日期范围重新加载数据
  const startDate = formatDate(range[0])
  const endDate = formatDate(range[1])
  selectedDate.value = endDate
  
  // 显示加载中提示
  const loading = ElMessage.info({
    message: '加载数据中...',
    duration: 0
  })
  
  try {
    // 并行加载数据以提高效率
    await Promise.all([
      loadTimelineData(),
      loadDetailsDataForRange(startDate, endDate), // 使用日期范围加载详细数据
      loadCountryDataForRange(startDate, endDate),
      loadDeviceDataForRange(startDate, endDate)
    ])
    
    // 关闭加载提示
    loading.close()
    
    // 更新成功提示
    ElMessage.success({
      message: `数据已更新，日期范围: ${formatDate(range[0])} 至 ${formatDate(range[1])}`,
      duration: 1500
    })
  } catch (error) {
    // 关闭加载提示
    loading.close()
    
    // 显示错误提示
    ElMessage.error({
      message: '数据加载失败，请重试',
      duration: 2000
    })
    console.error('加载数据失败', error)
  }
}

// 加载日期范围内的国家数据
const loadCountryDataForRange = async (startDate: string, endDate: string) => {
  try {
    // 使用日期范围参数加载数据
    const response = await getCountryData(`${startDate}|${endDate}`, loadingCountry)
    if (response && response.status === 'success') {
      countryData.value = response.data.items || []
      renderCountryChart()
    } else if (response) {
      ElMessage.warning(response.message || '获取国家数据格式不正确')
      countryData.value = []
    } else {
      countryData.value = []
    }
  } catch (error) {
    console.error('获取国家数据出错', error)
    ElMessage.error('获取国家数据出错，将显示空列表')
    countryData.value = []
  }
}

// 加载日期范围内的设备数据
const loadDeviceDataForRange = async (startDate: string, endDate: string) => {
  try {
    // 使用日期范围参数加载数据
    const response = await getDeviceData(`${startDate}|${endDate}`, loadingDevice)
    if (response && response.status === 'success') {
      deviceData.value = response.data.items || []
      renderDeviceChart()
    } else if (response) {
      ElMessage.warning(response.message || '获取设备数据格式不正确')
      deviceData.value = []
    } else {
      deviceData.value = []
    }
  } catch (error) {
    console.error('获取设备数据出错', error)
    ElMessage.error('获取设备数据出错，将显示空列表')
    deviceData.value = []
  }
}

// 加载所有数据
const loadAllData = () => {
  const start = formatDate(dateRange.value[0])
  const end = formatDate(dateRange.value[1])
  loadCountryDataForRange(start, end)
  loadDeviceDataForRange(start, end)
  loadTimelineData()
  loadDetailsDataForRange(start, end) // 使用日期范围加载详细数据
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
  return formatDate(today)
})

// 监听窗口大小变化，重新调整图表大小
const handleResize = () => {
  if (countryChart) countryChart.resize()
  if (deviceChart) deviceChart.resize()
  if (timelineChart) timelineChart.resize()
}

// 初始加载
onMounted(() => {
  loadAllData()
  window.addEventListener('resize', handleResize)
})

// 观察数据变化，重新渲染图表
watch(() => countryData.value, () => {
  nextTick(() => renderCountryChart())
}, { deep: true })

watch(() => deviceData.value, () => {
  nextTick(() => renderDeviceChart())
}, { deep: true })

watch(() => timelineData.value, () => {
  nextTick(() => renderTimelineChart())
}, { deep: true })

// 组件卸载时清理资源
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  
  if (countryChart) {
    countryChart.dispose()
    countryChart = null
  }
  
  if (deviceChart) {
    deviceChart.dispose()
    deviceChart = null
  }
  
  if (timelineChart) {
    timelineChart.dispose()
    timelineChart = null
  }
})
</script>

<template>
  <AppLayout>
    <div class="details-view">
      <!-- 页面顶部操作栏 -->
      <div class="actions-bar">
        <h1>数据详情分析</h1>
      </div>
      
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
              :shortcuts="dateRangeShortcuts"
              unlink-panels
              @change="handleDateRangeChange"
              class="date-picker-shorter"
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
                :default-sort="{ prop: 'revenue', order: 'descending' }"
              >
                <el-table-column prop="country" label="国家" width="120" sortable />
                <el-table-column prop="users" label="用户数" width="120" sortable>
                  <template #default="scope">
                    {{ formatNumber(scope.row.users) }}
                  </template>
                </el-table-column>
                <el-table-column prop="revenue" label="收入" sortable>
                  <template #default="scope">
                    {{ formatCurrency(scope.row.revenue) }}
                  </template>
                </el-table-column>
              </el-table>
              
              <!-- 骨架屏 -->
              <template v-if="loadingCountry && countryData.length === 0">
                <div class="skeleton-container">
                  <el-skeleton :rows="5" animated />
                </div>
              </template>
            </div>
            <div class="data-chart" ref="countryChartRef">
              <!-- 图表骨架屏 -->
              <template v-if="loadingCountry && !countryChart">
                <div class="chart-skeleton">
                  <el-skeleton :rows="8" animated />
                </div>
              </template>
            </div>
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
              :shortcuts="dateRangeShortcuts"
              unlink-panels
              @change="handleDateRangeChange"
              class="date-picker-shorter"
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
                :default-sort="{ prop: 'revenue', order: 'descending' }"
              >
                <el-table-column prop="device" label="设备" width="120" sortable />
                <el-table-column prop="users" label="用户数" width="120" sortable>
                  <template #default="scope">
                    {{ formatNumber(scope.row.users) }}
                  </template>
                </el-table-column>
                <el-table-column prop="revenue" label="收入" sortable>
                  <template #default="scope">
                    {{ formatCurrency(scope.row.revenue) }}
                  </template>
                </el-table-column>
              </el-table>
              
              <!-- 骨架屏 -->
              <template v-if="loadingDevice && deviceData.length === 0">
                <div class="skeleton-container">
                  <el-skeleton :rows="5" animated />
                </div>
              </template>
            </div>
            <div class="data-chart" ref="deviceChartRef">
              <!-- 图表骨架屏 -->
              <template v-if="loadingDevice && !deviceChart">
                <div class="chart-skeleton">
                  <el-skeleton :rows="8" animated />
                </div>
              </template>
            </div>
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
            :shortcuts="dateRangeShortcuts"
            unlink-panels
            @change="handleDateRangeChange"
            class="date-picker-shorter"
          />
        </div>
        
        <div class="timeline-chart" ref="timelineChartRef" v-loading="loadingTimeline"></div>
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
            :shortcuts="dateRangeShortcuts"
            unlink-panels
            @change="handleDateRangeChange"
            class="date-picker-shorter"
          />
        </div>
        
        <el-table
          :data="timelineData.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())"
          stripe
          border
          v-loading="loadingTimeline"
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
.details-view {
  width: 100%;
}

/* 日期选择器样式 */
.date-picker-shorter {
  width: 260px !important;
}

/* 全局样式覆盖，使用:deep来影响组件内部样式 */
:deep(.date-picker-shorter .el-input__wrapper),
:deep(.date-picker-shorter.el-date-editor--daterange),
:deep(.date-picker-shorter .el-range-editor),
:deep(.date-picker-shorter.el-range-editor) {
  width: 260px !important;
  max-width: 260px !important;
}

.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e6e6e6;
}

.actions-bar h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
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
  margin-bottom: 15px;
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
  position: relative;
}

.data-chart {
  height: 300px;
  width: 100%;
  margin-top: 20px;
  position: relative;
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
  margin-top: 20px;
  position: relative;
}

.details-section {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 30px;
}

.details-section .data-table {
  width: 100%;
  margin-top: 15px;
}

.details-date {
  display: flex;
  align-items: center;
}

.date-label {
  margin-right: 5px;
  font-weight: 500;
}

.date-value {
  font-weight: bold;
}

.details-tables {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 20px;
}

.details-countries,
.details-devices {
  flex: 1;
  min-width: 280px;
}

.details-tables h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 500;
}

/* 骨架屏样式 */
.skeleton-container {
  padding: 15px;
  border-radius: 4px;
  background-color: #fafafa;
  margin-top: 10px;
}

.chart-skeleton {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.8);
}

/* 表格加载效果 */
:deep(.el-loading-mask) {
  background-color: rgba(255, 255, 255, 0.7);
}

:deep(.el-loading-spinner .path) {
  stroke: #409eff;
}

@media (max-width: 1200px) {
  .country-section,
  .device-section {
    min-width: 100%;
  }
}
</style> 