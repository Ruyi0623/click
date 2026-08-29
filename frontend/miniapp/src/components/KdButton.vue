<template>
  <button
    class="kd-btn"
    :class="[`kd-btn--${type}`, { 'kd-btn--block': block, 'kd-btn--disabled': disabled, 'kd-btn--loading': loading }]"
    :disabled="disabled || loading"
    @tap="handleTap"
  >
    <view v-if="loading" class="kd-btn__loading animate-spin" />
    <slot />
  </button>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  type?: 'primary' | 'secondary' | 'text'
  block?: boolean
  disabled?: boolean
  loading?: boolean
}>(), {
  type: 'primary',
  block: false,
  disabled: false,
  loading: false,
})

const emit = defineEmits<{ tap: [] }>()
const handleTap = () => emit('tap')
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.kd-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: $radius-full;
  height: 96rpx;
  padding: 0 64rpx;
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  border: none;
  line-height: 1;
  transition: all $duration-normal $ease-soft;
  &::after { display: none; }

  &--primary {
    background: $gradient-heart;
    color: $text-inverse;
    box-shadow: $shadow-glow;
    &:active { transform: scale(0.96); box-shadow: none; }
  }
  &--secondary {
    background: transparent;
    color: $heart-pink;
    border: 2rpx solid $heart-pink;
    &:active { background: $heart-pink-ghost; }
  }
  &--text {
    background: transparent;
    color: $heart-pink;
    height: 80rpx;
    padding: 0 32rpx;
    font-size: $font-size-base;
    font-weight: $font-weight-medium;
    &:active { opacity: 0.7; }
  }
  &--block { width: 100%; }
  &--disabled { opacity: 0.5; pointer-events: none; }
  &--loading { pointer-events: none; }

  &__loading {
    width: 36rpx;
    height: 36rpx;
    border: 4rpx solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    margin-right: 16rpx;
  }
}
</style>
