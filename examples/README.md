# 示例 · Ipoh → 宜宾 5 天 4 夜

完整的示例数据 + 产出。

## 文件

| 文件 | 用途 |
|---|---|
| `trip-yibin-5day.json` | 完整行程 JSON 配置(7 页内容) |
| `README.md` | 行程说明 + 重跑命令 |

## 复跑方法

```bash
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14

# 1. 复制 JSON 到 /tmp
cp /Users/a1234/Documents/UZI/00-archive/05-IOPH-JLP/trip-planner-skill/examples/trip-yibin-5day.json /tmp/

# 2. 改目的地/日期/事件后,跑:
$PY /Users/a1234/Documents/UZI/00-archive/05-IOPH-JLP/trip-planner-skill/scripts/render_story.py \
  /tmp/trip-yibin-5day.json \
  /path/to/output
```

## JSON 结构

```json
{
  "cover":  { ... },        // 封面配置
  "pages":  [ ... ],        // 每页配置(每个 day 一页)
  "essentials": { ... },    // (未在 render_story.py 实现,可扩展)
  "cost":   { ... },        // (未在 render_story.py 实现,可扩展)
  "back":   { ... }         // 应急联系配置
}
```

## 配色

`cover.palette` 可选:
- `purple`(默认,深紫蓝)
- `coral`(暖珊瑚)
- `teal`(青绿)
- `lavender`(薰衣草)
- `warm`(暖橙)

每页可单独覆盖 `pages[i].color = [R, G, B]` 自定义。
