import { request } from '@/utils/request'

export interface Wish {
  id: string
  created_by: string
  creator_nickname: string
  content: string
  is_done: boolean
  done_at: string | null
  created_at: string
}

export const wishApi = {
  list: () =>
    request<Wish[]>({ url: '/api/wishes' }),

  create: (content: string) =>
    request<Wish>({ url: '/api/wishes', method: 'POST', data: { content } }),

  update: (id: string, data: { content?: string; is_done?: boolean }) =>
    request<Wish>({ url: `/api/wishes/${id}`, method: 'PUT', data }),

  delete: (id: string) =>
    request<{ message: string }>({ url: `/api/wishes/${id}`, method: 'DELETE' }),
}
