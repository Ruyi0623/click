import { request } from '@/utils/request'

export interface Collection {
  id: string
  name: string
  cover_photo_url: string | null
  photo_count: number
  created_at: string
}

export const collectionApi = {
  list: () =>
    request<Collection[]>({ url: '/api/collections' }),

  create: (name: string) =>
    request<Collection>({ url: '/api/collections', method: 'POST', data: { name } }),

  update: (id: string, data: { name?: string; cover_photo_id?: string }) =>
    request<Collection>({ url: `/api/collections/${id}`, method: 'PUT', data }),

  delete: (id: string) =>
    request<{ message: string }>({ url: `/api/collections/${id}`, method: 'DELETE' }),
}
