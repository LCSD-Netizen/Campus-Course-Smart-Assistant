import { ref } from 'vue'
import { api, errorMessage } from '../api/client'
import { notify } from './useToast'

// 学习总览、课表、任务和学习计划数据。
const dashboard = ref({ courses: [], tasks: [], plans: [], stats: {} })
const loading = ref(false)
const taskDialog = ref(false)
const taskForm = ref({ title: '', kind: '作业', due_date: '', course_id: null })

// 读取当前账户的课表、待办和计划摘要。
export async function loadDashboard() {
  if (!localStorage.getItem('campus-token')) return
  loading.value = true

  try {
    const { data } = await api.get('/dashboard')
    dashboard.value = data
  } catch (error) {
    if (error.response?.status !== 401) notify(errorMessage(error))
  } finally {
    loading.value = false
  }
}

export function useDashboard() {
  // 创建学习任务。
  async function createTask() {
    try {
      await api.post('/tasks', taskForm.value)
      taskDialog.value = false
      taskForm.value = { title: '', kind: '作业', due_date: '', course_id: null }
      await loadDashboard()
      notify('任务已添加')
    } catch (error) {
      notify(errorMessage(error))
    }
  }

  // 切换任务的完成状态。
  async function toggleTask(task) {
    try {
      await api.patch(`/tasks/${task.id}/complete`)
      await loadDashboard()
    } catch (error) {
      notify(errorMessage(error))
    }
  }

  return {
    dashboard,
    loading,
    taskDialog,
    taskForm,
    createTask,
    toggleTask,
    loadDashboard,
  }
}
