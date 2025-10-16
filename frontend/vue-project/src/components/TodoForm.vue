<script setup>
import { ref } from 'vue'

const emit = defineEmits(['add-task'])

const title = ref('')
const description = ref('')
const isSubmitting = ref(false)

const submitTask = async () => {
  if (!title.value.trim()) return
  
  isSubmitting.value = true
  
  try {
    await emit('add-task', {
      title: title.value.trim(),
      description: description.value.trim()
    })
    
    // フォームをリセット
    title.value = ''
    description.value = ''
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="todo-form">
    <h2>新しいタスクを追加</h2>
    <form @submit.prevent="submitTask">
      <div class="form-group">
        <label for="title">タイトル *</label>
        <input
          id="title"
          v-model="title"
          type="text"
          placeholder="タスクのタイトルを入力..."
          required
          :disabled="isSubmitting"
        />
      </div>
      
      <div class="form-group">
        <label for="description">説明</label>
        <textarea
          id="description"
          v-model="description"
          placeholder="タスクの詳細を入力..."
          :disabled="isSubmitting"
        ></textarea>
      </div>
      
      <button 
        type="submit" 
        :disabled="!title.trim() || isSubmitting"
        class="submit-btn"
      >
        {{ isSubmitting ? '追加中...' : 'タスクを追加' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.todo-form {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

h2 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

input,
textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

textarea {
  min-height: 80px;
  resize: vertical;
  font-family: inherit;
}

.submit-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.submit-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
</style>
