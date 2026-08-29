<template>
  <view class="page-magazine">
    <view v-if="loading" class="loading-wrap"><view class="loading-spinner animate-spin" /></view>
    <KdEmpty v-else-if="!list.length && !generating" title="还没有月刊" desc="AI 会根据你们的互动自动生成恋爱月刊" icon="tabler:book-2">
      <button class="empty-btn" @tap="generate">生成上月月刊</button>
    </KdEmpty>
    <view v-else>
      <!-- 统计卡片 -->
      <view v-if="list.length" class="stats-card animate-fade-in-down">
        <view class="stats-card__icon">
          <KdIcon name="tabler:book-2" :size="36" color="rgba(255,255,255,0.9)" />
        </view>
        <view class="stats-card__info">
          <text class="stats-card__label">恋爱月刊</text>
          <text class="stats-card__count">已生成 {{ list.filter(i => i.status === 'success').length }} 期</text>
        </view>
        <view class="stats-card__action" @tap="generate">
          <KdIcon name="tabler:reload" :size="28" color="rgba(255,255,255,0.8)" />
        </view>
      </view>

      <!-- 生成中动画 -->
      <view v-if="generating" class="generating-card animate-fade-in-up">
        <view class="generating-icon animate-breathe">
          <KdIcon name="tabler:sparkles" :size="48" color="#B39DDB" />
        </view>
        <text class="generating-text">{{ generatingText }}</text>
        <view class="generating-dots">
          <view class="generating-dot" />
          <view class="generating-dot" />
          <view class="generating-dot" />
        </view>
      </view>

      <!-- 月刊列表 -->
      <view class="magazine-list">
        <view v-for="(item, index) in list" :key="item.id" class="magazine-item animate-fade-in-up" :style="{ animationDelay: `${index * 50}ms` }" @tap="item.status === 'success' ? goDetail(item.id) : retryGenerate(item)" @longpress="onLongPress(item)">
          <view class="magazine-item__cover" :style="{ background: item.status === 'failed' ? 'linear-gradient(135deg, #E0E0E0, #BDBDBD)' : getMonthGradient(item.month) }">
            <text class="magazine-item__month">{{ item.month }}月</text>
            <text class="magazine-item__year">{{ item.year }}</text>
            <view v-if="item.status === 'failed'" class="magazine-item__failed">
              <KdIcon name="tabler:refresh" :size="28" color="#fff" />
              <text class="magazine-item__failed-text">生成失败，点击重试</text>
            </view>
          </view>
          <text class="magazine-item__title">恋爱月刊</text>
        </view>
      </view>
    </view>

    <!-- 操作菜单 -->
    <KdActionSheet
      v-model:visible="showAction"
      :actions="actionActions"
      @select="onActionSelect"
    />

    <!-- 删除确认 -->
    <KdDialog
      v-model:visible="showDeleteConfirm"
      title="删除月刊"
      content="确定要删除吗？"
      confirm-color="#EF5350"
      @confirm="onDeleteConfirm"
    />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'
import { magazineApi, type Magazine } from '@/api/magazine'
import KdEmpty from '@/components/KdEmpty.vue'
import KdIcon from '@/components/KdIcon.vue'
import KdActionSheet from '@/components/KdActionSheet.vue'
import KdDialog from '@/components/KdDialog.vue'

// 操作菜单状态
const showAction = ref(false)
const actionTarget = ref<Magazine | null>(null)
const actionActions = ref<Array<{ label: string; destructive?: boolean }>>([])

// 删除确认
const showDeleteConfirm = ref(false)

const list = ref<Magazine[]>([])
const loading = ref(true)
const generating = ref(false)
const generatingText = ref('')

// 12 个月份渐变色（春绿/夏蓝/秋橙/冬紫）
const monthGradients: Record<string, string> = {
  '01': 'linear-gradient(135deg, #E8DEF8, #B39DDB)',
  '02': 'linear-gradient(135deg, #FFD6DE, #FF8FA3)',
  '03': 'linear-gradient(135deg, #C8E6C9, #81C784)',
  '04': 'linear-gradient(135deg, #B3E5FC, #4FC3F7)',
  '05': 'linear-gradient(135deg, #FFF9C4, #FFD54F)',
  '06': 'linear-gradient(135deg, #B2EBF2, #00BCD4)',
  '07': 'linear-gradient(135deg, #F8BBD0, #E91E63)',
  '08': 'linear-gradient(135deg, #DCEDC8, #8BC34A)',
  '09': 'linear-gradient(135deg, #FFE0B2, #FF9800)',
  '10': 'linear-gradient(135deg, #FFCCBC, #FF5722)',
  '11': 'linear-gradient(135deg, #D1C4E9, #7E57C2)',
  '12': 'linear-gradient(135deg, #BBDEFB, #42A5F5)',
}

const getMonthGradient = (month: string) => monthGradients[month] || monthGradients['01']

const loadList = async () => { try { list.value = await magazineApi.list() } catch {} finally { loading.value = false } }
const goDetail = (id: string) => uni.navigateTo({ url: `/pages/magazine/detail?id=${id}` })

const retryGenerate = async (item: Magazine) => {
  uni.showModal({
    title: '重新生成',
    content: `${item.year}年${item.month}月的月刊生成失败，是否重新生成？`,
    success: async (res) => {
      if (res.confirm) {
        startGeneratingAnimation()
        try {
          await magazineApi.generate(item.year, item.month)
          uni.showToast({ title: '生成成功', icon: 'success' })
          await loadList()
        } catch (e: any) {
          uni.showToast({ title: e.message || '生成失败', icon: 'none' })
        } finally {
          stopGeneratingAnimation()
        }
      }
    },
  })
}

// 生成动画文字轮播
const generatingTexts = [
  'AI 正在观察你们的恋爱...',
  '分析本月互动数据...',
  '撰写恋爱月刊...',
  '即将完成...',
]
let textTimer: any = null

const startGeneratingAnimation = () => {
  generating.value = true
  let idx = 0
  generatingText.value = generatingTexts[0]
  textTimer = setInterval(() => {
    idx = (idx + 1) % generatingTexts.length
    generatingText.value = generatingTexts[idx]
  }, 2000)
}

const stopGeneratingAnimation = () => {
  generating.value = false
  if (textTimer) { clearInterval(textTimer); textTimer = null }
}

// 获取上个月的年月
const getPrevMonth = () => {
  const now = new Date()
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
  const prev = new Date(firstDay.getTime() - 1)
  return {
    year: String(prev.getFullYear()),
    month: String(prev.getMonth() + 1).padStart(2, '0'),
  }
}

const generate = async () => {
  const { year, month } = getPrevMonth()
  startGeneratingAnimation()
  try {
    await magazineApi.generate(year, month)
    uni.showToast({ title: '生成成功', icon: 'success' })
    await loadList()
  } catch (e: any) {
    uni.showToast({ title: e.message || '生成失败', icon: 'none' })
  } finally {
    stopGeneratingAnimation()
  }
}

const onLongPress = (item: Magazine) => {
  actionTarget.value = item
  if (item.status === 'failed') {
    actionActions.value = [
      { label: '重新生成' },
      { label: '删除', destructive: true },
    ]
  } else {
    // 成功的月刊：不可操作
    return
  }
  showAction.value = true
}

const onActionSelect = async (_action: any, index: number) => {
  const item = actionTarget.value
  if (!item) return

  if (item.status === 'failed' && index === 0) {
    // 重新生成
    startGeneratingAnimation()
    try {
      await magazineApi.generate(item.year, item.month)
      uni.showToast({ title: '生成成功', icon: 'success' })
      await loadList()
    } catch (e: any) {
      uni.showToast({ title: e.message || '生成失败', icon: 'none' })
    } finally {
      stopGeneratingAnimation()
    }
  } else {
    showDeleteConfirm.value = true
  }
}

const onDeleteConfirm = async () => {
  const item = actionTarget.value
  if (!item) return
  try {
    await magazineApi.delete(item.id)
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
.page-magazine { min-height: 100vh; background: $bg-page; padding: $padding-page; }
.loading-wrap { display: flex; justify-content: center; padding: 120rpx 0; }
.loading-spinner { width: 48rpx; height: 48rpx; border: 4rpx solid $border-light; border-top-color: $sunrise-gold; border-radius: 50%; }
.empty-btn { margin-top: 32rpx; background: $gradient-sunset; color: #fff; border: none; border-radius: $radius-full; height: 80rpx; padding: 0 48rpx; font-size: $font-size-base; display: flex; align-items: center; justify-content: center; &::after { display: none; } }

.stats-card {
  display: flex; align-items: center;
  background: linear-gradient(135deg, #FFD6DE, #FF8FA3);
  border-radius: $radius-lg; padding: 32rpx; margin-bottom: 24rpx;
  box-shadow:
    0 8rpx 32rpx rgba(255, 107, 138, 0.2),
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.3);
  opacity: 0;
}
.stats-card__icon { margin-right: 16rpx; }
.stats-card__info { flex: 1; }
.stats-card__label { font-size: $font-size-sm; color: rgba(255,255,255,0.85); display: block; }
.stats-card__count { font-size: $font-size-xl; font-weight: $font-weight-bold; color: #fff; font-family: $font-family-number; display: block; margin-top: 4rpx; }
.stats-card__action {
  width: 56rpx; height: 56rpx; border-radius: $radius-full;
  background: rgba(255,255,255,0.25); display: flex; align-items: center; justify-content: center;
}

.generating-card {
  background: $bg-card; border-radius: $radius-lg; padding: 48rpx; margin-bottom: 24rpx;
  text-align: center;
  box-shadow:
    0 4rpx 20rpx rgba(0, 0, 0, 0.04),
    0 8rpx 32rpx rgba(179, 157, 219, 0.08),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.8);
}
.generating-icon { margin-bottom: 16rpx; }
.generating-text { font-size: $font-size-base; color: $text-secondary; display: block; margin-bottom: 16rpx; }
.generating-dots { display: flex; justify-content: center; gap: 12rpx; }
.generating-dot {
  width: 12rpx; height: 12rpx; border-radius: 50%; background: $lavender;
  animation: dotPulse 1.4s infinite ease-in-out both;
  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}
@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.magazine-list { display: flex; flex-wrap: wrap; margin: 0 -10rpx; }
.magazine-item {
  width: calc(50% - 20rpx); margin: 0 10rpx $gap-grid;
  opacity: 0; background: $bg-card; border-radius: $radius-lg; overflow: hidden;
  box-shadow:
    0 4rpx 16rpx rgba(0, 0, 0, 0.05),
    0 8rpx 32rpx rgba(255, 107, 138, 0.08);
  &:active { transform: scale(0.96); }
  &__cover { padding: 48rpx 24rpx; text-align: center; }
  &__month { font-size: 72rpx; font-weight: $font-weight-bold; color: rgba(255, 255, 255, 0.9); display: block; font-family: $font-family-number; line-height: 1; }
  &__year { font-size: $font-size-sm; color: rgba(255, 255, 255, 0.7); display: block; margin-top: 8rpx; }
  &__title { font-size: $font-size-base; font-weight: $font-weight-medium; color: $text-primary; display: block; padding: 16rpx; text-align: center; }

  &__failed {
    margin-top: 16rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8rpx;
  }
  &__failed-text {
    font-size: 22rpx;
    color: rgba(255, 255, 255, 0.9);
  }
}
</style>
