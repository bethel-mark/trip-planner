#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双 provider 对比:同 1 份 prompt,出 2 张图(并排)+ 文字对比报告
- 输出一张 side-by-side 对比 PNG
- 输出 Markdown 报告
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from AppKit import NSAttributedString, NSFont, NSColor, NSBitmapImageRep, NSGraphicsContext
from Foundation import NSMakeSize
from io import BytesIO
import os, sys, json, subprocess, argparse

def measure_text(text, font_size):
    ns_str = NSAttributedString.alloc().initWithString_attributes_(
        text, {'NSFont': NSFont.fontWithName_size_("Hiragino Sans GB", font_size)})
    s = ns_str.size()
    return int(s.width), int(s.height)

def render_text_img(text, font_size, fill_rgb=(0,0,0)):
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
    except: return None

def paste_text(img, x, y, text, font_size, fill_rgb=(0,0,0)):
    pil = render_text_img(text, font_size, fill_rgb)
    if pil: img.alpha_composite(pil, (int(x), int(y)))

# 兜底 API key(可改 ~/.zshrc 覆盖)
FALLBACK_KEYS = {
    "minimax": "",       # 你的 MiniMax key
    "zai": "594db1c9fb1f4315ad8983c4e78e4bcc.vSEklXvaOt1pdRYD",  # Zhipu
    "openai": "",
    "google": "",
    "dashscope": "",
    "ark": "",
}
ENV_MAP = {
    "minimax": "MINIMAX_API_KEY",
    "zai": "ZAI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "dashscope": "DASHSCOPE_API_KEY",
    "ark": "ARK_API_KEY",
}

def call_provider(prompt_path, output_path, provider, model, ar="1:1", quality="2k"):
    """调 baoyu-image-gen 单图"""
    env = os.environ.copy()
    # 兜底 key
    env_var = ENV_MAP.get(provider)
    if env_var and not env.get(env_var) and FALLBACK_KEYS.get(provider):
        env[env_var] = FALLBACK_KEYS[provider]
    cmd = ["npx", "-y", "bun",
           "/Users/a1234/.codex/skills/baoyu-skills/skills/baoyu-image-gen/scripts/main.ts",
           "--promptfiles", prompt_path,
           "--image", output_path,
           "--provider", provider,
           "--ar", ar,
           "--quality", quality]
    if model:
        cmd += ["--model", model]
    print(f"  → {provider}/{model}: ", end="", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=180)
    if result.returncode == 0 and os.path.exists(output_path):
        sz = os.path.getsize(output_path) // 1024
        print(f"✅ {sz} KB")
        return output_path
    else:
        print(f"❌ 失败")
        print(f"    stderr: {result.stderr[-200:]}")
        return None

def side_by_side(left_path, right_path, left_label, right_label, output_path):
    """生成左右对比图 + 标签"""
    left = Image.open(left_path).convert('RGBA')
    right = Image.open(right_path).convert('RGBA')
    
    W, H = 1280, 720
    canvas = Image.new('RGBA', (W, H), (250, 248, 245, 255))
    # Title bar
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, W, 80], fill=(40, 50, 70, 255))
    paste_text(canvas, 30, 25, "🎨 双 Provider 对比", 36, (255, 255, 255))
    
    # Two image areas
    img_w, img_h = 560, 560
    margin_top = 100
    left_x, right_x = 30, W - 30 - img_w
    
    # Resize and paste
    left_resized = left.resize((img_w, img_h), Image.LANCZOS)
    right_resized = right.resize((img_w, img_h), Image.LANCZOS)
    canvas.alpha_composite(left_resized, (left_x, margin_top))
    canvas.alpha_composite(right_resized, (right_x, margin_top))
    
    # Labels
    paste_text(canvas, left_x + 10, margin_top + img_h + 10, left_label, 24, (200, 60, 50))
    paste_text(canvas, right_x + 10, margin_top + img_h + 10, right_label, 24, (50, 120, 200))
    
    # VS in middle
    paste_text(canvas, W//2 - 25, margin_top + img_h//2 - 30, "VS", 64, (150, 150, 150))
    
    canvas.convert('RGB').save(output_path, 'PNG', optimize=True)
    print(f"  → side-by-side saved: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="双 Provider 对比")
    parser.add_argument("prompt_file", help="prompt markdown 文件")
    parser.add_argument("outdir", help="输出目录")
    parser.add_argument("--provider-a", default="minimax", help="左 provider(默认 minimax)")
    parser.add_argument("--model-a", default="image-01")
    parser.add_argument("--provider-b", default="zai", help="右 provider(默认 zai)")
    parser.add_argument("--model-b", default="cogview-4-250304")
    parser.add_argument("--label-a", default=None, help="左标签(默认 provider/model)")
    parser.add_argument("--label-b", default=None)
    parser.add_argument("--ar", default="1:1")
    parser.add_argument("--quality", default="2k")
    args = parser.parse_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    label_a = args.label_a or f"{args.provider_a}/{args.model_a}"
    label_b = args.label_b or f"{args.provider_b}/{args.model_b}"
    
    out_a = os.path.join(args.outdir, f"a_{args.provider_a}.png")
    out_b = os.path.join(args.outdir, f"b_{args.provider_b}.png")
    
    print(f"双 provider 对比: {label_a} VS {label_b}")
    print("="*60)
    ok_a = call_provider(args.prompt_file, out_a, args.provider_a, args.model_a, args.ar, args.quality)
    ok_b = call_provider(args.prompt_file, out_b, args.provider_b, args.model_b, args.ar, args.quality)
    print("="*60)
    
    if ok_a and ok_b:
        compare_path = os.path.join(args.outdir, "compare.png")
        side_by_side(out_a, out_b, label_a, label_b, compare_path)
        print(f"\n✅ 完成:{compare_path}")
    else:
        print(f"\n❌ 至少一个 provider 失败,无法生成对比图")
        if not ok_a: print(f"   失败: {args.provider_a}")
        if not ok_b: print(f"   失败: {args.provider_b}")

if __name__ == "__main__":
    main()
