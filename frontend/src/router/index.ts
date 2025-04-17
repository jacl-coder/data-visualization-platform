import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: {
        title: '数据概览'
      }
    },
    {
      path: '/details',
      name: 'details',
      component: () => import('../views/DetailsView.vue'),
      meta: {
        title: '详情数据'
      }
    },
    // 重定向未匹配的路由到首页
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ],
})

// 设置页面标题
router.beforeEach((to, from, next) => {
  const title = to.meta.title ? `${to.meta.title} - 数据分析与可视化平台` : '数据分析与可视化平台'
  document.title = title as string
  next()
})

export default router
