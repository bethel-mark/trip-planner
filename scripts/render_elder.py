#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
老人/长辈友好大字版行程图生成器

设计原则:
- 大字体(标题 80pt, 正文 48pt, 提示 36pt)
- 高对比(深色文字 + 米白底)
- 一页一重点,不堆砌
- 朗读友好(结构清晰,TTS-friendly)
- 单列布局,无装饰干扰
- 极简 emoji(只用通用符号)
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from AppKit import NSAttributedString, NSFont, NSColor, NSBitmapImageRep, NSGraphicsContext
from Foundation import NSMakeSize
from io import BytesIO
import os, sys, json

W, H = 1080, 1440
OUTDIR_DEFAULT = "."

# ---------- 老人模式配色:米白 + 深色文字(高对比) ----------
COLOR_BG          = (250, 247, 240)  # 暖米白
COLOR_BG_DARK     = (60, 50, 40)     # 深棕(翻页底部)
COLOR_TEXT        = (40, 35, 30)     # 近黑(主文字)
COLOR_TEXT_SOFT   = (90, 80, 70)     # 浅棕(辅助文字)
COLOR_ACCENT      = (200, 60, 50)   # 砖红(强调/重点)
COLOR_LINE        = (180, 170, 155)  # 米灰(分隔线)
COLOR_HIGHLIGHT   = (255, 240, 200) # 浅黄(高亮框)

# ---------- Text ----------
def measure_text(text, font_size):
    ns_str = NSAttributedString.alloc().initWithString_attributes_(
        text, {'NSFont': NSFont.fontWithName_size_("Hiragino Sans GB", font_size)})
    s = ns_str.size()
    return int(s.width), int(s.height)

def render_text_img(text, font_size, fill_rgb=COLOR_TEXT, weight="bold"):
    """weight: 'bold' / 'regular' (用粗细区分字符;字号 40+ 时人眼可辨)"""
    try:
        # 中文:Hiragino Sans GB(支持 bold 通过 CTFontDescriptor)
        ns_str = NSAttributedString.alloc().initWithString_attributes_(
            text,
            {
                'NSFont': NSFont.fontWithName_size_("Hiragino Sans GB", font_size),
                'NSColor': NSColor.colorWithCalibratedRed_green_blue_alpha_(
                    fill_rgb[0]/255, fill_rgb[1]/255, fill_rgb[2]/255, 1.0)
            })
        size = ns_str.size()
        w_px = max(int(size.width) + 20, int(len(text)*font_size*0.7) + 10)
        h_px = max(int(size.height) + 20, int(font_size*1.6))
        rep = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_(
            None, w_px, h_px, 8, 4, True, False, "NSDeviceRGBColorSpace", 0, 32)
        NSGraphicsContext.saveGraphicsState()
        NSGraphicsContext.setCurrentContext_(NSGraphicsContext.graphicsContextWithBitmapImageRep_(rep))
        ns_str.drawAtPoint_((5, 5))
        NSGraphicsContext.restoreGraphicsState()
        png_data = rep.representationUsingType_properties_(4, {})
        pil = Image.open(BytesIO(bytes(png_data))).convert('RGBA')
        bbox = pil.getbbox()
        if bbox: pil = pil.crop(bbox)
        return pil
    except Exception as ex:
        return None

def paste_text(img, x, y, text, font_size, fill_rgb=COLOR_TEXT, weight="bold"):
    pil = render_text_img(text, font_size, fill_rgb, weight)
    if pil: img.alpha_composite(pil, (int(x), int(y)))
    return pil

def render_emoji(emoji, size=120):
    try:
        ns_str = NSAttributedString.alloc().initWithString_attributes_(
            emoji, {'NSFont': NSFont.fontWithName_size_("Apple Color Emoji", size)})
        pad = max(40, size // 2)
        w_px = size + pad * 2
        h_px = size + pad * 2
        rep = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_(
            None, w_px, h_px, 8, 4, True, False, "NSDeviceRGBColorSpace", 0, 32)
        NSGraphicsContext.saveGraphicsState()
        NSGraphicsContext.setCurrentContext_(NSGraphicsContext.graphicsContextWithBitmapImageRep_(rep))
        ns_str.drawAtPoint_((pad, pad))
        NSGraphicsContext.restoreGraphicsState()
        png_data = rep.representationUsingType_properties_(4, {})
        pil = Image.open(BytesIO(bytes(png_data))).convert('RGBA')
        bbox = pil.getbbox()
        if bbox: pil = pil.crop(bbox)
        return pil
    except: return None

def paste_emoji(img, x, y, emoji, size=120):
    pil = render_emoji(emoji, size)
    if pil:
        px = int(x - pil.width/2)
        py = int(y - pil.height)
        img.alpha_composite(pil, (px, py))

# ---------- Page 1: 封面(大字) ----------
def render_cover(data):
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    # 米白渐变
    for y in range(H):
        t = y / H
        r = int(250 - 15*t)
        g = int(247 - 18*t)
        b = int(240 - 25*t)
        ImageDraw.Draw(img).line([(0,y),(W,y)], fill=(r,g,b,255))

    # 大字标题(80pt)
    title = data["title"]
    tw, th = measure_text(title, 80)
    paste_text(img, (W-tw)//2, 200, title, 80, COLOR_TEXT, "bold")

    # 副标题
    subtitle = data.get("subtitle", "")
    if subtitle:
        sw, sh = measure_text(subtitle, 38)
        paste_text(img, (W-sw)//2, 350, subtitle, 38, COLOR_TEXT_SOFT, "regular")

    # 分隔线
    d = ImageDraw.Draw(img)
    d.line([(W//4, 460), (W*3//4, 460)], fill=COLOR_LINE, width=3)

    # 日期(60pt)
    date = data.get("date_range", "")
    dw, dh = measure_text(date, 60)
    paste_text(img, (W-dw)//2, 510, date, 60, COLOR_ACCENT, "bold")

    # 天数
    duration = data.get("duration", "")
    if duration:
        duw, _ = measure_text(duration, 44)
        paste_text(img, (W-duw)//2, 620, duration, 44, COLOR_TEXT, "regular")

    # 大 emoji
    hero_emoji = data.get("hero_emoji", "🌏")
    paste_emoji(img, W//2, 880, hero_emoji, 200)

    # 标语(底部)
    tagline = data.get("tagline", "")
    if tagline:
        tw2, _ = measure_text(tagline, 30)
        paste_text(img, (W-tw2)//2, H-180, tagline, 30, COLOR_TEXT_SOFT, "regular")

    # 提醒(超大)
    tip = data.get("tip", "此行程专为长辈设计 · 字体大 · 易读")
    tipw, _ = measure_text(tip, 24)
    paste_text(img, (W-tipw)//2, H-80, tip, 24, COLOR_TEXT_SOFT, "regular")

    fname = f"01_cover.png"
    img.convert('RGB').save(f"{OUTDIR_DEFAULT}/{fname}", 'PNG', optimize=True)

# ---------- Day 页面(大字版) ----------
def render_day(data):
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    for y in range(H):
        t = y / H
        r = int(250 - 15*t)
        g = int(247 - 18*t)
        b = int(240 - 25*t)
        ImageDraw.Draw(img).line([(0,y),(W,y)], fill=(r,g,b,255))

    # 顶部:Day 数字(超大 100pt)
    day_num = data["day"]
    paste_text(img, 100, 80, f"Day {day_num}", 100, COLOR_ACCENT, "bold")

    # 主题(大)
    title = data["day_title"]
    tw, _ = measure_text(title, 56)
    paste_text(img, W-tw-80, 110, title, 56, COLOR_TEXT, "bold")

    # 分隔粗线
    d = ImageDraw.Draw(img)
    d.line([(80, 220), (W-80, 220)], fill=COLOR_LINE, width=4)

    # 时间事件(每条占 200-220px)
    cur_y = 270
    for ev in data.get("events", [])[:4]:
        # 时间
        paste_text(img, 100, cur_y, ev["time"], 44, COLOR_ACCENT, "bold")
        # 地点 + emoji
        paste_emoji(img, 250, cur_y+30, ev.get("emoji", "📍"), 70)
        # 地点名(大字)
        paste_text(img, 320, cur_y+5, ev["place"][:18], 40, COLOR_TEXT, "bold")
        # 描述(中等字)
        desc = ev.get("desc", "")[:24]
        paste_text(img, 320, cur_y+55, desc, 26, COLOR_TEXT_SOFT, "regular")
        cur_y += 200

    # 分隔
    d.line([(80, cur_y+10), (W-80, cur_y+10)], fill=COLOR_LINE, width=3)

    # 提示(大字 36pt)
    cur_y += 50
    paste_text(img, 100, cur_y, "⚠️ 重要提醒", 40, COLOR_ACCENT, "bold")
    cur_y += 70
    for tip in data.get("tips", [])[:3]:
        # 圆点
        ov = Image.new('RGBA', img.size, (0,0,0,0))
        od = ImageDraw.Draw(ov)
        od.ellipse([100, cur_y+15, 122, cur_y+37], fill=COLOR_ACCENT+(255,))
        img.alpha_composite(ov)
        # 提示文字(36pt)
        text = tip[:50]
        paste_text(img, 140, cur_y, text, 32, COLOR_TEXT, "regular")
        cur_y += 70

    # 底部
    # 页面指示移到右上角(避开内容区,且和顶部 page_index 编号一致)
    paste_text(img, W-200, 80, f"第 {day_num} 天", 32, COLOR_TEXT_SOFT, "bold")

    fname = f"{day_num+1:02d}_day{day_num}.png"
    img.convert('RGB').save(f"{OUTDIR_DEFAULT}/{fname}", 'PNG', optimize=True)

# ---------- 应急联系页 ----------
def render_emergency(data):
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    for y in range(H):
        t = y / H
        r = int(250 - 15*t)
        g = int(247 - 18*t)
        b = int(240 - 25*t)
        ImageDraw.Draw(img).line([(0,y),(W,y)], fill=(r,g,b,255))

    # 大标题
    paste_text(img, 100, 100, "🆘 应急电话", 80, COLOR_ACCENT, "bold")

    # 分隔
    d = ImageDraw.Draw(img)
    d.line([(100, 230), (W-100, 230)], fill=COLOR_LINE, width=4)

    # 每个联系(超大字号)
    cur_y = 280
    for c in data.get("contacts", [])[:5]:
        paste_text(img, 100, cur_y, c.get("label", ""), 30, COLOR_TEXT_SOFT, "regular")
        cur_y += 50  # 标签和号码之间加大间距(原 40)
        paste_text(img, 100, cur_y, c.get("number", ""), 50, COLOR_TEXT, "bold")
        cur_y += 40  # 号码和下一项之间也加大(原 30)
        cur_y += 60  # 增加间距(原为 50),不画黄色干扰条

    # 底部提醒(居中,避开大数字)
    paste_text(img, (W-720)//2, H-100, "📱 长按此页可放大看 · 收藏到手机", 28, COLOR_TEXT_SOFT, "regular")

    fname = "08_emergency.png"
    img.convert('RGB').save(f"{OUTDIR_DEFAULT}/{fname}", 'PNG', optimize=True)

# ---------- 必备清单页 ----------
def render_essentials(data):
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    for y in range(H):
        t = y / H
        r = int(250 - 15*t)
        g = int(247 - 18*t)
        b = int(240 - 25*t)
        ImageDraw.Draw(img).line([(0,y),(W,y)], fill=(r,g,b,255))

    # 标题
    paste_text(img, 100, 100, "🎒 必带物品", 80, COLOR_ACCENT, "bold")
    paste_text(img, 100, 200, "⏰ 出发前 1 周打勾", 36, COLOR_TEXT_SOFT, "regular")

    # 分隔
    d = ImageDraw.Draw(img)
    d.line([(100, 270), (W-100, 270)], fill=COLOR_LINE, width=3)

    # 类别(2 列)
    cur_y = 320
    cats = data.get("categories", [])[:6]
    cat_h = 170
    for i, cat in enumerate(cats):
        col = i % 2
        row = i // 2
        x = 100 + col * 480
        y = cur_y + row * (cat_h + 30)
        # 类别标题
        paste_text(img, x, y, cat["name"], 38, COLOR_TEXT, "bold")
        # 物品(超大字)
        iy = y + 60
        for item in cat.get("items", [])[:3]:
            # 圆圈
            ov = Image.new('RGBA', img.size, (0,0,0,0))
            od = ImageDraw.Draw(ov)
            od.ellipse([x+4, iy+12, x+24, iy+32], outline=COLOR_ACCENT, width=3)
            img.alpha_composite(ov)
            paste_text(img, x+40, iy, item[:16], 32, COLOR_TEXT, "regular")
            iy += 50

    fname = "07_essentials.png"
    img.convert('RGB').save(f"{OUTDIR_DEFAULT}/{fname}", 'PNG', optimize=True)

# ---------- MAIN ----------
def render_trip_elder(trip, outdir="trip_elder"):
    global OUTDIR_DEFAULT
    os.makedirs(outdir, exist_ok=True)
    OUTDIR_DEFAULT = outdir

    print(f"开始生成老人大字版到 {outdir}/")
    print("="*50)

    # 封面
    cover = trip.get("cover", {})
    cover["page_index"] = 1
    cover["total_pages"] = len(trip.get("pages", [])) + 2
    render_cover(cover)
    print(f"  ✅ 01_cover.png (封面)")

    # 每天
    for i, page in enumerate(trip.get("pages", [])):
        page["page_index"] = i + 2
        page["total_pages"] = len(trip.get("pages", [])) + 2
        render_day(page)
        print(f"  ✅ {i+2:02d}_day{page['day']}.png (Day {page['day']}: {page['day_title']})")

    # 应急联系
    if "back" in trip:
        render_emergency(trip["back"])
        print(f"  ✅ 08_emergency.png (应急联系)")

    # 必备
    if "essentials" in trip:
        render_essentials(trip["essentials"])
        print(f"  ✅ 07_essentials.png (必备清单)")

    print("="*50)
    print(f"全部完成! {len(os.listdir(outdir))} 个文件已输出到 {outdir}/")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python render_elder.py <trip_data.json> <outdir>")
        sys.exit(1)
    trip = json.loads(open(sys.argv[1]).read())
    render_trip_elder(trip, sys.argv[2])
