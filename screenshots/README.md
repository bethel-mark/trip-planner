# 效果预览

下面是 `examples/trip-yibin-5day.json` 跑出来的 7 张 3:4 故事卡。

**自己复现**:
```bash
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14
$PY scripts/render_story.py examples/trip-yibin-5day.json /tmp/yibin
ls /tmp/yibin/
```

需要先把 `examples/trip-yibin-5day.json` 改目的地 / 日期 / 事件。
