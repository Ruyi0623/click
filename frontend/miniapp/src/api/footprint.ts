import { request } from '@/utils/request'

export interface Footprint {
  id: string
  created_by: string
  name: string
  latitude: number
  longitude: number
  visited_at: string
  note: string | null
  created_at: string
}

export interface FootprintCreate {
  name: string
  latitude: number
  longitude: number
  visited_at: string
  note?: string
}

export interface FootprintUpdate {
  name?: string
  latitude?: number
  longitude?: number
  visited_at?: string
  note?: string
}

export const footprintApi = {
  list: () =>
    request<Footprint[]>({ url: '/api/footprints' }),

  create: (data: FootprintCreate) =>
    request<Footprint>({ url: '/api/footprints', method: 'POST', data }),

  get: (id: string) =>
    request<Footprint>({ url: `/api/footprints/${id}` }),

  update: (id: string, data: FootprintUpdate) =>
    request<Footprint>({ url: `/api/footprints/${id}`, method: 'PUT', data }),

  delete: (id: string) =>
    request<{ message: string }>({ url: `/api/footprints/${id}`, method: 'DELETE' }),
}
