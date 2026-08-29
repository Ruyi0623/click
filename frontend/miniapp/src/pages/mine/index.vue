<template>
  <view class="page-mine">
    <view class="mine-bg">
      <view class="mine-bg__circle" />
    </view>

    <view class="mine-header animate-fade-in-down">
      <text class="mine-title">我的</text>
    </view>

    <view class="mine-profile animate-card-slide" @tap="goCoupleInfo">
      <image class="mine-avatar" :src="userInfo?.avatar_url || '/static/images/default-avatar.png'" mode="aspectFill" />
      <view class="mine-info">
        <text class="mine-nickname">{{ userInfo?.nickname || '未登录' }}</text>
        <text class="mine-phone">{{ userInfo?.phone || '' }}</text>
      </view>
      <KdIcon name="tabler:arrow-right" :size="32" color="#ccc" />
    </view>

    <view v-if="coupleInfo" class="mine-couple animate-card-slide" style="animation-delay: 100ms">
      <view class="mine-couple__item">
        <text class="mine-couple__label">恋爱天数</text>
        <text class="mine-couple__value">{{ coupleInfo.days_together }}</text>
      </view>
      <view class="mine-couple__divider" />
      <view class="mine-couple__item">
        <text class="mine-couple__label">起始日期</text>
        <text class="mine-couple__value">{{ coupleInfo.start_date }}</text>
      </view>
    </view>

    <view class="mine-menu animate-card-slide" style="animation-delay: 200ms">
      <view class="mine-menu__item" @tap="handleUnbind">
        <KdIcon class="mine-menu__icon" name="tabler:unlock" :size="40" />
        <text class="mine-menu__text">解除配对</text>
        <KdIcon name="tabler:arrow-right" :size="32" color="#ccc" />
      </view>
      <view class="mine-menu__item" @tap="handleLogout">
        <KdIcon class="mine-menu__icon" name="tabler:logout" :size="40" />
        <text class="mine-menu__text">退出登录</text>
        <KdIcon name="tabler:arrow-right" :size="32" color="#ccc" />
      </view>
    </view>

  </view>

  <KdDialog
    :visible="showUnbindConfirm"
    title="解除配对"
    content="解除配对后，所有共享数据将被清除，确定要解除吗？"
    confirm-color="#EF5350"
    @close="showUnbindConfirm = false"
    @confirm="onUnbindConfirm"
  />
  <KdDialog
    :visible="showLogoutConfirm"
    title="退出登录"
    content="确定要退出登录吗？"
    @close="showLogoutConfirm = false"
    @confirm="onLogoutConfirm"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useCoupleStore } from '@/stores/couple'
import { coupleApi, type CoupleInfo } from '@/api/couple'
import { ensureHttps } from '@/utils/request'
import KdIcon from '@/components/KdIcon.vue'
import KdDialog from '@/components/KdDialog.vue'

const authStore = useAuthStore()
const coupleStore = useCoupleStore()
const userInfo = computed(() => authStore.userInfo ? { ...authStore.userInfo, avatar_url: ensureHttps(authStore.userInfo.avatar_url || '') } : null)
const coupleInfo = ref<CoupleInfo | null>(null)
const showUnbindConfirm = ref(false)
const showLogoutConfirm = ref(false)

const navigateTo = (url: string) => uni.navigateTo({ url })
const goCoupleInfo = () => navigateTo('/pages/couple/info')

const loadData = async () => {
  try {
    coupleInfo.value = await coupleApi.info()
  } catch {}
}

const handleUnbind = () => {
  showUnbindConfirm.value = true
}
const onUnbindConfirm = async () => {
  try {
    await coupleApi.unbind()
    await authApi.deleteAccount()
    authStore.logout()
    coupleStore.clear()
    uni.reLaunch({ url: '/pages/login/index' })
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

const handleLogout = () => {
  showLogoutConfirm.value = true
}
const onLogoutConfirm = () => {
  authStore.logout()
  coupleStore.clear()
  uni.reLaunch({ url: '/pages/login/index' })
}

onMounted(loadData)
onShow(loadData)
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-mine {
  min-height: 100vh;
  background: $bg-page;
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
  position: relative;
  box-sizing: border-box;
  width: 100%;
  overflow: hidden;
}

.mine-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 400rpx;
  background: $gradient-dawn;
  &__circle {
    position: absolute;
    width: 300rpx;
    height: 300rpx;
    border-radius: 50%;
    background: $heart-pink;
    opacity: 0.06;
    top: -100rpx;
    right: -50rpx;
  }
}

.mine-header {
  position: relative;
  z-index: 1;
  padding: 80rpx $padding-page 24rpx;
  opacity: 0;
}
.mine-title {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;
  color: $text-primary;
}

.mine-profile {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 32rpx;
  margin: 0 $padding-page 24rpx;
  box-shadow: $shadow-sm;
  opacity: 0;
  transition: transform 0.2s ease;
  &:active { transform: scale(0.98); }
}
.mine-avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: $radius-full;
  margin-right: 24rpx;
}
.mine-info { flex: 1; }
.mine-nickname {
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  color: $text-primary;
  display: block;
}
.mine-phone {
  font-size: $font-size-sm;
  color: $text-secondary;
  display: block;
  margin-top: 8rpx;
}
.mine-arrow {
  color: $text-tertiary;
}

.mine-couple {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 32rpx;
  margin: 0 $padding-page 24rpx;
  box-shadow: $shadow-sm;
  opacity: 0;
  &__item {
    flex: 1;
    text-align: center;
  }
  &__label {
    font-size: $font-size-sm;
    color: $text-secondary;
    display: block;
    margin-bottom: 8rpx;
  }
  &__value {
    font-size: $font-size-xl;
    font-weight: $font-weight-bold;
    color: $heart-pink;
    font-family: $font-family-number;
  }
  &__divider {
    width: 2rpx;
    height: 60rpx;
    background: $border-light;
  }
}

.mine-menu {
  background: $bg-card;
  border-radius: $radius-lg;
  margin: 0 $padding-page 24rpx;
  box-shadow: $shadow-sm;
  overflow: hidden;
  opacity: 0;
  &__item {
    display: flex;
    align-items: center;
    padding: 32rpx;
    border-bottom: 2rpx solid $border-light;
    &:last-child { border-bottom: none; }
    &:active { background: $bg-page; }
  }
  &__icon {
    margin-right: 24rpx;
  }
  &__text {
    flex: 1;
    font-size: $font-size-md;
    color: $text-primary;
  }
  &__arrow {
    color: $text-tertiary;
  }
}
</style>
