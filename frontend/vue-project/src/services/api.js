/**
 * API管理インターフェース
 * 全てのAPI呼び出しを統一管理するためのサービスクラス
 */

class TaskAPI {
  constructor() {
    this.baseURL =
      "https://d2in2g7c2ijtcahoybn3xdxtpu.apigateway.uk-london-1.oci.customer-oci.com/v1";
    this.defaultHeaders = {
      "Content-Type": "application/json",
    };
  }

  /**
   * APIリクエストの基本処理
   * @param {string} endpoint - APIエンドポイント
   * @param {Object} options - fetchオプション
   * @returns {Promise<any>} レスポンスデータ
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(
          `HTTPエラー: ${response.status} ${response.statusText}`
        );
      }

      // レスポンスがJSONの場合のみパース
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return await response.json();
      }

      return response;
    } catch (error) {
      console.error(
        `API Request Error [${config.method || "GET"} ${url}]:`,
        error
      );
      throw error;
    }
  }

  /**
   * タスク一覧を取得
   * @returns {Promise<Array>} タスクの配列
   */
  async getTasks() {
    try {
      return await this.request("/tasks");
    } catch (error) {
      console.warn(
        "API呼び出しに失敗しました。サンプルデータを返します。",
        error
      );
      // API呼び出しに失敗した場合のフォールバックデータ
      return this.getFallbackTasks();
    }
  }

  /**
   * 新しいタスクを追加
   * @param {Object} taskData - 追加するタスクのデータ
   * @param {string} taskData.title - タスクのタイトル
   * @param {string} taskData.description - タスクの説明
   * @returns {Promise<Object>} 追加されたタスク
   */
  async addTask(taskData) {
    return await this.request("/tasks", {
      method: "POST",
      body: JSON.stringify(taskData),
    });
  }

  /**
   * タスクを更新
   * @param {string} taskId - 更新するタスクのID
   * @param {Object} updates - 更新データ
   * @param {string} updates.title - タスクのタイトル
   * @param {string} updates.description - タスクの説明
   * @param {boolean} updates.completed - 完了状態
   * @returns {Promise<Object>} 更新されたタスク
   */
  async updateTask(taskId, updates) {
    console.log("updateTask called with:", { taskId, updates });
    const endpoint = `/tasks?id=${taskId}`;
    console.log("Request URL will be:", `${this.baseURL}${endpoint}`);
    return await this.request(endpoint, {
      method: "PATCH",
      body: JSON.stringify(updates),
    });
  }

  /**
   * タスクを削除
   * @param {string} taskId - 削除するタスクのID
   * @returns {Promise<void>}
   */
  async deleteTask(taskId) {
    console.log("deleteTask called with taskId:", taskId);
    const endpoint = `/tasks?id=${taskId}`;
    console.log("Request URL will be:", `${this.baseURL}${endpoint}`);
    return await this.request(endpoint, {
      method: "DELETE",
    });
  }

  /**
   * API呼び出し失敗時のフォールバックデータ
   * @returns {Array} サンプルタスクの配列
   */
  getFallbackTasks() {
    return [
      {
        task_id: "sample-1",
        title: "サンプルタスク1",
        description: "これはテスト用のサンプルタスクです",
        created_at: new Date().toISOString(),
        completed: false,
      },
      {
        task_id: "sample-2",
        title: "サンプルタスク2",
        description: "完了済みのサンプルタスクです",
        created_at: new Date().toISOString(),
        completed: true,
      },
    ];
  }

  /**
   * APIベースURLを設定
   * @param {string} newBaseURL - 新しいベースURL
   */
  setBaseURL(newBaseURL) {
    this.baseURL = newBaseURL;
  }

  /**
   * デフォルトヘッダーを設定
   * @param {Object} headers - 設定するヘッダー
   */
  setDefaultHeaders(headers) {
    this.defaultHeaders = { ...this.defaultHeaders, ...headers };
  }

  /**
   * APIヘルスチェック
   * @returns {Promise<boolean>} APIが利用可能かどうか
   */
  async healthCheck() {
    try {
      await this.request("/health", { method: "GET" });
      return true;
    } catch (error) {
      console.warn("API health check failed:", error);
      return false;
    }
  }
}

// シングルトンインスタンスを作成してエクスポート
const taskAPI = new TaskAPI();

export default taskAPI;

// 個別の関数としてもエクスポート（コンポーザブルAPI用）
export const {
  getTasks,
  addTask,
  updateTask,
  deleteTask,
  setBaseURL,
  setDefaultHeaders,
  healthCheck,
} = taskAPI;
