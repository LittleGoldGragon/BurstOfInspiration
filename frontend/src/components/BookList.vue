<template>
  <div class="bookshelf">
    <div class="bookshelf-toolbar">
      <h2 class="section-title">书架</h2>
      <div class="toolbar-actions">
        <el-button class="btn-tag-manage" @click="showTagManager = true">
          <el-icon><CollectionTag /></el-icon>
          <span>标签</span>
        </el-button>
        <el-button circle class="btn-add-book" :icon="Plus" @click="showAddBook = true" />
      </div>
    </div>

    <div v-if="groups.length === 0" class="empty-state">
      <div class="empty-icon">
        <el-icon :size="48"><Notebook /></el-icon>
      </div>
      <p class="empty-text">还没有书籍</p>
      <p class="empty-hint">点击右上角 + 添加第一本书</p>
    </div>

    <div v-for="group in groups" :key="group.book.id" class="book-group">
      <div class="book-header" @click="toggleBook(group.book.id)">
        <span class="arrow-icon" :class="{ expanded: expandedBooks[group.book.id] }">
          <el-icon :size="14"><ArrowRight /></el-icon>
        </span>
        <span class="book-title">{{ group.book.title }}</span>
        <span class="book-author" v-if="group.book.author">{{ group.book.author }}</span>
        <span class="count-badge">{{ group.excerpts.length }}</span>
        <div class="book-actions" @click.stop>
          <el-button class="btn-excerpt" size="small" @click="openAddExcerpt(group.book.id)">
            <el-icon :size="14"><Plus /></el-icon>
            <span>摘抄</span>
          </el-button>
          <el-popconfirm
            title="确定删除此书及所有摘抄？"
            width="240"
            @confirm="handleDeleteBook(group.book.id)"
          >
            <template #reference>
              <el-button class="btn-delete-book" size="small" :icon="Delete" circle />
            </template>
          </el-popconfirm>
        </div>
      </div>

      <div v-show="expandedBooks[group.book.id]" class="book-excerpts">
        <div v-if="group.excerpts.length === 0" class="no-excerpts">
          暂无摘抄，点击右上角「摘抄」添加
        </div>

        <div class="excerpts-grid">
          <div
            v-for="excerpt in group.excerpts"
            :key="excerpt.id"
            class="excerpt-card"
          >
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
              <div class="card-actions">
                <button class="btn-text" @click="openEditExcerpt(excerpt)">编辑</button>
                <el-popconfirm
                  title="确定删除此摘抄？"
                  width="200"
                  @confirm="handleDeleteExcerpt(excerpt.id)"
                >
                  <template #reference>
                    <button class="btn-text btn-text-danger">删除</button>
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
      <el-form :model="newBook" label-position="top">
        <el-form-item label="书名" required>
          <el-input v-model="newBook.title" placeholder="请输入书名" maxlength="255" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="newBook.author" placeholder="选填" maxlength="255" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddBook = false" class="btn-cancel">取消</el-button>
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
      <el-form :model="editForm" label-position="top">
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
          <el-input v-model="editForm.content" type="textarea" :rows="5" maxlength="5000" show-word-limit />
        </el-form-item>
        <el-form-item label="个人想法">
          <el-input v-model="editForm.insights" type="textarea" :rows="3" maxlength="5000" show-word-limit />
        </el-form-item>
        <el-form-item label="相关链接">
          <div v-for="(link, idx) in editForm.links" :key="idx" class="link-input-row">
            <el-input v-model="editForm.links[idx]" placeholder="https://..." />
            <el-button :icon="Delete" circle size="small" @click="editForm.links.splice(idx, 1)" />
          </div>
          <el-button :icon="Plus" size="small" @click="editForm.links.push('')" class="btn-add-link">
            添加链接
          </el-button>
        </el-form-item>
        <el-form-item>
          <template #label>
            <span>标签</span>
            <el-button type="primary" link size="small" style="margin-left: 8px; font-weight: 400" @click="showTagManager = true">管理标签</el-button>
          </template>
          <el-select v-model="editForm.tag_ids" multiple filterable allow-create style="width: 100%" @change="handleEditTagChange">
            <el-option v-for="tag in allTags" :key="tag.id" :label="tag.name" :value="tag.id">
              <span class="tag-option">
                <span class="color-dot" :style="{ background: tag.color }"></span>
                {{ tag.name }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditExcerpt = false" class="btn-cancel">取消</el-button>
        <el-button type="primary" @click="handleEditExcerpt">保存</el-button>
      </template>
    </el-dialog>

    <!-- Tag Manager Dialog -->
    <el-dialog v-model="showTagManager" title="管理标签" width="480px" destroy-on-close>
      <div class="tag-manager">
        <div class="tag-mgr-add">
          <el-input
            v-model="newTagName"
            placeholder="标签名称"
            class="tag-mgr-input"
            maxlength="50"
            @keyup.enter="handleCreateTag"
          />
          <el-color-picker v-model="newTagColor" size="default" />
          <el-button type="primary" :icon="Plus" @click="handleCreateTag">添加</el-button>
        </div>
        <div class="tag-mgr-divider"></div>
        <div class="tag-mgr-list">
          <div v-for="tag in allTags" :key="tag.id" class="tag-mgr-item">
            <span class="color-dot" :style="{ background: tag.color }"></span>
            <el-input
              :model-value="tag.name"
              size="small"
              class="tag-mgr-edit-input"
              maxlength="50"
              @change="v => handleUpdateTag(tag.id, { name: v })"
            />
            <el-color-picker
              :model-value="tag.color"
              size="small"
              @change="v => handleUpdateTag(tag.id, { color: v })"
            />
            <el-popconfirm title="删除此标签？" width="200" @confirm="handleDeleteTag(tag.id)">
              <template #reference>
                <el-button :icon="Delete" circle size="small" class="btn-delete-tag" />
              </template>
            </el-popconfirm>
          </div>
          <div v-if="allTags.length === 0" class="tag-mgr-empty">
            暂无标签，在上方添加
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, ArrowRight, Edit, Delete, Link, Notebook, CollectionTag } from '@element-plus/icons-vue'
import {
  getBookGroups, createBook, deleteBook,
  updateExcerpt, deleteExcerpt,
  getTags, createTag, updateTag, deleteTag, getBooks,
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

const showTagManager = ref(false)
const newTagName = ref('')
const newTagColor = ref('#57534e')

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
      } catch { /* creation failed */ }
    }
  }
}

async function handleCreateTag() {
  if (!newTagName.value.trim()) return
  try {
    const res = await createTag({ name: newTagName.value.trim(), color: newTagColor.value })
    allTags.value.push(res.data)
    newTagName.value = ''
  } catch { /* creation failed */ }
}

async function handleDeleteTag(id) {
  try {
    await deleteTag(id)
    allTags.value = allTags.value.filter(t => t.id !== id)
    editForm.tag_ids = editForm.tag_ids.filter(tid => tid !== id)
  } catch { /* deletion failed */ }
}

async function handleUpdateTag(id, data) {
  try {
    await updateTag(id, data)
    await refresh()
  } catch { /* update failed */ }
}

onMounted(() => { refresh() })

defineExpose({ refresh })
</script>

<style scoped>
/* ─── Toolbar ─── */
.bookshelf {
  padding: 0;
}

.bookshelf-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1c1c1c;
  letter-spacing: 1px;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-tag-manage {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 34px;
  padding: 0 14px;
  border: 1px solid #d6d3d1;
  border-radius: 6px;
  background: #fff;
  color: #57534e;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-tag-manage:hover {
  border-color: #a8a29e;
  color: #1c1c1c;
}

.btn-add-book {
  width: 34px;
  height: 34px;
  background: #1c1c1c !important;
  border-color: #1c1c1c !important;
  color: #fff !important;
}

.btn-add-book:hover {
  background: #44403c !important;
  border-color: #44403c !important;
}

/* ─── Empty State ─── */
.empty-state {
  text-align: center;
  padding: 80px 0;
}

.empty-icon {
  color: #d6d3d1;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  color: #78716c;
  margin-bottom: 4px;
}

.empty-hint {
  font-size: 13px;
  color: #a8a29e;
}

/* ─── Book Group ─── */
.book-group {
  margin-bottom: 2px;
}

.book-header {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff;
  padding: 14px 18px;
  cursor: pointer;
  border: 1px solid #edeae5;
  border-bottom: none;
  transition: background 0.12s;
}

.book-group:first-of-type .book-header {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.book-group:last-of-type .book-header {
  border-bottom: 1px solid #edeae5;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}

.book-group:has(.book-excerpts[style*="display: none"]) .book-header,
.book-group:not(:has(.book-excerpts)) .book-header {
  border-bottom: 1px solid #edeae5;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}

.book-header:hover {
  background: #fafaf9;
}

.arrow-icon {
  display: flex;
  align-items: center;
  color: #a8a29e;
  transition: transform 0.2s;
}

.arrow-icon.expanded {
  transform: rotate(90deg);
}

.book-title {
  font-size: 15px;
  font-weight: 600;
  color: #1c1c1c;
}

.book-author {
  font-size: 13px;
  color: #a8a29e;
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: #f0eeea;
  color: #78716c;
  font-size: 11px;
  font-weight: 500;
}

.book-actions {
  margin-left: auto;
  display: flex;
  gap: 6px;
  align-items: center;
}

.btn-excerpt {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 28px;
  padding: 0 10px;
  border: 1px solid #d6d3d1;
  border-radius: 5px;
  background: #fff;
  color: #57534e;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-excerpt:hover {
  border-color: #1c1c1c;
  color: #1c1c1c;
  background: #fafaf9;
}

.btn-delete-book {
  width: 28px;
  height: 28px;
  border: 1px solid #edeae5 !important;
  background: #fff !important;
  color: #a8a29e !important;
}

.btn-delete-book:hover {
  border-color: #e74c3c !important;
  color: #e74c3c !important;
  background: #fef2f2 !important;
}

/* ─── Excerpts ─── */
.book-excerpts {
  background: #fcfbfa;
  border-left: 1px solid #edeae5;
  border-right: 1px solid #edeae5;
  border-bottom: 1px solid #edeae5;
  padding: 16px 18px 20px 36px;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}

.no-excerpts {
  text-align: center;
  color: #a8a29e;
  font-size: 13px;
  padding: 24px 0;
}

.excerpts-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.excerpt-card {
  background: #fff;
  border: 1px solid #edeae5;
  border-radius: 6px;
  padding: 16px 18px;
  transition: border-color 0.15s;
}

.excerpt-card:hover {
  border-color: #d6d3d1;
}

.card-body {
  display: flex;
  gap: 20px;
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
  margin-top: 10px;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f5f3f0;
}

.card-time {
  font-size: 12px;
  color: #d6d3d1;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.btn-text {
  background: none;
  border: none;
  font-size: 12px;
  color: #57534e;
  cursor: pointer;
  padding: 2px 0;
}

.btn-text:hover {
  color: #1c1c1c;
}

.btn-text-danger:hover {
  color: #e74c3c;
}

/* ─── Forms / Links ─── */
.link-input-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}

.btn-add-link {
  height: 28px;
  font-size: 12px;
}

.tag-option {
  display: flex;
  align-items: center;
  gap: 6px;
}

.color-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.btn-cancel {
  border: 1px solid #d6d3d1 !important;
  background: #fff !important;
  color: #57534e !important;
}

.btn-cancel:hover {
  border-color: #a8a29e !important;
  color: #1c1c1c !important;
}

/* ─── Tag Manager ─── */
.tag-manager {
  padding: 0;
}

.tag-mgr-add {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tag-mgr-input {
  flex: 1;
}

.tag-mgr-divider {
  height: 1px;
  background: #edeae5;
  margin: 18px 0;
}

.tag-mgr-list {
  max-height: 260px;
  overflow-y: auto;
}

.tag-mgr-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 4px;
  border-bottom: 1px solid #f5f3f0;
}

.tag-mgr-item:last-child {
  border-bottom: none;
}

.tag-mgr-edit-input {
  flex: 1;
}

.btn-delete-tag {
  border: 1px solid #edeae5 !important;
  background: #fff !important;
  color: #a8a29e !important;
}

.btn-delete-tag:hover {
  border-color: #e74c3c !important;
  color: #e74c3c !important;
  background: #fef2f2 !important;
}

.tag-mgr-empty {
  text-align: center;
  color: #a8a29e;
  font-size: 13px;
  padding: 24px 0;
}
</style>
