<template>
    <div class="login-content">
        <h2>2段階認証</h2>
        <div>管理者宛に通知された数値4桁の確認コードを入力してください（有効期限は3分です）</div>

        <form @submit.prevent="handleOpt">
            <div class="form-class">
                <label for="code">確認コード: </label>
                <input type="text" id="code" v-model="code" maxlength="4" pattern="\d{4}" required />
            </div>
            <button type="submit">送信する</button>
        </form>
        <p v-if="result" class="error">{{ result }}</p>
    </div>
</template>

<script>
import { GraphQLClient, gql } from 'graphql-request';

export default {
    name: 'OtpPage',
    data() {
        return {
        code: '',
        result: ''
        }
    },
    methods: {
        async handleOpt() {
        if (this.code) {
            const token = sessionStorage.getItem('tmptoken');
            const client = new GraphQLClient('http://127.0.0.1:8888/graphql', {headers: {Authorization: `Bearer ${token}`}});
            const mutation = gql`mutation loginotp($code: String!) {
                loginotp(code: $code) {
                    status
                    accessToken
                }
            }`;
            try {
            const variables = {
                code: this.code
            };
            const response = await client.request(mutation, variables);
            
            if(response.loginotp.status === "success" && response.loginotp.accessToken){
                sessionStorage.removeItem('tmptoken');
                sessionStorage.setItem('accesstoken', response.loginotp.accessToken);
                this.$router.push('/');
            }else{
                this.result = "認証コードが違います";
            }

            } catch (error) {
            this.result = 'エラーです: ' + (error.response?.errors?.[0]?.message);
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