<template>
  <view class="page-create">
    <!-- 选择地点 -->
    <view class="form-group">
      <text class="form-label">选择地点</text>
      <view class="location-card" @tap="chooseLocation">
        <view v-if="name" class="location-card__selected">
          <view class="location-card__icon-wrap">
            <KdIcon name="tabler:map-pin-filled" :size="32" color="#FF8A80" />
          </view>
          <view class="location-card__info">
            <text class="location-card__name">{{ name }}</text>
            <text class="location-card__coords">{{ latitude.toFixed(4) }}, {{ longitude.toFixed(4) }}</text>
          </view>
          <KdIcon name="tabler:chevron-right" :size="24" color="#ccc" />
        </view>
        <view v-else class="location-card__empty">
          <view class="location-card__empty-icon">
            <KdIcon name="tabler:map-pin" :size="48" color="#FFD6DE" />
          </view>
          <text class="location-card__hint">点击打开地图选择地点</text>
        </view>
      </view>
    </view>

    <!-- 地点名称 -->
    <view class="form-group">
      <text class="form-label">地点名称</text>
      <input
        class="form-input"
        v-model="name"
        placeholder="如：西湖"
        placeholder-style="color: #9E9EB0"
      />
    </view>

    <!-- 到访日期 -->
    <view class="form-group">
      <text class="form-label">到访日期</text>
      <picker mode="date" :value="visitedAt" @change="onDateChange">
        <view class="form-picker">
          <view class="form-picker__left">
            <KdIcon name="tabler:calendar" :size="32" color="#FF8A80" />
            <text :class="['form-picker__text', !visitedAt && 'form-picker__text--placeholder']">
              {{ visitedAt || '选择日期' }}
            </text>
          </view>
          <KdIcon name="tabler:chevron-right" :size="24" color="#ccc" />
        </view>
      </picker>
    </view>

    <!-- 备注 -->
    <view class="form-group">
      <text class="form-label">备注（可选）</text>
      <textarea
        class="form-textarea"
        v-model="note"
        placeholder="记录此刻的心情..."
        placeholder-style="color: #9E9EB0"
        maxlength="200"
      />
      <text class="form-hint">{{ note.length }}/200</text>
    </view>

    <!-- 提交按钮 -->
    <button
      class="submit-btn"
      :disabled="!name || !visitedAt || loading"
      @tap="submit"
    >
      <text v-if="loading" class="submit-btn__text">添加中...</text>
      <text v-else class="submit-btn__text">添加足迹</text>
    </button>
  </view>

  <!-- 权限提示弹窗 -->
  <KdDialog
    :visible="showPermissionDialog"
    title="需要位置权限"
    content="请在设置中允许使用位置信息"
    confirm-text="去设置"
    @close="showPermissionDialog = false"
    @confirm="onPermissionConfirm"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { footprintApi } from '@/api/footprint'
import KdIcon from '@/components/KdIcon.vue'
import KdDialog from '@/components/KdDialog.vue'

const name = ref('')
const visitedAt = ref('')
const note = ref('')
const latitude = ref(0)
const longitude = ref(0)
const loading = ref(false)
const showPermissionDialog = ref(false)

const onDateChange = (e: any) => {
  visitedAt.value = e.detail.value
}

const chooseLocation = () => {
  uni.chooseLocation({
    success: (res) => {
      name.value = res.name || res.address || ''
      latitude.value = res.latitude
      longitude.value = res.longitude
    },
    fail: (err) => {
      if (err.errMsg?.includes('deny') || err.errMsg?.includes('auth')) {
        showPermissionDialog.value = true
      }
    },
  })
}

const onPermissionConfirm = () => {
  uni.openSetting()
}

const submit = async () => {
  if (!name.value || !visitedAt.value) return
  loading.value = true
  try {
    await footprintApi.create({
      name: name.value,
      visited_at: visitedAt.value,
      note: note.value || undefined,
      latitude: latitude.value,
      longitude: longitude.value,
    })
    uni.showToast({ title: '添加成功', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-create {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF0F2 0%, #FFF8F9 40%, #FBF5FF 100%);
  padding: $padding-page;
}

// ===== 表单组 =====
.form-group {
  margin-bottom: $space-base;
}

.form-label {
  font-size: $font-size-base;
  font-weight: $font-weight-medium;
  color: $text-secondary;
  margin-bottom: $space-sm;
  display: block;
}

.form-hint {
  font-size: $font-size-xs;
  color: $text-tertiary;
  display: block;
  text-align: right;
  margin-top: $space-xs;
}

// ===== 输入框 =====
.form-input {
  background: $bg-card;
  border: 2rpx solid $border-light;
  border-radius: $radius-lg;
  padding: 28rpx 32rpx;
  font-size: $font-size-md;
  color: $text-primary;
  width: 100%;
  display: block;
  box-sizing: border-box;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.02);
  transition: border-color $duration-fast $ease-soft, box-shadow $duration-fast $ease-soft;

  &:focus {
    border-color: $coral-light;
    box-shadow: 0 0 0 4rpx rgba($coral, 0.08);
  }
}

.form-textarea {
  background: $bg-card;
  border: 2rpx solid $border-light;
  border-radius: $radius-lg;
  padding: 28rpx 32rpx;
  font-size: $font-size-md;
  color: $text-primary;
  width: 100%;
  height: 200rpx;
  display: block;
  box-sizing: border-box;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.02);
  transition: border-color $duration-fast $ease-soft, box-shadow $duration-fast $ease-soft;

  &:focus {
    border-color: $coral-light;
    box-shadow: 0 0 0 4rpx rgba($coral, 0.08);
  }
}

// ===== 日期选择器 =====
.form-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: $bg-card;
  border: 2rpx solid $border-light;
  border-radius: $radius-lg;
  padding: 28rpx 32rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.02);
  transition: border-color $duration-fast $ease-soft;

  &__left {
    display: flex;
    align-items: center;
    gap: $space-sm;
  }

  &__text {
    font-size: $font-size-md;
    color: $text-primary;

    &--placeholder {
      color: $text-tertiary;
    }
  }
}

// ===== 地点选择器 =====
.location-card {
  background: $bg-card;
  border: 2rpx solid $border-light;
  border-radius: $radius-lg;
  overflow: hidden;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.02);
  transition: border-color $duration-fast $ease-soft;

  &:active {
    border-color: $coral-light;
  }

  &__selected {
    display: flex;
    align-items: center;
    padding: 28rpx 32rpx;
    gap: $space-sm;
  }

  &__icon-wrap {
    width: 64rpx;
    height: 64rpx;
    border-radius: $radius-md;
    background: $coral-pale;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &__info {
    flex: 1;
    min-width: 0;
  }

  &__name {
    font-size: $font-size-md;
    color: $text-primary;
    font-weight: $font-weight-medium;
    display: block;
  }

  &__coords {
    font-size: $font-size-xs;
    color: $text-tertiary;
    display: block;
    margin-top: 4rpx;
  }

  &__empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48rpx;
  }

  &__empty-icon {
    width: 96rpx;
    height: 96rpx;
    border-radius: $radius-full;
    background: $coral-pale;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: $space-sm;
  }

  &__hint {
    font-size: $font-size-sm;
    color: $text-tertiary;
    margin-top: $space-xs;
  }
}

// ===== 提交按钮 =====
.submit-btn {
  width: 100%;
  height: 96rpx;
  background: $gradient-heart;
  color: $text-inverse;
  border: none;
  border-radius: $radius-full;
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: $space-xl;
  box-shadow:
    0 8rpx 24rpx rgba(255, 107, 138, 0.3),
    0 2rpx 8rpx rgba(255, 107, 138, 0.2);
  transition: transform $duration-fast $ease-soft, opacity $duration-fast $ease-soft;

  &::after {
    display: none;
  }

  &:active {
    transform: scale(0.98);
  }

  &[disabled] {
    opacity: 0.5;
  }

  &__text {
    opacity: 0.9;
  }
}
</style>
