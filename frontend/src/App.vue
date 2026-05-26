<template>
  <div class="app-wrapper">
    <header class="app-header">
      <h1>爆发的灵感</h1>
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
  background-color: #f8f7f4;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Noto Serif SC', 'Source Han Serif CN', serif;
  color: #1c1c1c;
  -webkit-font-smoothing: antialiased;
}

.app-wrapper {
  min-height: 100vh;
}

.app-header {
  text-align: center;
  padding: 40px 0 28px;
  background: #fff;
  border-bottom: 1px solid #edeae5;
}

.app-header h1 {
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 6px;
  color: #1c1c1c;
}

.app-header .subtitle {
  font-size: 13px;
  color: #a8a29e;
  margin-top: 6px;
  letter-spacing: 2px;
}

.app-main {
  max-width: 1120px;
  margin: 0 auto;
  padding: 28px 24px 60px;
}

.main-tabs > .el-tabs__header {
  margin-bottom: 24px;
}

.main-tabs .el-tabs__nav-wrap::after {
  background-color: transparent;
}

.main-tabs .el-tabs__item {
  font-size: 15px;
  font-weight: 500;
  color: #a8a29e;
  padding: 0 24px;
  transition: color 0.2s;
}

.main-tabs .el-tabs__item:hover {
  color: #57534e;
}

.main-tabs .el-tabs__active-bar {
  background-color: #1c1c1c;
  height: 2px;
}

.main-tabs .el-tabs__item.is-active {
  color: #1c1c1c;
  font-weight: 600;
}
</style>
