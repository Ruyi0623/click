import { request } from '@/utils/request'

export interface Photo {
  id: string
  uploader_id: string
  url: string
  thumbnail_url: string | null
  caption: string | null
  width: number | null
  height: number | null
  taken_at: string | null
  created_at: string
}

export const photoApi = {
  list: (collectionId?: string | null) => {
    if (collectionId === null) {
      return request<Photo[]>({ url: '/api/photos?collection_id=ungrouped' })
    }
    if (collectionId) {
      return request<Photo[]>({ url: `/api/photos?collection_id=${collectionId}` })
    }
    return request<Photo[]>({ url: '/api/photos' })
  },

  delete: (id: string) =>
    request<{ message: string }>({ url: `/api/photos/${id}`, method: 'DELETE' }),

  move: (id: string, collectionId: string | null) =>
    request<{ message: string }>({ url: `/api/photos/${id}/move`, method: 'PUT', data: { collection_id: collectionId } }),
}
