# 📱 咔哒小程序 · 微信小程序开发规划

> **主体** 个人 · **框架** Uni-app + Vue 3 + TypeScript
> **后端** 已完成（80+ 测试通过）· **API 地址** https://api1.sparkcore.cn

---

## 一、与原计划的差异说明

### 1.1 原计划回顾

根据最初的产品规划：

```
第四阶段 · 前端开发（待启动）
├── Uni-app 项目初始化，封装请求库
├── 登录 / 注册页
├── 配对流程页（生成码 + 输入码 + 配对成功）
├── 首页（恋爱天数 + 纪念日倒计时）
├── 共享相册（上传 + 时间线）
├── 愿望清单
├── 心情同步
├── 聊天页面              ← ⚠️ 需要调整
├── 时光胶囊 + 足迹地图
├── AI 月刊展示
├── 恋爱存折（基金 + 账单 + 罚单）
└── 个人设置

第五阶段 · 小程序收尾
├── 微信后台配置合法域名（必须备案 HTTPS）
├── WebSocket 接入（聊天实时通信）  ← ⚠️ 需要调整
├── 小程序订阅消息模板申请（纪念日提醒）
├── 全流程测试 + Bug 修复
└── 提交微信审核
```

### 1.2 需要调整的内容

| 原计划功能 | 问题 | 调整方案 |
|------------|------|----------|
| 💬 聊天页面 | 个人主体无法申请社交类目 | **移除**，保留 API 供后续 APP 使用 |
| 🔌 WebSocket 接入 | 依赖聊天功能 | **移除**，后续 APP 端实现 |
| 📢 订阅消息 | 可以保留（纪念日提醒） | **保留**，属于工具类通知 |

### 1.3 保持不变的内容

- ✅ 技术栈：Uni-app + Vue 3 + TypeScript + uView UI 3 + Pinia
- ✅ 后端 API 完全复用（除聊天相关）
- ✅ 配对码机制、登录流程
- ✅ 所有记录类功能

---

## 二、功能清单（个人主体适配版）

### 2.1 可上线功能

| 模块 | API 端点 | 优先级 | 说明 |
|------|----------|--------|------|
| 🔐 登录注册 | `/auth/send-code` `/auth/login` | P0 | 手机号 + 验证码 |
| 💑 情侣配对 | `/couple/generate` `/couple/confirm` | P0 | 配对码绑定 |
| 📅 纪念日 | `/anniversaries` | P0 | 增删改查 + 倒计时 |
| 📸 共享相册 | `/photos` | P0 | 上传 + 时间线浏览 |
| 💭 愿望清单 | `/wishes` | P1 | 增删 + 标记完成 |
| 😊 心情同步 | `/moods` | P1 | 每日记录 + 伴侣可见 |
| 💊 时光胶囊 | `/capsules` | P1 | 创建 + 定时开启 |
| 🗺️ 足迹地图 | `/footprints` | P2 | 腾讯地图 + 标记 |
| 📖 恋爱月刊 | `/magazines` | P2 | AI 生成 + 浏览 |
| 💰 心愿基金 | `/funds` | P2 | 创建 + 投入 + 进度 |
| 📊 恋爱账单 | `/transactions` | P2 | 记账 + 分摊 + 余额 |
| 📝 恋爱罚单 | `/penalties` | P3 | 开罚单 + 完成打卡 |

### 2.2 暂不上线功能（保留 API）

| 模块 | 原因 | 后续方案 |
|------|------|----------|
| 💬 聊天 | 需社交类目资质 | Flutter APP 端实现 |
| 🔔 WebSocket | 依赖聊天功能 | APP 端实时通信 |

---

## 三、页面结构设计

### 3.1 底部 TabBar（3 个）

```
┌─────────────────────────────────────────────────┐
│                    咔哒                          │
├─────────────────┬─────────────────┬─────────────┤
│      首页       │      相册       │     我的     │
│      ❤️         │      📸        │     👤      │
└─────────────────┴─────────────────┴─────────────┘
```

> 其他功能（月刊、基金、账单、罚单）通过首页网格入口进入

### 3.2 完整页面清单

```
pages/
├── index/              # 首页（恋爱天数 + 心情 + 纪念日）
│   └── index.vue
├── login/              # 登录页
│   └── index.vue
├── couple/
│   ├── bind.vue        # 配对页面（生成码 / 输入码）
│   └── info.vue        # 情侣信息
├── album/
│   ├── index.vue       # 相册列表（时间线）
│   └── upload.vue      # 上传照片
├── anniversary/
│   ├── index.vue       # 纪念日列表
│   └── create.vue      # 创建/编辑纪念日
├── wish/
│   └── index.vue       # 愿望清单
├── mood/
│   └── index.vue       # 心情记录
├── capsule/
│   ├── index.vue       # 时光胶囊列表
│   └── create.vue      # 创建胶囊
├── footprint/
│   ├── index.vue       # 足迹地图
│   └── create.vue      # 添加足迹
├── magazine/
│   ├── index.vue       # 月刊列表
│   └── detail.vue      # 月刊详情
├── fund/
│   ├── index.vue       # 心愿基金列表
│   ├── detail.vue      # 基金详情 + 投入记录
│   └── contribute.vue  # 投入资金
├── transaction/
│   ├── index.vue       # 账单列表 + 余额统计
│   └── create.vue      # 创建账单
├── penalty/
│   ├── index.vue       # 罚单列表
│   └── create.vue      # 开罚单
└── mine/
    └── index.vue       # 个人中心（用户信息 + 设置 + 解绑）
```

---

## 四、首页设计（聚焦式布局）

### 4.1 设计理念

- **一屏核心**：恋爱天数 + 心情占满上半屏，视觉焦点突出
- **紧凑功能**：3x3 网格展示所有功能入口，无需滚动即可触达
- **底部预览**：即将到来的纪念日，引导用户继续探索

### 4.2 首页布局

```
┌─────────────────────────────────────────┐
│  💕 咔哒                   ⚙️ 设置      │
├─────────────────────────────────────────┤
│                                         │
│           ❤️ 在一起 ❤️                   │
│              365                        │
│              天                         │
│        2025.05.30 - 今                  │
│                                         │
│    ─────────── ♡ ───────────           │
│                                         │
│      😊 我                🥰 TA        │
│      开心                  想你         │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│   📅        📸        💭               │
│  纪念日     相册      愿望              │
│                                         │
│   💊        🗺️        📖               │
│  胶囊       足迹      月刊              │
│                                         │
│   💰        📊        📝               │
│  基金       账单      罚单              │
│                                         │
├─────────────────────────────────────────┤
│  📮 即将到来                            │
│  ┌──────────────────────────────────┐   │
│  │  🎂 她的生日           还有 15 天 │   │
│  │  💑 恋爱纪念日         还有 30 天 │   │
│  └──────────────────────────────────┘   │
│                                         │
├─────────────────────────────────────────┤
│       ❤️ 首页  │  📸 相册  │  👤 我的   │
└─────────────────────────────────────────┘
```

### 4.3 首页功能点

| 区域 | 内容 | 说明 |
|------|------|------|
| 核心区 | 恋爱天数 | 大数字展示，心跳动画 |
| 心情区 | 双方今日心情 | 点击可记录心情 |
| 功能区 | 3x3 网格 | 9个功能入口，紧凑排列 |
| 预览区 | 即将到来 | 最近纪念日倒计时 |

### 4.4 数据来源

| 功能 | API 调用 |
|------|----------|
| 恋爱天数 | `couple.info.start_date` 计算 |
| 今日心情 | `moods.list` 筛选今日 |
| 即将到来 | `anniversaries.list` 排序取前2 |
| 功能入口 | 静态导航，点击跳转 |

---

## 五、技术方案

### 5.1 技术栈（与原计划一致）

| 类别 | 选型 | 说明 |
|------|------|------|
| 框架 | **Uni-app + Vue 3** | 编译微信小程序 |
| 语言 | **TypeScript** | 类型安全 |
| UI 库 | **uView Plus** | Vue 3 版本 |
| 状态管理 | **Pinia** | 轻量状态管理 |
| 网络请求 | **uni.request** 封装 | 统一拦截器 |
| 地图 | **腾讯地图 SDK** | 足迹地图功能 |

### 5.2 项目结构

```
kada-miniapp/
├── src/
│   ├── api/                # API 请求封装（对应后端 routers）
│   │   ├── auth.ts         # /auth/*
│   │   ├── couple.ts       # /couple/*
│   │   ├── anniversary.ts  # /anniversaries/*
│   │   ├── album.ts        # /photos/*
│   │   ├── wish.ts         # /wishes/*
│   │   ├── mood.ts         # /moods/*
│   │   ├── capsule.ts      # /capsules/*
│   │   ├── footprint.ts    # /footprints/*
│   │   ├── magazine.ts     # /magazines/*
│   │   ├── fund.ts         # /funds/*
│   │   ├── transaction.ts  # /transactions/*
│   │   └── penalty.ts      # /penalties/*
│   ├── components/         # 公共组件
│   │   ├── CoupleHeader.vue    # 情侣头部（头像 + 天数）
│   │   ├── AnniversaryCard.vue # 纪念日卡片
│   │   ├── PhotoGrid.vue       # 相册网格
│   │   ├── WishItem.vue        # 愿望条目
│   │   ├── MoodPicker.vue      # 心情选择器
│   │   └── Empty.vue           # 空状态组件
│   ├── pages/              # 页面（见第三章）
│   ├── stores/             # Pinia 状态管理
│   │   ├── auth.ts         # Token + 用户信息
│   │   └── couple.ts       # 配对信息 + 恋爱天数
│   ├── utils/              # 工具函数
│   │   ├── request.ts      # 请求封装
│   │   ├── storage.ts      # 本地存储
│   │   └── date.ts         # 日期计算
│   ├── static/             # 静态资源
│   │   ├── icons/          # 图标
│   │   └── images/         # 图片
│   ├── App.vue
│   ├── main.ts
│   ├── manifest.json       # Uni-app 配置
│   ├── pages.json          # 页面路由 + TabBar
│   └── uni.scss            # 全局样式变量
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### 5.3 API 请求封装

```typescript
// src/utils/request.ts
const BASE_URL = 'https://api1.sparkcore.cn'

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
}

export const request = <T = any>(options: RequestOptions): Promise<T> => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')

    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data as T)
        } else if (res.statusCode === 401) {
          // Token 过期，清除登录状态并跳转
          uni.removeStorageSync('token')
          uni.navigateTo({ url: '/pages/login/index' })
          reject(new Error('登录已过期'))
        } else {
          const errMsg = (res.data as any)?.detail || '请求失败'
          reject(new Error(errMsg))
        }
      },
      fail: (err) => {
        reject(new Error('网络错误'))
      }
    })
  })
}
```

### 5.4 API 模块示例

```typescript
// src/api/anniversary.ts
import { request } from '@/utils/request'

export interface Anniversary {
  id: string
  title: string
  date: string
  repeat_type: 'none' | 'yearly'
  days_until: number | null
}

export interface AnniversaryCreate {
  title: string
  date: string
  repeat_type?: 'none' | 'yearly'
}

export const anniversaryApi = {
  // 获取纪念日列表
  list: () => request<Anniversary[]>({ url: '/api/anniversaries' }),

  // 创建纪念日
  create: (data: AnniversaryCreate) =>
    request<Anniversary>({ url: '/api/anniversaries', method: 'POST', data }),

  // 更新纪念日
  update: (id: string, data: Partial<AnniversaryCreate>) =>
    request<Anniversary>({ url: `/api/anniversaries/${id}`, method: 'PUT', data }),

  // 删除纪念日
  delete: (id: string) =>
    request({ url: `/api/anniversaries/${id}`, method: 'DELETE' })
}
```

---

## 六、开发阶段（对齐原计划）

### 6.1 里程碑总览

```
原计划 Week 5-8   →   Uni-app 微信小程序开发
原计划 Week 9-10  →   小程序适配完善 + 提审

本规划细化：
Week 5      基础框架（登录 + 配对 + 请求封装 + TabBar）
Week 6-7    核心功能（首页 + 纪念日 + 相册 + 愿望 + 心情）
Week 7-8    进阶功能（胶囊 + 地图 + 月刊 + 存折）
Week 9      UI 美化 + 动画 + 体验优化
Week 10     测试 + 提审 + 上线
```

### 6.2 详细排期

#### 📦 阶段一：基础框架（Week 5）

| 任务 | 说明 | 产出 |
|------|------|------|
| Uni-app 项目初始化 | Vue 3 + TypeScript + uView Plus | 项目骨架 |
| 请求库封装 | Token 管理 + 拦截器 + 错误处理 | `utils/request.ts` |
| Pinia 状态管理 | auth store + couple store | 登录态管理 |
| 登录页 | 手机号 + 验证码输入 | `pages/login/index` |
| 配对流程 | 生成配对码 / 输入配对码 / 配对成功 | `pages/couple/bind` |
| TabBar 框架 | 4 个底部导航 + 图标 | `pages.json` |

#### 💝 阶段二：核心功能（Week 6-7）

| 任务 | 说明 | 产出 |
|------|------|------|
| 首页 | 恋爱天数 + 心情 + 纪念日预览 + 愿望 + 胶囊 | `pages/index/index` |
| 纪念日模块 | 列表 + 创建 + 编辑 + 删除 | `pages/anniversary/*` |
| 相册模块 | 时间线列表 + 上传 + 预览 + 删除 | `pages/album/*` |
| 愿望清单 | 列表 + 添加 + 标记完成 + 删除 | `pages/wish/index` |
| 心情同步 | 心情选择器 + 每日记录 + 双方展示 | `pages/mood/index` |

#### ✨ 阶段三：进阶功能（Week 7-8）

| 任务 | 说明 | 产出 |
|------|------|------|
| 时光胶囊 | 创建 + 列表 + 到期开启动画 | `pages/capsule/*` |
| 足迹地图 | 腾讯地图集成 + 添加标记 + 详情 | `pages/footprint/*` |
| 恋爱月刊 | 月刊列表 + 详情展示 | `pages/magazine/*` |
| 心愿基金 | 基金列表 + 详情 + 投入 | `pages/fund/*` |
| 恋爱账单 | 账单列表 + 创建 + 余额统计 | `pages/transaction/*` |
| 恋爱罚单 | 罚单列表 + 开罚单 + 完成 | `pages/penalty/*` |
| 个人中心 | 用户信息 + 情侣信息 + 设置 + 解绑 | `pages/mine/index` |

#### 🎨 阶段四：优化完善（Week 9）

| 任务 | 说明 |
|------|------|
| UI 细节 | 圆角、阴影、渐变、动画 |
| 加载状态 | 骨架屏 + 下拉刷新 + 上拉加载 |
| 空状态 | 各模块的空状态展示 |
| 错误处理 | 网络错误 + 服务异常提示 |
| 分包优化 | 主包 < 2MB，总包 < 20MB |

#### 🚀 阶段五：测试上线（Week 10）

| 任务 | 说明 |
|------|------|
| 功能测试 | 全流程测试 + 边界情况 |
| 微信后台 | 配置合法域名（HTTPS 备案） |
| 订阅消息 | 纪念日提醒模板申请 |
| 提交审核 | 准备材料 + 提交微信审核 |
| 上线监控 | 错误日志 + 性能监控 |

---

## 七、审核要点

### 7.1 类目选择

```
推荐类目：
├── 工具 → 信息查询（首选）
└── 生活服务 → 日历/记账（备选）

说明：纪念日、相册、记账等功能属于工具/生活服务范畴
```

### 7.2 描述文案

```
【小程序名称】咔哒
【小程序描述】
咔哒 - 记录我们的每一天
专为情侣打造的私密记录工具：
• 记录重要纪念日，不错过每一个重要时刻
• 共享甜蜜相册，珍藏美好回忆
• 心愿清单、心情日记，记录生活点滴
• 时光胶囊，封存此刻，未来开启
• 足迹地图，标记一起走过的路

【隐私说明】
所有数据仅配对双方可见，不涉及公开社交。
```

### 7.3 审核材料

| 材料 | 说明 |
|------|------|
| 测试账号 | 提供已配对的测试账号 |
| 功能说明 | 各功能模块的使用说明 |
| 隐私协议 | 说明数据仅两人可见 |
| 服务协议 | 用户服务条款 |

---

## 八、分包策略

```json
{
  "pages": [
    "pages/index/index",
    "pages/login/index",
    "pages/album/index",
    "pages/mine/index"
  ],
  "subPackages": [
    {
      "root": "pages/couple",
      "pages": ["bind", "info"]
    },
    {
      "root": "pages/anniversary",
      "pages": ["index", "create"]
    },
    {
      "root": "pages/wish",
      "pages": ["index"]
    },
    {
      "root": "pages/mood",
      "pages": ["index"]
    },
    {
      "root": "pages/capsule",
      "pages": ["index", "create"]
    },
    {
      "root": "pages/footprint",
      "pages": ["index", "create"]
    },
    {
      "root": "pages/magazine",
      "pages": ["index", "detail"]
    },
    {
      "root": "pages/fund",
      "pages": ["index", "detail", "contribute"]
    },
    {
      "root": "pages/transaction",
      "pages": ["index", "create"]
    },
    {
      "root": "pages/penalty",
      "pages": ["index", "create"]
    }
  ],
  "preloadRule": {
    "pages/index/index": {
      "network": "all",
      "packages": ["pages/anniversary", "pages/wish"]
    }
  }
}
```

---

## 九、UI 设计规范

### 9.1 色彩方案

```scss
// src/uni.scss

// 主色调 - 浪漫粉
$primary: #FF6B81;
$primary-light: #FFA3B1;
$primary-dark: #FF4757;

// 辅助色
$success: #2ED573;
$warning: #FFA502;
$error: #FF4757;

// 文字色
$text-primary: #2D3436;
$text-secondary: #636E72;
$text-placeholder: #B2BEC3;

// 背景色
$bg-page: #FFF5F5;
$bg-card: #FFFFFF;
$bg-input: #F8F9FA;

// 边框色
$border: #F1F2F6;
```

### 9.2 组件风格

```scss
// 卡片样式
.card {
  background: $bg-card;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(255, 107, 129, 0.08);
}

// 按钮样式
.btn-primary {
  background: linear-gradient(135deg, $primary, $primary-dark);
  color: #fff;
  border-radius: 48rpx;
  height: 88rpx;
  font-size: 32rpx;
}

// 输入框样式
.input {
  background: $bg-input;
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 28rpx;
}
```

### 9.3 设计原则

1. **温馨浪漫** — 粉色系 + 圆角 + 柔和阴影
2. **简洁易用** — 大按钮 + 清晰层级 + 一键操作
3. **情感化** — emoji + 动画 + 甜蜜文案
4. **一致性** — 统一的组件风格 + 间距规范

---

## 十、后续扩展路径

### 10.1 聊天功能方案（企业主体后）

```
方案 A：企业主体 + 社交类目（推荐）
├── 注册个体工商户（成本低）
├── 申请企业主体小程序
├── 申请社交类目资质
└── 接入聊天 + WebSocket

方案 B：原生 APP
├── Flutter 开发（原计划第六阶段）
├── 聊天功能在 APP 端实现
├── FCM + APNs 推送通知
└── 小程序作为轻量版共存
```

### 10.2 版本规划

```
v1.0 — 基础记录功能（审核上线版本）
       包含：登录、配对、纪念日、相册、愿望、心情

v1.1 — 进阶功能更新
       包含：时光胶囊、足迹地图

v1.2 — 特色功能更新
       包含：恋爱月刊、心愿基金、账单、罚单

v1.3 — 体验优化
       包含：动画、小组件、性能优化

v2.0 — 聊天功能（需企业主体）
       包含：实时聊天、WebSocket、推送通知
```

---

## 十一、与后端 API 对照表

| 前端模块 | API 端点 | 方法 | 状态 |
|----------|----------|------|------|
| 登录 | `/api/auth/send-code` | POST | ✅ |
| 登录 | `/api/auth/login` | POST | ✅ |
| 个人中心 | `/api/auth/me` | GET | ✅ |
| 配对 | `/api/couple/generate` | POST | ✅ |
| 配对 | `/api/couple/confirm` | POST | ✅ |
| 配对 | `/api/couple/info` | GET | ✅ |
| 配对 | `/api/couple/unbind` | POST | ✅ |
| 纪念日 | `/api/anniversaries` | GET/POST | ✅ |
| 纪念日 | `/api/anniversaries/{id}` | PUT/DELETE | ✅ |
| 相册 | `/api/photos` | GET/POST | ✅ |
| 相册 | `/api/photos/{id}` | DELETE | ✅ |
| 愿望 | `/api/wishes` | GET/POST | ✅ |
| 愿望 | `/api/wishes/{id}` | PUT/DELETE | ✅ |
| 心情 | `/api/moods` | GET/POST | ✅ |
| 心情 | `/api/moods/{id}` | DELETE | ✅ |
| 时光胶囊 | `/api/capsules` | GET/POST | ✅ |
| 时光胶囊 | `/api/capsules/{id}` | GET/DELETE | ✅ |
| 时光胶囊 | `/api/capsules/{id}/open` | POST | ✅ |
| 足迹 | `/api/footprints` | GET/POST | ✅ |
| 足迹 | `/api/footprints/{id}` | GET/PUT/DELETE | ✅ |
| 月刊 | `/api/magazines` | GET | ✅ |
| 月刊 | `/api/magazines/generate` | POST | ✅ |
| 月刊 | `/api/magazines/{id}` | GET/DELETE | ✅ |
| 基金 | `/api/funds` | GET/POST | ✅ |
| 基金 | `/api/funds/{id}/contribute` | POST | ✅ |
| 基金 | `/api/funds/{id}/contributions` | GET | ✅ |
| 基金 | `/api/funds/{id}` | DELETE | ✅ |
| 账单 | `/api/transactions` | GET/POST | ✅ |
| 账单 | `/api/transactions/balance` | GET | ✅ |
| 账单 | `/api/transactions/{id}` | DELETE | ✅ |
| 罚单 | `/api/penalties` | GET/POST | ✅ |
| 罚单 | `/api/penalties/{id}/done` | POST | ✅ |
| 罚单 | `/api/penalties/{id}` | DELETE | ✅ |

---

**下一步**：初始化 Uni-app 项目，开始阶段一开发。

*文档版本：v1.0 · 2026 年 5 月*
