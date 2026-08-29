import { defineStore } from 'pinia'
import { request } from '@/utils/request'

interface CoupleInfo {
  id: string
  partner_id: string
  partner_nickname: string
  partner_avatar: string | null
  start_date: string
  days_together: number
}

export const useCoupleStore = defineStore('couple', {
  state: () => ({
    coupleInfo: null as CoupleInfo | null,
  }),
  getters: {
    hasCouple: (state) => !!state.coupleInfo,
    daysTogether: (state) => state.coupleInfo?.days_together ?? 0,
    partner: (state) => state.coupleInfo
      ? { nickname: state.coupleInfo.partner_nickname, avatar: state.coupleInfo.partner_avatar }
      : null,
  },
  actions: {
    async fetchCoupleInfo() {
      try {
        const info = await request<CoupleInfo>({ url: '/api/couple/info' })
        this.coupleInfo = info
        return info
      } catch {
        this.coupleInfo = null
        return null
      }
    },
    clear() {
      this.coupleInfo = null
    },
  },
})
