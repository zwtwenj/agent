<script setup>
import { computed } from 'vue'
import { useChatStore } from './index.store'
import Bubble from '@/components/common/bubble.vue'
import ChatScanf from '@/components/common/chatScanf.vue'

const chatStore = useChatStore()

const history = computed(() => chatStore.history)
</script>

<template>
    <div class="chat-container">
        <div class="chat-body">
            <div class="chat-item" v-for="item in history" :key="item.id">
                <!-- <div class="chat-item-content">{{ item.text }}</div> -->
                <Bubble :item="item" />
            </div>
        </div>
        <ChatScanf class="chat-scanf" />
    </div>
</template>

<style scoped>
.chat-container{
    position: relative;
}
</style>