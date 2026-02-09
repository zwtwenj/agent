<script setup>
import { ref } from 'vue';
import { onMounted } from 'vue';
import { getUserChatHistory, addUserChatHistory, getTime } from '@/api/index.ts';
import dayjs from 'dayjs';

onMounted(() => {
    const params = {
        userId: 1000001,
        date: '2026-02-02'
    }
    getUserChatHistory(params).then(res => {
        console.log(res);
    });
    getTime().then(res => {
        console.log(res);
    });
});

const form = ref({
    userId: 1000001,
    time: '',
    text: ''
});

const submit = () => {
    const params = {
        ...form.value,
        date: dayjs(form.value.time).format('YYYY-MM-DD')
    }
    addUserChatHistory(params).then(res => {
        console.log(res);
    });
};
</script>

<template>
    <div class="app-container">
        <el-form>
            <el-form-item label="内容">
                <el-input v-model="form.text" type="textarea" />
            </el-form-item>
            <el-form-item label="时间">
                <el-date-picker type="datetime" v-model="form.time" format="YYYY-MM-DD HH:mm:ss" />
            </el-form-item>
        </el-form>
        <el-button type="primary" @click="submit">添加</el-button>
    </div>
</template>

<style scoped></style>
