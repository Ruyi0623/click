<template>
  <view class="page-fund">
    <!-- 顶部统计 -->
    <view class="stats-card animate-reveal-days" v-if="list.length">
      <view class="stats-card__bg" />
      <view class="stats-card__content">
        <view class="stats-card__row">
          <view class="stats-card__item">
            <text class="stats-card__label">进行中</text>
            <text class="stats-card__num">{{ activeCount }}</text>
          </view>
          <view class="stats-card__divider" />
          <view class="stats-card__item">
            <text class="stats-card__label">已达成</text>
            <text class="stats-card__num">{{ completedCount }}</text>
          </view>
          <view class="stats-card__divider" />
          <view class="stats-card__item">
            <text class="stats-card__label">总储蓄</text>
            <text class="stats-card__num stats-card__num--gold">¥{{ totalSaved.toFixed(0) }}</text>
          </view>
        </view>
      </view>
      <view class="stats-card__dot stats-card__dot--1" />
      <view class="stats-card__dot stats-card__dot--2" />
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading-wrap">
      <view class="loading-spinner" />
    </view>

    <!-- 空状态 -->
    <view v-else-if="!list.length" class="empty-state">
      <view class="empty-state__piggy">
        <view class="empty-state__piggy-body" />
        <view class="empty-state__piggy-ear" />
        <view class="empty-state__piggy-nose" />
        <view class="empty-state__piggy-slot" />
      </view>
      <text class="empty-state__title">存钱罐空空的</text>
      <text class="empty-state__desc">为你们的共同目标开始储蓄吧</text>
    </view>

    <!-- 存折列表 -->
    <view v-else class="passbook">
      <view class="passbook__header">
        <KdIcon name="tabler:passbook" :size="36" variant="pink" />
        <text class="passbook__title">心愿存折</text>
      </view>

      <view
        v-for="(item, index) in list"
        :key="item.id"
        class="passbook-item"
        :class="{ 'passbook-item--completed': item.progress >= 100 }"
        :style="{ animationDelay: `${index * 60}ms` }"
        @tap="goDetail(item.id)"
        @longpress="deleteItem(item.id)"
      >
        <!-- 存折顶部 -->
        <view class="passbook-item__header">
          <view class="passbook-item__icon-wrap">
            <KdIcon :name="item.icon?.startsWith('tabler:') ? item.icon : 'tabler:target'" :size="36" variant="pink" />
          </view>
          <view class="passbook-item__title-area">
            <text class="passbook-item__name">{{ item.name }}</text>
            <text class="passbook-item__status">{{ item.progress >= 100 ? '已达成' : '储蓄中' }}</text>
          </view>
          <view v-if="item.progress >= 100" class="passbook-item__badge">
            <KdIcon name="tabler:check" :size="24" color="#fff" />
          </view>
        </view>

        <!-- 金额区域 -->
        <view class="passbook-item__amounts">
          <view class="passbook-item__amount">
            <text class="passbook-item__amount-label">已存</text>
            <text class="passbook-item__amount-value">¥{{ item.current_amount.toFixed(0) }}</text>
          </view>
          <view class="passbook-item__amount-divider" />
          <view class="passbook-item__amount">
            <text class="passbook-item__amount-label">目标</text>
            <text class="passbook-item__amount-value">¥{{ item.target_amount.toFixed(0) }}</text>
          </view>
        </view>

        <!-- 进度条 -->
        <view class="passbook-item__progress">
          <view class="passbook-item__bar">
            <view class="passbook-item__bar-fill" :style="{ width: Math.min(item.progress, 100) + '%' }">
              <view class="passbook-item__bar-glow" />
            </view>
          </view>
          <text class="passbook-item__percent">{{ Math.min(item.progress, 100).toFixed(0) }}%</text>
        </view>

        <!-- 存折装饰 -->
        <view class="passbook-item__deco">
          <view class="passbook-item__line" />
          <text class="passbook-item__line-text">咔哒 · 心愿存折</text>
          <view class="passbook-item__line" />
        </view>
      </view>
    </view>

    <!-- FAB 按钮 -->
    <view class="fab" @tap="goCreate">
      <view class="fab__inner">
        <KdIcon name="tabler:plus" :size="48" color="#fff" />
      </view>
    </view>
  </view>

  <KdDialog
    :visible="showDeleteConfirm"
    title="删除存折"
    content="确定要删除这个心愿存折吗？"
    confirm-color="#EF5350"
    @close="showDeleteConfirm = false"
    @confirm="onDeleteConfirm"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'
import { fundApi, type Fund } from '@/api/fund'
import KdIcon from '@/components/KdIcon.vue'
import KdDialog from '@/components/KdDialog.vue'

const list = ref<Fund[]>([])
const loading = ref(true)
const showDeleteConfirm = ref(false)
const deleteTargetId = ref('')

const activeCount = computed(() => list.value.filter(f => f.progress < 100).length)
const completedCount = computed(() => list.value.filter(f => f.progress >= 100).length)
const totalSaved = computed(() => list.value.reduce((sum, f) => sum + f.current_amount, 0))

const loadList = async () => {
  try { list.value = await fundApi.list() } catch {} finally { loading.value = false }
}

const goCreate = () => uni.navigateTo({ url: '/pages/fund/detail' })
const goDetail = (id: string) => uni.navigateTo({ url: `/pages/fund/detail?id=${id}` })

const deleteItem = (id: string) => {
  deleteTargetId.value = id
  showDeleteConfirm.value = true
}
const onDeleteConfirm = async () => {
  try {
    await fundApi.delete(deleteTargetId.value)
    await loadList()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onMounted(loadList)
onShow(loadList)
onPullDownRefresh(async () => { await loadList(); uni.stopPullDownRefresh() })
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-fund {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF8E1 0%, #FFF3E0 30%, #FFF0F2 100%);
  padding: 24rpx 32rpx;
  padding-bottom: calc(160rpx + env(safe-area-inset-bottom));
}

// ========== 顶部统计 ==========
.stats-card {
  position: relative;
  background: linear-gradient(135deg, #FFB74D 0%, #FF9800 50%, #F57C00 100%);
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
  overflow: hidden;
  box-shadow: 0 8rpx 32rpx rgba(255, 152, 0, 0.3);
  opacity: 0;

  &__bg {
    position: absolute;
    top: -50%;
    right: -30%;
    width: 300rpx;
    height: 300rpx;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
  }

  &__content {
    position: relative;
    z-index: 1;
  }

  &__row {
    display: flex;
    align-items: center;
    justify-content: space-around;
  }

  &__item {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  &__label {
    font-size: 22rpx;
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 8rpx;
  }

  &__num {
    font-size: 40rpx;
    font-weight: 700;
    color: #fff;
    font-family: $font-family-number;

    &--gold {
      text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.2);
    }
  }

  &__divider {
    width: 2rpx;
    height: 48rpx;
    background: rgba(255, 255, 255, 0.2);
  }

  &__dot {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);

    &--1 {
      width: 100rpx;
      height: 100rpx;
      top: -20rpx;
      left: -20rpx;
      animation: float 6s ease-in-out infinite;
    }

    &--2 {
      width: 60rpx;
      height: 60rpx;
      bottom: -10rpx;
      right: 40rpx;
      animation: float 8s ease-in-out infinite reverse;
    }
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8rpx); }
}

// ========== 加载状态 ==========
.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 120rpx 0;
}

.loading-spinner {
  width: 48rpx;
  height: 48rpx;
  border: 4rpx solid #FFE0B2;
  border-top-color: #FFB74D;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// ========== 空状态 ==========
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 48rpx;

  &__piggy {
    position: relative;
    width: 140rpx;
    height: 120rpx;
    margin-bottom: 40rpx;
  }

  &__piggy-body {
    position: absolute;
    bottom: 0;
    left: 10rpx;
    right: 10rpx;
    height: 80rpx;
    background: linear-gradient(135deg, #FFCCBC 0%, #FFAB91 100%);
    border-radius: 50%;
  }

  &__piggy-ear {
    position: absolute;
    top: 10rpx;
    left: 30rpx;
    width: 30rpx;
    height: 24rpx;
    background: #FF8A65;
    border-radius: 50% 50% 0 0;
  }

  &__piggy-nose {
    position: absolute;
    bottom: 30rpx;
    left: 50%;
    transform: translateX(-50%);
    width: 40rpx;
    height: 24rpx;
    background: #FF7043;
    border-radius: 50%;
  }

  &__piggy-slot {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 40rpx;
    height: 8rpx;
    background: #5D4037;
    border-radius: 4rpx;
  }

  &__title {
    font-size: 32rpx;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 12rpx;
  }

  &__desc {
    font-size: 26rpx;
    color: $text-tertiary;
    margin-bottom: 48rpx;
  }

}

// ========== 存折列表 ==========
.passbook {
  &__header {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 24rpx;
    padding: 0 8rpx;
  }

  &__title {
    font-size: 32rpx;
    font-weight: 600;
    color: $text-primary;
  }
}

// ========== 存折卡片 ==========
.passbook-item {
  position: relative;
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    0 8rpx 24rpx rgba(255, 152, 0, 0.08);
  opacity: 0;
  animation: fadeIn 0.4s ease forwards;
  transition: transform 0.2s ease;

  &:active {
    transform: scale(0.98);
  }

  &--completed {
    border: 2rpx solid #FFD54F;
    background: linear-gradient(135deg, #FFFDE7 0%, #FFF8E1 100%);
  }

  // 顶部
  &__header {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 24rpx;
  }

  &__icon-wrap {
    width: 64rpx;
    height: 64rpx;
    background: #FFF3E0;
    border-radius: 16rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &__title-area {
    flex: 1;
    min-width: 0;
  }

  &__name {
    font-size: 30rpx;
    font-weight: 600;
    color: $text-primary;
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__status {
    font-size: 22rpx;
    color: #FFB74D;
    display: block;
    margin-top: 4rpx;
  }

  &__badge {
    width: 44rpx;
    height: 44rpx;
    background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2rpx 8rpx rgba(255, 193, 7, 0.3);
  }

  // 金额区域
  &__amounts {
    display: flex;
    align-items: center;
    justify-content: space-around;
    padding: 20rpx 0;
    margin-bottom: 20rpx;
    background: #FFF8E1;
    border-radius: 12rpx;
  }

  &__amount {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  &__amount-label {
    font-size: 22rpx;
    color: $text-tertiary;
    margin-bottom: 8rpx;
  }

  &__amount-value {
    font-size: 32rpx;
    font-weight: 700;
    color: #F57C00;
    font-family: $font-family-number;
  }

  &__amount-divider {
    width: 2rpx;
    height: 48rpx;
    background: #FFE0B2;
  }

  // 进度条
  &__progress {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 20rpx;
  }

  &__bar {
    flex: 1;
    height: 16rpx;
    background: #FFF3E0;
    border-radius: 8rpx;
    overflow: hidden;
  }

  &__bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #FFB74D 0%, #FF9800 50%, #F57C00 100%);
    border-radius: 8rpx;
    transition: width 0.6s ease;
    position: relative;
  }

  &__bar-glow {
    position: absolute;
    top: 0;
    right: 0;
    width: 20rpx;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4));
    border-radius: 0 8rpx 8rpx 0;
  }

  &__percent {
    font-size: 28rpx;
    font-weight: 700;
    color: #F57C00;
    font-family: $font-family-number;
    flex-shrink: 0;
    min-width: 80rpx;
    text-align: right;
  }

  // 底部装饰
  &__deco {
    display: flex;
    align-items: center;
    gap: 16rpx;
    padding-top: 16rpx;
    border-top: 2rpx dashed #FFE0B2;
  }

  &__line {
    flex: 1;
    height: 2rpx;
    background: #FFE0B2;
  }

  &__line-text {
    font-size: 18rpx;
    color: #FFCC80;
    letter-spacing: 2rpx;
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(16rpx); }
  to { opacity: 1; transform: translateY(0); }
}

// ========== FAB 按钮 ==========
.fab {
  position: fixed;
  right: 40rpx;
  bottom: calc(120rpx + env(safe-area-inset-bottom));
  z-index: 100;

  &__inner {
    width: 112rpx;
    height: 112rpx;
    border-radius: 50%;
    background: linear-gradient(135deg, #FFB74D 0%, #FF9800 100%);
    box-shadow: 0 8rpx 24rpx rgba(255, 152, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease;

    &:active {
      transform: scale(0.9);
    }
  }
}
</style>
