<script setup>
import {
  ArrowUp,
  BookOpen,
  CalendarDays,
  Check,
  LibraryBig,
  Sparkles,
  Trash2,
} from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'
import { useDashboard } from '../composables/useDashboard'
import { clearChat, useChat } from '../composables/useChat'

const { firstName } = useAuth()
const { dashboard } = useDashboard()
const { chatInput, messages, chatScroller, busy, sendMessage, ask } = useChat()
</script>

<template>
  <div class="page-heading compact-heading">
    <div>
      <p class="eyebrow">COURSE COPILOT</p>
      <h1>课程问答</h1>
      <p class="subheading">基于你的课表与课程资料，获得有依据的学习解答。</p>
    </div>
  </div>

  <div class="chat-layout">
    <section class="card chat-panel">
      <div class="chat-title">
        <span class="ai-spark"><Sparkles :size="16" /></span>
        <div>
          <b>知课 AI 助手</b>
          <small>记住最近 6 轮对话 · 刷新页面后清空</small>
        </div>
        <span class="online">在线</span>
        <button
          v-if="messages.length"
          class="clear-chat-button"
          type="button"
          title="清空本次对话记忆"
          @click="clearChat"
        >
          <Trash2 :size="14" />
          <span>清空对话</span>
        </button>
      </div>

      <div class="chat-messages" ref="chatScroller">
        <div v-if="!messages.length" class="welcome-message">
          <div class="welcome-mark"><Sparkles :size="20" /></div>
          <h3>你好，{{ firstName }}</h3>
          <p>我是你的课程学习助手。我可以查你的课表、根据课程资料回答问题，也能帮你规划并保存学习计划。</p>
          <div class="chat-suggestions">
            <button @click="ask('这周我的课表是什么？')"><CalendarDays />查一下这周我的课表</button>
            <button @click="ask('帮我总结数据结构课程重点')"><BookOpen />帮我总结课程重点</button>
            <button @click="ask('帮我制定并保存本周学习计划')"><Check />制定并保存学习计划</button>
          </div>
        </div>

        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message"
          :class="message.role"
        >
          <div class="message-avatar">{{ message.role === 'user' ? firstName.slice(0, 1) : '✳' }}</div>
          <div class="message-body">
            <div
              v-if="message.role === 'assistant' && message.events.length"
              class="tool-timeline"
            >
              <div
                v-for="(event, eventIndex) in message.events.filter((e) => e.kind === 'tool_start')"
                :key="eventIndex"
                class="tool-event"
              >
                <span class="tool-event-icon">
                  <Check
                    v-if="message.events.some((e) => e.kind === 'tool_result' && e.name === event.name)"
                    :size="12"
                  />
                  <span v-else class="tool-pulse"></span>
                </span>
                <span>{{ event.label }}</span>
                <small>{{ event.input?.query || '' }}</small>
              </div>
            </div>

            <div v-if="message.thinking" class="bubble thinking">
              <span class="typing-dots"><i></i><i></i><i></i></span>
              {{ message.status || '正在整理回答' }}
            </div>
            <div
              v-if="message.content"
              :class="['bubble', message.role === 'assistant' ? 'ai-answer' : '']"
              style="white-space: pre-wrap"
            >
              {{ message.content }}
            </div>
            <div v-if="message.error" class="bubble error-bubble">{{ message.error }}</div>
          </div>
        </div>

        <div v-if="busy" class="stream-state">
          <span class="stream-dot"></span>助手正在处理你的问题
        </div>
      </div>

      <form class="chat-compose" @submit.prevent="sendMessage()">
        <input v-model="chatInput" placeholder="输入你的课程问题..." :disabled="busy" />
        <span class="compose-hint">Enter 发送</span>
        <button class="send-btn" :disabled="busy || !chatInput.trim()"><ArrowUp :size="16" /></button>
      </form>
      <div class="privacy-note">AI 回答基于当前账户可访问的课程数据和资料</div>
    </section>

    <aside class="card chat-side">
      <h3>你可以问</h3>
      <button class="suggestion" @click="ask('这周我的课表是什么？')">这周我有哪些课程？</button>
      <button class="suggestion" @click="ask('帮我总结数据结构课程重点')">总结数据结构课程重点</button>
      <button class="suggestion" @click="ask('TCP 和 UDP 有什么区别？')">TCP 和 UDP 有什么区别？</button>
      <button class="suggestion" @click="ask('帮我制定并保存本周学习计划')">帮我保存一份学习计划</button>
      <div class="side-divider"></div>
      <h3>智能助手能做什么</h3>
      <div class="capability"><CalendarDays /><span><b>查本人课表</b><small>仅访问当前账户有权限的数据</small></span></div>
      <div class="capability"><LibraryBig /><span><b>课程资料问答</b><small>检索课程知识库并附资料来源</small></span></div>
      <div class="capability"><Check /><span><b>保存学习计划</b><small>生成后保存至你的个人空间</small></span></div>
    </aside>
  </div>
</template>
