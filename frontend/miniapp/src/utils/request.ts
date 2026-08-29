const BASE_URL = 'https://api1.sparkcore.cn'

/** 确保 URL 使用 HTTPS 协议 */
export const ensureHttps = (url: string): string => {
  if (!url) return url
  return url.replace(/^http:\/\//i, 'https://')
}

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
}

export const request = <T = any>(options: RequestOptions): Promise<T> => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')

    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        Authorization: token ? `Bearer ${token}` : '',
        ...options.header,
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T)
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.removeStorageSync('userInfo')
          uni.reLaunch({ url: '/pages/login/index' })
          reject(new Error('登录已过期'))
        } else {
          const detail = (res.data as any)?.detail
          let errMsg = '请求失败'
          if (typeof detail === 'string') {
            errMsg = detail
          } else if (Array.isArray(detail)) {
            // FastAPI 422 校验错误格式
            errMsg = detail.map((d: any) => d.msg || JSON.stringify(d)).join('; ')
          } else if (detail) {
            errMsg = JSON.stringify(detail)
          }
          reject(new Error(errMsg))
        }
      },
      fail: () => {
        reject(new Error('网络错误'))
      },
    })
  })
}

export const upload = <T = any>(filePath: string, collectionId?: string, url?: string): Promise<T> => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    const formData: Record<string, string> = {}
    if (collectionId) {
      formData.collection_id = collectionId
    }
    uni.uploadFile({
      url: `${BASE_URL}${url || '/api/photos'}`,
      filePath,
      name: 'file',
      formData,
      header: {
        Authorization: token ? `Bearer ${token}` : '',
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(JSON.parse(res.data) as T)
        } else {
          try {
            const data = JSON.parse(res.data)
            reject(new Error(data.detail || '上传失败'))
          } catch {
            reject(new Error('上传失败'))
          }
        }
      },
      fail: () => reject(new Error('网络错误')),
    })
  })
}
