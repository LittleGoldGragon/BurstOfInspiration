<template>
  <div class="search-view">
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="输入关键词搜索摘抄原文和个人想法..."
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
      <span class="filter-label">标签筛选：</span>
      <el-checkbox-group v-model="selectedTagIds" @change="doSearch">
        <el-checkbox v-for="tag in allTags" :key="tag.id" :value="tag.id" class="tag-checkbox">
          <el-tag :color="tag.color" effect="dark" size="small" style="border: none">
            {{ tag.name }}
          </el-tag>
        </el-checkbox>
      </el-checkbox-group>
    </div>

    <div class="results-header" v-if="searched">
      <span class="results-count">共找到 <strong>{{ total }}</strong> 条摘抄</span>
    </div>

    <div class="results-list">
      <div v-for="excerpt in items" :key="excerpt.id" class="excerpt-card">
        <div class="card-book-row">
          <el-icon><Notebook /></el-icon>
          <span class="book-name">{{ excerpt.book?.title || '未知书籍' }}</span>
          <span class="book-author" v-if="excerpt.book?.author">{{ excerpt.book.author }}</span>
        </div>

        <div class="card-columns">
          <div class="card-col content-col">
            <div class="col-label">摘抄原文</div>
            <div class="col-text">{{ excerpt.content }}</div>
          </div>
          <div class="card-col insights-col">
            <div class="col-label">个人想法</div>
            <div class="col-text">{{ excerpt.insights }}</div>
          </div>
          <div class="card-tags-col">
            <div class="col-label">标签</div>
            <div class="tags-wrap">
              <el-tag
                v-for="tag in excerpt.tags"
                :key="tag.id"
                :color="tag.color"
                effect="dark"
                size="small"
                style="margin: 2px"
              >
                {{ tag.name }}
              </el-tag>
            </div>
          </div>
        </div>

        <div class="card-meta" v-if="excerpt.links?.length || excerpt.images?.length">
          <div v-if="excerpt.links?.length" class="card-links">
            <el-icon><Link /></el-icon>
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
              class="card-image"
            />
          </div>
        </div>

        <div class="card-time">
          {{ excerpt.updated_at?.slice(0, 16) || excerpt.created_at?.slice(0, 16) }}
        </div>
      </div>

      <el-empty v-if="searched && items.length === 0" description="未找到匹配的摘抄" />
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

onMounted(() => {
  loadTags()
})

defineExpose({ refresh })
</script>

<style scoped>
.search-view {
  padding: 0;
}

.search-bar {
  margin-bottom: 16px;
}

.search-bar :deep(.el-input-group__append) {
  background-color: #5c4a32;
  border-color: #5c4a32;
}

.search-bar :deep(.el-input-group__append .el-button) {
  color: #fff;
}

.tag-filter {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.filter-label {
  font-size: 13px;
  color: #5c4a32;
  margin-right: 4px;
}

.tag-checkbox {
  margin-right: 2px !important;
}

.tag-checkbox :deep(.el-checkbox__label) {
  padding-left: 4px;
}

.results-header {
  margin-bottom: 12px;
}

.results-count {
  font-size: 14px;
  color: #666;
}

.results-count strong {
  color: #5c4a32;
}

.excerpt-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 12px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}

.card-book-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #5c4a32;
}

.card-book-row .book-author {
  font-weight: 400;
  font-size: 13px;
  color: #999;
}

.card-columns {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.card-col {
  flex: 1;
  min-width: 0;
}

.content-col {
  border-left: 3px solid #a67c52;
  padding-left: 10px;
}

.insights-col {
  border-left: 3px solid #409eff;
  padding-left: 10px;
}

.col-label {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.col-text {
  font-size: 14px;
  color: #3d3226;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-all;
}

.card-tags-col {
  max-width: 140px;
  min-width: 80px;
}

.tags-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
}

.card-meta {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.card-links {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

.card-link {
  color: #409eff;
  text-decoration: none;
  word-break: break-all;
}

.card-images {
  display: flex;
  gap: 6px;
}

.card-image {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  object-fit: cover;
}

.card-time {
  margin-top: 8px;
  font-size: 12px;
  color: #bbb;
}

.pagination-wrap {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
