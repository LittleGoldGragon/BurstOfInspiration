<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="添加摘抄"
    width="700px"
    destroy-on-close
    @opened="onOpened"
  >
    <el-form :model="form" label-width="80px" label-position="top">
      <el-form-item label="所属书籍" required>
        <el-select
          v-model="form.book_id"
          placeholder="选择已有书籍"
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="b in books"
            :key="b.id"
            :label="`${b.title}${b.author ? ' - ' + b.author : ''}`"
            :value="b.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="摘抄原文">
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="6"
          maxlength="5000"
          show-word-limit
          placeholder="粘贴书中原文..."
        />
      </el-form-item>

      <el-form-item label="个人想法">
        <el-input
          v-model="form.insights"
          type="textarea"
          :rows="3"
          maxlength="5000"
          show-word-limit
          placeholder="写下你的思考和感悟..."
        />
      </el-form-item>

      <el-form-item label="相关链接">
        <div v-for="(link, idx) in form.links" :key="idx" class="link-row">
          <el-input v-model="form.links[idx]" placeholder="https://..." />
          <el-button
            type="danger"
            :icon="Delete"
            circle
            size="small"
            @click="form.links.splice(idx, 1)"
          />
        </div>
        <el-button type="primary" :icon="Plus" size="small" @click="form.links.push('')">
          添加链接
        </el-button>
      </el-form-item>

      <el-form-item label="图片">
        <el-upload
          :auto-upload="false"
          list-type="picture-card"
          :file-list="fileList"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          accept="image/*"
        >
          <el-icon><Plus /></el-icon>
        </el-upload>
      </el-form-item>

      <el-form-item>
        <template #label>
          <span>标签</span>
          <el-button
            type="primary"
            link
            size="small"
            style="margin-left: 8px"
            @click="showTagManager = true"
          >
            管理标签
          </el-button>
        </template>
        <el-select
          v-model="form.tag_ids"
          multiple
          filterable
          allow-create
          placeholder="选择或输入新标签"
          style="width: 100%"
          @change="handleTagChange"
        >
          <el-option
            v-for="tag in allTags"
            :key="tag.id"
            :label="tag.name"
            :value="tag.id"
          >
            <span class="tag-option">
              <span class="tag-dot" :style="{ background: tag.color }"></span>
              {{ tag.name }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
    </template>

    <!-- Tag Manager Dialog -->
    <el-dialog v-model="showTagManager" title="管理标签" width="460px" append-to-body destroy-on-close>
      <div class="tag-manager-add">
        <el-input
          v-model="newTagName"
          placeholder="新标签名"
          style="width: 160px"
          maxlength="50"
        />
        <el-color-picker v-model="newTagColor" style="margin: 0 8px" />
        <el-button type="primary" :icon="Plus" size="small" @click="handleCreateTag">
          添加
        </el-button>
      </div>
      <el-divider />
      <div class="tag-manager-list">
        <div v-for="tag in allTags" :key="tag.id" class="tag-manager-item">
          <span class="tag-dot" :style="{ background: tag.color }"></span>
          <span class="tag-name">{{ tag.name }}</span>
          <el-popconfirm
            title="确定删除此标签？"
            @confirm="handleDeleteTag(tag.id)"
          >
            <template #reference>
              <el-button type="danger" :icon="Delete" circle size="small" />
            </template>
          </el-popconfirm>
        </div>
      </div>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { getBooks, createTag, deleteTag, getTags, uploadImage, createExcerpt } from '../api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  presetBookId: { type: Number, default: null },
})

const emit = defineEmits(['update:modelValue', 'saved'])

const books = ref([])
const allTags = ref([])
const saving = ref(false)

const form = reactive({
  book_id: null,
  content: '',
  insights: '',
  links: [],
  images: [],
  tag_ids: [],
})

const fileList = ref([])
const showTagManager = ref(false)
const newTagName = ref('')
const newTagColor = ref('#409EFF')

async function onOpened() {
  form.book_id = props.presetBookId || null
  form.content = ''
  form.insights = ''
  form.links = []
  form.images = []
  form.tag_ids = []
  fileList.value = []
  await Promise.all([loadBooks(), loadTags()])
}

async function loadBooks() {
  const res = await getBooks()
  books.value = res.data
}

async function loadTags() {
  const res = await getTags()
  allTags.value = res.data
}

async function handleSave() {
  if (!form.book_id) return
  saving.value = true
  try {
    const data = {
      book_id: form.book_id,
      content: form.content,
      insights: form.insights,
      links: form.links.filter(l => l.trim()),
      images: form.images,
      tag_ids: form.tag_ids,
    }
    await createExcerpt(data)
    emit('update:modelValue', false)
    emit('saved')
  } finally {
    saving.value = false
  }
}

async function handleFileChange(file) {
  try {
    const res = await uploadImage(file.raw)
    form.images.push(res.data.url)
  } catch {
    // upload failed
  }
}

function handleFileRemove(file) {
  const url = file.url || (file.response && file.response.url)
  if (url) {
    const idx = form.images.indexOf(url)
    if (idx > -1) form.images.splice(idx, 1)
  }
}

async function handleTagChange(val) {
  for (const v of val) {
    if (typeof v === 'string') {
      const idx = form.tag_ids.indexOf(v)
      if (idx > -1) form.tag_ids.splice(idx, 1)
      try {
        const res = await createTag({ name: v })
        allTags.value.push(res.data)
        form.tag_ids.push(res.data.id)
      } catch {
        // creation failed
      }
    }
  }
}

async function handleCreateTag() {
  if (!newTagName.value.trim()) return
  try {
    const res = await createTag({ name: newTagName.value.trim(), color: newTagColor.value })
    allTags.value.push(res.data)
    newTagName.value = ''
    newTagColor.value = '#409EFF'
  } catch {
    // creation failed
  }
}

async function handleDeleteTag(id) {
  try {
    await deleteTag(id)
    allTags.value = allTags.value.filter(t => t.id !== id)
    form.tag_ids = form.tag_ids.filter(tid => tid !== id)
  } catch {
    // deletion failed
  }
}
</script>

<style scoped>
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
  flex-shrink: 0;
}

.tag-manager-add {
  display: flex;
  align-items: center;
}

.tag-manager-list {
  max-height: 240px;
  overflow-y: auto;
}

.tag-manager-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
}

.tag-name {
  flex: 1;
  font-size: 14px;
}
</style>
