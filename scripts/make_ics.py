#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""根据 trip JSON 生成 .ics 日历文件,可导入 iOS Calendar / Google Calendar"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def make_ics(events: list, output: str, calendar_name: str = "Trip"):
    """events: list of {uid, dtstart, dtend, summary, location, description}"""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//trip-planner//EN",
        f"X-WR-CALNAME:{calendar_name}",
        "CALSCALE:GREGORIAN",
    ]
    for e in events:
        # dtstart, dtend format: "2026-07-19 06:30"
        s = datetime.strptime(e["dtstart"], "%Y-%m-%d %H:%M")
        en = datetime.strptime(e["dtend"], "%Y-%m-%d %H:%M")
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{e['uid']}@trip-planner",
            f"DTSTART:{s.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{en.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{e['summary']}",
            f"LOCATION:{e.get('location', '')}",
            f"DESCRIPTION:{e.get('description', '').replace(chr(10), chr(92)+'n')}",
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    Path(output).write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    print(f"Wrote {output} with {len(events)} events")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python make_ics.py <events.json> <output.ics>")
        sys.exit(1)
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    make_ics(data["events"], sys.argv[2], data.get("name", "Trip"))
