<template>
  <view class="page-bind">
    <view class="bind-bg">
      <view class="bind-bg__circle" />
    </view>

    <view class="bind-content">
      <view class="bind-header animate-zoom-in">
        <KdIcon class="bind-header__icon animate-float" name="tabler:couple" :size="80" variant="pink" />
        <text class="bind-header__title">和 TA 配对</text>
        <text class="bind-header__desc animate-fade-in" style="animation-delay: 200ms">输入对方的配对码，开始你们的专属空间</text>
      </view>

      <!-- 生成配对码 -->
      <view class="bind-card animate-card-slide" v-if="!showInput">
        <text class="bind-card__label">生成你的配对码</text>
        <text class="bind-card__desc">将配对码发给对方，让 TA 输入即可完成配对</text>
        <view class="bind-code animate-neon-pulse" v-if="pairCode">
          <text class="bind-code__text animate-count-pulse" @tap="copyCode">{{ pairCode }}</text>
          <text class="bind-code__tip">点击复制</text>
        </view>
        <button class="bind-btn" @tap="generateCode" :loading="generating">
          {{ pairCode ? '重新生成' : '生成配对码' }}
        </button>
        <view class="bind-divider">
          <view class="bind-divider__line" />
          <text class="bind-divider__text">或者</text>
          <view class="bind-divider__line" />
        </view>
        <button class="bind-btn bind-btn--secondary" @tap="switchToInput">
          输入对方的配对码
        </button>
      </view>

      <!-- 输入配对码 -->
      <view class="bind-card animate-card-slide" v-else>
        <text class="bind-card__label">输入配对码</text>
        <view class="bind-input-group">
          <input
            class="bind-input"
            v-model="inputCode"
            type="number"
            maxlength="6"
            placeholder="请输入 6 位配对码"
            placeholder-class="bind-input__placeholder"
          />
        </view>
        <view class="bind-date-row">
          <text class="bind-date-label">恋爱起始日</text>
          <picker mode="date" :value="startDate" @change="onDateChange">
            <text class="bind-date-value">{{ startDate || '选择日期（可选）' }}</text>
          </picker>
        </view>
        <button class="bind-btn" @tap="confirmPair" :loading="pairing" :disabled="inputCode.length < 6">
          确认配对
        </button>
        <button class="bind-btn bind-btn--text" @tap="switchToGenerate">返回</button>
      </view>
    </view>

    <!-- 配对成功动画 -->
    <view v-if="showSuccess" class="bind-success animate-fade-in">
      <view class="bind-success__hearts">
        <KdIcon v-for="i in 8" :key="i" name="tabler:heart" :size="32" variant="pink"
          class="bind-success__heart animate-heart-explode"
          :style="{ animationDelay: `${i * 100}ms` }" />
      </view>
      <!-- 上升的爱心粒子 -->
      <view class="bind-success__particles">
        <view v-for="n in 6" :key="n" class="bind-success__particle" :style="{
          '--delay': `${n * 0.4}s`,
          '--x': `${(n % 2 === 0 ? 1 : -1) * (20 + n * 15)}rpx`,
          left: `${15 + n * 12}%`,
        }">♡</view>
      </view>
      <view class="bind-success__content animate-elastic-pop">
        <KdIcon class="bind-success__icon animate-soft-bounce" name="tabler:star" :size="80" />
        <text class="bind-success__title">配对成功！</text>
        <text class="bind-success__desc">你们的专属空间已开启</text>
        <button class="bind-btn" @tap="goHome">进入咔哒</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { coupleApi } from '@/api/couple'
import { useCoupleStore } from '@/stores/couple'
import KdIcon from '@/components/KdIcon.vue'

const coupleStore = useCoupleStore()
const showInput = ref(false)
const pairCode = ref('')
const inputCode = ref('')
const startDate = ref('')
const generating = ref(false)
const pairing = ref(false)
const showSuccess = ref(false)

// 轮询检测配对状态
let pollTimer: ReturnType<typeof setInterval> | null = null

const startPolling = () => {
  stopPolling()
  pollTimer = setInterval(async () => {
    try {
      const info = await coupleApi.info()
      if (info && info.id) {
        stopPolling()
        coupleStore.coupleInfo = info
        showSuccess.value = true
      }
    } catch {}
  }, 3000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onUnmounted(stopPolling)

const generateCode = async () => {
  generating.value = true
  try {
    const res = await coupleApi.generate()
    pairCode.value = res.code
    // 生成配对码后开始轮询，等待对方输入
    startPolling()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    generating.value = false
  }
}

const switchToInput = () => {
  stopPolling()
  showInput.value = true
}

const switchToGenerate = () => {
  showInput.value = false
  if (pairCode.value) {
    startPolling()
  }
}

const copyCode = () => {
  uni.setClipboardData({
    data: pairCode.value,
    success: () => uni.showToast({ title: '已复制', icon: 'success' }),
  })
}

const onDateChange = (e: any) => {
  startDate.value = e.detail.value
}

const confirmPair = async () => {
  if (inputCode.value.length < 6) return
  stopPolling()
  pairing.value = true
  try {
    await coupleApi.confirm(inputCode.value, startDate.value || undefined)
    await coupleStore.fetchCoupleInfo()
    showSuccess.value = true
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    pairing.value = false
  }
}

const goHome = () => {
  uni.reLaunch({ url: '/pages/index/index' })
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-bind {
  min-height: 100vh;
  background: $bg-page;
  position: relative;
  overflow: hidden;
}

.bind-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 500rpx;
  background: $gradient-dawn;
  &__circle {
    position: absolute;
    width: 400rpx;
    height: 400rpx;
    border-radius: 50%;
    background: $heart-pink;
    opacity: 0.06;
    top: -100rpx;
    left: 50%;
    transform: translateX(-50%);
  }
}

.bind-content {
  position: relative;
  z-index: 1;
  padding: 0 $padding-page;
  padding-top: 160rpx;
}

.bind-header {
  text-align: center;
  margin-bottom: 64rpx;
  opacity: 0;
  &__icon { font-size: 80rpx; display: block; margin-bottom: 24rpx; }
  &__desc { opacity: 0; }
  &__title {
    font-size: $font-size-xl;
    font-weight: $font-weight-bold;
    color: $text-primary;
    display: block;
    margin-bottom: 16rpx;
  }
  &__desc {
    font-size: $font-size-base;
    color: $text-secondary;
  }
}

.bind-card {
  background: $bg-card;
  border-radius: $radius-xl;
  padding: 48rpx $padding-card;
  box-shadow: $shadow-md;
  opacity: 0;
  &__label {
    font-size: $font-size-lg;
    font-weight: $font-weight-semibold;
    color: $text-primary;
    display: block;
    margin-bottom: 16rpx;
  }
  &__desc {
    font-size: $font-size-sm;
    color: $text-secondary;
    display: block;
    margin-bottom: 32rpx;
  }
}

.bind-code {
  text-align: center;
  margin-bottom: 32rpx;
  padding: 32rpx;
  background: $heart-pink-ghost;
  border-radius: $radius-lg;
  &__text {
    font-size: 80rpx;
    font-weight: $font-weight-bold;
    color: $heart-pink;
    font-family: $font-family-number;
    letter-spacing: 16rpx;
  }
  &__tip {
    font-size: $font-size-sm;
    color: $text-tertiary;
    display: block;
    margin-top: 8rpx;
  }
}

.bind-input-group {
  background: $bg-page;
  border: 2rpx solid $border-light;
  border-radius: $radius-base;
  padding: 0 32rpx;
  height: 96rpx;
  display: flex;
  align-items: center;
  margin-bottom: 24rpx;
}

.bind-input {
  flex: 1;
  font-size: $font-size-xl;
  color: $text-primary;
  font-weight: $font-weight-semibold;
  letter-spacing: 8rpx;
  text-align: center;
  &__placeholder {
    color: $text-tertiary;
    font-size: $font-size-base;
    font-weight: $font-weight-regular;
    letter-spacing: 0;
  }
}

.bind-date-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32rpx;
  padding: 0 8rpx;
}
.bind-date-label {
  font-size: $font-size-base;
  color: $text-secondary;
}
.bind-date-value {
  font-size: $font-size-base;
  color: $heart-pink;
}

.bind-btn {
  width: 100%;
  height: 96rpx;
  background: $gradient-heart;
  color: $text-inverse;
  border: none;
  border-radius: $radius-full;
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  box-shadow: $shadow-glow;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
  &::after { display: none; }
  &[disabled] { opacity: 0.5; }
  &--secondary {
    background: transparent;
    color: $heart-pink;
    border: 2rpx solid $heart-pink;
    box-shadow: none;
  }
  &--text {
    background: transparent;
    color: $text-secondary;
    box-shadow: none;
    height: 80rpx;
    font-size: $font-size-base;
  }
}

.bind-divider {
  display: flex;
  align-items: center;
  margin: 32rpx 0;
  &__line {
    flex: 1;
    height: 2rpx;
    background: $border-light;
  }
  &__text {
    padding: 0 24rpx;
    font-size: $font-size-sm;
    color: $text-tertiary;
  }
}

.bind-success {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(255, 240, 242, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  &__hearts {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }
  &__heart {
    position: absolute;
    font-size: 48rpx;
    &:nth-child(1) { top: 20%; left: 10%; }
    &:nth-child(2) { top: 15%; right: 15%; }
    &:nth-child(3) { top: 35%; left: 20%; }
    &:nth-child(4) { top: 30%; right: 25%; }
    &:nth-child(5) { top: 50%; left: 15%; }
    &:nth-child(6) { top: 45%; right: 10%; }
    &:nth-child(7) { top: 60%; left: 30%; }
    &:nth-child(8) { top: 55%; right: 30%; }
  }
  &__particles {
    position: absolute;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
  }
  &__particle {
    position: absolute;
    bottom: -40rpx;
    font-size: 36rpx;
    color: $heart-pink;
    opacity: 0;
    animation: loveRise 3s ease-out infinite;
    animation-delay: var(--delay, 0s);
  }
  &__content {
    text-align: center;
    z-index: 1;
  }
  &__icon { font-size: 120rpx; display: block; margin-bottom: 32rpx; }
  &__title {
    font-size: $font-size-xxl;
    font-weight: $font-weight-bold;
    color: $heart-pink;
    display: block;
    margin-bottom: 16rpx;
  }
  &__desc {
    font-size: $font-size-base;
    color: $text-secondary;
    display: block;
    margin-bottom: 64rpx;
  }
}
</style>
