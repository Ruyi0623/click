<template>
  <view v-if="photos.length" class="photo-grid" :class="`photo-grid--count-${Math.min(photos.length, 9)}`">
    <image
      v-for="(photo, index) in displayPhotos"
      :key="photo.id"
      class="photo-grid__item"
      :src="ensureHttps(photo.thumbnail_url || photo.url)"
      mode="aspectFill"
      @tap="previewImage(index)"
    />
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ensureHttps } from '@/utils/request'

interface Photo {
  id: string
  url: string
  thumbnail_url?: string | null
}

const props = withDefaults(defineProps<{
  photos: Photo[]
  gap?: number
}>(), {
  gap: 8,
})

const displayPhotos = computed(() => props.photos.slice(0, 9))

const previewImage = (index: number) => {
  uni.previewImage({
    current: index,
    urls: props.photos.map(p => ensureHttps(p.url)),
  })
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.photo-grid {
  display: grid;
  gap: 8rpx;
  border-radius: $radius-sm;
  overflow: hidden;

  &__item {
    width: 100%;
    height: 100%;
    border-radius: $radius-sm;
  }

  // 1 张：正方形
  &--count-1 {
    grid-template-columns: 1fr;
    max-width: 480rpx;
    .photo-grid__item {
      aspect-ratio: 1;
    }
  }

  // 2 张：两列
  &--count-2 {
    grid-template-columns: repeat(2, 1fr);
    .photo-grid__item {
      aspect-ratio: 1;
    }
  }

  // 3 张：三列
  &--count-3 {
    grid-template-columns: repeat(3, 1fr);
    .photo-grid__item {
      aspect-ratio: 1;
    }
  }

  // 4 张：2x2
  &--count-4 {
    grid-template-columns: repeat(2, 1fr);
    .photo-grid__item {
      aspect-ratio: 1;
    }
  }

  // 5-6 张：3 列
  &--count-5,
  &--count-6 {
    grid-template-columns: repeat(3, 1fr);
    .photo-grid__item {
      aspect-ratio: 1;
    }
  }

  // 7-9 张：3 列
  &--count-7,
  &--count-8,
  &--count-9 {
    grid-template-columns: repeat(3, 1fr);
    .photo-grid__item {
      aspect-ratio: 1;
    }
  }
}
</style>
