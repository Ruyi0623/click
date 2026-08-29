# 💕 咔哒 · UI 设计系统

> **设计理念**：让每一帧都充满爱的温度  
> **设计风格**：Soft Warmth — 柔和温暖，如同晨曦中的拥抱  
> **目标**：打造情侣间最温馨的数字记忆空间

---

## 一、设计哲学

### 1.1 核心原则

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   "不是冷冰冰的工具，而是有温度的陪伴"                          │
│                                                             │
│   🎨 视觉语言：柔和渐变 + 圆润形态 + 呼吸动效                  │
│   💫 情感表达：每一处微交互都在说"我爱你"                        │
│   🌸 细节哲学：让用户在不经意间感受到用心                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 设计关键词

| 关键词 | 视觉表现 | 情感映射 |
|--------|----------|----------|
| 温暖 | 暖色调渐变 | 被爱包围的感觉 |
| 柔和 | 大圆角 + 模糊阴影 | 亲密无间 |
| 呼吸 | 轻微浮动动画 | 心跳同步 |
| 惊喜 | 彩蛋微交互 | 爱的小确幸 |
| 珍藏 | 精致细节 | 每一刻都值得记录 |

---

## 二、色彩系统

### 2.1 主色调 — 心动粉

```scss
// 不是普通的粉色，而是带着心跳温度的粉
$heart-pink: #FF6B8A;           // 主色 — 心动瞬间
$heart-pink-light: #FF8FA3;     // 浅色 — 温柔触碰
$heart-pink-pale: #FFD6DE;      // 极浅 — 晨曦薄雾
$heart-pink-ghost: #FFF0F2;     // 幽灵 — 页面背景
$heart-pink-dark: #E8527A;      // 深色 — 深情凝视
```

### 2.2 辅助色系

```scss
// 暖阳金 — 纪念日、重要时刻
$sunrise-gold: #FFB347;
$sunrise-gold-light: #FFD699;
$sunrise-gold-pale: #FFF3E0;

// 薰衣草紫 — 梦幻、时光胶囊
$lavender: #B39DDB;
$lavender-light: #D1C4E9;
$lavender-pale: #F3E5F5;

// 薄荷绿 — 心愿、成长
$mint: #80CBC4;
$mint-light: #B2DFDB;
$mint-pale: #E0F2F1;

// 天空蓝 — 信任、平静
$sky: #81D4FA;
$sky-light: #B3E5FC;
$sky-pale: #E1F5FE;

// 珊瑚橘 — 活力、热情
$coral: #FF8A80;
$coral-light: #FFCCBC;
$coral-pale: #FBE9E7;
```

### 2.3 中性色

```scss
// 文字色 — 不用纯黑，更柔和
$text-primary: #2D2D3F;      // 主要文字 — 深夜紫灰
$text-secondary: #6B6B80;    // 次要文字 — 薄暮灰
$text-tertiary: #9E9EB0;     // 辅助文字 — 晨雾灰
$text-inverse: #FFFFFF;      // 反色文字

// 背景色
$bg-page: #FFF8F9;           // 页面背景 — 微微泛粉的暖白
$bg-card: #FFFFFF;           // 卡片背景
$bg-elevated: #FFFFFF;       // 浮层背景
$bg-mask: rgba(45, 45, 63, 0.5); // 遮罩

// 边框色
$border-light: #FFE4E8;     // 浅边框
$border-normal: #FFD0D8;    // 常规边框
```

### 2.4 功能色

```scss
$success: #66BB6A;           // 成功 — 生机绿
$warning: #FFB74D;           // 警告 — 暖阳橙
$error: #EF5350;             // 错误 — 玫瑰红
$info: #42A5F5;              // 信息 — 天空蓝
```

### 2.5 渐变色

```scss
// 心动渐变 — 按钮、强调元素
$gradient-heart: linear-gradient(135deg, #FF6B8A 0%, #FF8FA3 100%);

// 晨曦渐变 — 背景、卡片
$gradient-dawn: linear-gradient(180deg, #FFF0F2 0%, #FFFFFF 100%);

// 日落渐变 — 特殊时刻
$gradient-sunset: linear-gradient(135deg, #FFB347 0%, #FF6B8A 100%);

// 星空渐变 — 时光胶囊
$gradient-starry: linear-gradient(135deg, #B39DDB 0%, #81D4FA 100%);

// 梦幻渐变 — 纪念日
$gradient-dream: linear-gradient(135deg, #FFD6DE 0%, #F3E5F5 100%);
```

---

## 三、字体系统

### 3.1 字体选择

```scss
// 主字体 — 优雅清晰
$font-family-base: 'PingFang SC', 'Helvetica Neue', sans-serif;

// 数字字体 — 恋爱天数等重要数字
$font-family-number: 'DIN Alternate', 'Roboto', monospace;

// 装饰字体 — 标题、特殊文案
// 注意：小程序中需要使用系统字体，这里定义的是优先级
$font-family-display: 'PingFang SC', sans-serif;
```

### 3.2 字号规范

```scss
// 基于 2x 设计稿，使用 rpx 单位
$font-size-xs: 20rpx;        // 10px — 标签、角标
$font-size-sm: 24rpx;        // 12px — 辅助文字
$font-size-base: 28rpx;      // 14px — 正文
$font-size-md: 32rpx;        // 16px — 小标题
$font-size-lg: 36rpx;        // 18px — 标题
$font-size-xl: 44rpx;        // 22px — 大标题
$font-size-xxl: 56rpx;       // 28px — 超大标题
$font-size-display: 72rpx;   // 36px — 展示数字
$font-size-hero: 96rpx;      // 48px — 英雄数字（恋爱天数）
```

### 3.3 字重规范

```scss
$font-weight-regular: 400;   // 正文
$font-weight-medium: 500;    // 标题
$font-weight-semibold: 600;  // 强调
$font-weight-bold: 700;      // 大标题
```

### 3.4 行高规范

```scss
$line-height-tight: 1.2;     // 标题
$line-height-normal: 1.5;    // 正文
$line-height-relaxed: 1.8;   // 长文本
```

---

## 四、间距系统

### 4.1 基础间距

```scss
// 基于 8px 网格
$space-xs: 8rpx;             // 4px — 极小间距
$space-sm: 16rpx;            // 8px — 小间距
$space-md: 24rpx;            // 12px — 中间距
$space-base: 32rpx;          // 16px — 基础间距
$space-lg: 48rpx;            // 24px — 大间距
$space-xl: 64rpx;            // 32px — 超大间距
$space-xxl: 96rpx;           // 48px — 巨大间距
```

### 4.2 组件间距

```scss
// 卡片内边距
$padding-card: 32rpx;

// 页面边距
$padding-page: 32rpx;

// 列表项间距
$gap-list: 24rpx;

// 网格间距
$gap-grid: 20rpx;
```

---

## 五、圆角系统

### 5.1 圆角规范

```scss
$radius-xs: 8rpx;            // 4px — 小元素（标签、角标）
$radius-sm: 12rpx;           // 6px — 按钮、输入框
$radius-md: 16rpx;           // 8px — 小卡片
$radius-base: 24rpx;         // 12px — 常规卡片
$radius-lg: 32rpx;           // 16px — 大卡片
$radius-xl: 48rpx;           // 24px — 特殊卡片
$radius-full: 9999rpx;       // 圆形 — 头像、圆形按钮
```

### 5.2 形态语言

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   大圆角 = 包容、温暖、无棱角的爱                               │
│   圆形 = 完整、永恒、无限循环的陪伴                             │
│   胶囊形 = 柔软、可爱、像棉花糖一样                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 六、阴影系统

### 6.1 阴影层级

```scss
// 不用生硬的黑色阴影，用主题色的柔和阴影
$shadow-sm: 0 2rpx 8rpx rgba(255, 107, 138, 0.08);    // 轻微悬浮
$shadow-md: 0 4rpx 16rpx rgba(255, 107, 138, 0.12);   // 卡片悬浮
$shadow-lg: 0 8rpx 32rpx rgba(255, 107, 138, 0.16);   // 强调悬浮
$shadow-xl: 0 16rpx 48rpx rgba(255, 107, 138, 0.20);  // 弹窗、浮层

// 特殊阴影 — 带颜色的光晕
$shadow-glow: 0 0 24rpx rgba(255, 107, 138, 0.30);    // 按钮光晕
$shadow-glow-lg: 0 0 48rpx rgba(255, 107, 138, 0.25); // 大光晕
```

### 6.2 阴影使用场景

| 元素 | 阴影 | 效果 |
|------|------|------|
| 普通卡片 | `$shadow-sm` | 轻微立体感 |
| 悬浮卡片 | `$shadow-md` | 明显层次 |
| 主按钮 | `$shadow-glow` | 发光吸引 |
| 弹窗 | `$shadow-xl` | 浮层效果 |
| 底部导航 | `$shadow-lg` | 分离内容 |

---

## 七、动画系统

### 7.1 动画哲学

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   "动画不是装饰，而是情感的延伸"                                │
│                                                             │
│   💓 心跳 — 微微的呼吸感，让界面活起来                          │
│   🌊 流动 — 元素如水般顺滑地出现和消失                          │
│   ✨ 惊喜 — 不经意间的微交互，让爱情充满小确幸                    │
│   🎭 情绪 — 不同场景有不同的情绪动画                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 基础动画

```scss
// 时间曲线 — 柔和自然
$ease-soft: cubic-bezier(0.25, 0.1, 0.25, 1);
$ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
$ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
$ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);

// 时长
$duration-fast: 150ms;       // 快速响应
$duration-normal: 300ms;     // 常规过渡
$duration-slow: 500ms;       // 缓慢变化
$duration-slower: 800ms;     // 强调动画
```

### 7.3 核心动画库

#### 心跳动画 — 恋爱天数、喜欢按钮

```scss
@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  14% { transform: scale(1.05); }
  28% { transform: scale(1); }
  42% { transform: scale(1.05); }
  70% { transform: scale(1); }
}

.animate-heartbeat {
  animation: heartbeat 1.5s ease-in-out infinite;
}
```

#### 呼吸动画 — 强调元素、悬浮提示

```scss
@keyframes breathe {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.02);
  }
}

.animate-breathe {
  animation: breathe 3s ease-in-out infinite;
}
```

#### 漂浮动画 — 装饰元素、空状态

```scss
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-12rpx);
  }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}
```

#### 闪烁动画 — 星星、胶囊光效

```scss
@keyframes twinkle {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.8);
  }
}

.animate-twinkle {
  animation: twinkle 2s ease-in-out infinite;
}
```

#### 渐入动画 — 元素出现

```scss
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(24rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp $duration-normal $ease-soft forwards;
}

// 延迟类 — 列表项依次出现
.delay-1 { animation-delay: 50ms; }
.delay-2 { animation-delay: 100ms; }
.delay-3 { animation-delay: 150ms }
```

#### 弹性出现 — 按钮、卡片

```scss
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-scale-in {
  animation: scaleIn $duration-normal $ease-spring forwards;
}
```

#### 脉冲光晕 — 重要按钮

```scss
@keyframes pulseGlow {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 107, 138, 0.4);
  }
  70% {
    box-shadow: 0 0 0 20rpx rgba(255, 107, 138, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 107, 138, 0);
  }
}

.animate-pulse-glow {
  animation: pulseGlow 2s infinite;
}
```

#### 摇晃动画 — 删除确认、错误提示

```scss
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-4rpx); }
  20%, 40%, 60%, 80% { transform: translateX(4rpx); }
}

.animate-shake {
  animation: shake $duration-normal ease;
}
```

#### 旋转出现 — 加载、刷新

```scss
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
```

### 7.4 场景动画

#### 页面进入 — 恋爱天数展示

```scss
@keyframes revealDays {
  0% {
    opacity: 0;
    transform: scale(0.5) rotate(-10deg);
    filter: blur(10px);
  }
  60% {
    opacity: 1;
    transform: scale(1.1) rotate(2deg);
    filter: blur(0);
  }
  100% {
    opacity: 1;
    transform: scale(1) rotate(0);
    filter: blur(0);
  }
}

.animate-reveal-days {
  animation: revealDays 800ms $ease-spring forwards;
}
```

#### 心情选择 — Emoji 弹出

```scss
@keyframes emojiPop {
  0% {
    opacity: 0;
    transform: scale(0) rotate(-180deg);
  }
  50% {
    transform: scale(1.2) rotate(10deg);
  }
  100% {
    opacity: 1;
    transform: scale(1) rotate(0);
  }
}

.animate-emoji-pop {
  animation: emojiPop $duration-slow $ease-bounce forwards;
}
```

#### 相册照片 — 依次展现

```scss
@keyframes photoReveal {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20rpx);
    filter: blur(4px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
    filter: blur(0);
  }
}

.animate-photo-reveal {
  animation: photoReveal $duration-slow $ease-soft forwards;
}
```

#### 时光胶囊 — 开启动画

```scss
@keyframes capsuleOpen {
  0% {
    transform: scale(1) rotate(0);
    box-shadow: $shadow-md;
  }
  30% {
    transform: scale(1.1) rotate(-5deg);
    box-shadow: $shadow-glow-lg;
  }
  60% {
    transform: scale(0.95) rotate(3deg);
  }
  100% {
    transform: scale(1) rotate(0);
    box-shadow: $shadow-md;
  }
}

.animate-capsule-open {
  animation: capsuleOpen 600ms $ease-bounce forwards;
}
```

#### 配对成功 — 爆炸心形

```scss
@keyframes heartExplode {
  0% {
    opacity: 1;
    transform: scale(0);
  }
  50% {
    opacity: 1;
    transform: scale(1.5);
  }
  100% {
    opacity: 0;
    transform: scale(2);
  }
}

.animate-heart-explode {
  animation: heartExplode 800ms $ease-soft forwards;
}
```

---

## 八、组件样式

### 8.1 按钮系统

```scss
// 主按钮 — 心动渐变 + 光晕
.btn-primary {
  background: $gradient-heart;
  color: $text-inverse;
  border: none;
  border-radius: $radius-full;
  height: 96rpx;
  padding: 0 64rpx;
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  box-shadow: $shadow-glow;
  transition: all $duration-normal $ease-soft;
  
  &:active {
    transform: scale(0.96);
    box-shadow: none;
  }
}

// 次按钮 — 透明 + 边框
.btn-secondary {
  background: transparent;
  color: $heart-pink;
  border: 2rpx solid $heart-pink;
  border-radius: $radius-full;
  height: 96rpx;
  padding: 0 64rpx;
  font-size: $font-size-lg;
  font-weight: $font-weight-medium;
  
  &:active {
    background: $heart-pink-ghost;
  }
}

// 文字按钮 — 无边框
.btn-text {
  background: transparent;
  color: $heart-pink;
  border: none;
  height: 80rpx;
  padding: 0 32rpx;
  font-size: $font-size-base;
  
  &:active {
    opacity: 0.7;
  }
}

// 图标按钮 — 圆形
.btn-icon {
  width: 88rpx;
  height: 88rpx;
  border-radius: $radius-full;
  background: $bg-card;
  box-shadow: $shadow-sm;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:active {
    transform: scale(0.92);
  }
}

// 浮动操作按钮 — 页面主操作
.fab {
  position: fixed;
  right: 40rpx;
  bottom: 200rpx;
  width: 112rpx;
  height: 112rpx;
  border-radius: $radius-full;
  background: $gradient-heart;
  box-shadow: $shadow-glow-lg;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  
  // 呼吸光效
  &::after {
    content: '';
    position: absolute;
    inset: -8rpx;
    border-radius: $radius-full;
    background: $gradient-heart;
    opacity: 0.3;
    animation: breathe 3s ease-in-out infinite;
    z-index: -1;
  }
  
  &:active {
    transform: scale(0.9);
  }
}
```

### 8.2 卡片系统

```scss
// 基础卡片 — 柔和阴影
.card {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: $padding-card;
  box-shadow: $shadow-sm;
  transition: all $duration-normal $ease-soft;
}

// 悬浮卡片 — 鼠标/触摸反馈
.card-hover {
  @extend .card;
  
  &:active {
    transform: translateY(2rpx);
    box-shadow: none;
  }
}

// 强调卡片 — 带渐变边框
.card-accent {
  @extend .card;
  position: relative;
  border: 2rpx solid transparent;
  background-clip: padding-box;
  
  &::before {
    content: '';
    position: absolute;
    inset: -2rpx;
    border-radius: inherit;
    background: $gradient-heart;
    z-index: -1;
    opacity: 0.1;
  }
}

// 玻璃卡片 — 毛玻璃效果
.card-glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: $radius-lg;
  padding: $padding-card;
  border: 1rpx solid rgba(255, 255, 255, 0.5);
}
```

### 8.3 输入框

```scss
.input-field {
  background: $bg-page;
  border: 2rpx solid $border-light;
  border-radius: $radius-base;
  padding: 24rpx 32rpx;
  font-size: $font-size-base;
  color: $text-primary;
  transition: all $duration-normal $ease-soft;
  
  &:focus {
    border-color: $heart-pink-light;
    box-shadow: 0 0 0 4rpx rgba(255, 107, 138, 0.1);
  }
  
  &::placeholder {
    color: $text-tertiary;
  }
}

// 带图标输入框
.input-with-icon {
  position: relative;
  
  .input-icon {
    position: absolute;
    left: 32rpx;
    top: 50%;
    transform: translateY(-50%);
    color: $text-tertiary;
  }
  
  .input-field {
    padding-left: 88rpx;
  }
}
```

### 8.4 标签

```scss
// 基础标签
.tag {
  display: inline-flex;
  align-items: center;
  padding: 8rpx 24rpx;
  border-radius: $radius-full;
  font-size: $font-size-sm;
  font-weight: $font-weight-medium;
}

// 主题标签
.tag-pink {
  @extend .tag;
  background: $heart-pink-pale;
  color: $heart-pink-dark;
}

.tag-gold {
  @extend .tag;
  background: $sunrise-gold-pale;
  color: $sunrise-gold;
}

.tag-lavender {
  @extend .tag;
  background: $lavender-pale;
  color: $lavender;
}

.tag-mint {
  @extend .tag;
  background: $mint-pale;
  color: $mint;
}
```

### 8.5 头像组件

```scss
// 单个头像
.avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: $radius-full;
  border: 4rpx solid $bg-card;
  box-shadow: $shadow-sm;
  overflow: hidden;
  
  image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

// 情侣头像 — 重叠排列
.couple-avatars {
  display: flex;
  align-items: center;
  
  .avatar:first-child {
    z-index: 2;
  }
  
  .avatar:last-child {
    margin-left: -24rpx;
    z-index: 1;
  }
  
  // 中间的爱心
  .heart-divider {
    width: 48rpx;
    height: 48rpx;
    margin: 0 -12rpx;
    z-index: 3;
    background: $gradient-heart;
    border-radius: $radius-full;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: $shadow-glow;
  }
}
```

### 8.6 列表项

```scss
.list-item {
  display: flex;
  align-items: center;
  padding: 32rpx;
  background: $bg-card;
  border-radius: $radius-base;
  margin-bottom: $gap-list;
  transition: all $duration-fast $ease-soft;
  
  &:active {
    background: $bg-page;
  }
  
  .list-item-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: $radius-base;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 24rpx;
    font-size: 40rpx;
  }
  
  .list-item-content {
    flex: 1;
    
    .list-item-title {
      font-size: $font-size-md;
      color: $text-primary;
      font-weight: $font-weight-medium;
    }
    
    .list-item-desc {
      font-size: $font-size-sm;
      color: $text-secondary;
      margin-top: 8rpx;
    }
  }
  
  .list-item-extra {
    margin-left: 24rpx;
  }
}
```

### 8.7 空状态

```scss
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 64rpx;
  
  .empty-illustration {
    width: 240rpx;
    height: 240rpx;
    margin-bottom: 48rpx;
    animation: float 3s ease-in-out infinite;
  }
  
  .empty-title {
    font-size: $font-size-lg;
    color: $text-primary;
    font-weight: $font-weight-semibold;
    margin-bottom: 16rpx;
  }
  
  .empty-desc {
    font-size: $font-size-base;
    color: $text-secondary;
    text-align: center;
    line-height: $line-height-relaxed;
    margin-bottom: 48rpx;
  }
}
```

---

## 九、页面示例

### 9.1 首页 — 恋爱天数展示

```vue
<template>
  <view class="page-home">
    <!-- 背景装饰 -->
    <view class="bg-decoration">
      <view class="bg-circle bg-circle-1"></view>
      <view class="bg-circle bg-circle-2"></view>
      <view class="bg-hearts">
        <text v-for="i in 6" :key="i" class="floating-heart">💕</text>
      </view>
    </view>
    
    <!-- 恋爱天数卡片 -->
    <view class="days-card animate-reveal-days">
      <view class="days-header">
        <view class="couple-avatars">
          <image class="avatar" :src="myAvatar" />
          <view class="heart-divider">
            <text class="heart-icon">❤️</text>
          </view>
          <image class="avatar" :src="partnerAvatar" />
        </view>
      </view>
      
      <view class="days-body">
        <text class="days-label">我们已经在一起</text>
        <view class="days-number-wrapper">
          <text class="days-number animate-heartbeat">{{ daysTogether }}</text>
          <text class="days-unit">天</text>
        </view>
        <text class="days-since">{{ startDate }} 至今</text>
      </view>
      
      <view class="days-footer">
        <view class="mood-item" @tap="goToMood">
          <text class="mood-emoji">{{ myMood }}</text>
          <text class="mood-name">我</text>
        </view>
        <view class="mood-divider"></view>
        <view class="mood-item" @tap="goToMood">
          <text class="mood-emoji">{{ partnerMood }}</text>
          <text class="mood-name">TA</text>
        </view>
      </view>
    </view>
    
    <!-- 功能入口网格 -->
    <view class="feature-grid">
      <view 
        v-for="(item, index) in features" 
        :key="item.id"
        class="feature-item animate-fade-in-up"
        :style="{ animationDelay: `${index * 50}ms` }"
        @tap="navigateTo(item.path)"
      >
        <view class="feature-icon" :style="{ background: item.gradient }">
          <text>{{ item.icon }}</text>
        </view>
        <text class="feature-name">{{ item.name }}</text>
        <text v-if="item.badge" class="feature-badge">{{ item.badge }}</text>
      </view>
    </view>
    
    <!-- 即将到来 -->
    <view class="section" v-if="upcoming.length">
      <view class="section-header">
        <text class="section-title">📅 即将到来</text>
        <text class="section-more" @tap="goToAnniversary">查看全部</text>
      </view>
      <view class="upcoming-list">
        <view 
          v-for="(item, index) in upcoming" 
          :key="item.id"
          class="upcoming-item animate-fade-in-up"
          :style="{ animationDelay: `${index * 80}ms` }"
        >
          <view class="upcoming-icon">{{ item.icon }}</view>
          <view class="upcoming-info">
            <text class="upcoming-title">{{ item.title }}</text>
            <text class="upcoming-date">{{ item.date }}</text>
          </view>
          <view class="upcoming-countdown">
            <text class="countdown-number">{{ item.daysUntil }}</text>
            <text class="countdown-unit">天后</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 最近心情 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">💭 心情日记</text>
      </view>
      <view class="mood-calendar">
        <!-- 最近7天心情展示 -->
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.page-home {
  min-height: 100vh;
  background: $bg-page;
  padding: 0 $padding-page $space-xxl;
  position: relative;
  overflow: hidden;
}

// 背景装饰
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 600rpx;
  background: $gradient-dawn;
  border-radius: 0 0 96rpx 96rpx;
  z-index: 0;
  
  .bg-circle {
    position: absolute;
    border-radius: $radius-full;
    opacity: 0.1;
  }
  
  .bg-circle-1 {
    width: 300rpx;
    height: 300rpx;
    background: $heart-pink;
    top: -50rpx;
    right: -50rpx;
    animation: float 6s ease-in-out infinite;
  }
  
  .bg-circle-2 {
    width: 200rpx;
    height: 200rpx;
    background: $lavender;
    top: 100rpx;
    left: -30rpx;
    animation: float 8s ease-in-out infinite reverse;
  }
  
  .bg-hearts {
    position: absolute;
    inset: 0;
    pointer-events: none;
    
    .floating-heart {
      position: absolute;
      font-size: 24rpx;
      opacity: 0.3;
      animation: float 4s ease-in-out infinite;
      
      &:nth-child(1) { top: 10%; left: 10%; animation-delay: 0s; }
      &:nth-child(2) { top: 20%; right: 15%; animation-delay: 0.5s; }
      &:nth-child(3) { top: 40%; left: 20%; animation-delay: 1s; }
      &:nth-child(4) { top: 15%; right: 30%; animation-delay: 1.5s; }
      &:nth-child(5) { top: 35%; left: 40%; animation-delay: 2s; }
      &:nth-child(6) { top: 50%; right: 10%; animation-delay: 2.5s; }
    }
  }
}

// 恋爱天数卡片
.days-card {
  position: relative;
  z-index: 1;
  background: $bg-card;
  border-radius: $radius-xl;
  padding: 48rpx $padding-card;
  margin-top: 80rpx;
  box-shadow: $shadow-lg;
  
  .days-header {
    display: flex;
    justify-content: center;
    margin-bottom: 40rpx;
  }
  
  .days-body {
    text-align: center;
    
    .days-label {
      font-size: $font-size-base;
      color: $text-secondary;
      display: block;
      margin-bottom: 16rpx;
    }
    
    .days-number-wrapper {
      display: flex;
      align-items: baseline;
      justify-content: center;
      margin-bottom: 16rpx;
      
      .days-number {
        font-size: 144rpx;
        font-weight: $font-weight-bold;
        color: $heart-pink;
        font-family: $font-family-number;
        line-height: 1;
        text-shadow: 0 4rpx 16rpx rgba(255, 107, 138, 0.3);
      }
      
      .days-unit {
        font-size: $font-size-xl;
        color: $heart-pink-light;
        margin-left: 12rpx;
        font-weight: $font-weight-medium;
      }
    }
    
    .days-since {
      font-size: $font-size-sm;
      color: $text-tertiary;
    }
  }
  
  .days-footer {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 48rpx;
    padding-top: 40rpx;
    border-top: 2rpx solid $border-light;
    
    .mood-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 0 48rpx;
      
      .mood-emoji {
        font-size: 56rpx;
        margin-bottom: 12rpx;
      }
      
      .mood-name {
        font-size: $font-size-sm;
        color: $text-secondary;
      }
    }
    
    .mood-divider {
      width: 2rpx;
      height: 80rpx;
      background: $border-light;
    }
  }
}

// 功能入口网格
.feature-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $gap-grid;
  margin-top: 48rpx;
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 40rpx 24rpx;
  box-shadow: $shadow-sm;
  
  .feature-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    
    &:active {
      transform: scale(0.92);
    }
    
    .feature-icon {
      width: 96rpx;
      height: 96rpx;
      border-radius: $radius-lg;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 48rpx;
      margin-bottom: 16rpx;
      box-shadow: $shadow-sm;
    }
    
    .feature-name {
      font-size: $font-size-sm;
      color: $text-primary;
    }
    
    .feature-badge {
      position: absolute;
      top: -8rpx;
      right: 8rpx;
      background: $error;
      color: $text-inverse;
      font-size: $font-size-xs;
      padding: 4rpx 12rpx;
      border-radius: $radius-full;
      min-width: 32rpx;
      text-align: center;
    }
  }
}

// 区块通用样式
.section {
  position: relative;
  z-index: 1;
  margin-top: 48rpx;
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;
    
    .section-title {
      font-size: $font-size-lg;
      font-weight: $font-weight-semibold;
      color: $text-primary;
    }
    
    .section-more {
      font-size: $font-size-sm;
      color: $text-secondary;
    }
  }
}

// 即将到来列表
.upcoming-list {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 16rpx;
  box-shadow: $shadow-sm;
  
  .upcoming-item {
    display: flex;
    align-items: center;
    padding: 24rpx;
    border-radius: $radius-base;
    
    &:active {
      background: $bg-page;
    }
    
    .upcoming-icon {
      width: 80rpx;
      height: 80rpx;
      border-radius: $radius-base;
      background: $gradient-dream;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 40rpx;
      margin-right: 24rpx;
    }
    
    .upcoming-info {
      flex: 1;
      
      .upcoming-title {
        font-size: $font-size-md;
        color: $text-primary;
        font-weight: $font-weight-medium;
        display: block;
      }
      
      .upcoming-date {
        font-size: $font-size-sm;
        color: $text-secondary;
        margin-top: 8rpx;
        display: block;
      }
    }
    
    .upcoming-countdown {
      text-align: center;
      
      .countdown-number {
        font-size: $font-size-xxl;
        font-weight: $font-weight-bold;
        color: $heart-pink;
        font-family: $font-family-number;
        display: block;
        line-height: 1;
      }
      
      .countdown-unit {
        font-size: $font-size-xs;
        color: $text-tertiary;
        display: block;
        margin-top: 4rpx;
      }
    }
  }
}
</style>
```

### 9.2 心情选择器

```vue
<template>
  <view class="mood-picker" v-if="visible">
    <view class="mood-mask" @tap="close"></view>
    <view class="mood-content" :class="{ 'animate-slide-up': visible }">
      <view class="mood-header">
        <text class="mood-title">今天心情如何？</text>
        <text class="mood-subtitle">选择一个代表你此刻的 emoji</text>
      </view>
      
      <view class="mood-grid">
        <view 
          v-for="(mood, index) in moods" 
          :key="mood.id"
          class="mood-item"
          :class="{ 'selected': selectedMood === mood.id }"
          :style="{ animationDelay: `${index * 50}ms` }"
          @tap="selectMood(mood)"
        >
          <text class="mood-emoji animate-emoji-pop">{{ mood.emoji }}</text>
          <text class="mood-label">{{ mood.label }}</text>
        </view>
      </view>
      
      <view class="mood-note">
        <input 
          class="note-input" 
          v-model="note" 
          placeholder="写点什么..."
          maxlength="50"
        />
      </view>
      
      <button 
        class="btn-primary mood-submit"
        :disabled="!selectedMood"
        @tap="submit"
      >
        记录此刻
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.mood-picker {
  position: fixed;
  inset: 0;
  z-index: 1000;
}

.mood-mask {
  position: absolute;
  inset: 0;
  background: $bg-mask;
  animation: fadeIn $duration-normal $ease-soft;
}

.mood-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: $bg-card;
  border-radius: $radius-xl $radius-xl 0 0;
  padding: 48rpx $padding-card;
  padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
  
  .mood-header {
    text-align: center;
    margin-bottom: 48rpx;
    
    .mood-title {
      font-size: $font-size-xl;
      font-weight: $font-weight-semibold;
      color: $text-primary;
      display: block;
      margin-bottom: 12rpx;
    }
    
    .mood-subtitle {
      font-size: $font-size-base;
      color: $text-secondary;
    }
  }
  
  .mood-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 32rpx 24rpx;
    margin-bottom: 40rpx;
    
    .mood-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 24rpx;
      border-radius: $radius-base;
      transition: all $duration-normal $ease-soft;
      animation: scaleIn $duration-normal $ease-spring forwards;
      opacity: 0;
      
      &:active, &.selected {
        background: $heart-pink-ghost;
        transform: scale(1.05);
      }
      
      &.selected {
        .mood-emoji {
          animation: heartbeat 1s ease-in-out infinite;
        }
      }
      
      .mood-emoji {
        font-size: 64rpx;
        margin-bottom: 12rpx;
      }
      
      .mood-label {
        font-size: $font-size-sm;
        color: $text-secondary;
      }
    }
  }
  
  .mood-note {
    margin-bottom: 32rpx;
    
    .note-input {
      background: $bg-page;
      border: 2rpx solid $border-light;
      border-radius: $radius-base;
      padding: 24rpx;
      font-size: $font-size-base;
      text-align: center;
      
      &:focus {
        border-color: $heart-pink-light;
      }
    }
  }
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.animate-slide-up {
  animation: slideUp $duration-slow $ease-soft;
}
</style>
```

---

## 十、设计规范速查表

### 10.1 色彩速查

| 场景 | 色值 | 用途 |
|------|------|------|
| 主色 | `#FF6B8A` | 按钮、强调 |
| 主色浅 | `#FF8FA3` | 悬停、渐变 |
| 主色极浅 | `#FFD6DE` | 标签背景 |
| 主色幽灵 | `#FFF0F2` | 页面背景 |
| 成功 | `#66BB6A` | 完成状态 |
| 警告 | `#FFB74D` | 提醒 |
| 错误 | `#EF5350` | 错误提示 |
| 文字主 | `#2D2D3F` | 标题 |
| 文字次 | `#6B6B80` | 正文 |
| 文字辅 | `#9E9EB0` | 辅助信息 |

### 10.2 动画速查

| 场景 | 动画 | 时长 |
|------|------|------|
| 按钮点击 | `scale(0.96)` | 150ms |
| 页面进入 | `fadeInUp` | 300ms |
| 列表项 | `fadeInUp` + 延迟 | 300ms × N |
| 弹窗出现 | `scaleIn` | 300ms |
| 底部弹出 | `slideUp` | 500ms |
| 心跳效果 | `heartbeat` | 1.5s 循环 |
| 呼吸效果 | `breathe` | 3s 循环 |
| 漂浮效果 | `float` | 3s 循环 |

### 10.3 组件速查

| 组件 | 圆角 | 阴影 | 用途 |
|------|------|------|------|
| 卡片 | 32rpx | `$shadow-sm` | 内容容器 |
| 按钮 | 9999rpx | `$shadow-glow` | 主操作 |
| 输入框 | 24rpx | 无 | 表单 |
| 标签 | 9999rpx | 无 | 状态标记 |
| 弹窗 | 48rpx 48rpx 0 0 | `$shadow-xl` | 浮层 |

---

*设计系统版本：v1.0 · 咔哒小程序专用 · 2026 年 5 月*
