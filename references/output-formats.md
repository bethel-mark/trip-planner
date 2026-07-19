# 输出格式指南(手机友好)

> 同一份行程数据可以有 5 种输出形式,按场景选最适合的。

---

## 1. 长截图 PNG(主推)
**适合**:发朋友圈 / 小红书 / 收藏手机相册
**规格**:1080 × 2000-3000 px(手机长截屏)
**技术**:`scripts/render_mobile.py`(PIL + Apple Color Emoji + 30° iso 平台)
**优点**:所见即所得,中文 100% 准确,无需任何 APP
**缺点**:不能编辑(若要改,改源 JSON 重跑)

## 2. Markdown 行程(可编辑)
**适合**:现场勾选 / 复制粘贴到 Notion / 邮件附件
**格式**:`itinerary.md`,每条用 `- [ ]` checkbox
**优点**:万能格式,可导入任何笔记软件
**缺点**:阅读体验不如长截图

```markdown
# 马来西亚 2 天 1 夜行程(2026-07-19 ~ 20)

## Day 1(7/19 周日)· 探校 + 签约
- [ ] 06:30 🚆 IPOH 火车站 → KL Sentral
  - KTM ETS Platinum · RM 50 · 2h15
  - ⚠️ 提前 1-2 周 KTMB APP 订
- [ ] 09:00 ☕ KL Sentral 寄存大件
  - RM 10-15/天,有中文界面
- ...
```

## 3. 必备清单 Markdown
**适合**:打包前对照 / 打印贴冰箱
**格式**:`essentials.md`,9 大类 checkbox

```markdown
# 出行必备清单 · 马来西亚 2 天
## A. 证件 📄
- [ ] 护照原件(有效期 ≥ 6 个月)
- [ ] 签证(VOA / ETA)
- ...
```

## 4. 成本拆解
**适合**:预算控制 / 报销
**格式**:Markdown 表格

```markdown
| 类别 | 预算 | 实际 | 备注 |
|---|---|---|---|
| 交通(ETS+大巴+Grab) | RM 240 | - | |
| 住宿 | RM 60 | - | Nilai hostel |
| 餐饮 | RM 120 | - | |
| ... | | | |
| **合计** | **RM 550** | | |
```

## 5. .ics 日历(可导入手机)
**适合**:在 iOS Calendar / Google Calendar 直接看到行程
**格式**:标准 RFC 5545 .ics 文件
**优点**:自动提醒 / 跨设备同步
**缺点**:不支持 emoji 备注

```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//trip-planner//EN
BEGIN:VEVENT
UID:day1-0630@trip
DTSTART:20260719T063000
DTEND:20260719T083000
SUMMARY:🚆 IPOH → KL (KTM ETS)
LOCATION:Ipoh Railway Station
DESCRIPTION:提前 1-2 周 KTMB APP 订
END:VEVENT
END:VCALENDAR
```

---

## 📱 手机友好排版要点

| 要素 | 建议 |
|---|---|
| 字体大小 | 正文 ≥ 16 px / 标题 ≥ 24 px |
| 行距 | 1.4-1.6 倍 |
| 段落 | 单段 ≤ 4 行(避免滚动) |
| 颜色对比 | ≥ 4.5:1(WCAG AA) |
| emoji | 用作图标(信息层级)而非装饰 |
| 表格 | 手机端 ≤ 3 列 |
| 链接 | 文字 + URL 都显示 |
| 文件大小 | PNG ≤ 5 MB(微信可发) |
| 命名 | `{目的地}-{日期}-v{版本}.{ext}` |

---

## 🎨 视觉一致性建议

- 同一次旅行所有输出用同一套图标(emoji 列表)
- 同一套配色(避免每个文件都换)
- 同一字体(Hiragino Sans GB + Helvetica 混排)
- 同一 logo / 顶栏设计
- 同一文件命名规范

---

## 📂 完整输出目录结构

```
trip-{目的地}-{日期}/
├── itinerary_long.png      # 长截图(主推)
├── itinerary.md            # Markdown 行程
├── essentials.md           # 必备清单
├── cost_breakdown.md       # 成本拆解
├── calendar.ics            # 可导入手机日历
├── raw_data.json           # 源数据(可重新生成其他格式)
└── README.md               # 目录说明 + 怎么用
```
