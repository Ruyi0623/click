<template>
  <view class="page-diary">
    <view v-if="loading" class="loading-wrap"><view class="loading-spinner animate-spin" /></view>

    <KdEmpty v-else-if="!list.length" title="翻开第一页" desc="记录属于你们的故事" icon="tabler:book-2" />

    <view v-else class="diary-feed">
      <template v-for="(item, index) in list" :key="item.id">
        <!-- 日期条 -->
        <view v-if="showDateBar(item, index)" class="date-bar animate-fade-in-up" :style="{ animationDelay: `${index * 60}ms` }">
          <view class="date-bar__line" />
          <view class="date-bar__content">
            <text class="date-bar__day">{{ getDay(item.created_at) }}</text>
            <text class="date-bar__month-year">{{ getMonthYear(item.created_at) }}</text>
          </view>
          <view class="date-bar__line" />
        </view>

        <!-- 日记卡片 -->
        <view class="diary-item animate-fade-in-up" :style="{ animationDelay: `${index * 60}ms` }">
          <!-- 胶片齿孔装饰 -->
          <view class="diary-item__film-edge">
            <view class="film-hole" />
            <view class="film-hole" />
            <view class="film-hole" />
            <view class="film-hole" />
          </view>

          <!-- 内容区 -->
          <view class="diary-item__body">
            <!-- 头像 + 昵称 + 时间 -->
            <view class="diary-item__meta">
              <image
                class="diary-item__avatar"
                :src="ensureHttps(item.author.avatar_url || '') || '/static/images/default-avatar.png'"
                mode="aspectFill"
              />
              <view class="diary-item__meta-text">
                <text class="diary-item__nickname">{{ item.author.nickname }}</text>
                <text class="diary-item__time">{{ getTime(item.created_at) }}</text>
              </view>
              <view class="diary-item__more" @tap.stop="showMoreActions(item)">
                <KdIcon name="tabler:dots" :size="28" color="#A89585" />
              </view>
            </view>

            <!-- 标题 -->
            <text v-if="item.title" class="diary-item__title">{{ item.title }}</text>

            <!-- 正文 -->
            <text class="diary-item__content">{{ item.content }}</text>

            <!-- 照片网格 -->
            <view v-if="item.photos.length" class="diary-item__photos-wrap">
              <KdPhotoGrid :photos="item.photos" />
            </view>

            <!-- 互动栏 -->
            <view class="diary-item__toolbar">
              <view class="diary-item__action" @tap.stop="toggleLike(item)">
                <KdIcon :name="item.liked_by_me ? 'tabler:heart-filled' : 'tabler:heart'" :size="28" :color="item.liked_by_me ? '#D4735F' : '#B5A598'" />
                <text class="diary-item__action-text" :class="{ 'diary-item__action-text--active': item.liked_by_me }">{{ item.like_count || '' }}</text>
              </view>
              <view class="diary-item__action" @tap.stop="openCommentInput(item)">
                <KdIcon name="tabler:message-circle" :size="28" color="#B5A598" />
                <text class="diary-item__action-text">{{ item.comments.length || '' }}</text>
              </view>
            </view>

            <!-- 点赞 + 评论区 -->
            <view v-if="item.like_count > 0 || item.comments.length" class="diary-item__interactions">
              <view v-if="item.like_count > 0" class="diary-item__likes">
                <KdIcon name="tabler:heart-filled" :size="20" color="#D4735F" />
                <text class="diary-item__likes-text">{{ likeNames(item) }}</text>
              </view>
              <view v-for="comment in item.comments" :key="comment.id" class="diary-item__comment" @longpress="deleteComment(item, comment)">
                <text class="diary-item__comment-author">{{ comment.author.nickname }}</text>
                <text class="diary-item__comment-text">{{ comment.content }}</text>
              </view>
            </view>
          </view>
        </view>
      </template>
    </view>

    <!-- 写日记 FAB -->
    <view class="fab" @tap="goCreate">
      <view class="fab__inner">
        <KdIcon name="tabler:pencil" :size="40" color="#FFFDF9" />
      </view>
    </view>

    <!-- 评论输入框 -->
    <view v-if="showComment" class="comment-bar">
      <input
        class="comment-bar__input"
        v-model="commentText"
        :placeholder="`回复 ${commentTarget?.author.nickname}...`"
        :focus="showComment"
        @confirm="submitComment"
      />
      <view class="comment-bar__btn" :class="{ 'comment-bar__btn--disabled': !commentText.trim() }" @tap="submitComment">
        <text>发送</text>
      </view>
    </view>
  </view>

  <KdDialog
    :visible="showDeleteConfirm"
    title="删除日记"
    content="这篇日记将被永久删除"
    confirm-color="#D4735F"
    @close="showDeleteConfirm = false"
    @confirm="onDeleteConfirm"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'
import { diaryApi, type Diary, type DiaryComment as DiaryCommentType } from '@/api/diary'
import { useAuthStore } from '@/stores/auth'
import { ensureHttps } from '@/utils/request'
import KdEmpty from '@/components/KdEmpty.vue'
import KdIcon from '@/components/KdIcon.vue'
import KdDialog from '@/components/KdDialog.vue'
import KdPhotoGrid from '@/components/KdPhotoGrid.vue'

const authStore = useAuthStore()
const myId = computed(() => authStore.userInfo?.id)
const list = ref<Diary[]>([])
const loading = ref(true)

const showDeleteConfirm = ref(false)
const deleteTargetId = ref('')

const showComment = ref(false)
const commentTarget = ref<Diary | null>(null)
const commentText = ref('')

// 判断是否显示日期条（第一条，或与上一条不同天）
const showDateBar = (item: Diary, index: number) => {
  if (index === 0) return true
  const prev = list.value[index - 1]
  const d1 = new Date(item.created_at)
  const d2 = new Date(prev.created_at)
  return d1.getFullYear() !== d2.getFullYear()
    || d1.getMonth() !== d2.getMonth()
    || d1.getDate() !== d2.getDate()
}

const getDay = (iso: string) => new Date(iso).getDate().toString()

const getMonthYear = (iso: string) => {
  const d = new Date(iso)
  const now = new Date()
  const month = d.getMonth() + 1
  if (d.getFullYear() === now.getFullYear()) return `${month}月`
  return `${d.getFullYear()}年${month}月`
}

const getTime = (iso: string) => {
  const d = new Date(iso)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`

  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

const likeNames = (item: Diary) => {
  const names: string[] = []
  if (item.liked_by_me) names.push('我')
  if (item.like_count > (item.liked_by_me ? 1 : 0)) names.push('TA')
  return names.join(', ') + ' 觉得很赞'
}

const loadList = async () => {
  try { list.value = await diaryApi.list() } catch {} finally { loading.value = false }
}

const goCreate = () => uni.navigateTo({ url: '/pages/diary/create' })

const toggleLike = async (item: Diary) => {
  try {
    const res = await diaryApi.like(item.id)
    item.liked_by_me = res.liked
    item.like_count = res.like_count
  } catch {}
}

const openCommentInput = (item: Diary) => {
  commentTarget.value = item
  commentText.value = ''
  showComment.value = true
}

const submitComment = async () => {
  if (!commentText.value.trim() || !commentTarget.value) return
  try {
    const comment = await diaryApi.addComment(commentTarget.value.id, commentText.value)
    commentTarget.value.comments.push(comment)
    commentText.value = ''
    showComment.value = false
  } catch (e: any) {
    uni.showToast({ title: e.message || '评论失败', icon: 'none' })
  }
}

const deleteComment = (item: Diary, comment: DiaryCommentType) => {
  if (comment.user_id !== myId.value) return
  uni.showModal({
    title: '删除评论',
    content: '确定要删除这条评论吗？',
    confirmColor: '#D4735F',
    success: async (res) => {
      if (res.confirm) {
        try {
          await diaryApi.deleteComment(item.id, comment.id)
          item.comments = item.comments.filter(c => c.id !== comment.id)
        } catch {}
      }
    },
  })
}

const showMoreActions = (item: Diary) => {
  if (item.created_by !== myId.value) return
  deleteTargetId.value = item.id
  showDeleteConfirm.value = true
}

const onDeleteConfirm = async () => {
  try {
    await diaryApi.delete(deleteTargetId.value)
    list.value = list.value.filter(d => d.id !== deleteTargetId.value)
    uni.showToast({ title: '已删除', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onShow(loadList)
onPullDownRefresh(async () => { await loadList(); uni.stopPullDownRefresh() })
</script>

<style lang="scss" scoped>
// 胶片日记专属色板
$film-brown: #C9875D;
$film-brown-light: #D4A574;
$film-coral: #D4735F;
$film-paper: #F8F3ED;
$film-card: #FFFDF9;
$film-text: #3D3028;
$film-text-secondary: #8C7B6B;
$film-text-tertiary: #B5A598;
$film-border: #E8DDD2;
$film-hole: #D9CFC3;

.page-diary {
  min-height: 100vh;
  background: $film-paper;
  padding: 24rpx 24rpx calc(200rpx + env(safe-area-inset-bottom));
  position: relative;
}

.loading-wrap { display: flex; justify-content: center; padding: 120rpx 0; }
.loading-spinner {
  width: 48rpx; height: 48rpx;
  border: 4rpx solid $film-border;
  border-top-color: $film-brown;
  border-radius: 50%;
}

// Feed
.diary-feed {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

// 日期条
.date-bar {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 16rpx 0;
  opacity: 0;

  &__line {
    flex: 1;
    height: 2rpx;
    background: linear-gradient(90deg, transparent, $film-border, transparent);
  }

  &__content {
    display: flex;
    align-items: baseline;
    gap: 8rpx;
    flex-shrink: 0;
  }

  &__day {
    font-size: 44rpx;
    font-weight: 700;
    color: $film-brown;
    font-family: 'DIN Alternate', 'Roboto', monospace;
    line-height: 1;
  }

  &__month-year {
    font-size: 22rpx;
    color: $film-text-tertiary;
    font-family: 'Noto Serif SC', 'Songti SC', serif;
    letter-spacing: 2rpx;
  }
}

.diary-item {
  display: flex;
  background: $film-card;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(61, 48, 40, 0.06);
  overflow: hidden;
  opacity: 0;

  // 胶片齿孔边条
  &__film-edge {
    width: 48rpx;
    background: linear-gradient(180deg, $film-brown-light 0%, $film-brown 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-evenly;
    padding: 24rpx 0;
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
    margin-bottom: 20rpx;
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
    min-width: 0;
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
  &__more {
    padding: 8rpx;
    margin-left: auto;
    &:active { opacity: 0.5; }
  }

  // 标题
  &__title {
    font-size: 32rpx;
    font-weight: 700;
    color: $film-text;
    display: block;
    margin-bottom: 12rpx;
    line-height: 1.4;
    font-family: 'Noto Serif SC', 'Songti SC', serif;
  }

  // 正文
  &__content {
    font-size: 28rpx;
    color: $film-text-secondary;
    line-height: 1.8;
    display: block;
    margin-bottom: 16rpx;
    word-break: break-all;
  }

  // 照片
  &__photos-wrap {
    margin-bottom: 16rpx;
    border-radius: 12rpx;
    overflow: hidden;
  }

  // 互动栏
  &__toolbar {
    display: flex;
    gap: 40rpx;
    padding-top: 16rpx;
    border-top: 2rpx solid $film-border;
  }
  &__action {
    display: flex;
    align-items: center;
    gap: 8rpx;
    padding: 8rpx 0;
    &:active { opacity: 0.5; }
  }
  &__action-text {
    font-size: 24rpx;
    color: $film-text-tertiary;
    font-family: 'DIN Alternate', monospace;
    &--active {
      color: $film-coral;
    }
  }

  // 点赞 + 评论
  &__interactions {
    margin-top: 16rpx;
    background: $film-paper;
    border-radius: 12rpx;
    padding: 16rpx 20rpx;
  }
  &__likes {
    display: flex;
    align-items: center;
    gap: 8rpx;
    padding-bottom: 12rpx;
    margin-bottom: 12rpx;
    border-bottom: 2rpx solid $film-border;
  }
  &__likes-text {
    font-size: 24rpx;
    color: $film-coral;
  }
  &__comment {
    padding: 8rpx 0;
    &:active { opacity: 0.6; }
  }
  &__comment-author {
    font-size: 24rpx;
    font-weight: 600;
    color: $film-text;
    margin-right: 8rpx;
  }
  &__comment-text {
    font-size: 24rpx;
    color: $film-text-secondary;
  }
}

// 胶片齿孔
.film-hole {
  width: 20rpx;
  height: 28rpx;
  border-radius: 6rpx;
  background: rgba(255, 253, 249, 0.4);
}

// FAB
.fab {
  position: fixed;
  right: 40rpx;
  bottom: calc(160rpx + env(safe-area-inset-bottom));
  z-index: 100;
  &__inner {
    width: 112rpx;
    height: 112rpx;
    border-radius: 50%;
    background: linear-gradient(135deg, $film-brown 0%, $film-coral 100%);
    box-shadow: 0 8rpx 32rpx rgba(201, 135, 93, 0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    &:active {
      transform: scale(0.9);
      box-shadow: 0 4rpx 16rpx rgba(201, 135, 93, 0.25);
    }
  }
}

// 评论栏
.comment-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: $film-card;
  padding: 16rpx 32rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  display: flex;
  align-items: center;
  gap: 16rpx;
  box-shadow: 0 -4rpx 20rpx rgba(61, 48, 40, 0.08);
  z-index: 200;

  &__input {
    flex: 1;
    height: 72rpx;
    background: $film-paper;
    border-radius: 36rpx;
    padding: 0 24rpx;
    font-size: 28rpx;
    color: $film-text;
  }

  &__btn {
    padding: 16rpx 32rpx;
    background: $film-brown;
    border-radius: 36rpx;
    &--disabled {
      opacity: 0.4;
      pointer-events: none;
    }
    text {
      color: #fff;
      font-size: 28rpx;
      font-weight: 600;
    }
  }
}
</style>
