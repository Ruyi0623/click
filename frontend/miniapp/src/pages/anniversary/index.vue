<template>
  <view class="page-anniversary">
    <!-- 顶部倒计时卡片 -->
    <view class="hero-card animate-reveal-days" v-if="nextAnniversary">
      <view class="hero-card__bg" />
      <view class="hero-card__content">
        <text class="hero-card__label">距离下一个纪念日</text>
        <text class="hero-card__title">{{ nextAnniversary.title }}</text>
        <view class="hero-card__countdown">
          <text class="hero-card__days animate-count-pulse">{{ nextAnniversary.days_until }}</text>
          <text class="hero-card__unit">天</text>
        </view>
        <text class="hero-card__date">{{ formatDateLong(nextAnniversary.date) }}</text>
      </view>
      <!-- 装饰圆点 -->
      <view class="hero-card__dot hero-card__dot--1" />
      <view class="hero-card__dot hero-card__dot--2" />
      <view class="hero-card__dot hero-card__dot--3" />
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading-wrap">
      <view class="loading-spinner" />
    </view>

    <!-- 空状态 -->
    <view v-else-if="!list.length" class="empty-state">
      <view class="empty-state__icon">
        <KdIcon name="tabler:calendar-star" :size="80" variant="pink" />
      </view>
      <text class="empty-state__title">时光等待被记录</text>
      <text class="empty-state__desc">创建你们的第一个纪念日，让每一个重要时刻都被铭记</text>
    </view>

    <!-- 时光轴列表 -->
    <view v-else class="timeline">
      <view class="timeline__header animate-fade-in-down">
        <view class="timeline__header-left">
          <KdIcon name="tabler:timeline" :size="36" variant="pink" />
          <text class="timeline__title">时光轴</text>
        </view>
        <text class="timeline__count">{{ list.length }} 个纪念日</text>
      </view>

      <!-- 即将到来 -->
      <view v-if="upcomingList.length" class="timeline__section">
        <view class="timeline__section-header">
          <view class="timeline__section-dot timeline__section-dot--future" />
          <text class="timeline__section-title">即将到来</text>
        </view>
        <view class="timeline__items">
          <view
            v-for="(item, index) in upcomingList"
            :key="item.id"
            class="polaroid animate-fade-in-up"
            :style="{ animationDelay: `${index * 80}ms` }"
            @tap="goEdit(item)"
            @longpress="deleteItem(item.id)"
          >
            <view class="polaroid__inner">
              <view class="polaroid__content">
                <view class="polaroid__icon-wrap">
                  <KdIcon :name="getAnniversaryIcon(item.title)" :size="44" variant="pink" />
                </view>
                <view class="polaroid__info">
                  <text class="polaroid__title">{{ item.title }}</text>
                  <text class="polaroid__date">{{ formatDateShort(item.date) }}</text>
                </view>
              </view>
              <view class="polaroid__footer">
                <view class="polaroid__badge">
                  <text class="polaroid__badge-days">{{ item.days_until }}</text>
                  <text class="polaroid__badge-unit">天后</text>
                </view>
                <view class="polaroid__repeat">
                  <KdIcon :name="item.repeat_type === 'yearly' ? 'tabler:reload' : 'tabler:clock'" :size="24" />
                  <text>{{ item.repeat_type === 'yearly' ? '每年' : '一次' }}</text>
                </view>
              </view>
            </view>
            <!-- 拍立得胶带效果 -->
            <view class="polaroid__tape" />
          </view>
        </view>
      </view>

      <!-- 已经过去 -->
      <view v-if="pastList.length" class="timeline__section">
        <view class="timeline__section-header">
          <view class="timeline__section-dot timeline__section-dot--past" />
          <text class="timeline__section-title">美好回忆</text>
        </view>
        <view class="timeline__items">
          <view
            v-for="(item, index) in pastList"
            :key="item.id"
            class="polaroid polaroid--past animate-fade-in-up"
            :style="{ animationDelay: `${(upcomingList.length + index) * 80}ms` }"
            @tap="goEdit(item)"
            @longpress="deleteItem(item.id)"
          >
            <view class="polaroid__inner">
              <view class="polaroid__content">
                <view class="polaroid__icon-wrap">
                  <KdIcon :name="getAnniversaryIcon(item.title)" :size="44" />
                </view>
                <view class="polaroid__info">
                  <text class="polaroid__title">{{ item.title }}</text>
                  <text class="polaroid__date">{{ formatDateShort(item.date) }}</text>
                </view>
              </view>
              <view class="polaroid__footer">
                <view class="polaroid__badge polaroid__badge--past">
                  <KdIcon name="tabler:backward" :size="24" />
                  <text class="polaroid__badge-text">已过</text>
                </view>
                <view class="polaroid__repeat">
                  <KdIcon :name="item.repeat_type === 'yearly' ? 'tabler:reload' : 'tabler:clock'" :size="24" />
                  <text>{{ item.repeat_type === 'yearly' ? '每年' : '一次' }}</text>
                </view>
              </view>
            </view>
            <view class="polaroid__tape" />
          </view>
        </view>
      </view>

      <!-- 时间轴装饰线 -->
      <view class="timeline__line" />
    </view>

    <!-- FAB 按钮 -->
    <view class="fab" @tap="goCreate">
      <view class="fab__inner">
        <KdIcon name="tabler:plus" :size="48" color="#fff" />
      </view>
    </view>

    <KdDialog
      v-model:visible="showDeleteConfirm"
      title="删除纪念日"
      content="确定要删除这个珍贵的回忆吗？"
      confirm-color="#EF5350"
      @confirm="onDeleteConfirm"
    />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'
import { anniversaryApi, type Anniversary } from '@/api/anniversary'
import KdIcon from '@/components/KdIcon.vue'
import KdDialog from '@/components/KdDialog.vue'

const showDeleteConfirm = ref(false)
const deleteTargetId = ref('')

const list = ref<Anniversary[]>([])
const loading = ref(true)

// 计算属性
const nextAnniversary = computed(() => {
  return list.value.find(item => item.days_until !== null && item.days_until > 0)
})

const upcomingList = computed(() => {
  return list.value
    .filter(item => item.days_until !== null && item.days_until > 0)
    .sort((a, b) => (a.days_until || 0) - (b.days_until || 0))
})

const pastList = computed(() => {
  return list.value.filter(item => item.days_until === null || item.days_until <= 0)
})

// 根据纪念日标题智能匹配图标
const getAnniversaryIcon = (title: string): string => {
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
    if (title.includes(key)) return icon
  }
  return 'tabler:calendar-heart'
}

// 日期格式化
const formatDateShort = (dateStr: string): string => {
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}

const formatDateLong = (dateStr: string): string => {
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  const weekDay = weekDays[date.getDay()]
  return `${year}年${month}月${day}日 · 周${weekDay}`
}

// 数据加载
const loadList = async () => {
  try {
    list.value = await anniversaryApi.list()
  } catch {} finally {
    loading.value = false
  }
}

const goCreate = () => uni.navigateTo({ url: '/pages/anniversary/create' })
const goEdit = (item: Anniversary) => {
  uni.navigateTo({ url: `/pages/anniversary/create?id=${item.id}&title=${item.title}&date=${item.date}&repeat=${item.repeat_type}` })
}

const deleteItem = (id: string) => {
  deleteTargetId.value = id
  showDeleteConfirm.value = true
}

const onDeleteConfirm = async () => {
  try {
    await anniversaryApi.delete(deleteTargetId.value)
    uni.showToast({ title: '已删除', icon: 'success' })
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

.page-anniversary {
  min-height: 100vh;
  background: #FFF5F7;
  padding: 0 32rpx;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));
}

// ========== 顶部倒计时卡片 ==========
.hero-card {
  position: relative;
  margin: 24rpx 0 40rpx;
  border-radius: 32rpx;
  overflow: hidden;
  background: linear-gradient(135deg, #FF8FA3 0%, #FF6B8A 50%, #FFB3C6 100%);
  padding: 48rpx 40rpx;
  box-shadow: 0 16rpx 48rpx rgba(255, 107, 138, 0.3);
  opacity: 0;

  &__bg {
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400rpx;
    height: 400rpx;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
  }

  &__content {
    position: relative;
    z-index: 1;
    text-align: center;
  }

  &__label {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.8);
    letter-spacing: 2rpx;
  }

  &__title {
    display: block;
    font-size: 36rpx;
    font-weight: 600;
    color: #fff;
    margin: 16rpx 0 24rpx;
  }

  &__countdown {
    display: flex;
    align-items: baseline;
    justify-content: center;
    gap: 8rpx;
  }

  &__days {
    font-size: 96rpx;
    font-weight: 700;
    color: #fff;
    font-family: 'DIN Alternate', 'Roboto Mono', monospace;
    line-height: 1;
    text-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  }

  &__unit {
    font-size: 32rpx;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 500;
  }

  &__date {
    display: block;
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 16rpx;
  }

  // 装饰圆点
  &__dot {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.15);

    &--1 {
      width: 120rpx;
      height: 120rpx;
      top: -30rpx;
      left: -20rpx;
      animation: float 6s ease-in-out infinite;
    }

    &--2 {
      width: 80rpx;
      height: 80rpx;
      bottom: -20rpx;
      right: 60rpx;
      animation: float 8s ease-in-out infinite reverse;
    }

    &--3 {
      width: 40rpx;
      height: 40rpx;
      top: 40rpx;
      right: 20rpx;
      animation: float 5s ease-in-out infinite 1s;
    }
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-10rpx) scale(1.05); }
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
  border: 4rpx solid #FFE4E8;
  border-top-color: #FF6B8A;
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
  padding: 120rpx 48rpx 80rpx;

  &__icon {
    width: 160rpx;
    height: 160rpx;
    background: linear-gradient(135deg, #FFF0F2 0%, #FFE4E8 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 40rpx;
    box-shadow: 0 8rpx 32rpx rgba(255, 107, 138, 0.15);
  }

  &__title {
    font-size: 36rpx;
    font-weight: 600;
    color: #2D2D3F;
    margin-bottom: 16rpx;
  }

  &__desc {
    font-size: 26rpx;
    color: #9E9EB0;
    text-align: center;
    line-height: 1.6;
  }
}

// ========== 时光轴 ==========
.timeline {
  position: relative;

  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32rpx;
    padding: 0 8rpx;
    opacity: 0;
  }

  &__header-left {
    display: flex;
    align-items: center;
    gap: 12rpx;
  }

  &__title {
    font-size: 32rpx;
    font-weight: 600;
    color: #2D2D3F;
  }

  &__count {
    font-size: 24rpx;
    color: #9E9EB0;
  }

  &__section {
    margin-bottom: 48rpx;
  }

  &__section-header {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 24rpx;
    padding-left: 8rpx;
  }

  &__section-dot {
    width: 16rpx;
    height: 16rpx;
    border-radius: 50%;

    &--future {
      background: linear-gradient(135deg, #FF6B8A, #FF8FA3);
      box-shadow: 0 0 12rpx rgba(255, 107, 138, 0.4);
    }

    &--past {
      background: linear-gradient(135deg, #B39DDB, #D1C4E9);
    }
  }

  &__section-title {
    font-size: 28rpx;
    font-weight: 500;
    color: #6B6B80;
  }

  &__items {
    display: flex;
    flex-direction: column;
    gap: 24rpx;
  }

  // 时间轴装饰线
  &__line {
    position: absolute;
    left: 48rpx;
    top: 180rpx;
    bottom: 100rpx;
    width: 4rpx;
    background: linear-gradient(
      180deg,
      rgba(255, 107, 138, 0.3) 0%,
      rgba(179, 157, 219, 0.3) 50%,
      rgba(255, 228, 232, 0) 100%
    );
    z-index: 0;
  }
}

// ========== 拍立得卡片 ==========
.polaroid {
  position: relative;
  z-index: 1;
  transition: transform 0.2s ease;

  &:active {
    transform: scale(0.96);
  }

  &__inner {
    background: #fff;
    border-radius: 20rpx;
    padding: 32rpx;
    margin-left: 64rpx;
    box-shadow:
      0 2rpx 8rpx rgba(0, 0, 0, 0.04),
      0 8rpx 24rpx rgba(255, 107, 138, 0.08);
    transition: box-shadow 0.2s ease;
  }

  &__content {
    display: flex;
    align-items: center;
    gap: 24rpx;
    margin-bottom: 24rpx;
  }

  &__icon-wrap {
    width: 80rpx;
    height: 80rpx;
    background: linear-gradient(135deg, #FFF0F2 0%, #FFE4E8 100%);
    border-radius: 20rpx;
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
    font-size: 30rpx;
    font-weight: 500;
    color: #2D2D3F;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 8rpx;
  }

  &__date {
    display: block;
    font-size: 24rpx;
    color: #9E9EB0;
  }

  &__footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 24rpx;
    border-top: 2rpx solid #FFF5F7;
  }

  &__badge {
    display: flex;
    align-items: baseline;
    gap: 4rpx;

    &-days {
      font-size: 40rpx;
      font-weight: 700;
      color: #FF6B8A;
      font-family: 'DIN Alternate', 'Roboto Mono', monospace;
      line-height: 1;
    }

    &-unit {
      font-size: 22rpx;
      color: #FF8FA3;
      font-weight: 500;
    }

    &--past {
      display: flex;
      align-items: center;
      gap: 8rpx;

      .polaroid__badge-text {
        font-size: 24rpx;
        color: #B39DDB;
        font-weight: 500;
      }
    }
  }

  &__repeat {
    display: flex;
    align-items: center;
    gap: 8rpx;
    font-size: 22rpx;
    color: #9E9EB0;
    background: #F8F8FC;
    padding: 8rpx 16rpx;
    border-radius: 8rpx;
  }

  // 胶带效果 - 和纸胶带风格
  &__tape {
    position: absolute;
    top: -14rpx;
    left: 36rpx;
    width: 100rpx;
    height: 36rpx;
    transform: rotate(-6deg);
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

  // 已过期状态
  &--past {
    .polaroid__inner {
      opacity: 0.85;
    }

    .polaroid__icon-wrap {
      background: linear-gradient(135deg, #F3E5F5 0%, #E8DEF8 100%);
    }

    .polaroid__tape {
      background-color: rgba(179, 157, 219, 0.8);
      background-image: repeating-linear-gradient(
        90deg,
        rgba(255, 255, 255, 0.25) 0rpx,
        rgba(255, 255, 255, 0.25) 2rpx,
        transparent 2rpx,
        transparent 8rpx
      );
      box-shadow:
        0 2rpx 6rpx rgba(0, 0, 0, 0.12),
        inset 0 1rpx 0 rgba(255, 255, 255, 0.35);
    }
  }
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
    background: linear-gradient(135deg, #FF6B8A 0%, #FF8FA3 100%);
    box-shadow:
      0 8rpx 24rpx rgba(255, 107, 138, 0.4),
      0 0 0 8rpx rgba(255, 107, 138, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;

    &:active {
      transform: scale(0.9);
      box-shadow:
        0 4rpx 12rpx rgba(255, 107, 138, 0.4),
        0 0 0 4rpx rgba(255, 107, 138, 0.1);
    }
  }
}

// ========== 动画 ==========
.animate-fade-in-up {
  animation: fadeInUp 0.5s ease forwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
