#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3:4 多页图片版生成器(玻璃拟态 + 等距 3D + Soft 3D)
- 适合小红书 / 朋友圈 / Instagram Story
- 每页 1080×1440(3:4 标准竖版)
- 一键生成 N 页 PNG
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from AppKit import NSAttributedString, NSFont, NSColor, NSBitmapImageRep, NSGraphicsContext
from Foundation import NSMakeSize
from io import BytesIO
import os, sys, json

W, H = 1080, 1440  # 3:4
OUTDIR_DEFAULT = "."

# ---------- Color helpers ----------
def rgb(r,g,b): return (r,g,b,255)

# ---------- Text / Emoji ----------
def measure_text(text, font_size):
    ns_str = NSAttributedString.alloc().initWithString_attributes_(
        text, {'NSFont': NSFont.fontWithName_size_("Hiragino Sans GB", font_size)})
    s = ns_str.size()
    return int(s.width), int(s.height)

def render_emoji(emoji, size=120):
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

def render_text_img(text, font_size, fill_rgb=(255,255,255)):
    try:
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
    except Exception:
        return None

def paste_text(img, x, y, text, font_size, fill_rgb=(255,255,255)):
    pil = render_text_img(text, font_size, fill_rgb)
    if pil: img.alpha_composite(pil, (int(x), int(y)))
    return pil

def paste_emoji(img, x, y, emoji, size=120, center=True):
    pil = render_emoji(emoji, size)
    px = int(x - pil.width / 2)
    py = int(y - pil.height / 2) if center else int(y - pil.height)
    img.alpha_composite(pil, (px, py))

# ---------- Background ----------
def draw_background(img, palette="purple"):
    palettes = {
        "purple": [(15,12,48),(45,20,75),(75,40,100)],  # navy → purple
        "coral":  [(40,15,30),(80,30,50),(120,55,75)],  # dark coral
        "teal":   [(10,25,40),(20,60,80),(40,100,120)],  # navy → teal
        "lavender":[(20,15,40),(60,50,90),(100,90,140)],
        "warm":   [(40,25,15),(80,55,30),(120,90,55)],
    }
    r1, g1, b1 = palettes[palette][0]
    r2, g2, b2 = palettes[palette][2]
    for y in range(H):
        t = y / H
        r = int(r1 + (r2-r1)*t**1.2)
        g = int(g1 + (g2-g1)*t**1.2)
        b = int(b1 + (b2-b1)*t**1.2)
        ImageDraw.Draw(img).line([(0,y),(W,y)], fill=rgb(r,g,b))

def glow(img, cx, cy, radius, color, alpha=160, blur=70):
    ov = Image.new('RGBA', img.size, (0,0,0,0))
    ImageDraw.Draw(ov).ellipse([cx-radius,cy-radius,cx+radius,cy+radius], fill=color+(alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(ov)

# ---------- Glass card ----------
def draw_glass_card(img, x, y, w, h, fill=(255,255,255), alpha=42,
                    border=(255,255,255,180), border_w=2, radius=24, shadow=True):
    if shadow:
        sh = Image.new('RGBA', img.size, (0,0,0,0))
        for off, a in [(8,30),(16,18),(24,8)]:
            ImageDraw.Draw(sh).rounded_rectangle([x+off,y+off,x+w+off,y+h+off],
                                    radius=radius, fill=(0,0,0,a))
        sh = sh.filter(ImageFilter.GaussianBlur(20))
        img.alpha_composite(sh)
    glass = Image.new('RGBA', img.size, (0,0,0,0))
    gd = ImageDraw.Draw(glass)
    gd.rounded_rectangle([x,y,x+w,y+h], radius=radius,
                         fill=fill+(alpha,), outline=border, width=border_w)
    for i in range(6):
        gd.line([(x+radius-i, y+i+2),(x+w-radius+i, y+i+2)],
                fill=(255,255,255, max(0,90-i*15)))
    img.alpha_composite(glass)

def glass_card_for_text(img, text, font_size, top_y, left_x=40,
                        fill=(255,255,255), alpha=80, border=(255,255,255,220),
                        radius=22, pad_x=28, pad_y=14):
    tw, th = measure_text(text, font_size)
    card_w = tw + pad_x * 2
    card_h = th + pad_y * 2
    draw_glass_card(img, int(left_x), int(top_y), card_w, card_h,
                    fill=fill, alpha=alpha, border=border, radius=radius)
    paste_text(img, left_x + pad_x, top_y + pad_y, text, font_size, (255,255,255))
    return card_w, card_h

# ---------- Isometric ----------
def iso_project(x, y, z=0):
    sx = x - y
    sy = (x + y) * 0.5 - z
    return sx, sy

def draw_iso_platform(img, cx, cy, w=120, d=120, h=24,
                       top=(255,255,255,80), left=(200,200,220,140), right=(180,180,200,160)):
    hw, hd, hh = w/2, d/2, h
    corners = [(-hw,-hd,0),(hw,-hd,0),(hw,hd,0),(-hw,hd,0),
               (-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]
    pts = [(cx+iso_project(*c)[0], cy+iso_project(*c)[1]) for c in corners]
    iso = Image.new('RGBA', img.size, (0,0,0,0))
    d_ = ImageDraw.Draw(iso)
    d_.polygon([pts[1],pts[2],pts[6],pts[5]], fill=right)
    d_.polygon([pts[0],pts[1],pts[5],pts[4]], fill=left)
    d_.polygon([pts[4],pts[5],pts[6],pts[7]], fill=top)
    for a, b in [(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:
        d_.line([pts[a],pts[b]], fill=(255,255,255,90), width=2)
    img.alpha_composite(iso)

def icon_on_platform(img, cx, cy_top, emoji, size=110,
                     plat_w=140, plat_d=140, plat_h=22):
    draw_iso_platform(img, cx, cy_top+10, plat_w, plat_d, plat_h)
    paste_emoji(img, cx, cy_top + 10, emoji, size, center=False)

# ============= PAGE 1: COVER =============
def render_cover(data):
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    palette = data.get("palette", "purple")
    draw_background(img, palette)
    
    # Glow blobs
    glow(img, 200, 250, 250, (90,120,255), alpha=140, blur=90)
    glow(img, W-200, 400, 280, (200,80,200), alpha=120, blur=100)
    glow(img, W//2, H-200, 350, (80,220,180), alpha=100, blur=110)
    
    # Page number badge (top-right)
    page_n = f"{data['page_index']:02d} / {data['total_pages']:02d}"
    glass_card_for_text(img, page_n, 16, 30, left_x=W-130,
                        fill=(255,255,255), alpha=40, border=(255,255,255,150),
                        pad_x=14, pad_y=6)
    
    # Big hero emoji (center top)
    hero_emoji = data.get("hero_emoji", "✈️")
    paste_emoji(img, W//2, 480, hero_emoji, 280)
    
    # Trip title (big, bold)
    title = data["title"]
    tw, th = measure_text(title, 60)
    if tw > W - 80:
        # Auto-split title to two lines
        words = title.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        paste_text(img, (W-min(measure_text(line1,60)[0], W-80))//2, 600, line1, 60, (255,255,255))
        paste_text(img, (W-min(measure_text(line2,60)[0], W-80))//2, 680, line2, 60, (255,255,255))
    else:
        paste_text(img, (W-tw)//2, 620, title, 60, (255,255,255))
    
    # Subtitle (route)
    subtitle = data.get("subtitle", "")
    if subtitle:
        sw, sh = measure_text(subtitle, 26)
        paste_text(img, (W-sw)//2, 790, subtitle, 26, (200,220,255))
    
    # Date / duration card
    info = f"📅 {data['date_range']}  ·  {data['duration']}  ·  {data.get('travelers', '2 人')}"
    info_w, info_h = measure_text(info, 22)
    draw_glass_card(img, (W-info_w)//2 - 24, 880, info_w + 48, info_h + 28,
                    fill=(255,255,255), alpha=60, border=(255,255,255,200), radius=20)
    paste_text(img, (W-info_w)//2, 882+14, info, 22, (255,255,255))
    
    # Tagline at bottom
    tagline = data.get("tagline", "")
    if tagline:
        tw2, th2 = measure_text(tagline, 22)
        paste_text(img, (W-tw2)//2, 1100, tagline, 22, (255,200,150))
    
    # Bottom brand
    paste_text(img, W-200, H-50, "📱 长按可分享", 16, (180,200,220))
    
    img.convert('RGB').save(f"{OUTDIR_DEFAULT}/01_cover.png", 'PNG', optimize=True)
    return img

# ============= PAGE N: DAY OVERVIEW =============
def render_day(data):
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    palette = data.get("palette", "purple")
    draw_background(img, palette)
    # Ensure color is tuple (JSON may give list)
    color = data.get("color", (100, 200, 230))
    if isinstance(color, list):
        color = tuple(color)
    glow(img, 200, 250, 250, (90,120,255), alpha=120, blur=90)
    glow(img, W-200, 500, 280, (200,80,200), alpha=100, blur=100)
    
    # Page number
    page_n = f"{data['page_index']:02d} / {data['total_pages']:02d}"
    glass_card_for_text(img, page_n, 16, 30, left_x=W-130,
                        fill=(255,255,255), alpha=40, border=(255,255,255,150),
                        pad_x=14, pad_y=6)
    
    # Day badge (big circle top-left)
    day_num = data["day"]
    # Big number background
    ov = Image.new('RGBA', img.size, (0,0,0,0))
    od = ImageDraw.Draw(ov)
    od.ellipse([60, 90, 220, 250], fill=color+(180,), outline=(255,255,255,255), width=4)
    img.alpha_composite(ov)
    paste_text(img, 100, 130, f"Day", 24, (255,255,255))
    paste_text(img, 113, 162, f"{day_num}", 56, (255,255,255))
    
    # Day title
    title = data["day_title"]
    paste_text(img, 260, 130, title, 30, (255,255,255))
    # Date
    if "date" in data:
        paste_text(img, 260, 175, data["date"], 18, (200,220,255))
    
    # Theme subtitle
    if "theme" in data:
        tw, _ = measure_text(data["theme"], 20)
        draw_glass_card(img, 60, 270, tw+48, 50,
                        fill=color, alpha=80, border=color+(200,), radius=16)
        paste_text(img, 84, 285, data["theme"], 20, (255,255,255))
    
    # Timeline events (compact, 5-6 events)
    cur_y = 360
    for ev in data.get("events", [])[:6]:
        # Time + emoji + place
        time_x = 60
        ov = Image.new('RGBA', img.size, (0,0,0,0))
        od = ImageDraw.Draw(ov)
        od.rounded_rectangle([time_x, cur_y, time_x+90, cur_y+44],
                            radius=10, fill=color+(200,))
        img.alpha_composite(ov)
        tw, _ = measure_text(ev["time"], 18)
        paste_text(img, time_x + (90-tw)//2, cur_y+12, ev["time"], 18, (255,255,255))
        
        # Place + emoji
        paste_emoji(img, time_x+135, cur_y+22, ev.get("emoji", "📍"), 36)
        place_x = time_x + 170
        paste_text(img, place_x, cur_y+5, ev["place"], 22, (255,255,255))
        if "desc" in ev:
            paste_text(img, place_x, cur_y+30, ev["desc"][:38], 15, (200,215,235))
        cur_y += 70
    
    # Tips section at bottom
    if data.get("tips"):
        # Section header
        tips_y = 850
        glass_card_for_text(img, "⚠️ 关键 tips", 22, tips_y, left_x=60,
                            fill=(255,180,100), alpha=100, border=(255,200,140,220),
                            pad_x=20, pad_y=10)
        # Tips
        ty = tips_y + 70
        for tip in data["tips"][:5]:
            # Bullet
            ov = Image.new('RGBA', img.size, (0,0,0,0))
            od = ImageDraw.Draw(ov)
            od.ellipse([75, ty+8, 88, ty+21], fill=(255,200,100,255))
            img.alpha_composite(ov)
            # Wrap text
            max_chars = 28
            if len(tip) > max_chars:
                cut = tip.rfind(' ', 0, max_chars)
                if cut < 1: cut = max_chars
                line1 = tip[:cut]
                line2 = tip[cut:].lstrip()
            else:
                line1, line2 = tip, None
            paste_text(img, 100, ty, line1, 17, (240,235,220))
            if line2:
                paste_text(img, 100, ty+22, line2, 17, (240,235,220))
            ty += 22 + (22 if line2 else 0) + 8
    
    # Cost badge (top-right)
    if "cost" in data:
        cost = data["cost"]
        cw, ch = measure_text(cost, 18)
        draw_glass_card(img, W-220, 270, 180, ch+28,
                        fill=(80,200,160), alpha=80, border=(150,230,200,220), radius=16)
        paste_text(img, W-220+90-cw//2, 270+14, cost, 18, (255,255,255))
    
    # Bottom page number
    paste_text(img, W//2-30, H-50, f"📄 第 {data['page_index']} / {data['total_pages']} 页", 16, (180,200,220))
    
    fname = f"{data['page_index']:02d}_day{day_num}.png"
    img.convert('RGB').save(f"{OUTDIR_DEFAULT}/{fname}", 'PNG', optimize=True)
    return img

# ============= PAGE: ESSENTIALS =============
def render_essentials(data):
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    draw_background(img, "teal")
    glow(img, 200, 200, 250, (80,200,180), alpha=120, blur=90)
    glow(img, W-200, 600, 250, (200,80,200), alpha=100, blur=100)

    page_n = f"{data['page_index']:02d} / {data['total_pages']:02d}"
    glass_card_for_text(img, page_n, 16, 30, left_x=W-130, fill=(255,255,255), alpha=40, border=(255,255,255,150), pad_x=14, pad_y=6)

    paste_text(img, 60, 80, data.get("title", "🎒 出行必备"), 44, (255,255,255))
    paste_text(img, 60, 135, data.get("subtitle", "出发前 1 周对照打勾"), 20, (200,230,210))

    # Divider
    d = ImageDraw.Draw(img)
    d.line([(60, 175), (W-60, 175)], fill=(255,255,255,60), width=1)

    # Categories (6 categories, 2 columns) - compact design to make room
    categories = data.get("categories", [])
    cat_w = (W - 60*2 - 24) // 2
    cat_h = 165
    for i, cat in enumerate(categories[:6]):
        col = i % 2; row = i // 2
        x = 60 + col * (cat_w + 24)
        y = 200 + row * (cat_h + 20)
        draw_glass_card(img, x, y, cat_w, cat_h, fill=(255,255,255), alpha=18, border=(255,255,255,60), radius=18)
        paste_emoji(img, x+35, y+28, cat["icon"], 28)
        paste_text(img, x+65, y+18, cat["name"], 18, (255,255,255))
        iy = y + 55
        for item in cat["items"][:5]:
            ov = Image.new('RGBA', img.size, (0,0,0,0))
            od = ImageDraw.Draw(ov)
            od.rectangle([x+15, iy+4, x+23, iy+12], outline=(200,220,210,200), width=2)
            img.alpha_composite(ov)
            paste_text(img, x+32, iy-3, item[:24], 12, (220,230,210))
            iy += 18

    # Pre-departure timeline at bottom
    cats_end = 200 + 3 * (cat_h + 20)
    draw_glass_card(img, 60, cats_end, W-120, 75, fill=(100,220,200), alpha=40, border=(150,240,220,150), radius=18)
    paste_text(img, 80, cats_end+10, "⏰ 打勾时间线", 18, (255,255,255))
    timeline_text = "1周前:买SIM卡・订ETS票・换泰铢  |  1天前:打包行李・装APP  |  出发:检查护照"
    paste_text(img, 80, cats_end+42, timeline_text, 14, (200,255,240))

    if data.get("footer"):
        paste_text(img, 60, H-50, data["footer"], 16, (255,200,150))

    fname = f"{data['page_index']:02d}_essentials.png"
    img.convert('RGB').save(f"{OUTDIR_DEFAULT}/{fname}", 'PNG', optimize=True)
    return img

# ============= PAGE: COST =============
def render_cost(data):
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    draw_background(img, "warm")
    glow(img, 200, 250, 250, (255,160,80), alpha=120, blur=90)
    glow(img, W-200, 500, 280, (200,80,200), alpha=100, blur=100)

    page_n = f"{data['page_index']:02d} / {data['total_pages']:02d}"
    glass_card_for_text(img, page_n, 16, 30, left_x=W-130, fill=(255,255,255), alpha=40, border=(255,255,255,150), pad_x=14, pad_y=6)

    paste_text(img, 60, 80, data.get("title", "💰 成本拆解"), 44, (255,255,255))
    paste_text(img, 60, 135, data.get("subtitle", ""), 20, (255,220,180))

    # Big total card
    total = data.get("total", "RM 0")
    tw, th = measure_text(total, 70)
    total_card_w = W - 120
    draw_glass_card(img, 60, 200, total_card_w, 155, fill=(255,180,80), alpha=80, border=(255,210,140,220), radius=24)
    paste_text(img, 60 + (total_card_w - tw)//2, 220, total, 70, (255,255,255))
    if "per_person" in data:
        pw, ph = measure_text(data["per_person"], 20)
        paste_text(img, 60 + (total_card_w - pw)//2, 305, data["per_person"], 20, (255,255,255))

    # Cost breakdown (6 items, 2 columns)
    items = data.get("items", [])[:8]
    col_w = (W - 60*2 - 30) // 2
    for i, item in enumerate(items):
        col = i % 2; row = i // 2
        x = 60 + col * (col_w + 30)
        y = 390 + row * 108
        draw_glass_card(img, x, y, col_w, 90, fill=(255,255,255), alpha=20, border=(255,255,255,80), radius=18)
        paste_emoji(img, x+40, y+28, item.get("icon", "💵"), 26)
        paste_text(img, x+78, y+14, item.get("category", "")[:14], 16, (255,255,255))
        paste_text(img, x+78, y+36, item.get("desc", "")[:24], 12, (220,210,200))
        amt = item.get("amount", "")
        aw, ah = measure_text(amt, 20)
        paste_text(img, x + col_w - aw - 15, y + 55, amt, 20, (255,255,200))

    # Savings tips section
    items_end = 390 + (len(items)+1)//2 * 108 + 30
    tips_data = data.get("saving_tips", ["💡 住宿选Lee Garden附近可步行省打车费", "🍜 路边摊比商场便宜50% ・味道一样好"])
    draw_glass_card(img, 60, items_end, W-120, 85, fill=(255,200,100), alpha=55, border=(255,220,150,180), radius=18)
    paste_text(img, 80, items_end+12, "💰 省钱贴士", 18, (255,255,255))
    for j, tip in enumerate(tips_data[:2]):
        paste_text(img, 80, items_end + 40 + j*22, tip, 15, (255,255,230))

    if data.get("tip"):
        paste_text(img, 60, H-50, data["tip"], 16, (255,200,150))

    fname = f"{data['page_index']:02d}_cost.png"
    img.convert('RGB').save(f"{OUTDIR_DEFAULT}/{fname}", 'PNG', optimize=True)
    return img


# ============= PAGE: SOUVENIRS =============
def render_souvenirs(data):
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    draw_background(img, "warm")
    glow(img, 200, 250, 250, (255,180,100), alpha=120, blur=90)
    glow(img, W-200, 500, 280, (200,80,200), alpha=100, blur=100)

    page_n = f"{data['page_index']:02d} / {data['total_pages']:02d}"
    glass_card_for_text(img, page_n, 16, 30, left_x=W-130, fill=(255,255,255), alpha=40, border=(255,255,255,150), pad_x=14, pad_y=6)

    paste_text(img, 60, 80, data.get("title", "🎁 回程必带"), 44, (255,255,255))
    paste_text(img, 60, 135, data.get("subtitle", ""), 20, (255,220,180))

    # Divider line
    d = ImageDraw.Draw(img)
    d.line([(60, 175), (W-60, 175)], fill=(255,255,255,60), width=1)

    items = data.get("items", [])[:8]
    col_w = (W - 60*2 - 30) // 2
    for i, item in enumerate(items):
        col = i % 2; row = i // 2
        x = 60 + col * (col_w + 30)
        y = 210 + row * 130
        draw_glass_card(img, x, y, col_w, 110, fill=(255,255,255), alpha=22, border=(255,255,255,80), radius=18)
        paste_emoji(img, x+40, y+32, item.get("icon", "🎁"), 32)
        paste_text(img, x+80, y+12, item.get("name", "")[:14], 18, (255,255,255))
        paste_text(img, x+80, y+40, item.get("desc", "")[:26], 13, (210,200,190))
        price = item.get("price", "")
        paste_text(img, x+80, y+62, price, 16, (255,200,100))

    # Tips section
    tips = data.get("tips", ["💡 Big C 满2000 THB可退税", "⚠️ 烟酒限额:200支+1L", "🏪 7-11最后补货机会"])
    ty = 210 + min(len(items),8)//2 * 130 + 30
    draw_glass_card(img, 60, ty, W-120, 90, fill=(255,200,100), alpha=60, border=(255,220,150,180), radius=18)
    paste_text(img, 80, ty+12, "💡 购物贴士", 18, (255,255,255))
    for j, t in enumerate(tips[:2]):
        paste_text(img, 80, ty + 42 + j*24, t, 15, (255,255,230))

    fname = f"{data['page_index']:02d}_souvenirs.png"
    img.convert('RGB').save(f"{OUTDIR_DEFAULT}/{fname}", 'PNG', optimize=True)
    return img

# ============= PAGE: APPS =============
def render_apps(data):
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    draw_background(img, "teal")
    glow(img, 200, 250, 250, (80,200,180), alpha=120, blur=90)
    glow(img, W-200, 600, 250, (200,80,200), alpha=100, blur=100)

    page_n = f"{data['page_index']:02d} / {data['total_pages']:02d}"
    glass_card_for_text(img, page_n, 16, 30, left_x=W-130, fill=(255,255,255), alpha=40, border=(255,255,255,150), pad_x=14, pad_y=6)

    paste_text(img, 60, 80, data.get("title", "📱 实用APP"), 44, (255,255,255))
    paste_text(img, 60, 135, data.get("subtitle", "出发前装好"), 20, (200,230,210))

    # Divider
    d = ImageDraw.Draw(img)
    d.line([(60, 175), (W-60, 175)], fill=(255,255,255,60), width=1)

    items = data.get("items", [])[:8]
    col_w = (W - 60*2 - 30) // 2
    for i, item in enumerate(items):
        col = i % 2; row = i // 2
        x = 60 + col * (col_w + 30)
        y = 210 + row * 115
        draw_glass_card(img, x, y, col_w, 95, fill=(255,255,255), alpha=22, border=(255,255,255,80), radius=18)
        paste_emoji(img, x+40, y+28, item.get("icon", "📱"), 28)
        paste_text(img, x+80, y+14, item.get("name", "")[:16], 18, (255,255,255))
        paste_text(img, x+80, y+40, item.get("desc", "")[:30], 12, (200,220,210))

    # Installation guide section
    apps_end_y = 210 + min(len(items),8)//2 * 115 + 40
    draw_glass_card(img, 60, apps_end_y, W-120, 85, fill=(100,220,200), alpha=50, border=(150,240,220,180), radius=18)
    paste_text(img, 80, apps_end_y+12, "📲 安装方式", 18, (255,255,255))
    paste_text(img, 80, apps_end_y+38, "App Store / Play Store 搜索名称下载", 15, (200,255,240))
    paste_text(img, 80, apps_end_y+58, "泰国 SIM 卡 7-11 有售 . RM 10-15/7天", 15, (200,255,240))

    if data.get("footer"):
        paste_text(img, 60, H-50, data["footer"], 16, (200,255,200))

    fname = f"{data['page_index']:02d}_apps.png"
    img.convert('RGB').save(f"{OUTDIR_DEFAULT}/{fname}", 'PNG', optimize=True)
    return img

# ============= PAGE: BACK =============
def render_back(data):
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    draw_background(img, "lavender")
    glow(img, W//2, H//2, 400, (160,120,220), alpha=120, blur=120)
    
    # Page number
    page_n = f"{data['page_index']:02d} / {data['total_pages']:02d}"
    glass_card_for_text(img, page_n, 16, 30, left_x=W-130,
                        fill=(255,255,255), alpha=40, border=(255,255,255,150),
                        pad_x=14, pad_y=6)
    
    # Title
    paste_text(img, 60, 200, data.get("title", "🆘 应急联系"), 44, (255,255,255))
    paste_text(img, 60, 260, data.get("subtitle", "收藏到手机,真出事时一查就有"), 20, (220,210,240))
    
    # Contacts
    contacts = data.get("contacts", [])[:6]
    cy = 340
    for c in contacts:
        draw_glass_card(img, 60, cy, W-120, 80,
                        fill=(255,255,255), alpha=22, border=(255,255,255,80), radius=18)
        # Emoji
        paste_emoji(img, 110, cy+40, c.get("icon", "📞"), 32)
        # Label
        paste_text(img, 150, cy+15, c.get("label", ""), 18, (255,255,255))
        # Number
        paste_text(img, 150, cy+42, c.get("number", ""), 22, (255,220,150))
        cy += 95
    
    # Big share message at bottom
    if data.get("share"):
        sw, sh = measure_text(data["share"], 26)
        draw_glass_card(img, (W-sw)//2 - 30, H-200, sw+60, 90,
                        fill=(255,180,100), alpha=100, border=(255,210,140,220), radius=20)
        paste_text(img, (W-sw)//2, H-180, data["share"], 26, (255,255,255))
    
    paste_text(img, 60, H-80, "📱 长按任意页即可分享 · 一图一卡", 16, (200,210,230))
    
    fname = f"{data['page_index']:02d}_back.png"
    img.convert('RGB').save(f"{OUTDIR_DEFAULT}/{fname}", 'PNG', optimize=True)
    return img

# ============= MAIN ORCHESTRATOR =============
def render_trip_story(trip_data, outdir="trip_story"):
    global OUTDIR_DEFAULT
    os.makedirs(outdir, exist_ok=True)
    OUTDIR_DEFAULT = outdir

    # PRO: build full page list with all sections
    full_pages = [("cover", trip_data.get("cover", {}))]
    for p in trip_data["pages"]:
        full_pages.append(("page", p))
    SECTION_ORDER = ["essentials", "cost", "souvenirs", "apps"]
    for key in SECTION_ORDER:
        if key in trip_data:
            full_pages.append((key, trip_data[key]))
    full_pages.append(("back", trip_data.get("back", {})))

    render_map = {
        "cover": render_cover, "page": render_day,
        "essentials": render_essentials, "cost": render_cost,
        "souvenirs": render_souvenirs, "apps": render_apps,
        "back": render_back,
    }

    total = len(full_pages)
    for i, (kind, page) in enumerate(full_pages):
        page["page_index"] = i + 1
        page["total_pages"] = total
        render_map[kind](page)
        print(f"  ✅ {i+1}/{total} 渲染完成 ({kind})")

    print(f"\n全部 {total} 页已输出到 {outdir}/")
    print(f"文件列表:")
    for f in sorted(os.listdir(outdir)):
        sz = os.path.getsize(f"{outdir}/{f}") // 1024
        print(f"  {f} ({sz} KB)")

# ============= CLI ENTRY =============
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python render_story.py <trip_data.json> <outdir>")
        sys.exit(1)
    trip = json.loads(open(sys.argv[1]).read())
    render_trip_story(trip, sys.argv[2])
