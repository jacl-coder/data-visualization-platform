<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 导航菜单项
const navItems = [
  { name: '数据概览', path: '/', icon: 'DataAnalysis' },
  { name: '详情数据', path: '/details', icon: 'Document' }
]

// 是否折叠侧边栏
const isCollapsed = ref(false)

// 当前菜单项
const currentPath = computed(() => route.path)

// 导航到页面
const navigateTo = (path: string) => {
  router.push(path)
}

// 切换侧边栏
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<template>
  <el-container class="app-container">
    <!-- 顶部导航栏 -->
    <el-header height="60px" class="app-header">
      <div class="header-left">
        <div class="menu-toggle" @click="toggleSidebar">
          <el-icon><Fold v-if="isCollapsed" /><Expand v-else /></el-icon>
        </div>
        <div class="logo">
          <h1>数据分析平台</h1>
        </div>
      </div>
      
      <div class="header-right">
        <div class="user-info">
          <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
          <span>管理员</span>
        </div>
      </div>
    </el-header>
    
    <el-container class="main-container">
      <!-- 侧边导航 -->
      <el-aside :width="isCollapsed ? '64px' : '220px'" class="app-sidebar">
        <el-menu
          :default-active="currentPath"
          class="nav-menu"
          :collapse="isCollapsed"
          :collapse-transition="false"
          router
        >
          <el-menu-item 
            v-for="item in navItems" 
            :key="item.path" 
            :index="item.path"
            @click="navigateTo(item.path)"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ item.name }}</template>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main class="app-main">
        <slot></slot>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  min-width: 100%;
  max-width: 100vw;
  overflow-x: hidden;
}

.app-header {
  background-color: #ffffff;
  color: #333;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  z-index: 100;
  position: relative;
  width: 100%;
  flex-shrink: 0;
}

.header-left, .header-right {
  display: flex;
  align-items: center;
}

.menu-toggle {
  cursor: pointer;
  font-size: 20px;
  margin-right: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 4px;
  transition: all 0.3s;
}

.menu-toggle:hover {
  background-color: #f5f7fa;
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  background-image: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-info span {
  margin-left: 8px;
  font-size: 14px;
}

.main-container {
  flex: 1;
  overflow: hidden;
  width: 100%;
  display: flex;
}

.app-sidebar {
  background-color: #ffffff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
  transition: width 0.3s;
  z-index: 99;
  flex-shrink: 0;
}

.nav-menu {
  height: 100%;
  border-right: none;
}

.nav-menu:not(.el-menu--collapse) {
  width: 220px;
}

.app-main {
  padding: 20px;
  background-color: #f5f7fa;
  overflow-y: auto;
  flex: 1;
  width: calc(100% - 220px);
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 15px;
  }
  
  .logo h1 {
    font-size: 18px;
  }
  
  .user-info span {
    display: none;
  }
  
  .app-main {
    width: calc(100% - 64px);
  }
}
</style> 