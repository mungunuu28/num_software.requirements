#!/usr/bin/env python3

"""
Шаардлагын баримт бичиг дэх хэмжигдэх боломжгүй, тодорхойгүй үгсийг
илрүүлэх скрипт.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

# 1. Шаардлагад ашиглахыг хориглох тодорхойгүй, субьектив үгсийн жагсаалт

VAGUE_TERMS: list[str] = [
    # Англи үгс
    "fast",
    "quick",
    "efficient",
    "user-friendly",
    "robust",
    "robust",
    "easy",
    "flexible",
    "reliable",
    "secure",
    "modern",
    "optimal",
    "appropriate",
    "sufficient",

    # Герман үгс (эх кодын жишээ)
    "schnell",
    "angemessen",
    "benutzerfreundlich",
    "genau",

    # Монгол үгс
    "хурдан",
    "хялбар",
    "найдвартай",
    "аюулгүй",
    "хэрэглэгчдэд ээлтэй",
    "боломжийн",
    "хангалттай",
    "үр дүнтэй",
    "орчин үеийн",
]

# 2. Тусгайлан зөвшөөрөх үгс (Exceptions)
ALLOWED: set[str] = set()
# Код бичсэн хэсгийг (Markdown code fence) алгасах
FENCE = re.compile(r"^\s*```")

def compile_patterns(terms: list[str]) -> list[tuple[str, re.Pattern[str]]]:
    """Үгсийг том жижиг үсэг харгалзахгүй хайх regex болгож бэлдэх."""
    return [(t, re.compile(rf"\b{re.escape(t)}\b", re.IGNORECASE)) for t in terms]

def check_line(line: str, patterns: list[tuple[str, re.Pattern[str]]]) -> list[str]:
    """Мөр бүрээс тодорхойгүй үгс орсон эсэхийг шалгах."""
    hits: list[str] = []
    for term, pattern in patterns:
        if term in ALLOWED:
            continue
        if pattern.search(line):
            hits.append(term)
    return hits

def check_file(path: Path, patterns: list[tuple[str, re.Pattern[str]]]) -> int:
    findings = 0
    in_fence = False
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
    for term in check_line(raw, patterns):
        print(f'{path}:{number}: "{term}" -> replace with a measurable target')
        findings += 1
    return findings

def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv[1:]] or [Path("docs")]
    patterns = compile_patterns(VAGUE_TERMS)
    files: list[Path] = []
    for target in targets:
        if target.is_dir():
            files.extend(sorted(target.rglob("*.md")))
        elif target.is_file():
            files.append(target)
        else:
            print(f"Анхааруулга: {target} олдсонгүй", file=sys.stderr)
    if not files:
        print("Шалгах Markdown файл олдсонгүй.", file=sys.stderr)
        return 0
    findings = sum(check_file(f, patterns) for f in files)
    print(f"\nШалгасан файл: {len(files)}, Нийт олдсон зөрчил: {findings}")
    if findings:
        print("Шалгалт амжилтгүй боллоо: Тодорхойгүй үгсээ бодит тоон үзүүлэлтээр сольно уу!")
        return 1
    print("Бүх шаардлага хэмжигдэхүйц тодорхой байна. Амжилттай!")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))