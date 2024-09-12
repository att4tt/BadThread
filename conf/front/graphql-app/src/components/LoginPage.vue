<template>
    <div class="login-content">
        <h2>ログイン</h2>
        <form @submit.prevent="handleLogin">
            <div class="form-class">
                <label for="email">email: </label>
                <input type="text" id="email" v-model="email" required />
            </div>
            <div class="form-class">
                <label for="password">password: </label>
                <input type="password" id="password" v-model="password" required />
            </div>
            <button type="submit">ログイン</button>
        </form>
        <p v-if="result" class="error">{{ result }}</p>
    </div>
</template>

<script>
import { GraphQLClient, gql } from 'graphql-request';

export default {
    name: 'LoginPage',
    data() {
        return {
        email: '',
        password: '',
        result: ''
        }
    },
    methods: {
        async handleLogin() {
        if (this.email && this.password) {
            const client = new GraphQLClient('http://127.0.0.1:8888/graphql');
            const mutation = gql`mutation login($email: String!, $password: String!) {
                login(email: $email, password: $password) {
                    status
                    tmpToken
                    accessToken
                }
            }`;
            try {
            const variables = {
                email: this.email,
                password: this.password
            };
            const response = await client.request(mutation, variables);
            
            if(response.login.status === "success" && response.login.accessToken){
                sessionStorage.setItem('accesstoken', response.login.accessToken);
                this.$router.push('/');
            }else if(response.login.status === "success" && response.login.tmpToken){
                sessionStorage.setItem('tmptoken', response.login.tmpToken);
                this.$router.push('/otp');
            }else{
                this.result = "ログインに失敗しました";
            }

            } catch (error) {
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

.error {
  color: red;
  margin-top: 10px;
}
</style>