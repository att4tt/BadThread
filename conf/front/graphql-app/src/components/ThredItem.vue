<template>
  <div class="thred-item">
    <h3>タイトル:{{ title }}</h3>
    <p><strong>ユーザ名:</strong> {{ author }}</p>
    <p>{{ detail }}</p>
  </div>
</template>

<script>
export default {
  name: 'ThredItem',
  props: {
    title: String,
    author: String,
    detail: String
  }
}
</script>

<style scoped>
.thred-item {
  border: 1px solid #ddd;
  padding: 10px;
  margin: 10px 0;
}
</style>