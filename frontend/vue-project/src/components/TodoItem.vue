<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  task: {
    type: Object,
    required: true
  }
})

// タスクデータをデバッグ出力
console.log("TodoItem received task:", props.task);

const emit = defineEmits(['update-task', 'delete-task'])

const isEditing = ref(false)
const editTitle = ref('')
const editDescription = ref('')
const isUpdating = ref(false)

// 編集モードに入る
const startEdit = () => {
  editTitle.value = props.task.title
  editDescription.value = props.task.description
  isEditing.value = true
}

// 編集をキャンセル
const cancelEdit = () => {
  isEditing.value = false
  editTitle.value = ''
  editDescription.value = ''
}

// タスクを更新
const saveEdit = async () => {
  if (!editTitle.value.trim()) return
  
  isUpdating.value = true
  
  try {
    const eventData = {
      taskId: props.task.task_id,
      updates: {
        title: editTitle.value.trim(),
        description: editDescription.value.trim(),
        completed: props.task.completed
      }
    };
    console.log("TodoItem saveEdit emitting:", eventData);
    await emit('update-task', eventData)
    isEditing.value = false
  } finally {
    isUpdating.value = false
  }
}

// 完了状態を切り替え
const toggleComplete = async () => {
  isUpdating.value = true
  
  try {
    const eventData = {
      taskId: props.task.task_id,
      updates: {
        title: props.task.title,
        description: props.task.description,
        completed: !props.task.completed
      }
    };
    console.log("TodoItem toggleComplete emitting:", eventData);
    await emit('update-task', eventData)
  } finally {
    isUpdating.value = false
  }
}

// タスクを削除
const deleteTask = () => {
  if (confirm('このタスクを削除しますか？')) {
    console.log("TodoItem deleteTask emitting taskId:", props.task.task_id);
    emit('delete-task', props.task.task_id)
  }
}

// 作成日時をフォーマット
const formattedDate = computed(() => {
  const date = new Date(props.task.created_at)
  return date.toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})
</script>

<template>
  <div class="todo-item" :class="{ completed: task.completed }">
    <div class="task-content">
      <!-- 編集モード -->
      <div v-if="isEditing" class="edit-mode">
        <div class="edit-form">
          <input
            v-model="editTitle"
            type="text"
            placeholder="タイトル"
            class="edit-title"
            :disabled="isUpdating"
            @keyup.enter="saveEdit"
            @keyup.escape="cancelEdit"
          />
          <textarea
            v-model="editDescription"
            placeholder="説明"
            class="edit-description"
            :disabled="isUpdating"
          ></textarea>
          <div class="edit-actions">
            <button 
              @click="saveEdit" 
              :disabled="!editTitle.trim() || isUpdating"
              class="save-btn"
            >
              {{ isUpdating ? '保存中...' : '保存' }}
            </button>
            <button 
              @click="cancelEdit" 
              :disabled="isUpdating"
              class="cancel-btn"
            >
              キャンセル
            </button>
          </div>
        </div>
      </div>

      <!-- 表示モード -->
      <div v-else class="view-mode">
        <div class="task-header">
          <div class="checkbox-wrapper">
            <input
              type="checkbox"
              :checked="task.completed"
              @change="toggleComplete"
              :disabled="isUpdating"
              class="task-checkbox"
            />
          </div>
          <div class="task-info">
            <h3 class="task-title">{{ task.title }}</h3>
            <p v-if="task.description" class="task-description">
              {{ task.description }}
            </p>
            <div class="task-meta">
              <span class="created-date">{{ formattedDate }}</span>
              <span v-if="task.completed" class="completed-badge">完了</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- アクションボタン -->
    <div class="task-actions" v-if="!isEditing">
      <button 
        @click="startEdit" 
        :disabled="isUpdating"
        class="edit-btn"
        title="編集"
      >
        ✏️
      </button>
      <button 
        @click="deleteTask" 
        :disabled="isUpdating"
        class="delete-btn"
        title="削除"
      >
        🗑️
      </button>
    </div>
  </div>
</template>

<style scoped>
.todo-item {
  display: flex;
  align-items: flex-start;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  transition: background-color 0.3s;
}

.todo-item:hover {
  background-color: #f8f9fa;
}

.todo-item.completed {
  opacity: 0.7;
}

.task-content {
  flex: 1;
  min-width: 0;
}

.view-mode .task-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.checkbox-wrapper {
  margin-top: 0.25rem;
}

.task-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: #2c3e50;
  word-wrap: break-word;
}

.completed .task-title {
  text-decoration: line-through;
  color: #6c757d;
}

.task-description {
  margin: 0 0 0.75rem 0;
  color: #6c757d;
  line-height: 1.4;
  word-wrap: break-word;
}

.completed .task-description {
  text-decoration: line-through;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
}

.created-date {
  color: #6c757d;
}

.completed-badge {
  background-color: #28a745;
  color: white;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
}

.edit-mode .edit-form {
  width: 100%;
}

.edit-title {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  box-sizing: border-box;
}

.edit-description {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-height: 60px;
  margin-bottom: 0.75rem;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}

.edit-title:focus,
.edit-description:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
}

.save-btn,
.cancel-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.save-btn {
  background-color: #28a745;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background-color: #218838;
}

.save-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-btn:hover:not(:disabled) {
  background-color: #5a6268;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
  margin-left: 0.75rem;
}

.edit-btn,
.delete-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.1rem;
  transition: background-color 0.3s;
}

.edit-btn:hover:not(:disabled) {
  background-color: #e9ecef;
}

.delete-btn:hover:not(:disabled) {
  background-color: #f8d7da;
}

.edit-btn:disabled,
.delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
