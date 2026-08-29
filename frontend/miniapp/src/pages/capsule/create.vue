<template>
  <view class="page-create">
    <view class="content">
      <!-- 标题 -->
      <view class="header animate-zoom-in">
        <view class="header__icon-wrap">
          <view class="header__icon-bg" />
          <KdIcon name="tabler:mail" :size="48" color="#42A5F5" />
        </view>
        <text class="header__title">写一封信</text>
        <text class="header__subtitle">寄给未来的你们</text>
      </view>

      <!-- 信纸表单 -->
      <view class="letter-form animate-card-slide" style="animation-delay: 150ms">
        <view class="letter-form__header">
          <KdIcon name="tabler:calendar" :size="20" color="#42A5F5" />
          <text class="letter-form__date">{{ todayStr }}</text>
        </view>
        <view class="letter-form__body">
          <textarea
            class="letter-form__textarea"
            v-model="content"
            placeholder="写下你想对未来说的话..."
            maxlength="500"
            :placeholder-style="placeholderStyle"
          />
          <text class="letter-form__count">{{ content.length }} / 500</text>
        </view>
      </view>

      <!-- 开启时间 -->
      <view class="time-section animate-card-slide" style="animation-delay: 250ms">
        <view class="time-section__header">
          <KdIcon name="tabler:clock" :size="24" color="#42A5F5" />
          <text class="time-section__title">设定开启时间</text>
        </view>
        <picker mode="date" :start="minDate" @change="onDateChange">
          <view class="time-picker" :class="{ 'time-picker--selected': openDate }">
            <view class="time-picker__icon">
              <KdIcon :name="openDate ? 'tabler:lock-open' : 'tabler:lock'" :size="24" color="#fff" />
            </view>
            <view class="time-picker__info">
              <text class="time-picker__label">{{ openDate ? '开启日期' : '选择日期' }}</text>
              <text class="time-picker__value">{{ openDate || '点击选择' }}</text>
            </view>
            <KdIcon name="tabler:chevron-right" :size="24" color="#ccc" />
          </view>
        </picker>
        <view v-if="openDate" class="time-section__hint">
          <KdIcon name="tabler:hourglass" :size="20" color="#42A5F5" />
          <text class="time-section__hint-text">信件将在 {{ daysUntil }} 天后送达</text>
        </view>
      </view>

      <!-- 封存按钮 -->
      <view class="submit-section animate-fade-in-up" style="animation-delay: 350ms">
        <button
          class="submit-btn"
          :class="{ 'submit-btn--disabled': !content.trim() || !openDate || loading }"
          :disabled="!content.trim() || !openDate || loading"
          @tap="submit"
        >
          <view class="submit-btn__inner">
            <KdIcon v-if="!loading" name="tabler:send" :size="28" color="#fff" />
            <view v-else class="submit-btn__loading" />
            <text class="submit-btn__text">{{ loading ? '封存中...' : '封存信件' }}</text>
          </view>
        </button>
        <text class="submit-hint">封存后将无法修改</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { capsuleApi } from '@/api/capsule'
import KdIcon from '@/components/KdIcon.vue'

const content = ref('')
const openDate = ref('')
const loading = ref(false)
const placeholderStyle = 'color: #9E9EB0; font-size: 30rpx; line-height: 1.8;'

const todayStr = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
})

const minDate = computed(() => {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
})

const daysUntil = computed(() => {
  if (!openDate.value) return 0
  const diff = new Date(openDate.value).getTime() - Date.now()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
})

const onDateChange = (e: any) => { openDate.value = e.detail.value }

const submit = async () => {
  if (!content.value.trim() || !openDate.value || loading.value) return
  loading.value = true
  try {
    await capsuleApi.create(content.value, `${openDate.value}T00:00:00`)
    uni.showToast({ title: '信件已封存', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-create {
  min-height: 100vh;
  background: linear-gradient(180deg, #E3F2FD 0%, #E8EAF6 30%, #FFF0F2 70%);
}

.content {
  padding: 32rpx;
  padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
}

// ========== 标题 ==========
.header {
  text-align: center;
  padding: 24rpx 0 48rpx;
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
    font-size: $font-size-xxl; font-weight: $font-weight-bold;
    color: $text-primary;
    display: block; margin-bottom: 8rpx;
  }
  &__subtitle {
    font-size: $font-size-base; color: $text-secondary;
    display: block;
  }
}

// ========== 信纸表单 ==========
.letter-form {
  background: $bg-card;
  border-radius: $radius-xl;
  margin-bottom: 32rpx;
  overflow: hidden;
  box-shadow:
    0 4rpx 20rpx rgba(0, 0, 0, 0.04),
    0 12rpx 40rpx rgba(66, 165, 245, 0.06),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.8);
  opacity: 0;

  &__header {
    display: flex; align-items: center; gap: 10rpx;
    padding: 20rpx 28rpx;
    border-bottom: 2rpx solid $border-light;
  }
  &__date {
    font-size: $font-size-sm; color: $info;
    font-weight: $font-weight-medium;
  }

  &__body { padding: 24rpx 28rpx; }

  &__textarea {
    width: 100%; height: 320rpx;
    background: transparent; border: none;
    font-size: $font-size-md; color: $text-primary;
    line-height: 1.8; padding: 0;
  }
  &__count {
    display: block; text-align: right;
    font-size: $font-size-xs; color: $text-tertiary;
    margin-top: 16rpx; font-family: $font-family-number;
  }
}

// ========== 开启时间 ==========
.time-section {
  margin-bottom: 48rpx;
  opacity: 0;

  &__header {
    display: flex; align-items: center; gap: 10rpx;
    margin-bottom: 20rpx;
  }
  &__title {
    font-size: $font-size-md; font-weight: $font-weight-semibold;
    color: $text-primary;
  }
  &__hint {
    display: flex; align-items: center; gap: 8rpx;
    margin-top: 16rpx; padding-left: 4rpx;
  }
  &__hint-text {
    font-size: $font-size-sm; color: $info;
    font-weight: $font-weight-medium;
  }
}

.time-picker {
  display: flex; align-items: center; gap: 20rpx;
  background: $bg-card;
  border: 2rpx solid $border-light;
  border-radius: $radius-lg;
  padding: 28rpx;
  box-shadow:
    0 2rpx 12rpx rgba(0, 0, 0, 0.03),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.8);
  transition: all $duration-normal $ease-soft;

  &--selected {
    border-color: rgba(66, 165, 245, 0.3);
    background: $sky-pale;
    box-shadow:
      0 4rpx 16rpx rgba(66, 165, 245, 0.12),
      inset 0 1rpx 0 rgba(255, 255, 255, 0.6);
  }

  &__icon {
    width: 52rpx; height: 52rpx;
    background: linear-gradient(135deg, #42A5F5, #1E88E5);
    border-radius: 16rpx;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 4rpx 12rpx rgba(66, 165, 245, 0.2);
  }
  &__info { flex: 1; }
  &__label {
    font-size: $font-size-sm; color: $text-tertiary;
    display: block; margin-bottom: 4rpx;
  }
  &__value {
    font-size: $font-size-md; color: $text-primary;
    display: block;
  }
}

// ========== 封存按钮 ==========
.submit-section { text-align: center; opacity: 0; }

.submit-btn {
  width: 100%; height: 104rpx;
  background: linear-gradient(135deg, #42A5F5 0%, #1E88E5 50%, #1976D2 100%);
  border: none; border-radius: $radius-full;
  padding: 0; margin: 0;
  box-shadow:
    0 8rpx 32rpx rgba(66, 165, 245, 0.3),
    0 2rpx 8rpx rgba(21, 101, 192, 0.2),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.2);
  transition: all $duration-normal $ease-soft;
  &::after { display: none; }
  &:active:not(&--disabled) { transform: scale(0.96); }
  &--disabled { opacity: 0.5; box-shadow: none; }

  &__inner {
    display: flex; align-items: center; justify-content: center;
    gap: 12rpx; height: 100%;
  }
  &__text {
    font-size: $font-size-lg; font-weight: $font-weight-semibold;
    color: #fff;
  }
  &__loading {
    width: 36rpx; height: 36rpx;
    border: 4rpx solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin { to { transform: rotate(360deg); } }

.submit-hint {
  display: block; font-size: $font-size-sm;
  color: $text-tertiary; margin-top: 20rpx;
}
</style>
