#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一调度器:一个入口,自动选普通版或老人大字版
- 根据用户输入关键词自动判断 mode
- 也支持 --mode 显式指定
- 同一份 trip JSON 出两种风格
"""
import sys, os, json, argparse, subprocess

def detect_mode_from_prompt(prompt: str) -> str:
    """从用户原文里自动判断 mode"""
    p = prompt.lower()
    elder_kw = ["老人", "大字", "长辈", "爸妈", "父母", "视障", "易读", "朗读", "tts", "打印", "print"]
    for kw in elder_kw:
        if kw in prompt:
            return "elder"
    return "story"

def detect_mode_from_data(data: dict) -> str:
    """从 trip JSON 里读 elder 字段"""
    if data.get("elder") or data.get("mode") == "elder":
        return "elder"
    return "story"

def render(trip_path: str, outdir: str, mode: str = None, user_prompt: str = ""):
    """主入口"""
    with open(trip_path) as f:
        trip = json.load(f)
    
    # 1. 决定 mode:CLI 参数 > JSON 字段 > 用户原文关键词 > 默认 story
    if mode is None:
        mode = detect_mode_from_data(trip)
    if mode == "auto" and user_prompt:
        mode = detect_mode_from_prompt(user_prompt)
    if mode is None or mode == "auto":
        mode = "story"  # 默认
    
    script_map = {
        "story": "render_story.py",
        "elder": "render_elder.py",
        "long":  "render_mobile.py",
    }
    
    if mode not in script_map:
        print(f"未知 mode: {mode},可选: {list(script_map.keys())}")
        sys.exit(1)
    
    script = script_map[mode]
    print(f"==> 模式:{mode} → {script}")
    print(f"==> 提示词触发检测:{user_prompt[:60]!r}")
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
    # 直接 exec 当前解释器(避免子进程丢 PIL / PyObjC)
    with open(script_path) as f:
        script_code = f.read()
    # 把 trip_path / outdir / mode 注入
    script_globals = {'__name__': '__main__', '__file__': script_path}
    # 临时替换 argv 给子脚本
    import sys as _sys
    _sys.argv = [script_path, trip_path, outdir]
    exec(compile(script_code, script_path, 'exec'), script_globals)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="统一 trip-planner 调度器")
    parser.add_argument("trip_json", help="trip JSON 路径")
    parser.add_argument("outdir", help="输出目录")
    parser.add_argument("--mode", choices=["story", "elder", "long", "pro", "auto"], default="pro",
                        help="输出模式(默认 pro = 全部三种都出)")
    parser.add_argument("--prompt", default="", help="用户原文(触发自动判断)")
    args = parser.parse_args()
    

    if args.mode == "pro":
        # PRO mode: render all 3 outputs into subdirectories
        subdirs = {"story": "玻璃拟态", "elder": "大字版", "long": "长截图"}
        all_files = []
        for m, label in subdirs.items():
            mdir = os.path.join(args.outdir, m)
            os.makedirs(mdir, exist_ok=True)
            print(f"\n{'='*50}")
            print(f"  [{label}] 渲染中...")
            print(f"{'='*50}")
            render(args.trip_json, mdir, m, args.prompt)
            for f in os.listdir(mdir):
                sz = os.path.getsize(f"{mdir}/{f}") // 1024
                all_files.append((m, label, f, sz))
        # Summary
        print(f"\n{'='*50}")
        print(f"  🎉 PRO 模式全部完成!  输出目录: {args.outdir}")
        print(f"{'='*50}")
        for mode, label, fname, sz in all_files:
            print(f"  [{label}] {fname} ({sz} KB)")
        print(f"\n  共 {len(all_files)} 个文件")
    else:
        render(args.trip_json, args.outdir, args.mode, args.prompt)
