<template>
  <view class="kd-dialog" v-if="visible">
    <view class="kd-dialog__mask" @tap="onCancel" />
    <view class="kd-dialog__card">
      <view class="kd-dialog__accent" />
      <text class="kd-dialog__title">{{ title }}</text>

      <text v-if="content && !showInput" class="kd-dialog__body">{{ content }}</text>

      <view v-if="showInput" class="kd-dialog__input-wrap">
        <input
          class="kd-dialog__input"
          :value="inputValue"
          :placeholder="inputPlaceholder"
          :focus="visible"
          @input="onInput"
          @confirm="onConfirm"
        />
      </view>

      <view class="kd-dialog__actions">
        <view v-if="showCancel" class="kd-dialog__btn kd-dialog__btn--cancel" @tap="onCancel">
          <text>{{ cancelText }}</text>
        </view>
        <view
          class="kd-dialog__btn kd-dialog__btn--confirm"
          :style="confirmColor !== '#FF6B8A' ? { background: confirmColor, boxShadow: `0 0 24rpx ${confirmColor}40` } : undefined"
          @tap="onConfirm"
        >
          <text>{{ confirmText }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(defineProps<{
  visible: boolean
  title: string
  content?: string
  showInput?: boolean
  inputPlaceholder?: string
  inputValue?: string
  confirmText?: string
  cancelText?: string
  confirmColor?: string
  showCancel?: boolean
}>(), {
  confirmText: '确认',
  cancelText: '取消',
  confirmColor: '#FF6B8A',
  showCancel: true,
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  close: []
  confirm: [value?: string]
  cancel: []
}>()

const currentValue = ref('')

const onInput = (e: any) => {
  currentValue.value = e.detail.value
}

const onConfirm = () => {
  if (props.showInput) {
    emit('confirm', currentValue.value || props.inputValue || '')
  } else {
    emit('confirm')
  }
  currentValue.value = ''
  emit('update:visible', false)
  emit('close')
}

const onCancel = () => {
  currentValue.value = ''
  emit('cancel')
  emit('update:visible', false)
  emit('close')
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.kd-dialog {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;

  &__mask {
    position: absolute;
    inset: 0;
    background: $bg-mask;
    animation: fadeIn $duration-normal $ease-soft;
  }

  &__card {
    position: relative;
    width: 560rpx;
    background: $bg-card;
    border-radius: $radius-xl;
    padding: 44rpx 40rpx 0;
    box-shadow: $shadow-xl, 0 0 80rpx rgba(255, 107, 138, 0.08);
    overflow: hidden;
    animation: dialogIn $duration-normal $ease-spring;
  }

  &__accent {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 80rpx;
    height: 6rpx;
    border-radius: 0 0 6rpx 6rpx;
    background: $gradient-heart;
    opacity: 0.7;
  }

  &__title {
    display: block;
    text-align: center;
    font-size: $font-size-md;
    font-weight: $font-weight-semibold;
    color: $text-primary;
    letter-spacing: 0.5rpx;
    margin-bottom: 16rpx;
  }

  &__body {
    display: block;
    text-align: center;
    font-size: $font-size-base;
    color: $text-secondary;
    line-height: $line-height-relaxed;
    padding: 0 8rpx;
    margin-bottom: 36rpx;
  }

  &__input-wrap {
    margin-bottom: 36rpx;
  }

  &__input {
    width: 100%;
    height: 80rpx;
    background: $bg-page;
    border: 2rpx solid $border-light;
    border-radius: $radius-base;
    padding: 0 24rpx;
    font-size: $font-size-base;
    color: $text-primary;
    box-sizing: border-box;
    transition: border-color $duration-fast $ease-soft, box-shadow $duration-fast $ease-soft;

    &:focus {
      border-color: $heart-pink-light;
      box-shadow: 0 0 0 6rpx rgba($heart-pink, 0.08);
    }
  }

  &__actions {
    display: flex;
    gap: 20rpx;
    padding: 24rpx 0;
    padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  }

  &__btn {
    flex: 1;
    height: 80rpx;
    border-radius: $radius-full;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: $font-size-base;
    transition: transform $duration-fast $ease-soft, opacity $duration-fast $ease-soft;

    &:active {
      transform: scale(0.96);
      opacity: 0.85;
    }

    &--cancel {
      background: $bg-page;
      color: $text-secondary;
      font-weight: $font-weight-medium;
    }

    &--confirm {
      background: $gradient-heart;
      color: $text-inverse;
      font-weight: $font-weight-semibold;
      box-shadow: $shadow-glow;
    }
  }
}

@keyframes dialogIn {
  from {
    opacity: 0;
    transform: scale(0.92);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
