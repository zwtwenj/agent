import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
    state: () => {
        return {
            history: [
                { role: 'system', content: 'aaaaaa' },
                { role: 'user', id: 1, content: '11111', time: '2026-02-11 10:00:00' },
                { role: 'self', id: 2, content: '22222', time: '2026-02-11 11:00:00' }
            ],
            member: {
                system: { id: 0, name: '系统' },
                1: { id: 1, name: '小明' },
                2: { id: 2, name: '小红' },
            }
        }
    },
    actions: {
        invoke(content) {
            
        }
    }
})