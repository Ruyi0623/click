<template>
  <view class="page-create">
    <!-- 发布按钮（固定右上角，原生标题栏下方） -->
    <view class="create-publish-wrap">
      <view
        class="create-publish"
        :class="{ 'create-publish--disabled': !content.trim() || loading }"
        @tap="submit"
      >
        <text>{{ isEdit ? '保存' : '发布' }}</text>
      </view>
    </view>

    <!-- 日记卡片（与列表页卡片风格一致） -->
    <view class="create-card">
      <!-- 胶片齿孔边条 -->
      <view class="create-card__film-edge">
        <view class="film-hole" />
        <view class="film-hole" />
        <view class="film-hole" />
      </view>

      <!-- 内容区 -->
      <view class="create-card__body">
        <!-- 头像 + 日期行 -->
        <view class="create-card__meta">
          <image
            class="create-card__avatar"
            :src="ensureHttps(myAvatar || '') || '/static/images/default-avatar.png'"
            mode="aspectFill"
          />
          <view class="create-card__meta-text">
            <text class="create-card__nickname">{{ myNickname }}</text>
            <text class="create-card__time">{{ currentWeekday }} {{ currentMonthDay }}</text>
          </view>
        </view>

        <!-- 标题 -->
        <input
          class="create-card__title"
          v-model="title"
          placeholder="给今天起个名字..."
          placeholder-class="create-card__title--placeholder"
          maxlength="50"
        />

        <!-- 正文 -->
        <textarea
          class="create-card__content"
          v-model="content"
          :placeholder="placeholderText"
          placeholder-class="create-card__content--placeholder"
          maxlength="2000"
          :auto-height="false"
        />

        <!-- 照片网格预览 -->
        <view v-if="selectedPhotos.length" class="create-card__photos">
          <view v-for="(photo, index) in selectedPhotos" :key="photo.id" class="create-card__photo-item">
            <image class="create-card__photo-img" :src="ensureHttps(photo.thumbnail_url || photo.url)" mode="aspectFill" />
            <view class="create-card__photo-delete" @tap="removePhoto(index)">
              <KdIcon name="tabler:x" :size="18" color="#fff" />
            </view>
          </view>
          <view v-if="selectedPhotos.length < 9" class="create-card__photo-add" @tap="addPhotos">
            <KdIcon name="tabler:plus" :size="32" color="#B5A598" />
          </view>
        </view>

        <!-- 无照片时的添加入口 -->
        <view v-else class="create-card__add-photos" @tap="addPhotos">
          <KdIcon name="tabler:photo-plus" :size="32" color="#B5A598" />
          <text class="create-card__add-photos-text">添加照片</text>
        </view>

        <!-- 底部信息 -->
        <view class="create-card__footer">
          <text class="create-card__count">{{ content.length }} / 2000</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { diaryApi, type DiaryPhoto } from '@/api/diary'
import { useAuthStore } from '@/stores/auth'
import { upload, ensureHttps } from '@/utils/request'
import KdIcon from '@/components/KdIcon.vue'

const authStore = useAuthStore()
const myAvatar = computed(() => authStore.userInfo?.avatar_url || '')
const myNickname = computed(() => authStore.userInfo?.nickname || '我')

const isEdit = ref(false)
const editId = ref('')
const title = ref('')
const content = ref('')
const loading = ref(false)
const selectedPhotos = ref<DiaryPhoto[]>([])
const placeholderText = '今天发生了什么值得记住的事呢？\n\n写下你们的故事、心情、或者想对 TA 说的话...'

const now = new Date()
const currentWeekday = computed(() => {
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return days[now.getDay()]
})
const currentMonthDay = computed(() => `${now.getMonth() + 1}月${now.getDate()}日`)

onLoad(async (query: any) => {
  if (query?.id) {
    isEdit.value = true
    editId.value = query.id
    try {
      const list = await diaryApi.list()
      const diary = list.find(d => d.id === query.id)
      if (diary) {
        title.value = diary.title || ''
        content.value = diary.content
        selectedPhotos.value = diary.photos || []
      }
    } catch {}
  }
})

const addPhotos = () => {
  const remaining = 9 - selectedPhotos.value.length
  if (remaining <= 0) {
    uni.showToast({ title: '最多添加9张照片', icon: 'none' })
    return
  }

  const chooseFn = uni.chooseMedia || uni.chooseImage
  const options: any = uni.chooseMedia
    ? { count: remaining, mediaType: ['image'], sourceType: ['album', 'camera'], sizeType: ['compressed'] }
    : { count: remaining, sizeType: ['compressed'], sourceType: ['album', 'camera'] }

  chooseFn({
    ...options,
    success: async (res: any) => {
      const paths: string[] = res.tempFiles
        ? res.tempFiles.map((f: any) => f.tempFilePath)
        : res.tempFilePaths
      if (!paths?.length) return

      uni.showLoading({ title: '上传中...' })
      try {
        for (const path of paths) {
          const photo = await upload<DiaryPhoto>(path)
          selectedPhotos.value.push(photo)
        }
      } catch (e: any) {
        uni.showToast({ title: e.message || '上传失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
    fail: (err: any) => {
      if (err.errMsg?.includes('cancel')) return
      uni.showToast({ title: '选择照片失败', icon: 'none' })
    },
  })
}

const removePhoto = (index: number) => {
  selectedPhotos.value.splice(index, 1)
}

const submit = async () => {
  if (!content.value.trim()) return
  loading.value = true
  try {
    const photoIds = selectedPhotos.value.map(p => p.id)
    if (isEdit.value) {
      await diaryApi.update(editId.value, { title: title.value || undefined, content: content.value, photo_ids: photoIds })
      uni.showToast({ title: '已保存', icon: 'success' })
    } else {
      await diaryApi.create({ title: title.value || undefined, content: content.value, photo_ids: photoIds })
      uni.showToast({ title: '已发布', icon: 'success' })
    }
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally { loading.value = false }
}
</script>

<style lang="scss" scoped>
// 与列表页一致的胶片色板
$film-brown: #C9875D;
$film-brown-light: #D4A574;
$film-coral: #D4735F;
$film-paper: #F8F3ED;
$film-card: #FFFDF9;
$film-text: #3D3028;
$film-text-secondary: #8C7B6B;
$film-text-tertiary: #B5A598;
$film-border: #E8DDD2;

.page-create {
  min-height: 100vh;
  background: $film-paper;
  padding: 24rpx 24rpx calc(48rpx + env(safe-area-inset-bottom));
}

// ── 发布按钮 ──
.create-publish-wrap {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20rpx;
}

.create-publish {
  padding: 10rpx 28rpx;
  background: linear-gradient(135deg, $film-brown 0%, $film-coral 100%);
  border-radius: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(201, 135, 93, 0.25);
  transition: all 0.2s ease;
  &:active { transform: scale(0.94); }
  &--disabled {
    opacity: 0.3;
    pointer-events: none;
    box-shadow: none;
  }
  text {
    font-size: 25rpx;
    font-weight: 600;
    color: #fff;
    letter-spacing: 1rpx;
  }
}

// ── 日记卡片（与列表页 diary-item 风格一致） ──
.create-card {
  display: flex;
  background: $film-card;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(61, 48, 40, 0.06);
  overflow: hidden;

  // 胶片齿孔边条
  &__film-edge {
    width: 48rpx;
    background: linear-gradient(180deg, $film-brown-light 0%, $film-brown 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-evenly;
    padding: 32rpx 0;
    flex-shrink: 0;
  }

  &__body {
    flex: 1;
    min-width: 0;
    padding: 28rpx 28rpx 20rpx;
  }

  // 头像行
  &__meta {
    display: flex;
    align-items: center;
    margin-bottom: 24rpx;
  }
  &__avatar {
    width: 68rpx;
    height: 68rpx;
    border-radius: 50%;
    margin-right: 16rpx;
    border: 3rpx solid $film-border;
  }
  &__meta-text {
    flex: 1;
  }
  &__nickname {
    font-size: 28rpx;
    font-weight: 600;
    color: $film-text;
    display: block;
    line-height: 1.3;
  }
  &__time {
    font-size: 22rpx;
    color: $film-text-tertiary;
    display: block;
    margin-top: 4rpx;
    font-family: 'DIN Alternate', 'Roboto', monospace;
  }

  // 标题
  &__title {
    font-size: 34rpx;
    font-weight: 700;
    color: $film-text;
    border: none;
    background: transparent;
    width: 100%;
    padding: 8rpx 0 16rpx;
    font-family: 'Noto Serif SC', 'Songti SC', serif;
    letter-spacing: 2rpx;
    &--placeholder {
      color: $film-text-tertiary;
      font-weight: 400;
      font-family: system-ui, sans-serif;
      letter-spacing: 0;
    }
  }

  // 正文
  &__content {
    min-height: 200rpx;
    font-size: 28rpx;
    color: $film-text-secondary;
    border: none;
    background: transparent;
    width: 100%;
    line-height: 1.8;
    padding: 0;
    &--placeholder {
      color: $film-text-tertiary;
    }
  }

  // 照片网格
  &__photos {
    display: flex;
    flex-wrap: wrap;
    gap: 12rpx;
    margin-top: 20rpx;
  }
  &__photo-item {
    position: relative;
    width: 160rpx;
    height: 160rpx;
    border-radius: 12rpx;
    overflow: hidden;
  }
  &__photo-img {
    width: 100%;
    height: 100%;
  }
  &__photo-delete {
    position: absolute;
    top: 4rpx;
    right: 4rpx;
    width: 32rpx;
    height: 32rpx;
    background: rgba(61, 48, 40, 0.55);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  &__photo-add {
    width: 160rpx;
    height: 160rpx;
    border: 2rpx dashed $film-border;
    border-radius: 12rpx;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  // 无照片添加入口
  &__add-photos {
    margin-top: 20rpx;
    padding: 28rpx;
    border: 2rpx dashed $film-border;
    border-radius: 12rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
    background: $film-paper;
  }
  &__add-photos-text {
    font-size: 24rpx;
    color: $film-text-tertiary;
  }

  // 底部
  &__footer {
    display: flex;
    justify-content: flex-end;
    margin-top: 20rpx;
    padding-top: 16rpx;
    border-top: 2rpx solid $film-border;
  }
  &__count {
    font-size: 22rpx;
    color: $film-text-tertiary;
    font-family: 'DIN Alternate', monospace;
  }
}

// 胶片齿孔
.film-hole {
  width: 20rpx;
  height: 28rpx;
  border-radius: 6rpx;
  background: rgba(255, 253, 249, 0.4);
}
</style>
