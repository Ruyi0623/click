<template>
  <view class="kd-action-sheet" v-if="visible">
    <view class="kd-action-sheet__mask" @tap="close" />
    <view class="kd-action-sheet__sheet">
      <view class="kd-action-sheet__handle" />

      <view v-if="title" class="kd-action-sheet__header">
        <text class="kd-action-sheet__title">{{ title }}</text>
      </view>

      <view class="kd-action-sheet__list">
        <view
          v-for="(action, index) in actions"
          :key="index"
          class="kd-action-sheet__item"
          :class="{ 'kd-action-sheet__item--destructive': action.destructive }"
          @tap="onSelect(action, index)"
        >
          <text
            class="kd-action-sheet__label"
            :style="action.color && !action.destructive ? { color: action.color } : undefined"
          >
            {{ action.label }}
          </text>
        </view>
      </view>

      <view v-if="showCancel" class="kd-action-sheet__cancel" @tap="close">
        <text>取消</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
interface ActionItem {
  label: string
  icon?: string
  color?: string
  destructive?: boolean
}

withDefaults(defineProps<{
  visible: boolean
  title?: string
  actions: ActionItem[]
  showCancel?: boolean
}>(), {
  showCancel: true,
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  close: []
  select: [action: ActionItem, index: number]
}>()

const close = () => {
  emit('update:visible', false)
  emit('close')
}

const onSelect = (action: ActionItem, index: number) => {
  emit('select', action, index)
  emit('update:visible', false)
  emit('close')
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.kd-action-sheet {
  position: fixed;
  inset: 0;
  z-index: 1000;

  &__mask {
    position: absolute;
    inset: 0;
    background: $bg-mask;
    animation: fadeIn $duration-normal $ease-soft;
  }

  &__sheet {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: $bg-page;
    border-radius: $radius-xl $radius-xl 0 0;
    padding: 12rpx 16rpx 0;
    padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
    animation: sheetUp $duration-normal $ease-spring;
  }

  &__handle {
    width: 56rpx;
    height: 8rpx;
    border-radius: 4rpx;
    background: $border-normal;
    margin: 8rpx auto 12rpx;
  }

  &__header {
    text-align: center;
    padding: 12rpx 0 16rpx;
  }

  &__title {
    font-size: $font-size-sm;
    color: $text-tertiary;
    letter-spacing: 1rpx;
  }

  &__list {
    background: $bg-card;
    border-radius: $radius-lg;
    overflow: hidden;
  }

  &__item {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100rpx;
    position: relative;
    transition: background $duration-fast $ease-soft;

    &:active {
      background: $heart-pink-ghost;
    }

    & + & {
      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 40rpx;
        right: 40rpx;
        height: 1rpx;
        background: $border-light;
      }
    }

    &--destructive {
      .kd-action-sheet__label {
        color: $error;
      }
    }
  }

  &__label {
    font-size: $font-size-lg;
    color: $text-primary;
    font-weight: $font-weight-medium;
    letter-spacing: 0.5rpx;
  }

  &__cancel {
    margin-top: 16rpx;
    background: $bg-card;
    border-radius: $radius-lg;
    height: 100rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: $font-size-lg;
    color: $text-secondary;
    font-weight: $font-weight-medium;
    transition: background $duration-fast $ease-soft;

    &:active {
      background: $heart-pink-ghost;
    }
  }
}

@keyframes sheetUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}
</style>
