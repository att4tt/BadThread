<template>
    <p v-if="flashMessage">{{ flashMessage }}</p>
    <main>
        <ThreadDev />
        <PostForm />
    </main>
</template>
  
  <script>
  import ThreadDev from './ThreadDev.vue';
  import PostForm from './PostForm.vue';
  
  export default {
    name: 'TopPage',
    components: {
        ThreadDev,
        PostForm
    }
  };
  </script>

<style scoped>
p {
  color: rgb(81, 0, 255);
  font-weight: bold;
}
</style>