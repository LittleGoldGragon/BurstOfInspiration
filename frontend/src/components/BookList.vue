<template>
  <div class="bookshelf">
    <div class="bookshelf-header">
      <h2 class="section-title">我的书架</h2>
      <el-button
        type="primary"
        circle
        :icon="Plus"
        class="add-book-btn"
        @click="showAddBook = true"
      />
    </div>

    <!-- Book Groups -->
    <div v-if="groups.length === 0" class="empty-state">
      <el-empty description="还没有书籍，点击右上角 + 添加第一本书吧" />
    </div>

    <div v-for="group in groups" :key="group.book.id" class="book-group">
      <div class="book-header" @click="toggleBook(group.book.id)">
        <el-icon :class="['arrow', { expanded: expandedBooks[group.book.id] }]">
          <ArrowRight />
        </el-icon>
        <span class="book-title">{{ group.book.title }}</span>
        <span class="book-author" v-if="group.book.author">{{ group.book.author }}</span>
        <el-tag size="small" effect="plain" type="info" class="count-tag">
          {{ group.excerpts.length }} 条摘抄
        </el-tag>
        <div class="book-actions" @click.stop>
          <el-button
            type="primary"
            :icon="Plus"
            size="small"
            @click="openAddExcerpt(group.book.id)"
          >
            摘抄
          </el-button>
          <el-popconfirm
            title="确定删除此书及所有摘抄？"
            @confirm="handleDeleteBook(group.book.id)"
          >
            <template #reference>
              <el-button
                type="danger"
                :icon="Delete"
                size="small"
              />
            </template>
          </el-popconfirm>
        </div>
      </div>

      <div v-show="expandedBooks[group.book.id]" class="book-excerpts">
        <div v-if="group.excerpts.length === 0" class="no-excerpts">
          暂无摘抄
        </div>

        <div class="excerpts-grid">
          <div
            v-for="excerpt in group.excerpts"
            :key="excerpt.id"
            class="excerpt-card"
          >
            <div class="card-columns">
              <div class="card-col content-col">
                <div class="col-label">摘抄原文</div>
                <div class="col-text">{{ excerpt.content || '（无原文）' }}</div>
              </div>
              <div class="card-col insights-col">
                <div class="col-label">个人想法</div>
                <div class="col-text">{{ excerpt.insights || '（无想法）' }}</div>
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
                    style="margin: 2px; border: none"
                  >
                    {{ tag.name }}
                  </el-tag>
                  <span v-if="!excerpt.tags?.length" class="no-tags">-</span>
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

            <div class="card-footer">
              <span class="card-time">
                {{ excerpt.updated_at?.slice(0, 16) || excerpt.created_at?.slice(0, 16) }}
              </span>
              <div class="card-actions">
                <el-button
                  type="primary"
                  :icon="Edit"
                  size="small"
                  text
                  @click="openEditExcerpt(excerpt)"
                >
                  编辑
                </el-button>
                <el-popconfirm
                  title="确定删除此摘抄？"
                  @confirm="handleDeleteExcerpt(excerpt.id)"
                >
                  <template #reference>
                    <el-button
                      type="danger"
                      :icon="Delete"
                      size="small"
                      text
                    />
                  </template>
                </el-popconfirm>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Book Dialog -->
    <el-dialog v-model="showAddBook" title="添加书籍" width="400px" destroy-on-close>
      <el-form :model="newBook" label-width="60px">
        <el-form-item label="书名" required>
          <el-input v-model="newBook.title" placeholder="请输入书名" maxlength="255" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="newBook.author" placeholder="选填" maxlength="255" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddBook = false">取消</el-button>
        <el-button type="primary" @click="handleAddBook">添加</el-button>
      </template>
    </el-dialog>

    <!-- Add Excerpt Dialog -->
    <AddExcerpt
      v-model="showAddExcerpt"
      :preset-book-id="presetBookId"
      @saved="refresh"
    />

    <!-- Edit Excerpt Dialog -->
    <el-dialog v-model="showEditExcerpt" title="编辑摘抄" width="700px" destroy-on-close>
      <el-form :model="editForm" label-width="80px" label-position="top">
        <el-form-item label="所属书籍">
          <el-select v-model="editForm.book_id" filterable style="width: 100%">
            <el-option
              v-for="b in books"
              :key="b.id"
              :label="`${b.title}${b.author ? ' - ' + b.author : ''}`"
              :value="b.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="摘抄原文">
          <el-input v-model="editForm.content" type="textarea" :rows="6" maxlength="5000" show-word-limit />
        </el-form-item>
        <el-form-item label="个人想法">
          <el-input v-model="editForm.insights" type="textarea" :rows="3" maxlength="5000" show-word-limit />
        </el-form-item>
        <el-form-item label="相关链接">
          <div v-for="(link, idx) in editForm.links" :key="idx" class="link-row">
            <el-input v-model="editForm.links[idx]" />
            <el-button :icon="Delete" circle size="small" @click="editForm.links.splice(idx, 1)" />
          </div>
          <el-button type="primary" :icon="Plus" size="small" @click="editForm.links.push('')">添加链接</el-button>
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="editForm.tag_ids" multiple filterable allow-create style="width: 100%" @change="handleEditTagChange">
            <el-option v-for="tag in allTags" :key="tag.id" :label="tag.name" :value="tag.id">
              <span class="tag-option">
                <span class="tag-dot" :style="{ background: tag.color }"></span>
                {{ tag.name }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditExcerpt = false">取消</el-button>
        <el-button type="primary" @click="handleEditExcerpt">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, ArrowRight, Edit, Delete, Link } from '@element-plus/icons-vue'
import {
  getBookGroups, createBook, deleteBook,
  updateExcerpt, deleteExcerpt,
  getTags, createTag, getBooks,
} from '../api'
import AddExcerpt from './AddExcerpt.vue'

const groups = ref([])
const expandedBooks = reactive({})
const books = ref([])
const allTags = ref([])

const showAddBook = ref(false)
const newBook = reactive({ title: '', author: '' })

const showAddExcerpt = ref(false)
const presetBookId = ref(null)

const showEditExcerpt = ref(false)
const editForm = reactive({
  id: null,
  book_id: null,
  content: '',
  insights: '',
  links: [],
  tag_ids: [],
})

async function refresh() {
  const [groupsRes, booksRes, tagsRes] = await Promise.all([
    getBookGroups(),
    getBooks(),
    getTags(),
  ])
  groups.value = groupsRes.data
  books.value = booksRes.data
  allTags.value = tagsRes.data
}

function toggleBook(id) {
  expandedBooks[id] = !expandedBooks[id]
}

async function handleAddBook() {
  if (!newBook.title.trim()) return
  await createBook({ title: newBook.title.trim(), author: newBook.author.trim() })
  showAddBook.value = false
  newBook.title = ''
  newBook.author = ''
  await refresh()
}

async function handleDeleteBook(id) {
  await deleteBook(id)
  await refresh()
}

function openAddExcerpt(bookId) {
  presetBookId.value = bookId
  showAddExcerpt.value = true
}

function openEditExcerpt(excerpt) {
  editForm.id = excerpt.id
  editForm.book_id = excerpt.book_id
  editForm.content = excerpt.content
  editForm.insights = excerpt.insights
  editForm.links = [...(excerpt.links || [])]
  editForm.tag_ids = (excerpt.tags || []).map(t => t.id)
  showEditExcerpt.value = true
}

async function handleEditExcerpt() {
  const { id, ...rest } = editForm
  await updateExcerpt(id, {
    ...rest,
    links: rest.links.filter(l => l.trim()),
  })
  showEditExcerpt.value = false
  await refresh()
}

async function handleDeleteExcerpt(id) {
  await deleteExcerpt(id)
  await refresh()
}

async function handleEditTagChange(val) {
  for (const v of val) {
    if (typeof v === 'string') {
      const idx = editForm.tag_ids.indexOf(v)
      if (idx > -1) editForm.tag_ids.splice(idx, 1)
      try {
        const res = await createTag({ name: v })
        allTags.value.push(res.data)
        editForm.tag_ids.push(res.data.id)
      } catch {
        // creation failed
      }
    }
  }
}

onMounted(() => {
  refresh()
})

defineExpose({ refresh })
</script>

<style scoped>
.bookshelf {
  padding: 0;
}

.bookshelf-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  color: #3d3226;
}

.add-book-btn {
  width: 36px;
  height: 36px;
  background-color: #a67c52 !important;
  border-color: #a67c52 !important;
}

.add-book-btn:hover {
  background-color: #8b5e3c !important;
  border-color: #8b5e3c !important;
}

.empty-state {
  margin-top: 60px;
}

.book-group {
  margin-bottom: 12px;
}

.book-header {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s;
}

.book-header:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.arrow {
  transition: transform 0.2s;
  color: #5c4a32;
}

.arrow.expanded {
  transform: rotate(90deg);
}

.book-title {
  font-size: 16px;
  font-weight: 600;
  color: #3d3226;
}

.book-author {
  font-size: 13px;
  color: #999;
}

.count-tag {
  margin-left: 4px;
}

.book-actions {
  margin-left: auto;
  display: flex;
  gap: 6px;
}

.book-excerpts {
  padding-top: 12px;
}

.no-excerpts {
  text-align: center;
  color: #bbb;
  font-size: 13px;
  padding: 20px;
}

.excerpts-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.excerpt-card {
  background: #fff;
  border-radius: 8px;
  padding: 14px 18px;
  margin-left: 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.card-columns {
  display: flex;
  gap: 16px;
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
  font-size: 11px;
  color: #999;
  margin-bottom: 3px;
}

.col-text {
  font-size: 13px;
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

.no-tags {
  color: #ccc;
  font-size: 12px;
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
  font-size: 12px;
}

.card-link {
  color: #409eff;
  text-decoration: none;
  word-break: break-all;
  font-size: 12px;
}

.card-images {
  display: flex;
  gap: 6px;
}

.card-image {
  width: 56px;
  height: 56px;
  border-radius: 4px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.card-time {
  font-size: 12px;
  color: #bbb;
}

.card-actions {
  display: flex;
  gap: 4px;
}

.link-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}

.tag-option {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
</style>
