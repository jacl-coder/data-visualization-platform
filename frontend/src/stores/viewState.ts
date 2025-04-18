import { defineStore } from 'pinia'
import { ref } from 'vue'

interface HomeViewState {
  days: number;
  date: string;
}

interface DetailsViewState {
  dateRange: string[];
}

/**
 * 视图状态存储 - 用于保存视图之间的状态
 * 注意：这个存储会自动持久化，通过 pinia-plugin-persistedstate 插件
 */
export const useViewStateStore = defineStore('viewState', () => {
  // HomeView 状态
  const homeViewState = ref<HomeViewState>({
    days: 30, // 默认显示30天
    date: new Date().toISOString().slice(0, 10) // 今天的日期，格式为YYYY-MM-DD
  })

  // DetailsView 状态
  const detailsViewState = ref<DetailsViewState>({
    dateRange: [
      new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10), // 30天前
      new Date().toISOString().slice(0, 10) // 今天
    ]
  })

  // 更新 HomeView 状态
  const updateHomeViewState = (state: Partial<HomeViewState>) => {
    homeViewState.value = { ...homeViewState.value, ...state }
  }

  // 更新 DetailsView 状态
  const updateDetailsViewState = (state: Partial<DetailsViewState>) => {
    detailsViewState.value = { ...detailsViewState.value, ...state }
  }

  return {
    homeViewState,
    detailsViewState,
    updateHomeViewState,
    updateDetailsViewState
  }
}) 