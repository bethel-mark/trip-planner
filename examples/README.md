# 示例 · Ipoh → 宜宾 5 天 4 夜

完整示例数据 + 两种产出风格。

## 文件

| 文件 | 用途 |
|---|---|
| `trip-yibin-5day.json` | 完整行程 JSON(5 天 4 夜,6 页) |
| `README.md` | 本说明 |

## 3 种产出模式

### 模式 1:3:4 故事卡(玻璃拟态,默认)

```bash
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14
$PY ../scripts/render_story.py trip-yibin-5day.json /tmp/yibin-story
ls /tmp/yibin-story/
# 01_cover.png  02_day1.png  ...  07_back.png
```

### 模式 2:老人大字版(长辈 / 视障 / 朗读)

```bash
$PY ../scripts/render_elder.py trip-yibin-5day.json /tmp/yibin-elder
ls /tmp/yibin-elder/
# 01_cover.png  02_day1.png  ...  08_emergency.png
```

- 标题 80pt,正文 36pt
- 米白底 + 砖红强调,高对比
- 一页一重点,无装饰干扰

### 模式 3:单张长截图(桌面 / 投影)

```bash
$PY ../scripts/render_mobile.py trip-yibin-5day.json /tmp/yibin-long
ls /tmp/yibin-long/
# itinerary_long.png
```

## JSON 结构

```json
{
  "cover":  { "title": "...", "subtitle": "...", "hero_emoji": "..." },
  "pages":  [ { "day": 1, "day_title": "...", "events": [...], "tips": [...] } ],
  "essentials": { "categories": [ {"name":"...", "items":[...]} ] },
  "cost":   { "total": "...", "items": [...] },
  "back":   { "title": "...", "contacts": [...] }
}
```

## 配色

`cover.palette` 可选:
- `purple`(默认,深紫蓝)
- `coral`(暖珊瑚)
- `teal`(青绿)
- `lavender`(薰衣草)
- `warm`(暖橙)
- `macaron`(马卡龙)

每页可单独覆盖 `pages[i].color = [R, G, B]` 自定义。
