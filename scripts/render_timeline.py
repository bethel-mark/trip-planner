#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_timeline.py - 时间轴视图(Notion-style timeline)
- 每天一根横轴,事件按时间铺成方块
- 多天瀑布排列(Gantt-style)
- 适合:总体行程一览 / 打印贴冰箱
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from AppKit import NSAttributedString, NSFont, NSColor, NSBitmapImageRep, NSGraphicsContext
from Foundation import NSMakeSize
from io import BytesIO
import os, sys, json, argparse

# 复用 helper(简化版)
def measure_text(text, font_size):
    ns_str = NSAttributedString.alloc().initWithString_attributes_(
        text, {'NSFont': NSFont.fontWithName_size_("Hiragino Sans GB", font_size)})
    return int(ns_str.size().width), int(ns_str.size().height)

def render_text_img(text, font_size, fill_rgb=(40, 35, 30)):
    try:
        ns_str = NSAttributedString.alloc().initWithString_attributes_(
            text, {
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
    except: return None

def paste_text(img, x, y, text, font_size, fill_rgb=(40, 35, 30)):
    pil = render_text_img(text, font_size, fill_rgb)
    if pil: img.alpha_composite(pil, (int(x), int(y)))

def render_emoji(emoji, size=40):
    try:
        ns_str = NSAttributedString.alloc().initWithString_attributes_(
            emoji, {'NSFont': NSFont.fontWithName_size_("Apple Color Emoji", size)})
        pad = max(20, size // 2)
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

def paste_emoji(img, x, y, emoji, size=40):
    pil = render_emoji(emoji, size)
    if pil:
        img.alpha_composite(pil, (int(x - pil.width/2), int(y - pil.height)))

def draw_background(img):
    for y in range(img.height):
        t = y / img.height
        r = int(15 + (45-15)*t**1.3)
        g = int(12 + (20-12)*t**1.3)
        b = int(48 + (75-48)*t**1.3)
        ImageDraw.Draw(img).line([(0,y),(img.width,y)], fill=(r,g,b,255))

def parse_time(t):
    """'08:30' -> 8.5"""
    try:
        h, m = t.split(':')
        return int(h) + int(m)/60
    except: return 0

def render_timeline_image(trip, outpath):
    """主函数:从 trip 数据出整张时间轴图"""
    cover = trip.get('cover', {})
    def to_rgb(c):
        return tuple(c) if isinstance(c, list) else c
    pages = trip.get('pages', [])
    title = cover.get('title', '行程总览')
    subtitle = cover.get('subtitle', '')
    
    # 计算画布:每天 130px 高度
    top_margin = 200
    bottom_margin = 100
    canvas_h = top_margin + len(pages) * 130 + bottom_margin
    canvas_w = 1600
    
    img = Image.new('RGBA', (canvas_w, canvas_h), (0,0,0,255))
    draw_background(img)
    d = ImageDraw.Draw(img)
    
    # 标题
    paste_text(img, 80, 60, title, 48, (255, 255, 255))
    if subtitle:
        paste_text(img, 80, 120, subtitle, 22, (200, 220, 255))
    
    # 时间轴参数
    time_x_start = 280  # 时间轴起点
    time_x_end = 1500   # 时间轴终点
    time_width = time_x_end - time_x_start
    day_height = 110
    day_y_start = top_margin
    
    # 每天一条
    for day_idx, page in enumerate(pages):
        y_top = day_y_start + day_idx * 130
        y_mid = y_top + day_height // 2
        
        # Day 标签(左)
        day_num = page.get('day', day_idx + 1)
        day_title = page.get('day_title', f'Day {day_num}')
        color = page.get('color', (100, 200, 230))
        
        # 圆形 day badge
        d.ellipse([40, y_mid-35, 120, y_mid+35], fill=to_rgb(color)+(255,))
        paste_text(img, 55, y_mid-20, f"Day", 16, (255, 255, 255))
        paste_text(img, 65, y_mid, f"{day_num}", 28, (255, 255, 255))
        
        # 标题
        paste_text(img, 140, y_mid-22, day_title, 22, (255, 255, 255))
        
        # 横轴
        d.line([(time_x_start, y_mid), (time_x_end, y_mid)], fill=(180, 170, 155, 200), width=2)
        
        # 时间刻度
        for h in range(0, 25, 4):
            x = time_x_start + int((h/24) * time_width)
            d.line([(x, y_mid-3), (x, y_mid+3)], fill=(255, 255, 255, 200), width=1)
            paste_text(img, x-12, y_mid+10, f"{h:02d}", 12, (200, 200, 200))
        
        # 事件方块
        events = page.get('events', [])
        for ev in events:
            t = parse_time(ev.get('time', '12:00'))
            x = time_x_start + int((t/24) * time_width)
            # 圆点
            d.ellipse([x-8, y_mid-8, x+8, y_mid+8], fill=to_rgb(color)+(255,))
            # 事件标签(短)
            place = ev.get('place', '')[:12]
            if place:
                place_w, _ = measure_text(place, 14)
                paste_text(img, x-place_w//2, y_mid-38, place[:10], 11, color)
            # 时间
            time_str = ev.get('time', '')
            time_w, _ = measure_text(time_str, 11)
            paste_text(img, x-time_w//2, y_mid+15, time_str, 11, (220, 220, 220))
    
    # 标题栏装饰
    d.rectangle([0, 0, canvas_w, 20], fill=(200, 60, 50, 255))
    
    img.convert('RGB').save(outpath, 'PNG', optimize=True)
    print(f"✅ 输出: {outpath} ({canvas_w}x{canvas_h})")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trip_json")
    parser.add_argument("outfile")
    args = parser.parse_args()
    with open(args.trip_json) as f:
        data = json.load(f)
    render_timeline_image(data, args.outfile)

if __name__ == "__main__":
    main()
