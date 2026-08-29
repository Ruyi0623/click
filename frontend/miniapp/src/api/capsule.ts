import { request } from '@/utils/request'

export interface Capsule {
  id: string
  created_by: string
  content: string
  open_at: string
  is_opened: boolean
  created_at: string
}

export const capsuleApi = {
  list: () =>
    request<Capsule[]>({ url: '/api/capsules' }),

  create: (content: string, open_at: string) =>
    request<Capsule>({ url: '/api/capsules', method: 'POST', data: { content, open_at } }),

  get: (id: string) =>
    request<Capsule>({ url: `/api/capsules/${id}` }),

  open: (id: string) =>
    request<Capsule>({ url: `/api/capsules/${id}/open`, method: 'POST' }),

  delete: (id: string) =>
    request<{ message: string }>({ url: `/api/capsules/${id}`, method: 'DELETE' }),
}
