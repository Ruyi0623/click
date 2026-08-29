<template>
  <view class="page-detail">
    <view v-if="loading" class="loading-wrap"><view class="loading-spinner animate-spin" /></view>
    <view v-else-if="magazine" class="detail-content">
      <!-- 封面头部 -->
      <view class="detail-header" :style="{ background: getMonthGradient(magazine.month) }">
        <text class="detail-month">{{ magazine.month }}月</text>
        <text class="detail-year">{{ magazine.year }}</text>
        <text class="detail-title">恋爱月刊</text>
      </view>

      <!-- Markdown 正文 -->
      <view class="detail-body">
        <view class="detail-body__inner">
          <KdMarkdown :content="magazine.content" />
        </view>
      </view>

      <!-- 分享按钮 -->
      <view class="share-section">
        <button class="share-btn" open-type="share">
          <KdIcon name="tabler:share" :size="28" color="#FF8FA3" />
          <text class="share-btn__text">分享给 TA</text>
        </button>
        <button class="share-btn share-btn--save" @tap="savePoster">
          <KdIcon name="tabler:download" :size="28" color="#FF8FA3" />
          <text class="share-btn__text">保存海报</text>
        </button>
      </view>

      <!-- 底部落款 -->
      <view class="detail-footer">
        <text class="detail-footer__text">— 咔哒 · 恋爱月刊 —</text>
        <text class="detail-footer__ai">基于 DeepSeek V4 Flash 生成</text>
      </view>
    </view>

    <!-- 海报 Canvas（隐藏） -->
    <canvas id="poster" canvas-id="poster" type="2d" class="poster-canvas" />
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad, onShareAppMessage } from '@dcloudio/uni-app'
import { magazineApi, type Magazine } from '@/api/magazine'
import KdMarkdown from '@/components/KdMarkdown.vue'
import KdIcon from '@/components/KdIcon.vue'

const magazine = ref<Magazine | null>(null)
const loading = ref(true)
let magazineId = ''

const monthGradients: Record<string, string> = {
  '01': 'linear-gradient(135deg, #E8DEF8, #B39DDB)',
  '02': 'linear-gradient(135deg, #FFD6DE, #FF8FA3)',
  '03': 'linear-gradient(135deg, #C8E6C9, #81C784)',
  '04': 'linear-gradient(135deg, #B3E5FC, #4FC3F7)',
  '05': 'linear-gradient(135deg, #FFF9C4, #FFD54F)',
  '06': 'linear-gradient(135deg, #B2EBF2, #00BCD4)',
  '07': 'linear-gradient(135deg, #F8BBD0, #E91E63)',
  '08': 'linear-gradient(135deg, #DCEDC8, #8BC34A)',
  '09': 'linear-gradient(135deg, #FFE0B2, #FF9800)',
  '10': 'linear-gradient(135deg, #FFCCBC, #FF5722)',
  '11': 'linear-gradient(135deg, #D1C4E9, #7E57C2)',
  '12': 'linear-gradient(135deg, #BBDEFB, #42A5F5)',
}

const monthColors: Record<string, string[]> = {
  '01': ['#E8DEF8', '#B39DDB'],
  '02': ['#FFD6DE', '#FF8FA3'],
  '03': ['#C8E6C9', '#81C784'],
  '04': ['#B3E5FC', '#4FC3F7'],
  '05': ['#FFF9C4', '#FFD54F'],
  '06': ['#B2EBF2', '#00BCD4'],
  '07': ['#F8BBD0', '#E91E63'],
  '08': ['#DCEDC8', '#8BC34A'],
  '09': ['#FFE0B2', '#FF9800'],
  '10': ['#FFCCBC', '#FF5722'],
  '11': ['#D1C4E9', '#7E57C2'],
  '12': ['#BBDEFB', '#42A5F5'],
}

const getMonthGradient = (month: string) => monthGradients[month] || monthGradients['01']

// 解析 Markdown 为可绘制的行
const parseContent = (content: string) => {
  const lines = content.split('\n')
  const result: Array<{ text: string; type: 'heading' | 'normal' | 'hr' | 'list' }> = []
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue
    if (/^---+$/.test(trimmed)) { result.push({ text: '', type: 'hr' }); continue }
    if (/^#{1,4}\s/.test(trimmed)) { result.push({ text: trimmed.replace(/^#{1,4}\s+/, ''), type: 'heading' }); continue }
    if (trimmed.startsWith('- ')) { result.push({ text: '• ' + trimmed.replace(/^- /, '').replace(/\*\*/g, ''), type: 'list' }); continue }
    const clean = trimmed.replace(/\*\*/g, '')
    result.push({ text: clean, type: 'normal' })
  }
  return result
}

// 按固定字数换行，返回行数
const wrapText = (text: string, maxChars: number) => {
  return Math.ceil(text.length / maxChars) || 1
}

// 保存海报到相册（Canvas 2D API）
const savePoster = () => {
  if (!magazine.value) return
  uni.showLoading({ title: '生成长图中...' })

  const W = 375
  const PADDING = 30
  const colors = monthColors[magazine.value.month] || monthColors['01']
  const MAX_CHARS_NORMAL = 26
  const MAX_CHARS_HEADING = 16
  const FONT_SIZE_NORMAL = 14
  const FONT_SIZE_HEADING = 18
  const LINE_HEIGHT_NORMAL = FONT_SIZE_NORMAL * 1.8
  const LINE_HEIGHT_HEADING = FONT_SIZE_HEADING * 1.8

  // 计算总高度
  const parsed = parseContent(magazine.value.content)
  let totalH = 260 // 封面头部高度
  totalH += 30 // 内容区上间距
  for (const item of parsed) {
    if (item.type === 'hr') { totalH += 30; continue }
    if (item.type === 'heading') {
      totalH += wrapText(item.text, MAX_CHARS_HEADING) * LINE_HEIGHT_HEADING + 20
    } else {
      totalH += wrapText(item.text, MAX_CHARS_NORMAL) * LINE_HEIGHT_NORMAL + 12
    }
  }
  totalH += 80
  totalH = Math.max(totalH, 500)

  // Canvas 2D API 获取 canvas 节点
  const query = uni.createSelectorQuery()
  query.select('#poster')
    .fields({ node: true, size: true })
    .exec((res) => {
      if (!res[0]) {
        uni.hideLoading()
        uni.showToast({ title: '画布初始化失败', icon: 'none' })
        return
      }
      const canvas = res[0].node
      const ctx = canvas.getContext('2d')

      // 设置画布尺寸（移动端限制，用固定比例）
      const dpr = 2
      canvas.width = W * dpr
      canvas.height = totalH * dpr
      ctx.scale(dpr, dpr)

      // 白色背景
      ctx.fillStyle = '#fff'
      ctx.fillRect(0, 0, W, totalH)

      // 封面渐变
      const HEADER_H = 240
      const grd = ctx.createLinearGradient(0, 0, W, HEADER_H)
      grd.addColorStop(0, colors[0])
      grd.addColorStop(1, colors[1])
      ctx.fillStyle = grd
      ctx.fillRect(0, 0, W, HEADER_H)

      // 月份大字
      ctx.fillStyle = 'rgba(255,255,255,0.9)'
      ctx.font = 'bold 64px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText(`${magazine.value!.month}月`, W / 2, 120)

      // 年份
      ctx.fillStyle = 'rgba(255,255,255,0.7)'
      ctx.font = '14px sans-serif'
      ctx.fillText(magazine.value!.year, W / 2, 150)

      // 标题
      ctx.fillStyle = 'rgba(255,255,255,0.9)'
      ctx.font = 'bold 20px sans-serif'
      ctx.fillText('恋爱月刊', W / 2, 190)

      // 白色内容区圆角过渡
      const CORNER_Y = HEADER_H - 20
      ctx.fillStyle = '#fff'
      ctx.beginPath()
      ctx.moveTo(0, HEADER_H)
      ctx.arcTo(0, CORNER_Y, 16, CORNER_Y, 16)
      ctx.lineTo(W - 16, CORNER_Y)
      ctx.arcTo(W, CORNER_Y, W, HEADER_H, 16)
      ctx.lineTo(W, totalH)
      ctx.lineTo(0, totalH)
      ctx.closePath()
      ctx.fill()

      // 绘制内容
      let y = HEADER_H + 30
      ctx.textAlign = 'left'
      for (const item of parsed) {
        if (item.type === 'hr') {
          ctx.strokeStyle = '#eee'
          ctx.lineWidth = 1
          ctx.beginPath()
          ctx.moveTo(PADDING, y)
          ctx.lineTo(W - PADDING, y)
          ctx.stroke()
          y += 30
          continue
        }
        if (item.type === 'heading') {
          ctx.fillStyle = '#E91E63'
          ctx.font = `bold ${FONT_SIZE_HEADING}px sans-serif`
          ctx.textAlign = 'center'
          const maxChars = MAX_CHARS_HEADING
          for (let i = 0; i < item.text.length; i += maxChars) {
            ctx.fillText(item.text.slice(i, i + maxChars), W / 2, y)
            y += LINE_HEIGHT_HEADING
          }
          ctx.textAlign = 'left'
          y += 20
          continue
        }
        ctx.fillStyle = item.type === 'list' ? '#666' : '#333'
        ctx.font = `${FONT_SIZE_NORMAL}px sans-serif`
        const maxChars = MAX_CHARS_NORMAL
        for (let i = 0; i < item.text.length; i += maxChars) {
          ctx.fillText(item.text.slice(i, i + maxChars), PADDING, y)
          y += LINE_HEIGHT_NORMAL
        }
        y += 12
      }

      // 底部水印
      ctx.fillStyle = 'rgba(0,0,0,0.15)'
      ctx.font = '10px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('咔哒 · 恋爱月刊 · 基于 DeepSeek V4 Flash 生成', W / 2, totalH - 30)

      // 导出图片（移动端需要更长延迟确保渲染完成）
      setTimeout(() => {
        uni.canvasToTempFilePath({
          canvas,
          destWidth: W * 2,
          destHeight: totalH * 2,
          success: (res) => {
            uni.saveImageToPhotosAlbum({
              filePath: res.tempFilePath,
              success: () => {
                uni.hideLoading()
                uni.showToast({ title: '已保存到相册', icon: 'success' })
              },
              fail: () => {
                uni.hideLoading()
                uni.showToast({ title: '保存失败', icon: 'none' })
              },
            })
          },
          fail: () => {
            uni.hideLoading()
            uni.showToast({ title: '生成长图失败', icon: 'none' })
          },
        })
      }, 1000)
    })
}

// 微信分享
onShareAppMessage(() => {
  return {
    title: `${magazine.value?.year}年${magazine.value?.month}月 恋爱月刊`,
    path: `/pages/magazine/detail?id=${magazineId}`,
  }
})

onLoad((query: any) => { magazineId = query?.id || '' })

onMounted(async () => {
  if (!magazineId) return
  try { magazine.value = await magazineApi.get(magazineId) } catch {} finally { loading.value = false }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-detail {
  min-height: 100vh;
  background: $bg-page;
}

.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 120rpx 0;
}
.loading-spinner {
  width: 48rpx;
  height: 48rpx;
  border: 4rpx solid $border-light;
  border-top-color: $sunrise-gold;
  border-radius: 50%;
}

.detail-header {
  padding: 80rpx 48rpx;
  text-align: center;
}
.detail-month {
  font-size: 120rpx;
  font-weight: $font-weight-bold;
  color: rgba(255, 255, 255, 0.9);
  display: block;
  font-family: $font-family-number;
  line-height: 1;
}
.detail-year {
  font-size: $font-size-md;
  color: rgba(255, 255, 255, 0.7);
  display: block;
  margin-top: 16rpx;
}
.detail-title {
  font-size: $font-size-xl;
  font-weight: $font-weight-semibold;
  color: rgba(255, 255, 255, 0.9);
  display: block;
  margin-top: 24rpx;
}

.detail-body {
  margin: -40rpx 24rpx 0;
  padding: 0;
  background: $bg-card;
  border-radius: 32rpx 32rpx 24rpx 24rpx;
  box-shadow: 0 8rpx 40rpx rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 1;

  &__inner {
    padding: 48rpx 36rpx;
  }
}

.share-section {
  display: flex;
  gap: 24rpx;
  margin: 32rpx 24rpx 0;
}
.share-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  background: $bg-card;
  border: 2rpx solid $border-light;
  border-radius: $radius-full;
  height: 80rpx;
  &::after { display: none; }
  &__text { font-size: $font-size-base; color: $text-primary; }
  &--save { border-color: $heart-pink; }
}

.detail-footer {
  padding: 48rpx 0 80rpx;
  text-align: center;
  &__text {
    font-size: $font-size-sm;
    color: $text-tertiary;
    display: block;
  }
  &__ai {
    font-size: $font-size-xs;
    color: $text-tertiary;
    opacity: 0.6;
    display: block;
    margin-top: 8rpx;
  }
}

.poster-canvas {
  position: fixed;
  left: -9999px;
  top: -9999px;
  width: 600px;
  height: 5000px;
}
</style>
