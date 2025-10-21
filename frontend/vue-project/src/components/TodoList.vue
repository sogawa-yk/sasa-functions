<script setup>
import TodoItem from './TodoItem.vue'

defineProps({
  tasks: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update-task', 'delete-task'])
</script>

<template>
  <div class="todo-list">
    <div class="list-header">
      <h2>タスク一覧</h2>
      <div class="task-count">
        {{ tasks.length }}件のタスク
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>タスクを読み込み中...</p>
    </div>

    <div v-else-if="tasks.length === 0" class="empty-state">
      <div class="empty-icon">📝</div>
      <p>まだタスクがありません</p>
      <p class="empty-subtitle">上のフォームから新しいタスクを追加してください</p>
    </div>

    <div v-else class="tasks-container">
      <TodoItem
        v-for="task in tasks"
        :key="task.task_id"
        :task="task"
        @update-task="$emit('update-task', $event)"
        @delete-task="$emit('delete-task', $event)"
      />
    </div>
  </div>
</template>

<style scoped>
.todo-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.list-header {
  background: #f8f9fa;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.task-count {
  color: #6c757d;
  font-size: 0.9rem;
}

.loading {
  padding: 3rem;
  text-align: center;
  color: #6c757d;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #6c757d;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-subtitle {
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.tasks-container {
  max-height: 600px;
  overflow-y: auto;
}
</style>
