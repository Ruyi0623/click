<template>
  <view class="page-transaction">
    <!-- 月份切换 -->
    <view class="tx-header animate-fade-in-down">
      <view class="tx-header__arrow" @tap="prevMonth">
        <KdIcon name="tabler:chevron-left" :size="34" :color="isCurrentMonth ? '#ddd' : '#666'" />
      </view>
      <view class="tx-header__month-wrap" @tap="showMonthPicker = true">
        <text class="tx-header__month">{{ displayMonth }}</text>
        <text v-if="!isCurrentMonth" class="tx-header__back-hint" @tap.stop="resetToCurrent">回到本月</text>
      </view>
      <view class="tx-header__arrow" @tap="nextMonth">
        <KdIcon name="tabler:chevron-right" :size="34" :color="isFutureMonth ? '#ddd' : '#666'" />
      </view>
    </view>

    <!-- 月份选择面板 -->
    <view v-if="showMonthPicker" class="month-picker-mask" @tap="showMonthPicker = false">
      <view class="month-picker animate-slide-up" @tap.stop>
        <view class="month-picker__year-row">
          <view class="month-picker__year-arrow" @tap="pickerYear--">
            <KdIcon name="tabler:chevron-left" :size="32" color="#666" />
          </view>
          <text class="month-picker__year">{{ pickerYear }}年</text>
          <view class="month-picker__year-arrow" @tap="pickerYear++">
            <KdIcon name="tabler:chevron-right" :size="32" color="#666" />
          </view>
        </view>
        <view class="month-picker__grid">
          <view
            v-for="m in 12"
            :key="m"
            class="month-picker__cell"
            :class="{
              'month-picker__cell--active': pickerYear === selectedYear && m - 1 === selectedMonthIdx,
              'month-picker__cell--current': pickerYear === currentYear && m - 1 === currentMonthIdx,
              'month-picker__cell--disabled': pickerYear > currentYear || (pickerYear === currentYear && m - 1 > currentMonthIdx),
            }"
            @tap="pickMonth(m - 1)"
          >
            <text>{{ m }}月</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 双人消费对比卡片 -->
    <view class="balance-card animate-card-slide">
      <!-- 双人区域 -->
      <view class="balance-people">
        <view class="balance-person">
          <image
            class="balance-person__avatar"
            :src="myAvatar || '/static/images/default-avatar.png'"
            mode="aspectFill"
          />
          <text class="balance-person__name">我</text>
          <text class="balance-person__amount">¥{{ myTotal.toFixed(0) }}</text>
        </view>

        <view class="balance-bridge">
          <view class="balance-bridge__line" />
          <view class="balance-bridge__heart">♥</view>
          <view class="balance-bridge__line" />
        </view>

        <view class="balance-person">
          <image
            class="balance-person__avatar"
            :src="partnerAvatar || '/static/images/default-avatar.png'"
            mode="aspectFill"
          />
          <text class="balance-person__name">{{ partnerName }}</text>
          <text class="balance-person__amount">¥{{ partnerTotal.toFixed(0) }}</text>
        </view>
      </view>

      <!-- 总计 + 预算 -->
      <view class="balance-summary">
        <view class="balance-summary__row">
          <text class="balance-summary__label">本月共消费</text>
          <text class="balance-summary__total">¥{{ (stats?.total || 0).toFixed(0) }}</text>
        </view>
        <view v-if="stats?.budget" class="balance-budget" @tap="editBudget">
          <view class="balance-budget__bar">
            <view
              class="balance-budget__fill"
              :class="{ 'balance-budget__fill--over': budgetPercent > 100 }"
              :style="{ width: Math.min(budgetPercent, 100) + '%' }"
            />
          </view>
          <view class="balance-budget__info">
            <text class="balance-budget__text">
              {{ stats.budget_remaining >= 0 ? `剩余 ¥${stats.budget_remaining.toFixed(0)}` : `超支 ¥${Math.abs(stats.budget_remaining).toFixed(0)}` }}
            </text>
            <view class="balance-budget__right">
              <text class="balance-budget__percent">{{ budgetPercent.toFixed(0) }}%</text>
              <KdIcon name="tabler:pencil" :size="22" color="#ccc" />
            </view>
          </view>
        </view>
        <text v-else class="balance-budget__hint" @tap="editBudget">点击设置月度预算</text>
      </view>
    </view>

    <!-- 分类统计 -->
    <view v-if="stats?.categories?.length" class="categories animate-soft-slide" style="animation-delay: 150ms">
      <scroll-view scroll-x class="categories-scroll">
        <view class="categories-tags">
          <view
            v-for="cat in stats.categories"
            :key="cat.category"
            class="cat-tag"
            :style="{ '--cat-color': categoryColor[cat.category] || '#999' }"
            @tap="toggleCategoryFilter(cat.category)"
          >
            <view class="cat-tag__dot" />
            <text class="cat-tag__name">{{ cat.category }}</text>
            <text class="cat-tag__amount">¥{{ cat.amount.toFixed(0) }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 筛选栏 -->
    <view class="filter-row animate-soft-slide" style="animation-delay: 200ms">
      <view
        class="filter-chip"
        :class="{ 'filter-chip--active': !filterCategory }"
        @tap="clearCategoryFilter"
      >
        <text class="filter-chip__text">全部</text>
      </view>
      <view
        v-for="cat in allCategories"
        :key="cat"
        class="filter-chip"
        :class="{ 'filter-chip--active': filterCategory === cat }"
        @tap="toggleCategoryFilter(cat)"
      >
        <view class="filter-chip__dot" :style="{ background: categoryColor[cat] || '#999' }" />
        <text class="filter-chip__text">{{ cat }}</text>
      </view>
    </view>

    <!-- 交易列表 -->
    <view v-if="loading" class="loading-wrap">
      <view class="loading-spinner animate-spin" />
    </view>

    <KdEmpty v-else-if="!list.length" title="还没有账单" desc="记录你们的每一笔开销" icon="tabler:receipt" />

    <view v-else class="tx-groups">
      <view v-for="group in groupedTransactions" :key="group.date" class="tx-group">
        <view class="tx-group__header">
          <text class="tx-group__date">{{ group.label }}</text>
          <text class="tx-group__sum">-¥{{ group.total.toFixed(0) }}</text>
        </view>
        <view
          v-for="(item, index) in group.items"
          :key="item.id"
          class="tx-item animate-fade-in-up"
          :style="{ animationDelay: `${index * 40}ms` }"
          @tap="goEdit(item.id)"
          @longpress="deleteItem(item.id)"
        >
          <view class="tx-item__stripe" :style="{ background: categoryColor[item.category] || '#999' }" />
          <view class="tx-item__icon">
            <KdIcon :name="categoryIcon[item.category] || 'tabler:wallet'" :size="32" />
          </view>
          <view class="tx-item__info">
            <text class="tx-item__desc">{{ item.description || item.category }}</text>
            <text class="tx-item__meta">{{ whoBears(item) }} · {{ formatTime(item.happened_at || item.created_at) }}</text>
          </view>
          <text class="tx-item__amount">-¥{{ item.amount.toFixed(2) }}</text>
        </view>
      </view>
    </view>

    <!-- FAB -->
    <view class="fab animate-pulse-glow" @tap="goCreate">
      <KdIcon name="tabler:plus" :size="48" color="#fff" />
    </view>
  </view>

  <KdDialog
    :visible="showDeleteConfirm"
    title="删除账单"
    content="确定要删除吗？"
    confirm-color="#EF5350"
    @close="showDeleteConfirm = false"
    @confirm="onDeleteConfirm"
  />
  <KdDialog
    :visible="showBudgetDialog"
    title="设置月度预算"
    :show-input="true"
    input-placeholder="请输入金额"
    :input-value="budgetInput"
    @close="showBudgetDialog = false"
    @confirm="onBudgetConfirm"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'
import { transactionApi, type Transaction, type MonthlyStats } from '@/api/transaction'
import { coupleApi } from '@/api/couple'
import { useAuthStore } from '@/stores/auth'
import { useCoupleStore } from '@/stores/couple'
import { ensureHttps } from '@/utils/request'
import KdEmpty from '@/components/KdEmpty.vue'
import KdIcon from '@/components/KdIcon.vue'
import KdDialog from '@/components/KdDialog.vue'

const authStore = useAuthStore()
const coupleStore = useCoupleStore()
const currentUserId = computed(() => authStore.userInfo?.id || '')
const partnerName = computed(() => coupleStore.partner?.nickname || 'TA')

const myAvatar = computed(() => ensureHttps(authStore.userInfo?.avatar_url || ''))
const partnerAvatar = computed(() => ensureHttps(coupleStore.partner?.avatar || ''))

if (!authStore.userInfo?.id) {
  authStore.loadFromStorage()
  if (!authStore.userInfo?.id) authStore.fetchUserInfo()
}
if (!coupleStore.coupleInfo) coupleStore.fetchCoupleInfo()

const list = ref<Transaction[]>([])
const stats = ref<MonthlyStats | null>(null)
const loading = ref(true)
const showDeleteConfirm = ref(false)
const deleteTargetId = ref('')
const showBudgetDialog = ref(false)
const budgetInput = ref('')

const categoryIcon: Record<string, string> = {
  '餐饮': 'tabler:food', '交通': 'tabler:car', '娱乐': 'tabler:game',
  '购物': 'tabler:shopping-bag', '旅行': 'tabler:plane', '其他': 'tabler:wallet',
}
const categoryColor: Record<string, string> = {
  '餐饮': '#FF7043', '交通': '#42A5F5', '娱乐': '#AB47BC',
  '购物': '#FFA726', '旅行': '#26C6DA', '其他': '#78909C',
}

// 月份切换
const now = new Date()
const currentYear = now.getFullYear()
const currentMonthIdx = now.getMonth()
const selectedYear = ref(currentYear)
const selectedMonthIdx = ref(currentMonthIdx)

// 月份选择面板
const showMonthPicker = ref(false)
const pickerYear = ref(currentYear)

const displayMonth = computed(() => `${selectedYear.value}年${selectedMonthIdx.value + 1}月`)
const isCurrentMonth = computed(() => {
  const now = new Date()
  return selectedYear.value === now.getFullYear() && selectedMonthIdx.value === now.getMonth()
})
const isFutureMonth = computed(() => {
  const now = new Date()
  return selectedYear.value > now.getFullYear() ||
    (selectedYear.value === now.getFullYear() && selectedMonthIdx.value >= now.getMonth())
})
const selectedMonthStr = computed(() =>
  `${selectedYear.value}-${(selectedMonthIdx.value + 1).toString().padStart(2, '0')}`
)

const prevMonth = () => {
  if (selectedMonthIdx.value === 0) {
    selectedYear.value--
    selectedMonthIdx.value = 11
  } else {
    selectedMonthIdx.value--
  }
  loadData()
}
const nextMonth = () => {
  if (isFutureMonth.value) return
  if (selectedMonthIdx.value === 11) {
    selectedYear.value++
    selectedMonthIdx.value = 0
  } else {
    selectedMonthIdx.value++
  }
  loadData()
}
const resetToCurrent = () => {
  if (isCurrentMonth.value) return
  selectedYear.value = currentYear
  selectedMonthIdx.value = currentMonthIdx
  loadData()
}

const pickMonth = (m: number) => {
  if (pickerYear.value > currentYear || (pickerYear.value === currentYear && m > currentMonthIdx)) return
  selectedYear.value = pickerYear.value
  selectedMonthIdx.value = m
  showMonthPicker.value = false
  loadData()
}

const budgetPercent = computed(() => {
  if (!stats.value?.budget) return 0
  return (stats.value.total / stats.value.budget) * 100
})

// 双人消费拆分
const myTotal = computed(() => {
  const userStat = stats.value?.users?.find(u => u.user_id === currentUserId.value)
  return userStat?.amount || 0
})
const partnerTotal = computed(() => {
  const userStat = stats.value?.users?.find(u => u.user_id !== currentUserId.value)
  return userStat?.amount || 0
})

// 按日期分组
const groupedTransactions = computed(() => {
  const groups: Record<string, Transaction[]> = {}
  for (const item of list.value) {
    const d = new Date(item.happened_at || item.created_at)
    const key = `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`
    if (!groups[key]) groups[key] = []
    groups[key].push(item)
  }
  const today = new Date()
  const todayKey = `${today.getFullYear()}-${(today.getMonth() + 1).toString().padStart(2, '0')}-${today.getDate().toString().padStart(2, '0')}`
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const yesterdayKey = `${yesterday.getFullYear()}-${(yesterday.getMonth() + 1).toString().padStart(2, '0')}-${yesterday.getDate().toString().padStart(2, '0')}`

  return Object.entries(groups)
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([date, items]) => {
      let label = date
      if (date === todayKey) label = '今天'
      else if (date === yesterdayKey) label = '昨天'
      else {
        const d = new Date(date)
        label = `${d.getMonth() + 1}月${d.getDate()}日`
      }
      const total = items.reduce((sum, i) => sum + i.amount, 0)
      return { date, label, items, total }
    })
})

// 筛选
const filterCategory = ref('')
const allCategories = ['餐饮', '交通', '娱乐', '购物', '旅行', '其他']

const toggleCategoryFilter = (cat: string) => {
  filterCategory.value = filterCategory.value === cat ? '' : cat
  loadList()
}
const clearCategoryFilter = () => {
  filterCategory.value = ''
  loadList()
}

const formatTime = (iso: string) => {
  const d = new Date(iso)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

const whoBears = (item: Transaction) => {
  if (item.split_type === 'equal') return 'AA'
  if (item.split_type === 'payer_full') return item.paid_by === currentUserId.value ? '我承担' : `${partnerName.value}承担`
  if (item.split_type === 'other_full') return item.paid_by === currentUserId.value ? `${partnerName.value}承担` : '我承担'
  if (item.split_type === 'custom') {
    const other = item.custom_amount || 0
    const mine = item.amount - other
    return `我${mine.toFixed(0)} · TA${other.toFixed(0)}`
  }
  return 'AA'
}

const loadList = async () => {
  try {
    const filter: any = { limit: 100 }
    // 按月筛选：start_date 和 end_date
    const y = selectedYear.value
    const m = selectedMonthIdx.value
    const start = `${y}-${(m + 1).toString().padStart(2, '0')}-01`
    const lastDay = new Date(y, m + 1, 0).getDate()
    const end = `${y}-${(m + 1).toString().padStart(2, '0')}-${lastDay}`
    filter.start_date = start
    filter.end_date = end
    if (filterCategory.value) filter.category = filterCategory.value
    list.value = await transactionApi.list(filter)
  } catch {}
}

const loadData = async () => {
  loading.value = true
  try {
    await Promise.all([loadList(), loadStats()])
  } catch {} finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try { stats.value = await transactionApi.stats(selectedMonthStr.value) } catch {}
}

const editBudget = () => {
  budgetInput.value = stats.value?.budget?.toString() || ''
  showBudgetDialog.value = true
}
const onBudgetConfirm = async (value?: string) => {
  const raw = value ?? budgetInput.value
  const amount = parseFloat(raw)
  if (isNaN(amount) || amount <= 0) {
    uni.showToast({ title: '请输入有效金额', icon: 'none' })
    return
  }
  try {
    await coupleApi.updateBudget(amount, selectedMonthStr.value)
    uni.showToast({ title: '已设置', icon: 'success' })
    await loadStats()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

const goCreate = () => uni.navigateTo({ url: '/pages/transaction/create' })
const goEdit = (id: string) => uni.navigateTo({ url: `/pages/transaction/create?id=${id}` })
const deleteItem = (id: string) => {
  deleteTargetId.value = id
  showDeleteConfirm.value = true
}
const onDeleteConfirm = async () => {
  try {
    await transactionApi.delete(deleteTargetId.value)
    await loadData()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onMounted(loadData)
onShow(loadData)
onPullDownRefresh(async () => { await loadData(); uni.stopPullDownRefresh() })
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-transaction {
  min-height: 100vh;
  background: $bg-page;
  padding: 0 $padding-page;
  padding-bottom: calc(160rpx + env(safe-area-inset-bottom));
}

// ========== 月份切换 ==========
.tx-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
  padding: 80rpx 0 32rpx;
  opacity: 0;

  &__arrow {
    padding: 8rpx;
    &:active { opacity: 0.5; }
  }

  &__month-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 200rpx;
    &:active { opacity: 0.7; }
  }

  &__month {
    font-size: 32rpx;
    font-weight: $font-weight-bold;
    color: $text-primary;
    font-family: $font-family-number;
  }

  &__back-hint {
    font-size: 20rpx;
    color: $heart-pink;
    margin-top: 4rpx;
  }
}

// ========== 月份选择面板 ==========
.month-picker-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 500;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.month-picker {
  width: 100%;
  background: $bg-card;
  border-radius: $radius-xl $radius-xl 0 0;
  padding: 40rpx 36rpx;
  padding-bottom: calc(40rpx + env(safe-area-inset-bottom));

  &__year-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 48rpx;
    margin-bottom: 36rpx;
  }

  &__year-arrow {
    padding: 12rpx;
    &:active { opacity: 0.5; }
  }

  &__year {
    font-size: 34rpx;
    font-weight: $font-weight-bold;
    color: $text-primary;
    font-family: $font-family-number;
  }

  &__grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20rpx;
  }

  &__cell {
    height: 88rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: $radius-base;
    background: $bg-page;
    transition: all $duration-fast $ease-soft;

    text {
      font-size: $font-size-base;
      color: $text-primary;
      font-weight: $font-weight-medium;
    }

    &--active {
      background: $gradient-heart;
      box-shadow: $shadow-glow;
      text {
        color: #fff;
        font-weight: $font-weight-bold;
      }
    }

    &--current:not(&--active) {
      border: 2rpx solid $heart-pink;
      text { color: $heart-pink; }
    }

    &--disabled {
      opacity: 0.3;
      pointer-events: none;
    }

    &:active:not(&--disabled) {
      transform: scale(0.95);
    }
  }
}

// ========== 双人对比卡片 ==========
.balance-card {
  background: $bg-card;
  border-radius: $radius-xl;
  padding: 40rpx 32rpx 32rpx;
  margin-bottom: 24rpx;
  box-shadow:
    0 8rpx 32rpx rgba(255, 107, 138, 0.12),
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.8);
  opacity: 0;
}

.balance-people {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  margin-bottom: 32rpx;
}

.balance-person {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  &__avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: $radius-full;
    border: 4rpx solid $heart-pink-pale;
    margin-bottom: 12rpx;
  }
  &__name {
    font-size: $font-size-sm;
    color: $text-secondary;
    margin-bottom: 6rpx;
  }
  &__amount {
    font-size: 40rpx;
    font-weight: $font-weight-bold;
    font-family: $font-family-number;
    color: $text-primary;
  }
}

.balance-bridge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 0 8rpx;
  &__line {
    width: 2rpx;
    height: 24rpx;
    background: $heart-pink-pale;
  }
  &__heart {
    font-size: 28rpx;
    color: $heart-pink;
    animation: heartbeat 1.5s ease-in-out infinite;
  }
}

.balance-summary {
  border-top: 2rpx solid $border-light;
  padding-top: 24rpx;
  &__row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 16rpx;
  }
  &__label {
    font-size: $font-size-sm;
    color: $text-secondary;
  }
  &__total {
    font-size: $font-size-xl;
    font-weight: $font-weight-bold;
    font-family: $font-family-number;
    color: $heart-pink;
  }
}

.balance-budget {
  &__bar {
    height: 16rpx;
    background: $heart-pink-ghost;
    border-radius: $radius-full;
    overflow: hidden;
    margin-bottom: 12rpx;
  }
  &__fill {
    height: 100%;
    background: $gradient-heart;
    border-radius: $radius-full;
    transition: width 0.6s $ease-soft;
    &--over {
      background: linear-gradient(135deg, $error, #D32F2F);
    }
  }
  &__info {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  &__text {
    font-size: $font-size-sm;
    color: $text-secondary;
  }
  &__right {
    display: flex;
    align-items: center;
    gap: 8rpx;
  }
  &__percent {
    font-size: $font-size-sm;
    font-weight: $font-weight-semibold;
    font-family: $font-family-number;
    color: $heart-pink;
  }
  &__hint {
    font-size: $font-size-sm;
    color: $text-tertiary;
    text-align: center;
    padding: 8rpx 0;
  }
}

// ========== 分类统计 ==========
.categories {
  margin-bottom: 20rpx;
  opacity: 0;
}

.categories-scroll {
  white-space: nowrap;
  margin: 0 -32rpx;
  padding: 0 32rpx;
}

.categories-tags {
  display: inline-flex;
  gap: 16rpx;
}

.cat-tag {
  display: inline-flex;
  align-items: center;
  gap: 10rpx;
  background: $bg-card;
  border-radius: $radius-full;
  padding: 16rpx 24rpx;
  box-shadow: $shadow-sm;
  &__dot {
    width: 12rpx;
    height: 12rpx;
    border-radius: 50%;
    background: var(--cat-color, #999);
  }
  &__name {
    font-size: $font-size-sm;
    color: $text-secondary;
  }
  &__amount {
    font-size: $font-size-sm;
    font-weight: $font-weight-semibold;
    font-family: $font-family-number;
    color: $text-primary;
  }
}

// ========== 筛选栏 ==========
.filter-row {
  display: flex;
  gap: 12rpx;
  margin-bottom: 24rpx;
  overflow-x: auto;
  white-space: nowrap;
  opacity: 0;
  -webkit-overflow-scrolling: touch;
  &::-webkit-scrollbar { display: none; }
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 24rpx;
  border-radius: $radius-full;
  background: $bg-card;
  border: 2rpx solid transparent;
  flex-shrink: 0;
  transition: all $duration-fast $ease-soft;

  &--active {
    background: $heart-pink-ghost;
    border-color: $heart-pink;
    .filter-chip__text { color: $heart-pink; font-weight: $font-weight-semibold; }
  }

  &__dot {
    width: 10rpx;
    height: 10rpx;
    border-radius: 50%;
  }

  &__text {
    font-size: $font-size-sm;
    color: $text-secondary;
    transition: color $duration-fast $ease-soft;
  }
}

// ========== 加载 ==========
.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 120rpx 0;
}
.loading-spinner {
  width: 48rpx;
  height: 48rpx;
  border: 4rpx solid $border-light;
  border-top-color: $heart-pink;
  border-radius: 50%;
}

// ========== 交易分组 ==========
.tx-groups {
  margin-top: 8rpx;
}

.tx-group {
  margin-bottom: 32rpx;
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16rpx;
    padding: 0 4rpx;
  }
  &__date {
    font-size: $font-size-base;
    font-weight: $font-weight-semibold;
    color: $text-primary;
  }
  &__sum {
    font-size: $font-size-sm;
    color: $text-tertiary;
    font-family: $font-family-number;
  }
}

// ========== 交易项 ==========
.tx-item {
  display: flex;
  align-items: center;
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    0 4rpx 16rpx rgba(255, 107, 138, 0.06);
  opacity: 0;
  overflow: hidden;
  position: relative;
  transition: transform $duration-fast $ease-soft;
  &:active { transform: scale(0.98); }

  &__stripe {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 6rpx;
    border-radius: 0 4rpx 4rpx 0;
  }

  &__icon {
    width: 64rpx;
    height: 64rpx;
    border-radius: $radius-base;
    background: $bg-page;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: 16rpx;
    margin-right: 20rpx;
    flex-shrink: 0;
    color: $text-secondary;
  }

  &__info {
    flex: 1;
    min-width: 0;
  }

  &__desc {
    font-size: $font-size-md;
    color: $text-primary;
    font-weight: $font-weight-medium;
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__meta {
    font-size: $font-size-sm;
    color: $text-secondary;
    display: block;
    margin-top: 6rpx;
  }

  &__amount {
    font-size: $font-size-lg;
    font-weight: $font-weight-bold;
    color: $text-primary;
    font-family: $font-family-number;
    flex-shrink: 0;
    margin-left: 16rpx;
  }
}

// ========== FAB ==========
.fab {
  position: fixed;
  right: 40rpx;
  bottom: calc(160rpx + env(safe-area-inset-bottom));
  width: 112rpx;
  height: 112rpx;
  border-radius: $radius-full;
  background: $gradient-heart;
  box-shadow:
    0 8rpx 32rpx rgba(255, 107, 138, 0.35),
    0 2rpx 8rpx rgba(232, 82, 122, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  transition: transform $duration-fast $ease-soft;
  &:active { transform: scale(0.9); }
}
</style>
