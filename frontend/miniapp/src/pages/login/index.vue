<template>
  <view class="page-login">
    <view class="login-bg">
      <view class="login-bg__circle login-bg__circle--1" />
      <view class="login-bg__circle login-bg__circle--2" />
    </view>

    <view class="login-content">
      <view class="login-logo animate-zoom-in">
        <KdIcon class="login-logo__icon animate-heartbeat" name="tabler:heart" :size="80" variant="pink" />
        <text class="login-logo__name">咔哒</text>
        <text class="login-logo__slogan animate-fade-in" style="animation-delay: 300ms">记录我们的每一天</text>
      </view>

      <!-- 微信一键登录 -->
      <view v-if="mode === 'wx'" class="login-wx animate-fade-in-up" style="animation-delay: 400ms">
        <button class="login-btn login-btn--wx" :loading="wxLoading" @tap="handleWxLogin">
          微信一键登录
        </button>
        <view class="login-divider">
          <view class="login-divider__line" />
          <text class="login-divider__text">其他方式</text>
          <view class="login-divider__line" />
        </view>
        <button class="login-btn login-btn--secondary" @tap="mode = 'password'">
          用户名密码登录
        </button>
      </view>

      <!-- 用户名密码登录 -->
      <view v-else-if="mode === 'password'" class="login-form">
        <view class="login-input-group">
          <input class="login-input" v-model="username" placeholder="用户名" placeholder-class="login-input__placeholder" maxlength="50" />
        </view>
        <view class="login-input-group">
          <input class="login-input" v-model="password" :password="true" placeholder="密码" placeholder-class="login-input__placeholder" maxlength="128" />
        </view>
        <button class="login-btn" :disabled="!username || !password || loading" @tap="handlePasswordLogin">
          <view v-if="loading" class="login-btn__loading animate-spin" />
          {{ loading ? '登录中...' : '登录' }}
        </button>
        <button class="login-btn login-btn--text" @tap="mode = 'wx'">返回微信登录</button>
      </view>

      <!-- 首次微信登录：完善资料 -->
      <view v-else-if="mode === 'bind'" class="login-form">
        <text class="bind-title">完善个人资料</text>

        <!-- 头像 -->
        <view class="bind-avatar-wrap">
          <button class="bind-avatar-btn" open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
            <image v-if="avatarUrl" class="bind-avatar-img" :src="avatarUrl" mode="aspectFill" />
            <view v-else class="bind-avatar-placeholder">
              <KdIcon name="tabler:camera" :size="48" color="#999" />
              <text class="bind-avatar-placeholder__text">选择头像</text>
            </view>
          </button>
        </view>

        <!-- 昵称 -->
        <view class="login-input-group">
          <input class="login-input" :value="bindNickname" @input="bindNickname = ($event as any).detail.value" placeholder="昵称（必填）" placeholder-class="login-input__placeholder" maxlength="20" type="nickname" />
        </view>

        <!-- 生日 -->
        <view class="login-input-group">
          <text class="login-input-label">生日</text>
          <picker mode="date" :value="bindBirthday" :end="todayStr" @change="onBirthdayChange">
            <text :class="['login-input-picker', !bindBirthday && 'login-input-picker--placeholder']">
              {{ bindBirthday || '选择生日（必填）' }}
            </text>
          </picker>
        </view>

        <!-- 用户名 -->
        <view class="login-input-group">
          <input class="login-input" v-model="bindUsername" placeholder="用户名（2-50位，用于登录）" placeholder-class="login-input__placeholder" maxlength="50" />
        </view>

        <!-- 密码 -->
        <view class="login-input-group">
          <input class="login-input" v-model="bindPassword" :password="true" placeholder="密码（至少6位）" placeholder-class="login-input__placeholder" maxlength="128" />
        </view>

        <button
          class="login-btn"
          :disabled="!canBind || loading"
          @tap="handleBind"
        >
          <view v-if="loading" class="login-btn__loading animate-spin" />
          {{ loading ? '保存中...' : '完成' }}
        </button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { ensureHttps } from '@/utils/request'
import KdIcon from '@/components/KdIcon.vue'

const authStore = useAuthStore()

const mode = ref<'wx' | 'password' | 'bind'>('wx')
const wxLoading = ref(false)
const loading = ref(false)

// 用户名密码登录
const username = ref('')
const password = ref('')

// 绑定资料
const avatarUrl = ref('')
const avatarPath = ref('')
const bindNickname = ref('')
const bindBirthday = ref('')
const bindUsername = ref('')
const bindPassword = ref('')

const todayStr = new Date().toISOString().split('T')[0]

const canBind = computed(() =>
  bindNickname.value.trim() &&
  bindBirthday.value &&
  bindUsername.value.length >= 2 &&
  bindPassword.value.length >= 6
)

/** 登录成功后的跳转 */
const afterLogin = async () => {
  const userInfo = await authStore.fetchUserInfo()
  uni.showToast({ title: '登录成功', icon: 'success' })
  setTimeout(() => {
    if (userInfo.has_couple) {
      uni.reLaunch({ url: '/pages/index/index' })
    } else {
      uni.reLaunch({ url: '/pages/couple/bind' })
    }
  }, 500)
}

/** 微信登录 */
const handleWxLogin = async () => {
  wxLoading.value = true
  try {
    // #ifdef MP-WEIXIN
    const wxRes = await new Promise<{code: string}>((resolve, reject) => {
      wx.login({
        success: (res: any) => res.code ? resolve({ code: res.code }) : reject(new Error('获取登录凭证失败')),
        fail: (err: any) => reject(err),
      })
    })
    const res = await authApi.wxLogin(wxRes.code)
    authStore.setToken(res.access_token)
    const userInfo = await authApi.getMe()
    authStore.setUserInfo(userInfo)
    if (!userInfo.username) {
      mode.value = 'bind'
    } else {
      await afterLogin()
    }
    // #endif
    // #ifndef MP-WEIXIN
    uni.showToast({ title: '请在微信小程序中使用', icon: 'none' })
    // #endif
  } catch (e: any) {
    uni.showToast({ title: e.message || '微信登录失败', icon: 'none', duration: 3000 })
  } finally {
    wxLoading.value = false
  }
}

/** 用户名密码登录 */
const handlePasswordLogin = async () => {
  if (!username.value || !password.value) return
  loading.value = true
  try {
    const res = await authApi.loginPassword(username.value, password.value)
    authStore.setToken(res.access_token)
    await afterLogin()
  } catch (e: any) {
    uni.showToast({ title: e.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

/** 选择头像 */
const onChooseAvatar = (e: any) => {
  const path = e.detail.avatarUrl
  if (path) {
    avatarPath.value = path
    avatarUrl.value = path
  }
}

/** 选择生日 */
const onBirthdayChange = (e: any) => {
  bindBirthday.value = e.detail.value
}

/** 完善资料并绑定 */
const handleBind = async () => {
  if (!canBind.value) return
  loading.value = true
  try {
    // 上传头像
    if (avatarPath.value) {
      const uploadRes = await authApi.uploadAvatar(avatarPath.value)
      avatarUrl.value = ensureHttps(uploadRes.avatar_url)
    }
    // 绑定用户名密码 + 更新昵称生日
    await authApi.bindUsername({
      username: bindUsername.value,
      password: bindPassword.value,
      nickname: bindNickname.value.trim(),
      birthday: bindBirthday.value,
    })
    uni.showToast({ title: '资料已完善', icon: 'success' })
    await authStore.fetchUserInfo()
    await afterLogin()
  } catch (e: any) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-login {
  min-height: 100vh;
  background: $bg-page;
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 600rpx;
  background: $gradient-dawn;
  &__circle {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
    &--1 { width: 300rpx; height: 300rpx; background: $heart-pink; top: -50rpx; right: -50rpx; animation: float 6s ease-in-out infinite; }
    &--2 { width: 200rpx; height: 200rpx; background: $lavender; top: 100rpx; left: -30rpx; animation: float 8s ease-in-out infinite reverse; }
  }
}

.login-content {
  position: relative;
  z-index: 1;
  padding: 0 64rpx;
  padding-top: 200rpx;
}

.login-logo {
  text-align: center;
  margin-bottom: 80rpx;
  opacity: 0;
  &__icon { font-size: 80rpx; display: block; margin-bottom: 16rpx; }
  &__name { font-size: $font-size-hero; font-weight: $font-weight-bold; color: $heart-pink; display: block; margin-bottom: 12rpx; }
  &__slogan { font-size: $font-size-base; color: $text-secondary; opacity: 0; }
}

.login-wx { opacity: 0; }
.login-form { margin-bottom: 48rpx; }

.login-input-group {
  display: flex;
  align-items: center;
  background: $bg-card;
  border: 2rpx solid $border-light;
  border-radius: $radius-base;
  padding: 0 32rpx;
  height: 96rpx;
  margin-bottom: 24rpx;
  transition: all $duration-normal $ease-soft;
  &:focus-within { border-color: $heart-pink-light; box-shadow: 0 0 0 4rpx rgba(255, 107, 138, 0.1); }
}

.login-input {
  flex: 1;
  height: 96rpx;
  font-size: $font-size-md;
  color: $text-primary;
  &__placeholder { color: $text-tertiary; }
}

.login-input-label {
  font-size: $font-size-sm;
  color: $text-tertiary;
  margin-right: 16rpx;
  flex-shrink: 0;
}

.login-input-picker {
  flex: 1;
  font-size: $font-size-md;
  color: $text-primary;
  &--placeholder { color: $text-tertiary; }
}

.login-btn {
  width: 100%;
  height: 96rpx;
  background: $gradient-heart;
  color: $text-inverse;
  border: none;
  border-radius: $radius-full;
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  box-shadow: $shadow-glow;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 32rpx;
  &::after { display: none; }
  &[disabled] { opacity: 0.5; }
  &__loading {
    width: 36rpx; height: 36rpx;
    border: 4rpx solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    margin-right: 16rpx;
  }
  &--wx { background: #07C160; box-shadow: 0 0 24rpx rgba(7, 193, 96, 0.3); &:active { background: #06AD56; } }
  &--secondary { background: transparent; color: $text-secondary; border: 2rpx solid $border-normal; box-shadow: none; &:active { background: $bg-page; } }
  &--text { background: transparent; color: $text-secondary; box-shadow: none; height: 80rpx; font-size: $font-size-base; font-weight: $font-weight-regular; &:active { opacity: 0.7; } }
}

.login-divider {
  display: flex;
  align-items: center;
  margin: 32rpx 0;
  &__line { flex: 1; height: 2rpx; background: $border-light; }
  &__text { padding: 0 24rpx; font-size: $font-size-sm; color: $text-tertiary; }
}

.bind-title {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;
  color: $text-primary;
  display: block;
  text-align: center;
  margin-bottom: 32rpx;
}

.bind-avatar-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 32rpx;
}

.bind-avatar-btn {
  width: 160rpx;
  height: 160rpx;
  border-radius: $radius-full;
  overflow: hidden;
  padding: 0;
  margin: 0;
  background: $bg-page;
  border: 4rpx dashed $border-normal;
  &::after { display: none; }
}

.bind-avatar-img {
  width: 160rpx;
  height: 160rpx;
}

.bind-avatar-placeholder {
  width: 160rpx;
  height: 160rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  &__icon { font-size: 48rpx; margin-bottom: 8rpx; }
  &__text { font-size: $font-size-xs; color: $text-tertiary; }
}
</style>
