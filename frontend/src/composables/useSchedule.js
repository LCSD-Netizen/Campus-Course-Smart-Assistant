import { computed, ref } from 'vue'
import { useDashboard } from './useDashboard'

export const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

const weekOffset = ref(0)
const selectedDate = ref(new Date())

// 根据周偏移量计算当前周周一至周日的日期。
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

export function useSchedule() {
  const { dashboard } = useDashboard()

  // 返回某一天（周一为索引 0）的课程列表。
  function dayCourses(dayIndex) {
    return dashboard.value.courses.filter(
      (course) => course.weekday === dayIndex + 1,
    )
  }

  return { weekdays, weekOffset, selectedDate, weekDays, dayCourses }
}
