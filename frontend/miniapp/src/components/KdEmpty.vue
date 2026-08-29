<template>
  <view class="kd-empty">
    <view class="kd-empty__icon animate-float">
      <KdIcon :name="icon" :size="100" />
    </view>
    <text class="kd-empty__title">{{ title }}</text>
    <text v-if="desc" class="kd-empty__desc">{{ desc }}</text>
    <slot />
  </view>
</template>

<script setup lang="ts">
import KdIcon from '@/components/KdIcon.vue'

withDefaults(defineProps<{
  icon?: string
  title: string
  desc?: string
}>(), {
  icon: 'tabler:heart',
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.kd-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 64rpx;

  &__icon {
    width: 200rpx;
    height: 200rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 48rpx;
  }
  &__title {
    font-size: $font-size-lg;
    color: $text-primary;
    font-weight: $font-weight-semibold;
    margin-bottom: 16rpx;
  }
  &__desc {
    font-size: $font-size-base;
    color: $text-secondary;
    text-align: center;
    line-height: $line-height-relaxed;
  }
}
</style>
