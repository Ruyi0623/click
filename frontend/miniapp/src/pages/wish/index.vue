<template>
  <view class="page-wish" :class="{ 'page-wish--loaded': loaded }">
    <!-- 统计区 -->
    <view class="stats" :class="{ 'stats--show': loaded }">
      <view class="stats__row">
        <view class="stats__icon-wrap">
          <KdIcon name="tabler:heart" :size="48" variant="pink" />
        </view>
        <view class="stats__numbers">
          <view class="stats__fraction">
            <text class="stats__num stats__num--done">{{ doneCount }}</text>
            <text class="stats__sep">/</text>
            <text class="stats__num stats__num--total">{{ list.length }}</text>
          </view>
          <text class="stats__label">已完成的心愿</text>
        </view>
      </view>
      <view class="stats__bar">
        <view class="stats__bar-fill" :style="{ width: progressWidth }" />
      </view>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading-wrap">
      <view class="loading-spinner" />
    </view>

    <!-- 空状态 -->
    <view v-else-if="!list.length" class="empty-state" :class="{ 'empty-state--show': loaded }">
      <view class="empty-state__icon-wrap">
        <text class="empty-state__heart">♥</text>
      </view>
      <text class="empty-state__fraction">0 / ∞</text>
      <text class="empty-state__title">还没有心愿</text>
      <text class="empty-state__desc">许下你们的第一个愿望</text>
    </view>

    <!-- 愿望列表 -->
    <view v-else class="wish-list">
      <view
        v-for="(item, index) in list"
        :key="item.id"
        class="wish-card"
        :class="{
          'wish-card--done': item.is_done,
          'wish-card--entering': enteringId === item.id,
          'wish-card--deleting': deletingId === item.id,
        }"
        :style="{ '--delay': `${index * 60}ms` }"
        @tap="toggleDone(item)"
        @longpress="onLongPress(item)"
      >
        <!-- 左侧指示器 -->
        <view class="wish-card__indicator">
          <view class="wish-card__dot" />
        </view>

        <!-- 内容 -->
        <view class="wish-card__body">
          <text class="wish-card__text">{{ item.content }}</text>
          <view class="wish-card__meta">
            <text v-if="item.creator_nickname" class="wish-card__creator">{{ item.creator_nickname }}</text>
            <text v-if="item.created_at" class="wish-card__time">{{ formatCreatedAt(item.created_at) }}</text>
          </view>
          <text v-if="item.is_done && item.done_at" class="wish-card__done-date">
            ♥ {{ formatDoneDate(item.done_at) }} 已实现
          </text>
        </view>

        <!-- 已完成装饰 -->
        <view v-if="item.is_done" class="wish-card__deco">♥</view>
      </view>
    </view>

    <!-- 悬浮按钮 -->
    <view class="fab" @tap="showCreateDialog = true">
      <KdIcon name="tabler:plus" :size="48" color="#fff" />
    </view>
  </view>

  <!-- 操作菜单 -->
  <KdActionSheet
    :visible="showMenu"
    :actions="menuActions"
    @close="showMenu = false"
    @select="onMenuSelect"
  />

  <!-- 编辑弹窗 -->
  <KdDialog
    :visible="showEditDialog"
    title="编辑愿望"
    :show-input="true"
    :input-value="editContent"
    input-placeholder="输入愿望内容"
    @close="showEditDialog = false"
    @confirm="onEditConfirm"
  />

  <!-- 删除确认弹窗 -->
  <KdDialog
    :visible="showDeleteDialog"
    title="删除愿望"
    content="删除后无法恢复，确定吗？"
    confirm-text="删除"
    confirm-color="#EF5350"
    @close="showDeleteDialog = false"
    @confirm="onDeleteConfirm"
  />

  <!-- 新建愿望弹窗 -->
  <KdDialog
    :visible="showCreateDialog"
    title="许个愿吧"
    :show-input="true"
    input-placeholder="写下你们的心愿"
    confirm-text="许愿"
    @close="showCreateDialog = false"
    @confirm="onCreateConfirm"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'
import { wishApi, type Wish } from '@/api/wish'
import KdIcon from '@/components/KdIcon.vue'
import KdActionSheet from '@/components/KdActionSheet.vue'
import KdDialog from '@/components/KdDialog.vue'

// ===== 数据 =====
const list = ref<Wish[]>([])
const loading = ref(true)
const loaded = ref(false)
let loadSeq = 0  // 请求序号，防止并发 loadList 交错

// ===== 动画状态 =====
const enteringId = ref('')
const deletingId = ref('')

// ===== 菜单/弹窗 =====
const showMenu = ref(false)
const menuTarget = ref<Wish | null>(null)
const showEditDialog = ref(false)
const editContent = ref('')
const showDeleteDialog = ref(false)
const showCreateDialog = ref(false)

const menuActions = [
  { label: '编辑', color: '#42A5F5' },
  { label: '删除', destructive: true },
]

// ===== 计算属性 =====
const doneCount = computed(() => list.value.filter((w) => w.is_done).length)
const progressWidth = computed(() => {
  if (!list.value.length) return '0%'
  return `${Math.round((doneCount.value / list.value.length) * 100)}%`
})

// ===== 工具函数 =====
const formatCreatedAt = (dateStr: string): string => {
  try {
    const d = new Date(dateStr)
    return `${d.getMonth() + 1}月${d.getDate()}日`
  } catch {
    return ''
  }
}

const formatDoneDate = (dateStr: string): string => {
  try {
    const d = new Date(dateStr)
    return `${d.getMonth() + 1}月${d.getDate()}日`
  } catch {
    return ''
  }
}

// ===== 数据加载 =====
const loadList = async () => {
  const seq = ++loadSeq
  try {
    const data = await wishApi.list()
    if (seq !== loadSeq) return  // 有更新的请求，丢弃本次结果
    list.value = data
  } catch {
  } finally {
    if (seq !== loadSeq) return
    loading.value = false
    if (!loaded.value) {
      await nextTick()
      setTimeout(() => { loaded.value = true }, 50)
    }
  }
}

// ===== 添加愿望 =====
const onCreateConfirm = async (value?: string) => {
  const content = (value || '').trim()
  if (!content) return
  try {
    const newItem = await wishApi.create(content)
    showCreateDialog.value = false
    uni.vibrateShort({ type: 'light' })
    enteringId.value = newItem.id
    await loadList()
    setTimeout(() => { enteringId.value = '' }, 400)
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

// ===== 切换完成状态 =====
const togglingIds = new Set<string>()
const toggleDone = async (item: Wish) => {
  if (togglingIds.has(item.id)) return  // 防止重复点击
  togglingIds.add(item.id)
  try {
    uni.vibrateShort({ type: 'medium' })
    await wishApi.update(item.id, { is_done: !item.is_done })
    await loadList()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    togglingIds.delete(item.id)
  }
}

// ===== 长按菜单 =====
const onLongPress = (item: Wish) => {
  uni.vibrateShort({ type: 'heavy' })
  menuTarget.value = item
  showMenu.value = true
}

const onMenuSelect = (action: { label: string }) => {
  showMenu.value = false
  if (!menuTarget.value) return

  if (action.label === '编辑') {
    editContent.value = menuTarget.value.content
    setTimeout(() => { showEditDialog.value = true }, 100)
  } else if (action.label === '删除') {
    setTimeout(() => { showDeleteDialog.value = true }, 100)
  }
}

// ===== 编辑 =====
const onEditConfirm = async (value?: string) => {
  const content = (value || '').trim()
  if (!content || !menuTarget.value) return
  const targetId = menuTarget.value.id
  menuTarget.value = null
  try {
    await wishApi.update(targetId, { content })
    showEditDialog.value = false
    await loadList()
    uni.showToast({ title: '已修改', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

// ===== 删除 =====
const onDeleteConfirm = async () => {
  if (!menuTarget.value) return
  const id = menuTarget.value.id
  menuTarget.value = null
  showDeleteDialog.value = false

  deletingId.value = id
  setTimeout(async () => {
    try {
      await wishApi.delete(id)
      await loadList()
      deletingId.value = ''  // 列表已刷新，卡片已不存在，再清状态
      uni.showToast({ title: '已删除', icon: 'success' })
    } catch (e: any) {
      deletingId.value = ''
      uni.showToast({ title: e.message, icon: 'none' })
    }
  }, 450)
}

// ===== 生命周期 =====
onMounted(loadList)
onShow(loadList)
onPullDownRefresh(async () => {
  await loadList()
  uni.stopPullDownRefresh()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

// ===== 缓动曲线 =====
$ease-power2-out: cubic-bezier(0.22, 0.61, 0.36, 1);
$ease-power2-in: cubic-bezier(0.55, 0.06, 0.68, 0.19);

// ===== 页面 =====
.page-wish {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF0F2 0%, #FFF8F9 40%, #FBF5FF 100%);
  padding: $padding-page;
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
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
  border-top-color: $heart-pink;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

// ===== 统计区 =====
.stats {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 32rpx;
  margin-bottom: $space-base;
  box-shadow:
    0 2rpx 8rpx rgba(255, 107, 138, 0.06),
    0 8rpx 24rpx rgba(255, 107, 138, 0.04);
  opacity: 0;
  transform: translateY(-20rpx);
  transition: opacity 0.5s $ease-power2-out, transform 0.5s $ease-power2-out;

  &--show {
    opacity: 1;
    transform: translateY(0);
  }

  &__row {
    display: flex;
    align-items: center;
    gap: $space-md;
    margin-bottom: $space-md;
  }

  &__icon-wrap {
    width: 80rpx;
    height: 80rpx;
    border-radius: $radius-full;
    background: $heart-pink-ghost;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &__numbers {
    flex: 1;
  }

  &__fraction {
    display: flex;
    align-items: baseline;
    gap: 6rpx;
  }

  &__num {
    font-family: $font-family-number;
    font-weight: $font-weight-bold;
    line-height: 1;

    &--done {
      font-size: $font-size-xxl;
      color: $heart-pink;
    }

    &--total {
      font-size: $font-size-xl;
      color: $text-tertiary;
    }
  }

  &__sep {
    font-size: $font-size-lg;
    color: $border-normal;
    font-weight: $font-weight-regular;
  }

  &__label {
    font-size: $font-size-xs;
    color: $text-tertiary;
    margin-top: 4rpx;
    display: block;
  }

  &__bar {
    width: 100%;
    height: 12rpx;
    background: $border-light;
    border-radius: 6rpx;
    overflow: hidden;
  }

  &__bar-fill {
    height: 100%;
    background: $gradient-heart;
    border-radius: 6rpx;
    transition: width 0.6s $ease-power2-out;
    min-width: 0;
    box-shadow: 0 0 8rpx rgba($heart-pink, 0.3);
  }
}

// ===== 空状态 =====
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 48rpx;
  opacity: 0;
  transition: opacity 0.5s $ease-power2-out;

  &--show {
    opacity: 1;
  }

  &__icon-wrap {
    width: 160rpx;
    height: 160rpx;
    border-radius: $radius-full;
    background: $heart-pink-ghost;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: $space-lg;
  }

  &__heart {
    font-size: 80rpx;
    color: $heart-pink-pale;
    line-height: 1;
    animation: heartBeat 2s ease-in-out infinite;
  }

  &__fraction {
    font-size: $font-size-display;
    font-weight: $font-weight-bold;
    color: $heart-pink-pale;
    font-family: $font-family-number;
    margin-bottom: $space-sm;
  }

  &__title {
    font-size: $font-size-md;
    font-weight: $font-weight-semibold;
    color: $text-primary;
    margin-bottom: $space-xs;
  }

  &__desc {
    font-size: $font-size-sm;
    color: $text-tertiary;
  }
}

@keyframes heartBeat {
  0%, 100% { transform: scale(1); }
  14% { transform: scale(1.08); }
  28% { transform: scale(1); }
  42% { transform: scale(1.08); }
  56% { transform: scale(1); }
}

// ===== 愿望列表 =====
.wish-list {
  display: flex;
  flex-direction: column;
  gap: $space-sm;
}

// ===== 愿望卡片 =====
.wish-card {
  display: flex;
  align-items: flex-start;
  gap: $space-md;
  background: $bg-card;
  border-radius: $radius-lg;
  padding: $space-base;
  position: relative;
  overflow: hidden;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.03),
    0 4rpx 12rpx rgba(255, 107, 138, 0.03);
  transition:
    background-color 0.3s $ease-power2-out,
    box-shadow 0.3s $ease-power2-out,
    transform 0.15s ease,
    opacity 0.25s $ease-power2-in,
    max-height 0.2s $ease-power2-out,
    margin-bottom 0.2s $ease-power2-out,
    padding 0.2s $ease-power2-out;

  // 入场动画
  opacity: 0;
  transform: translateY(16rpx);
  .page-wish--loaded & {
    opacity: 1;
    transform: translateY(0);
    transition-delay: var(--delay, 0ms), 0ms, 0ms, 0ms, 0ms, 0ms, 0ms;
  }

  // 按压反馈
  &:active {
    transform: scale(0.98);
  }

  // 已完成状态
  &--done {
    background: linear-gradient(135deg, $heart-pink-ghost 0%, rgba(255, 255, 255, 0.95) 100%);
    box-shadow:
      0 2rpx 8rpx rgba(0, 0, 0, 0.02),
      0 4rpx 16rpx rgba(255, 107, 138, 0.06);

    .wish-card__text {
      color: $text-secondary;
      text-decoration: line-through;
      text-decoration-color: rgba($text-tertiary, 0.4);
    }
  }

  // 新增入场
  &--entering {
    animation: cardEnter 0.35s $ease-power2-out forwards;
  }

  // 删除动画
  &--deleting {
    opacity: 0;
    transform: translateX(-16rpx) scale(0.98);
    max-height: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    overflow: hidden;
  }

  // ===== 指示器 =====
  &__indicator {
    width: 40rpx;
    height: 40rpx;
    flex-shrink: 0;
    margin-top: 2rpx;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__dot {
    width: 20rpx;
    height: 20rpx;
    border-radius: 50%;
    background: $mint;
    box-shadow:
      0 0 0 6rpx rgba($mint, 0.12),
      0 0 12rpx rgba($mint, 0.25);
    animation: breathe 3s ease-in-out infinite;
    transition: background 0.3s $ease-power2-out, box-shadow 0.3s $ease-power2-out;
  }

  &--done &__dot {
    background: $heart-pink;
    box-shadow:
      0 0 0 6rpx rgba($heart-pink, 0.12),
      0 0 12rpx rgba($heart-pink, 0.3);
    animation: none;
  }

  // ===== 内容 =====
  &__body {
    flex: 1;
    min-width: 0;
  }

  &__text {
    font-size: $font-size-base;
    font-weight: $font-weight-medium;
    color: $text-primary;
    display: block;
    line-height: $line-height-relaxed;
    transition: color 0.2s $ease-power2-out;
  }

  &__meta {
    display: flex;
    align-items: center;
    gap: $space-xs;
    margin-top: 6rpx;
  }

  &__creator {
    font-size: $font-size-xs;
    color: $text-tertiary;
    font-weight: $font-weight-medium;
  }

  &__time {
    font-size: $font-size-xs;
    color: $text-tertiary;

    &::before {
      content: '·';
      margin-right: $space-xs;
    }
  }

  &__done-date {
    font-size: $font-size-xs;
    color: $heart-pink-light;
    display: block;
    margin-top: 6rpx;
    font-weight: $font-weight-medium;
  }

  // ===== 已完成装饰 =====
  &__deco {
    position: absolute;
    right: 20rpx;
    top: 50%;
    transform: translateY(-50%);
    font-size: 64rpx;
    color: $heart-pink-pale;
    opacity: 0.15;
    pointer-events: none;
    line-height: 1;
  }
}

// ===== 光点呼吸 =====
@keyframes breathe {
  0%, 100% {
    box-shadow:
      0 0 0 6rpx rgba($mint, 0.12),
      0 0 8rpx rgba($mint, 0.2);
  }
  50% {
    box-shadow:
      0 0 0 8rpx rgba($mint, 0.18),
      0 0 16rpx rgba($mint, 0.35);
  }
}

// ===== 卡片入场 =====
@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(-16rpx) scale(0.97);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

// ===== 悬浮按钮 =====
.fab {
  position: fixed;
  right: 40rpx;
  bottom: 200rpx;
  width: 112rpx;
  height: 112rpx;
  border-radius: $radius-full;
  background: $gradient-heart;
  box-shadow:
    0 8rpx 24rpx rgba(255, 107, 138, 0.3),
    0 2rpx 8rpx rgba(255, 107, 138, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  transition: transform $duration-fast $ease-soft, box-shadow $duration-fast $ease-soft;

  &:active {
    transform: scale(0.92);
    box-shadow:
      0 4rpx 16rpx rgba(255, 107, 138, 0.25),
      0 2rpx 4rpx rgba(255, 107, 138, 0.15);
  }
}
</style>
