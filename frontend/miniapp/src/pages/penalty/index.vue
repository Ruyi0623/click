<template>
  <view class="page-penalty">
    <!-- 顶部统计 -->
    <view class="stats-card animate-reveal-days" v-if="list.length">
      <view class="stats-card__content">
        <view class="stats-card__row">
          <view class="stats-card__item">
            <text class="stats-card__num">{{ pendingCount }}</text>
            <text class="stats-card__label">待执行</text>
          </view>
          <view class="stats-card__divider" />
          <view class="stats-card__item">
            <text class="stats-card__num">{{ doneCount }}</text>
            <text class="stats-card__label">已完成</text>
          </view>
          <view class="stats-card__divider" />
          <view class="stats-card__item">
            <text class="stats-card__num stats-card__num--red">¥{{ totalAmount.toFixed(0) }}</text>
            <text class="stats-card__label">总罚款</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading-wrap">
      <view class="loading-spinner" />
    </view>

    <!-- 空状态 -->
    <view v-else-if="!list.length" class="empty-state">
      <view class="empty-state__ticket">
        <view class="empty-state__ticket-body" />
        <view class="empty-state__ticket-tear" />
      </view>
      <text class="empty-state__title">没有罚单</text>
      <text class="empty-state__desc">给对方开一张甜蜜的罚单吧</text>
    </view>

    <!-- 罚单列表 -->
    <view v-else class="ticket-list">
      <view class="ticket-list__header">
        <KdIcon name="tabler:ticket" :size="36" variant="pink" />
        <text class="ticket-list__title">甜蜜罚单</text>
      </view>

      <view
        v-for="(item, index) in list"
        :key="item.id"
        class="ticket-item"
        :class="{ 'ticket-item--done': item.is_done }"
        :style="{ animationDelay: `${index * 60}ms` }"
      >
        <!-- 罚单顶部 -->
        <view class="ticket-item__header">
          <view class="ticket-item__icon-wrap">
            <KdIcon :name="item.penalty_type === 'money' ? 'tabler:receipt' : 'tabler:heart'" :size="32" variant="pink" />
          </view>
          <view class="ticket-item__title-area">
            <text class="ticket-item__reason">{{ item.reason }}</text>
            <text class="ticket-item__date">{{ formatDate(item.created_at) }}</text>
          </view>
          <view class="ticket-item__tag" :class="item.is_done ? 'ticket-item__tag--done' : 'ticket-item__tag--pending'">
            <text class="ticket-item__tag-text">{{ item.is_done ? '已执行' : '待执行' }}</text>
          </view>
        </view>

        <!-- 罚单内容 -->
        <view class="ticket-item__body">
          <view v-if="item.penalty_type === 'money'" class="ticket-item__amount-wrap">
            <text class="ticket-item__amount-label">罚款金额</text>
            <text class="ticket-item__amount">¥{{ item.amount }}</text>
          </view>
          <view v-else class="ticket-item__action-wrap">
            <text class="ticket-item__action-label">惩罚行动</text>
            <text class="ticket-item__action">{{ item.action }}</text>
          </view>
          <text v-if="item.note" class="ticket-item__note">{{ item.note }}</text>
        </view>

        <!-- 证据照片 -->
        <view v-if="item.photo_url" class="ticket-item__evidence" @tap="previewPhoto(item.photo_url)">
          <image class="ticket-item__evidence-img" :src="ensureHttps(item.photo_url)" mode="aspectFill" />
          <view class="ticket-item__evidence-tag">
            <KdIcon name="tabler:camera" :size="20" color="#fff" />
            <text class="ticket-item__evidence-text">证据</text>
          </view>
        </view>

        <!-- 罚单底部 -->
        <view class="ticket-item__footer">
          <view class="ticket-item__footer-line" />
          <view class="ticket-item__actions">
            <view v-if="!item.is_done && item.offender_id === currentUserId" class="ticket-item__btn ticket-item__btn--done" @tap="markDone(item.id)">
              <KdIcon name="tabler:check" :size="24" color="#fff" />
              <text class="ticket-item__btn-text">完成</text>
            </view>
            <view class="ticket-item__btn ticket-item__btn--delete" @tap="deleteItem(item.id)">
              <KdIcon name="tabler:trash" :size="24" />
              <text class="ticket-item__btn-text">删除</text>
            </view>
          </view>
        </view>

        <!-- 罚单撕边装饰 -->
        <view class="ticket-item__tear ticket-item__tear--left" />
        <view class="ticket-item__tear ticket-item__tear--right" />
      </view>
    </view>

    <!-- FAB 按钮 -->
    <view class="fab" @tap="goCreate">
      <view class="fab__inner">
        <KdIcon name="tabler:plus" :size="48" color="#fff" />
      </view>
    </view>
  </view>

  <KdDialog
    :visible="showDeleteConfirm"
    title="删除罚单"
    content="确定要删除这张罚单吗？"
    confirm-color="#EF5350"
    @close="showDeleteConfirm = false"
    @confirm="onDeleteConfirm"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'
import { penaltyApi, type Penalty } from '@/api/penalty'
import { useAuthStore } from '@/stores/auth'
import { ensureHttps } from '@/utils/request'
import KdIcon from '@/components/KdIcon.vue'
import KdDialog from '@/components/KdDialog.vue'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.userInfo?.id || '')

if (!authStore.userInfo?.id) {
  authStore.loadFromStorage()
  if (!authStore.userInfo?.id) authStore.fetchUserInfo()
}

const list = ref<Penalty[]>([])
const loading = ref(true)
const showDeleteConfirm = ref(false)
const deleteTargetId = ref('')

const pendingCount = computed(() => list.value.filter(p => !p.is_done).length)
const doneCount = computed(() => list.value.filter(p => p.is_done).length)
const totalAmount = computed(() => list.value.filter(p => p.penalty_type === 'money').reduce((sum, p) => sum + (p.amount || 0), 0))

const formatDate = (iso: string) => {
  const d = new Date(iso)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

const loadList = async () => {
  try { list.value = await penaltyApi.list() } catch {} finally { loading.value = false }
}

const goCreate = () => uni.navigateTo({ url: '/pages/penalty/create' })

const previewPhoto = (url: string) => {
  uni.previewImage({ urls: [ensureHttps(url)] })
}

const markDone = async (id: string) => {
  try {
    await penaltyApi.done(id)
    uni.showToast({ title: '已完成', icon: 'success' })
    await loadList()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

const deleteItem = (id: string) => {
  deleteTargetId.value = id
  showDeleteConfirm.value = true
}
const onDeleteConfirm = async () => {
  try {
    await penaltyApi.delete(deleteTargetId.value)
    await loadList()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onMounted(loadList)
onShow(loadList)
onPullDownRefresh(async () => { await loadList(); uni.stopPullDownRefresh() })
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-penalty {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF0F2 0%, #FFE4E8 50%, #FFF5F7 100%);
  padding: 24rpx 32rpx;
  padding-bottom: calc(160rpx + env(safe-area-inset-bottom));
}

// ========== 顶部统计 ==========
.stats-card {
  background: linear-gradient(135deg, #FF8A80 0%, #EF5350 50%, #E53935 100%);
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 8rpx 32rpx rgba(239, 83, 80, 0.3);
  opacity: 0;

  &__content {
    position: relative;
    z-index: 1;
  }

  &__row {
    display: flex;
    align-items: center;
    justify-content: space-around;
  }

  &__item {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  &__num {
    font-size: 40rpx;
    font-weight: 700;
    color: #fff;
    font-family: $font-family-number;
    margin-bottom: 8rpx;

    &--red {
      text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.2);
    }
  }

  &__label {
    font-size: 22rpx;
    color: rgba(255, 255, 255, 0.7);
  }

  &__divider {
    width: 2rpx;
    height: 48rpx;
    background: rgba(255, 255, 255, 0.2);
  }
}

// ========== 加载状态 ==========
.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 120rpx 0;
}

.loading-spinner {
  width: 48rpx;
  height: 48rpx;
  border: 4rpx solid #FFCDD2;
  border-top-color: #EF5350;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// ========== 空状态 ==========
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 48rpx;

  &__ticket {
    position: relative;
    width: 120rpx;
    height: 100rpx;
    margin-bottom: 40rpx;
  }

  &__ticket-body {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #FFCDD2 0%, #EF9A9A 100%);
    border-radius: 12rpx;
    clip-path: polygon(0 0, 100% 0, 100% 40%, 90% 50%, 100% 60%, 100% 100%, 0 100%, 0 60%, 10% 50%, 0 40%);
  }

  &__title {
    font-size: 32rpx;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 12rpx;
  }

  &__desc {
    font-size: 26rpx;
    color: $text-tertiary;
  }
}

// ========== 罚单列表 ==========
.ticket-list {
  &__header {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 24rpx;
    padding: 0 8rpx;
  }

  &__title {
    font-size: 32rpx;
    font-weight: 600;
    color: $text-primary;
  }
}

// ========== 罚单卡片 ==========
.ticket-item {
  position: relative;
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    0 8rpx 24rpx rgba(239, 83, 80, 0.08);
  opacity: 0;
  animation: fadeIn 0.4s ease forwards;
  overflow: hidden;

  &--done {
    opacity: 0.85;
    background: #FAFAFA;
  }

  // 顶部
  &__header {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 20rpx;
  }

  &__icon-wrap {
    width: 56rpx;
    height: 56rpx;
    background: #FFEBEE;
    border-radius: 14rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &__title-area {
    flex: 1;
    min-width: 0;
  }

  &__reason {
    font-size: 30rpx;
    font-weight: 600;
    color: $text-primary;
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__date {
    font-size: 22rpx;
    color: $text-tertiary;
    display: block;
    margin-top: 4rpx;
  }

  &__tag {
    padding: 8rpx 16rpx;
    border-radius: 8rpx;
    flex-shrink: 0;

    &--done {
      background: #E8F5E9;
    }

    &--pending {
      background: #FFEBEE;
    }

    &-text {
      font-size: 22rpx;
      font-weight: 500;
    }

    &--done &-text {
      color: #4CAF50;
    }

    &--pending &-text {
      color: #EF5350;
    }
  }

  // 内容
  &__body {
    margin-bottom: 20rpx;
  }

  &__amount-wrap,
  &__action-wrap {
    display: flex;
    align-items: center;
    gap: 12rpx;
    padding: 16rpx 20rpx;
    background: #FFF5F5;
    border-radius: 12rpx;
    margin-bottom: 12rpx;
  }

  &__amount-label,
  &__action-label {
    font-size: 22rpx;
    color: $text-tertiary;
  }

  &__amount {
    font-size: 36rpx;
    font-weight: 700;
    color: #EF5350;
    font-family: $font-family-number;
  }

  &__action {
    font-size: 28rpx;
    font-weight: 500;
    color: $text-primary;
  }

  &__note {
    font-size: 24rpx;
    color: $text-secondary;
    display: block;
    line-height: 1.5;
  }

  // 证据
  &__evidence {
    position: relative;
    margin-bottom: 20rpx;
    border-radius: 12rpx;
    overflow: hidden;
  }

  &__evidence-img {
    width: 100%;
    height: 300rpx;
    border-radius: 12rpx;
  }

  &__evidence-tag {
    position: absolute;
    bottom: 12rpx;
    left: 12rpx;
    display: flex;
    align-items: center;
    gap: 6rpx;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 9999rpx;
    padding: 6rpx 16rpx;
  }

  &__evidence-text {
    font-size: 22rpx;
    color: #fff;
  }

  // 底部
  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 20rpx;
    border-top: 2rpx dashed #FFEBEE;
  }

  &__footer-line {
    flex: 1;
  }

  &__actions {
    display: flex;
    gap: 12rpx;
  }

  &__btn {
    display: flex;
    align-items: center;
    gap: 8rpx;
    padding: 12rpx 24rpx;
    border-radius: 9999rpx;
    transition: all 0.2s ease;

    &:active {
      transform: scale(0.95);
    }

    &--done {
      background: linear-gradient(135deg, #66BB6A 0%, #4CAF50 100%);
      box-shadow: 0 4rpx 12rpx rgba(76, 175, 80, 0.3);
    }

    &--delete {
      background: #FFEBEE;
    }

    &-text {
      font-size: 24rpx;
      font-weight: 500;
    }

    &--done &-text {
      color: #fff;
    }

    &--delete &-text {
      color: #EF5350;
    }
  }

  // 撕边装饰
  &__tear {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 24rpx;
    height: 24rpx;
    background: #FFF0F2;
    border-radius: 50%;

    &--left {
      left: -12rpx;
    }

    &--right {
      right: -12rpx;
    }
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(16rpx); }
  to { opacity: 1; transform: translateY(0); }
}

// ========== FAB 按钮 ==========
.fab {
  position: fixed;
  right: 40rpx;
  bottom: calc(120rpx + env(safe-area-inset-bottom));
  z-index: 100;

  &__inner {
    width: 112rpx;
    height: 112rpx;
    border-radius: 50%;
    background: linear-gradient(135deg, #FF8A80 0%, #EF5350 100%);
    box-shadow: 0 8rpx 24rpx rgba(239, 83, 80, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease;

    &:active {
      transform: scale(0.9);
    }
  }
}
</style>
