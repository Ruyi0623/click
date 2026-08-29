<template>
  <view class="page-create">
    <!-- 标题 -->
    <view class="create-header">
      <view class="create-header__icon">
        <KdIcon name="tabler:ticket" :size="48" variant="pink" />
      </view>
      <text class="create-header__title">开一张罚单</text>
      <text class="create-header__subtitle">给对方一个甜蜜的惩罚</text>
    </view>

    <!-- 罚单表单 -->
    <view class="ticket-form">
      <!-- 罚单顶部装饰 -->
      <view class="ticket-form__header">
        <view class="ticket-form__line" />
        <text class="ticket-form__date">{{ todayStr }}</text>
        <view class="ticket-form__line" />
      </view>

      <!-- 罚单原因 -->
      <view class="form-group">
        <view class="form-group__header">
          <KdIcon name="tabler:alert-circle" :size="28" variant="pink" />
          <text class="form-group__label">罚单原因</text>
        </view>
        <input class="form-input" v-model="reason" placeholder="如：打游戏超时" maxlength="100" />
      </view>

      <!-- 罚单类型 -->
      <view class="form-group">
        <view class="form-group__header">
          <KdIcon name="tabler:list" :size="28" variant="pink" />
          <text class="form-group__label">罚单类型</text>
        </view>
        <view class="type-selector">
          <view
            class="type-option"
            :class="{ 'type-option--active': penaltyType === 'money' }"
            @tap="penaltyType = 'money'"
          >
            <view class="type-option__icon">
              <KdIcon name="tabler:coin" :size="32" :variant="penaltyType === 'money' ? 'pink' : 'dark'" />
            </view>
            <text class="type-option__text">罚款</text>
            <text class="type-option__desc">金钱惩罚</text>
            <view v-if="penaltyType === 'money'" class="type-option__check">
              <KdIcon name="tabler:check" :size="20" color="#fff" />
            </view>
          </view>
          <view
            class="type-option"
            :class="{ 'type-option--active': penaltyType === 'action' }"
            @tap="penaltyType = 'action'"
          >
            <view class="type-option__icon">
              <KdIcon name="tabler:heart" :size="32" :variant="penaltyType === 'action' ? 'pink' : 'dark'" />
            </view>
            <text class="type-option__text">行动</text>
            <text class="type-option__desc">甜蜜任务</text>
            <view v-if="penaltyType === 'action'" class="type-option__check">
              <KdIcon name="tabler:check" :size="20" color="#fff" />
            </view>
          </view>
        </view>
      </view>

      <!-- 罚款金额 -->
      <view v-if="penaltyType === 'money'" class="form-group">
        <view class="form-group__header">
          <KdIcon name="tabler:coin" :size="28" variant="pink" />
          <text class="form-group__label">罚款金额</text>
        </view>
        <view class="form-input-wrap">
          <text class="form-input-wrap__prefix">¥</text>
          <input class="form-input form-input--amount" v-model="amount" type="digit" placeholder="10" />
        </view>
      </view>

      <!-- 行动内容 -->
      <view v-if="penaltyType === 'action'" class="form-group">
        <view class="form-group__header">
          <KdIcon name="tabler:heart" :size="28" variant="pink" />
          <text class="form-group__label">行动内容</text>
        </view>
        <input class="form-input" v-model="action" placeholder="如：做一顿饭" />
      </view>

      <!-- 备注说明 -->
      <view class="form-group">
        <view class="form-group__header">
          <KdIcon name="tabler:note" :size="28" variant="pink" />
          <text class="form-group__label">备注说明（可选）</text>
        </view>
        <input class="form-input" v-model="note" placeholder="补充说明" maxlength="200" />
      </view>

      <!-- 拍照取证 -->
      <view class="form-group">
        <view class="form-group__header">
          <KdIcon name="tabler:camera" :size="28" variant="pink" />
          <text class="form-group__label">拍照取证（可选）</text>
        </view>
        <view v-if="photoPath" class="photo-preview">
          <image class="photo-preview__img" :src="photoPath" mode="aspectFill" @tap="previewPhoto" />
          <view class="photo-preview__delete" @tap="removePhoto">
            <KdIcon name="tabler:x" :size="24" color="#fff" />
          </view>
        </view>
        <view v-else class="photo-add" @tap="choosePhoto">
          <KdIcon name="tabler:camera" :size="48" variant="pink" />
          <text class="photo-add__text">点击拍照/选择照片</text>
        </view>
      </view>

      <!-- 罚单底部装饰 -->
      <view class="ticket-form__footer">
        <view class="ticket-form__corner ticket-form__corner--bl" />
        <view class="ticket-form__corner ticket-form__corner--br" />
      </view>
    </view>

    <!-- 提交按钮 -->
    <button
      class="submit-btn"
      :class="{ 'submit-btn--disabled': !reason || loading }"
      :disabled="!reason || loading"
      @tap="submit"
    >
      <KdIcon v-if="!loading" name="tabler:ticket" :size="32" color="#fff" />
      <view v-else class="submit-btn__loading" />
      <text class="submit-btn__text">{{ loading ? '开罚中...' : '开出罚单' }}</text>
    </button>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { penaltyApi } from '@/api/penalty'
import { useCoupleStore } from '@/stores/couple'
import { upload, ensureHttps } from '@/utils/request'
import KdIcon from '@/components/KdIcon.vue'

const coupleStore = useCoupleStore()
const reason = ref('')
const penaltyType = ref<'money' | 'action'>('money')
const amount = ref('')
const action = ref('')
const note = ref('')
const photoPath = ref('')
const photoUrl = ref('')
const loading = ref(false)

const todayStr = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
})

const choosePhoto = () => {
  const chooseFn = uni.chooseMedia || uni.chooseImage
  const options: any = uni.chooseMedia
    ? { count: 1, mediaType: ['image'], sourceType: ['album', 'camera'], sizeType: ['compressed'] }
    : { count: 1, sizeType: ['compressed'], sourceType: ['album', 'camera'] }

  chooseFn({
    ...options,
    success: (res: any) => {
      photoPath.value = res.tempFiles ? res.tempFiles[0].tempFilePath : res.tempFilePaths[0]
    },
    fail: (err: any) => {
      if (err.errMsg?.includes('cancel')) return
      uni.showToast({ title: '选择照片失败', icon: 'none' })
    },
  })
}

const removePhoto = () => {
  photoPath.value = ''
  photoUrl.value = ''
}

const previewPhoto = () => {
  if (photoPath.value) {
    uni.previewImage({ urls: [photoPath.value] })
  }
}

const submit = async () => {
  if (!reason.value) return
  if (penaltyType.value === 'money') {
    const amt = parseFloat(amount.value)
    if (isNaN(amt) || amt < 0) {
      uni.showToast({ title: '金额不能为负数', icon: 'none' })
      return
    }
  }
  const partnerId = coupleStore.coupleInfo?.partner_id
  if (!partnerId) { uni.showToast({ title: '未配对', icon: 'none' }); return }
  loading.value = true
  try {
    // 先上传照片
    if (photoPath.value) {
      const result: any = await upload(photoPath.value)
      photoUrl.value = result.url
    }
    await penaltyApi.create({
      offender_id: partnerId,
      reason: reason.value,
      penalty_type: penaltyType.value,
      amount: penaltyType.value === 'money' ? parseFloat(amount.value) : undefined,
      action: penaltyType.value === 'action' ? action.value : undefined,
      photo_url: photoUrl.value || undefined,
      note: note.value || undefined,
    })
    uni.showToast({ title: '罚单已开出', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e: any) { uni.showToast({ title: e.message, icon: 'none' }) }
  finally { loading.value = false }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-create {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF0F2 0%, #FFE4E8 50%, #FFF5F7 100%);
  padding: 24rpx 32rpx;
  padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
}

// ========== 标题 ==========
.create-header {
  text-align: center;
  padding: 32rpx 0 40rpx;

  &__icon {
    width: 100rpx;
    height: 100rpx;
    background: #FFEBEE;
    border-radius: 28rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 24rpx;
    box-shadow: 0 4rpx 16rpx rgba(239, 83, 80, 0.15);
  }

  &__title {
    font-size: 36rpx;
    font-weight: 700;
    color: $text-primary;
    display: block;
    margin-bottom: 8rpx;
  }

  &__subtitle {
    font-size: 26rpx;
    color: $text-tertiary;
    display: block;
  }
}

// ========== 罚单表单 ==========
.ticket-form {
  background: #fff;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 40rpx;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    0 8rpx 24rpx rgba(239, 83, 80, 0.08);
  position: relative;

  &__header {
    display: flex;
    align-items: center;
    gap: 16rpx;
    padding-bottom: 20rpx;
    margin-bottom: 24rpx;
    border-bottom: 2rpx dashed #FFEBEE;
  }

  &__line {
    flex: 1;
    height: 2rpx;
    background: #FFCDD2;
  }

  &__date {
    font-size: 22rpx;
    color: #EF9A9A;
    letter-spacing: 2rpx;
  }

  &__footer {
    position: relative;
    height: 16rpx;
    margin-top: 24rpx;
  }

  &__corner {
    position: absolute;
    width: 24rpx;
    height: 24rpx;
    border-color: #FFCDD2;
    border-style: solid;
    border-width: 0;

    &--bl {
      bottom: 0;
      left: 12rpx;
      border-bottom-width: 4rpx;
      border-left-width: 4rpx;
      border-radius: 0 0 0 8rpx;
    }

    &--br {
      bottom: 0;
      right: 12rpx;
      border-bottom-width: 4rpx;
      border-right-width: 4rpx;
      border-radius: 0 0 8rpx 0;
    }
  }
}

// ========== 表单元素 ==========
.form-group {
  margin-bottom: 28rpx;

  &__header {
    display: flex;
    align-items: center;
    gap: 10rpx;
    margin-bottom: 14rpx;
  }

  &__label {
    font-size: 26rpx;
    font-weight: 500;
    color: $text-primary;
  }
}

.form-input {
  background: #FFF5F5;
  border: 2rpx solid #FFEBEE;
  border-radius: 14rpx;
  padding: 22rpx 24rpx;
  font-size: 28rpx;
  color: $text-primary;
  width: 100%;
  display: block;
  box-sizing: border-box;
  transition: border-color 0.2s ease;

  &:focus {
    border-color: #EF9A9A;
  }
}

.form-input-wrap {
  display: flex;
  align-items: center;
  background: #FFF5F5;
  border: 2rpx solid #FFEBEE;
  border-radius: 14rpx;
  padding: 0 24rpx;
  transition: border-color 0.2s ease;

  &:focus-within {
    border-color: #EF9A9A;
  }

  &__prefix {
    font-size: 28rpx;
    font-weight: 600;
    color: #EF5350;
    margin-right: 8rpx;
  }
}

.form-input--amount {
  border: none;
  padding: 22rpx 0;
  background: transparent;
}

// ========== 类型选择 ==========
.type-selector {
  display: flex;
  gap: 16rpx;
}

.type-option {
  flex: 1;
  position: relative;
  background: #FFF5F5;
  border: 2rpx solid #FFEBEE;
  border-radius: 16rpx;
  padding: 24rpx 20rpx;
  text-align: center;
  transition: all 0.2s ease;

  &--active {
    border-color: #EF5350;
    background: #FFEBEE;
  }

  &__icon {
    width: 56rpx;
    height: 56rpx;
    background: #fff;
    border-radius: 14rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12rpx;
  }

  &__text {
    font-size: 28rpx;
    font-weight: 600;
    color: $text-primary;
    display: block;
    margin-bottom: 4rpx;
  }

  &__desc {
    font-size: 22rpx;
    color: $text-tertiary;
    display: block;
  }

  &__check {
    position: absolute;
    top: 12rpx;
    right: 12rpx;
    width: 32rpx;
    height: 32rpx;
    background: #EF5350;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: scaleIn 0.2s ease;
  }
}

@keyframes scaleIn {
  from { transform: scale(0); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

// ========== 照片 ==========
.photo-add {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200rpx;
  background: #FFF5F5;
  border: 2rpx dashed #FFCDD2;
  border-radius: 16rpx;

  &__text {
    font-size: 24rpx;
    color: $text-tertiary;
    margin-top: 12rpx;
  }
}

.photo-preview {
  position: relative;
  width: 200rpx;
  height: 200rpx;
  border-radius: 16rpx;
  overflow: hidden;

  &__img {
    width: 100%;
    height: 100%;
    border-radius: 16rpx;
  }

  &__delete {
    position: absolute;
    top: 8rpx;
    right: 8rpx;
    width: 44rpx;
    height: 44rpx;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

// ========== 提交按钮 ==========
.submit-btn {
  width: 100%;
  height: 104rpx;
  background: linear-gradient(135deg, #FF8A80 0%, #EF5350 100%);
  color: #fff;
  border: none;
  border-radius: 52rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 8rpx 24rpx rgba(239, 83, 80, 0.35);
  transition: all 0.2s ease;
  &::after { display: none; }

  &:active:not(&--disabled) {
    transform: scale(0.96);
  }

  &--disabled {
    opacity: 0.5;
    box-shadow: none;
  }

  &__text {
    font-size: 32rpx;
    font-weight: 600;
  }

  &__loading {
    width: 36rpx;
    height: 36rpx;
    border: 4rpx solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
