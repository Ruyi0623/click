import { request } from '@/utils/request'

export interface Anniversary {
  id: string
  title: string
  date: string
  repeat_type: 'yearly' | 'none'
  days_until: number | null
}

export interface AnniversaryCreate {
  title: string
  date: string
  repeat_type?: 'yearly' | 'none'
}

export const anniversaryApi = {
  list: () =>
    request<Anniversary[]>({ url: '/api/anniversaries' }),

  create: (data: AnniversaryCreate) =>
    request<Anniversary>({ url: '/api/anniversaries', method: 'POST', data }),

  update: (id: string, data: Partial<AnniversaryCreate>) =>
    request<Anniversary>({ url: `/api/anniversaries/${id}`, method: 'PUT', data }),

  delete: (id: string) =>
    request<{ message: string }>({ url: `/api/anniversaries/${id}`, method: 'DELETE' }),
}
