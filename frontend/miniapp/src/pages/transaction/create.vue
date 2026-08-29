<template>
  <view class="page-create">
    <view class="form-group">
      <text class="form-label">金额</text>
      <input class="form-input form-input--amount" v-model="amount" type="digit" placeholder="0.00" placeholder-style="font-size: 44rpx; color: #9E9EB0;" />
    </view>
    <view class="form-group">
      <text class="form-label">分类</text>
      <view class="category-grid">
        <view v-for="cat in categories" :key="cat.name" class="category-item" :class="{ 'category-item--active': category === cat.name }" @tap="category = cat.name">
          <KdIcon :name="cat.iconName" :size="40" />
          <text class="category-item__name">{{ cat.name }}</text>
        </view>
      </view>
    </view>
    <view class="form-group">
      <text class="form-label">描述（可选）</text>
      <input class="form-input" v-model="description" placeholder="如：火锅" />
    </view>
    <view class="form-group">
      <text class="form-label">消费时间</text>
      <picker mode="multiSelector" :range="pickerRange" :value="pickerValue" @change="onTimeChange" @columnchange="onColumnChange">
        <view class="form-input form-input--picker">
          <text>{{ happenedDisplay || '点击选择消费时间' }}</text>
          <KdIcon name="tabler:calendar" :size="28" color="#999" />
        </view>
      </picker>
    </view>
    <view class="form-group">
      <text class="form-label">分摊方式</text>
      <view class="form-radio-group">
        <view class="form-radio" :class="{ 'form-radio--active': splitType === 'equal' }" @tap="splitType = 'equal'"><text>AA</text></view>
        <view class="form-radio" :class="{ 'form-radio--active': splitType === 'payer_full' }" @tap="splitType = 'payer_full'"><text>我全付</text></view>
        <view class="form-radio" :class="{ 'form-radio--active': splitType === 'other_full' }" @tap="splitType = 'other_full'"><text>TA全付</text></view>
        <view class="form-radio" :class="{ 'form-radio--active': splitType === 'custom' }" @tap="splitType = 'custom'"><text>自定义</text></view>
      </view>
    </view>
    <view v-if="splitType === 'custom'" class="form-group">
      <text class="form-label">我承担金额</text>
      <input class="form-input" v-model="customAmount" type="digit" placeholder="我承担的金额" />
      <text class="form-hint">我承担 ¥{{ customAmount || '0' }}，TA 承担 ¥{{ taPart }}</text>
    </view>
    <button class="submit-btn" :disabled="!amount || !category || loading" @tap="submit">{{ isEdit ? '保存修改' : '记一笔' }}</button>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { transactionApi, type Transaction } from '@/api/transaction'
import KdIcon from '@/components/KdIcon.vue'

const isEdit = ref(false)
const editId = ref('')
const amount = ref('')
const category = ref('')
const description = ref('')
const splitType = ref('equal')
const customAmount = ref('')
const loading = ref(false)

const taPart = computed(() => {
  const total = parseFloat(amount.value) || 0
  const mine = parseFloat(customAmount.value) || 0
  return Math.max(total - mine, 0).toFixed(2)
})

// 消费时间
const now = new Date()
const pickedYear = ref(now.getFullYear())
const pickedMonth = ref(now.getMonth() + 1)
const pickedDay = ref(now.getDate())
const pickedHour = ref(now.getHours())

const categories = [
  { name: '餐饮', iconName: 'tabler:food' }, { name: '交通', iconName: 'tabler:car' }, { name: '娱乐', iconName: 'tabler:game' },
  { name: '购物', iconName: 'tabler:shopping-bag' }, { name: '旅行', iconName: 'tabler:plane' }, { name: '其他', iconName: 'tabler:wallet' },
]

// 日期时间选择器
const years = Array.from({ length: 5 }, (_, i) => now.getFullYear() - 2 + i)
const months = Array.from({ length: 12 }, (_, i) => i + 1)
const getDaysInMonth = (y: number, m: number) => new Date(y, m, 0).getDate()
const days = computed(() => Array.from({ length: getDaysInMonth(pickedYear.value, pickedMonth.value) }, (_, i) => i + 1))
const hours = Array.from({ length: 24 }, (_, i) => i)

const pickerRange = computed(() => [
  years.map(y => y + '年'),
  months.map(m => m + '月'),
  days.value.map(d => d + '日'),
  hours.map(h => h.toString().padStart(2, '0') + '时'),
])

const pickerValue = computed(() => [
  years.indexOf(pickedYear.value),
  months.indexOf(pickedMonth.value),
  days.value.indexOf(pickedDay.value),
  hours.indexOf(pickedHour.value),
])

const happenedDisplay = computed(() => {
  return `${pickedYear.value}-${String(pickedMonth.value).padStart(2, '0')}-${String(pickedDay.value).padStart(2, '0')} ${String(pickedHour.value).padStart(2, '0')}:00`
})

const onColumnChange = (e: any) => {
  const { column, value } = e.detail
  if (column === 0) pickedYear.value = years[value]
  else if (column === 1) pickedMonth.value = months[value]
  else if (column === 2) pickedDay.value = days.value[value]
  else if (column === 3) pickedHour.value = hours[value]
  const maxDay = getDaysInMonth(pickedYear.value, pickedMonth.value)
  if (pickedDay.value > maxDay) pickedDay.value = maxDay
}

const onTimeChange = (e: any) => {
  const [yi, mi, di, hi] = e.detail.value
  pickedYear.value = years[yi]
  pickedMonth.value = months[mi]
  pickedDay.value = days.value[di]
  pickedHour.value = hours[hi]
}

const happenedAtIso = () => {
  return `${pickedYear.value}-${String(pickedMonth.value).padStart(2, '0')}-${String(pickedDay.value).padStart(2, '0')}T${String(pickedHour.value).padStart(2, '0')}:00:00`
}

onLoad(async (query: any) => {
  if (query?.id) {
    isEdit.value = true
    editId.value = query.id
    try {
      const list = await transactionApi.list({ limit: 200 })
      const tx = list.find(t => t.id === query.id)
      if (tx) {
        amount.value = String(tx.amount)
        category.value = tx.category
        description.value = tx.description || ''
        splitType.value = tx.split_type
        if (tx.custom_amount != null) customAmount.value = String(Math.max(tx.amount - tx.custom_amount, 0))
        if (tx.happened_at) {
          const d = new Date(tx.happened_at)
          pickedYear.value = d.getFullYear()
          pickedMonth.value = d.getMonth() + 1
          pickedDay.value = d.getDate()
          pickedHour.value = d.getHours()
        }
      }
    } catch {}
  }
})

const submit = async () => {
  if (!amount.value || !category.value) return
  const amt = parseFloat(amount.value)
  if (isNaN(amt) || amt <= 0) {
    uni.showToast({ title: '金额必须大于 0', icon: 'none' })
    return
  }
  if (splitType.value === 'custom') {
    const myShare = parseFloat(customAmount.value) || 0
    if (myShare < 0) {
      uni.showToast({ title: '金额不能为负数', icon: 'none' })
      return
    }
  }
  loading.value = true
  try {
    const data: any = {
      amount: parseFloat(amount.value),
      category: category.value,
      description: description.value || undefined,
      split_type: splitType.value,
      happened_at: happenedAtIso(),
    }
    if (splitType.value === 'custom') {
      // custom_amount 存对方承担的金额 = 总额 - 我承担
      const myShare = parseFloat(customAmount.value) || 0
      data.custom_amount = Math.max(data.amount - myShare, 0)
    }
    if (isEdit.value) {
      await transactionApi.update(editId.value, data)
      uni.showToast({ title: '修改成功', icon: 'success' })
    } else {
      await transactionApi.create(data)
      uni.showToast({ title: '记录成功', icon: 'success' })
    }
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e: any) { uni.showToast({ title: e.message, icon: 'none' }) }
  finally { loading.value = false }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;
.page-create { min-height: 100vh; background: $bg-page; padding: $padding-page; }
.form-group { margin-bottom: 32rpx; }
.form-label { font-size: $font-size-base; color: $text-secondary; margin-bottom: 16rpx; display: block; }
.form-hint { font-size: $font-size-sm; color: $text-tertiary; margin-top: 8rpx; display: block; }
.form-input { background: $bg-card; border: 2rpx solid $border-light; border-radius: $radius-base; padding: 24rpx 32rpx; font-size: $font-size-md; color: $text-primary; width: 100%; display: block; box-sizing: border-box; }
.form-input--amount { font-size: 44rpx; font-weight: $font-weight-bold; color: $text-primary; text-align: center; font-family: $font-family-number; }
.form-input--picker { display: flex; align-items: center; justify-content: space-between; }
.category-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; }
.category-item { display: flex; flex-direction: column; align-items: center; padding: 24rpx; background: $bg-card; border: 2rpx solid $border-light; border-radius: $radius-base; transition: all $duration-fast $ease-soft; &--active { border-color: $heart-pink; background: $heart-pink-ghost; } &__icon { font-size: 40rpx; margin-bottom: 8rpx; } &__name { font-size: $font-size-sm; color: $text-secondary; } }
.form-radio-group { display: flex; gap: 16rpx; }
.form-radio { flex: 1; height: 80rpx; display: flex; align-items: center; justify-content: center; background: $bg-card; border: 2rpx solid $border-light; border-radius: $radius-base; font-size: $font-size-base; color: $text-secondary; transition: all $duration-fast $ease-soft; &--active { border-color: $heart-pink; background: $heart-pink-ghost; color: $heart-pink; } }
.submit-btn { width: 100%; height: 96rpx; background: linear-gradient(135deg, #C8E6C9, #66BB6A); color: #fff; border: none; border-radius: $radius-full; font-size: $font-size-lg; font-weight: $font-weight-semibold; display: flex; align-items: center; justify-content: center; margin-top: 64rpx; &::after { display: none; } &[disabled] { opacity: 0.5; } }
</style>
