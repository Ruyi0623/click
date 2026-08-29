import { request } from '@/utils/request'

export interface DiaryAuthor {
  id: string
  nickname: string
  avatar_url: string | null
}

export interface DiaryPhoto {
  id: string
  url: string
  thumbnail_url: string | null
}

export interface DiaryComment {
  id: string
  user_id: string
  author: DiaryAuthor
  content: string
  created_at: string
}

export interface Diary {
  id: string
  created_by: string
  author: DiaryAuthor
  title: string | null
  content: string
  photos: DiaryPhoto[]
  like_count: number
  liked_by_me: boolean
  comments: DiaryComment[]
  created_at: string
  updated_at: string | null
}

export interface DiaryCreate {
  title?: string
  content: string
  photo_ids?: string[]
}

export interface DiaryUpdate {
  title?: string
  content?: string
  photo_ids?: string[]
}

export interface DiaryLikeResult {
  liked: boolean
  like_count: number
}

export const diaryApi = {
  list: () =>
    request<Diary[]>({ url: '/api/diaries' }),

  create: (data: DiaryCreate) =>
    request<Diary>({ url: '/api/diaries', method: 'POST', data }),

  update: (id: string, data: DiaryUpdate) =>
    request<Diary>({ url: `/api/diaries/${id}`, method: 'PUT', data }),

  delete: (id: string) =>
    request<{ message: string }>({ url: `/api/diaries/${id}`, method: 'DELETE' }),

  like: (id: string) =>
    request<DiaryLikeResult>({ url: `/api/diaries/${id}/like`, method: 'POST' }),

  addComment: (id: string, content: string) =>
    request<DiaryComment>({ url: `/api/diaries/${id}/comments`, method: 'POST', data: { content } }),

  deleteComment: (diaryId: string, commentId: string) =>
    request<{ message: string }>({ url: `/api/diaries/${diaryId}/comments/${commentId}`, method: 'DELETE' }),
}
