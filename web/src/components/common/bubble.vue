<script setup>
const props = defineProps({
    role: {
        type: String,
        default: '', // system, user
    },
    user: {
        type: Object,
        default: {
            id: 0,
            name: '111',
            avatar: '',
        }
    },
    position: {
        type: String,
        default: '', // left, right
    },
    // 内容
    content: {
        type: String,
        default: ''
    },
    // 时间
    time: {
        type: String,
        default: '2026-02-11 10:00'
    }
})
</script>

<template>
    <!--做一个对话气泡组件，根据position来决定气泡的位置-->
    <div class="bubble" :class="'bubble-' + position">
        <div class="bubble-avatar">
            <img src="https://avatars.githubusercontent.com/u/30250194?v=4&size=64" class="bubble-top-avatar">
            <!-- <img :src="user.avatar" class="bubble-top-avatar"> -->
        </div>
        <div class="bubble-content">
            <div class="bubble-user-info">
                <div class="bubble-top-name">{{ user.name }}</div>
                <!-- <div class="bubble-top-time">{{ time }}</div> -->
            </div>
            <div class="bubble-content-body">
                <div class="bubble-content-arrow"></div>
                <div class="bubble-content-text">
                    {{ content }}
                    21312312
                </div>
            </div>
        </div>
    </div>
</template>

<style lang="less" scoped>
.bubble{
    display: flex;
    .bubble-avatar{
        .bubble-top-avatar{
            display: block;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin-right: 10px;
            margin-top: 4px;
        }
    }
    .bubble-content{
        .bubble-user-info{
            display: flex;
            margin-bottom: 4px;
            .bubble-top-name{
                margin-right: 10px;
            }
        }
        .bubble-content-body{
            position: relative;
            .bubble-content-arrow{
                position: absolute;
                top: 0;
                left: -6px;
                width: 0;
                height: 0;
                border-top: 0px solid transparent;
                border-bottom: 8px solid transparent;
                border-right: 6px solid blue;
            }
            .bubble-content-text{
                background-color: blue;
                color: #fff;
                padding: 10px;
                border-radius: 10px;
                border-top-left-radius: 0;
            }
        }
    }
}
</style>