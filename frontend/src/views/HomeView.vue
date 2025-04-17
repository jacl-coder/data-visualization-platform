<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElDatePicker } from 'element-plus'
import AppLayout from '../components/AppLayout.vue'
import { getOverview, getTimeline } from '../api'
import type { OverviewData, TimelineItem } from '../api'

// 日期选择
const selectedDate = ref(new Date())

// 概览数据
const overviewData = reactive<OverviewData>({
  user_count: 0,
  event_count: 0,
  device_count: 0,
  total_revenue: 0
})

// 指标趋势数据（实际应用中应从API获取）
const trends = reactive({
  user_count: { 
    day_on_day: 0, // 日环比
    week_on_week: 0 // 周环比
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

// 时间线数据
const timelineData = ref<TimelineItem[]>([])
const loading = ref(false)
const loadingOverview = ref(false)
const days = ref(30)

// 格式化日期为YYYY-MM-DD
const formatDate = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 加载概览数据，根据选定日期
const loadOverviewData = async (date: string = formatDate(selectedDate.value)) => {
  loadingOverview.value = true
  try {
    const response = await getOverview()
    if (response && response.status === 'success') {
      Object.assign(overviewData, response.data)
      
      // 临时: 随机生成-5%到+5%之间的趋势数据
      // 实际项目中这些数据应该从API获取
      Object.keys(trends).forEach(key => {
        trends[key as keyof typeof trends].day_on_day = parseFloat((Math.random() * 10 - 5).toFixed(1))
        trends[key as keyof typeof trends].week_on_week = parseFloat((Math.random() * 10 - 5).toFixed(1))
      })
    } else if (response) {
      ElMessage.warning(response.message || '获取概览数据格式不正确')
    } else {
      // API已经在内部处理了错误，这里不需要再显示消息
    }
  } catch (error) {
    console.error('获取概览数据出错', error)
    ElMessage.error('获取概览数据出错，将显示默认值')
    // 使用默认数据
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
  
  // 重新加载该日期的数据
  loadOverviewData(formattedDate)
  // 如果需要根据选择的日期重新加载时间线数据，也可以在这里触发
}

// 初始加载数据
onMounted(() => {
  loadOverviewData()
  loadTimelineData()
})
</script>

<template>
  <AppLayout>
    <div class="home-view">
      <!-- 日期选择器 -->
      <div class="date-picker-container">
        <span class="date-label">日期：</span>
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          @change="handleDateChange"
        />
      </div>
      
      <!-- 指标卡片 -->
      <div class="metric-cards">
        <el-card class="metric-card" v-loading="loadingOverview">
          <div class="metric-title">用户数</div>
          <div class="metric-date">{{ formatDate(selectedDate) }}</div>
          <div class="metric-value">{{ formatNumber(overviewData.user_count) }}</div>
          <div class="metric-trend">
            <span class="trend-label">较同比</span>
            <span class="trend-value" :class="trends.user_count.day_on_day >= 0 ? 'up' : 'down'">
              {{ formatPercentage(trends.user_count.day_on_day) }}
            </span>
            <span class="trend-label">较环比</span>
            <span class="trend-value" :class="trends.user_count.week_on_week >= 0 ? 'up' : 'down'">
              {{ formatPercentage(trends.user_count.week_on_week) }}
            </span>
          </div>
        </el-card>
        
        <el-card class="metric-card" v-loading="loadingOverview">
          <div class="metric-title">事件数</div>
          <div class="metric-date">{{ formatDate(selectedDate) }}</div>
          <div class="metric-value">{{ formatNumber(overviewData.event_count) }}</div>
          <div class="metric-trend">
            <span class="trend-label">较同比</span>
            <span class="trend-value" :class="trends.event_count.day_on_day >= 0 ? 'up' : 'down'">
              {{ formatPercentage(trends.event_count.day_on_day) }}
            </span>
            <span class="trend-label">较环比</span>
            <span class="trend-value" :class="trends.event_count.week_on_week >= 0 ? 'up' : 'down'">
              {{ formatPercentage(trends.event_count.week_on_week) }}
            </span>
          </div>
        </el-card>
        
        <el-card class="metric-card" v-loading="loadingOverview">
          <div class="metric-title">设备数</div>
          <div class="metric-date">{{ formatDate(selectedDate) }}</div>
          <div class="metric-value">{{ formatNumber(overviewData.device_count) }}</div>
          <div class="metric-trend">
            <span class="trend-label">较同比</span>
            <span class="trend-value" :class="trends.device_count.day_on_day >= 0 ? 'up' : 'down'">
              {{ formatPercentage(trends.device_count.day_on_day) }}
            </span>
            <span class="trend-label">较环比</span>
            <span class="trend-value" :class="trends.device_count.week_on_week >= 0 ? 'up' : 'down'">
              {{ formatPercentage(trends.device_count.week_on_week) }}
            </span>
          </div>
        </el-card>
        
        <el-card class="metric-card" v-loading="loadingOverview">
          <div class="metric-title">总收入</div>
          <div class="metric-date">{{ formatDate(selectedDate) }}</div>
          <div class="metric-value">{{ formatCurrency(overviewData.total_revenue) }}</div>
          <div class="metric-trend">
            <span class="trend-label">较同比</span>
            <span class="trend-value" :class="trends.total_revenue.day_on_day >= 0 ? 'up' : 'down'">
              {{ formatPercentage(trends.total_revenue.day_on_day) }}
            </span>
            <span class="trend-label">较环比</span>
            <span class="trend-value" :class="trends.total_revenue.week_on_week >= 0 ? 'up' : 'down'">
              {{ formatPercentage(trends.total_revenue.week_on_week) }}
            </span>
          </div>
        </el-card>
      </div>
      
      <!-- 时间线数据表格 -->
      <div class="timeline-section">
        <div class="section-header">
          <h2>按日期的基本数据</h2>
          <el-select v-model="days" @change="loadTimelineData">
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
.home-view {
  width: 100%;
}

.date-picker-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.date-label {
  margin-right: 10px;
  font-weight: 500;
}

.metric-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  flex: 1;
  min-width: 230px;
  max-width: calc(25% - 15px);
}

.metric-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 5px;
}

.metric-date {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.metric-trend {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.trend-label {
  color: #909399;
  margin-right: 5px;
}

.trend-value {
  font-weight: 500;
  margin-right: 15px;
}

.trend-value.up {
  color: #f56c6c;
}

.trend-value.down {
  color: #67c23a;
}

.timeline-section {
  margin-top: 30px;
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

@media (max-width: 1200px) {
  .metric-card {
    max-width: calc(50% - 10px);
  }
}

@media (max-width: 768px) {
  .metric-card {
    max-width: 100%;
  }
}
</style> 