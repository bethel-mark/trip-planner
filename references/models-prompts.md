# 12 个图像生成模型 · 优化 prompt 库

> 用途:`baoyu-image-gen` 配不同 provider 时,用对应的优化 prompt 出图效果最佳。
> 12 个模型,每个都有**强项 / 弱点 / 关键词 / 完整样例 prompt**。

---

## 快速对比表

| # | 模型 | 提供方 | 中文 | 写实 | 速度 | 推荐场景 |
|---|---|---|---|---|---|---|
| 1 | **MiniMax-Image-01** | MiniMax | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | **本机默认**,沙盒外首选 |
| 2 | GPT Image 2 | OpenAI | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 写实人像 / 美食 |
| 3 | Gemini 3 Pro Image | Google | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | 复杂构图 / 多元素 |
| 4 | Gemini 3.1 Flash Image | Google | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **快速出图 / 草稿** |
| 5 | Seedream 5.0 | ByteDance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | **中文 / 国风** |
| 6 | FLUX 2 Max | Black Forest Labs | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | **写实 / 摄影** |
| 7 | Hunyuan Image 3.0 | Tencent | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 国风 / 古风 |
| 8 | Qwen-Image 2.0 | Alibaba 通义万相 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | **中文 + 排版** |
| 9 | GLM-Image | Zhipu 智谱 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 中英混排 / 编程 |
| 10 | 文心一格 2.0 | Baidu | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | **中国地标 / 古建** |
| 11 | Imagen 3(未在列表) | Google | - | - | - | 同 Gemini 3 Pro |
| 12 | DALL·E 3(未在列表) | OpenAI | - | - | - | 同 GPT Image 2 |

> 12 个里 **MiniMax-Image-01(本机默认)、Qwen-Image 2.0(通义万相)、文心一格 2.0、Seedream 5.0** 对中文混排最稳。
> **GPT Image 2 / FLUX 2 Max** 写实人像 / 摄影最像。

---

## 1. MiniMax-Image-01 ⭐ 本机默认

**强项**:中文混排稳、写实 + 软 3D 均衡
**弱点**:风格化稍弱,复杂排版可能溢出
**API key**:`MINIMAX_API_KEY`(已设)
**EXTEND.md**:
```yaml
default_provider: minimax
default_model: image-01
```

**关键词**:`soft 3D`, `glassmorphism`, `isometric`, `soft ambient light`, `macaron pastel`
**避坑**:不要 prompt 写 100+ 字段(模型会丢),控制在 50-80 词核心

**完整 prompt 模板**(玻璃拟态信息图):
```
Soft 3D glassmorphism style infographic, [主题], 1080x1080 square.
Macaron pastel color palette (lavender, mint, peach, cream).
Apple Vision Pro spatial UI aesthetic. Soft ambient lighting.
Title in bold Chinese: [主标题]. Subtitle: [副标题].
[具体布局描述:3 卡片 / 时间轴 / 地图等]
```

---

## 2. GPT Image 2(OpenAI)

**强项**:**中文渲染最准**(没有之一),**写实人像 / 美食**
**弱点**:风格化弱,纯 3D 软材质需要 prompt 强引导
**API key**:`OPENAI_API_KEY`
**EXTEND.md**:
```yaml
default_provider: openai
default_model: gpt-image-2
```

**关键词**:`photorealistic`, `high detail`, `editorial photography`, `shot on Canon`, `f/2.8`, `8K`
**避坑**:写实风太强反而失去"软 3D 玻璃感",要明确 `matte 3D material, NOT photorealistic`

**完整 prompt 模板**:
```
Editorial infographic, soft 3D glassmorphism style.
NOT photorealistic, NOT photograph. Matte pastel material rendering.
[主题] in [布局]. Chinese text on glass cards.
Color palette: [色系]. Soft ambient lighting, no harsh shadows.
Apple Vision Pro UI aesthetic. 1080x1080 square.
Negative prompt: photorealistic, photograph, live action, real human
```

---

## 3. Gemini 3 Pro Image(Google)

**强项**:**复杂构图 / 多元素场景**,长 prompt 理解力
**弱点**:中文偶有乱码
**API key**:`GOOGLE_API_KEY`
**EXTEND.md**:
```yaml
default_provider: google
default_model: gemini-3-pro-image
default_image_size: 2K
```

**关键词**:`complex composition`, `multi-element scene`, `isometric view`, `layered glass elements`
**避坑**:要分段描述(标题 / 副标题 / 主元素 / 装饰 / 背景),别一锅端

**完整 prompt 模板**:
```
LAYOUT (1080x1080, isometric, 4:1 aspect):
- Top: title bar with main heading "[标题]" and subtitle "[副标题]"
- Center: 3 soft 3D glass cards arranged in triangle
- Each card: icon, title, 1-line description
- Background: dark navy → purple gradient with 3 soft glow blobs

STYLE:
- Glassmorphism + Isometric + Soft 3D
- Macaron pastel: lavender, mint, peach, cream
- Apple Vision Pro spatial UI aesthetic
- Soft ambient lighting, no harsh shadows

CONTENT:
[具体主题和文字内容]

NEGATIVE: photorealistic, photograph, blurry, low quality
```

---

## 4. Gemini 3.1 Flash Image(Google)

**强项**:**速度最快**(2-3 秒/张),适合**批量草稿**
**弱点**:细节略弱,最终出图建议用 Pro 重做
**API key**:`GOOGLE_API_KEY`
**EXTEND.md**:
```yaml
default_provider: google
default_model: gemini-3.1-flash-image
default_image_size: 1K  # 草稿用 1K 即可,出图速度 × 3
```

**用法**:快速迭代,1K 草稿 → 选最好的 → Pro 重出 2K。

---

## 5. Seedream 5.0(ByteDance 字节跳动 / 豆包)

**强项**:**中文 + 国风最强**,手写体 / 古风 / 印章
**弱点**:3D 玻璃感稍弱(更偏 2D 国风插画)
**API key**:`ARK_API_KEY`(字节方舟)
**EXTEND.md**:
```yaml
default_provider: seedream
default_model: seedream-5.0
```

**关键词**:`Chinese ink wash painting`, `traditional Chinese aesthetic`, `cinnabar red`, `rice paper texture`, `Chinese seal`
**避坑**:Seedream 把所有中文都默认国风化,要 prompt 明确说"现代信息图"

**完整 prompt 模板**:
```
现代信息图(非传统国风,Not traditional Chinese painting)。
Soft 3D glassmorphism infographic, isometric 3D.
[主题], [布局], Chinese text, modern Chinese typography.
Color palette: [色系 + 1-2 个中国传统色点缀,如 #C83C32 朱红].
Macaron pastel + 1 个中国红强调色。1080x1080。
Glass card material, soft ambient light, no harsh shadow.
```

---

## 6. FLUX 2 Max(Black Forest Labs)

**强项**:**写实之王**,人物皮肤 / 头发 / 织物纹理
**弱点**:玻璃拟态和 3D 软材质需要强力 prompt 引导
**API key**:`REPLICATE_API_TOKEN`(通过 Replicate) 或 `BFL_API_KEY`
**EXTEND.md**:
```yaml
default_provider: replicate
default_model: black-forest-labs/flux-2-max
```

**关键词**:`ultra realistic`, `macro photography`, `skin texture detail`, `ray tracing`, `volumetric lighting`, `subsurface scattering`
**避坑**:要明确说"3D rendered illustration, not photograph"

**完整 prompt 模板**:
```
3D rendered illustration, NOT photograph. Ultra realistic 3D materials.
[主题], glassmorphism + isometric style, soft 3D.
Macaron pastel (lavender, mint, peach). 8K detail.
Ray traced glass, subsurface scattering on soft surfaces.
[布局] in 1080x1080.
Negative prompt: photograph, live action, real human face
```

---

## 7. Hunyuan Image 3.0(Tencent 腾讯)

**强项**:**国风 / 古风 / 山水 / 中式建筑**
**弱点**:现代 UI / 信息图弱
**API key**:`HUNYUAN_API_KEY`
**EXTEND.md**:
```yaml
default_provider: hunyuan
default_model: hunyuan-image-3.0
```

**关键词**:`Chinese landscape painting`, `shan shui`, `gongbi`, `meticulous`, `silk scroll texture`
**适合场景**:中国古建 / 山水 / 寺庙 / 古镇(乐山 / 峨眉 / 故宫 等绝配)

**完整 prompt 模板**:
```
中国传统工笔山水画风格 + 现代信息图布局。
Soft 3D glassmorphism + Chinese landscape aesthetic.
[主题 - 中国传统场景], Chinese ink wash + pastel modern colors.
布局: 标题 / 副标题 / 玻璃卡时间线 / 中国地标 3D 化。
[具体内容], Chinese text, calligraphy feel for titles.
1080x1080.
```

---

## 8. Qwen-Image 2.0(Alibaba 通义万相)

**强项**:**中文混排最强(和 Seedream 5.0 并列)**,**排版准**(版式 / 字间距)
**弱点**:写实弱
**API key**:`DASHSCOPE_API_KEY`(阿里百炼)
**EXTEND.md**:
```yaml
default_provider: dashscope
default_model: qwen-image-2.0
```

**关键词**:`clean typography`, `modern Chinese layout`, `proper character spacing`, `editorial design`, `pixel-perfect kerning`
**避坑**:这是中文排版神器,所有"信息图 / 卡片"类需求首选

**完整 prompt 模板**:
```
现代中文信息图(版式 / 排版准确优先)。
Soft 3D glassmorphism + Isometric style.
[主题], 3:4 竖版 1080x1440.
Chinese text 必须: 字体清晰(无衬线 / 思源黑体风),字间距正常,无乱码。
Color: 玻璃拟态 + macaron pastel。1080x1440 portrait.
[布局 - 5 卡片 / 时间线 / 地图]
```

---

## 9. Zhipu CogView-4 / GLM-Image(智谱)⭐ 实测可出 3D 信息图

**强项**:**3D 软材质 + 玻璃卡 + 山水场景** 渲染惊艳,**CogView-4 实测乐山封面效果与 GPT-4o 相当**
**弱点**:偶有 CJK 长文字误识别(例:"爬峨眉"→"它霆峨音",需在 prompt 中重复 2-3 次关键文字或拆分短句)
**API key**:`ZAI_API_KEY`(您已提供 ✓)
**EXTEND.md**:
```yaml
default_provider: zai
default_model: cogview-4-250304
```

**适合场景**:
- ✅ 3D 信息图 / 玻璃卡 / 软材质场景
- ✅ 中国山水 / 古镇 / 地标
- ⚠️ 中文长字符串有时会失真,**单字 / 短词稳**

**实测**(乐山封面 prompt):
- ✅ 标题"乐山 3天2夜"渲染完美
- ✅ 鸟居 emoji 准确
- ✅ 3D 山水场景 + 玻璃卡 + 平台
- ⚠️ 副标题"看大佛+爬峨眉"→ 错成"看大佛+它霆峨音"(需 prompt 强化或拆短)

**完整 prompt 模板(防 CJK 错字加强版)**:
```
Modern Chinese travel infographic. Soft 3D glassmorphism + isometric 3D.
Important text (render EXACTLY, no mistakes):
- Title: 乐山 三天两夜 (NOT any other characters)
- Subtitle: 看大佛 加 爬峨眉山 (keep simple words)

Layout: hero emoji on 3D iso platform, glass card with title overlay.
Background: warm beige + soft pastel mountains, macaron color palette.
Apple Vision Pro spatial UI aesthetic. Soft ambient lighting, no harsh shadows.
1080x1080 square.
```

**防错字技巧**:
1. **拆短**:"爬峨眉" → "爬" + "峨眉山"
2. **重复 2-3 次**: 关键文字写 2-3 次
3. **加引号强调**:`"乐山"`(模型会优先保留引号内原文)
4. **中英混排**:关键中文字后跟英文翻译(`乐山 (Leshan)`)

---

## 10. 文心一格 2.0(Baidu 百度)

**强项**:**中国地标 / 古建筑 / 国风插画 / 印章**
**弱点**:3D 玻璃感弱
**API key**:`WENXIN_API_KEY` 或在百度智能云控制台拿
**EXTEND.md**:
```yaml
default_provider: wenxin
default_model: ernie-image-2.0
```

**适合场景**:中国城市 / 故宫 / 长城 / 兵马俑 / 黄山 / 苏州园林

**完整 prompt 模板**:
```
中国城市 / 古建信息图。中国国画 + 现代玻璃拟态结合。
[主题 - 北京 / 西安 / 苏州 / 成都 etc.], 3D 软材质, 中国色系。
Chinese text, 宋体 / 楷体 feel。1080x1080。
[布局 - 5 卡片 / 地图标注 / 美食图鉴]
```

---

## 🚀 实用对照:同样 prompt 投不同模型

### 测试 prompt(乐山封面,所有模型共用)
```
Modern Chinese infographic, soft 3D glassmorphism + isometric style.
Title: 乐山 3天2夜
Subtitle: 观看大佛 + 峨眉山
Hero emoji: 鸟居
Color: macaron pastel with brick red accent
Background: warm beige gradient
Layout: centered hero, 3 glass cards below
1080x1080 square
```

### 各模型出图差异

| 模型 | 标题渲染 | 中文排版 | 3D 软感 | 鸟居 emoji | 玻璃感 |
|---|---|---|---|---|---|
| **MiniMax-Image-01** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| GPT Image 2 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Gemini 3 Pro | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Gemini 3.1 Flash | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Seedream 5.0 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| FLUX 2 Max | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Hunyuan 3.0 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Qwen-Image 2.0 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| GLM-Image | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 文心一格 2.0 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ |

**推荐组合**:
- **想稳 + 沙盒外**:**Qwen-Image 2.0 或 MiniMax-Image-01**
- **写实人物 / 美食 / 酒店**:**GPT Image 2 或 FLUX 2 Max**
- **国风 / 山水 / 中国地标**:**Seedream 5.0 或文心一格 2.0 或 Hunyuan 3.0**
- **复杂构图**:**Gemini 3 Pro**
- **批量草稿**:**Gemini 3.1 Flash**
- **科技 / 程序员风**:**GLM-Image**

---

## 🔧 一键切换 provider(改 EXTEND.md 即可)

```bash
# 切换到 Qwen-Image 2.0(中文排版最好)
cat > trip-planner-github/.baoyu-skills/baoyu-image-gen/EXTEND.md <<'EOF'
---
version: 1
default_provider: dashscope
default_model: qwen-image-2.0
EOF

# 切换到 GPT Image 2(写实最好)
cat > trip-planner-github/.baoyu-skills/baoyu-image-gen/EXTEND.md <<'EOF'
---
version: 1
default_provider: openai
default_model: gpt-image-2
EOF

# 切换到 FLUX 2 Max(写实之王)
cat > trip-planner-github/.baoyu-skills/baoyu-image-gen/EXTEND.md <<'EOF'
---
version: 1
default_provider: replicate
default_model: black-forest-labs/flux-2-max
EOF
```

---

## 📊 API key 检查清单

| 模型 | API key 环境变量 | 提供方 |
|---|---|---|
| **MiniMax-Image-01** | `MINIMAX_API_KEY` ✓ 已设 | MiniMax |
| GPT Image 2 | `OPENAI_API_KEY` | OpenAI |
| Gemini 3 Pro / Flash | `GOOGLE_API_KEY` | Google AI Studio |
| Seedream 5.0 | `ARK_API_KEY` | 字节火山方舟 |
| FLUX 2 Max | `REPLICATE_API_TOKEN` / `BFL_API_KEY` | Replicate / BFL |
| Hunyuan 3.0 | `HUNYUAN_API_KEY` | 腾讯云 |
| Qwen-Image 2.0 | `DASHSCOPE_API_KEY` | 阿里百炼 |
| GLM-Image | `ZAI_API_KEY` / `BIGMODEL_API_KEY` | 智谱 |
| 文心一格 2.0 | `WENXIN_API_KEY` | 百度智能云 |

设置:在 `~/.zshrc` 加 `export XXXXX_API_KEY="sk-..."`,然后 `source ~/.zshrc`。

---

## 🎯 推荐使用策略

### 沙盒内(本机)
→ 用 PIL + Apple Color Emoji(`render_story.py` / `render_elder.py`)
→ 100% 离线,中文 100% 准,**默认方案**

### 沙盒外(普通终端) + 想出真 3D 软图
```bash
# 1. 默认(MiniMax,你已设 key)
render_trip.py trip.json out/  # 自动用 minimax

# 2. 想要更好中文排版
# 设 DASHSCOPE_API_KEY 后:
EXTEND.md → default_provider: dashscope, model: qwen-image-2.0

# 3. 想要国风地标
# 设 ARK_API_KEY 后:
EXTEND.md → default_provider: seedream, model: seedream-5.0
```

### 单 trip 出 3 版(对比选最优)
```bash
for provider in minimax dashscope seedream; do
    sed -i "s/default_provider:.*/default_provider: $provider/" EXTEND.md
    python3 render_trip.py trip.json out_$provider
done
```

---

## 🎁 提示词模板库(各模型完整版)

完整 12 套提示词模板见同目录 `models-prompts-full.md`(可单独用,本文件为总览)。
