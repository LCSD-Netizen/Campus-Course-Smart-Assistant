<script setup>
import { useDashboard } from '../composables/useDashboard'

const { dashboard, taskDialog, taskForm, createTask } = useDashboard()
</script>

<template>
  <el-dialog v-model="taskDialog" title="添加学习任务" width="430px">
    <el-form label-position="top">
      <el-form-item label="任务名称">
        <el-input v-model="taskForm.title" placeholder="例如：完成数据结构编程作业" />
      </el-form-item>
      <el-form-item label="课程">
        <el-select
          v-model="taskForm.course_id"
          placeholder="选择所属课程"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="course in dashboard.courses"
            :key="course.id"
            :label="course.name"
            :value="course.id"
          />
        </el-select>
      </el-form-item>
      <div class="dialog-row">
        <el-form-item label="类型">
          <el-select v-model="taskForm.kind">
            <el-option label="作业" value="作业" />
            <el-option label="考试" value="考试" />
            <el-option label="实验报告" value="实验报告" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker
            v-model="taskForm.due_date"
            value-format="YYYY-MM-DD"
            type="date"
            placeholder="选择日期"
          />
        </el-form-item>
      </div>
    </el-form>
    <template #footer>
      <el-button @click="taskDialog = false">取消</el-button>
      <el-button
        type="primary"
        :disabled="!taskForm.title || !taskForm.due_date"
        @click="createTask"
      >
        保存任务
      </el-button>
    </template>
  </el-dialog>
</template>
