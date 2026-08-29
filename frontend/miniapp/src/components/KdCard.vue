<template>
  <view class="kd-card" :class="[variant && `kd-card--${variant}`]" @tap="emit('tap')">
    <slot />
  </view>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  variant?: 'default' | 'accent' | 'glass'
}>(), {
  variant: 'default',
})

const emit = defineEmits<{ tap: [] }>()
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.kd-card {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: $padding-card;
  box-shadow: $shadow-sm;
  transition: all $duration-normal $ease-soft;

  &--accent {
    position: relative;
    border: 2rpx solid transparent;
    &::before {
      content: '';
      position: absolute;
      inset: -2rpx;
      border-radius: inherit;
      background: $gradient-heart;
      z-index: -1;
      opacity: 0.1;
    }
  }
  &--glass {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    border: 1rpx solid rgba(255, 255, 255, 0.5);
  }
}
</style>
