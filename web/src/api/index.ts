import axios from 'axios';

const request = axios.create({
    baseURL: 'http://localhost:5000/api',
    timeout: 5000
});

const agentRequest = axios.create({
    baseURL: 'http://localhost:5001/api',
    timeout: 5000
});

export default request;

export const getUserChatHistory = (data: { userId: number }) => {
    return request.post(`/user/chat/history`, data);
};


// 添加用户chat历史
interface AddUserChatHistoryParams {
    userId: number;
    time: string;
    text: string;
    date: string;
}
export const addUserChatHistory = (params: AddUserChatHistoryParams) => {
    return request.post(`/user/chat/history/add`, params);
};

export const getTime = () => {
    return agentRequest.post(`/get_time`);
};