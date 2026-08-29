<template>
  <view class="page-detail">
    <!-- 创建模式 -->
    <view v-if="!fundId" class="create-mode">
      <!-- 标题 -->
      <view class="create-header">
        <view class="create-header__icon">
          <KdIcon name="tabler:passbook" :size="48" variant="pink" />
        </view>
        <text class="create-header__title">创建心愿存折</text>
        <text class="create-header__subtitle">为你们的共同目标储蓄</text>
      </view>

      <!-- 表单 -->
      <view class="create-form">
        <view class="form-group">
          <view class="form-group__header">
            <KdIcon name="tabler:target" :size="28" variant="pink" />
            <text class="form-group__label">基金名称</text>
          </view>
          <input class="form-input" v-model="name" placeholder="如：日本旅行基金" />
        </view>

        <view class="form-group">
          <view class="form-group__header">
            <KdIcon name="tabler:coin" :size="28" variant="pink" />
            <text class="form-group__label">目标金额</text>
          </view>
          <view class="form-input-wrap">
            <text class="form-input-wrap__prefix">¥</text>
            <input class="form-input form-input--amount" v-model="targetAmount" type="digit" placeholder="10000" />
          </view>
        </view>
      </view>

      <!-- 提交按钮 -->
      <button
        class="submit-btn"
        :class="{ 'submit-btn--disabled': !name || !targetAmount || loading }"
        :disabled="!name || !targetAmount || loading"
        @tap="createFund"
      >
        <KdIcon v-if="!loading" name="tabler:passbook" :size="32" color="#fff" />
        <view v-else class="submit-btn__loading" />
        <text class="submit-btn__text">{{ loading ? '创建中...' : '创建存折' }}</text>
      </button>
    </view>

    <!-- 详情模式 -->
    <view v-else-if="fund" class="detail-mode">
      <!-- 存折头部 -->
      <view class="passbook-header">
        <view class="passbook-header__icon">
          <KdIcon :name="fund.icon?.startsWith('tabler:') ? fund.icon : 'tabler:target'" :size="48" variant="pink" />
        </view>
        <text class="passbook-header__name">{{ fund.name }}</text>
        <view class="passbook-header__amounts">
          <view class="passbook-header__amount">
            <text class="passbook-header__amount-label">已存</text>
            <text class="passbook-header__amount-value">¥{{ fund.current_amount.toFixed(0) }}</text>
          </view>
          <view class="passbook-header__divider" />
          <view class="passbook-header__amount">
            <text class="passbook-header__amount-label">目标</text>
            <text class="passbook-header__amount-value">¥{{ fund.target_amount.toFixed(0) }}</text>
          </view>
        </view>
        <view class="passbook-header__progress">
          <view class="passbook-header__bar">
            <view class="passbook-header__bar-fill" :style="{ width: Math.min(fund.progress, 100) + '%' }">
              <view class="passbook-header__bar-glow" />
            </view>
          </view>
          <text class="passbook-header__percent">{{ Math.min(fund.progress, 100).toFixed(0) }}%</text>
        </view>
        <view class="passbook-header__deco">
          <view class="passbook-header__line" />
          <text class="passbook-header__line-text">咔哒 · 心愿存折</text>
          <view class="passbook-header__line" />
        </view>
      </view>

      <!-- 资金操作 -->
      <view class="contribute-section">
        <view class="contribute-section__header">
          <KdIcon name="tabler:arrows-up-down" :size="28" variant="pink" />
          <text class="contribute-section__title">资金操作</text>
        </view>

        <view class="contribute-form">
          <view class="contribute-form__row">
            <view class="contribute-form__input-wrap">
              <text class="contribute-form__prefix">¥</text>
              <input class="contribute-form__input" v-model="amount" type="digit" placeholder="金额" />
            </view>
          </view>
          <input class="contribute-form__note" v-model="note" placeholder="备注（可选）" />
          <view class="contribute-form__btns">
            <button class="contribute-btn contribute-btn--deposit" :disabled="!amount || loading" @tap="contribute">
              <KdIcon name="tabler:arrow-up" :size="28" color="#fff" />
              <text>投入</text>
            </button>
            <button class="contribute-btn contribute-btn--withdraw" :disabled="!amount || loading" @tap="withdraw">
              <KdIcon name="tabler:arrow-down" :size="28" />
              <text>取出</text>
            </button>
          </view>
        </view>
      </view>

      <!-- 操作记录 -->
      <view class="history-section">
        <view class="history-section__header">
          <KdIcon name="tabler:history" :size="28" variant="pink" />
          <text class="history-section__title">操作记录</text>
          <text class="history-section__count">{{ contributions.length }} 笔</text>
        </view>

        <view v-if="!contributions.length" class="history-empty">
          <text class="history-empty__text">暂无记录</text>
        </view>

        <view v-else class="history-list">
          <view
            v-for="(c, index) in contributions"
            :key="c.id"
            class="history-item"
            :style="{ animationDelay: `${index * 50}ms` }"
            @longpress="deleteContribution(c)"
          >
            <view class="history-item__icon" :class="c.type === 'withdraw' ? 'history-item__icon--withdraw' : 'history-item__icon--deposit'">
              <KdIcon :name="c.type === 'withdraw' ? 'tabler:arrow-down' : 'tabler:arrow-up'" :size="24" />
            </view>
            <view class="history-item__info">
              <text class="history-item__amount" :class="c.type === 'withdraw' ? 'history-item__amount--withdraw' : 'history-item__amount--deposit'">
                {{ c.type === 'withdraw' ? '-' : '+' }}¥{{ c.amount.toFixed(0) }}
              </text>
              <text v-if="c.note" class="history-item__note">{{ c.note }}</text>
            </view>
            <text class="history-item__date">{{ formatDate(c.created_at) }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>

  <KdDialog
    :visible="showDeleteConfirm"
    title="撤销记录"
    :content="`确定要撤销这笔${deleteTargetType}记录吗？`"
    confirm-color="#EF5350"
    @close="showDeleteConfirm = false"
    @confirm="onDeleteConfirm"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { fundApi, type Fund, type Contribution } from '@/api/fund'
import KdIcon from '@/components/KdIcon.vue'
import KdDialog from '@/components/KdDialog.vue'

const fundId = ref('')
const fund = ref<Fund | null>(null)
const contributions = ref<Contribution[]>([])
const name = ref('')
const targetAmount = ref('')
const amount = ref('')
const note = ref('')
const loading = ref(false)
const showDeleteConfirm = ref(false)
const deleteTargetId = ref('')
const deleteTargetType = ref('')

const formatDate = (iso: string) => {
  const d = new Date(iso)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

onLoad((query: any) => { if (query?.id) fundId.value = query.id })

const loadData = async () => {
  if (!fundId.value) return
  try {
    const [list, contribs] = await Promise.all([fundApi.list(), fundApi.contributions(fundId.value)])
    fund.value = list.find(f => f.id === fundId.value) || null
    contributions.value = contribs
  } catch {}
}

const createFund = async () => {
  const target = parseFloat(targetAmount.value)
  if (isNaN(target) || target <= 0) {
    uni.showToast({ title: '目标金额必须大于 0', icon: 'none' })
    return
  }
  loading.value = true
  try {
    await fundApi.create({ name: name.value, target_amount: target })
    uni.showToast({ title: '创建成功', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e: any) { uni.showToast({ title: e.message, icon: 'none' }) }
  finally { loading.value = false }
}

const contribute = async () => {
  const amt = parseFloat(amount.value)
  if (isNaN(amt) || amt <= 0) {
    uni.showToast({ title: '金额必须大于 0', icon: 'none' })
    return
  }
  loading.value = true
  try {
    await fundApi.contribute(fundId.value, amt, note.value || undefined)
    uni.showToast({ title: '投入成功', icon: 'success' })
    amount.value = ''; note.value = ''
    await loadData()
  } catch (e: any) { uni.showToast({ title: e.message, icon: 'none' }) }
  finally { loading.value = false }
}

const withdraw = async () => {
  const amt = parseFloat(amount.value)
  if (isNaN(amt) || amt <= 0) {
    uni.showToast({ title: '金额必须大于 0', icon: 'none' })
    return
  }
  loading.value = true
  try {
    await fundApi.withdraw(fundId.value, amt, note.value || undefined)
    uni.showToast({ title: '取出成功', icon: 'success' })
    amount.value = ''; note.value = ''
    await loadData()
  } catch (e: any) { uni.showToast({ title: e.message, icon: 'none' }) }
  finally { loading.value = false }
}

const deleteContribution = (c: Contribution) => {
  deleteTargetId.value = c.id
  deleteTargetType.value = c.type === 'withdraw' ? '取出' : '投入'
  showDeleteConfirm.value = true
}
const onDeleteConfirm = async () => {
  try {
    await fundApi.deleteContribution(fundId.value, deleteTargetId.value)
    uni.showToast({ title: '已撤销', icon: 'success' })
    await loadData()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-detail {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF8E1 0%, #FFF3E0 30%, #FFF0F2 100%);
  padding: 24rpx 32rpx;
  padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
}

// ========== 创建模式 ==========
.create-header {
  text-align: center;
  padding: 32rpx 0 48rpx;

  &__icon {
    width: 100rpx;
    height: 100rpx;
    background: #FFF3E0;
    border-radius: 28rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 24rpx;
    box-shadow: 0 4rpx 16rpx rgba(255, 152, 0, 0.15);
  }

  &__title {
    font-size: 36rpx;
    font-weight: 700;
    color: $text-primary;
    display: block;
    margin-bottom: 8rpx;
  }

  &__subtitle {
    font-size: 26rpx;
    color: $text-tertiary;
    display: block;
  }
}

.create-form {
  margin-bottom: 48rpx;
}

.form-group {
  margin-bottom: 32rpx;

  &__header {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 16rpx;
  }

  &__label {
    font-size: 28rpx;
    font-weight: 500;
    color: $text-primary;
  }
}

.form-input {
  background: #fff;
  border: 2rpx solid #FFE0B2;
  border-radius: 16rpx;
  padding: 24rpx 28rpx;
  font-size: 28rpx;
  color: $text-primary;
  width: 100%;
  display: block;
  box-sizing: border-box;
  transition: border-color 0.2s ease;

  &:focus {
    border-color: #FFB74D;
  }
}

.form-input-wrap {
  display: flex;
  align-items: center;
  background: #fff;
  border: 2rpx solid #FFE0B2;
  border-radius: 16rpx;
  padding: 0 28rpx;
  transition: border-color 0.2s ease;

  &:focus-within {
    border-color: #FFB74D;
  }

  &__prefix {
    font-size: 32rpx;
    font-weight: 600;
    color: #F57C00;
    margin-right: 12rpx;
  }
}

.form-input--amount {
  border: none;
  padding: 24rpx 0;
  background: transparent;
}

.submit-btn {
  width: 100%;
  height: 104rpx;
  background: linear-gradient(135deg, #FFB74D 0%, #FF9800 100%);
  color: #fff;
  border: none;
  border-radius: 52rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 8rpx 24rpx rgba(255, 152, 0, 0.35);
  transition: all 0.2s ease;
  &::after { display: none; }

  &:active:not(&--disabled) {
    transform: scale(0.96);
  }

  &--disabled {
    opacity: 0.5;
    box-shadow: none;
  }

  &__text {
    font-size: 32rpx;
    font-weight: 600;
  }

  &__loading {
    width: 36rpx;
    height: 36rpx;
    border: 4rpx solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// ========== 详情模式 ==========
.passbook-header {
  background: #fff;
  border-radius: 24rpx;
  padding: 36rpx;
  margin-bottom: 32rpx;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    0 8rpx 24rpx rgba(255, 152, 0, 0.08);

  &__icon {
    width: 96rpx;
    height: 96rpx;
    background: #FFF3E0;
    border-radius: 24rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 20rpx;
  }

  &__name {
    font-size: 36rpx;
    font-weight: 700;
    color: $text-primary;
    display: block;
    text-align: center;
    margin-bottom: 24rpx;
  }

  &__amounts {
    display: flex;
    align-items: center;
    justify-content: space-around;
    padding: 20rpx 0;
    margin-bottom: 24rpx;
    background: #FFF8E1;
    border-radius: 16rpx;
  }

  &__amount {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  &__amount-label {
    font-size: 22rpx;
    color: $text-tertiary;
    margin-bottom: 8rpx;
  }

  &__amount-value {
    font-size: 36rpx;
    font-weight: 700;
    color: #F57C00;
    font-family: $font-family-number;
  }

  &__divider {
    width: 2rpx;
    height: 48rpx;
    background: #FFE0B2;
  }

  &__progress {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 20rpx;
  }

  &__bar {
    flex: 1;
    height: 20rpx;
    background: #FFF3E0;
    border-radius: 10rpx;
    overflow: hidden;
  }

  &__bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #FFB74D 0%, #FF9800 50%, #F57C00 100%);
    border-radius: 10rpx;
    transition: width 0.6s ease;
    position: relative;
  }

  &__bar-glow {
    position: absolute;
    top: 0;
    right: 0;
    width: 24rpx;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4));
    border-radius: 0 10rpx 10rpx 0;
  }

  &__percent {
    font-size: 32rpx;
    font-weight: 700;
    color: #F57C00;
    font-family: $font-family-number;
    flex-shrink: 0;
    min-width: 80rpx;
    text-align: right;
  }

  &__deco {
    display: flex;
    align-items: center;
    gap: 16rpx;
    padding-top: 16rpx;
    border-top: 2rpx dashed #FFE0B2;
  }

  &__line {
    flex: 1;
    height: 2rpx;
    background: #FFE0B2;
  }

  &__line-text {
    font-size: 18rpx;
    color: #FFCC80;
    letter-spacing: 2rpx;
  }
}

// ========== 资金操作 ==========
.contribute-section {
  margin-bottom: 40rpx;

  &__header {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 20rpx;
  }

  &__title {
    font-size: 28rpx;
    font-weight: 600;
    color: $text-primary;
  }
}

.contribute-form {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);

  &__row {
    margin-bottom: 16rpx;
  }

  &__input-wrap {
    display: flex;
    align-items: center;
    background: #FFF8E1;
    border: 2rpx solid #FFE0B2;
    border-radius: 12rpx;
    padding: 0 20rpx;
  }

  &__prefix {
    font-size: 28rpx;
    font-weight: 600;
    color: #F57C00;
    margin-right: 8rpx;
  }

  &__input {
    flex: 1;
    background: transparent;
    border: none;
    padding: 20rpx 0;
    font-size: 28rpx;
    color: $text-primary;
  }

  &__note {
    background: #FFF8E1;
    border: 2rpx solid #FFE0B2;
    border-radius: 12rpx;
    padding: 20rpx;
    font-size: 26rpx;
    color: $text-primary;
    margin-bottom: 20rpx;
  }

  &__btns {
    display: flex;
    gap: 16rpx;
  }
}

.contribute-btn {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  font-size: 28rpx;
  font-weight: 600;
  border: none;
  transition: all 0.2s ease;
  &::after { display: none; }

  &:active {
    transform: scale(0.96);
  }

  &--deposit {
    background: linear-gradient(135deg, #FFB74D 0%, #FF9800 100%);
    color: #fff;
    box-shadow: 0 4rpx 16rpx rgba(255, 152, 0, 0.3);
  }

  &--withdraw {
    background: #fff;
    color: #F57C00;
    border: 2rpx solid #FFB74D;
  }

  &[disabled] {
    opacity: 0.5;
    box-shadow: none;
  }
}

// ========== 操作记录 ==========
.history-section {
  &__header {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 20rpx;
  }

  &__title {
    font-size: 28rpx;
    font-weight: 600;
    color: $text-primary;
    flex: 1;
  }

  &__count {
    font-size: 22rpx;
    color: $text-tertiary;
  }
}

.history-empty {
  text-align: center;
  padding: 48rpx 0;

  &__text {
    font-size: 26rpx;
    color: $text-tertiary;
  }
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx;
  opacity: 0;
  animation: fadeIn 0.3s ease forwards;

  &__icon {
    width: 48rpx;
    height: 48rpx;
    border-radius: 12rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    &--deposit {
      background: #E8F5E9;
      color: #4CAF50;
    }

    &--withdraw {
      background: #FFEBEE;
      color: #EF5350;
    }
  }

  &__info {
    flex: 1;
    min-width: 0;
  }

  &__amount {
    font-size: 28rpx;
    font-weight: 600;
    display: block;

    &--deposit {
      color: #4CAF50;
    }

    &--withdraw {
      color: #EF5350;
    }
  }

  &__note {
    font-size: 22rpx;
    color: $text-tertiary;
    display: block;
    margin-top: 4rpx;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__date {
    font-size: 22rpx;
    color: $text-tertiary;
    flex-shrink: 0;
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8rpx); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
