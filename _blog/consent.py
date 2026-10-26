#!/usr/bin/env python3
"""Insert the cookie-consent banner (which loads Yandex Metrika after "Accept") into every page.

The site's own script already looks for [data-cc] with data-ym / data-ga and loads analytics only
after consent; the banner element itself was missing from the Astro build. Idempotent: pages that
already have the banner get their counter ids updated.

Usage: python3 _blog/consent.py            (ids below)
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YM = "113803365"   # Yandex Metrika counter for architeam.me
GA = ""            # Google Analytics id (G-XXXX), empty = not used
CID = " data-astro-cid-kror3uvh"

TEXT = {
    "sr": ("Koristimo kolačiće za analitiku posjeta (Yandex Metrica), samo uz vašu saglasnost.", "Kolačići", "/kolacici/", "Prihvati", "Samo neophodni", "Kolačići"),
    "ru": ("Мы используем cookies для аналитики посещений (Яндекс Метрика) — только с вашего согласия.", "Подробнее", "/ru/cookies/", "Принять", "Только необходимые", "Cookies"),
    "en": ("We use cookies for visit analytics (Yandex Metrica) only with your consent.", "Cookies", "/en/cookies/", "Accept", "Necessary only", "Cookies"),
}
ANCHOR = '<script type="module">var e=document.querySelector(`[data-cc]`)'


def banner(lang):
    msg, more, url, ok, no, label = TEXT[lang]
    ga = f' data-ga="{GA}"' if GA else ""
    return (f'<div class="cc" data-cc data-ym="{YM}"{ga} hidden role="dialog" aria-label="{label}"{CID}>'
            f'<p{CID}>{msg} <a href="{url}"{CID}>{more}</a></p>'
            f'<div class="btn-row"{CID}><button type="button" class="btn btn-primary" data-cc-accept{CID}>{ok}</button>'
            f'<button type="button" class="btn btn-ghost" data-cc-decline{CID}>{no}</button></div></div>')


def main():
    n = 0
    for dirpath, _, files in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT)
        if rel.startswith((".git", "_blog", "_astro", ".github")):
            continue
        for f in files:
            if not f.endswith(".html"):
                continue
            path = os.path.join(dirpath, f)
            s = open(path, encoding="utf-8").read()
            if ANCHOR not in s:
                continue
            lang = re.search(r'<html lang="([a-z]+)', s).group(1)
            lang = lang if lang in TEXT else "sr"
            o = s
            s = re.sub(r'<div class="cc" data-cc.*?</div></div>', "", s, flags=re.S)
            s = s.replace(ANCHOR, banner(lang) + ANCHOR, 1)
            if s != o:
                open(path, "w", encoding="utf-8").write(s)
                n += 1
    print(f"consent banner set on {n} page(s), Metrika {YM}")


if __name__ == "__main__":
    main()
