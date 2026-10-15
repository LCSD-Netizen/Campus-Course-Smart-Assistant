import { ref } from 'vue'
import { api, errorMessage } from '../api/client'
import { notify } from './useToast'
import { loadDashboard } from './useDashboard'

// 知识库、管理员页面数据。
const documents = ref([])
const users = ref([])
const courseOptions = ref([])
const uploadCourseId = ref(null)

export function useKnowledge() {
  // 读取知识库资料。
  async function loadDocuments() {
    try {
      const { data } = await api.get('/documents')
      documents.value = data
    } catch (error) {
      notify(errorMessage(error))
    }
  }

  // 读取管理员维护页面所需的用户、资料和课程数据。
  async function loadAdmin() {
    try {
      const [userResponse, documentResponse, courseResponse] = await Promise.all([
        api.get('/admin/users'),
        api.get('/documents'),
        api.get('/courses'),
      ])
      users.value = userResponse.data
      documents.value = documentResponse.data
      courseOptions.value = courseResponse.data
    } catch (error) {
      notify(errorMessage(error))
    }
  }

  // 上传资料文件并逐个入库。
  async function uploadFiles(files) {
    if (!files?.length) return

    for (const file of files) {
      const form = new FormData()
      form.append('file', file)

      try {
        await api.post('/admin/documents', form, {
          params: uploadCourseId.value
            ? { course_id: uploadCourseId.value }
            : {},
        })
        notify(`${file.name} 已入库`)
      } catch (error) {
        notify(`${file.name}：${errorMessage(error)}`)
      }
    }

    await loadDocuments()
    await loadDashboard()
  }

  // 切换用户的管理员角色。
  async function changeRole(row) {
    const role = row.role === 'admin' ? 'student' : 'admin'

    try {
      await api.patch(`/admin/users/${row.id}/role`, { role })
      row.role = role
      notify('用户角色已更新')
    } catch (error) {
      notify(errorMessage(error))
    }
  }

  // 保存用户的课程访问权限。
  async function saveCourseAccess(row) {
    try {
      await api.put(`/admin/users/${row.id}/courses`, {
        course_ids: row.course_ids || [],
      })
      notify(`已更新 ${row.display_name} 的课程权限`)
    } catch (error) {
      notify(errorMessage(error))
      await loadAdmin()
    }
  }

  return {
    documents,
    users,
    courseOptions,
    uploadCourseId,
    loadDocuments,
    loadAdmin,
    uploadFiles,
    changeRole,
    saveCourseAccess,
  }
}
