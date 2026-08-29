<template>
  <view class="page-edit">
    <!-- 加载中 -->
    <view v-if="pageLoading" class="loading-wrap">
      <view class="loading-spinner" />
    </view>

    <view v-else>
      <!-- 地点名称 -->
      <view class="form-group">
        <text class="form-label">地点名称</text>
        <input
          class="form-input"
          v-model="form.name"
          placeholder="如：西湖"
          placeholder-style="color: #9E9EB0"
        />
      </view>

      <!-- 到访日期 -->
      <view class="form-group">
        <text class="form-label">到访日期</text>
        <picker mode="date" :value="form.visited_at" @change="onDateChange">
          <view class="form-picker">
            <view class="form-picker__left">
              <KdIcon name="tabler:calendar" :size="32" color="#FF8A80" />
              <text :class="['form-picker__text', !form.visited_at && 'form-picker__text--placeholder']">
                {{ form.visited_at || '选择日期' }}
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
          v-model="form.note"
          placeholder="记录此刻的心情..."
          placeholder-style="color: #9E9EB0"
          maxlength="200"
        />
        <text class="form-hint">{{ (form.note || '').length }}/200</text>
      </view>

      <!-- 提交按钮 -->
      <button
        class="submit-btn"
        :disabled="!form.name || !form.visited_at || saving"
        @tap="submit"
      >
        <text v-if="saving" class="submit-btn__text">保存中...</text>
        <text v-else class="submit-btn__text">保存修改</text>
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { footprintApi } from '@/api/footprint'
import KdIcon from '@/components/KdIcon.vue'

const pageLoading = ref(true)
const saving = ref(false)
const footprintId = ref('')

const form = reactive({
  name: '',
  visited_at: '',
  note: '',
})

const onDateChange = (e: any) => {
  form.visited_at = e.detail.value
}

onLoad((options) => {
  if (options?.id) {
    footprintId.value = options.id
    loadDetail(options.id)
  } else {
    pageLoading.value = false
    uni.showToast({ title: '参数错误', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 1000)
  }
})

const loadDetail = async (id: string) => {
  try {
    const detail = await footprintApi.get(id)
    form.name = detail.name
    form.visited_at = detail.visited_at
    form.note = detail.note || ''
  } catch (e: any) {
    uni.showToast({ title: '加载失败', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 1000)
  } finally {
    pageLoading.value = false
  }
}

const submit = async () => {
  if (!form.name || !form.visited_at) return
  saving.value = true
  try {
    await footprintApi.update(footprintId.value, {
      name: form.name,
      visited_at: form.visited_at,
      note: form.note || undefined,
    })
    uni.showToast({ title: '已保存', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-edit {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF0F2 0%, #FFF8F9 40%, #FBF5FF 100%);
  padding: $padding-page;
}

// ===== 加载 =====
.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 120rpx 0;
}
.loading-spinner {
  width: 48rpx;
  height: 48rpx;
  border: 4rpx solid $border-light;
  border-top-color: $coral;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
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
