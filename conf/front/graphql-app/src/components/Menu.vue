<template>
    <nav class="menu">
        <ul>
            <li>
                <router-link to="/">TOP</router-link>
            </li>
            <br>
            <li>
                <a href="" v-if="loginstatus" @click="logout">Logout</a>
                <router-link v-if="!loginstatus" to="/login">Login</router-link>
                <br>
                <router-link v-if="!loginstatus" to="/signup">Signup</router-link>
            </li>
        </ul>
    </nav>

    <main>
        <router-view></router-view>
    </main>
    
</template>

<script>
export default {
    name: 'HeaderName',
    data() {
        return {
            loginstatus: ''
        };
    },
    mounted(){
        this.loginstatus = sessionStorage.getItem('accesstoken');
    },
    watch: {
        '$route'() {
            this.loginstatus = sessionStorage.getItem('accesstoken');
        }
    },
    methods: {
        logout(){
            sessionStorage.removeItem('accesstoken');
            this.$router.push('/');
            this.loginstatus = sessionStorage.getItem('accesstoken');
        }
    }
};

</script>

<style scoped>
.menu li {
    display: inline;
  }
</style>
