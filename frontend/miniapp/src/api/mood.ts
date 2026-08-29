import { request } from '@/utils/request'

export interface Mood {
  id: string
  user_id: string
  emoji: string
  content: string | null
  mood_date: string
}

export const moodApi = {
  list: () =>
    request<Mood[]>({ url: '/api/moods' }),

  create: (emoji: string, mood_date: string, content?: string) =>
    request<Mood>({ url: '/api/moods', method: 'POST', data: { emoji, mood_date, content } }),

  delete: (id: string) =>
    request<{ message: string }>({ url: `/api/moods/${id}`, method: 'DELETE' }),
}
