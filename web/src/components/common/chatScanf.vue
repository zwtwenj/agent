<!--用户输入-->
<script setup>
import { ref } from 'vue'

const input = ref('')
</script>

<template>
    <div class="chat-scanf">
        <div class="chat-scanf-input">
            <input type="text" v-model="input" />
        </div>
        <div class="chat-scanf-send">
            <button @click="send">发送</button>
        </div>
    </div>
</template>

<style scoped lang="less">
.chat-scanf{
    display: flex;
    .chat-scanf-input{
        flex: 1;
    }
    .chat-scanf-send{
        flex: 1;
    }
}
</style>