<template>
  <view class="page-album">
    <view class="album-header animate-fade-in-down">
      <text class="album-title">我们的相册</text>
      <view class="album-upload-btn" @tap="createCollection">
        <KdIcon name="tabler:plus" :size="32" color="#fff" />
      </view>
    </view>

    <view v-if="loading" class="album-loading">
      <view class="album-loading__spinner animate-spin" />
    </view>

    <KdEmpty v-else-if="!collections.length && !ungroupedCount" title="还没有合集" desc="创建合集，整理你们的回忆" icon="tabler:folder">
      <button class="album-empty-btn" @tap="createCollection">创建合集</button>
    </KdEmpty>

    <view v-else class="album-collections">
      <!-- 合集列表 -->
      <view
        v-for="(col, index) in collections"
        :key="col.id"
        class="album-collection-item animate-fade-in-up"
        :style="{ animationDelay: `${index * 50}ms` }"
        @tap="goToCollection(col)"
        @longpress="editCollection(col)"
      >
        <view class="album-collection-item__cover-wrap">
          <image
            v-if="col.cover_photo_url"
            class="album-collection-item__cover"
            :src="ensureHttps(col.cover_photo_url)"
            mode="aspectFill"
          />
          <view v-else class="album-collection-item__cover album-collection-item__cover--empty">
            <KdIcon name="tabler:photo" :size="48" color="#ccc" />
          </view>
          <view class="album-collection-item__count-badge">
            <text>{{ col.photo_count }}</text>
          </view>
        </view>
        <text class="album-collection-item__name">{{ col.name }}</text>
      </view>
      <!-- 未分组入口（始终在最后） -->
      <view
        class="album-collection-item animate-fade-in-up"
        :style="{ animationDelay: `${collections.length * 50}ms` }"
        @tap="goToUngrouped"
      >
        <view class="album-collection-item__cover-wrap">
          <view class="album-collection-item__cover album-collection-item__cover--empty">
            <KdIcon name="tabler:inbox" :size="48" color="#FFB347" />
          </view>
          <view v-if="ungroupedCount > 0" class="album-collection-item__count-badge">
            <text>{{ ungroupedCount }}</text>
          </view>
        </view>
        <text class="album-collection-item__name">未分组</text>
      </view>
    </view>

    <!-- 操作菜单 -->
    <KdActionSheet
      v-model:visible="showEditAction"
      :actions="editActions"
      @select="onEditActionSelect"
    />

    <!-- 对话框 -->
    <KdDialog
      v-model:visible="showCreateDialog"
      title="新建合集"
      show-input
      input-placeholder="请输入合集名称"
      @confirm="onCreateConfirm"
    />
    <KdDialog
      v-model:visible="showRenameDialog"
      title="修改合集名称"
      show-input
      input-placeholder="请输入合集名称"
      :input-value="renameValue"
      @confirm="onRenameConfirm"
    />
    <KdDialog
      v-model:visible="showDeleteDialog"
      title="删除合集"
      content="确定要删除这个合集吗？"
      confirm-color="#EF5350"
      @confirm="onDeleteConfirm"
    />
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { collectionApi, type Collection } from '@/api/collection'
import { photoApi } from '@/api/photo'
import { upload, ensureHttps } from '@/utils/request'
import KdEmpty from '@/components/KdEmpty.vue'
import KdIcon from '@/components/KdIcon.vue'
import KdActionSheet from '@/components/KdActionSheet.vue'
import KdDialog from '@/components/KdDialog.vue'

const collections = ref<Collection[]>([])
const ungroupedCount = ref(0)
const loading = ref(true)

// 新建合集
const showCreateDialog = ref(false)

// 编辑合集
const showEditAction = ref(false)
const editTarget = ref<Collection | null>(null)
const editActions = [
  { label: '修改名称' },
  { label: '设置封面' },
  { label: '删除合集', destructive: true },
]

const showRenameDialog = ref(false)
const renameValue = ref('')

const showDeleteDialog = ref(false)

const loadCollections = async () => {
  try {
    collections.value = await collectionApi.list()
  } catch {} finally {
    loading.value = false
  }
}

const loadUngroupedCount = async () => {
  try {
    const photos = await photoApi.list(null)
    ungroupedCount.value = photos.length
  } catch {}
}

const createCollection = () => {
  showCreateDialog.value = true
}

const onCreateConfirm = async (value?: string) => {
  if (!value) return
  try {
    await collectionApi.create(value)
    uni.showToast({ title: '创建成功', icon: 'success' })
    await loadCollections()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

const goToCollection = (col: Collection) => {
  uni.navigateTo({
    url: `/pages/album/collection?id=${col.id}&name=${encodeURIComponent(col.name)}`,
  })
}

const goToUngrouped = () => {
  uni.navigateTo({
    url: '/pages/album/collection?id=ungrouped&name=未分组',
  })
}

const setCover = (col: Collection) => {
  const chooseFn = uni.chooseMedia || uni.chooseImage
  const options: any = uni.chooseMedia
    ? { count: 1, mediaType: ['image'], sourceType: ['album', 'camera'], sizeType: ['compressed'] }
    : { count: 1, sizeType: ['compressed'], sourceType: ['album', 'camera'] }

  chooseFn({
    ...options,
    success: (res: any) => {
      const filePath = res.tempFiles ? res.tempFiles[0].tempFilePath : res.tempFilePaths[0]
      uni.cropImage({
        src: filePath,
        cropScale: '1:1',
        success: async (cropRes: any) => {
          uni.showLoading({ title: '上传中...' })
          try {
            const result = await upload(cropRes.tempFilePath, col.id)
            await collectionApi.update(col.id, { cover_photo_id: result.id })
            uni.showToast({ title: '封面已更新', icon: 'success' })
            await loadCollections()
          } catch (e: any) {
            uni.showToast({ title: e.message || '上传失败', icon: 'none' })
          } finally {
            uni.hideLoading()
          }
        },
      })
    },
    fail: (err: any) => {
      if (err.errMsg?.includes('cancel')) return
      uni.showToast({ title: '选择照片失败', icon: 'none' })
    },
  })
}

const editCollection = (col: Collection) => {
  editTarget.value = col
  showEditAction.value = true
}

const onEditActionSelect = (_action: any, index: number) => {
  const col = editTarget.value
  if (!col) return
  if (index === 0) {
    renameValue.value = col.name
    showRenameDialog.value = true
  } else if (index === 1) {
    setCover(col)
  } else if (index === 2) {
    showDeleteDialog.value = true
  }
}

const onRenameConfirm = async (value?: string) => {
  const col = editTarget.value
  if (!col || !value) return
  try {
    await collectionApi.update(col.id, { name: value })
    uni.showToast({ title: '修改成功', icon: 'success' })
    await loadCollections()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

const onDeleteConfirm = async () => {
  const col = editTarget.value
  if (!col) return
  try {
    await collectionApi.delete(col.id)
    uni.showToast({ title: '已删除', icon: 'success' })
    await loadCollections()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onShow(() => {
  loadCollections()
  loadUngroupedCount()
})
onPullDownRefresh(async () => {
  await loadCollections()
  await loadUngroupedCount()
  uni.stopPullDownRefresh()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-album {
  min-height: 100vh;
  background: $bg-page;
  padding: $padding-page;
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}

.album-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32rpx;
  opacity: 0;
}
.album-title {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;
  color: $text-primary;
}
.album-upload-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: $radius-full;
  background: $gradient-heart;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $shadow-glow;
  transition: transform 0.2s ease;
  &:active { transform: scale(0.9); }
}

.album-loading {
  display: flex;
  justify-content: center;
  padding: 120rpx 0;
  &__spinner {
    width: 48rpx;
    height: 48rpx;
    border: 4rpx solid $border-light;
    border-top-color: $heart-pink;
    border-radius: 50%;
  }
}

.album-empty-btn {
  margin-top: 32rpx;
  background: $gradient-heart;
  color: #fff;
  border: none;
  border-radius: $radius-full;
  height: 80rpx;
  padding: 0 48rpx;
  font-size: $font-size-base;
  display: flex;
  align-items: center;
  justify-content: center;
  &::after { display: none; }
}

.album-collections {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24rpx;
}

.album-collection-item {
  opacity: 0;
  transition: transform 0.2s ease;
  &:active { transform: scale(0.96); }
  &__cover-wrap {
    position: relative;
    border-radius: $radius-xl;
    overflow: hidden;
    aspect-ratio: 1;
    margin-bottom: 12rpx;
  }
  &__cover {
    width: 100%;
    height: 100%;
    &--empty {
      background: $bg-card;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
  &__count-badge {
    position: absolute;
    bottom: 12rpx;
    right: 12rpx;
    background: rgba(0, 0, 0, 0.5);
    color: #fff;
    font-size: $font-size-xs;
    padding: 4rpx 12rpx;
    border-radius: $radius-full;
  }
  &__name {
    font-size: $font-size-base;
    color: $text-primary;
    font-weight: $font-weight-medium;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: block;
    padding: 0 4rpx;
  }
}
</style>
