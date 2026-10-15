// 模板格式化辅助函数。

// 将日期字符串格式化为「月/日」形式，缺失时给出占位文案。
export function formatDate(value) {
  if (!value) return '未设置'
  return new Date(`${value}T00:00:00`).toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
  })
}

// 根据文件扩展名返回用于展示的图标文字。
export function fileIcon(filename) {
  return filename.split('.').pop()?.toUpperCase() || '文件'
}
