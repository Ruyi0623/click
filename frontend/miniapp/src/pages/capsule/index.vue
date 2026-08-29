<template>
  <view class="page-capsule">
    <!-- 加载状态 -->
    <view v-if="loading" class="loading-wrap">
      <view class="loading-spinner animate-spin" />
    </view>

    <!-- 空状态 -->
    <view v-else-if="!list.length" class="empty-state animate-fade-in">
      <view class="empty-state__icon-wrap">
        <view class="empty-state__icon-bg" />
        <KdIcon name="tabler:mailbox" :size="80" color="#42A5F5" />
      </view>
      <text class="empty-state__title">邮箱空空如也</text>
      <text class="empty-state__desc">写一封信寄给未来的你们</text>
    </view>

    <!-- 主内容 -->
    <view v-else class="content">
      <!-- Hero 统计卡 -->
      <view class="hero-card animate-reveal-days">
        <view class="hero-card__bg" />
        <view class="hero-card__dot hero-card__dot--1" />
        <view class="hero-card__dot hero-card__dot--2" />
        <view class="hero-card__content">
          <view class="hero-card__stats">
            <view class="hero-card__stat">
              <text class="hero-card__num">{{ pendingList.length }}</text>
              <text class="hero-card__label">在路上</text>
            </view>
            <view class="hero-card__divider" />
            <view class="hero-card__stat">
              <text class="hero-card__num">{{ openedList.length }}</text>
              <text class="hero-card__label">已送达</text>
            </view>
            <view class="hero-card__divider" />
            <view class="hero-card__stat">
              <text class="hero-card__num">{{ overdueList.length }}</text>
              <text class="hero-card__label">待开启</text>
            </view>
          </view>
          <text class="hero-card__hint">{{ list.length }} 封信件在旅行中</text>
        </view>
      </view>

      <!-- 在路上 -->
      <view v-if="pendingList.length" class="section animate-soft-slide" style="animation-delay: 100ms">
        <view class="section__header">
          <KdIcon name="tabler:route" :size="24" color="#42A5F5" />
          <text class="section__title">在路上</text>
          <text class="section__count">{{ pendingList.length }}</text>
        </view>
        <view class="envelope-list">
          <view
            v-for="(item, index) in pendingList"
            :key="item.id"
            class="envelope-card animate-fade-in-up"
            :class="{ 'envelope-card--ready': canOpen(item) }"
            :style="{ animationDelay: `${150 + index * 60}ms` }"
            @tap="onTap(item)"
            @longpress="deleteCapsule(item)"
          >
            <view class="envelope-card__seal" :class="{ 'envelope-card__seal--ready': canOpen(item) }">
              <KdIcon :name="canOpen(item) ? 'tabler:lock-open' : 'tabler:lock'" :size="24" color="#fff" />
            </view>
            <view class="envelope-card__body">
              <view class="envelope-card__timeline">
                <text class="envelope-card__date">{{ formatDateShort(item.created_at) }}</text>
                <view class="envelope-card__line">
                  <view class="envelope-card__line-fill" :style="{ width: getProgress(item) + '%' }" />
                </view>
                <text class="envelope-card__date">{{ formatDateShort(item.open_at) }}</text>
              </view>
              <text class="envelope-card__preview">{{ item.content.slice(0, 20) }}...</text>
              <text v-if="canOpen(item)" class="envelope-card__ready">可以开启了</text>
              <text v-else class="envelope-card__days">还有 {{ daysLeft(item.open_at) }} 天</text>
            </view>
            <KdIcon v-if="canOpen(item)" name="tabler:chevron-right" :size="24" color="#1565C0" />
          </view>
        </view>
      </view>

      <!-- 待开启 -->
      <view v-if="overdueList.length" class="section animate-soft-slide" style="animation-delay: 200ms">
        <view class="section__header">
          <KdIcon name="tabler:lock-open" :size="24" color="#1565C0" />
          <text class="section__title">待开启</text>
          <text class="section__count section__count--alert">{{ overdueList.length }}</text>
        </view>
        <view class="envelope-list">
          <view
            v-for="(item, index) in overdueList"
            :key="item.id"
            class="envelope-card envelope-card--ready animate-fade-in-up"
            :style="{ animationDelay: `${250 + index * 60}ms` }"
            @tap="openCapsule(item)"
            @longpress="deleteCapsule(item)"
          >
            <view class="envelope-card__seal envelope-card__seal--ready">
              <KdIcon name="tabler:lock-open" :size="24" color="#fff" />
            </view>
            <view class="envelope-card__body">
              <text class="envelope-card__preview">{{ item.content.slice(0, 20) }}...</text>
              <text class="envelope-card__ready">可以开启了</text>
            </view>
            <view class="envelope-card__open-btn">
              <KdIcon name="tabler:mail-opened" :size="20" color="#fff" />
              <text class="envelope-card__open-text">开启</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 已送达 -->
      <view v-if="openedList.length" class="section animate-soft-slide" style="animation-delay: 300ms">
        <view class="section__header">
          <KdIcon name="tabler:mail-opened" :size="24" color="#80CBC4" />
          <text class="section__title">已送达</text>
          <text class="section__count">{{ openedList.length }}</text>
        </view>
        <view class="envelope-list">
          <view
            v-for="(item, index) in openedList"
            :key="item.id"
            class="letter-card animate-fade-in-up"
            :style="{ animationDelay: `${350 + index * 60}ms` }"
            @tap="goDetail(item.id)"
            @longpress="deleteCapsule(item)"
          >
            <view class="letter-card__icon">
              <KdIcon name="tabler:mail-opened" :size="28" color="#80CBC4" />
            </view>
            <view class="letter-card__info">
              <text class="letter-card__preview">{{ item.content.slice(0, 25) }}...</text>
              <text class="letter-card__date">开启于 {{ formatDate(item.open_at) }}</text>
            </view>
            <KdIcon name="tabler:chevron-right" :size="24" color="#ccc" />
          </view>
        </view>
      </view>
    </view>

    <!-- FAB 写信按钮 -->
    <view class="fab-wrap" v-if="!loading">
      <view class="fab" @tap="goCreate">
        <KdIcon name="tabler:pen" :size="48" color="#fff" />
      </view>
      <view class="fab-ring" />
    </view>
  </view>

  <KdDialog
    :visible="showDeleteConfirm"
    title="删除信件"
    content="这封来自过去的信将永远消失"
    confirm-color="#EF5350"
    @close="showDeleteConfirm = false"
    @confirm="onDeleteConfirm"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'
import { capsuleApi, type Capsule } from '@/api/capsule'
import KdIcon from '@/components/KdIcon.vue'
import KdDialog from '@/components/KdDialog.vue'

const list = ref<Capsule[]>([])
const loading = ref(true)
const showDeleteConfirm = ref(false)
const deleteTargetId = ref('')

const pendingList = computed(() =>
  list.value
    .filter(c => !c.is_opened && !canOpen(c))
    .sort((a, b) => new Date(a.open_at).getTime() - new Date(b.open_at).getTime())
)
const openedList = computed(() => list.value.filter(c => c.is_opened))
const overdueList = computed(() => list.value.filter(c => !c.is_opened && canOpen(c)))

const canOpen = (item: Capsule) => !item.is_opened && new Date(item.open_at) <= new Date()

const daysLeft = (openAt: string) => {
  const diff = new Date(openAt).getTime() - Date.now()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
}

const getProgress = (item: Capsule) => {
  const created = new Date(item.created_at).getTime()
  const open = new Date(item.open_at).getTime()
  const now = Date.now()
  const total = open - created
  if (total <= 0) return 100
  return Math.min(100, Math.max(0, ((now - created) / total) * 100))
}

const formatDate = (iso: string) => {
  const d = new Date(iso)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

const formatDateShort = (iso: string) => {
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

const loadList = async () => {
  try { list.value = await capsuleApi.list() } catch {} finally { loading.value = false }
}

const onTap = (item: Capsule) => {
  if (item.is_opened) goDetail(item.id)
  else if (canOpen(item)) openCapsule(item)
}

const goDetail = (id: string) => uni.navigateTo({ url: `/pages/capsule/detail?id=${id}` })

const openCapsule = async (item: Capsule) => {
  try {
    await capsuleApi.open(item.id)
    await loadList()
    goDetail(item.id)
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

const deleteCapsule = (item: Capsule) => {
  deleteTargetId.value = item.id
  showDeleteConfirm.value = true
}
const onDeleteConfirm = async () => {
  try {
    await capsuleApi.delete(deleteTargetId.value)
    uni.showToast({ title: '已删除', icon: 'success' })
    await loadList()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

const goCreate = () => uni.navigateTo({ url: '/pages/capsule/create' })

onMounted(loadList)
onShow(loadList)
onPullDownRefresh(async () => { await loadList(); uni.stopPullDownRefresh() })
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-capsule {
  min-height: 100vh;
  background: linear-gradient(180deg, #E3F2FD 0%, #E8EAF6 30%, #FFF0F2 70%);
  padding: 24rpx 32rpx;
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}

// ========== 加载 ==========
.loading-wrap { display: flex; justify-content: center; padding: 120rpx 0; }
.loading-spinner {
  width: 48rpx; height: 48rpx;
  border: 4rpx solid rgba(66, 165, 245, 0.2);
  border-top-color: $info;
  border-radius: 50%;
}

// ========== 空状态 ==========
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 160rpx 48rpx 0;
  &__icon-wrap { position: relative; margin-bottom: 40rpx; }
  &__icon-bg {
    position: absolute; inset: -24rpx;
    background: $sky-pale;
    border-radius: 50%;
    opacity: 0.5;
  }
  &__title {
    font-size: $font-size-xl; font-weight: $font-weight-bold;
    color: $text-primary; margin-bottom: 12rpx;
  }
  &__desc {
    font-size: $font-size-base; color: $text-secondary;
  }
}

// ========== Hero 卡片 ==========
.hero-card {
  position: relative;
  background: linear-gradient(135deg, #42A5F5 0%, #1E88E5 40%, #1565C0 100%);
  border-radius: 28rpx;
  padding: 44rpx 36rpx 36rpx;
  margin-bottom: 36rpx;
  overflow: hidden;
  box-shadow:
    0 16rpx 48rpx rgba(21, 101, 192, 0.25),
    0 4rpx 12rpx rgba(66, 165, 245, 0.15),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.15);
  opacity: 0;

  &__bg {
    position: absolute; top: -60%; right: -30%;
    width: 360rpx; height: 360rpx;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 50%;
  }

  &__dot {
    position: absolute; border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
    &--1 { width: 120rpx; height: 120rpx; top: -30rpx; left: -30rpx; animation: float 6s ease-in-out infinite; }
    &--2 { width: 80rpx; height: 80rpx; bottom: -20rpx; right: 60rpx; animation: float 8s ease-in-out infinite reverse; }
  }

  &__content { position: relative; z-index: 1; }

  &__stats {
    display: flex; align-items: center;
    justify-content: space-around;
    margin-bottom: 24rpx;
  }
  &__stat { display: flex; flex-direction: column; align-items: center; }
  &__num {
    font-size: 52rpx; font-weight: $font-weight-bold;
    font-family: $font-family-number;
    color: #fff; line-height: 1;
    text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
  }
  &__label {
    font-size: 22rpx; color: rgba(255, 255, 255, 0.75);
    margin-top: 8rpx;
  }
  &__divider {
    width: 2rpx; height: 48rpx;
    background: rgba(255, 255, 255, 0.2);
  }
  &__hint {
    display: block; font-size: 22rpx;
    color: rgba(255, 255, 255, 0.6);
    text-align: center;
    padding-top: 16rpx;
    border-top: 2rpx solid rgba(255, 255, 255, 0.12);
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8rpx); }
}

// ========== 区块标题 ==========
.section {
  margin-bottom: 36rpx; opacity: 0;
  &__header {
    display: flex; align-items: center; gap: 12rpx;
    margin-bottom: 20rpx;
    padding-left: 4rpx;
  }
  &__title {
    font-size: 30rpx; font-weight: $font-weight-semibold;
    color: $text-primary; flex: 1;
    letter-spacing: 1rpx;
  }
  &__count {
    font-size: 20rpx; font-family: $font-family-number;
    color: $text-tertiary;
    background: rgba(66, 165, 245, 0.08);
    border-radius: $radius-full;
    padding: 4rpx 16rpx;
    min-width: 36rpx;
    text-align: center;
    &--alert {
      color: #1565C0;
      background: rgba(66, 165, 245, 0.12);
      font-weight: $font-weight-semibold;
    }
  }
}

// ========== 信封卡片 ==========
.envelope-list { display: flex; flex-direction: column; gap: 16rpx; }

.envelope-card {
  display: flex; align-items: center;
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 24rpx;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    0 8rpx 24rpx rgba(66, 165, 245, 0.06);
  opacity: 0;
  transition: transform $duration-fast $ease-soft;
  &:active { transform: scale(0.98); }

  &--ready {
    background: #E3F2FD;
    box-shadow:
      0 4rpx 16rpx rgba(66, 165, 245, 0.15),
      0 8rpx 32rpx rgba(21, 101, 192, 0.08);
    border: 2rpx solid rgba(66, 165, 245, 0.12);
  }

  &__seal {
    width: 52rpx; height: 52rpx;
    border-radius: 16rpx;
    background: linear-gradient(135deg, $sky-light, $info);
    display: flex; align-items: center; justify-content: center;
    margin-right: 20rpx; flex-shrink: 0;
    box-shadow: 0 4rpx 12rpx rgba(66, 165, 245, 0.2);
    &--ready {
      background: linear-gradient(135deg, #1976D2, #1565C0);
      box-shadow: 0 4rpx 16rpx rgba(21, 101, 192, 0.3);
    }
  }

  &__body { flex: 1; min-width: 0; }

  &__timeline {
    display: flex; align-items: center; gap: 10rpx;
    margin-bottom: 10rpx;
  }
  &__date {
    font-size: 20rpx; color: $text-tertiary;
    font-family: $font-family-number;
    flex-shrink: 0;
  }
  &__line {
    flex: 1; height: 6rpx;
    background: $border-light;
    border-radius: 3rpx;
    overflow: hidden;
  }
  &__line-fill {
    height: 100%;
    background: linear-gradient(90deg, $sky-light, $info);
    border-radius: 3rpx;
    transition: width 0.6s $ease-soft;
  }

  &__preview {
    font-size: $font-size-base; color: $text-primary;
    font-weight: $font-weight-medium;
    display: block;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    margin-bottom: 6rpx;
  }
  &__days {
    font-size: $font-size-sm; color: $info;
    font-weight: $font-weight-medium;
  }
  &__ready {
    font-size: $font-size-sm; color: #1565C0;
    font-weight: $font-weight-semibold;
  }

  &__open-btn {
    display: flex; align-items: center; gap: 6rpx;
    padding: 12rpx 24rpx;
    background: linear-gradient(135deg, $info, #1565C0);
    border-radius: $radius-full;
    flex-shrink: 0; margin-left: 16rpx;
    box-shadow: 0 4rpx 12rpx rgba(245, 124, 0, 0.2);
  }
  &__open-text {
    font-size: $font-size-sm; color: #fff;
    font-weight: $font-weight-semibold;
  }
}

// ========== 已送达 ==========
.letter-card {
  display: flex; align-items: center;
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 24rpx;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    0 4rpx 16rpx rgba(128, 203, 196, 0.08);
  opacity: 0;
  transition: transform $duration-fast $ease-soft;
  &:active { transform: scale(0.98); }

  &__icon {
    width: 52rpx; height: 52rpx;
    border-radius: 16rpx;
    background: $mint-pale;
    display: flex; align-items: center; justify-content: center;
    margin-right: 20rpx; flex-shrink: 0;
  }
  &__info { flex: 1; min-width: 0; }
  &__preview {
    font-size: $font-size-base; color: $text-primary;
    font-weight: $font-weight-medium;
    display: block;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  &__date {
    font-size: $font-size-sm; color: $text-tertiary;
    display: block; margin-top: 6rpx;
  }
}

// ========== FAB 写信按钮 ==========
.fab-wrap {
  position: fixed;
  right: 40rpx;
  bottom: calc(160rpx + env(safe-area-inset-bottom));
  z-index: 100;
}

.fab {
  width: 112rpx;
  height: 112rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #42A5F5, #1E88E5);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
  box-shadow:
    0 8rpx 32rpx rgba(66, 165, 245, 0.35),
    0 2rpx 8rpx rgba(21, 101, 192, 0.2);
  transition: transform $duration-fast $ease-soft;
  &:active { transform: scale(0.9); }
}

.fab-ring {
  position: absolute;
  inset: -8rpx;
  border-radius: 50%;
  border: 2rpx solid rgba(66, 165, 245, 0.3);
  animation: fabRingPulse 2s ease-in-out infinite;
}

@keyframes fabRingPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.15); opacity: 0; }
}
</style>
