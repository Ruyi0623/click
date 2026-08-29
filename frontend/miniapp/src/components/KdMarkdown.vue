<template>
  <view class="kd-markdown">
    <template v-for="(block, bi) in blocks" :key="bi">
      <!-- 分割线 -->
      <view v-if="block.type === 'hr'" class="md-hr">
        <view class="md-hr__line" />
        <view class="md-hr__dot" />
        <view class="md-hr__line" />
      </view>

      <!-- ## 大标题 -->
      <view v-else-if="block.type === 'heading' && block.level === 2" class="md-h2">
        <view class="md-h2__accent" />
        <view class="md-h2__text">
          <template v-for="(t, ti) in block.children" :key="ti">
            <text v-if="t.type === 'text'" class="md-h2__content">{{ t.content }}</text>
            <text v-else-if="t.type === 'bold'" class="md-h2__content md-h2__content--bold">{{ t.content }}</text>
          </template>
        </view>
      </view>

      <!-- ### 小标题 -->
      <view v-else-if="block.type === 'heading' && block.level === 3" class="md-h3">
        <template v-for="(t, ti) in block.children" :key="ti">
          <text v-if="t.type === 'text'" class="md-h3__content">{{ t.content }}</text>
          <text v-else-if="t.type === 'bold'" class="md-h3__content md-h3__content--bold">{{ t.content }}</text>
        </template>
      </view>

      <!-- 其他级别标题 -->
      <view v-else-if="block.type === 'heading'" class="md-h4">
        <template v-for="(t, ti) in block.children" :key="ti">
          <text v-if="t.type === 'text'" class="md-h4__content">{{ t.content }}</text>
          <text v-else-if="t.type === 'bold'" class="md-h4__content md-h4__content--bold">{{ t.content }}</text>
        </template>
      </view>

      <!-- 引用块 -->
      <view v-else-if="block.type === 'blockquote'" class="md-quote">
        <view class="md-quote__bar" />
        <view class="md-quote__content">
          <template v-for="(t, ti) in block.children" :key="ti">
            <text v-if="t.type === 'text'" class="md-text md-text--quote">{{ t.content }}</text>
            <text v-else-if="t.type === 'bold'" class="md-bold">{{ t.content }}</text>
            <text v-else-if="t.type === 'italic'" class="md-italic">{{ t.content }}</text>
          </template>
        </view>
      </view>

      <!-- 列表 -->
      <view v-else-if="block.type === 'list'" class="md-list">
        <view v-for="(item, ii) in block.items" :key="ii" class="md-list__item">
          <view class="md-list__bullet-wrap">
            <view class="md-list__bullet" />
          </view>
          <view class="md-list__text">
            <template v-for="(t, ti) in item" :key="ti">
              <text v-if="t.type === 'text'" class="md-text">{{ t.content }}</text>
              <text v-else-if="t.type === 'bold'" class="md-bold">{{ t.content }}</text>
              <text v-else-if="t.type === 'italic'" class="md-italic">{{ t.content }}</text>
              <text v-else-if="t.type === 'code'" class="md-code">{{ t.content }}</text>
            </template>
          </view>
        </view>
      </view>

      <!-- 段落 -->
      <view v-else class="md-paragraph">
        <template v-for="(t, ti) in block.children" :key="ti">
          <text v-if="t.type === 'text'" class="md-text">{{ t.content }}</text>
          <text v-else-if="t.type === 'bold'" class="md-bold">{{ t.content }}</text>
          <text v-else-if="t.type === 'italic'" class="md-italic">{{ t.content }}</text>
          <text v-else-if="t.type === 'code'" class="md-code">{{ t.content }}</text>
        </template>
      </view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { parseMarkdown, type BlockToken } from '@/utils/markdown'

const props = defineProps<{ content: string }>()

const blocks = computed<BlockToken[]>(() => parseMarkdown(props.content))
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.kd-markdown {
  padding: 0;
}

// ── ## 大标题 ──
.md-h2 {
  display: flex;
  align-items: stretch;
  margin: 48rpx 0 28rpx;
  &:first-child { margin-top: 0; }

  &__accent {
    width: 8rpx;
    border-radius: 4rpx;
    background: linear-gradient(180deg, #C9875D, #D4735F);
    margin-right: 20rpx;
    flex-shrink: 0;
  }

  &__text {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  &__content {
    font-size: 34rpx;
    font-weight: 700;
    color: $text-primary;
    font-family: 'Noto Serif SC', 'Songti SC', serif;
    letter-spacing: 2rpx;
    line-height: 1.4;
    &--bold { font-weight: 800; }
  }
}

// ── ### 小标题 ──
.md-h3 {
  margin: 36rpx 0 16rpx;
  padding-left: 4rpx;

  &__content {
    font-size: 28rpx;
    font-weight: 600;
    color: #8C7B6B;
    font-family: 'Noto Serif SC', 'Songti SC', serif;
    letter-spacing: 1rpx;
    line-height: 1.5;
    &--bold { font-weight: 700; color: $text-primary; }
  }
}

// ── 其他标题 ──
.md-h4 {
  margin: 28rpx 0 12rpx;

  &__content {
    font-size: 26rpx;
    font-weight: 600;
    color: $text-primary;
    line-height: 1.5;
    &--bold { font-weight: 700; }
  }
}

// ── 段落 ──
.md-paragraph {
  margin-bottom: 24rpx;
}

// ── 文字 ──
.md-text {
  font-size: 28rpx;
  color: $text-primary;
  line-height: 2;
  &--quote {
    color: $text-secondary;
    font-style: italic;
  }
}

.md-bold {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
  line-height: 2;
}

.md-italic {
  font-size: 28rpx;
  font-style: italic;
  color: $text-secondary;
  line-height: 2;
}

.md-code {
  font-size: 24rpx;
  color: #C9875D;
  background: #FDF8F0;
  padding: 2rpx 12rpx;
  border-radius: 6rpx;
  font-family: 'SF Mono', 'Menlo', monospace;
}

// ── 分割线 ──
.md-hr {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin: 40rpx 0;
  padding: 0 20rpx;

  &__line {
    flex: 1;
    height: 2rpx;
    background: linear-gradient(90deg, transparent, #E8DDD2, transparent);
  }

  &__dot {
    width: 8rpx;
    height: 8rpx;
    border-radius: 50%;
    background: #D4A574;
  }
}

// ── 引用块 ──
.md-quote {
  display: flex;
  margin: 28rpx 0;
  border-radius: 0 16rpx 16rpx 0;
  overflow: hidden;
  background: #FDF8F0;

  &__bar {
    width: 6rpx;
    background: linear-gradient(180deg, #D4A574, #C9875D);
  }

  &__content {
    flex: 1;
    padding: 24rpx 28rpx;
  }
}

// ── 列表 ──
.md-list {
  margin: 16rpx 0 28rpx;
  background: #FAF6F0;
  border-radius: 16rpx;
  padding: 20rpx 24rpx 20rpx 12rpx;

  &__item {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    margin-bottom: 16rpx;
    &:last-child { margin-bottom: 0; }
  }

  &__bullet-wrap {
    width: 44rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    padding-top: 16rpx;
  }

  &__bullet {
    width: 10rpx;
    height: 10rpx;
    border-radius: 50%;
    background: #C9875D;
  }

  &__text {
    flex: 1;
  }
}
</style>
