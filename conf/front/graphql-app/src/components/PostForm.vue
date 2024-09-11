<template>
  <div class="post-form">
    <form @submit.prevent="submitPost">
      <div class="form-group">
        <label for="title">タイトル</label>
        <input
          type="text"
          id="title"
          v-model="title"
          required
        />
      </div>
      <div class="form-group">
        <label for="detail">本文</label>
        <textarea
          id="detail"
          v-model="detail"
          rows="4"
          required
        ></textarea>
      </div>
      <button type="submit">投稿</button>
    </form>
    <div v-if="result" class="result-txt" :class="resultstatus">
      {{ result }}
    </div>
  </div>
</template>

<script>
import { GraphQLClient, gql } from 'graphql-request';

export default {
  name: 'PostForm',
  data() {
    return {
      title: '',
      detail: '',
      result: '',
      resultstatus: ''
    }
  },
  methods: {
    async submitPost() {
      if (this.title && this.detail) {
        const token = sessionStorage.getItem('accesstoken');
        const client = new GraphQLClient('http://127.0.0.1:8888/graphql', {headers: {Authorization: `Bearer ${token}`}});
        const mutation = gql`mutation postMessage($title: String!, $message: String!) {
            postMessage(title: $title, message: $message) {
              status
              message
            }
          }`;
        try {
          const variables = {
            title: this.title,
            message: this.detail
          };
          await client.request(mutation, variables);
          this.result = `投稿が完了しました`;
          this.resultstatus = 'success';
          this.title = '';
          this.detail = '';
        } catch (error) {
          this.result = 'エラーです: ' + (error.response?.errors?.[0]?.message);
          this.resultstatus = 'error';
        }
      } else {
        alert('未入力箇所があります');
      }
    }
  }
}
</script>

<style scoped>
.post-form {
  margin-top: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input, textarea {
  width: 95%;
  padding: 10px;
  border: 1px solid #cccccc;
  border-radius: 20px;
}

button {
  padding: 10px 15px;
  background-color: #4800ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

.result-message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
}

.result-txt.success {
  padding: 5px;
  color: green;
  border: 1px solid green;
}

.result-txt.error {
  padding: 5px;
  color: red;
  border: 1px solid red;
}
</style>
