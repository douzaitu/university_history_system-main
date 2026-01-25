import axios from "axios";

// 创建axios实例
const service = axios.create({
  baseURL: "http://localhost:8000/api/", // 改回8000端口
  timeout: 15000,
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default service;
