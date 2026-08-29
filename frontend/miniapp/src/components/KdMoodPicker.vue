<template>
  <view class="kd-mood-picker" v-if="visible">
    <view class="kd-mood-picker__mask" @tap="close" />
    <view class="kd-mood-picker__content animate-slide-up">
      <view class="kd-mood-picker__header">
        <text class="kd-mood-picker__title">今天心情如何？</text>
        <text class="kd-mood-picker__subtitle">选择一个代表你此刻的心情</text>
      </view>

      <view class="kd-mood-picker__grid">
        <view
          v-for="(m, index) in moods"
          :key="m.id"
          class="kd-mood-picker__item"
          :class="{ 'kd-mood-picker__item--selected': selected === m.id }"
          :data-index="index"
          @tap="select(m)"
        >
          <image class="kd-mood-picker__emoji" :src="getTwemojiUrl(m.icon)" mode="aspectFit" />
          <text class="kd-mood-picker__label">{{ m.label }}</text>
        </view>
      </view>

      <button
        class="kd-mood-picker__btn"
        :class="{ 'is-disabled': !selected }"
        :disabled="!selected"
        @tap="submit"
      >
        记录此刻
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getTwemojiUrl } from '@/utils/emoji'

defineProps<{ visible: boolean }>()
const emit = defineEmits<{ close: []; select: [mood: string] }>()

const moods = [
  { id: 'happy', icon: '😊', label: '开心' },
  { id: 'love', icon: '😍', label: '想你' },
  { id: 'calm', icon: '😌', label: '平静' },
  { id: 'excited', icon: '🤩', label: '惊喜' },
  { id: 'sweet', icon: '😘', label: '甜蜜' },
  { id: 'tired', icon: '😪', label: '困倦' },
  { id: 'sad', icon: '😢', label: '难过' },
  { id: 'angry', icon: '😤', label: '生气' },
]

const selected = ref('')

const select = (m: typeof moods[0]) => {
  selected.value = m.id
}

const submit = () => {
  if (selected.value) {
    emit('select', selected.value)
    selected.value = ''
  }
}

const close = () => {
  selected.value = ''
  emit('close')
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.kd-mood-picker {
  position: fixed;
  inset: 0;
  z-index: 1000;

  &__mask {
    position: absolute;
    inset: 0;
    background: $bg-mask;
    animation: fadeIn $duration-normal $ease-soft;
  }
  &__content {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: $bg-card;
    border-radius: $radius-xl $radius-xl 0 0;
    padding: 48rpx $padding-card;
    padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
  }
  &__header {
    text-align: center;
    margin-bottom: 48rpx;
  }
  &__title {
    font-size: $font-size-xl;
    font-weight: $font-weight-semibold;
    color: $text-primary;
    display: block;
    margin-bottom: 12rpx;
  }
  &__subtitle {
    font-size: $font-size-base;
    color: $text-secondary;
  }
  &__grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 32rpx 24rpx;
    margin-bottom: 40rpx;
  }
  &__item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 24rpx;
    border-radius: $radius-base;
    transition: all $duration-normal $ease-soft;
    animation: scaleIn $duration-normal $ease-soft both;
    @for $i from 0 through 7 {
      &:nth-child(#{$i + 1}) { animation-delay: #{$i * 50}ms; }
    }
    &--selected,
    &:active {
      background: $heart-pink-ghost;
      transform: scale(1.05);
    }
    &--selected .kd-mood-picker__emoji {
      animation: heartbeat 1s ease-in-out infinite;
    }
  }
  &__emoji {
    width: 64rpx;
    height: 64rpx;
    margin-bottom: 12rpx;
    mix-blend-mode: multiply;
  }
  &__label {
    font-size: $font-size-sm;
    color: $text-secondary;
  }
  &__btn {
    background: $gradient-heart;
    color: $text-inverse;
    border: none;
    border-radius: $radius-full;
    height: 96rpx;
    font-size: $font-size-lg;
    font-weight: $font-weight-semibold;
    box-shadow: $shadow-glow;
    display: flex;
    align-items: center;
    justify-content: center;
    &.is-disabled { opacity: 0.5; }
    &::after { display: none; }
  }
}
</style>
