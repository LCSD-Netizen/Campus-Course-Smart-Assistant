import { nextTick, ref, watch } from 'vue'
import router from '../router'
import { errorMessage } from '../api/client'
import { loadDashboard } from './useDashboard'

// 课程问答和 SSE 流式响应状态。
const chatInput = ref('')
const messages = ref([])
const activeTools = ref([])
const chatScroller = ref(null)
const busy = ref(false)

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

export function useChat() {
  // 提交问题，读取 SSE 响应并实时追加 AI 回复。
  async function sendMessage(value = chatInput.value) {
    const prompt = value.trim()
    if (!prompt || busy.value) return

    // 只回传最近 12 条已完成的普通消息，不包含工具调用过程和临时状态。
    const history = messages.value
      .filter(
        (message) =>
          message.role === 'user' ||
          (message.role === 'assistant' && message.done && message.content),
      )
      .slice(-12)
      .map(({ role, content }) => ({ role, content }))

    chatInput.value = ''
    router.push({ name: 'chat' })
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
          Authorization: `Bearer ${localStorage.getItem('campus-token')}`,
        },
        body: JSON.stringify({ message: prompt, history }),
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

  return {
    chatInput,
    messages,
    activeTools,
    chatScroller,
    busy,
    sendMessage,
    ask,
  }
}

// 清空当前会话的聊天记录，退出登录或切换账户时调用。
export function clearChat() {
  messages.value = []
  activeTools.value = []
}
