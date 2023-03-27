import axios from 'axios'
import { Notification } from 'element-ui'

// 配置优先级： 全局配置 < 实例配置 < 请求的config参数
// 全局axios默认值配置
axios.defaults.baseURL = 'http://127.0.0.1:8000/'
axios.defaults.timeout = 5000 // 设置请求延迟时间
axios.defaults.headers.post['Content-Type'] = 'multipart/form-data'
axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*'
axios.defaults.withCredentials = false // 允许跨域请求携带cookie做身份认证

/* 添加拦截器 */
// request interceptor
axios.interceptors.request.use(
  function (config) {
    return config
  }, function (error) {
    // 对请求错误做些什么
    return Promise.reject(error)
  })

// response interceptor
axios.interceptors.response.use(
  (response) => {
    // 2xx 范围内的状态码都会触发该函数。
    // 对响应数据做点什么
    return response.data
  }, (error) => {
    // 超出 2xx 范围的状态码都会触发该函数。
    // 对响应错误做点什么
    // 请求超时
    console.log(error)
    if (error.message.includes('timeout')) {
      Notification({
        title: '发生错误',
        message: '网络超时,请求超过200s未有相应，请检查网络配置',
        type: 'error',
        duration: 0
      })
      return Promise.reject(error)
    }
    Notification({
      title: '发生错误',
      message: error.response.data.msg,
      type: 'error',
      duration: 0
    })
    return Promise.reject(error.response)
  })

export default axios
