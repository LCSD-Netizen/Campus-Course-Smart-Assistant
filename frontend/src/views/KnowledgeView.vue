<script setup>
import { computed, onMounted, ref } from 'vue'
import { LibraryBig, Search, Upload } from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'
import { useDashboard } from '../composables/useDashboard'
import { useKnowledge } from '../composables/useKnowledge'
import { fileIcon } from '../utils/format'

const { user } = useAuth()
const { dashboard } = useDashboard()
const {
  documents,
  courseOptions,
  uploadCourseId,
  loadDocuments,
  uploadFiles,
} = useKnowledge()

const uploadInput = ref(null)
const docSearch = ref('')

// 根据搜索关键字过滤可访问的资料。
const visibleDocuments = computed(() =>
  documents.value.filter((doc) =>
    doc.filename.toLowerCase().includes(docSearch.value.toLowerCase()),
  ),
)

onMounted(loadDocuments)
</script>

<template>
  <div class="page-heading">
    <div>
      <p class="eyebrow">YOUR COURSE KNOWLEDGE</p>
      <h1>智能知识库</h1>
      <p class="subheading">课程资料由管理员维护，问答时会按你的选课权限检索。</p>
    </div>
    <el-button v-if="user.role === 'admin'" type="primary" @click="uploadInput?.click()">
      <Upload :size="15" /> 上传资料
    </el-button>
  </div>

  <div class="kb-stats">
    <div class="card"><strong>{{ documents.length }}</strong><small>份可访问资料</small></div>
    <div class="card"><strong>{{ dashboard.stats.courses || 0 }}</strong><small>门已选课程</small></div>
    <div class="card"><strong>RAG</strong><small>语义检索问答</small></div>
  </div>

  <section class="card wide-card">
    <div v-if="user.role === 'admin'">
      <div class="upload-course">
        <span>资料所属课程</span>
        <el-select
          v-model="uploadCourseId"
          clearable
          placeholder="共享资料（所有学生可访问）"
          size="small"
        >
          <el-option
            v-for="course in courseOptions"
            :key="course.id"
            :label="course.name"
            :value="course.id"
          />
        </el-select>
      </div>
      <div
        class="upload-zone"
        @click="uploadInput?.click()"
        @dragover.prevent
        @drop.prevent="uploadFiles($event.dataTransfer.files)"
      >
        <Upload :size="20" />
        <b>点击上传或拖拽资料到这里</b>
        <span>PDF、DOCX、PPTX、TXT，单个文件最大 20MB</span>
      </div>
    </div>
    <div v-else class="access-note">
      <LibraryBig :size="16" /> 学生账户仅可访问已选课程资料；资料由管理员上传与维护。
    </div>

    <div class="section-head document-heading">
      <div><h2>可访问资料</h2><small>资料检索范围受课程权限控制</small></div>
      <label class="search-field">
        <Search :size="15" />
        <input v-model="docSearch" placeholder="搜索资料名称..." />
      </label>
    </div>

    <div v-for="doc in visibleDocuments" :key="doc.id" class="document-row">
      <span class="file-icon">{{ fileIcon(doc.filename) }}</span>
      <div class="document-name">
        <b>{{ doc.filename }}</b>
        <small>
          {{ doc.characters.toLocaleString() }} 字符 ·
          {{ new Date(doc.created_at).toLocaleDateString('zh-CN') }}
        </small>
      </div>
      <span class="status-pill done">已入库</span>
    </div>
    <div v-if="!visibleDocuments.length" class="empty-state">
      {{ user.role === 'admin' ? '还没有资料，上传课件即可建立课程知识库。' : '当前选课范围内暂无资料，请联系管理员维护。' }}
    </div>
  </section>

  <input
    ref="uploadInput"
    type="file"
    hidden
    multiple
    accept=".pdf,.docx,.pptx,.txt"
    @change="uploadFiles($event.target.files)"
  />
</template>
