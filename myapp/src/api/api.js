// src/api/api.js
import axios from "axios";

// Axios instance
const API = axios.create({
  baseURL: "http://127.0.0.1:8000/api/", // Django API ana URL
  timeout: 5000, // isteğe bağlı: uzun süren istekleri kesmek için
});

//  Request interceptor – access token otomatik eklenir
API.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem("access_token");
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor – token süresi dolmuşsa refresh yapar
API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        const res = await axios.post("http://127.0.0.1:8000/api/users/refresh/", {
          refresh: refreshToken,
        });

        const newAccessToken = res.data.access;
        localStorage.setItem("access_token", newAccessToken);

        // Güncellenmiş token’ı hem genel hem orijinal isteğe ekle
        API.defaults.headers.common["Authorization"] = `Bearer ${newAccessToken}`;
        originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;

        // İstek yeniden gönderilir
        return API(originalRequest);
      } catch (err) {
        // Refresh başarısızsa tokenları temizle ve login sayfasına at
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/signin";
      }
    }

    return Promise.reject(error);
  }
);

export default API;
