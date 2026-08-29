# 咔哒小程序 — 技术设计规格

> **日期** 2026-06-06 · **状态** 已确认 · **框架** Uni-app + Vue 3 + TypeScript  
> **UI 底座** uView Plus 3.x · **图标** Tabler Icons via Iconify · **后端** 已完成（80+ 测试通过）

---

## 一、项目概述

### 1.1 目标

基于已完成的后端 API，开发"咔哒"情侣记录小程序微信端。面向中国大陆用户，设计风格为"Soft Warmth — 柔和温暖"。

### 1.2 范围

- **包含**：登录、配对、首页、纪念日、相册、愿望、心情、时光胶囊、足迹（列表）、月刊、基金、账单、罚单、个人中心
- **排除**：聊天功能（需社交类目）、WebSocket、腾讯地图 SDK（后续集成）

### 1.3 设计文档索引

| 文档 | 路径 | 说明 |
|------|------|------|
| UI 设计规范 | `frontend/kada-miniapp-design.md` | 色彩/字体/间距/圆角/阴影/动画/组件样式 |
| 开发规划 | `frontend/mini-program-plan.md` | 功能清单/页面结构/技术方案/分包策略 |
| API 文档 | `docs/API文档.md` | 后端 REST API 接口规范 |

---

## 二、技术栈

| 类别 | 选型 | 说明 |
|------|------|------|
| 框架 | Uni-app + Vue 3 | 编译微信小程序 |
| 语言 | TypeScript | 类型安全 |
| UI 底座 | uView Plus 3.x | 仅用 JS 逻辑能力（表单验证/导航/加载），视觉全部自定义 |
| 状态管理 | Pinia | auth + couple 两个 store |
| 图标 | Tabler Icons via @iconify/vue | 按需引入，无 emoji |
| 请求 | uni.request 封装 | Token 自动注入 + 401 拦截 |
| 地图 | 暂不集成 | 足迹功能先做列表/创建 |

---

## 三、项目结构

```
frontend/miniapp/
├── src/
│   ├── api/                    # API 请求模块（12 个）
│   │   ├── auth.ts             # /api/auth/*
│   │   ├── couple.ts           # /api/couple/*
│   │   ├── anniversary.ts      # /api/anniversaries/*
│   │   ├── photo.ts            # /api/photos/*
│   │   ├── wish.ts             # /api/wishes/*
│   │   ├── mood.ts             # /api/moods/*
│   │   ├── capsule.ts          # /api/capsules/*
│   │   ├── footprint.ts        # /api/footprints/*
│   │   ├── magazine.ts         # /api/magazines/*
│   │   ├── fund.ts             # /api/funds/*
│   │   ├── transaction.ts      # /api/transactions/*
│   │   └── penalty.ts          # /api/penalties/*
│   ├── components/             # 自定义组件（Kd 前缀）
│   │   ├── KdButton.vue        # 渐变按钮 + 光晕
│   │   ├── KdCard.vue          # 卡片（普通/强调/玻璃）
│   │   ├── KdIcon.vue          # Iconify 封装
│   │   ├── KdEmpty.vue         # 空状态（漂浮动画）
│   │   ├── KdMoodPicker.vue    # 心情选择器（底部弹出）
│   │   ├── KdCoupleHeader.vue  # 情侣头像 + 天数
│   │   └── KdCountdown.vue     # 纪念日倒计时
│   ├── pages/                  # 页面
│   │   ├── index/index.vue     # 首页（主包）
│   │   ├── login/index.vue     # 登录（主包）
│   │   ├── album/              # 相册（主包）
│   │   ├── mine/index.vue      # 我的（主包）
│   │   ├── couple/             # 配对（分包）
│   │   ├── anniversary/        # 纪念日（分包）
│   │   ├── wish/               # 愿望（分包）
│   │   ├── mood/               # 心情（分包）
│   │   ├── capsule/            # 胶囊（分包）
│   │   ├── footprint/          # 足迹（分包）
│   │   ├── magazine/           # 月刊（分包）
│   │   ├── fund/               # 基金（分包）
│   │   ├── transaction/        # 账单（分包）
│   │   └── penalty/            # 罚单（分包）
│   ├── stores/
│   │   ├── auth.ts             # Token + 用户信息
│   │   └── couple.ts           # 配对信息 + 恋爱天数
│   ├── styles/
│   │   ├── variables.scss      # 设计规范变量
│   │   ├── mixins.scss         # 常用 mixin
│   │   └── animations.scss     # 动画库
│   ├── utils/
│   │   ├── request.ts          # 请求封装
│   │   ├── storage.ts          # 本地存储
│   │   └── date.ts             # 日期计算
│   ├── static/images/          # 图片资源
│   ├── App.vue
│   ├── main.ts
│   ├── manifest.json
│   ├── pages.json              # 路由 + TabBar + 分包
│   └── uni.scss                # 全局变量入口
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## 四、图标系统

### 4.1 图标集选择

使用 **Tabler Icons** 作为主图标集，通过 `@iconify/vue` 按需引入。

理由：
- 线条风格统一、简洁优雅
- 圆润设计与"柔和温暖"理念契合
- 2000+ 图标覆盖所有功能场景
- 不使用 emoji，保持视觉一致性

### 4.2 功能图标映射

| 功能 | 图标 | 说明 |
|------|------|------|
| 纪念日 | `tabler:calendar-heart` | 日历+爱心 |
| 相册 | `tabler:photo` | 照片 |
| 愿望 | `tabler:sparkles` | 星星 |
| 时光胶囊 | `tabler:hourglass` | 沙漏 |
| 足迹 | `tabler:map-pin` | 地图标记 |
| 月刊 | `tabler:book-2` | 书本 |
| 心愿基金 | `tabler:piggy-bank` | 存钱罐 |
| 账单 | `tabler:receipt` | 收据 |
| 罚单 | `tabler:ticket` | 票券 |
| 心情 | `tabler:mood-smile` | 笑脸 |
| 设置 | `tabler:settings` | 齿轮 |
| 添加 | `tabler:plus` | 加号 |
| 删除 | `tabler:trash` | 垃圾桶 |
| 编辑 | `tabler:pencil` | 铅笔 |
| 返回 | `tabler:chevron-left` | 左箭头 |

### 4.3 TabBar 图标

| Tab | 默认态 | 选中态 |
|-----|--------|--------|
| 首页 | `tabler:home` | `tabler:home-filled` |
| 相册 | `tabler:photo` | `tabler:photo-filled` |
| 我的 | `tabler:user` | `tabler:user-filled` |

### 4.4 心情图标（替代 emoji）

| 心情 | 图标 |
|------|------|
| 开心 | `tabler:mood-happy` |
| 想你 | `tabler:mood-heart-eyes` |
| 难过 | `tabler:mood-sad` |
| 生气 | `tabler:mood-angry` |
| 平静 | `tabler:mood-neutral` |
| 惊喜 | `tabler:mood-crazy-happy` |
| 困倦 | `tabler:mood-wrrr` |
| 甜蜜 | `tabler:mood-wink-2` |

---

## 五、样式系统

### 5.1 全局变量（uni.scss）

将 `kada-miniapp-design.md` 中的设计规范映射为 SCSS 变量，通过 `uni.scss` 全局注入。

#### 色彩

```scss
// 主色 — 心动粉
$heart-pink: #FF6B8A;
$heart-pink-light: #FF8FA3;
$heart-pink-pale: #FFD6DE;
$heart-pink-ghost: #FFF0F2;
$heart-pink-dark: #E8527A;

// 辅助色
$sunrise-gold: #FFB347;
$lavender: #B39DDB;
$mint: #80CBC4;
$sky: #81D4FA;
$coral: #FF8A80;

// 功能色
$success: #66BB6A;
$warning: #FFB74D;
$error: #EF5350;
$info: #42A5F5;

// 文字
$text-primary: #2D2D3F;
$text-secondary: #6B6B80;
$text-tertiary: #9E9EB0;

// 背景
$bg-page: #FFF0F2;
$bg-card: #FFFFFF;

// 边框
$border-light: #FFE4E8;
```

#### 间距（8px 网格）

```scss
$space-xs: 8rpx;
$space-sm: 16rpx;
$space-md: 24rpx;
$space-base: 32rpx;
$space-lg: 48rpx;
$space-xl: 64rpx;
```

#### 圆角

```scss
$radius-sm: 12rpx;
$radius-base: 24rpx;
$radius-lg: 32rpx;
$radius-xl: 48rpx;
$radius-full: 9999rpx;
```

#### 阴影（粉色系）

```scss
$shadow-sm: 0 2rpx 8rpx rgba(255, 107, 138, 0.08);
$shadow-md: 0 4rpx 16rpx rgba(255, 107, 138, 0.12);
$shadow-lg: 0 8rpx 32rpx rgba(255, 107, 138, 0.16);
$shadow-glow: 0 0 24rpx rgba(255, 107, 138, 0.30);
```

#### 渐变

```scss
$gradient-heart: linear-gradient(135deg, #FF6B8A, #FF8FA3);
$gradient-dawn: linear-gradient(180deg, #FFF0F2, #FFFFFF);
$gradient-sunset: linear-gradient(135deg, #FFB347, #FF6B8A);
$gradient-starry: linear-gradient(135deg, #B39DDB, #81D4FA);
```

#### 动画

```scss
$ease-soft: cubic-bezier(0.25, 0.1, 0.25, 1);
$ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
$duration-fast: 150ms;
$duration-normal: 300ms;
$duration-slow: 500ms;
```

### 5.2 uView Plus 主题覆盖

```scss
$u-primary: $heart-pink;
$u-warning: $sunrise-gold;
$u-success: $success;
$u-error: $error;
$u-info: $sky;
$u-main-color: $text-primary;
$u-content-color: $text-secondary;
$u-tips-color: $text-tertiary;
```

### 5.3 动画库（animations.scss）

预定义动画类，全局复用：

| 类名 | 效果 | 用途 |
|------|------|------|
| `.animate-heartbeat` | 心跳缩放 | 恋爱天数、喜欢按钮 |
| `.animate-breathe` | 呼吸透明度 | 强调元素 |
| `.animate-float` | 上下漂浮 | 装饰、空状态 |
| `.animate-fade-in-up` | 渐入上移 | 列表项 |
| `.animate-scale-in` | 弹性缩放 | 按钮、卡片 |
| `.animate-pulse-glow` | 脉冲光晕 | 重要按钮 |
| `.animate-shake` | 水平摇晃 | 删除确认 |
| `.animate-slide-up` | 底部滑入 | 弹窗 |

---

## 六、组件设计

### 6.1 自定义组件（Kd 前缀）

所有视觉组件自定义实现，不使用 uView 默认样式。仅使用 uView 的 JS 逻辑能力。

| 组件 | 说明 | 特色 |
|------|------|------|
| KdButton | 渐变按钮 | 光晕效果 + 按压缩放 |
| KdCard | 卡片容器 | 3 种变体（普通/强调/玻璃） |
| KdIcon | 图标封装 | 统一 Iconify 接口 |
| KdEmpty | 空状态 | 漂浮动画 + 插画 |
| KdMoodPicker | 心情选择器 | 底部弹出 + 心情图标动画 |
| KdCoupleHeader | 情侣头部 | 重叠头像 + 爱心分隔 |
| KdCountdown | 倒计时 | 大数字 + 单位 |

### 6.2 页面级特色

| 页面 | 特色设计 |
|------|----------|
| 首页 | 背景装饰圆 + 浮动粒子 + 恋爱天数心跳 + 功能网格渐入 |
| 配对成功 | 爆炸心形动画 |
| 心情选择 | 底部弹出 + 图标弹出动画 + 选中心跳 |
| 时光胶囊 | 开启时放大旋转回弹 + 光晕扩散 |
| 纪念日 | 梦幻渐变背景 + 大数字倒计时 |

---

## 七、请求封装

### 7.1 基础封装（utils/request.ts）

- 基础地址：`https://api1.sparkcore.cn`
- Token 注入：从 `uni.getStorageSync('token')` 读取
- 401 处理：清除 Token + 跳转登录页
- 错误处理：统一 reject Error，页面层 catch 展示

### 7.2 文件上传

照片上传使用 `uni.uploadFile` 而非 `uni.request`，接口为 `POST /api/photos`。

### 7.3 列表页面模式

- 下拉刷新：`onPullDownRefresh` → 重新请求第一页
- 上拉加载：`onReachBottom` → 请求下一页
- 空状态：KdEmpty 组件展示

---

## 八、分包策略

### 主包（< 2MB）

| 页面 | 说明 |
|------|------|
| pages/index/index | 首页 |
| pages/login/index | 登录 |
| pages/album/index | 相册列表 |
| pages/mine/index | 我的 |

### 分包（10 个）

| 分包 | 页面 |
|------|------|
| pages/couple | bind, info |
| pages/anniversary | index, create |
| pages/wish | index |
| pages/mood | index |
| pages/capsule | index, create |
| pages/footprint | index, create |
| pages/magazine | index, detail |
| pages/fund | index, detail, contribute |
| pages/transaction | index, create |
| pages/penalty | index, create |

### 预加载

首页预加载 `pages/anniversary` 和 `pages/wish` 分包。

---

## 九、开发顺序

### 第一批 — 基础框架

1. 项目初始化（Uni-app + Vue 3 + TS + uView Plus + Iconify）
2. 全局样式系统
3. 请求封装
4. Pinia Stores
5. 登录页
6. 配对流程
7. TabBar 框架

### 第二批 — 核心功能

8. 首页
9. 纪念日模块
10. 相册模块
11. 愿望清单
12. 心情同步

### 第三批 — 进阶功能

13. 时光胶囊
14. 足迹（列表+创建）
15. 恋爱月刊
16. 心愿基金
17. 恋爱账单
18. 恋爱罚单
19. 个人中心

---

## 十、API 对照表

| 前端模块 | API 端点 | 方法 |
|----------|----------|------|
| 登录 | `/api/auth/send-code` | POST |
| 登录 | `/api/auth/login` | POST |
| 个人 | `/api/auth/me` | GET |
| 配对 | `/api/couple/generate` | POST |
| 配对 | `/api/couple/confirm` | POST |
| 配对 | `/api/couple/info` | GET |
| 配对 | `/api/couple/unbind` | POST |
| 纪念日 | `/api/anniversaries` | GET/POST |
| 纪念日 | `/api/anniversaries/{id}` | PUT/DELETE |
| 相册 | `/api/photos` | GET/POST |
| 相册 | `/api/photos/{id}` | DELETE |
| 愿望 | `/api/wishes` | GET/POST |
| 愿望 | `/api/wishes/{id}` | PUT/DELETE |
| 心情 | `/api/moods` | GET/POST |
| 心情 | `/api/moods/{id}` | DELETE |
| 胶囊 | `/api/capsules` | GET/POST |
| 胶囊 | `/api/capsules/{id}` | GET/DELETE |
| 胶囊 | `/api/capsules/{id}/open` | POST |
| 足迹 | `/api/footprints` | GET/POST |
| 足迹 | `/api/footprints/{id}` | GET/PUT/DELETE |
| 月刊 | `/api/magazines` | GET |
| 月刊 | `/api/magazines/generate` | POST |
| 月刊 | `/api/magazines/{id}` | GET/DELETE |
| 基金 | `/api/funds` | GET/POST |
| 基金 | `/api/funds/{id}/contribute` | POST |
| 基金 | `/api/funds/{id}/contributions` | GET |
| 基金 | `/api/funds/{id}` | DELETE |
| 账单 | `/api/transactions` | GET/POST |
| 账单 | `/api/transactions/balance` | GET |
| 账单 | `/api/transactions/{id}` | DELETE |
| 罚单 | `/api/penalties` | GET/POST |
| 罚单 | `/api/penalties/{id}/done` | POST |
| 罚单 | `/api/penalties/{id}` | DELETE |

---

## 十一、审核适配

### 类目

- 首选：工具 → 信息查询
- 备选：生活服务 → 日历/记账

### 描述

咔哒 - 记录我们的每一天。专为情侣打造的私密记录工具：纪念日、相册、心愿、心情、时光胶囊、足迹地图。所有数据仅配对双方可见。

---

*规格版本：v1.0 · 2026-06-06*
