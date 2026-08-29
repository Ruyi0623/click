<template>
  <view class="page-collection">
    <view class="collection-header">
      <text class="collection-title">{{ collectionName }}</text>
      <view class="collection-actions">
        <view v-if="!isSelectMode" class="collection-action-btn" @tap="enterSelectMode">
          <KdIcon name="tabler:checkbox" :size="32" color="#666" />
        </view>
        <view v-if="!isSelectMode && !isUngrouped" class="collection-action-btn" @tap="editName">
          <KdIcon name="tabler:pencil" :size="32" color="#666" />
        </view>
        <view v-if="!isSelectMode && !isUngrouped" class="collection-action-btn" @tap="deleteCollection">
          <KdIcon name="tabler:trash" :size="32" color="#EF5350" />
        </view>
        <view v-if="isSelectMode" class="collection-action-btn" @tap="exitSelectMode">
          <KdIcon name="tabler:x" :size="32" color="#666" />
        </view>
      </view>
    </view>

    <view v-if="loading" class="collection-loading">
      <view class="collection-loading__spinner animate-spin" />
    </view>

    <KdEmpty v-else-if="!photos.length" :title="isUngrouped ? '没有未分组照片' : '还没有照片'" :desc="isUngrouped ? '所有照片都在合集中' : '点击右下角添加照片'" icon="tabler:photo">
      <button v-if="!isUngrouped" class="collection-empty-btn" @tap="addPhotos">添加照片</button>
    </KdEmpty>

    <view v-else class="collection-grid">
      <view
        v-for="(photo, index) in photos"
        :key="photo.id"
        class="collection-item animate-fade-in-up"
        :class="{ 'collection-item--selected': selectedIds.has(photo.id) }"
        :style="{ animationDelay: `${index * 30}ms` }"
        @tap="onPhotoTap(photo, index)"
        @longpress="onLongPress(photo)"
      >
        <image
          class="collection-item__img"
          :src="ensureHttps(photo.thumbnail_url || photo.url)"
          mode="aspectFill"
          lazy-load
        />
        <view v-if="isSelectMode" class="collection-item__check">
          <view class="collection-item__check-icon" :class="{ active: selectedIds.has(photo.id) }">
            <KdIcon v-if="selectedIds.has(photo.id)" name="tabler:check" :size="24" color="#fff" />
          </view>
        </view>
      </view>
    </view>

    <!-- 批量操作栏 -->
    <view v-if="isSelectMode" class="batch-bar">
      <view class="batch-bar__left" @tap="toggleSelectAll">
        <view class="batch-bar__check" :class="{ active: isAllSelected }">
          <KdIcon v-if="isAllSelected" name="tabler:check" :size="24" color="#fff" />
        </view>
        <text class="batch-bar__text">全选 ({{ selectedIds.size }})</text>
      </view>
      <view class="batch-bar__actions">
        <view class="batch-bar__btn" @tap="batchMove">
          <KdIcon name="tabler:folder" :size="32" color="#666" />
          <text>移动</text>
        </view>
        <view class="batch-bar__btn batch-bar__btn--danger" @tap="batchDelete">
          <KdIcon name="tabler:trash" :size="32" color="#EF5350" />
          <text>删除</text>
        </view>
      </view>
    </view>

    <!-- 底部添加照片按钮（未分组不显示，选择模式不显示） -->
    <view v-if="!isUngrouped && !isSelectMode" class="collection-fab" @tap="addPhotos">
      <KdIcon name="tabler:plus" :size="48" color="#fff" />
    </view>

    <!-- 操作菜单 -->
    <KdActionSheet
      v-model:visible="showPhotoAction"
      :actions="photoActions"
      @select="onPhotoActionSelect"
    />
    <KdActionSheet
      v-model:visible="showMoveTarget"
      title="选择目标"
      :actions="moveTargetActions"
      @select="onMoveTargetSelect"
    />

    <!-- 确认对话框 -->
    <KdDialog
      v-model:visible="showDeletePhotoConfirm"
      title="删除照片"
      content="确定要删除这张照片吗？"
      confirm-color="#EF5350"
      @confirm="onDeletePhotoConfirm"
    />
    <KdDialog
      v-model:visible="showBatchMoveConfirm"
      title="移动照片"
      :content="`将 ${selectedIds.size} 张照片移回未分组？`"
      @confirm="doBatchMove(null)"
    />
    <KdDialog
      v-model:visible="showBatchDeleteConfirm"
      title="批量删除"
      :content="`确定要删除选中的 ${selectedIds.size} 张照片吗？`"
      confirm-color="#EF5350"
      @confirm="onBatchDeleteConfirm"
    />
    <KdDialog
      v-model:visible="showEditName"
      title="修改合集名称"
      show-input
      input-placeholder="请输入合集名称"
      :input-value="editNameValue"
      @confirm="onEditNameConfirm"
    />
    <KdDialog
      v-model:visible="showDeleteCollectionConfirm"
      title="删除合集"
      content="确定要删除这个合集吗？合集内的照片也会被删除。"
      confirm-color="#EF5350"
      @confirm="onDeleteCollectionConfirm"
    />
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad, onUnload } from '@dcloudio/uni-app'
import { photoApi, type Photo } from '@/api/photo'
import { collectionApi, type Collection } from '@/api/collection'
import { upload, ensureHttps } from '@/utils/request'
import KdEmpty from '@/components/KdEmpty.vue'
import KdIcon from '@/components/KdIcon.vue'
import KdActionSheet from '@/components/KdActionSheet.vue'
import KdDialog from '@/components/KdDialog.vue'

const collectionId = ref('')
const collectionName = ref('')
const photos = ref<Photo[]>([])
const collections = ref<Collection[]>([])
const loading = ref(true)

// Action Sheet 状态
const showPhotoAction = ref(false)
const photoActionTarget = ref<Photo | null>(null)
const photoActions = computed(() => [
  { label: '移动到合集' },
  { label: '删除照片', destructive: true },
])

const showMoveTarget = ref(false)
const moveTargetPhotoId = ref('')
const isBatchMove = ref(false)
const moveTargetActions = computed(() => {
  if (isUngrouped.value && isBatchMove.value) {
    // 从未分组批量移动：只显示合集列表
    return collections.value.map(c => ({ label: c.name }))
  }
  // 单张移动或从合集批量移动：显示"未分组"+其他合集
  const other = collections.value.filter(c => c.id !== collectionId.value)
  return [{ label: '未分组' }, ...other.map(c => ({ label: c.name }))]
})

// Dialog 状态
const showDeletePhotoConfirm = ref(false)
const deletePhotoTarget = ref<Photo | null>(null)

const showBatchMoveConfirm = ref(false)
const showBatchDeleteConfirm = ref(false)

const showEditName = ref(false)
const editNameValue = ref('')

const showDeleteCollectionConfirm = ref(false)

// 选择模式
const isSelectMode = ref(false)
const selectedIds = ref(new Set<string>())

const isUngrouped = computed(() => collectionId.value === 'ungrouped')
const isAllSelected = computed(() => photos.value.length > 0 && selectedIds.value.size === photos.value.length)

const loadPhotos = async () => {
  try {
    photos.value = await photoApi.list(isUngrouped.value ? null : collectionId.value)
  } catch {} finally {
    loading.value = false
  }
}

const loadCollections = async () => {
  try {
    collections.value = await collectionApi.list()
  } catch {}
}

// 选择模式相关
const enterSelectMode = () => {
  isSelectMode.value = true
  selectedIds.value.clear()
}

const exitSelectMode = () => {
  isSelectMode.value = false
  selectedIds.value.clear()
}

const toggleSelect = (id: string) => {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value.clear()
  } else {
    photos.value.forEach(p => selectedIds.value.add(p.id))
  }
}

const onPhotoTap = (photo: Photo, index: number) => {
  if (isSelectMode.value) {
    toggleSelect(photo.id)
  } else {
    previewPhoto(index)
  }
}

// 上传照片
const addPhotos = () => {
  // 新版微信用 chooseMedia，旧版 fallback chooseImage
  const chooseFn = uni.chooseMedia || uni.chooseImage
  const options: any = uni.chooseMedia
    ? {
        count: 9,
        mediaType: ['image'],
        sourceType: ['album', 'camera'],
        sizeType: ['compressed'],
      }
    : {
        count: 9,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
      }

  chooseFn({
    ...options,
    success: async (res: any) => {
      // chooseMedia 返回 tempFiles[].tempFilePath，chooseImage 返回 tempFilePaths[]
      const paths: string[] = res.tempFiles
        ? res.tempFiles.map((f: any) => f.tempFilePath)
        : res.tempFilePaths
      if (!paths?.length) return

      uni.showLoading({ title: '上传中...' })
      try {
        for (const path of paths) {
          await upload(path, collectionId.value)
        }
        uni.showToast({ title: '上传成功', icon: 'success' })
        await loadPhotos()
      } catch (e: any) {
        uni.showToast({ title: e.message, icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
    fail: (err: any) => {
      console.error('选择照片失败:', err)
      if (err.errMsg?.includes('cancel')) return
      uni.showToast({ title: '选择照片失败', icon: 'none' })
    },
  })
}

// 预览照片
const previewPhoto = (index: number) => {
  uni.previewImage({
    current: index,
    urls: photos.value.map(p => p.url),
  })
}

// 长按操作
const onLongPress = (photo: Photo) => {
  if (isSelectMode.value) return
  if (isUngrouped.value) {
    ungroupedPhotoAction(photo)
  } else {
    collectionPhotoAction(photo)
  }
}

const ungroupedPhotoAction = (photo: Photo) => {
  photoActionTarget.value = photo
  showPhotoAction.value = true
}

const collectionPhotoAction = (photo: Photo) => {
  photoActionTarget.value = photo
  showPhotoAction.value = true
}

const onPhotoActionSelect = async (_action: any, index: number) => {
  const photo = photoActionTarget.value
  if (!photo) return
  if (index === 0) {
    // 移动到合集
    if (!collections.value.length) {
      uni.showToast({ title: '请先创建合集', icon: 'none' })
      return
    }
    moveTargetPhotoId.value = photo.id
    isBatchMove.value = false
    showMoveTarget.value = true
  } else if (index === 1) {
    // 删除照片
    deletePhotoTarget.value = photo
    showDeletePhotoConfirm.value = true
  }
}

const onBatchMoveConfirm = async () => {
  await doBatchMove(null)
}

const onMoveTargetSelect = async (_action: any, index: number) => {
  if (isBatchMove.value) {
    if (isUngrouped.value) {
      // 批量移动从未分组到合集
      const target = collections.value[index]
      await doBatchMove(target.id)
    } else {
      // 批量移动从合集到未分组/其他合集
      const other = collections.value.filter(c => c.id !== collectionId.value)
      const targetId = index === 0 ? null : other[index - 1].id
      await doBatchMove(targetId)
    }
  } else {
    // 单张移动
    const other = collections.value.filter(c => c.id !== collectionId.value)
    const targetId = index === 0 ? null : other[index - 1].id
    try {
      await photoApi.move(moveTargetPhotoId.value, targetId)
      uni.showToast({ title: '已移动', icon: 'success' })
      await loadPhotos()
    } catch (e: any) {
      uni.showToast({ title: e.message, icon: 'none' })
    }
  }
}

const onDeletePhotoConfirm = async () => {
  const photo = deletePhotoTarget.value
  if (!photo) return
  try {
    await photoApi.delete(photo.id)
    uni.showToast({ title: '已删除', icon: 'success' })
    await loadPhotos()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

// 批量操作
const batchMove = async () => {
  if (!selectedIds.value.size) {
    uni.showToast({ title: '请先选择照片', icon: 'none' })
    return
  }

  if (isUngrouped.value) {
    // 未分组：移动到某个合集
    if (!collections.value.length) {
      uni.showToast({ title: '请先创建合集', icon: 'none' })
      return
    }
    isBatchMove.value = true
    showMoveTarget.value = true
  } else {
    // 合集内：可移动到其他合集或未分组
    const otherCollections = collections.value.filter(c => c.id !== collectionId.value)
    if (!otherCollections.length) {
      // 没有其他合集，只能移回未分组
      showBatchMoveConfirm.value = true
      return
    }
    moveTargetPhotoId.value = ''
    isBatchMove.value = true
    showMoveTarget.value = true
  }
}

const doBatchMove = async (targetId: string | null) => {
  uni.showLoading({ title: '移动中...' })
  try {
    const ids = Array.from(selectedIds.value)
    for (const id of ids) {
      await photoApi.move(id, targetId)
    }
    uni.showToast({ title: `已移动 ${ids.length} 张照片`, icon: 'success' })
    exitSelectMode()
    await loadPhotos()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

const batchDelete = async () => {
  if (!selectedIds.value.size) {
    uni.showToast({ title: '请先选择照片', icon: 'none' })
    return
  }
  showBatchDeleteConfirm.value = true
}

const onBatchDeleteConfirm = async () => {
  uni.showLoading({ title: '删除中...' })
  try {
    const ids = Array.from(selectedIds.value)
    for (const id of ids) {
      await photoApi.delete(id)
    }
    uni.showToast({ title: `已删除 ${ids.length} 张照片`, icon: 'success' })
    exitSelectMode()
    await loadPhotos()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

// 编辑合集名称
const editName = () => {
  editNameValue.value = collectionName.value
  showEditName.value = true
}

const onEditNameConfirm = async (value?: string) => {
  if (!value) return
  try {
    await collectionApi.update(collectionId.value, { name: value })
    collectionName.value = value
    uni.showToast({ title: '修改成功', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

// 删除合集
const deleteCollection = () => {
  showDeleteCollectionConfirm.value = true
}

const onDeleteCollectionConfirm = async () => {
  try {
    await collectionApi.delete(collectionId.value)
    uni.showToast({ title: '已删除', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onLoad((options) => {
  if (options?.id) {
    collectionId.value = options.id
    collectionName.value = decodeURIComponent(options.name || '合集')
    loadPhotos()
    loadCollections()
  }
})
onUnload(() => {
  try { uni.hideLoading() } catch {}
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-collection {
  min-height: 100vh;
  background: $bg-page;
  padding: $padding-page;
  padding-bottom: calc(240rpx + env(safe-area-inset-bottom));
}

.collection-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32rpx;
}
.collection-title {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;
  color: $text-primary;
}
.collection-actions {
  display: flex;
  gap: 24rpx;
}
.collection-action-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: $radius-full;
  background: $bg-card;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $shadow-sm;
}

.collection-loading {
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

.collection-empty-btn {
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

.collection-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8rpx;
}
.collection-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: $radius-sm;
  overflow: hidden;
  opacity: 0;
  &--selected {
    .collection-item__img {
      opacity: 0.7;
    }
  }
  &__img {
    width: 100%;
    height: 100%;
  }
  &__check {
    position: absolute;
    top: 8rpx;
    right: 8rpx;
    z-index: 10;
  }
  &__check-icon {
    width: 40rpx;
    height: 40rpx;
    border-radius: $radius-full;
    border: 3rpx solid #fff;
    background: rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    &.active {
      background: $heart-pink;
      border-color: $heart-pink;
    }
  }
}

.batch-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: $bg-card;
  padding: 24rpx $padding-page;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.05);
  z-index: 100;
  &__left {
    display: flex;
    align-items: center;
    gap: 16rpx;
  }
  &__check {
    width: 40rpx;
    height: 40rpx;
    border-radius: $radius-full;
    border: 3rpx solid $border-normal;
    display: flex;
    align-items: center;
    justify-content: center;
    &.active {
      background: $heart-pink;
      border-color: $heart-pink;
    }
  }
  &__text {
    font-size: $font-size-base;
    color: $text-primary;
  }
  &__actions {
    display: flex;
    gap: 32rpx;
  }
  &__btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4rpx;
    font-size: $font-size-xs;
    color: $text-secondary;
    &--danger {
      color: $error;
    }
  }
}

.collection-fab {
  position: fixed;
  right: 40rpx;
  bottom: 200rpx;
  width: 112rpx;
  height: 112rpx;
  border-radius: $radius-full;
  background: $gradient-heart;
  box-shadow: $shadow-glow-lg;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  &:active { transform: scale(0.9); }
}
</style>
