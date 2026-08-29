<template>
  <view class="kd-calendar">
    <!-- 月份导航 -->
    <view class="kd-calendar__header">
      <view class="kd-calendar__nav" @tap="prevMonth">
        <KdIcon name="tabler:chevron-left" :size="28" color="#999" />
      </view>
      <text class="kd-calendar__title">{{ currentYear }}年{{ currentMonth }}月</text>
      <view class="kd-calendar__nav" @tap="nextMonth">
        <KdIcon name="tabler:arrow-right" :size="28" color="#999" />
      </view>
    </view>

    <!-- 星期标题 -->
    <view class="kd-calendar__weekdays">
      <text v-for="w in weekdays" :key="w" class="kd-calendar__weekday">{{ w }}</text>
    </view>

    <!-- 日期网格 -->
    <view class="kd-calendar__grid">
      <view
        v-for="(day, index) in calendarDays"
        :key="index"
        class="kd-calendar__day"
        :class="{
          'kd-calendar__day--today': day.isToday,
          'kd-calendar__day--other': !day.isCurrentMonth,
          'kd-calendar__day--has-event': day.anniversaries.length || day.capsuleOpen || day.myMood || day.partnerMood
        }"
        @tap="onDayTap(day)"
      >
        <text class="kd-calendar__day-num">{{ day.day }}</text>
        <view class="kd-calendar__day-markers">
          <image v-if="day.myMood" class="kd-calendar__mood" :src="getTwemojiUrl(moodIconMap[day.myMood] || '😊')" mode="aspectFit" />
          <image v-if="day.partnerMood" class="kd-calendar__mood" :src="getTwemojiUrl(moodIconMap[day.partnerMood] || '😊')" mode="aspectFit" />
          <view v-for="(_, i) in day.anniversaries.slice(0, 2)" :key="i" class="kd-calendar__dot kd-calendar__dot--anniversary" />
          <view v-if="day.capsuleOpen" class="kd-calendar__dot kd-calendar__dot--capsule" />
        </view>
      </view>
    </view>

    <!-- 图例 -->
    <view class="kd-calendar__legend">
      <view class="kd-calendar__legend-item">
        <view class="kd-calendar__dot kd-calendar__dot--anniversary" />
        <text class="kd-calendar__legend-text">纪念日</text>
      </view>
      <view class="kd-calendar__legend-item">
        <view class="kd-calendar__dot kd-calendar__dot--capsule" />
        <text class="kd-calendar__legend-text">胶囊开启</text>
      </view>
      <view class="kd-calendar__legend-item">
        <image class="kd-calendar__mood kd-calendar__mood--legend" :src="getTwemojiUrl('😊')" mode="aspectFit" />
        <text class="kd-calendar__legend-text">心情</text>
      </view>
    </view>

    <!-- 当天事件摘要 -->
    <view v-if="selectedDay && (selectedDay.anniversaries.length || selectedDay.capsuleOpen || selectedDay.myMood || selectedDay.partnerMood)" class="kd-calendar__summary">
      <text class="kd-calendar__summary-date">{{ selectedDay.date }}</text>
      <view v-for="(title, i) in selectedDay.anniversaries" :key="i" class="kd-calendar__summary-item">
        <view class="kd-calendar__dot kd-calendar__dot--anniversary" />
        <text class="kd-calendar__summary-text">{{ title }}</text>
      </view>
      <view v-if="selectedDay.capsuleOpen" class="kd-calendar__summary-item">
        <view class="kd-calendar__dot kd-calendar__dot--capsule" />
        <text class="kd-calendar__summary-text">有胶囊到期可开启</text>
      </view>
      <view v-if="selectedDay.myMood" class="kd-calendar__summary-item">
        <image class="kd-calendar__mood kd-calendar__mood--summary" :src="getTwemojiUrl(moodIconMap[selectedDay.myMood] || '😊')" mode="aspectFit" />
        <text class="kd-calendar__summary-text">我的心情</text>
      </view>
      <view v-if="selectedDay.partnerMood" class="kd-calendar__summary-item">
        <image class="kd-calendar__mood kd-calendar__mood--summary" :src="getTwemojiUrl(moodIconMap[selectedDay.partnerMood] || '😊')" mode="aspectFit" />
        <text class="kd-calendar__summary-text">TA的心情</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { getTwemojiUrl } from '@/utils/emoji'
import KdIcon from '@/components/KdIcon.vue'

interface CalendarDay {
  day: number
  date: string
  isToday: boolean
  isCurrentMonth: boolean
  anniversaries: string[]
  capsuleOpen: boolean
  myMood?: string
  partnerMood?: string
}

const props = defineProps<{
  anniversaries: Array<{ date: string; title: string; repeat_type: string }>
  capsules: Array<{ open_at: string; is_opened: boolean }>
  moods: Array<{ user_id: string; mood_date: string; emoji: string }>
  currentUserId: string
}>()

const emit = defineEmits<{
  (e: 'dayTap', day: CalendarDay): void
}>()

const weekdays = ['日', '一', '二', '三', '四', '五', '六']
const moodIconMap: Record<string, string> = {
  happy: '😊', love: '😍', calm: '😌', excited: '🤩',
  sweet: '😘', tired: '😪', sad: '😢', angry: '😤',
}

const now = new Date()
const currentYear = ref(now.getFullYear())
const currentMonth = ref(now.getMonth() + 1)
const selectedDay = ref<CalendarDay | null>(null)

const todayStr = computed(() => {
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
})

const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const firstDay = new Date(year, month - 1, 1).getDay()
  const daysInMonth = new Date(year, month, 0).getDate()
  const daysInPrevMonth = new Date(year, month - 1, 0).getDate()

  const days: CalendarDay[] = []

  // 上月末尾
  for (let i = firstDay - 1; i >= 0; i--) {
    const d = daysInPrevMonth - i
    const m = month === 1 ? 12 : month - 1
    const y = month === 1 ? year - 1 : year
    days.push({
      day: d,
      date: `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
      isToday: false,
      isCurrentMonth: false,
      anniversaries: [],
      capsuleOpen: false,
    })
  }

  // 本月
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({
      day: d,
      date: dateStr,
      isToday: dateStr === todayStr.value,
      isCurrentMonth: true,
      anniversaries: getAnniversaries(dateStr),
      capsuleOpen: hasCapsuleOpen(dateStr),
      myMood: getMyMood(dateStr),
      partnerMood: getPartnerMood(dateStr),
    })
  }

  // 下月开头
  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    const m = month === 12 ? 1 : month + 1
    const y = month === 12 ? year + 1 : year
    days.push({
      day: d,
      date: `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
      isToday: false,
      isCurrentMonth: false,
      anniversaries: [],
      capsuleOpen: false,
    })
  }

  return days
})

const getAnniversaries = (dateStr: string) => {
  const [, m, d] = dateStr.split('-')
  const titles: string[] = []
  for (const a of props.anniversaries) {
    if (a.repeat_type === 'yearly') {
      const [, am, ad] = a.date.split('-')
      if (am === m && ad === d) titles.push(a.title)
    } else {
      if (a.date === dateStr) titles.push(a.title)
    }
  }
  return titles
}

const hasCapsuleOpen = (dateStr: string) => {
  return props.capsules.some(c => {
    if (c.is_opened) return false
    const capsuleDate = c.open_at.split('T')[0]
    return capsuleDate === dateStr
  })
}

const getMyMood = (dateStr: string) => {
  const mood = props.moods.find(m => m.user_id === props.currentUserId && m.mood_date === dateStr)
  return mood?.emoji
}

const getPartnerMood = (dateStr: string) => {
  const mood = props.moods.find(m => m.user_id !== props.currentUserId && m.mood_date === dateStr)
  return mood?.emoji
}

const prevMonth = () => {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  selectedDay.value = null
}

const nextMonth = () => {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  selectedDay.value = null
}

const onDayTap = (day: CalendarDay) => {
  selectedDay.value = day
  emit('dayTap', day)
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.kd-calendar {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 24rpx;
  box-shadow: $shadow-sm;
}

.kd-calendar__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}
.kd-calendar__nav {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.kd-calendar__title {
  font-size: $font-size-md;
  font-weight: $font-weight-semibold;
  color: $text-primary;
}

.kd-calendar__weekdays {
  display: flex;
  margin-bottom: 12rpx;
}
.kd-calendar__weekday {
  flex: 1;
  text-align: center;
  font-size: $font-size-xs;
  color: $text-tertiary;
}

.kd-calendar__grid {
  display: flex;
  flex-wrap: wrap;
}
.kd-calendar__day {
  width: calc(100% / 7);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8rpx 0;
  min-height: 80rpx;
}
.kd-calendar__day-num {
  font-size: $font-size-sm;
  color: $text-primary;
  width: 48rpx;
  height: 48rpx;
  line-height: 48rpx;
  text-align: center;
  border-radius: $radius-full;
}
.kd-calendar__day--today .kd-calendar__day-num {
  background: $heart-pink;
  color: #fff;
  font-weight: $font-weight-bold;
}
.kd-calendar__day--other .kd-calendar__day-num {
  color: $text-tertiary;
  opacity: 0.4;
}

.kd-calendar__day-markers {
  display: flex;
  align-items: center;
  gap: 4rpx;
  margin-top: 4rpx;
  height: 20rpx;
}

.kd-calendar__dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  &--anniversary { background: $heart-pink; }
  &--capsule { background: $lavender; }
}

.kd-calendar__mood {
  width: 20rpx;
  height: 20rpx;
  mix-blend-mode: multiply;
  &--legend { width: 16rpx; height: 16rpx; }
  &--summary { width: 24rpx; height: 24rpx; }
}

.kd-calendar__legend {
  display: flex;
  justify-content: center;
  gap: 32rpx;
  margin-top: 16rpx;
  padding-top: 16rpx;
  border-top: 2rpx solid $border-light;
}
.kd-calendar__legend-item {
  display: flex;
  align-items: center;
  gap: 6rpx;
}
.kd-calendar__legend-text {
  font-size: $font-size-xs;
  color: $text-tertiary;
}

.kd-calendar__summary {
  margin-top: 16rpx;
  padding: 16rpx;
  background: $bg-page;
  border-radius: $radius-base;
}
.kd-calendar__summary-date {
  font-size: $font-size-xs;
  color: $text-tertiary;
  display: block;
  margin-bottom: 8rpx;
}
.kd-calendar__summary-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 4rpx 0;
}
.kd-calendar__summary-text {
  font-size: $font-size-sm;
  color: $text-secondary;
}
</style>
