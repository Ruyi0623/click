<template>
  <view class="page-detail">
    <!-- 加载状态 -->
    <view v-if="loading" class="loading-wrap">
      <view class="loading-spinner animate-spin" />
    </view>

    <!-- 开启动画层 -->
    <view v-else-if="showAnimation" class="animation-overlay animate-fade-in" @tap="skipAnimation">
      <view class="animation-seal">
        <view class="animation-seal__icon">
          <KdIcon name="tabler:mail-opened" :size="64" color="#42A5F5" />
        </view>
        <view class="animation-seal__burst">
          <view v-for="i in 8" :key="i" class="burst-particle" :style="{ '--angle': `${i * 45}deg` }" />
        </view>
      </view>
      <text class="animation-title">信件已送达</text>
      <text class="animation-subtitle">来自过去的讯息</text>
      <text class="animation-skip">点击跳过</text>
    </view>

    <!-- 内容区 -->
    <view v-else-if="capsule" class="detail-body">
      <!-- 信件头部 -->
      <view class="letter-header animate-zoom-in">
        <view class="letter-header__icon-wrap">
          <view class="letter-header__icon-bg" />
          <KdIcon name="tabler:mail-opened" :size="48" color="#42A5F5" />
        </view>
        <text class="letter-header__title">来自过去的信</text>
        <text class="letter-header__subtitle">已送达 {{ formatDate(capsule.open_at) }}</text>
      </view>

      <!-- 信件内容 -->
      <view class="letter-card animate-card-slide" style="animation-delay: 150ms">
        <view class="letter-card__corner letter-card__corner--tl" />
        <view class="letter-card__corner letter-card__corner--tr" />
        <view class="letter-card__corner letter-card__corner--bl" />
        <view class="letter-card__corner letter-card__corner--br" />
        <text class="letter-card__text">{{ capsule.content }}</text>
      </view>

      <!-- 信件信息 -->
      <view class="letter-meta animate-card-slide" style="animation-delay: 250ms">
        <view class="letter-meta__row">
          <view class="letter-meta__icon">
            <KdIcon name="tabler:lock" :size="20" color="#fff" />
          </view>
          <view class="letter-meta__info">
            <text class="letter-meta__label">封存时间</text>
            <text class="letter-meta__value">{{ formatDate(capsule.created_at) }}</text>
          </view>
        </view>
        <view class="letter-meta__divider" />
        <view class="letter-meta__row">
          <view class="letter-meta__icon">
            <KdIcon name="tabler:lock-open" :size="20" color="#fff" />
          </view>
          <view class="letter-meta__info">
            <text class="letter-meta__label">开启时间</text>
            <text class="letter-meta__value">{{ formatDate(capsule.open_at) }}</text>
          </view>
        </view>
        <view class="letter-meta__divider" />
        <view class="letter-meta__row">
          <view class="letter-meta__icon">
            <KdIcon name="tabler:hourglass" :size="20" color="#fff" />
          </view>
          <view class="letter-meta__info">
            <text class="letter-meta__label">封存时长</text>
            <text class="letter-meta__value letter-meta__value--highlight">{{ daysBetween }} 天</text>
          </view>
        </view>
      </view>

      <!-- 底部署名 -->
      <view class="letter-footer animate-fade-in" style="animation-delay: 350ms">
        <view class="letter-footer__line" />
        <text class="letter-footer__text">咔哒 · 星际邮局</text>
        <view class="letter-footer__line" />
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { capsuleApi, type Capsule } from '@/api/capsule'
import KdIcon from '@/components/KdIcon.vue'

const capsule = ref<Capsule | null>(null)
const loading = ref(true)
const showAnimation = ref(false)

const daysBetween = computed(() => {
  if (!capsule.value) return 0
  const created = new Date(capsule.value.created_at)
  const opened = new Date(capsule.value.open_at)
  return Math.round((opened.getTime() - created.getTime()) / (1000 * 60 * 60 * 24))
})

const formatDate = (iso: string) => {
  const d = new Date(iso)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

const skipAnimation = () => { showAnimation.value = false }

onLoad(async (query: any) => {
  if (!query?.id) return
  try {
    capsule.value = await capsuleApi.get(query.id)
    if (query.animate === '1') {
      showAnimation.value = true
      setTimeout(() => { showAnimation.value = false }, 3000)
    }
  } catch {} finally { loading.value = false }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-detail {
  min-height: 100vh;
  background: linear-gradient(180deg, #E3F2FD 0%, #E8EAF6 30%, #FFF0F2 70%);
}

.loading-wrap { display: flex; justify-content: center; padding: 120rpx 0; }
.loading-spinner {
  width: 48rpx; height: 48rpx;
  border: 4rpx solid rgba(66, 165, 245, 0.2);
  border-top-color: $info;
  border-radius: 50%;
}

// ========== 开启动画 ==========
.animation-overlay {
  position: fixed; inset: 0;
  background: rgba(255, 248, 225, 0.97);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  z-index: 1000;
}

.animation-seal {
  position: relative; margin-bottom: 40rpx;
  &__icon {
    width: 140rpx; height: 140rpx;
    background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    animation: sealPop 0.6s $ease-spring forwards;
    box-shadow:
      0 8rpx 32rpx rgba(66, 165, 245, 0.2),
      0 0 60rpx rgba(66, 165, 245, 0.15),
      inset 0 2rpx 0 rgba(255, 255, 255, 0.5);
  }
  &__burst {
    position: absolute; top: 50%; left: 50%;
    width: 0; height: 0;
  }
}

.burst-particle {
  position: absolute;
  width: 12rpx; height: 12rpx;
  border-radius: 50%;
  background: $info;
  top: 0; left: 0; opacity: 0;
  animation: burstOut 1s 0.3s ease-out forwards;
  transform: rotate(var(--angle)) translateX(0);
}

@keyframes sealPop {
  0% { transform: scale(0.3); opacity: 0; }
  60% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes burstOut {
  0% { opacity: 1; transform: rotate(var(--angle)) translateX(0) scale(1); }
  100% { opacity: 0; transform: rotate(var(--angle)) translateX(120rpx) scale(0); }
}

.animation-title {
  font-size: $font-size-xxl; font-weight: $font-weight-bold;
  color: $info;
  margin-top: 24rpx;
  animation: fadeInUp 0.5s 0.5s $ease-soft forwards;
  opacity: 0;
}
.animation-subtitle {
  font-size: $font-size-base; color: $text-secondary;
  margin-top: 12rpx;
  animation: fadeInUp 0.5s 0.7s $ease-soft forwards;
  opacity: 0;
}
.animation-skip {
  font-size: $font-size-sm; color: $text-tertiary;
  margin-top: 60rpx;
  animation: fadeInUp 0.5s 1s $ease-soft forwards;
  opacity: 0;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16rpx); }
  to { opacity: 1; transform: translateY(0); }
}

// ========== 内容区 ==========
.detail-body {
  padding: 32rpx;
  padding-bottom: calc(80rpx + env(safe-area-inset-bottom));
}

// ========== 信件头部 ==========
.letter-header {
  text-align: center;
  padding: 32rpx 0 48rpx;
  opacity: 0;

  &__icon-wrap {
    position: relative;
    display: inline-flex;
    margin-bottom: 24rpx;
  }
  &__icon-bg {
    position: absolute; inset: -20rpx;
    background: $sky-pale;
    border-radius: 50%;
    opacity: 0.5;
  }

  &__title {
    font-size: $font-size-xl; font-weight: $font-weight-bold;
    color: $text-primary;
    display: block; margin-bottom: 8rpx;
  }
  &__subtitle {
    font-size: $font-size-sm; color: $text-secondary;
    display: block;
  }
}

// ========== 信件卡片 ==========
.letter-card {
  position: relative;
  background: $bg-card;
  border-radius: $radius-xl;
  padding: 48rpx 36rpx;
  margin-bottom: 32rpx;
  box-shadow:
    0 4rpx 20rpx rgba(0, 0, 0, 0.04),
    0 12rpx 40rpx rgba(66, 165, 245, 0.06),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.8);
  opacity: 0;

  &__corner {
    position: absolute;
    width: 24rpx; height: 24rpx;
    border-color: $sky-light;
    border-style: solid; border-width: 0;
    &--tl { top: 12rpx; left: 12rpx; border-top-width: 4rpx; border-left-width: 4rpx; border-radius: 8rpx 0 0 0; }
    &--tr { top: 12rpx; right: 12rpx; border-top-width: 4rpx; border-right-width: 4rpx; border-radius: 0 8rpx 0 0; }
    &--bl { bottom: 12rpx; left: 12rpx; border-bottom-width: 4rpx; border-left-width: 4rpx; border-radius: 0 0 0 8rpx; }
    &--br { bottom: 12rpx; right: 12rpx; border-bottom-width: 4rpx; border-right-width: 4rpx; border-radius: 0 0 8rpx 0; }
  }

  &__text {
    font-size: $font-size-md; color: $text-primary;
    line-height: 1.8; display: block;
  }
}

// ========== 信件信息 ==========
.letter-meta {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 8rpx 28rpx;
  margin-bottom: 48rpx;
  box-shadow:
    0 2rpx 12rpx rgba(0, 0, 0, 0.04),
    0 8rpx 24rpx rgba(66, 165, 245, 0.05);
  opacity: 0;

  &__row {
    display: flex; align-items: center; gap: 20rpx;
    padding: 20rpx 0;
  }
  &__icon {
    width: 44rpx; height: 44rpx;
    background: linear-gradient(135deg, #42A5F5, #1E88E5);
    border-radius: 14rpx;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  &__info { flex: 1; }
  &__label {
    font-size: $font-size-sm; color: $text-tertiary;
    display: block; margin-bottom: 4rpx;
  }
  &__value {
    font-size: $font-size-base; color: $text-primary;
    display: block;
    &--highlight { color: $info; font-weight: $font-weight-semibold; }
  }
  &__divider {
    height: 2rpx; background: $border-light;
    margin: 0 8rpx;
  }
}

// ========== 底部署名 ==========
.letter-footer {
  display: flex; align-items: center; justify-content: center;
  gap: 24rpx; padding: 16rpx 0;
  opacity: 0;
  &__line { width: 64rpx; height: 2rpx; background: $border-normal; }
  &__text {
    font-size: $font-size-sm; color: $text-tertiary;
    letter-spacing: 4rpx;
  }
}
</style>
