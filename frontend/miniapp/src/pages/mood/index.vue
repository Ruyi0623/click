<template>
  <view class="page-mood">
    <view v-if="loading" class="loading-wrap"><view class="loading-spinner animate-spin" /></view>
    <KdEmpty v-else-if="!list.length" title="还没有心情记录" desc="点击下方按钮记录今天的心情" icon="tabler:mood-happy" />
    <view v-else class="mood-list">
      <view v-for="(item, index) in list" :key="item.id" class="mood-item animate-fade-in-up" :style="{ animationDelay: `${index * 30}ms` }">
        <image class="mood-item__emoji" :src="getTwemojiUrl(moodIconMap[item.emoji] || '😊')" mode="aspectFit" />
        <view class="mood-item__info">
          <text class="mood-item__label">{{ moodLabelMap[item.emoji] || item.emoji }}</text>
          <text class="mood-item__date">{{ item.mood_date }}</text>
        </view>
        <text class="mood-item__who">{{ item.user_id === myId ? '我' : 'TA' }}</text>
      </view>
    </view>

    <view class="fab animate-pulse-glow" @tap="showPicker = true">
      <KdIcon name="tabler:plus" :size="48" color="#fff" />
    </view>

    <KdMoodPicker :visible="showPicker" @close="showPicker = false" @select="onSelect" />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { moodApi, type Mood } from '@/api/mood'
import { useAuthStore } from '@/stores/auth'
import { today } from '@/utils/date'
import { getTwemojiUrl } from '@/utils/emoji'
import KdEmpty from '@/components/KdEmpty.vue'
import KdMoodPicker from '@/components/KdMoodPicker.vue'
import KdIcon from '@/components/KdIcon.vue'

const authStore = useAuthStore()
const myId = computed(() => authStore.userInfo?.id)
const list = ref<Mood[]>([])
const loading = ref(true)
const showPicker = ref(false)

const moodIconMap: Record<string, string> = {
  happy: '😊', love: '😍', calm: '😌', excited: '🤩',
  sweet: '😘', tired: '😪', sad: '😢', angry: '😤',
}
const moodLabelMap: Record<string, string> = {
  happy: '开心', love: '想你', calm: '平静', excited: '惊喜',
  sweet: '甜蜜', tired: '困倦', sad: '难过', angry: '生气',
}

const loadList = async () => {
  try { list.value = await moodApi.list() } catch {} finally { loading.value = false }
}

const onSelect = async (moodId: string) => {
  showPicker.value = false
  try {
    await moodApi.create(moodId, today())
    uni.showToast({ title: '已记录', icon: 'success' })
    await loadList()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onMounted(loadList)
onPullDownRefresh(async () => { await loadList(); uni.stopPullDownRefresh() })
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-mood {
  min-height: 100vh;
  background: $bg-page;
  padding: $padding-page;
  padding-bottom: calc(160rpx + env(safe-area-inset-bottom));
}

.loading-wrap { display: flex; justify-content: center; padding: 120rpx 0; }
.loading-spinner { width: 48rpx; height: 48rpx; border: 4rpx solid $border-light; border-top-color: $heart-pink; border-radius: 50%; }

.mood-item {
  display: flex; align-items: center;
  background: $bg-card; border-radius: $radius-lg; padding: 24rpx; margin-bottom: $gap-list; box-shadow: $shadow-sm;
  opacity: 0;
  &__emoji { width: 56rpx; height: 56rpx; margin-right: 24rpx; mix-blend-mode: multiply; }
  &__info { flex: 1; }
  &__label { font-size: $font-size-md; color: $text-primary; font-weight: $font-weight-medium; display: block; }
  &__date { font-size: $font-size-sm; color: $text-secondary; display: block; margin-top: 4rpx; }
  &__who { font-size: $font-size-sm; color: $heart-pink; font-weight: $font-weight-medium; }
}

.fab {
  position: fixed; right: 40rpx; bottom: 200rpx;
  width: 112rpx; height: 112rpx; border-radius: $radius-full;
  background: $gradient-heart; box-shadow: $shadow-glow-lg;
  display: flex; align-items: center; justify-content: center; z-index: 100;
  &__icon { font-size: 48rpx; color: #fff; }
  &:active { transform: scale(0.9); }
}
</style>
