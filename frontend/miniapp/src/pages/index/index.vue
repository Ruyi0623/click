<template>
  <view class="page-home">
    <!-- 背景装饰 -->
    <view class="home-bg">
      <view class="home-bg__circle home-bg__circle--1" />
      <view class="home-bg__circle home-bg__circle--2" />
    </view>

    <!-- 顶部导航 -->
    <view class="home-nav animate-fade-in-down">
      <view class="home-nav__badge">
        <text class="home-nav__badge-icon animate-heartbeat">♡</text>
        <text class="home-nav__title">咔哒</text>
      </view>
    </view>

    <!-- 恋爱天数卡片 -->
    <view class="home-days-card animate-reveal-days">
      <KdCoupleHeader
        :my-avatar="ensureHttps(authStore.userInfo?.avatar_url || '')"
        :partner-avatar="ensureHttps(coupleStore.partner?.avatar || '')"
        :days="coupleStore.daysTogether"
        :start-date="coupleStore.coupleInfo?.start_date ? formatDate(coupleStore.coupleInfo.start_date) : ''"
      />

      <view class="home-mood-row animate-soft-slide" :style="{ animationDelay: '300ms' }">
        <view class="home-mood-item" @tap="showMoodPicker = true">
          <image
            v-if="hasMyMood && myMoodIcon"
            class="home-mood-emoji"
            :class="{ 'animate-bounce-wobble': hasMyMood }"
            :src="getTwemojiUrl(myMoodIcon)"
            mode="aspectFit"
          />
          <view v-else class="home-mood-emoji home-mood-emoji--empty">
            <text class="home-mood-emoji-plus">+</text>
          </view>
          <text class="home-mood-label">我</text>
        </view>
        <view class="home-mood-divider" />
        <view class="home-mood-item">
          <image
            v-if="hasPartnerMood && partnerMoodIcon"
            class="home-mood-emoji animate-bounce-wobble"
            :src="getTwemojiUrl(partnerMoodIcon)"
            mode="aspectFit"
          />
          <view v-else class="home-mood-emoji home-mood-emoji--empty">
            <text class="home-mood-emoji-plus">+</text>
          </view>
          <text class="home-mood-label">TA</text>
        </view>
      </view>
    </view>

    <!-- 功能区 -->
    <view class="home-features">
      <!-- 大卡片行 -->
      <view class="home-features__row home-features__row--large">
        <view
          v-for="item in features.filter(f => f.size === 'large')"
          :key="item.id"
          class="feature-card feature-card--large animate-card-slide"
          @tap="navigateTo(item.path)"
        >
          <view class="feature-card__icon" :style="{ background: item.gradient }">
            <KdIcon :name="item.iconName" :size="56" variant="white" />
          </view>
          <text class="feature-card__name">{{ item.name }}</text>
        </view>
      </view>

      <!-- 中卡片行 -->
      <view class="home-features__row home-features__row--medium">
        <view
          v-for="item in features.filter(f => f.size === 'medium')"
          :key="item.id"
          class="feature-card feature-card--medium animate-fade-in-up"
          @tap="navigateTo(item.path)"
        >
          <view class="feature-card__icon" :style="{ background: item.gradient }">
            <KdIcon :name="item.iconName" :size="44" variant="white" />
          </view>
          <text class="feature-card__name">{{ item.name }}</text>
        </view>
      </view>

      <!-- 小卡片行 -->
      <view class="home-features__row home-features__row--small">
        <view
          v-for="item in features.filter(f => f.size === 'small')"
          :key="item.id"
          class="feature-card feature-card--small animate-fade-in-up"
          @tap="navigateTo(item.path)"
        >
          <view class="feature-card__icon" :style="{ background: item.gradient }">
            <KdIcon :name="item.iconName" :size="36" variant="white" />
          </view>
          <text class="feature-card__name">{{ item.name }}</text>
        </view>
      </view>
    </view>

    <!-- 日历卡片 -->
    <view class="home-calendar animate-fade-in-up" v-if="coupleStore.hasCouple">
      <KdCalendar
        :anniversaries="anniversaries"
        :capsules="capsules"
        :moods="moods"
        :current-user-id="authStore.userInfo?.id || ''"
      />
    </view>

    <!-- 即将到来 -->
    <view class="home-section animate-card-slide" v-if="upcoming.length">
      <view class="home-section__header">
        <text class="home-section__title">即将到来</text>
        <text class="home-section__more" @tap="navigateTo('/pages/anniversary/index')">查看全部</text>
      </view>
      <view class="home-upcoming">
        <KdCountdown
          v-for="(item, index) in upcoming"
          :key="item.id"
          :icon="item.icon"
          :title="item.title"
          :date="item.date"
          :days="item.days"
          :style="{ animationDelay: `${index * 80}ms` }"
          @tap="navigateTo('/pages/anniversary/index')"
        />
      </view>
    </view>

    <!-- 心情选择器 -->
    <KdMoodPicker
      :visible="showMoodPicker"
      @close="showMoodPicker = false"
      @select="onMoodSelect"
    />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useCoupleStore } from '@/stores/couple'
import { moodApi, type Mood } from '@/api/mood'
import { anniversaryApi, type Anniversary } from '@/api/anniversary'
import { capsuleApi, type Capsule } from '@/api/capsule'
import { formatDate, today } from '@/utils/date'
import { ensureHttps } from '@/utils/request'
import { getTwemojiUrl } from '@/utils/emoji'
import KdCoupleHeader from '@/components/KdCoupleHeader.vue'
import KdCountdown from '@/components/KdCountdown.vue'
import KdMoodPicker from '@/components/KdMoodPicker.vue'
import KdCalendar from '@/components/KdCalendar.vue'
import KdIcon from '@/components/KdIcon.vue'

const authStore = useAuthStore()
const coupleStore = useCoupleStore()
const showMoodPicker = ref(false)
const moods = ref<Mood[]>([])
const anniversaries = ref<Anniversary[]>([])
const capsules = ref<Capsule[]>([])

const moodIconMap: Record<string, string> = {
  happy: '😊', love: '😍', calm: '😌', excited: '🤩',
  sweet: '😘', tired: '😪', sad: '😢', angry: '😤',
}

const myMood = computed(() => moods.value.find(m => m.user_id === authStore.userInfo?.id && m.mood_date === today()))
const partnerMood = computed(() => moods.value.find(m => m.user_id !== authStore.userInfo?.id && m.mood_date === today()))
const myMoodIcon = computed(() => myMood.value ? moodIconMap[myMood.value.emoji] || '😊' : null)
const partnerMoodIcon = computed(() => partnerMood.value ? moodIconMap[partnerMood.value.emoji] || '😊' : null)
const hasMyMood = computed(() => !!myMood.value)
const hasPartnerMood = computed(() => !!partnerMood.value)

const upcoming = computed(() => {
  return anniversaries.value
    .filter(a => a.days_until !== null && a.days_until > 0)
    .slice(0, 2)
    .map(a => ({
      id: a.id,
      icon: 'tabler:calendar-heart',
      title: a.title,
      date: formatDate(a.date),
      days: a.days_until!,
    }))
})

const features = [
  // 大卡片 - 最常用
  { id: 'anniversary', iconName: 'tabler:calendar-heart', name: '纪念日', path: '/pages/anniversary/index', gradient: 'linear-gradient(135deg, #FFD6DE, #FF8FA3)', size: 'large' },
  { id: 'diary', iconName: 'tabler:book-2', name: '日记', path: '/pages/diary/index', gradient: 'linear-gradient(135deg, #E8DEF8, #B39DDB)', size: 'large' },
  // 中卡片 - 常用
  { id: 'wish', iconName: 'tabler:sparkles', name: '愿望', path: '/pages/wish/index', gradient: 'linear-gradient(135deg, #B2DFDB, #80CBC4)', size: 'medium' },
  { id: 'capsule', iconName: 'tabler:mail', name: '邮局', path: '/pages/capsule/index', gradient: 'linear-gradient(135deg, #D1C4E9, #B39DDB)', size: 'medium' },
  { id: 'footprint', iconName: 'tabler:map-pin', name: '足迹', path: '/pages/footprint/index', gradient: 'linear-gradient(135deg, #FFCCBC, #FF8A80)', size: 'medium' },
  // 小卡片 - 次要
  { id: 'magazine', iconName: 'tabler:book-2', name: '月刊', path: '/pages/magazine/index', gradient: 'linear-gradient(135deg, #FFF3E0, #FFB347)', size: 'small' },
  { id: 'fund', iconName: 'tabler:passbook', name: '存折', path: '/pages/fund/index', gradient: 'linear-gradient(135deg, #FFE0B2, #FFB74D)', size: 'small' },
  { id: 'transaction', iconName: 'tabler:receipt', name: '账单', path: '/pages/transaction/index', gradient: 'linear-gradient(135deg, #C8E6C9, #66BB6A)', size: 'small' },
  { id: 'penalty', iconName: 'tabler:ticket', name: '罚单', path: '/pages/penalty/index', gradient: 'linear-gradient(135deg, #FFCDD2, #EF5350)', size: 'small' },
]

const tabPages = ['/pages/index/index', '/pages/album/index', '/pages/mine/index']
const navigateTo = (url: string) => {
  if (tabPages.some(p => url.startsWith(p))) {
    uni.switchTab({ url: url.split('?')[0] })
  } else {
    uni.navigateTo({ url })
  }
}

const loadData = async () => {
  // 登录和配对检查已在 App.vue 处理，这里只加载数据
  try {
    const coupleInfo = await coupleStore.fetchCoupleInfo()
    // 未配对则不加载共享数据（避免 400 错误）
    if (!coupleInfo) return
    const [moodList, anniversaryList, capsuleList] = await Promise.all([
      moodApi.list(),
      anniversaryApi.list(),
      capsuleApi.list(),
    ])
    moods.value = moodList
    anniversaries.value = anniversaryList
    capsules.value = capsuleList
  } catch {}
}

const onMoodSelect = async (moodId: string) => {
  showMoodPicker.value = false
  try {
    await moodApi.create(moodId, today())
    uni.showToast({ title: '已记录', icon: 'success' })
    const moodList = await moodApi.list()
    moods.value = moodList
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onMounted(loadData)

onPullDownRefresh(async () => {
  await loadData()
  uni.stopPullDownRefresh()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-home {
  min-height: 100vh;
  background: $bg-page;
  padding: 0 $padding-page;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));
  position: relative;
  overflow: hidden;
}

.home-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 600rpx;
  background: $gradient-dawn;
  border-radius: 0 0 96rpx 96rpx;
  z-index: 0;
  &__circle {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
    &--1 {
      width: 300rpx;
      height: 300rpx;
      background: $heart-pink;
      top: -50rpx;
      right: -50rpx;
      animation: float 6s ease-in-out infinite;
    }
    &--2 {
      width: 200rpx;
      height: 200rpx;
      background: $lavender;
      top: 100rpx;
      left: -30rpx;
      animation: float 8s ease-in-out infinite reverse;
    }
  }
}

.home-nav {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 80rpx 0 24rpx;
  &__badge {
    display: inline-flex;
    align-items: center;
    gap: 8rpx;
    background: linear-gradient(135deg, #FF6B8A, #FF8FA3);
    padding: 12rpx 32rpx;
    border-radius: 40rpx;
    box-shadow: 0 4rpx 16rpx rgba(255, 107, 138, 0.3);
  }
  &__badge-icon {
    font-size: 28rpx;
    color: #fff;
  }
  &__title {
    font-size: $font-size-lg;
    font-weight: $font-weight-bold;
    color: #fff;
    letter-spacing: 4rpx;
  }
}

.home-days-card {
  position: relative;
  z-index: 1;
  background: $bg-card;
  border-radius: $radius-xl;
  padding: 48rpx $padding-card;
  margin-bottom: 32rpx;
  box-shadow:
    0 8rpx 32rpx rgba(255, 107, 138, 0.12),
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.8);
}

.home-mood-row {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 40rpx;
  padding-top: 32rpx;
  border-top: 2rpx solid $border-light;
}
.home-mood-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 48rpx;
}
.home-mood-emoji {
  width: 56rpx;
  height: 56rpx;
  margin-bottom: 12rpx;
  mix-blend-mode: multiply;
  &--empty {
    display: flex;
    align-items: center;
    justify-content: center;
    background: $bg-page;
    border: 2rpx dashed $border-light;
    border-radius: 50%;
    mix-blend-mode: normal;
  }
  &-plus {
    font-size: 32rpx;
    color: $text-tertiary;
    line-height: 1;
  }
}
.home-mood-label { font-size: $font-size-sm; color: $text-secondary; }
.home-mood-divider {
  width: 2rpx;
  height: 80rpx;
  background: $border-light;
}

// ========== 功能区 ==========
.home-features {
  position: relative;
  z-index: 1;
  margin-bottom: 32rpx;

  &__row {
    display: flex;
    gap: 16rpx;
    margin-bottom: 16rpx;

    &--large {
      .feature-card {
        flex: 1;
      }
    }

    &--medium {
      .feature-card {
        flex: 1;
      }
    }

    &--small {
      .feature-card {
        flex: 1;
      }
    }
  }
}

.feature-card {
  background: $bg-card;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    0 4rpx 16rpx rgba(255, 107, 138, 0.06),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.8);
  opacity: 0;
  transition: transform 0.2s ease;

  &:active {
    transform: scale(0.95);
  }

  // 大卡片
  &--large {
    padding: 32rpx 24rpx;

    .feature-card__icon {
      width: 96rpx;
      height: 96rpx;
      border-radius: 24rpx;
      margin-bottom: 16rpx;
    }

    .feature-card__name {
      font-size: 28rpx;
      font-weight: 600;
    }
  }

  // 中卡片
  &--medium {
    padding: 24rpx 16rpx;

    .feature-card__icon {
      width: 72rpx;
      height: 72rpx;
      border-radius: 20rpx;
      margin-bottom: 12rpx;
    }

    .feature-card__name {
      font-size: 24rpx;
      font-weight: 500;
    }
  }

  // 小卡片
  &--small {
    padding: 20rpx 12rpx;

    .feature-card__icon {
      width: 56rpx;
      height: 56rpx;
      border-radius: 16rpx;
      margin-bottom: 10rpx;
    }

    .feature-card__name {
      font-size: 22rpx;
      font-weight: 500;
    }
  }

  &__icon {
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: $shadow-sm;
  }

  &__name {
    color: $text-primary;
    text-align: center;
  }
}

.home-section {
  position: relative;
  z-index: 1;
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;
  }
  &__title {
    font-size: $font-size-lg;
    font-weight: $font-weight-semibold;
    color: $text-primary;
  }
  &__more {
    font-size: $font-size-sm;
    color: $text-secondary;
  }
}

.home-upcoming {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 16rpx;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    0 4rpx 16rpx rgba(255, 107, 138, 0.06),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.8);
}

.home-calendar {
  position: relative;
  z-index: 1;
  margin-bottom: 32rpx;
  opacity: 0;
}
</style>
