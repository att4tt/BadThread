<template>
    <div class="login-content">
        <h2>新規登録</h2>
        <form @submit.prevent="handleLogin">
            <div class="form-class">
                <label for="name">ユーザ名: </label>
                <input type="text" id="name" v-model="name" required />
            </div>
            <div class="form-class">
                <label for="email">email: </label>
                <input type="text" id="email" v-model="email" required />
            </div>
            <div class="form-class">
                <label for="password">password: </label>
                <input type="password" id="password" v-model="password" required minlength="8"/>
            </div>
            <button type="submit">登録する</button>
        </form>
        <p v-if="result === 'success'" class="success">{{ resultmes }}</p>
        <p v-else-if="result === 'error'" class="error">{{ resultmes }}</p>
    </div>
</template>

<script>
import { GraphQLClient, gql } from 'graphql-request';

export default {
    name: 'LoginPage',
    data() {
        return {
        name: '',
        email: '',
        password: '',
        result: '',
        resultmes: ''
        }
    },
    methods: {
        async handleLogin() {
        if (this.email && this.password) {
            const client = new GraphQLClient('http://127.0.0.1:8888/graphql');
            const mutation = gql`mutation registerUser($name: String!, $email: String!, $password: String!) {
                registerUser(name: $name, email: $email, password: $password) {
                    status
                    message
                }
            }`;

            this.result = '';
            this.resultmes = '';

            try {
            const variables = {
                name: this.name,
                email: this.email,
                password: this.password
            };
            const response = await client.request(mutation, variables);

            if(response.registerUser.status === 'success'){
                this.result = "success";
                this.resultmes = "登録完了しました";
                this.name = '';
                this.email = '';
                this.password = '';
            }else if(response.registerUser.status === 'error'){
                this.result = "error";
                this.resultmes = "登録内容に問題があります: " + response.registerUser.message;
            }

            } catch (error) {
                this.result = "error"
                this.resultmes = 'エラーです: ' + (error.response?.errors?.[0]?.message);
            }
        } else {
            alert('未入力箇所があります');
        }
        }
    }
};
</script>


<style scoped>
.login-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 20vh;
  padding: 20px;
}

.form-class {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
  max-width: 300px;
}

.success {
  color: rgb(0, 38, 255);
  margin-top: 10px;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>