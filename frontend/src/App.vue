<template>
  <div class="app-wrapper">
    <header class="app-header">
      <h1>爆发的灵感</h1>
      <p class="subtitle">记录书中智慧，标注个人思考</p>
    </header>
    <main class="app-main">
      <el-tabs v-model="activeTab" class="main-tabs">
        <el-tab-pane label="书架" name="bookshelf">
          <BookList ref="bookListRef" />
        </el-tab-pane>
        <el-tab-pane label="检索" name="search">
          <SearchView ref="searchViewRef" />
        </el-tab-pane>
      </el-tabs>
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import BookList from './components/BookList.vue'
import SearchView from './components/SearchView.vue'

const activeTab = ref('bookshelf')
const bookListRef = ref(null)
const searchViewRef = ref(null)

watch(activeTab, (tab) => {
  if (tab === 'bookshelf' && bookListRef.value) {
    bookListRef.value.refresh()
  } else if (tab === 'search' && searchViewRef.value) {
    searchViewRef.value.refresh()
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: #f5f0eb;
  font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.app-wrapper {
  min-height: 100vh;
}

.app-header {
  text-align: center;
  padding: 24px 0 8px;
  background: linear-gradient(135deg, #5c4a32 0%, #7a6348 100%);
  color: #fff;
}

.app-header h1 {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 4px;
}

.app-header .subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 4px;
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 20px 40px;
}

.main-tabs > .el-tabs__header {
  margin-bottom: 16px;
}

.main-tabs .el-tabs__item {
  font-size: 15px;
  font-weight: 500;
  color: #5c4a32;
}

.main-tabs .el-tabs__active-bar {
  background-color: #5c4a32;
}

.main-tabs .el-tabs__item.is-active {
  color: #5c4a32;
}
</style>
