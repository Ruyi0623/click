<template>
  <view class="page-footprint">
    <!-- 加载状态 -->
    <view v-if="loading" class="loading-wrap">
      <view class="loading-spinner" />
    </view>

    <!-- 空状态 -->
    <KdEmpty
      v-else-if="!list.length"
      title="还没有足迹"
      desc="标记你们一起走过的地方"
      icon="tabler:map-pin"
    />

    <view v-else>
      <!-- 统计卡片 -->
      <view class="stats animate-fade-in-down">
        <text class="stats__total">{{ list.length }}</text>
        <text class="stats__label">个地点</text>
        <view class="stats__row">
          <view class="stats__item">
            <text class="stats__num">{{ thisYearCount }}</text>
            <text class="stats__sub">今年</text>
          </view>
          <view class="stats__divider" />
          <view class="stats__item">
            <text class="stats__num">{{ thisMonthCount }}</text>
            <text class="stats__sub">本月</text>
          </view>
        </view>
      </view>

      <!-- 地图 -->
      <view v-if="markers.length" class="map-wrap animate-fade-in-up">
        <map
          class="map"
          :latitude="mapCenter.lat"
          :longitude="mapCenter.lng"
          :scale="mapScale"
          :markers="markers"
          @markertap="onMarkerTap"
        />
      </view>

      <!-- 列表标题 -->
      <view class="section-header">
        <text class="section-title">全部足迹</text>
        <text class="section-count">{{ list.length }} 个地点</text>
      </view>

      <!-- 足迹列表 -->
      <view class="fp-list">
        <view
          v-for="(item, index) in list"
          :key="item.id"
          class="fp-card animate-fade-in-up"
          :style="{ animationDelay: `${index * 50}ms` }"
          @tap="goEdit(item.id)"
          @longpress="onLongPress(item.id)"
        >
          <view class="fp-card__indicator" />
          <view class="fp-card__body">
            <text class="fp-card__name">{{ item.name }}</text>
            <view class="fp-card__meta">
              <text class="fp-card__date">{{ item.visited_at }}</text>
              <text v-if="item.note" class="fp-card__note">{{ item.note }}</text>
            </view>
          </view>
          <view class="fp-card__arrow">
            <KdIcon name="tabler:chevron-right" :size="24" color="#ccc" />
          </view>
        </view>
      </view>
    </view>

    <!-- FAB -->
    <view class="fab" @tap="goCreate">
      <KdIcon name="tabler:plus" :size="48" color="#fff" />
    </view>
  </view>

  <!-- 删除确认弹窗 -->
  <KdDialog
    :visible="showDeleteConfirm"
    title="删除足迹"
    content="删除后无法恢复，确定要删除吗？"
    confirm-text="删除"
    confirm-color="#EF5350"
    @close="showDeleteConfirm = false"
    @confirm="onDeleteConfirm"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'
import { footprintApi, type Footprint } from '@/api/footprint'
import KdEmpty from '@/components/KdEmpty.vue'
import KdIcon from '@/components/KdIcon.vue'
import KdDialog from '@/components/KdDialog.vue'

const list = ref<Footprint[]>([])
const loading = ref(true)
const showDeleteConfirm = ref(false)
const deleteTargetId = ref('')

const now = new Date()
const thisYear = now.getFullYear()
const thisMonth = now.getMonth() + 1

const thisYearCount = computed(() =>
  list.value.filter((f) => f.visited_at.startsWith(String(thisYear))).length
)
const thisMonthCount = computed(() =>
  list.value.filter((f) =>
    f.visited_at.startsWith(`${thisYear}-${String(thisMonth).padStart(2, '0')}`)
  ).length
)

// 地图中心点
const mapCenter = computed(() => {
  const valid = list.value.filter((f) => f.latitude && f.longitude)
  if (!valid.length) return { lat: 39.9, lng: 116.4 }
  const lat = valid.reduce((s, f) => s + f.latitude, 0) / valid.length
  const lng = valid.reduce((s, f) => s + f.longitude, 0) / valid.length
  return { lat, lng }
})

const mapScale = computed(() => {
  const valid = list.value.filter((f) => f.latitude && f.longitude)
  return valid.length <= 1 ? 12 : 5
})

// 地图标记点
const markers = computed(() => {
  return list.value
    .filter((f) => f.latitude && f.longitude)
    .map((f, i) => ({
      id: i,
      latitude: f.latitude,
      longitude: f.longitude,
      title: f.name,
      callout: {
        content: `${f.name}\n${f.visited_at}`,
        padding: 12,
        borderRadius: 8,
        display: 'BYCLICK',
      },
    }))
})

const onMarkerTap = () => {}

const loadList = async () => {
  try {
    list.value = await footprintApi.list()
  } catch {
  } finally {
    loading.value = false
  }
}

const goCreate = () => uni.navigateTo({ url: '/pages/footprint/create' })
const goEdit = (id: string) => uni.navigateTo({ url: `/pages/footprint/edit?id=${id}` })

const onLongPress = (id: string) => {
  uni.vibrateShort({ type: 'medium' })
  deleteTargetId.value = id
  showDeleteConfirm.value = true
}

const onDeleteConfirm = async () => {
  try {
    await footprintApi.delete(deleteTargetId.value)
    showDeleteConfirm.value = false
    await loadList()
    uni.showToast({ title: '已删除', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onMounted(loadList)
onShow(loadList)
onPullDownRefresh(async () => {
  await loadList()
  uni.stopPullDownRefresh()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-footprint {
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
  border-top-color: $coral;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

// ===== 统计卡片 =====
.stats {
  background: linear-gradient(135deg, #FFE8E0 0%, #FFDDE2 50%, #FFEAE8 100%);
  border-radius: $radius-lg;
  padding: 40rpx $space-base $space-base;
  margin-bottom: $space-base;
  box-shadow:
    0 2rpx 8rpx rgba(255, 138, 128, 0.08),
    0 8rpx 24rpx rgba(255, 138, 128, 0.05);
  opacity: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow: hidden;

  // 右上角装饰圆
  &::before {
    content: '';
    position: absolute;
    top: -40rpx;
    right: -40rpx;
    width: 160rpx;
    height: 160rpx;
    border-radius: 50%;
    background: rgba($coral, 0.1);
  }

  &__total {
    font-size: 80rpx;
    font-weight: $font-weight-bold;
    font-family: $font-family-number;
    color: $coral;
    line-height: 1;
    position: relative;
    z-index: 1;
  }

  &__label {
    font-size: $font-size-sm;
    color: $text-tertiary;
    margin-top: 4rpx;
    margin-bottom: $space-md;
    position: relative;
    z-index: 1;
  }

  &__row {
    display: flex;
    align-items: center;
    gap: $space-lg;
    width: 100%;
    justify-content: center;
    padding-top: $space-md;
    border-top: 1rpx solid rgba($coral, 0.12);
    position: relative;
    z-index: 1;
  }

  &__item {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  &__num {
    font-size: $font-size-xl;
    font-weight: $font-weight-bold;
    font-family: $font-family-number;
    color: $text-primary;
    line-height: 1;
  }

  &__sub {
    font-size: $font-size-xs;
    color: $text-tertiary;
    margin-top: 4rpx;
  }

  &__divider {
    width: 1rpx;
    height: 48rpx;
    background: $border-light;
  }
}

// ===== 地图 =====
.map-wrap {
  border-radius: $radius-lg;
  overflow: hidden;
  margin-bottom: $space-base;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    0 8rpx 24rpx rgba(255, 138, 128, 0.06);
}
.map {
  width: 100%;
  height: 400rpx;
}

// ===== 列表标题 =====
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: $space-sm;
}
.section-title {
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  color: $text-primary;
}
.section-count {
  font-size: $font-size-xs;
  color: $text-tertiary;
}

// ===== 足迹卡片 =====
.fp-list {
  display: flex;
  flex-direction: column;
  gap: $space-sm;
}

.fp-card {
  display: flex;
  align-items: center;
  background: $bg-card;
  border-radius: $radius-lg;
  padding: $space-base;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.03),
    0 4rpx 12rpx rgba(255, 138, 128, 0.03);
  opacity: 0;
  transition: transform $duration-fast ease;

  &:active {
    transform: scale(0.98);
  }

  &__indicator {
    width: 8rpx;
    height: 48rpx;
    border-radius: 4rpx;
    background: linear-gradient(180deg, $coral-light, $coral);
    flex-shrink: 0;
    margin-right: $space-md;
  }

  &__body {
    flex: 1;
    min-width: 0;
  }

  &__name {
    font-size: $font-size-md;
    font-weight: $font-weight-medium;
    color: $text-primary;
    display: block;
  }

  &__meta {
    display: flex;
    align-items: center;
    gap: $space-sm;
    margin-top: 4rpx;
  }

  &__date {
    font-size: $font-size-xs;
    color: $text-tertiary;
  }

  &__note {
    font-size: $font-size-xs;
    color: $text-tertiary;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 300rpx;

    &::before {
      content: '·';
      margin-right: $space-xs;
    }
  }

  &__arrow {
    flex-shrink: 0;
    margin-left: $space-xs;
    opacity: 0.4;
  }
}

// ===== FAB =====
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
