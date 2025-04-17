<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="app">
    <RouterView />
  </div>
</template>

<style>
.app {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-width: 100vw;
  min-height: 100vh;
}
</style>
