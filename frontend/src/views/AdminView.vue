<script setup>
import { onMounted, ref } from 'vue'
import { Upload } from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'
import { useKnowledge } from '../composables/useKnowledge'
import { fileIcon } from '../utils/format'

const { user } = useAuth()
const {
  documents,
  users,
  courseOptions,
  uploadCourseId,
  loadAdmin,
  uploadFiles,
  changeRole,
  saveCourseAccess,
} = useKnowledge()

const uploadInput = ref(null)

onMounted(loadAdmin)
</script>

<template>
  <div class="page-heading">
    <div>
      <p class="eyebrow">ADMIN CONSOLE</p>
      <h1>管理后台</h1>
      <p class="subheading">维护用户、选课权限和课程资料入库。</p>
    </div>
    <el-button type="primary" @click="uploadInput?.click()">
      <Upload :size="15" /> 上传课程资料
    </el-button>
  </div>

  <div class="admin-grid">
    <section class="card wide-card">
      <div class="section-head">
        <div><h2>用户管理</h2><small>{{ users.length }} 个账户</small></div>
      </div>
      <div v-for="row in users" :key="row.id" class="user-row">
        <div class="avatar avatar-blue">{{ row.display_name.slice(0, 1) }}</div>
        <div class="document-name">
          <b>{{ row.display_name }}</b>
          <small>{{ row.username }} · {{ row.department }}</small>
        </div>
        <el-select
          v-if="row.role === 'student'"
          v-model="row.course_ids"
          multiple
          collapse-tags
          size="small"
          class="access-select"
          placeholder="分配课程"
          @change="saveCourseAccess(row)"
        >
          <el-option
            v-for="course in courseOptions"
            :key="course.id"
            :label="course.name"
            :value="course.id"
          />
        </el-select>
        <el-tag size="small" :type="row.role === 'admin' ? 'warning' : 'info'">
          {{ row.role === 'admin' ? '管理员' : '学生' }}
        </el-tag>
        <el-button
          v-if="row.id !== user.id"
          text
          type="primary"
          @click="changeRole(row)"
        >
          {{ row.role === 'admin' ? '设为学生' : '设为管理员' }}
        </el-button>
      </div>
    </section>

    <section class="card wide-card">
      <div class="section-head">
        <div><h2>资料入库</h2><small>{{ documents.length }} 份资料可用</small></div>
      </div>
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
      <div class="upload-zone small-upload" @click="uploadInput?.click()">
        <Upload :size="19" />
        <b>上传课程资料</b>
        <span>PDF / DOCX / PPTX / TXT</span>
      </div>
      <div v-for="doc in documents.slice(0, 4)" :key="doc.id" class="document-row">
        <span class="file-icon">{{ fileIcon(doc.filename) }}</span>
        <div class="document-name">
          <b>{{ doc.filename }}</b>
          <small>{{ doc.characters.toLocaleString() }} 字符</small>
        </div>
      </div>
    </section>
  </div>

  <input
    ref="uploadInput"
    type="file"
    hidden
    multiple
    accept=".pdf,.docx,.pptx,.txt"
    @change="uploadFiles($event.target.files)"
  />
</template>
