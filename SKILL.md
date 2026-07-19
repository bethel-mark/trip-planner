---
name: trip-planner
license: MIT
description: Plan complete trips with day-by-day timeline, per-step precautions, full essentials checklist (9 categories), cost breakdown, targeted question lists, and mobile-friendly output (long-screenshot, per-day story cards, .ics calendar). Triggers on "行程规划", "旅行计划", "trip plan", "travel itinerary", "攻略", "路线", "去 X 玩", "going to X", or any "规划 X 旅行" intent.
metadata:
  homepage: internal://trip-planner
  applies_to: trip, travel, itinerary, vacation, business-trip, school-visit
---

# 🧳 Trip Planner — 端到端旅行规划 skill

**定位**:从用户给的一句"我要去 X 玩 N 天"开始,**全自动**产出一套可以直接打包带走的旅行手册。

## 1. 何时使用(触发语库 - 2026-07 扩充)

### 1.0 自动调度逻辑(关键)

用户说一句话,系统自动判断输出模式:

| 触发关键词 | 自动 mode | 渲染器 |
|---|---|---|
| 默认 / "出张图" / "做个图" / "小红书风" / "玻璃拟态" | **story**(3:4 玻璃拟态多页) | `render_story.py` |
| "老人版" / "大字版" / "长辈版" / "给爸妈看" / "朗读友好" / "打印" | **elder**(米白底大字) | `render_elder.py` |
| "长截图" / "一整张" | **long**(单张超长截图) | `render_mobile.py` |

**用法**(统一入口):
```bash
python3 scripts/render_trip.py trip.json outdir --prompt "做老人版给爸妈看"
# 系统自动检测 → mode=elder
```

JSON 也能显式指定:
```json
{ "elder": true, ... }  // 或 "mode": "elder"
```



**A. 黄金触发语(最稳,推荐):**
- "做一张玻璃拟态+等距3D+软3D UI风格的信息图"
- "用 Glassmorphism + Isometric + Soft 3D 风格出图"
- "用上次那个小红书风格做一张"

**B. 口语化触发(日常对话就能用):**
- "出张图"、"出个图"、"做个图"、"画一张"
- "做个信息图"、"来张信息图"、"来张图"
- "做张旅行图"、"做张行程图"、"做张攻略图"
- "做个 PPT 风的图"、"做个 Apple 风"

**C. 行程类自动触发(无需明说风格):**
- "行程规划"、"旅行计划"、"攻略"、"路线"、"旅游"
- "trip plan"、"travel itinerary"、"travel"、"itinerary"
- "去 X 玩"、"去 X 几天"、"X 几日游"、"X 月去 X"
- "帮我安排 X 行程"、"X 哪里好玩"、"X 怎么玩"
- "出发"、"返程"、"机票"、"酒店"、"签证"

**D. 设计风触发(只要听到这些词就触发):**
- "玻璃拟态"、"Glassmorphism"、"等距 3D"、"Isometric"
- "软 3D"、"Soft 3D"、"苹果风"、"Apple 风"
- "小红书风"、"Xiaohongshu 风"、"小红书风格"
- "Vision Pro 风"、"空间 UI"
- "马卡龙"、"macaron"、"莫兰迪"

**E. 视觉风格变体(可选):**
- "出冷色调的"、"出暖色调的"、"出高级感的"
- "出可爱风的"、"出商务风的"、"出学术风的"
- "出夜景的"、"出极简的"、"出插画风的"

**F. 输出格式触发:**
- "出长截图"、"出小红书版"、"出 3:4 多页"
- "出手机版"、"出打印版"、"出 A4"、"出 PDF"
- "出老人版"、"出大字版"、"给爸妈看"、"长辈版"
- "出儿童版"、"出童趣版"

**G. 隐式触发(系统自动判断):**
用户说"帮我做 X"+"信息图/图/海报/封面/卡片/PPT"等任何视觉产出词,
且当前工作流符合 trip-planner 覆盖范围时,自动激活本 skill。

**不触发的反例(避免误触发):**
- "把这张照片调亮"(单纯修图 → 走其他 skill)
- "我的代码报错"(debug 任务)
- "帮我写个函数"(编程任务)

## 2. 默认交付 4 件套(无需用户重申)

按 PROJECT_MEMORY.md 常驻规则 R01,自动交付:

| # | 交付物 | 形式 | 用途 |
|---|---|---|---|
| 1 | **行程图** | 长截图 PNG(Glassmorphism + 等距 3D + Soft 3D 风格) | 手机随时翻阅,转发分享 |
| 2 | **每步 ⚠️ 注意事项** | 嵌入行程图每张卡片 | 现场避坑 |
| 3 | **出行必备清单** | 9 大类 checkbox 清单 | 打包前对照 |
| 4 | **成本拆解** | Markdown 表格 | 预算控制 |

## 3. 工作流程(默认 5 步)

```
1. CLARIFY  主动问 4 个问题(最多):目的地 / 天数 / 同行人 / 预算级别
2. RESEARCH 调用 必查信息:签证、电源插头、汇率、当地紧急电话
3. DRAFT    按天+按小时生成 timeline,每步含 ⚠️ 注意
4. ASSEMBLE 自动产出 4 件套:
           - long_screenshot.png (用 render_mobile.py)
           - itinerary.md         (手机友好 Markdown)
           - essentials.md        (9 类清单)
           - cost_breakdown.md    (成本表)
           - calendar.ics         (可导入手机日历)
5. DELIVER  输出到 ./trip-{目的地}-{日期}/ 目录
```

## 4. 核心组件速查

| 组件 | 详情 | 在哪 |
|---|---|---|
| **必备清单模板** | 9 大类 A-I(80+ checkbox) | `references/essentials-checklist.md` |
| **针对性问题模板** | 6 类行程的提问清单(学校/商务/家庭/蜜月/探险/邮轮) | `references/question-templates.md` |
| **信息图 prompt** | Glassmorphism + 等距 3D 风格英文 prompt 模板 | `references/style-prompts.md` |
| **手机长截图生成器** | PIL + Apple Color Emoji + 30° iso 平台 + 玻璃卡 | `scripts/render_mobile.py` |
| **完整行程示例** | Malaysia IP→KL→SG 2 天实例 | `examples/malaysia-2day/` |
| **ICS 日历生成器** | 标准 .ics 格式,可导入 iOS Calendar / Google Calendar | `scripts/make_ics.py` |

## 5. 风格系统(与"小红书风"对齐)

| 风格关键词 | 含义 | 适用 |
|---|---|---|
| **Glassmorphism** | 玻璃拟态(透明卡 + 描边 + 柔光) | 所有信息图底色 |
| **Isometric** | 30° 等距投影 3D 建筑 | 校园、地标、交通 |
| **Soft 3D UI** | 苹果 Vision Pro 风格圆角 3D 元素 | 装饰、按钮、图标 |
| **Apple Color Emoji** | macOS 原生彩色 emoji | 替代手画图标(保真度 100%) |
| **Macaron Palette** | 紫/薄荷/桃/奶油 马卡龙色 | 现代、温柔 |

**触发语**(用户可直接说):

- "做一张玻璃拟态+等距3D+软3D UI风格的信息图"
- "用 Glassmorphism + Isometric + Soft 3D 风格出图"
- "用上次那个小红书风格做一张"

## 6. 智能适配规则

### 6.1 按行程类型自动调整

| 行程类型 | 必备清单增项 | 信息图侧重点 |
|---|---|---|
| **学校探校** | 孩子简历 5 份 + 成绩单 + 获奖证书 + 信用卡额度证明 | 学校等距建筑 + 录取门槛 |
| **家庭度假** | 儿童药品 + 防晒霜 + 雨具 + 零食 | 地标图标 + 餐厅 |
| **商务出差** | 名片 + 西装 + 充电宝 + 备用证件 | 会议地点 + 客户公司 |
| **蜜月** | 戒指 + 相机 + 情侣装 | 浪漫氛围 + 酒店 |
| **高原/雪山** | 红景天 + 高原安 + 厚羽绒 + 抗高反 | 雪山 + 装备 |
| **海岛** | 泳衣 + 浮潜 + 防水袋 + 防晒 | 海滩 + 浮潜 |

### 6.2 按目的地气候调整衣物类

| 气候 | 推荐 |
|---|---|
| 热带(东南亚、中东) | 快干 + 防晒 + 雨衣 + 蚊液 |
| 温带(日韩欧洲) | 薄外套 + 1 件防风 |
| 寒带(北欧、冬季) | 厚羽绒 + 雪地靴 + 暖宝宝 |
| 高原 | 厚外套 + 防晒 + 抗高反 |

### 6.3 按目的地电源插头(自动查表)

| 区域 | 插头类型 |
|---|---|
| 中港澳台、日韩 | A / C |
| 马来西亚、新加坡、英港 | G |
| 欧洲大陆 | C / E / F |
| 美国、加拿大、墨西哥 | A / B |
| 澳洲、新西兰 | I |
| 印度、斯里兰卡 | C / D / M |
| 巴西 | C / N |
| 南非 | C / D / M / N |

## 7. 输出样例

### 7.1 标准 4 件套 + 1 长截图


### 7.2 新增:3:4 多页图片版(主推)


**每页 1080 × 1440(3:4 标准竖版)**,适合:
- 小红书 / 朋友圈 / Instagram Story
- 长按单页可独立分享
- 像翻书一样按天切换
- 比一张超长截图更易消费

技术: + ```
trip-malaysia-2day/
├── itinerary_long.png        # 玻璃拟态长截图(手机翻转)
├── itinerary.md              # Markdown 行程
├── essentials.md             # 9 大类清单
├── cost_breakdown.md         # 成本表
└── calendar.ics              # 可导入手机日历
```

## 8. 安装方法

`~/.codex/skills/` 只读,放在 workspace 后用 skill-installer 装到用户级:

```bash
# 在普通终端跑
/Users/a1234/.codex/skills/.system/skill-installer/scripts/install-skill.sh \
  /Users/a1234/Documents/UZI/00-archive/05-IOPH-JLP/trip-planner-skill \
  --target user
```

## 9. 与既有 skill 的关系

- 复用 `baoyu-image-gen` 的 MiniMax provider 出 AI 真 3D 图(终端)
- 复用 `baoyu-xhs-images` 的小红书排版(若需要)
- 复用 `.system/imagegen` 的 GPT-4o 通道(终端)
- 沙盒内自带 PIL + Apple Color Emoji 渲染层(无需网络)

## 10. 维护者笔记

- v1.0 2026-07-19 由 IOPH→KL→SG 行程项目孵化
- 触发语、必备清单、4 件套交付规则均来自该项目的 PROJECT_MEMORY.md
- 后续:加打包/翻译/天气 API 等可选 sub-skill
