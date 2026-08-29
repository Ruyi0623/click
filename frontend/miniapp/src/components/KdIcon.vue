<template>
  <view class="kd-icon" :style="iconStyle">
    <image
      v-if="localSrc"
      :src="localSrc"
      :style="{ width: size + 'rpx', height: size + 'rpx' }"
      mode="aspectFit"
    />
    <text v-else class="kd-icon-text" :style="{ fontSize: size + 'rpx', color }">{{ fallback }}</text>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  name: string
  size?: number
  color?: string
  /** dark=深色描边（默认），white=白色描边（用于彩色背景），pink=粉色描边（品牌色），capsule=胶囊主题（深色背景） */
  variant?: 'dark' | 'white' | 'pink' | 'capsule'
}>(), {
  size: 40,
  color: '',
  variant: 'dark',
})

// 图标名称 → SVG 本地路径映射
const iconMap: Record<string, string> = {
  // 功能图标
  'tabler:calendar-heart': '/static/icons/calendar-heart.svg',
  'tabler:photo': '/static/icons/photo.svg',
  'tabler:sparkles': '/static/icons/sparkles.svg',
  'tabler:hourglass': '/static/icons/hourglass.svg',
  'tabler:map-pin': '/static/icons/map-pin.svg',
  'tabler:book-2': '/static/icons/book-2.svg',
  'tabler:piggy-bank': '/static/icons/piggy-bank.svg',
  'tabler:receipt': '/static/icons/receipt.svg',
  'tabler:ticket': '/static/icons/ticket.svg',
  // 心情图标
  'tabler:mood-smile': '/static/icons/mood-happy.svg',
  'tabler:mood-happy': '/static/icons/mood-happy.svg',
  'tabler:mood-heart-eyes': '/static/icons/mood-love.svg',
  'tabler:mood-neutral': '/static/icons/mood-calm.svg',
  'tabler:mood-crazy-happy': '/static/icons/mood-excited.svg',
  'tabler:mood-wink-2': '/static/icons/mood-sweet.svg',
  'tabler:mood-sad': '/static/icons/mood-sad.svg',
  'tabler:mood-angry': '/static/icons/mood-angry.svg',
  // 通用操作
  'tabler:settings': '/static/icons/settings.svg',
  'tabler:plus': '/static/icons/plus.svg',
  'tabler:trash': '/static/icons/trash.svg',
  'tabler:pencil': '/static/icons/pencil.svg',
  'tabler:home': '/static/icons/home.svg',
  'tabler:home-filled': '/static/icons/home.svg',
  'tabler:user': '/static/icons/user.svg',
  'tabler:user-filled': '/static/icons/user.svg',
  'tabler:heart': '/static/icons/heart.svg',
  'tabler:search': '/static/icons/search.svg',
  'tabler:x': '/static/icons/x.svg',
  'tabler:check': '/static/icons/check.svg',
  'tabler:checkbox': '/static/icons/checkbox.svg',
  'tabler:inbox': '/static/icons/inbox.svg',
  'tabler:folder': '/static/icons/folder.svg',
  'tabler:folder-move': '/static/icons/folder-move.svg',
  'tabler:arrow-right': '/static/icons/arrow-right.svg',
  'tabler:clock': '/static/icons/clock.svg',
  'tabler:bell': '/static/icons/bell.svg',
  'tabler:star': '/static/icons/star.svg',
  'tabler:chevron-left': '/static/icons/chevron-left.svg',
  'tabler:dots': '/static/icons/dots.svg',
  // 业务图标
  'tabler:mail': '/static/icons/mail.svg',
  'tabler:lock': '/static/icons/lock.svg',
  'tabler:unlock': '/static/icons/unlock.svg',
  'tabler:logout': '/static/icons/logout.svg',
  'tabler:couple': '/static/icons/couple.svg',
  'tabler:cake': '/static/icons/cake.svg',
  'tabler:camera': '/static/icons/camera.svg',
  'tabler:mail-open': '/static/icons/mail-open.svg',
  'tabler:target': '/static/icons/target.svg',
  // 纪念日图标
  'tabler:calendar-star': '/static/icons/calendar-star.svg',
  'tabler:timeline': '/static/icons/timeline.svg',
  'tabler:countdown': '/static/icons/countdown.svg',
  'tabler:forward': '/static/icons/forward.svg',
  'tabler:backward': '/static/icons/backward.svg',
  'tabler:gift': '/static/icons/gift.svg',
  'tabler:ring': '/static/icons/ring.svg',
  // 愿望图标
  'tabler:plant-2': '/static/icons/plant-2.svg',
  // 胶囊图标
  'tabler:mail-opened': '/static/icons/mail-opened.svg',
  'tabler:lock-open': '/static/icons/lock-open.svg',
  'tabler:send': '/static/icons/send.svg',
  // 基金图标
  'tabler:coin': '/static/icons/coin.svg',
  'tabler:history': '/static/icons/history.svg',
  'tabler:arrows-up-down': '/static/icons/arrows-up-down.svg',
  'tabler:arrow-up': '/static/icons/arrow-up.svg',
  'tabler:arrow-down': '/static/icons/arrow-down.svg',
  'tabler:passbook': '/static/icons/passbook.svg',
  // 罚单图标
  'tabler:alert-circle': '/static/icons/alert-circle.svg',
  'tabler:list': '/static/icons/list.svg',
  'tabler:note': '/static/icons/note.svg',
  // 交易分类
  'tabler:food': '/static/icons/food.svg',
  'tabler:car': '/static/icons/car.svg',
  'tabler:game': '/static/icons/game.svg',
  'tabler:shopping-bag': '/static/icons/shopping-bag.svg',
  'tabler:plane': '/static/icons/plane.svg',
  'tabler:wallet': '/static/icons/wallet.svg',
  'tabler:reload': '/static/icons/reload.svg',
}

// 纯文字 fallback（仅用于未知图标名）
const textFallback: Record<string, string> = {
  'tabler:plus': '＋',
  'tabler:chevron-left': '‹',
  'tabler:x': '✕',
  'tabler:check': '✓',
  'tabler:arrow-right': '→',
}

const localSrc = computed(() => {
  const path = iconMap[props.name]
  if (!path) return ''
  if (props.variant === 'white') {
    return path.replace('/static/icons/', '/static/icons-white/')
  }
  if (props.variant === 'pink') {
    return path.replace('/static/icons/', '/static/icons-pink/')
  }
  if (props.variant === 'capsule') {
    return path.replace('/static/icons/', '/static/icons-capsule/')
  }
  return path
})
const fallback = computed(() => textFallback[props.name] || '•')
const iconStyle = computed(() => ({
  width: props.size + 'rpx',
  height: props.size + 'rpx',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}))
</script>

<style lang="scss" scoped>
.kd-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.kd-icon-text {
  line-height: 1;
}
</style>
