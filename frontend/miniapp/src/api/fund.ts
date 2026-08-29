import { request } from '@/utils/request'

export interface Fund {
  id: string
  name: string
  target_amount: number
  current_amount: number
  icon: string
  progress: number
  created_at: string
}

export interface Contribution {
  id: string
  fund_id: string
  user_id: string
  amount: number
  type: 'deposit' | 'withdraw'
  note: string | null
  created_at: string
}

export const fundApi = {
  list: () =>
    request<Fund[]>({ url: '/api/funds' }),

  create: (data: { name: string; target_amount: number; icon?: string }) =>
    request<Fund>({ url: '/api/funds', method: 'POST', data }),

  delete: (id: string) =>
    request<{ message: string }>({ url: `/api/funds/${id}`, method: 'DELETE' }),

  contribute: (id: string, amount: number, note?: string) =>
    request<Contribution>({ url: `/api/funds/${id}/contribute`, method: 'POST', data: { amount, note } }),

  withdraw: (id: string, amount: number, note?: string) =>
    request<Contribution>({ url: `/api/funds/${id}/contribute`, method: 'POST', data: { amount, type: 'withdraw', note } }),

  contributions: (id: string) =>
    request<Contribution[]>({ url: `/api/funds/${id}/contributions` }),

  deleteContribution: (fundId: string, contributionId: string) =>
    request<{ message: string }>({ url: `/api/funds/${fundId}/contributions/${contributionId}`, method: 'DELETE' }),
}
