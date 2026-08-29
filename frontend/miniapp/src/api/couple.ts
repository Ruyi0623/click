import { request } from '@/utils/request'

export interface CoupleInfo {
  id: string
  partner_id: string
  partner_nickname: string
  partner_username: string | null
  partner_avatar: string | null
  partner_birthday: string | null
  partner_gender: string | null
  start_date: string
  days_together: number
  monthly_budget: number | null
}

export const coupleApi = {
  generate: () =>
    request<{ code: string; expires_in: number }>({ url: '/api/couple/generate', method: 'POST' }),

  confirm: (code: string, start_date?: string) =>
    request<{ message: string; couple_id: string }>({
      url: '/api/couple/confirm', method: 'POST', data: { code, start_date },
    }),

  info: () =>
    request<CoupleInfo>({ url: '/api/couple/info' }),

  unbind: () =>
    request<{ message: string }>({ url: '/api/couple/unbind', method: 'POST' }),

  updateBudget: (monthly_budget: number, month?: string) =>
    request<CoupleInfo>({ url: '/api/couple/budget', method: 'PUT', data: { monthly_budget, month } }),
}
