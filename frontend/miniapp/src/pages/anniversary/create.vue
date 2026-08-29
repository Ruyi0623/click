<template>
  <view class="page-create">
    <!-- 顶部预览卡片 -->
    <view class="preview-card">
      <view class="preview-card__inner">
        <view class="preview-card__content">
          <view class="preview-card__icon-wrap">
            <KdIcon :name="previewIcon" :size="48" variant="pink" />
          </view>
          <view class="preview-card__info">
            <text class="preview-card__title">{{ title || '纪念日名称' }}</text>
            <text class="preview-card__date">{{ date || '选择日期' }}</text>
          </view>
        </view>
        <view class="preview-card__footer">
          <view class="preview-card__badge">
            <KdIcon :name="repeatType === 'yearly' ? 'tabler:reload' : 'tabler:clock'" :size="24" />
            <text class="preview-card__badge-text">{{ repeatType === 'yearly' ? '每年' : '一次性' }}</text>
          </view>
        </view>
      </view>
      <view class="preview-card__tape" />
    </view>

    <!-- 表单区域 -->
    <view class="form-section">
      <view class="form-group">
        <view class="form-group__header">
          <KdIcon name="tabler:pencil" :size="32" variant="pink" />
          <text class="form-group__label">纪念日名称</text>
        </view>
        <input
          class="form-input"
          v-model="title"
          placeholder="如：在一起纪念日"
          maxlength="100"
          :placeholder-style="placeholderStyle"
        />
      </view>

      <view class="form-group">
        <view class="form-group__header">
          <KdIcon name="tabler:calendar-heart" :size="32" variant="pink" />
          <text class="form-group__label">日期</text>
        </view>
        <picker mode="date" :value="date" @change="onDateChange">
          <view class="form-picker" :class="{ 'form-picker--empty': !date }">
            <text class="form-picker__text">{{ date || '选择日期' }}</text>
            <KdIcon name="tabler:arrow-right" :size="32" />
          </view>
        </picker>
      </view>

      <view class="form-group">
        <view class="form-group__header">
          <KdIcon name="tabler:reload" :size="32" variant="pink" />
          <text class="form-group__label">重复</text>
        </view>
        <view class="repeat-options">
          <view
            class="repeat-option"
            :class="{ 'repeat-option--active': repeatType === 'yearly' }"
            @tap="repeatType = 'yearly'"
          >
            <view class="repeat-option__icon-wrap">
              <KdIcon name="tabler:calendar-heart" :size="36" :variant="repeatType === 'yearly' ? 'pink' : 'dark'" />
            </view>
            <text class="repeat-option__text">每年</text>
            <text class="repeat-option__desc">适合节日、纪念日</text>
            <view v-if="repeatType === 'yearly'" class="repeat-option__check">
              <KdIcon name="tabler:check" :size="24" color="#fff" />
            </view>
          </view>
          <view
            class="repeat-option"
            :class="{ 'repeat-option--active': repeatType === 'none' }"
            @tap="repeatType = 'none'"
          >
            <view class="repeat-option__icon-wrap">
              <KdIcon name="tabler:clock" :size="36" :variant="repeatType === 'none' ? 'pink' : 'dark'" />
            </view>
            <text class="repeat-option__text">一次性</text>
            <text class="repeat-option__desc">适合特定日期</text>
            <view v-if="repeatType === 'none'" class="repeat-option__check">
              <KdIcon name="tabler:check" :size="24" color="#fff" />
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 提交按钮 -->
    <view class="submit-section">
      <button
        class="submit-btn"
        :class="{ 'submit-btn--disabled': !title || !date || loading }"
        :disabled="!title || !date || loading"
        @tap="submit"
      >
        <text class="submit-btn__text">{{ isEdit ? '保存修改' : '创建纪念日' }}</text>
        <KdIcon v-if="!loading" :name="isEdit ? 'tabler:check' : 'tabler:plus'" :size="32" color="#fff" />
        <view class="submit-btn__loading" v-else />
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { anniversaryApi } from '@/api/anniversary'
import KdIcon from '@/components/KdIcon.vue'

const title = ref('')
const date = ref('')
const repeatType = ref<'yearly' | 'none'>('yearly')
const loading = ref(false)
const isEdit = ref(false)
const editId = ref('')

const placeholderStyle = 'color: #B8B8CC'

// 预览图标
const previewIcon = computed(() => {
  const iconMap: Record<string, string> = {
    '在一起': 'tabler:heart',
    '恋爱': 'tabler:heart',
    '结婚': 'tabler:ring',
    '婚礼': 'tabler:ring',
    '生日': 'tabler:cake',
    '生日快乐': 'tabler:cake',
    '情人节': 'tabler:gift',
    '七夕': 'tabler:sparkles',
    '圣诞节': 'tabler:star',
    '新年': 'tabler:sparkles',
    '纪念': 'tabler:calendar-star',
    '周年': 'tabler:calendar-heart',
    '毕业': 'tabler:target',
    '旅行': 'tabler:map-pin',
    '求婚': 'tabler:ring',
  }
  for (const [key, icon] of Object.entries(iconMap)) {
    if (title.value.includes(key)) return icon
  }
  return 'tabler:calendar-heart'
})

onLoad((query: any) => {
  if (query?.id) {
    isEdit.value = true
    editId.value = query.id
    title.value = query.title || ''
    date.value = query.date || ''
    repeatType.value = query.repeat || 'yearly'
  }
})

const onDateChange = (e: any) => {
  date.value = e.detail.value
}

const submit = async () => {
  if (!title.value || !date.value || loading.value) return
  loading.value = true
  try {
    if (isEdit.value) {
      await anniversaryApi.update(editId.value, {
        title: title.value,
        date: date.value,
        repeat_type: repeatType.value,
      })
    } else {
      await anniversaryApi.create({
        title: title.value,
        date: date.value,
        repeat_type: repeatType.value,
      })
    }
    uni.showToast({ title: isEdit.value ? '已更新' : '创建成功', icon: 'success' })
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
  background: #FFF5F7;
  padding: 24rpx 32rpx calc(48rpx + env(safe-area-inset-bottom));
}

// ========== 预览卡片 ==========
.preview-card {
  position: relative;
  margin-bottom: 48rpx;

  &__inner {
    background: #fff;
    border-radius: 24rpx;
    padding: 32rpx;
    box-shadow:
      0 2rpx 8rpx rgba(0, 0, 0, 0.04),
      0 8rpx 24rpx rgba(255, 107, 138, 0.1);
  }

  &__content {
    display: flex;
    align-items: center;
    gap: 24rpx;
    margin-bottom: 24rpx;
  }

  &__icon-wrap {
    width: 96rpx;
    height: 96rpx;
    background: linear-gradient(135deg, #FFF0F2 0%, #FFE4E8 100%);
    border-radius: 24rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &__info {
    flex: 1;
    min-width: 0;
  }

  &__title {
    display: block;
    font-size: 32rpx;
    font-weight: 600;
    color: #2D2D3F;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 8rpx;
  }

  &__date {
    display: block;
    font-size: 26rpx;
    color: #9E9EB0;
  }

  &__footer {
    padding-top: 24rpx;
    border-top: 2rpx solid #FFF5F7;
  }

  &__badge {
    display: inline-flex;
    align-items: center;
    gap: 8rpx;
    background: #FFF0F2;
    padding: 8rpx 20rpx;
    border-radius: 8rpx;

    &-text {
      font-size: 22rpx;
      color: #FF6B8A;
      font-weight: 500;
    }
  }

  // 胶带效果 - 和纸胶带风格
  &__tape {
    position: absolute;
    top: -14rpx;
    left: 50%;
    transform: translateX(-50%) rotate(-4deg);
    width: 112rpx;
    height: 36rpx;
    z-index: 2;
    background-color: rgba(255, 183, 197, 0.85);
    border-radius: 4rpx;
    // 模拟纸张纹理的条纹
    background-image: repeating-linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.3) 0rpx,
      rgba(255, 255, 255, 0.3) 2rpx,
      transparent 2rpx,
      transparent 8rpx
    );
    // 边框增加立体感
    border-top: 2rpx solid rgba(255, 255, 255, 0.5);
    border-bottom: 2rpx solid rgba(0, 0, 0, 0.1);
    // 阴影
    box-shadow:
      0 2rpx 6rpx rgba(0, 0, 0, 0.15),
      inset 0 1rpx 0 rgba(255, 255, 255, 0.4);
  }
}

// ========== 表单区域 ==========
.form-section {
  margin-bottom: 48rpx;
}

.form-group {
  margin-bottom: 40rpx;

  &__header {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 20rpx;
  }

  &__label {
    font-size: 28rpx;
    font-weight: 500;
    color: #2D2D3F;
  }
}

.form-input {
  background: #fff;
  border: 2rpx solid #FFE4E8;
  border-radius: 20rpx;
  padding: 28rpx 32rpx;
  font-size: 30rpx;
  color: #2D2D3F;
  width: 100%;
  display: block;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;

  &:focus {
    border-color: #FFB3C6;
    box-shadow: 0 0 0 4rpx rgba(255, 107, 138, 0.1);
  }
}

.form-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border: 2rpx solid #FFE4E8;
  border-radius: 20rpx;
  padding: 28rpx 32rpx;
  transition: border-color 0.2s ease;

  &--empty {
    .form-picker__text {
      color: #B8B8CC;
    }
  }

  &__text {
    font-size: 30rpx;
    color: #2D2D3F;
  }
}

// ========== 重复选项 ==========
.repeat-options {
  display: flex;
  gap: 24rpx;
}

.repeat-option {
  flex: 1;
  position: relative;
  background: #fff;
  border: 2rpx solid #FFE4E8;
  border-radius: 20rpx;
  padding: 28rpx 24rpx;
  transition: all 0.2s ease;
  cursor: pointer;

  &--active {
    border-color: #FF6B8A;
    background: #FFF8F9;
    box-shadow: 0 0 0 4rpx rgba(255, 107, 138, 0.1);
  }

  &__icon-wrap {
    width: 56rpx;
    height: 56rpx;
    background: #FFF0F2;
    border-radius: 14rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16rpx;
  }

  &__text {
    display: block;
    font-size: 28rpx;
    font-weight: 500;
    color: #2D2D3F;
    margin-bottom: 8rpx;
  }

  &__desc {
    display: block;
    font-size: 22rpx;
    color: #9E9EB0;
    line-height: 1.4;
  }

  &__check {
    position: absolute;
    top: 16rpx;
    right: 16rpx;
    width: 36rpx;
    height: 36rpx;
    background: #FF6B8A;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: scaleIn 0.2s ease;
  }
}

@keyframes scaleIn {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

// ========== 提交按钮 ==========
.submit-section {
  padding: 0 16rpx;
}

.submit-btn {
  width: 100%;
  height: 104rpx;
  background: linear-gradient(135deg, #FF6B8A 0%, #FF8FA3 100%);
  color: #fff;
  border: none;
  border-radius: 52rpx;
  font-size: 32rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 8rpx 24rpx rgba(255, 107, 138, 0.35);
  transition: all 0.2s ease;
  &::after { display: none; }

  &:active:not(&--disabled) {
    transform: scale(0.96);
    box-shadow: 0 4rpx 12rpx rgba(255, 107, 138, 0.35);
  }

  &--disabled {
    opacity: 0.5;
    box-shadow: none;
  }

  &__text {
    font-size: 32rpx;
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
