<template>
  <view class="kd-countdown" @tap="emit('tap')">
    <view class="kd-countdown__icon">
      <KdIcon :name="icon || 'tabler:cake'" :size="40" variant="white" />
    </view>
    <view class="kd-countdown__info">
      <text class="kd-countdown__title">{{ title }}</text>
      <text v-if="date" class="kd-countdown__date">{{ date }}</text>
    </view>
    <view class="kd-countdown__days">
      <text class="kd-countdown__days-num">{{ days }}</text>
      <text class="kd-countdown__days-unit">天后</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import KdIcon from '@/components/KdIcon.vue'

defineProps<{
  icon?: string
  title: string
  date?: string
  days: number
}>()

const emit = defineEmits<{ tap: [] }>()
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.kd-countdown {
  display: flex;
  align-items: center;
  padding: 24rpx;
  border-radius: $radius-base;
  transition: all $duration-fast $ease-soft;
  &:active { background: $bg-page; }

  &__icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: $radius-base;
    background: $gradient-dream;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 24rpx;
    flex-shrink: 0;
    &-text { font-size: 40rpx; }
  }
  &__info {
    flex: 1;
    min-width: 0;
  }
  &__title {
    font-size: $font-size-md;
    color: $text-primary;
    font-weight: $font-weight-medium;
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  &__date {
    font-size: $font-size-sm;
    color: $text-secondary;
    margin-top: 8rpx;
    display: block;
  }
  &__days {
    text-align: center;
    margin-left: 24rpx;
    flex-shrink: 0;
    &-num {
      font-size: $font-size-xxl;
      font-weight: $font-weight-bold;
      color: $heart-pink;
      font-family: $font-family-number;
      display: block;
      line-height: 1;
    }
    &-unit {
      font-size: $font-size-xs;
      color: $text-tertiary;
      display: block;
      margin-top: 4rpx;
    }
  }
}
</style>
