import { createRouter, createWebHistory } from 'vue-router';
import TopPage from './components/TopPage.vue';
import LoginPage from './components/LoginPage.vue';
import OtpPage from './components/OtpPage.vue';
import SignupPage from './components/SignupPage.vue';


const routes = [
    {path: '/', component: TopPage},
    {path: '/login', component: LoginPage},
    {path: '/otp', component: OtpPage},
    {path: '/signup', component: SignupPage}
];

const router = createRouter({history: createWebHistory(), routes});

export default router;