<script setup>
import { ref, onMounted } from "vue";
import TodoList from "./components/TodoList.vue";
import TodoForm from "./components/TodoForm.vue";
import taskAPI from "./services/api.js";

const tasks = ref([]);
const loading = ref(false);
const error = ref("");

// タスク一覧を取得
const fetchTasks = async () => {
  loading.value = true;
  error.value = "";
  try {
    tasks.value = await taskAPI.getTasks();
  } catch (err) {
    error.value = err.message || "タスクの取得に失敗しました";
    console.error("API Error:", err);
  } finally {
    loading.value = false;
  }
};

// タスク追加
const addTask = async (taskData) => {
  try {
    const newTask = await taskAPI.addTask(taskData);
    tasks.value.push(newTask);
  } catch (err) {
    error.value = err.message || "タスクの追加に失敗しました";
  }
};

// タスク更新
const updateTask = async (eventData) => {
  console.log("updateTask called with eventData:", eventData);
  const { taskId, updates } = eventData;
  console.log("Extracted taskId:", taskId, "updates:", updates);
  try {
    const updatedTask = await taskAPI.updateTask(taskId, updates);
    const index = tasks.value.findIndex((task) => task.task_id === taskId);
    if (index !== -1) {
      tasks.value[index] = updatedTask;
    }
  } catch (err) {
    error.value = err.message || "タスクの更新に失敗しました";
  }
};

// タスク削除
const deleteTask = async (taskId) => {
  console.log("deleteTask called with taskId:", taskId);
  try {
    await taskAPI.deleteTask(taskId);
    tasks.value = tasks.value.filter((task) => task.task_id !== taskId);
  } catch (err) {
    error.value = err.message || "タスクの削除に失敗しました";
  }
};

onMounted(() => {
  fetchTasks();
});
</script>

<template>
  <div id="app">
    <header>
      <h1>📝 ToDo アプリ</h1>
    </header>

    <main>
      <div v-if="error" class="error-message">
        {{ error }}
        <button @click="error = ''" class="close-btn">×</button>
      </div>

      <TodoForm @add-task="addTask" />

      <TodoList
        :tasks="tasks"
        :loading="loading"
        @update-task="updateTask"
        @delete-task="deleteTask"
      />
    </main>
  </div>
</template>

<style scoped>
#app {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

header {
  text-align: center;
  margin-bottom: 2rem;
}

h1 {
  color: #2c3e50;
  margin: 0;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #c33;
}
</style>
