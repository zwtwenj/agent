import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            redirect: '/chat'
        },
        {
            path: '/chat',
            component: () => import('@/views/chat/index.vue')
        }
    ],
})

export default router
