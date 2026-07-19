import sys, os, json
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""玻璃拟态 + 等距 3D + Soft 3D UI · 手机长截图版
- 宽 1080(适配手机)
- 每步加入详细"⚠️ 注意"事项
- 字号整体放大,适合转发截图
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from AppKit import NSAttributedString, NSFont, NSColor, NSBitmapImageRep, NSGraphicsContext
from Foundation import NSMakeSize
from io import BytesIO
import os

W = 1080
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "."
OUT_FILE = sys.argv[3] if len(sys.argv) > 3 else None  # 可选,指定文件名

# ---------- Color helpers ----------
def rgb(r,g,b): return (r,g,b,255)

# ---------- Text / Emoji via NSBitmapImageRep ----------
def measure_text(text, font_size):
    ns_str = NSAttributedString.alloc().initWithString_attributes_(
        text,
        {'NSFont': NSFont.fontWithName_size_("Hiragino Sans GB", font_size)}
    )
    s = ns_str.size()
    return int(s.width), int(s.height)

def render_emoji(emoji, size=120):
    ns_str = NSAttributedString.alloc().initWithString_attributes_(
        emoji,
        {'NSFont': NSFont.fontWithName_size_("Apple Color Emoji", size)}
    )
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
            }
        )
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
    if pil:
        img.alpha_composite(pil, (int(x), int(y)))

def paste_emoji(img, x, y, emoji, size=120):
    pil = render_emoji(emoji, size)
    px = int(x - pil.width / 2)
    py = int(y - pil.height)
    img.alpha_composite(pil, (px, py))

# ---------- Background ----------
def draw_background(img, height):
    for y in range(height):
        t = y / height
        r = int(15 + (45-15)*t**1.3)
        g = int(12 + (20-12)*t**1.3)
        b = int(48 + (75-48)*t**1.3)
        ImageDraw.Draw(img).line([(0,y),(W,y)], fill=rgb(r,g,b))

def glow(img, cx, cy, radius, color, alpha=180, blur=60):
    ov = Image.new('RGBA', img.size, (0,0,0,0))
    ImageDraw.Draw(ov).ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill=color+(alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(ov)

# ---------- Glass card ----------
def draw_glass_card(img, x, y, w, h, fill=(255,255,255), alpha=42,
                    border=(255,255,255,180), border_w=2, radius=22, shadow=True):
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

def right_aligned_glass_card(img, text, font_size, top_y, right_margin=40,
                              fill=(255,255,255), alpha=80, border=(255,255,255,220),
                              radius=22, pad_x=28, pad_y=14):
    tw, th = measure_text(text, font_size)
    card_w = tw + pad_x * 2
    card_h = th + pad_y * 2
    left_x = W - right_margin - card_w
    draw_glass_card(img, int(left_x), int(top_y), card_w, card_h,
                    fill=fill, alpha=alpha, border=border, radius=radius)
    paste_text(img, left_x + pad_x, top_y + pad_y, text, font_size, (255,255,255))
    return left_x, card_w, card_h

# ---------- Isometric platform ----------
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
    paste_emoji(img, cx, cy_top - 5, emoji, size)

# ---------- EVENT CARD (the new big unit) ----------
def event_card(img, x, y, w, time, place, desc, precautions,
                time_color=(100,200,230), accent=(160,230,250)):
    """Draw one event card with time badge, place, desc, and precautions."""
    # Compute height based on precautions length
    max_chars = 38
    total_lines = 0
    for p in precautions:
        if len(p) <= max_chars:
            total_lines += 1
        else:
            cur = p
            while len(cur) > max_chars:
                cut = cur.rfind(' ', 0, max_chars)
                if cut == -1: cut = max_chars
                total_lines += 1
                cur = cur[cut:].lstrip()
            total_lines += 1
    # height = time/place section (~110) + caution label (30) + precautions (lines*22 + gaps*8) + padding (40)
    h = 110 + 35 + total_lines * 24 + len(precautions) * 8 + 50
    h = max(h, 320)  # minimum card height
    # Main glass card
    draw_glass_card(img, x, y, w, h,
                    fill=(255,255,255), alpha=18,
                    border=(255,255,255,80), border_w=2, radius=24)
    # Time badge - left side circle
    cx_t = x + 80
    cy_t = y + 70
    ov = Image.new('RGBA', img.size, (0,0,0,0))
    od = ImageDraw.Draw(ov)
    od.ellipse([cx_t-52, cy_t-52, cx_t+52, cy_t+52],
               fill=time_color+(255,), outline=accent+(220,), width=4)
    img.alpha_composite(ov)
    paste_text(img, cx_t - 40, cy_t - 16, time, 30, (255,255,255))
    # Place + desc (right of time badge)
    paste_text(img, x + 170, y + 35, place, 28, (255,255,255))
    paste_text(img, x + 170, y + 78, desc, 18, (200,215,235))
    # ⚠️ Precautions section header
    paste_text(img, x + 28, y + 140, "⚠️ 注意", 20, (255,200,100))
    # Precautions bullet points
    py = y + 178
    f_p = 18
    for i, p in enumerate(precautions):
        # Bullet
        ov = Image.new('RGBA', img.size, (0,0,0,0))
        od = ImageDraw.Draw(ov)
        od.ellipse([x+38, py+5, x+50, py+17], fill=(255,200,100,255))
        img.alpha_composite(ov)
        # Text wrap
        if len(p) > max_chars:
            lines = []
            cur = p
            while len(cur) > max_chars:
                cut = cur.rfind(' ', 0, max_chars)
                if cut == -1: cut = max_chars
                lines.append(cur[:cut])
                cur = cur[cut:].lstrip()
            lines.append(cur)
        else:
            lines = [p]
        for line in lines:
            paste_text(img, x + 60, py, line, f_p, (230,235,250))
            py += 26
        py += 4
    return h

# ---------- MAIN ----------
def main():
    # First pass: estimate total height based on content
    # Day 1: 8 events x ~280 = 2240 + 100 (header) = 2340
    # Day 2: 5 events x ~280 = 1400 + 100 = 1500
    # Title: 200
    # Questions: ~700
    # Spacing: 200
    # Total: ~4900
    H = 11000
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    draw_background(img, H)

    # Glow blobs (scattered)
    glow(img, 100, 100, 200, (90,120,255), alpha=140, blur=80)
    glow(img, W-150, 600, 220, (200,80,200), alpha=110, blur=90)
    glow(img, W//2, 1800, 300, (80,220,180), alpha=90, blur=100)
    glow(img, W-200, 3000, 200, (255,160,100), alpha=110, blur=80)
    glow(img, 150, 4200, 240, (140,180,255), alpha=100, blur=90)

    # ============ COVER / TITLE ============
    title = "🇲🇾 IPOH → KL → 🇸🇬 SINGAPORE"
    subtitle = "🎒 仅背包 · 2 天 1 夜 · 探校 + 一日游"
    sub2 = "Glassmorphism + Isometric + Soft 3D"
    tw, th = measure_text(title, 44)
    sub_tw, sub_th = measure_text(subtitle, 22)
    sub2_tw, sub2_th = measure_text(sub2, 16)
    bar_w = max(tw, sub_tw, sub2_tw) + 60
    bar_x = (W - bar_w) // 2
    draw_glass_card(img, bar_x, 30, bar_w, 200,
                    fill=(255,255,255), alpha=30, radius=28)
    paste_text(img, bar_x + 30, 55, title, 44, (255,255,255))
    paste_text(img, bar_x + 30, 115, subtitle, 22, (200,220,255))
    paste_text(img, bar_x + 30, 150, sub2, 16, (180,200,235))

    # ============ DAY 1 ============
    DAY1_Y = 270
    # Day 1 header bar
    draw_glass_card(img, 40, DAY1_Y, W-80, 100,
                    fill=(80,180,200), alpha=80,
                    border=(160,230,250,220), border_w=2, radius=24)
    paste_text(img, 70, DAY1_Y + 28, "DAY 1  ·  探校 + 签约", 38, (255,255,255))
    paste_text(img, 70, DAY1_Y + 75, "≈ RM 550 / 人 · Wesley A-Level 已选", 18, (200,230,250))
    right_aligned_glass_card(img, "Wesley Methodist International School", 16, DAY1_Y+35,
                              right_margin=70, fill=(255,255,255), alpha=60,
                              border=(255,255,255,180), pad_x=20, pad_y=8)
    
    # 8 events for Day 1
    events_d1 = [
        ("06:30", "🚆 IPOH 火车站 → KL Sentral",
         "KTM ETS Platinum · RM 50 · 2h15",
         [
            "提前 1-2 周在 KTMB APP 或 Easybook 预订,周末 / 长假必满",
            "提前 30 分钟到站,护照原件必带(查票 + 进站查证)",
            "选右侧靠窗可看到油棕园 + 椰林,2 小时不无聊",
            "车上冷气足,带薄外套;车厢有小桌可吃饭",
            "末班车约 22:00,千万别误点",
         ]),
        ("09:00", "☕ KL Sentral 寄存 / 轻装",
         "若有行李寄存,RM 10-15/天",
         [
            "KL Sentral 行李寄存柜 24h,中文界面,信用卡 OK",
            "无行李请跳过此步(仅背包就是这种状态)",
            "趁此补:Grab 充值 MYR 50 / 装好离线地图",
            "手机充电到 100%,今日 4 个学校转场全靠它",
         ]),
        ("09:30", "🏛 WESLEY METHODIST ★ 签约日",
         "Jalan Bellamy, KL · 招生办 10:00 见",
         [
            "提前 3 天邮件招生办,附孩子近 2 年成绩单扫描",
            "学生穿白衬衫 + 深色长裤(印象分,招生官会更认真)",
            "准备 5 份孩子简历 + 获奖证书复印件(分发给各校)",
            "签约必带:护照、信用卡(Visa/Master,额度 ≥ RM 1 万)、户口本翻译件",
            "招生办常要求当场交押金(可砍,见现场 11 件事清单)",
            "Grab 直接搜 'Wesley Methodist School KL',停在正门",
         ]),
        ("13:00", "🍜 茶餐室 lunch",
         "Sunway Pyramid 或 KL 街边 · RM 15",
         [
            "Sunway Pyramid 楼下茶餐室选择多,RM 15-20",
            "若想更便宜,KL 街边 Mamak(印度餐厅)RM 8-12 搞定",
            "避开 13:30-14:30 高峰,排队浪费时间",
            "吃饱再走,Sunway 校园里选择少且贵",
         ]),
        ("13:30", "🏢 SUNWAY UNIVERSITY 摸底",
         "Bandar Sunway · Grab RM 25 · 30 min",
         [
            "Pre-U 直升协议要求什么 GPA / A-Level 等级?",
            "Sunway Excellence Scholarship 截止 + 门槛 GPA?",
            "带学生证 / 成绩单问 '内部直升' 政策",
            "Sunway BRT 站到校门口 5 分钟,顺便看通勤省钱潜力",
            "索取:校园地图 + 招生办直线电话(回 KL 后还要用)",
         ]),
        ("16:30", "🚌 Grab → NILAI",
         "约 1 小时 · RM 70-100",
         [
            "Grab 大车 XL(7 座)更舒适,长途不累",
            "高峰期 17:00-19:00 严重堵车,务必 16:30 前出发",
            "司机可能不熟 Nilai 大学地址,把马来文地址截图:'Universiti Nilai'",
            "若 Grab 无车,试 KTM Komuter 到 Nilai 站 + 短途 Grab 进校",
         ]),
        ("17:30", "🏘 NILAI UNIVERSITY 摸底",
         "Putra Nilai · A-Level 中心核实",
         [
            "A-Level 中心是直营还是第三方挂靠?(影响质量)",
            "Hostel 强制住校还是可选?月租区间?影响预算 RM 1k-2k",
            "Nilai 镇上 Mamak 晚饭便宜 RM 8-12,推荐试试 Roti Canai",
            "中国学生比例 + 签证 / 监护协助?现场问招办",
            "问 '今晚 hostel 试住一晚 RM 30 行不行?'(超低价换好评)",
         ]),
        ("20:30", "🛏 NILAI 校内 hostel",
         "RM 60-80 / 晚 · 省返 KL 的 1 小时",
         [
            "校内 hostel 比镇上便宜,含空调 + 热水",
            "明天直接从 Nilai 去 KLIA Transit / 大巴去新加坡,省 1h",
            "确认 hostel 早餐是否含(有些 7:00-9:00 含)",
            "注意:校外镇上更热闹,但晚上 22:00 后安静,安全 OK",
            "若想住 KL,Bukit Bintang 中端酒店 RM 150-250(逛夜景版)",
         ]),
    ]
    
    # Render Day 1 events
    cur_y = DAY1_Y + 130
    card_gap = 18
    for i, (time, place, desc, precautions) in enumerate(events_d1):
        # Number badge on left (centered vertically with card)
        # Render card first to get height
        h = event_card(img, 80, cur_y, W-120, time, place, desc, precautions,
                    time_color=(100,200,230), accent=(160,230,250))
        # Number badge aligned to card top + 40
        ov = Image.new('RGBA', img.size, (0,0,0,0))
        od = ImageDraw.Draw(ov)
        od.ellipse([20, cur_y+20, 60, cur_y+60], fill=(100,200,230,255), outline=(200,240,255,255), width=3)
        od.text((33, cur_y+28), str(i+1).zfill(2), font=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24, 1), fill=(20,30,40,255))
        img.alpha_composite(ov)
        cur_y += h + card_gap

    # ============ DAY 2 ============
    DAY2_Y = cur_y + 40
    draw_glass_card(img, 40, DAY2_Y, W-80, 100,
                    fill=(255,140,140), alpha=80,
                    border=(255,200,200,220), border_w=2, radius=24)
    paste_text(img, 70, DAY2_Y + 28, "DAY 2  ·  新加坡一日游", 38, (255,255,255))
    paste_text(img, 70, DAY2_Y + 75, "≈ SGD 35 / 人 · KL → Singapore → KL", 18, (255,220,220))
    right_aligned_glass_card(img, "Tourist Pass SGD 10", 16, DAY2_Y+35,
                              right_margin=70, fill=(255,255,255), alpha=60,
                              border=(255,255,255,180), pad_x=20, pad_y=8)

    events_d2 = [
        ("06:30", "🚌 NILAI/KL → 新加坡 Queen Street",
         "KKKL / Aeroline · RM 60 · 5h · Easybook 提前订",
         [
            "大巴公司推荐 KKKL(便宜)或 Aeroline(高端,有 USB)",
            "从 TBS(Bandar Tasik Selatan)出发,地铁 KTM Komuter 可达",
            "车程 5-6h 含过关 1h,过关需护照原件 + SG Arrival Card",
            "提前 3 天填新加坡入境卡:eservices.ica.gov.sg/sgarrivalcard",
            "车上充电口可能不够,带充电宝 + 颈枕,长途舒服点",
            "末班车 22:30 左右,迟到就只能飞机或过夜大巴",
         ]),
        ("12:00", "🇸🇬 QUEEN STREET TERMINAL",
         "新加坡入境 · Tourist Pass SGD 10(全天无限)",
         [
            "地铁站客服中心办 Tourist Pass,SGD 10 一天无限次 MRT+巴士",
            "无押金,只收 SGD 10,卡不退但能留作纪念",
            "若只坐 3-4 次,买单程 EZ-Link 卡更划算(SGD 12 含卡费)",
            "手机装 Google Maps,新加坡地铁非常准时",
            "新加坡法律严:不乱扔垃圾、不嚼口香糖、不在地铁饮食",
         ]),
        ("12:30", "🍚 MAXWELL 熟食中心 午饭",
         "天天海南鸡饭 SGD 6 · 街区免费逛",
         [
            "牛车水 Smith Street 麦士威熟食中心,天天海南鸡饭招牌",
            "茶餐室一餐 SGD 5-8,比商场 Food Court 便宜一半以上",
            "高峰 12:30-13:30 排队,错峰更省时间",
            "现金备用,部分摊位只收现金",
            "吃饱去牛车水街区逛,免费,中国城氛围浓",
         ]),
        ("13:30", "🦁 Marina → Gardens 一线",
         "Merlion + MBS + Gardens 户外免费 · Cloud Forest SGD 8 学生",
         [
            "Merlion Park 免费,新加坡地标,必拍",
            "Marina Bay Sands 户外观景台免费(不进赌场)",
            "Gardens by the Bay 户外花园免费,Cloud Forest 室内 SGD 8(学生价)",
            "全程步行 + 地铁,无需 Grab(车费贵且堵)",
            "室内冷气足,带薄外套;户外防晒 + 帽子 + 水",
         ]),
        ("19:30", "🌃 SPECTRA 光影秀",
         "Marina Bay 浮桥 · 19:30 / 20:30 / 21:30 · 免费",
         [
            "19:30 / 20:30 / 21:30 三场,免费,提前 15 分钟占位",
            "最佳观看位:Marina Bay 浮桥正对 MBS 那一侧",
            "周末人多,工作日更舒服",
            "拍照手机广角更出片;夜景手机模式更稳",
            "看完直奔 Chinatown Complex 晚饭,SGD 6-8 搞定",
         ]),
    ]
    
    cur_y = DAY2_Y + 130
    for i, (time, place, desc, precautions) in enumerate(events_d2):
        h = event_card(img, 80, cur_y, W-120, time, place, desc, precautions,
                    time_color=(255,150,120), accent=(255,210,200))
        ov = Image.new('RGBA', img.size, (0,0,0,0))
        od = ImageDraw.Draw(ov)
        od.ellipse([20, cur_y+20, 60, cur_y+60], fill=(255,150,120,255), outline=(255,210,200,255), width=3)
        od.text((33, cur_y+28), str(i+1).zfill(2), font=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24, 1), fill=(20,30,40,255))
        img.alpha_composite(ov)
        cur_y += h + card_gap

    # ============ SUMMARY QUESTIONS (long-strip vertical) ============
    SUM_Y = cur_y + 40

    # Section title
    draw_glass_card(img, 40, SUM_Y, W-80, 90,
                    fill=(255,255,255), alpha=24,
                    border=(255,255,255,180), border_w=2, radius=22)
    paste_text(img, 70, SUM_Y + 22, "📋 31 条核心问题 · 每条独立卡片 · 现场逐项打勾", 26, (255,255,255))

    cur_y = SUM_Y + 120

    # Long-strip question lists
    # Each question is its own glass card row: number + text + tag + tip
    question_data = [
        # (school, color, [list of (text, tag, tip)])
        ("🏛 WESLEY METHODIST · 签约日必问 · 11 问",
         (60,170,200), (140,220,250),
         [
            ("当前最近入学点是几月?最晚报到日?", "⏰ 时间",
             "关系签证办理节奏,直接决定整个时间规划"),
            ("A-Level 学制 1.5 年 vs 2 年?对应哪一年级?", "📚 学术",
             "读完高一/高二插班必须对齐,否则浪费 1 年"),
            ("押金+注册+考试局费 Year 1 total 多少钱?", "💰 费用",
             "打包价常比单加便宜 RM 2k-5k,务必问打包"),
            ("数学/进阶/物理/经济组合开班人数门槛?", "📚 学术",
             "5-8 人以下不开,可能影响你的选课组合"),
            ("任课老师是否全职 Cambridge 培训师?外籍比?", "👨‍🏫 师资",
             "兼职老师水平参差,直接影响 A-Level 出分"),
            ("模拟考+预测成绩+UCAS 升学指导谁负责?", "📈 升学",
             "从哪一年级开始介入?G5 申请通常需 2 年规划"),
            ("住宿/Homestay 提供吗?校方 vs 第三方?", "🏠 生活",
             "校方直接管更安全,第三方可能便宜但纠纷多"),
            ("校服/教材/笔记本 购买渠道+二手市场?", "💰 费用",
             "二手市场可省 RM 500-1000,毕业生群常转让"),
            ("签证+监护人 一条龙谁负责?额外收费?", "📋 手续",
             "自己办可能省 RM 2-5k,但流程繁琐"),
            ("ECA/体育强项?(影响大学 PS 含金量)", "🎯 背景",
             "MUN/辩论/体育奖牌 = G5 申请的隐形加分"),
            ("Sibling/早报/现金奖学金?(现场问官网不写)", "💰 优惠",
             "官网不写但确实存在的折扣,问就完事"),
         ]),
        ("🏢 SUNWAY UNIVERSITY · 摸底日必问 · 10 问",
         (220,110,110), (255,180,180),
         [
            ("A-Level 录取底线等级 A*AA / AAA / AAB?", "📊 录取",
             "不同专业底线差很大,商科 / CS 比工程高 1-2 档"),
            ("Pre-U 直升协议要求什么 GPA / 等级?", "📚 学术",
             "可省 1 年预科直接进本科,关键看具体条款"),
            ("Sunway Excellence Scholarship 截止+门槛?", "💰 费用",
             "通常 GPA 3.5/4.0 + 课外活动,覆盖 50-100% 学费"),
            ("A-Level → 本科最快几年?3+0 / 2+1?", "⏰ 时间",
             "3+0 全在马来西亚;2+1 后 1 年可去英澳合作校"),
            ("ACCA / CFA / BCS / 工程 认证覆盖专业?", "🎓 证书",
             "决定未来 1-2 年能不能省下 RM 5k-15k 认证费"),
            ("带薪实习合作企业名单?(直接挂钩就业)", "💼 就业",
             "只问'合作'还不够,要问'具体岗位类型'"),
            ("Sunway Geo / Pyramid 周边租房行情?", "🏠 生活",
             "步行 10 分钟内 RM 1.2k-2k/月,远一点便宜 30%"),
            ("Sunway BRT 是否仍通校门口?(通勤省钱)", "🚇 交通",
             "BRT 学生月票 RM 50,比 Grab 月省 RM 300+"),
            ("中国/国际学生比例 + 中文支持?", "🌏 适应",
             "比例太低容易孤独,太高又少英语环境"),
            ("招办能开一封推荐信模板吗?", "📋 手续",
             "很多学校提供,可带回去给 Wesley 用"),
         ]),
        ("🏘 NILAI UNIVERSITY · 摸底日必问 · 10 问",
         (150,110,200), (210,170,255),
         [
            ("A-Level 中心是直营还是第三方挂靠?", "📚 学术",
             "直接影响教学质量和升学率,质量参差大"),
            ("对 A-Level 各等级的录取底线+conditional offer?", "📊 录取",
             "Conditional 可保底,但要看清楚换 offer 条件"),
            ("A-Level → 本科最快几年?学分减免规则?", "⏰ 时间",
             "减免学分 = 提前毕业,省 1 年学费 RM 30k-50k"),
            ("Hostel 强制住校还是可选?月租区间?", "🏠 生活",
             "强制住校 RM 600-1000/月,可选可省 50%"),
            ("升读本地公立(UUM/UKM)的转学分比例?", "🎓 升学",
             "转公立 = 省 1 年 + 学费砍半,关键看转学分率"),
            ("Nilai 镇上 Mamak/食堂 月生活费预算?", "💰 费用",
             "比 KL 便宜 20-30%,月 RM 800-1.2k 可过"),
            ("医药预科:Nilai Medical Centre 实习网络?", "🎓 实习",
             "读医预科这是核心,实习网络决定就业起跑线"),
            ("中国/国际学生比例+签证/监护协助?", "🌏 适应",
             "中国学生多的学校生活压力小,但圈子更封闭"),
            ("今晚 hostel 试住一晚 RM 30 行不行?", "💡 试探",
             "很多 hostel 乐意用超低价换好评,直接开口问"),
            ("Nilai 镇到 KL Sentral/KLIA 通勤时间?", "🚇 交通",
             "决定周末能否方便回 KL,影响生活品质"),
         ]),
    ]

    # Render each school's question strip
    d = ImageDraw.Draw(img)
    for school_title, color, border, qs in question_data:
        # School header
        tw, th = measure_text(school_title, 22)
        header_w = tw + 60
        header_h = th + 30
        header_x = 40
        draw_glass_card(img, header_x, cur_y, header_w, header_h,
                        fill=color, alpha=100, border=border+(220,), border_w=2, radius=18)
        paste_text(img, header_x + 30, cur_y + 15, school_title, 22, (255,255,255))
        cur_y += header_h + 18

        # Each question as a long-strip card
        for idx, (q_text, q_tag, q_tip) in enumerate(qs):
            # Compute card height (depends on text wrap)
            f_q = 20
            max_chars_per_line = 38
            # Text width estimate
            chars = len(q_text) + 12 + len(q_tag)  # + space for tag
            if chars > max_chars_per_line:
                n_lines = 2
            else:
                n_lines = 1
            tip_chars = len(q_tip)
            tip_lines = (tip_chars // max_chars_per_line) + 1
            card_h = 30 + n_lines * 28 + tip_lines * 22 + 20  # padding + q + tip + gap
            card_h = max(card_h, 95)
            # Card
            draw_glass_card(img, 40, cur_y, W-80, card_h,
                            fill=(255,255,255), alpha=14,
                            border=(255,255,255,60), border_w=1, radius=18)
            # Number badge
            ov = Image.new('RGBA', img.size, (0,0,0,0))
            od = ImageDraw.Draw(ov)
            od.ellipse([cur_y_text_x:=60, cur_y+18, 60+30, cur_y+18+30],
                       fill=color+(255,))
            od.text((60+8, cur_y+22), str(idx+1).zfill(2),
                    font=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16, 1),
                    fill=(20,20,40,255))
            img.alpha_composite(ov)
            # Tag pill (right side)
            tw, th = measure_text(q_tag, 14)
            tag_w = tw + 24
            tag_h = 28
            tag_x = W - 80 - tag_w - 20
            tag_y = cur_y + 15
            ov = Image.new('RGBA', img.size, (0,0,0,0))
            od = ImageDraw.Draw(ov)
            od.rounded_rectangle([tag_x, tag_y, tag_x+tag_w, tag_y+tag_h],
                                 radius=14, fill=color+(80,), outline=border+(180,), width=1)
            img.alpha_composite(ov)
            paste_text(img, tag_x + 12, tag_y + 6, q_tag, 14, (255,255,255))
            # Question text (after number, before tag)
            q_text_x = 110
            q_text_w = tag_x - q_text_x - 15
            # Simple wrap by char count
            wrap_chars = max(20, q_text_w // 14)
            lines = []
            cur = q_text
            while len(cur) > wrap_chars:
                cut = cur.rfind(' ', 0, wrap_chars)
                if cut == -1 or cut < wrap_chars * 0.5:
                    cut = wrap_chars
                lines.append(cur[:cut])
                cur = cur[cut:].lstrip()
            lines.append(cur)
            for li, line in enumerate(lines):
                paste_text(img, q_text_x, cur_y + 18 + li*26, line, f_q, (255,255,255))
            # Tip (small italic-feel text below)
            tip_y = cur_y + 18 + len(lines)*26 + 6
            tip_color = (255, 220, 130)  # warm yellow
            # Wrap tip
            wrap_tip = max(30, (W-80 - 110 - 20) // 12)
            tip_lns = []
            cur = q_tip
            while len(cur) > wrap_tip:
                cut = cur.rfind(' ', 0, wrap_tip)
                if cut == -1 or cut < wrap_tip * 0.5:
                    cut = wrap_tip
                tip_lns.append(cur[:cut])
                cur = cur[cut:].lstrip()
            tip_lns.append(cur)
            for li, line in enumerate(tip_lns):
                paste_text(img, 110, tip_y + li*22, "💡 " + line, 14, tip_color)
            cur_y += card_h + 10
        cur_y += 20  # gap between schools

    # Bottom footer
    FOOTER_Y = H - 80
    draw_glass_card(img, 40, FOOTER_Y, W-80, 50,
                    fill=(255,180,80), alpha=60,
                    border=(255,210,140,220), border_w=2, radius=18)
    paste_text(img, W//2 - 240, FOOTER_Y + 13, "💾 长按保存 / 转发给同行人", 22, (255,255,255))

        # 输出路径(优先 OUT_FILE,否则 OUT_DIR/itinerary_long.png)
    out_path = OUT_FILE if OUT_FILE else os.path.join(OUT_DIR, "itinerary_long.png")
    os.makedirs(OUT_DIR, exist_ok=True)
    img.convert('RGB').save(out_path, 'PNG', optimize=True)
    print(f"Saved: {out_path}  ({os.path.getsize(out_path)//1024} KB)")
    print(f"Size: {W}x{H}")

if __name__ == "__main__":
    main()
