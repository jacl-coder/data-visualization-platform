<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 导航菜单项
const navItems = [
  { name: '数据概览', path: '/', icon: 'el-icon-data-analysis' },
  { name: '详情数据', path: '/details', icon: 'el-icon-document' }
]

// 当前菜单项
const currentPath = ref(route.path)

// 导航到页面
const navigateTo = (path: string) => {
  currentPath.value = path
  router.push(path)
}
</script>

<template>
  <el-container class="app-container">
    <el-header height="60px" class="app-header">
      <div class="logo">
        <h1>数据分析与可视化平台</h1>
      </div>
    </el-header>
    
    <el-container class="main-container">
      <el-aside width="200px" class="app-sidebar">
        <el-menu
          :default-active="currentPath"
          class="nav-menu"
          router
        >
          <el-menu-item 
            v-for="item in navItems" 
            :key="item.path" 
            :index="item.path"
            @click="navigateTo(item.path)"
          >
            <span>{{ item.name }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
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
}

.app-header {
  background-color: #409eff;
  color: white;
  padding: 0 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 2;
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.main-container {
  flex: 1;
  overflow: hidden;
}

.app-sidebar {
  background-color: #fff;
  border-right: 1px solid #e6e6e6;
  overflow-y: auto;
}

.nav-menu {
  border-right: none;
}

.app-main {
  padding: 20px;
  background-color: #f5f7fa;
  overflow-y: auto;
}
</style> 