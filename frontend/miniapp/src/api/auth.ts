import { request, upload } from '@/utils/request'

export interface LoginResponse {
  access_token: string
  token_type: string
  user_id: string
  nickname: string
}

export interface UserInfo {
  id: string
  phone: string | null
  nickname: string
  avatar_url: string | null
  username: string | null
  email: string | null
  birthday: string | null
  gender: string | null
  has_couple: boolean
  has_password: boolean
}

export const authApi = {
  // 微信登录
  wxLogin: (code: string) =>
    request<LoginResponse>({ url: '/api/auth/wx-login', method: 'POST', data: { code } }),

  // 用户名密码登录
  loginPassword: (username: string, password: string) =>
    request<LoginResponse>({ url: '/api/auth/login-password', method: 'POST', data: { username, password } }),

  // 绑定用户名密码（含昵称、生日）
  bindUsername: (data: { username: string; password: string; nickname?: string; birthday?: string }) =>
    request<{ message: string }>({ url: '/api/auth/bind-username', method: 'POST', data }),

  // 绑定邮箱
  bindEmail: (email: string) =>
    request<{ message: string }>({ url: '/api/auth/bind-email', method: 'POST', data: { email } }),

  // 上传头像
  uploadAvatar: (filePath: string) =>
    upload<{ avatar_url: string }>(filePath, undefined, '/api/auth/avatar'),

  // 获取用户信息
  getMe: () =>
    request<UserInfo>({ url: '/api/auth/me' }),

  // 更新资料
  updateProfile: (data: { nickname?: string; birthday?: string }) =>
    request<{ message: string }>({ url: '/api/auth/me', method: 'PUT', data }),

  // 手机号验证码登录
  sendCode: (phone: string) =>
    request<{ message: string }>({ url: '/api/auth/send-code', method: 'POST', data: { phone } }),

  login: (phone: string, code: string, nickname?: string) =>
    request<LoginResponse>({ url: '/api/auth/login', method: 'POST', data: { phone, code, nickname } }),

  deleteAccount: () =>
    request<{ message: string }>({ url: '/api/auth/me', method: 'DELETE' }),
}
