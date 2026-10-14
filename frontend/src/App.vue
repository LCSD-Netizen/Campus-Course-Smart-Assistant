<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import {
  ArrowUp,
  Bell,
  BookOpen,
  CalendarDays,
  Check,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  Clock3,
  FileText,
  GraduationCap,
  LayoutDashboard,
  LibraryBig,
  LogOut,
  MessageCircle,
  PanelLeftClose,
  Plus,
  Search,
  Settings,
  Sparkles,
  Upload,
  Users,
} from 'lucide-vue-next'
import { api, errorMessage } from './api/client'

// 登录信息和页面状态。
const token = ref(localStorage.getItem('campus-token'))
const user = ref(null)
const page = ref('home')
const busy = ref(false)
const loading = ref(false)
const loginForm = ref({ username: 'demo', password: 'demo1234' })
const registerMode = ref(false)
const registerName = ref('')
const loginError = ref('')

// 学习总览、课表、任务和学习计划数据。
const dashboard = ref({ courses: [], tasks: [], plans: [], stats: {} })
const taskDialog = ref(false)
const taskForm = ref({ title: '', kind: '作业', due_date: '', course_id: null })
const weekOffset = ref(0)
const selectedDate = ref(new Date())
const courseSearch = ref('')

// 课程问答和 SSE 流式响应状态。
const chatInput = ref('')
const messages = ref([])
const activeTools = ref([])
const chatScroller = ref(null)

// 知识库、管理员页面和全局提示状态。
const documents = ref([])
const users = ref([])
const courseOptions = ref([])
const uploadCourseId = ref(null)
const uploadInput = ref(null)
const docSearch = ref('')
const toast = ref('')
let toastTimer

// 收到新消息后自动滚动，保持最新回答可见。
watch(
  messages,
  () =>
    nextTick(() => {
      if (chatScroller.value) {
        chatScroller.value.scrollTop = chatScroller.value.scrollHeight
      }
    }),
  { deep: true },
)

// 根据页面状态计算标题、周日期及筛选结果。
const pageTitle = computed(() => ({
  home: '学习总览',
  schedule: '我的课表',
  courses: '课程资料',
  tasks: '作业与考试',
  plans: '学习计划',
  chat: '课程问答',
  knowledge: '智能知识库',
  admin: '管理后台',
}[page.value]))
const firstName = computed(() => user.value?.display_name || '同学')
const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const weekDays = computed(() => {
  const now = new Date()
  const monday = new Date(now)
  monday.setDate(now.getDate() - ((now.getDay() + 6) % 7) + weekOffset.value * 7)

  return weekdays.map((label, index) => {
    const date = new Date(monday)
    date.setDate(monday.getDate() + index)

    return {
      label,
      date,
      day: date.getDate(),
      selected: date.toDateString() === selectedDate.value.toDateString(),
    }
  })
})
const visibleCourses = computed(() =>
  dashboard.value.courses.filter((course) =>
    course.name.includes(courseSearch.value),
  ),
)
const visibleDocuments = computed(() =>
  documents.value.filter((doc) =>
    doc.filename.toLowerCase().includes(docSearch.value.toLowerCase()),
  ),
)

// 显示短暂提示，并清理上一次提示的计时器。
function notify(message) {
  toast.value = message
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.value = ''
  }, 2600)
}

// 切换左侧导航对应的页面，并按需加载页面数据。
function navigate(name) {
  page.value = name
  if (name === 'knowledge') loadDocuments()
  if (name === 'admin') loadAdmin()
}

// 清除本地登录状态，回到账户登录页面。
function logout() {
  localStorage.removeItem('campus-token')
  token.value = null
  user.value = null
  messages.value = []
  page.value = 'home'
  loginForm.value = { username: '', password: '' }
  registerName.value = ''
  registerMode.value = false
  loginError.value = ''
}

// 切换登录和注册表单。
function toggleAuthMode() {
  registerMode.value = !registerMode.value
  loginError.value = ''

  if (registerMode.value) {
    loginForm.value = { username: '', password: '' }
    registerName.value = ''
  }
}

// 登录成功后保存令牌并读取学习总览。
async function login() {
  busy.value = true
  loginError.value = ''

  try {
    const { data } = await api.post('/auth/login', loginForm.value)
    localStorage.setItem('campus-token', data.access_token)
    token.value = data.access_token
    user.value = data.user
    await loadDashboard()
    notify(`欢迎回来，${data.user.display_name}`)
  } catch (error) {
    loginError.value = errorMessage(error)
  } finally {
    busy.value = false
  }
}

// 创建账户后自动登录新账户。
async function register() {
  busy.value = true
  loginError.value = ''

  try {
    const { data } = await api.post('/auth/register', {
      username: loginForm.value.username,
      password: loginForm.value.password,
      display_name: registerName.value || '新同学',
    })
    localStorage.setItem('campus-token', data.access_token)
    token.value = data.access_token
    user.value = data.user
    await loadDashboard()
    notify('账户已创建，欢迎加入知课')
  } catch (error) {
    loginError.value = errorMessage(error)
  } finally {
    busy.value = false
  }
}

// 读取当前账户的课表、待办和计划摘要。
async function loadDashboard() {
  if (!token.value) return
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

// 刷新页面时验证并恢复上一次登录状态。
async function restoreSession() {
  if (!token.value) return

  try {
    const { data } = await api.get('/auth/me')
    user.value = data
    await loadDashboard()
  } catch {
    logout()
  }
}

// 读取知识库和管理员维护页面所需的数据。
async function loadDocuments() {
  try {
    const { data } = await api.get('/documents')
    documents.value = data
  } catch (error) {
    notify(errorMessage(error))
  }
}

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

// 处理服务端事件流中的进度、工具结果和回答文本。
function parseSSEBlock(block, message) {
  const lines = block.split('\n')
  const eventLine = lines.find((line) => line.startsWith('event: '))
  const dataLine = lines.find((line) => line.startsWith('data: '))
  if (!eventLine || !dataLine) return

  const kind = eventLine.slice(7)
  let payload
  try {
    payload = JSON.parse(dataLine.slice(6))
  } catch {
    return
  }

  if (kind === 'status') {
    message.status = payload.message
    message.thinking = true
  }
  if (kind === 'tool_start') {
    message.thinking = false
    activeTools.value.push({
      name: payload.name,
      label: payload.label,
      input: payload.input,
      state: 'running',
    })
    message.events.push({ kind, ...payload })
  }
  if (kind === 'tool_result') {
    const item = [...activeTools.value]
      .reverse()
      .find((tool) => tool.name === payload.name && tool.state === 'running')
    if (item) {
      item.state = 'done'
      item.result = payload.result
    }
    message.events.push({ kind, ...payload })
  }
  if (kind === 'token') {
    message.thinking = false
    message.content += payload.text
  }
  if (kind === 'done') {
    message.thinking = false
    message.done = true
    if (!message.content) message.content = payload.answer || ''
    activeTools.value = []
    loadDashboard()
  }
  if (kind === 'error') {
    message.thinking = false
    message.error = payload.message
    activeTools.value = []
  }
}

// 提交问题，读取 SSE 响应并实时追加 AI 回复。
async function sendMessage(value = chatInput.value) {
  const prompt = value.trim()
  if (!prompt || busy.value) return

  chatInput.value = ''
  navigate('chat')
  messages.value.push({ role: 'user', content: prompt })
  const assistant = {
    role: 'assistant',
    content: '',
    events: [],
    thinking: true,
    done: false,
  }
  messages.value.push(assistant)
  busy.value = true

  try {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify({ message: prompt }),
    })
    if (!response.ok) {
      throw new Error((await response.json()).detail || '对话请求失败')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { value: chunk, done } = await reader.read()
      if (done) break

      buffer += decoder.decode(chunk, { stream: true })
      const blocks = buffer.split('\n\n')
      buffer = blocks.pop() || ''
      for (const block of blocks) parseSSEBlock(block, assistant)
    }
  } catch (error) {
    assistant.thinking = false
    assistant.error = errorMessage(error)
    activeTools.value = []
  } finally {
    busy.value = false
  }
}

// 点击推荐问题时复用统一的发送流程。
function ask(prompt) {
  sendMessage(prompt)
}

// 创建、完成任务以及维护课程资料和账户权限。
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

async function toggleTask(task) {
  try {
    await api.patch(`/tasks/${task.id}/complete`)
    await loadDashboard()
  } catch (error) {
    notify(errorMessage(error))
  }
}

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

// 模板格式化辅助函数。
function formatDate(value) {
  if (!value) return '未设置'
  return new Date(`${value}T00:00:00`).toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
  })
}

function dayCourses(dayIndex) {
  return dashboard.value.courses.filter(
    (course) => course.weekday === dayIndex + 1,
  )
}

function fileIcon(filename) {
  return filename.split('.').pop()?.toUpperCase() || '文件'
}

// 组件加载后尝试恢复现有登录会话。
onMounted(restoreSession)
</script>

<template>
  <!-- 登录和注册页面：未登录时展示账户表单。 -->
  <div v-if="!user" class="login-page">
    <div class="login-art"><div class="art-glow"></div><div class="art-brand"><span class="brand-mark">知</span><span><b>知课</b><small>CAMPUS COPILOT</small></span></div><div class="art-copy"><div class="eyebrow">YOUR CAMPUS, CONNECTED</div><h1>让每一门课，<br>都变得更清晰。</h1><p>课程安排、学习资料与智能问答，<br>一个学习空间，陪你把知识学得更扎实。</p><div class="floating-note"><Sparkles :size="16"/><span>你的课程 AI 助手已准备就绪</span><i></i></div></div><div class="art-bottom">课程 · 知识 · 计划　　为学习而连接</div></div>
    <div class="login-side"><form class="login-form" @submit.prevent="registerMode?register():login()"><div class="mobile-brand"><span class="brand-mark">知</span><b>知课</b></div><div class="eyebrow">{{ registerMode?'CREATE YOUR ACCOUNT':'WELCOME BACK' }}</div><h2>{{ registerMode?'创建学习账户':'登录你的学习空间' }}</h2><p class="muted">{{ registerMode?'创建账户，开始管理你的校园学习。':'输入账户信息，继续你的校园学习旅程。' }}</p><label v-if="registerMode">你的称呼<el-input v-model="registerName" size="large" placeholder="例如：林同学" autocomplete="name" /></label><label>用户名<el-input v-model="loginForm.username" size="large" placeholder="输入用户名" autocomplete="username" /></label><label>密码<el-input v-model="loginForm.password" size="large" type="password" show-password :placeholder="registerMode?'至少 8 位':'输入密码'" autocomplete="current-password" /></label><div v-if="loginError" class="form-error">{{ loginError }}</div><el-button class="login-button" type="primary" size="large" native-type="submit" :loading="busy">{{ registerMode?'创建账户':'登录' }}</el-button><div class="auth-switch">{{ registerMode?'已有账户？':'还没有账户？' }} <button type="button" @click="toggleAuthMode">{{ registerMode?'返回登录':'注册一个账户' }}</button></div><div v-if="!registerMode" class="demo-hint"><span>演示账户</span><b>学生 demo / demo1234</b><b>管理员 admin / admin1234</b></div></form></div>
  </div>
  <!-- 主应用：侧边导航、当前功能页和全局弹窗。 -->
  <div v-else class="app-shell">
    <aside class="sidebar">
      <a class="brand" href="#" @click.prevent="navigate('home')"><span class="brand-mark">知</span><span><b>知课</b><small>CAMPUS COPILOT</small></span></a>
      <div class="workspace-label">工作空间 <span>⌄</span></div><div class="workspace"><div class="avatar avatar-blue">{{ firstName.slice(0, 1) }}</div><span><b>{{ firstName }}</b><small>{{ user.department || '计算机科学与技术' }}</small></span><span class="role-badge">{{ user.role === 'admin' ? '管理员' : '学生' }}</span></div>
      <div class="nav-label">学习空间</div><nav class="nav-list"><button v-for="item in [{id:'home',label:'学习总览',icon:LayoutDashboard},{id:'schedule',label:'我的课表',icon:CalendarDays},{id:'courses',label:'课程资料',icon:BookOpen},{id:'tasks',label:'作业与考试',icon:ClipboardList},{id:'plans',label:'学习计划',icon:Check}]" :key="item.id" class="nav-item" :class="{active:page===item.id}" @click="navigate(item.id)"><component :is="item.icon" :size="17"/><span>{{ item.label }}</span><span v-if="item.id==='tasks'&&dashboard.stats.pending_tasks" class="nav-count">{{ dashboard.stats.pending_tasks }}</span></button></nav>
      <div class="nav-label assistant-label">智能助手</div><nav class="nav-list"><button class="nav-item" :class="{active:page==='chat'}" @click="navigate('chat')"><MessageCircle :size="17"/><span>课程问答</span></button><button class="nav-item" :class="{active:page==='knowledge'}" @click="navigate('knowledge')"><LibraryBig :size="17"/><span>知识库</span></button><button v-if="user.role==='admin'" class="nav-item" :class="{active:page==='admin'}" @click="navigate('admin')"><Users :size="17"/><span>管理后台</span></button></nav>
      <div class="sidebar-bottom"><div class="plan-card"><div class="plan-icon"><Sparkles :size="15"/></div><b>让学习更进一步</b><p>连接课程资料，获得专属 AI 学习伙伴。</p><button @click="navigate('knowledge')">管理智能知识库 <span>→</span></button></div><button class="nav-item settings" @click="notify('账户设置即将开放')"><Settings :size="16"/><span>设置</span></button><div class="sidebar-user"><div class="avatar avatar-green">{{ firstName.slice(0, 1) }}</div><span><b>{{ firstName }}</b><small>{{ user.username }}</small></span><button title="退出登录" class="logout" @click="logout"><LogOut :size="15"/></button></div></div>
    </aside>
    <main class="main-area"><header class="topbar"><div class="breadcrumb">学习空间 <span>/</span> <b>{{ pageTitle }}</b></div><div class="top-actions"><button class="icon-btn" title="搜索课程" @click="navigate('courses')"><Search :size="19"/></button><button class="icon-btn notification" title="通知" @click="navigate('tasks')"><Bell :size="18"/><i></i></button><button class="account-exit" title="退出当前账号并切换登录" @click="logout"><LogOut :size="14"/><span>退出</span></button></div></header>
      <div class="page-content">
        <!-- 学习总览：课程、近期任务和 AI 快捷提问。 -->
        <template v-if="page==='home'">
          <div class="page-heading"><div><p class="eyebrow">{{ new Date().toLocaleDateString('zh-CN',{weekday:'long',month:'long',day:'numeric'}) }}</p><h1>早上好，{{ firstName }} <span class="wave">👋</span></h1><p class="subheading">新的一天，继续保持学习节奏。</p></div><el-button class="date-chip" plain><CalendarDays :size="15"/> {{ new Date().getFullYear() }} 学年 · 秋季学期</el-button></div>
          <div class="stats-grid"><div class="card stat-card"><div class="stat-top">本学期课程<span class="stat-icon lilac"><BookOpen :size="16"/></span></div><div class="stat-value">{{ dashboard.stats.courses || 0 }}<small> 门</small></div><div class="stat-foot">课程表已同步</div></div><div class="card stat-card"><div class="stat-top">待完成任务<span class="stat-icon amber"><Clock3 :size="16"/></span></div><div class="stat-value">{{ dashboard.stats.pending_tasks || 0 }}<small> 项</small></div><div class="stat-foot">安排好截止时间</div></div><div class="card stat-card"><div class="stat-top">学习计划<span class="stat-icon mint"><Check :size="16"/></span></div><div class="stat-value">{{ dashboard.plans?.length || 0 }}<small> 份</small></div><div class="stat-foot">由你和 AI 共同整理</div></div><div class="card stat-card"><div class="stat-top">课程资料<span class="stat-icon sky"><LibraryBig :size="16"/></span></div><div class="stat-value">{{ dashboard.stats.documents || 0 }}<small> 份</small></div><div class="stat-foot">检索增强问答已就绪</div></div></div>
          <div class="dashboard-grid"><div><section class="card section-card"><div class="section-head"><div><h2>本周课程</h2><small>按时间顺序安排好你的学习</small></div><button class="text-link" @click="navigate('schedule')">完整课表　→</button></div><div class="week-strip"><button v-for="day in weekDays" :key="day.date.toISOString()" class="week-day" :class="{selected:day.selected}" @click="selectedDate=day.date"><span>{{ day.label }}</span><b>{{ day.day }}</b></button></div><div v-if="dayCourses((selectedDate.getDay()+6)%7).length" class="lesson-list"><div v-for="course in dayCourses((selectedDate.getDay()+6)%7)" :key="course.id" class="lesson"><div class="lesson-time">{{ course.start_time }}<small>{{ course.end_time }}</small></div><div class="lesson-bar" :class="course.color"></div><div><div class="lesson-name">{{ course.name }}</div><div class="lesson-meta">{{ course.teacher }} · {{ course.room }}</div></div><span class="status-pill">{{ course.weeks }}</span></div></div><div v-else class="empty-state">今天没有排课，给自己留一些自由学习时间。</div></section><section class="card section-card upcoming-card"><div class="section-head"><div><h2>近期任务</h2><small>记得按时完成哦</small></div><button class="text-link" @click="navigate('tasks')">查看全部　→</button></div><div v-for="task in dashboard.tasks.slice(0,3)" :key="task.id" class="task-row"><button class="task-check" :class="{checked:task.completed}" @click="toggleTask(task)"><Check :size="12"/></button><div class="task-info"><b>{{ task.title }}</b><small>{{ task.course_name }} · {{ task.kind }}</small></div><div class="task-due">{{ task.days_left < 0 ? '已逾期' : task.days_left===0 ? '今天截止' : `${task.days_left} 天后` }}<small>{{ formatDate(task.due_date) }}</small></div></div><div v-if="!dashboard.tasks.length" class="empty-state compact">还没有任务，保持轻松。</div></section></div>
            <div><section class="card ai-card"><div class="ai-top"><span class="ai-spark"><Sparkles :size="16"/></span><b>知课 AI 助手</b><span class="online">在线</span></div><h3>今天想学点什么？</h3><p>我可以帮你查课表、解答课程问题，或整理一份学习计划。</p><div class="prompt-chips"><button class="prompt-chip" @click="ask('这周我的课表是什么？')">✦　这周我的课表是什么？</button><button class="prompt-chip" @click="ask('帮我总结数据结构课程重点')">▧　帮我总结课程重点</button><button class="prompt-chip" @click="ask('帮我制定并保存本周学习计划')">◷　制定本周学习计划</button></div><form class="chat-entry" @submit.prevent="sendMessage()"><input v-model="chatInput" placeholder="问问你的课程..."/><button class="send-btn"><ArrowUp :size="15"/></button></form></section><section class="card quick-card"><div class="section-head"><h2>快捷入口</h2></div><div class="quick-links"><button class="quick-link" @click="navigate('courses')"><BookOpen/>课程资料</button><button class="quick-link" @click="navigate('tasks')"><ClipboardList/>待办任务</button><button class="quick-link" @click="navigate('schedule')"><CalendarDays/>查看课表</button><button class="quick-link" @click="navigate('knowledge')"><LibraryBig/>智能知识库</button></div></section></div></div>
        </template>
        <!-- 我的课表：查看当前周和各课程时间。 -->
        <template v-else-if="page==='schedule'"><div class="page-heading"><div><p class="eyebrow">{{ weekDays[0]?.date.toLocaleDateString('zh-CN',{month:'long',day:'numeric'}) }} — {{ weekDays[6]?.date.toLocaleDateString('zh-CN',{month:'long',day:'numeric'}) }}</p><h1>我的课表</h1><p class="subheading">只展示你已选课程的安排。</p></div><div class="week-nav"><el-button circle plain @click="weekOffset--"><ChevronLeft :size="16"/></el-button><el-button plain @click="weekOffset=0">本周</el-button><el-button circle plain @click="weekOffset++"><ChevronRight :size="16"/></el-button></div></div><section class="card wide-card"><div class="schedule"><div class="schedule-corner"></div><div v-for="day in weekDays" :key="day.date.toISOString()" class="schedule-head" :class="{today:day.selected}">{{ day.label }}<b>{{ day.day }}</b></div><template v-for="hour in ['08:00','10:00','12:00','14:00','16:00','18:00']" :key="hour"><div class="schedule-time">{{ hour }}</div><div v-for="day in weekDays" :key="`${hour}-${day.label}`" class="schedule-cell"><div v-for="course in dayCourses(weekdays.indexOf(day.label)).filter(c=>parseInt(c.start_time.slice(0,2))===parseInt(hour.slice(0,2)))" :key="course.id" class="schedule-lesson" :class="course.color"><b>{{ course.name }}</b><small>{{ course.start_time }}-{{ course.end_time }} · {{ course.room }}</small></div></div></template></div><div class="schedule-legend"><span><i class="legend-dot blue"></i>课程时间以教务安排为准</span><span>{{ dashboard.courses.length }} 门已选课程</span></div></section></template>
        <!-- 课程资料：浏览已选课程并搜索课程信息。 -->
        <template v-else-if="page==='courses'"><div class="page-heading"><div><p class="eyebrow">COURSE SPACE</p><h1>课程资料</h1><p class="subheading">整理课程内容，快速回到你的学习现场。</p></div><el-button type="primary" @click="navigate('knowledge')"><Plus :size="15"/> 添加资料</el-button></div><section class="card wide-card"><div class="toolbar"><label class="search-field"><Search :size="15"/><input v-model="courseSearch" placeholder="搜索课程名称、教师..."/></label><span class="muted small">{{ visibleCourses.length }} 门课程</span></div><div class="course-grid"><article v-for="(course,index) in visibleCourses" :key="course.id" class="course-card" @click="navigate('knowledge')"><div class="course-cover" :class="course.color"><span>{{ ['⌘','⌁','◉','▤','⌬','文'][index%6] }}</span><small>{{ course.credits }} 学分</small></div><h3>{{ course.name }}</h3><p>{{ course.teacher }} · {{ course.room }}</p><div class="course-progress"><span>{{ weekdays[course.weekday-1] }} {{ course.start_time }}</span><span>{{ course.weeks }}</span></div></article><div v-if="!visibleCourses.length" class="empty-state">还没有课程安排。</div></div></section></template>
        <!-- 作业与考试：查看截止日期并标记任务完成。 -->
        <template v-else-if="page==='tasks'"><div class="page-heading"><div><p class="eyebrow">KEEP YOUR LEARNING ON TRACK</p><h1>作业与考试</h1><p class="subheading">所有截止日期都在这里，安排好你的学习计划。</p></div><el-button type="primary" @click="taskDialog=true"><Plus :size="15"/> 添加任务</el-button></div><div class="task-cards"><div class="card task-summary"><span>全部任务</span><strong>{{ dashboard.tasks.length }}</strong><small>个人课程任务</small></div><div class="card task-summary"><span>待完成</span><strong>{{ dashboard.tasks.filter(t=>!t.completed).length }}</strong><small>记得按时完成</small></div><div class="card task-summary"><span>本周截止</span><strong>{{ dashboard.tasks.filter(t=>!t.completed&&t.days_left>=0&&t.days_left<=7).length }}</strong><small>最近任务优先处理</small></div></div><section class="card wide-card task-table"><div class="section-head"><div><h2>近期任务</h2><small>按截止时间排序</small></div></div><div v-for="task in dashboard.tasks" :key="task.id" class="task-list-row"><button class="task-check" :class="{checked:task.completed}" @click="toggleTask(task)"><Check :size="12"/></button><div class="task-date"><b>{{ formatDate(task.due_date).slice(-2) }}</b>{{ formatDate(task.due_date).slice(0,2) }}月</div><div class="task-main"><b :class="{strikethrough:task.completed}">{{ task.title }}</b><small>{{ task.course_name }} · 截止 {{ formatDate(task.due_date) }}</small></div><span class="task-kind">{{ task.kind }}</span><span class="status-pill" :class="task.completed?'done':''">{{ task.completed?'已完成':task.days_left<0?'已逾期':task.days_left===0?'今天截止':`${task.days_left} 天后` }}</span></div><div v-if="!dashboard.tasks.length" class="empty-state">暂时没有任务安排。添加一项试试。</div></section></template>
        <!-- 学习计划：集中查看已保存的学习安排。 -->
        <template v-else-if="page==='plans'"><div class="page-heading"><div><p class="eyebrow">PLAN WITH INTENTION</p><h1>学习计划</h1><p class="subheading">你和 AI 一起整理的学习安排，会保存在这里。</p></div><el-button type="primary" @click="ask('帮我制定并保存本周学习计划')"><Sparkles :size="15"/> 让 AI 帮我规划</el-button></div><div class="plan-list"><article v-for="plan in dashboard.plans" :key="plan.id" class="card plan-row"><div class="plan-icon"><Check :size="16"/></div><div><h3>{{ plan.title }}</h3><div class="plan-content">{{ plan.content }}</div><small class="muted">创建于 {{ new Date(plan.created_at).toLocaleDateString('zh-CN') }}<span v-if="plan.due_date"> · 目标日期 {{ formatDate(plan.due_date) }}</span></small></div></article><div v-if="!dashboard.plans?.length" class="card empty-state plan-empty"><span class="ai-spark"><Sparkles/></span><b>还没有保存的学习计划</b><p>告诉助手你的目标，它会帮你生成并保存计划。</p><el-button type="primary" plain @click="ask('帮我制定并保存本周学习计划')">开始规划</el-button></div></div></template>
        <!-- 课程问答：查看 AI 回复和工具调用过程。 -->
        <template v-else-if="page==='chat'"><div class="page-heading compact-heading"><div><p class="eyebrow">COURSE COPILOT</p><h1>课程问答</h1><p class="subheading">基于你的课表与课程资料，获得有依据的学习解答。</p></div></div><div class="chat-layout"><section class="card chat-panel"><div class="chat-title"><span class="ai-spark"><Sparkles :size="16"/></span><div><b>知课 AI 助手</b><small>{{ dashboard.stats.documents || 0 }} 份课程资料 · 个人数据已隔离</small></div><span class="online">在线</span></div><div class="chat-messages" ref="chatScroller"><div v-if="!messages.length" class="welcome-message"><div class="welcome-mark"><Sparkles :size="20"/></div><h3>你好，{{ firstName }}</h3><p>我是你的课程学习助手。我可以查你的课表、根据课程资料回答问题，也能帮你规划并保存学习计划。</p><div class="chat-suggestions"><button @click="ask('这周我的课表是什么？')"><CalendarDays/>查一下这周我的课表</button><button @click="ask('帮我总结数据结构课程重点')"><BookOpen/>帮我总结课程重点</button><button @click="ask('帮我制定并保存本周学习计划')"><Check/>制定并保存学习计划</button></div></div><div v-for="(message,index) in messages" :key="index" class="message" :class="message.role"><div class="message-avatar">{{ message.role==='user'?firstName.slice(0,1):'✳' }}</div><div class="message-body"><div v-if="message.role==='assistant'&&message.events.length" class="tool-timeline"><div v-for="(event,eventIndex) in message.events.filter(e=>e.kind==='tool_start')" :key="eventIndex" class="tool-event"><span class="tool-event-icon"><Check v-if="message.events.some(e=>e.kind==='tool_result'&&e.name===event.name)" :size="12"/><span v-else class="tool-pulse"></span></span><span>{{ event.label }}</span><small>{{ event.input?.query || '' }}</small></div></div><div v-if="message.thinking" class="bubble thinking"><span class="typing-dots"><i></i><i></i><i></i></span>{{ message.status || '正在整理回答' }}</div><div v-if="message.content" :class="['bubble',message.role==='assistant'?'ai-answer':'']" style="white-space:pre-wrap">{{ message.content }}</div><div v-if="message.error" class="bubble error-bubble">{{ message.error }}</div></div></div><div v-if="busy" class="stream-state"><span class="stream-dot"></span>助手正在处理你的问题</div></div><form class="chat-compose" @submit.prevent="sendMessage()"><input v-model="chatInput" placeholder="输入你的课程问题..." :disabled="busy"/><span class="compose-hint">Enter 发送</span><button class="send-btn" :disabled="busy||!chatInput.trim()"><ArrowUp :size="16"/></button></form><div class="privacy-note">AI 回答基于当前账户可访问的课程数据和资料</div></section><aside class="card chat-side"><h3>你可以问</h3><button class="suggestion" @click="ask('这周我的课表是什么？')">这周我有哪些课程？</button><button class="suggestion" @click="ask('帮我总结数据结构课程重点')">总结数据结构课程重点</button><button class="suggestion" @click="ask('TCP 和 UDP 有什么区别？')">TCP 和 UDP 有什么区别？</button><button class="suggestion" @click="ask('帮我制定并保存本周学习计划')">帮我保存一份学习计划</button><div class="side-divider"></div><h3>智能助手能做什么</h3><div class="capability"><CalendarDays/><span><b>查本人课表</b><small>仅访问当前账户有权限的数据</small></span></div><div class="capability"><LibraryBig/><span><b>课程资料问答</b><small>检索课程知识库并附资料来源</small></span></div><div class="capability"><Check/><span><b>保存学习计划</b><small>生成后保存至你的个人空间</small></span></div></aside></div></template>
        <!-- 智能知识库：管理员上传资料，学生查看有权限的资料。 -->
        <template v-else-if="page==='knowledge'"><div class="page-heading"><div><p class="eyebrow">YOUR COURSE KNOWLEDGE</p><h1>智能知识库</h1><p class="subheading">课程资料由管理员维护，问答时会按你的选课权限检索。</p></div><el-button v-if="user.role==='admin'" type="primary" @click="uploadInput?.click()"><Upload :size="15"/> 上传资料</el-button></div><div class="kb-stats"><div class="card"><strong>{{ documents.length }}</strong><small>份可访问资料</small></div><div class="card"><strong>{{ dashboard.stats.courses || 0 }}</strong><small>门已选课程</small></div><div class="card"><strong>RAG</strong><small>语义检索问答</small></div></div><section class="card wide-card"><div v-if="user.role==='admin'"><div class="upload-course"><span>资料所属课程</span><el-select v-model="uploadCourseId" clearable placeholder="共享资料（所有学生可访问）" size="small"><el-option v-for="course in courseOptions" :key="course.id" :label="course.name" :value="course.id"/></el-select></div><div class="upload-zone" @click="uploadInput?.click()" @dragover.prevent @drop.prevent="uploadFiles($event.dataTransfer.files)"><Upload :size="20"/><b>点击上传或拖拽资料到这里</b><span>PDF、DOCX、PPTX、TXT，单个文件最大 20MB</span></div></div><div v-else class="access-note"><LibraryBig :size="16"/> 学生账户仅可访问已选课程资料；资料由管理员上传与维护。</div><div class="section-head document-heading"><div><h2>可访问资料</h2><small>资料检索范围受课程权限控制</small></div><label class="search-field"><Search :size="15"/><input v-model="docSearch" placeholder="搜索资料名称..."/></label></div><div v-for="doc in visibleDocuments" :key="doc.id" class="document-row"><span class="file-icon">{{ fileIcon(doc.filename) }}</span><div class="document-name"><b>{{ doc.filename }}</b><small>{{ doc.characters.toLocaleString() }} 字符 · {{ new Date(doc.created_at).toLocaleDateString('zh-CN') }}</small></div><span class="status-pill done">已入库</span></div><div v-if="!visibleDocuments.length" class="empty-state">{{ user.role==='admin'?'还没有资料，上传课件即可建立课程知识库。':'当前选课范围内暂无资料，请联系管理员维护。' }}</div></section><input ref="uploadInput" type="file" hidden multiple accept=".pdf,.docx,.pptx,.txt" @change="uploadFiles($event.target.files)"/></template>
        <!-- 管理后台：维护用户角色、选课权限和课程资料。 -->
        <template v-else-if="page==='admin'"><div class="page-heading"><div><p class="eyebrow">ADMIN CONSOLE</p><h1>管理后台</h1><p class="subheading">维护用户、选课权限和课程资料入库。</p></div><el-button type="primary" @click="uploadInput?.click()"><Upload :size="15"/> 上传课程资料</el-button></div><div class="admin-grid"><section class="card wide-card"><div class="section-head"><div><h2>用户管理</h2><small>{{ users.length }} 个账户</small></div></div><div v-for="row in users" :key="row.id" class="user-row"><div class="avatar avatar-blue">{{ row.display_name.slice(0,1) }}</div><div class="document-name"><b>{{ row.display_name }}</b><small>{{ row.username }} · {{ row.department }}</small></div><el-select v-if="row.role==='student'" v-model="row.course_ids" multiple collapse-tags size="small" class="access-select" placeholder="分配课程" @change="saveCourseAccess(row)"><el-option v-for="course in courseOptions" :key="course.id" :label="course.name" :value="course.id"/></el-select><el-tag size="small" :type="row.role==='admin'?'warning':'info'">{{ row.role==='admin'?'管理员':'学生' }}</el-tag><el-button v-if="row.id!==user.id" text type="primary" @click="changeRole(row)">{{ row.role==='admin'?'设为学生':'设为管理员' }}</el-button></div></section><section class="card wide-card"><div class="section-head"><div><h2>资料入库</h2><small>{{ documents.length }} 份资料可用</small></div></div><div class="upload-course"><span>资料所属课程</span><el-select v-model="uploadCourseId" clearable placeholder="共享资料（所有学生可访问）" size="small"><el-option v-for="course in courseOptions" :key="course.id" :label="course.name" :value="course.id"/></el-select></div><div class="upload-zone small-upload" @click="uploadInput?.click()"><Upload :size="19"/><b>上传课程资料</b><span>PDF / DOCX / PPTX / TXT</span></div><div v-for="doc in documents.slice(0,4)" :key="doc.id" class="document-row"><span class="file-icon">{{ fileIcon(doc.filename) }}</span><div class="document-name"><b>{{ doc.filename }}</b><small>{{ doc.characters.toLocaleString() }} 字符</small></div></div></section></div><input ref="uploadInput" type="file" hidden multiple accept=".pdf,.docx,.pptx,.txt" @change="uploadFiles($event.target.files)"/></template>
      </div>
    </main>
    <el-dialog v-model="taskDialog" title="添加学习任务" width="430px"><el-form label-position="top"><el-form-item label="任务名称"><el-input v-model="taskForm.title" placeholder="例如：完成数据结构编程作业"/></el-form-item><el-form-item label="课程"><el-select v-model="taskForm.course_id" placeholder="选择所属课程" clearable style="width:100%"><el-option v-for="course in dashboard.courses" :key="course.id" :label="course.name" :value="course.id"/></el-select></el-form-item><div class="dialog-row"><el-form-item label="类型"><el-select v-model="taskForm.kind"><el-option label="作业" value="作业"/><el-option label="考试" value="考试"/><el-option label="实验报告" value="实验报告"/></el-select></el-form-item><el-form-item label="截止日期"><el-date-picker v-model="taskForm.due_date" value-format="YYYY-MM-DD" type="date" placeholder="选择日期"/></el-form-item></div></el-form><template #footer><el-button @click="taskDialog=false">取消</el-button><el-button type="primary" :disabled="!taskForm.title||!taskForm.due_date" @click="createTask">保存任务</el-button></template></el-dialog>
    <Transition><div v-if="toast" class="toast"><Check :size="14"/>{{ toast }}</div></Transition>
  </div>
</template>
