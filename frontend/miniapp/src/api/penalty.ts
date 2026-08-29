import { request } from '@/utils/request'

export interface Penalty {
  id: string
  issuer_id: string
  offender_id: string
  reason: string
  penalty_type: 'money' | 'action'
  amount: number | null
  action: string | null
  photo_url: string | null
  note: string | null
  is_done: boolean
  done_at: string | null
  created_at: string
}

export interface PenaltyCreate {
  offender_id: string
  reason: string
  penalty_type?: 'money' | 'action'
  amount?: number
  action?: string
  photo_url?: string
  note?: string
}

export const penaltyApi = {
  list: () =>
    request<Penalty[]>({ url: '/api/penalties' }),

  create: (data: PenaltyCreate) =>
    request<Penalty>({ url: '/api/penalties', method: 'POST', data }),

  done: (id: string) =>
    request<Penalty>({ url: `/api/penalties/${id}/done`, method: 'POST' }),

  delete: (id: string) =>
    request<{ message: string }>({ url: `/api/penalties/${id}`, method: 'DELETE' }),
}
