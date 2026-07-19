# Provider 对比实测(2026-07-19)

> 用 **同 1 份 prompt** 跑 2 个 provider,出图对比

## 测试条件

- **Prompt**:乐山 3 天 2 夜 旅行封面
- **Provider A**:`minimax/image-01`(本机默认)
- **Provider B**:`zai/cogview-4-250304`(智谱)
- **测试工具**:`scripts/compare_providers.py`
- **完整对比图**:[provider_comparison_sample.png](provider_comparison_sample.png)

## 结果

| 维度 | MiniMax-Image-01 | Zhipu CogView-4 |
|---|---|---|
| **标题中文** | ❌ 完全错("睦鄄诗火舍") | ✅ **完美**("乐山 3天2夜") |
| **副标题中文** | ❌ 乱码 | ⚠️ 1 字错("螽" 应为"爬") |
| **3D 软材质** | ⭐⭐ 弱 | ⭐⭐⭐⭐⭐ **惊艳** |
| **玻璃卡平台** | ❌ 无 | ✅ 完美呈现 |
| **整体风格** | 偏向 2D 插画 | 3D 写实 + 软材质 |
| **图标准确** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 结论

**Zhipu CogView-4 完胜 MiniMax-Image-01**(对当前 prompt 而言)。

**推荐组合**:
- **Zhipu CogView-4** 做封面 / 主图(3D 软材质)
- **沙盒内 PIL** 做多页信息图(中文 100% 准)
- 两者结合 = 最佳效果

## 使用方式

```bash
# 一键对比
python3 scripts/compare_providers.py trip.json out/ \
  --provider-a minimax --model-a image-01 \
  --provider-b zai --model-b cogview-4-250304

# 也可批量
for page in 01_cover 02_day1 03_day2 04_day3 05_day4; do
  python3 scripts/compare_providers.py prompts/${page}.md out/${page}/
done
```

## 真实文件

| 文件 | 描述 |
|---|---|
| `provider_comparison_sample.png` | 并排对比图(已带标签) |
| `a_minimax_sample.png` | MiniMax 单图 |
| `b_zai_sample.png` | Zhipu 单图 |
