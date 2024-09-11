<template>
  <div>
    <ThredItem
      v-for="(result, item) in results"
      :key="item"
      :title="result.title"
      :author="result.author.name"
      :detail="result.detail"
    />
  </div>
</template>

<script>
import { GraphQLClient, gql } from 'graphql-request';
import ThredItem from './ThredItem.vue';

export default {
  name: 'ThredDev',
  components: {
    ThredItem
  },
  data() {
    return {
      results: []
    }
  },
  async created() {
    const token = sessionStorage.getItem('accesstoken');
    const client = new GraphQLClient('http://127.0.0.1:8888/graphql', {headers: {Authorization: `Bearer ${token}`}});
    const query = gql`query thread{
        thread {
          title
          detail
          author {
            name
          }
        }
      }`;
    try {
      const data = await client.request(query);
      this.results = data.thread;
    } catch (error) {
      console.error("error")
    }
  }
}
</script>