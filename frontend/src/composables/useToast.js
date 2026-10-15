import { ref } from 'vue'

const toast = ref('')
let toastTimer

// 显示短暂提示，并清理上一次提示的计时器。
export function notify(message) {
  toast.value = message
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.value = ''
  }, 2600)
}

// 组件中通过此函数获取共享的提示状态。
export function useToast() {
  return { toast, notify }
}
