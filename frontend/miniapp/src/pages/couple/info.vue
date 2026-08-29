<template>
  <view class="page-couple-info">
    <view v-if="info" class="info-card">
      <KdCoupleHeader
        :my-avatar="ensureHttps(authStore.userInfo?.avatar_url || '')"
        :partner-avatar="ensureHttps(info.partner_avatar || '')"
        :days="info.days_together"
        :start-date="info.start_date"
      />
    </view>

    <!-- 个人信息 -->
    <view class="info-section">
      <text class="info-section__title">个人信息</text>
      <view class="info-list">
        <view class="info-item info-item--avatar">
          <text class="info-item__label">头像</text>
          <view class="info-item__right">
            <image class="info-item__avatar" :src="ensureHttps(authStore.userInfo?.avatar_url || '')" mode="aspectFill" />
            <KdIcon name="tabler:arrow-right" :size="32" color="#ccc" />
          </view>
          <button class="info-item__avatar-btn" open-type="chooseAvatar" @chooseavatar="onChooseAvatar" />
        </view>
        <view class="info-item" @tap="editNickname">
          <text class="info-item__label">昵称</text>
          <view class="info-item__right">
            <text class="info-item__value">{{ authStore.userInfo?.nickname || '-' }}</text>
            <KdIcon name="tabler:arrow-right" :size="32" color="#ccc" />
          </view>
        </view>
        <view v-if="authStore.userInfo?.username" class="info-item">
          <text class="info-item__label">用户名</text>
          <view class="info-item__right">
            <text class="info-item__value">{{ authStore.userInfo.username }}</text>
          </view>
        </view>
        <view class="info-item" @tap="editBirthday">
          <text class="info-item__label">生日</text>
          <view class="info-item__right">
            <text class="info-item__value">{{ authStore.userInfo?.birthday || '未设置' }}</text>
            <KdIcon name="tabler:arrow-right" :size="32" color="#ccc" />
          </view>
        </view>
        <view class="info-item" @tap="showGenderPicker = true">
          <text class="info-item__label">性别</text>
          <view class="info-item__right">
            <text class="info-item__value">{{ genderText }}</text>
            <KdIcon name="tabler:arrow-right" :size="32" color="#ccc" />
          </view>
        </view>
        <view class="info-item" @tap="!authStore.userInfo?.email && (showBindEmail = true)">
          <text class="info-item__label">邮箱</text>
          <view class="info-item__right">
            <text class="info-item__value">{{ authStore.userInfo?.email || '未绑定' }}</text>
            <KdIcon v-if="!authStore.userInfo?.email" name="tabler:arrow-right" :size="32" color="#ccc" />
          </view>
        </view>
      </view>
    </view>

    <!-- 情侣信息 -->
    <view class="info-section">
      <text class="info-section__title">情侣信息</text>
      <view class="info-list">
        <view class="info-item">
          <text class="info-item__label">配对关系 ID</text>
          <text class="info-item__value">{{ info?.id || '-' }}</text>
        </view>
        <view class="info-item">
          <text class="info-item__label">伴侣昵称</text>
          <text class="info-item__value">{{ info?.partner_nickname || '-' }}</text>
        </view>
        <view class="info-item">
          <text class="info-item__label">伴侣用户名</text>
          <text class="info-item__value">{{ info?.partner_username || '未设置' }}</text>
        </view>
        <view class="info-item">
          <text class="info-item__label">伴侣生日</text>
          <text class="info-item__value">{{ info?.partner_birthday || '未设置' }}</text>
        </view>
        <view class="info-item">
          <text class="info-item__label">伴侣性别</text>
          <text class="info-item__value">{{ partnerGenderText }}</text>
        </view>
        <view class="info-item">
          <text class="info-item__label">恋爱起始日</text>
          <text class="info-item__value">{{ info?.start_date || '-' }}</text>
        </view>
        <view class="info-item">
          <text class="info-item__label">在一起天数</text>
          <text class="info-item__value info-item__value--highlight">{{ info?.days_together || 0 }} 天</text>
        </view>
      </view>
    </view>

    <!-- 绑定邮箱弹窗 -->
    <view v-if="showBindEmail" class="modal">
      <view class="modal__mask" @tap="showBindEmail = false" />
      <view class="modal__content animate-slide-up">
        <text class="modal__title">绑定邮箱</text>
        <input class="modal__input" v-model="emailInput" placeholder="请输入邮箱地址" />
        <button class="modal__btn" :disabled="!emailInput || emailLoading" @tap="handleBindEmail">
          {{ emailLoading ? '绑定中...' : '确认绑定' }}
        </button>
      </view>
    </view>

    <!-- 修改昵称弹窗 -->
    <view v-if="showEditNickname" class="modal">
      <view class="modal__mask" @tap="showEditNickname = false" />
      <view class="modal__content animate-slide-up">
        <text class="modal__title">修改昵称</text>
        <input class="modal__input" v-model="nicknameInput" placeholder="请输入新昵称" />
        <button class="modal__btn" :disabled="!nicknameInput || nicknameLoading" @tap="handleUpdateNickname">
          {{ nicknameLoading ? '保存中...' : '确认修改' }}
        </button>
      </view>
    </view>

    <!-- 修改生日弹窗 -->
    <view v-if="showEditBirthday" class="modal">
      <view class="modal__mask" @tap="showEditBirthday = false" />
      <view class="modal__content animate-slide-up">
        <text class="modal__title">修改生日</text>
        <picker mode="date" :value="birthdayInput" @change="onBirthdayChange">
          <view class="modal__picker">
            <text>{{ birthdayInput || '请选择生日' }}</text>
          </view>
        </picker>
        <button class="modal__btn" :disabled="!birthdayInput || birthdayLoading" @tap="handleUpdateBirthday">
          {{ birthdayLoading ? '保存中...' : '确认修改' }}
        </button>
      </view>
    </view>

    <!-- 性别选择弹窗 -->
    <view v-if="showGenderPicker" class="modal">
      <view class="modal__mask" @tap="showGenderPicker = false" />
      <view class="modal__content animate-slide-up">
        <text class="modal__title">选择性别</text>
        <view class="gender-options">
          <view class="gender-option" :class="{ active: genderInput === 'male' }" @tap="genderInput = 'male'">
            <text>男</text>
          </view>
          <view class="gender-option" :class="{ active: genderInput === 'female' }" @tap="genderInput = 'female'">
            <text>女</text>
          </view>
        </view>
        <button class="modal__btn" :disabled="!genderInput || genderLoading" @tap="handleUpdateGender">
          {{ genderLoading ? '保存中...' : '确认修改' }}
        </button>
      </view>
    </view>

  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { coupleApi, type CoupleInfo } from '@/api/couple'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { ensureHttps } from '@/utils/request'
import KdCoupleHeader from '@/components/KdCoupleHeader.vue'
import KdIcon from '@/components/KdIcon.vue'

const authStore = useAuthStore()
const info = ref<CoupleInfo | null>(null)

// 绑定邮箱
const showBindEmail = ref(false)
const emailInput = ref('')
const emailLoading = ref(false)

// 修改昵称
const showEditNickname = ref(false)
const nicknameInput = ref('')
const nicknameLoading = ref(false)

// 修改生日
const showEditBirthday = ref(false)
const birthdayInput = ref('')
const birthdayLoading = ref(false)

// 修改性别
const showGenderPicker = ref(false)
const genderInput = ref('')
const genderLoading = ref(false)

const genderText = computed(() => {
  const g = authStore.userInfo?.gender
  if (g === 'male') return '男'
  if (g === 'female') return '女'
  return '未设置'
})

const partnerGenderText = computed(() => {
  const g = info.value?.partner_gender
  if (g === 'male') return '男'
  if (g === 'female') return '女'
  return '未设置'
})

const loadData = async () => {
  try {
    info.value = await coupleApi.info()
    await authStore.fetchUserInfo()
  } catch {}
}

// 修改头像（open-type="chooseAvatar" 回调，微信头像已是正方形，无需裁剪）
const onChooseAvatar = (e: any) => {
  const avatarUrl = e.detail.avatarUrl
  if (!avatarUrl) return
  uni.showLoading({ title: '上传中...' })
  authApi.uploadAvatar(avatarUrl).then(async () => {
    await authStore.fetchUserInfo()
    uni.showToast({ title: '头像更新成功', icon: 'success' })
  }).catch((err: any) => {
    uni.showToast({ title: err.message || '上传失败', icon: 'none' })
  }).finally(() => {
    uni.hideLoading()
  })
}

// 修改昵称
const editNickname = () => {
  nicknameInput.value = authStore.userInfo?.nickname || ''
  showEditNickname.value = true
}

const handleUpdateNickname = async () => {
  if (!nicknameInput.value) return
  nicknameLoading.value = true
  try {
    await authApi.updateProfile({ nickname: nicknameInput.value })
    await authStore.fetchUserInfo()
    showEditNickname.value = false
    uni.showToast({ title: '昵称更新成功', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '更新失败', icon: 'none' })
  } finally {
    nicknameLoading.value = false
  }
}

// 修改生日
const editBirthday = () => {
  birthdayInput.value = authStore.userInfo?.birthday || ''
  showEditBirthday.value = true
}

const onBirthdayChange = (e: any) => {
  birthdayInput.value = e.detail.value
}

const handleUpdateBirthday = async () => {
  if (!birthdayInput.value) return
  birthdayLoading.value = true
  try {
    await authApi.updateProfile({ birthday: birthdayInput.value })
    await authStore.fetchUserInfo()
    showEditBirthday.value = false
    uni.showToast({ title: '生日更新成功', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '更新失败', icon: 'none' })
  } finally {
    birthdayLoading.value = false
  }
}

// 绑定邮箱
const handleBindEmail = async () => {
  if (!emailInput.value) return
  emailLoading.value = true
  try {
    await authApi.bindEmail(emailInput.value)
    await authStore.fetchUserInfo()
    showBindEmail.value = false
    emailInput.value = ''
    uni.showToast({ title: '绑定成功', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '绑定失败', icon: 'none' })
  } finally {
    emailLoading.value = false
  }
}

// 修改性别
const handleUpdateGender = async () => {
  genderLoading.value = true
  try {
    await authApi.updateProfile({ gender: genderInput.value })
    await authStore.fetchUserInfo()
    showGenderPicker.value = false
    uni.showToast({ title: '性别更新成功', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '更新失败', icon: 'none' })
  } finally {
    genderLoading.value = false
  }
}

onMounted(loadData)
onShow(loadData)
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-couple-info {
  min-height: 100vh;
  background: $bg-page;
  padding: $padding-page;
  padding-bottom: calc(#{$padding-page} + env(safe-area-inset-bottom));
}

.info-card {
  background: $bg-card;
  border-radius: $radius-xl;
  padding: 48rpx;
  margin-bottom: 32rpx;
  box-shadow: $shadow-lg;
}

.info-section {
  margin-bottom: 32rpx;
  &__title {
    font-size: $font-size-sm;
    color: $text-secondary;
    margin-bottom: 16rpx;
    padding-left: 8rpx;
  }
}

.info-list {
  background: $bg-card;
  border-radius: $radius-lg;
  overflow: hidden;
  box-shadow: $shadow-sm;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx;
  border-bottom: 2rpx solid $border-light;
  &:last-child { border-bottom: none; }
  &__label {
    font-size: $font-size-base;
    color: $text-secondary;
  }
  &__right {
    display: flex;
    align-items: center;
    gap: 16rpx;
  }
  &__value {
    font-size: $font-size-base;
    color: $text-primary;
    font-weight: $font-weight-medium;
    &--highlight {
      color: $heart-pink;
      font-size: $font-size-lg;
      font-weight: $font-weight-bold;
    }
  }
  &__avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: $radius-full;
  }
}

.modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  &__mask {
    position: absolute;
    inset: 0;
    background: $bg-mask;
  }
  &__content {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: $bg-card;
    border-radius: $radius-xl $radius-xl 0 0;
    padding: 48rpx $padding-card;
    padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
  }
  &__title {
    font-size: $font-size-xl;
    font-weight: $font-weight-semibold;
    color: $text-primary;
    display: block;
    text-align: center;
    margin-bottom: 32rpx;
  }
  &__input {
    background: $bg-page;
    border: 2rpx solid $border-light;
    border-radius: $radius-base;
    padding: 24rpx 32rpx;
    font-size: $font-size-md;
    margin-bottom: 24rpx;
  }
  &__picker {
    background: $bg-page;
    border: 2rpx solid $border-light;
    border-radius: $radius-base;
    padding: 24rpx 32rpx;
    font-size: $font-size-md;
    margin-bottom: 24rpx;
    color: $text-primary;
  }
  &__btn {
    width: 100%;
    height: 96rpx;
    background: $gradient-heart;
    color: #fff;
    border: none;
    border-radius: $radius-full;
    font-size: $font-size-lg;
    font-weight: $font-weight-semibold;
    display: flex;
    align-items: center;
    justify-content: center;
    &::after { display: none; }
    &[disabled] { opacity: 0.5; }
  }
}

.gender-options {
  display: flex;
  gap: 24rpx;
  margin-bottom: 24rpx;
}

.gender-option {
  flex: 1;
  height: 96rpx;
  background: $bg-page;
  border: 2rpx solid $border-light;
  border-radius: $radius-base;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-size-md;
  color: $text-primary;
  transition: all 0.2s;

  &.active {
    background: $heart-pink-ghost;
    border-color: $heart-pink;
    color: $heart-pink;
  }
}

.info-item--avatar {
  position: relative;
}

.info-item__avatar-btn {
  position: absolute;
  inset: 0;
  opacity: 0;
  border: none;
  padding: 0;
  margin: 0;
  width: 100%;
  height: 100%;
  &::after { display: none; }
}
</style>
