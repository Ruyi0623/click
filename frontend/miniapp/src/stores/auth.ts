import { defineStore } from 'pinia'
import { authApi, type UserInfo } from '@/api/auth'

export type { UserInfo }

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: uni.getStorageSync('token') || '',
    userInfo: null as UserInfo | null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    setToken(token: string) {
      this.token = token
      uni.setStorageSync('token', token)
    },
    setUserInfo(info: UserInfo) {
      this.userInfo = info
      uni.setStorageSync('userInfo', JSON.stringify(info))
    },
    async fetchUserInfo() {
      const info = await authApi.getMe()
      this.setUserInfo(info)
      return info
    },
    logout() {
      this.token = ''
      this.userInfo = null
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
    },
    loadFromStorage() {
      const cached = uni.getStorageSync('userInfo')
      if (cached) {
        try { this.userInfo = JSON.parse(cached) } catch {}
      }
    },
  },
})
