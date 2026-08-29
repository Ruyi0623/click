import { request } from '@/utils/request'

export interface Magazine {
  id: string
  year: string
  month: string
  content: string
  generate_count: number
  status: 'success' | 'failed'
  created_at: string
}

export const magazineApi = {
  list: () =>
    request<Magazine[]>({ url: '/api/magazines' }),

  generate: (year: string, month: string) =>
    request<Magazine>({ url: '/api/magazines/generate', method: 'POST', data: { year, month } }),

  get: (id: string) =>
    request<Magazine>({ url: `/api/magazines/${id}` }),

  delete: (id: string) =>
    request<{ message: string }>({ url: `/api/magazines/${id}`, method: 'DELETE' }),
}
