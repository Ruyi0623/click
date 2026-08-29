<script setup lang="ts">
import { onLaunch } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

onLaunch(async () => {
  const authStore = useAuthStore()
  authStore.loadFromStorage()

  // 未登录 → 登录页
  if (!authStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/login/index' })
    return
  }

  // 已登录 → 验证 token + 检查配对状态
  try {
    const userInfo = await authApi.getMe()
    authStore.setUserInfo(userInfo)

    if (!userInfo.has_couple) {
      // 已登录但未配对 → 配对页
      uni.reLaunch({ url: '/pages/couple/bind' })
    }
    // 已登录且已配对 → 留在首页（index 会加载数据）
  } catch {
    // token 失效 → 登录页
    authStore.logout()
    uni.reLaunch({ url: '/pages/login/index' })
  }
})
</script>

<style lang="scss">
@use '@/styles/variables.scss' as *;
@use '@/styles/animations.scss' as *;

page {
  font-family: $font-family-base;
  background: $bg-page;
  color: $text-primary;
  font-size: $font-size-base;
  line-height: $line-height-normal;
  -webkit-font-smoothing: antialiased;
  padding: 0;
  margin: 0;
  overflow-y: scroll;
  &::-webkit-scrollbar {
    display: none;
  }
}

/* 全局重置 */
view, text, scroll-view, swiper, button, input, textarea, navigator, image {
  box-sizing: border-box;
}

/* 隐藏滚动条 */
::-webkit-scrollbar {
  display: none;
}

/* 隐藏默认 button 样式 */
button::after {
  display: none;
}

/* 全局输入框样式 */
input {
  width: 100%;
  min-height: 96rpx;
  line-height: 96rpx;
  box-sizing: border-box;
}
textarea {
  width: 100%;
  box-sizing: border-box;
}
</style>
