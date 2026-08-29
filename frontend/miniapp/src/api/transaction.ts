import { request } from '@/utils/request'

export interface Transaction {
  id: string
  paid_by: string
  amount: number
  category: string
  description: string | null
  split_type: string
  custom_amount: number | null
  photo_url: string | null
  mood: string | null
  happened_at: string | null
  created_at: string
}

export interface Balance {
  user1_id: string
  user1_nickname: string
  user1_paid: number
  user2_id: string
  user2_nickname: string
  user2_paid: number
  balance: number
  who_owes: string
}

export interface TransactionCreate {
  amount: number
  category: string
  description?: string
  split_type?: string
  custom_amount?: number
  photo_url?: string
  mood?: string
  happened_at?: string
}

export interface TransactionUpdate {
  amount?: number
  category?: string
  description?: string
  split_type?: string
  custom_amount?: number
  happened_at?: string
}

export interface TransactionFilter {
  limit?: number
  category?: string
  start_date?: string
  end_date?: string
}

export interface CategoryStat {
  category: string
  amount: number
  percentage: number
}

export interface UserSpending {
  user_id: string
  nickname: string
  amount: number
}

export interface MonthlyStats {
  month: string
  total: number
  budget: number | null
  budget_remaining: number | null
  categories: CategoryStat[]
  users: UserSpending[]
}

export const transactionApi = {
  list: (filter?: TransactionFilter) =>
    request<Transaction[]>({ url: '/api/transactions', data: filter }),

  create: (data: TransactionCreate) =>
    request<Transaction>({ url: '/api/transactions', method: 'POST', data }),

  update: (id: string, data: TransactionUpdate) =>
    request<Transaction>({ url: `/api/transactions/${id}`, method: 'PUT', data }),

  balance: () =>
    request<Balance>({ url: '/api/transactions/balance' }),

  stats: (month?: string) =>
    request<MonthlyStats>({ url: '/api/transactions/stats', data: month ? { month } : undefined }),

  delete: (id: string) =>
    request<{ message: string }>({ url: `/api/transactions/${id}`, method: 'DELETE' }),
}
