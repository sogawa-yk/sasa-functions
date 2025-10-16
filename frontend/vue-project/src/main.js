import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'

console.log('main.js loaded')

try {
  const app = createApp(App)
  console.log('Vue app created')
  app.mount('#app')
  console.log('Vue app mounted')
} catch (error) {
  console.error('Error mounting Vue app:', error)
  document.getElementById('app').innerHTML = `
    <div style="text-align: center; padding: 2rem; color: #c33;">
      <h2>❌ アプリの読み込みに失敗しました</h2>
      <p>エラー: ${error.message}</p>
      <pre style="background: #f5f5f5; padding: 1rem; border-radius: 4px; text-align: left; max-width: 600px; margin: 1rem auto;">${error.stack}</pre>
    </div>
  `
}
