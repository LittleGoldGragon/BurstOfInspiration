<template>
  <div class="search-view">
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索摘抄原文或个人想法..."
        size="large"
        clearable
        @keyup.enter="doSearch"
      >
        <template #append>
          <el-button :icon="Search" @click="doSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <div class="tag-filter" v-if="allTags.length">
      <span class="filter-label">标签</span>
      <el-checkbox-group v-model="selectedTagIds" @change="doSearch" class="filter-group">
        <el-checkbox v-for="tag in allTags" :key="tag.id" :value="tag.id" class="tag-checkbox">
          <span class="filter-tag-pill" :style="{ background: tag.color }">{{ tag.name }}</span>
        </el-checkbox>
      </el-checkbox-group>
    </div>

    <div class="results-header" v-if="searched">
      <span class="results-count">共 <strong>{{ total }}</strong> 条结果</span>
    </div>

    <div class="results-list">
      <div v-for="excerpt in items" :key="excerpt.id" class="result-card">
        <div class="card-book-row">
          <el-icon :size="15" class="book-icon"><Notebook /></el-icon>
          <span class="book-name">{{ excerpt.book?.title || '未知书籍' }}</span>
          <span class="book-author" v-if="excerpt.book?.author">{{ excerpt.book.author }}</span>
        </div>

        <div class="card-body">
          <div class="card-col content-col">
            <div class="col-label">摘抄原文</div>
            <div class="col-text">{{ excerpt.content || '（无内容）' }}</div>
          </div>
          <div class="card-col insights-col">
            <div class="col-label">个人想法</div>
            <div class="col-text">{{ excerpt.insights || '（无想法）' }}</div>
          </div>
          <div class="card-col tags-col">
            <div class="col-label">标签</div>
            <div class="tags-wrap">
              <span
                v-for="tag in excerpt.tags"
                :key="tag.id"
                class="tag-pill"
                :style="{ background: tag.color }"
              >{{ tag.name }}</span>
              <span v-if="!excerpt.tags?.length" class="no-tags">&mdash;</span>
            </div>
          </div>
        </div>

        <div class="card-meta" v-if="excerpt.links?.length || excerpt.images?.length">
          <div v-if="excerpt.links?.length" class="card-links">
            <el-icon :size="13"><Link /></el-icon>
            <a
              v-for="(link, i) in excerpt.links"
              :key="i"
              :href="link"
              target="_blank"
              class="card-link"
            >{{ link }}</a>
          </div>
          <div v-if="excerpt.images?.length" class="card-images">
            <el-image
              v-for="(img, i) in excerpt.images"
              :key="i"
              :src="img"
              :preview-src-list="excerpt.images"
              fit="cover"
              class="card-thumb"
            />
          </div>
        </div>

        <div class="card-footer">
          <span class="card-time">
            {{ excerpt.updated_at?.slice(0, 16) || excerpt.created_at?.slice(0, 16) }}
          </span>
        </div>
      </div>

      <div v-if="searched && items.length === 0" class="empty-result">
        <p class="empty-result-text">未找到匹配的摘抄</p>
      </div>
    </div>

    <div class="pagination-wrap" v-if="total > page_size">
      <el-pagination
        v-model:current-page="page"
        :page-size="page_size"
        :total="total"
        layout="prev, pager, next"
        @current-change="doSearch"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, Notebook, Link } from '@element-plus/icons-vue'
import { getExcerpts, getTags } from '../api'

const keyword = ref('')
const selectedTagIds = ref([])
const allTags = ref([])
const items = ref([])
const total = ref(0)
const page = ref(1)
const page_size = ref(10)
const searched = ref(false)

async function loadTags() {
  const res = await getTags()
  allTags.value = res.data
}

async function doSearch() {
  const params = {
    page: page.value,
    page_size: page_size.value,
  }
  if (keyword.value.trim()) {
    params.keyword = keyword.value.trim()
  }
  if (selectedTagIds.value.length) {
    params.tag_ids = selectedTagIds.value.join(',')
  }
  const res = await getExcerpts(params)
  items.value = res.data.items
  total.value = res.data.total
  searched.value = true
}

function refresh() {
  loadTags()
  doSearch()
}

onMounted(() => { loadTags() })

defineExpose({ refresh })
</script>

<style scoped>
.search-view {
  padding: 0;
}

/* ─── Search Bar ─── */
.search-bar {
  margin-bottom: 20px;
}

.search-bar :deep(.el-input__wrapper) {
  border-radius: 6px 0 0 6px;
  box-shadow: none;
  border: 1px solid #d6d3d1;
}

.search-bar :deep(.el-input__wrapper:hover) {
  border-color: #a8a29e;
}

.search-bar :deep(.el-input__wrapper.is-focus) {
  border-color: #1c1c1c;
  box-shadow: 0 0 0 1px rgba(28, 28, 28, 0.1);
}

.search-bar :deep(.el-input-group__append) {
  background: #1c1c1c;
  border-color: #1c1c1c;
  border-radius: 0 6px 6px 0;
}

.search-bar :deep(.el-input-group__append .el-button) {
  color: #fff;
}

/* ─── Tag Filter ─── */
.tag-filter {
  margin-bottom: 20px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.filter-label {
  font-size: 13px;
  color: #a8a29e;
  padding-top: 6px;
  flex-shrink: 0;
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-checkbox {
  margin-right: 0 !important;
}

.tag-checkbox :deep(.el-checkbox__input) {
  display: none;
}

.tag-checkbox :deep(.el-checkbox__label) {
  padding: 0;
}

.filter-tag-pill {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  color: #fff;
  cursor: pointer;
  opacity: 0.55;
  transition: opacity 0.15s;
}

.tag-checkbox.is-checked .filter-tag-pill {
  opacity: 1;
}

/* ─── Results ─── */
.results-header {
  margin-bottom: 14px;
}

.results-count {
  font-size: 13px;
  color: #a8a29e;
}

.results-count strong {
  color: #1c1c1c;
  font-weight: 600;
}

.result-card {
  background: #fff;
  border: 1px solid #edeae5;
  border-radius: 6px;
  padding: 16px 18px;
  margin-bottom: 8px;
  transition: border-color 0.15s;
}

.result-card:hover {
  border-color: #d6d3d1;
}

.card-book-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #1c1c1c;
}

.book-icon {
  color: #a8a29e;
}

.book-author {
  font-weight: 400;
  font-size: 13px;
  color: #a8a29e;
}

.card-body {
  display: flex;
  gap: 20px;
  margin-bottom: 6px;
}

.card-col {
  flex: 1;
  min-width: 0;
}

.content-col {
  border-left: 2px solid #d4a574;
  padding-left: 12px;
}

.insights-col {
  border-left: 2px solid #94a3b8;
  padding-left: 12px;
}

.col-label {
  font-size: 11px;
  color: #a8a29e;
  margin-bottom: 4px;
  letter-spacing: 1px;
}

.col-text {
  font-size: 13px;
  color: #44403c;
  line-height: 1.75;
  white-space: pre-wrap;
  word-break: break-all;
}

.tags-col {
  max-width: 140px;
  min-width: 80px;
}

.tags-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag-pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
  color: #fff;
  line-height: 1.6;
}

.no-tags {
  color: #d6d3d1;
  font-size: 13px;
}

.card-meta {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.card-links {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #78716c;
}

.card-link {
  color: #57534e;
  text-decoration: none;
  word-break: break-all;
}

.card-link:hover {
  color: #1c1c1c;
}

.card-images {
  display: flex;
  gap: 6px;
}

.card-thumb {
  width: 52px;
  height: 52px;
  border-radius: 4px;
  border: 1px solid #edeae5;
}

.card-footer {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f5f3f0;
}

.card-time {
  font-size: 12px;
  color: #d6d3d1;
}

.empty-result {
  text-align: center;
  padding: 60px 0;
}

.empty-result-text {
  font-size: 14px;
  color: #a8a29e;
}

.pagination-wrap {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
</style>
