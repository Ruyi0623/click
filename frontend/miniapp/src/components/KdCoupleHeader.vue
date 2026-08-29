<template>
  <view class="kd-couple-header">
    <view class="kd-couple-header__avatars">
      <image class="kd-couple-header__avatar" :src="myAvatar || '/static/images/default-avatar.png'" mode="aspectFill" />
      <view class="kd-couple-header__heart">
        <KdIcon name="tabler:heart" :size="24" color="#fff" />
      </view>
      <image class="kd-couple-header__avatar" :src="partnerAvatar || '/static/images/default-avatar.png'" mode="aspectFill" />
    </view>
    <view v-if="showDays" class="kd-couple-header__days">
      <text class="kd-couple-header__label">我们已经在一起</text>
      <view class="kd-couple-header__number-wrap">
        <text class="kd-couple-header__number animate-heartbeat">{{ days }}</text>
        <text class="kd-couple-header__unit">天</text>
      </view>
      <text v-if="startDate" class="kd-couple-header__since">{{ startDate }} 至今</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import KdIcon from '@/components/KdIcon.vue'

withDefaults(defineProps<{
  myAvatar?: string
  partnerAvatar?: string
  days?: number
  startDate?: string
  showDays?: boolean
}>(), {
  showDays: true,
  days: 0,
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.kd-couple-header {
  display: flex;
  flex-direction: column;
  align-items: center;

  &__avatars {
    display: flex;
    align-items: center;
    margin-bottom: 32rpx;
  }
  &__avatar {
    width: 96rpx;
    height: 96rpx;
    border-radius: $radius-full;
    border: 4rpx solid $bg-card;
    box-shadow: $shadow-sm;
    &:last-child { margin-left: -24rpx; z-index: 1; }
    &:first-child { z-index: 2; }
  }
  &__heart {
    width: 48rpx;
    height: 48rpx;
    margin: 0 -12rpx;
    z-index: 3;
    background: $gradient-heart;
    border-radius: $radius-full;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: $shadow-glow;
    &-icon { font-size: 24rpx; color: #fff; }
  }

  &__days { text-align: center; }
  &__label {
    font-size: $font-size-base;
    color: $text-secondary;
    display: block;
    margin-bottom: 16rpx;
  }
  &__number-wrap {
    display: flex;
    align-items: baseline;
    justify-content: center;
    margin-bottom: 16rpx;
  }
  &__number {
    font-size: 144rpx;
    font-weight: $font-weight-bold;
    color: $heart-pink;
    font-family: $font-family-number;
    line-height: 1;
    text-shadow: 0 4rpx 16rpx rgba(255, 107, 138, 0.3);
  }
  &__unit {
    font-size: $font-size-xl;
    color: $heart-pink-light;
    margin-left: 12rpx;
    font-weight: $font-weight-medium;
  }
  &__since {
    font-size: $font-size-sm;
    color: $text-tertiary;
  }
}
</style>
