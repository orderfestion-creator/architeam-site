#!/usr/bin/env python3
"""Architeam blog builder (ME / RU / EN).

The site itself is a finished Astro build (no source). This script reuses the real
header, footer and styles of an existing page per language, so blog pages look native.

Sources:  _blog/posts/<lang>/YYYY-MM-DD-<slug>.html   (lang = me | ru | en)
  <!--META
  { "slug": "...", "date": "YYYY-MM-DD", "title": "...", "h1": "...",
    "description": "...", "lead": "...", "keyword": "...", "service": "/projekat-kuce/",
    "faq": [{"q": "...", "a": "..."}] }
  -->
  <h2>…</h2><p>…</p> …   (body HTML)

Output:   /blog/…  /ru/blog/…  /en/blog/…  (index + one page per post), rss.xml per language,
          sitemap-blog.xml (+ registered in sitemap-index.xml), "Blog" link in the main nav of every page.

Run:  python3 _blog/build.py [--check]   (standard library only)
"""
import html
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_blog", "posts")
SITE = "https://architeam.me"
LANGS = ["me", "ru", "en"]
REQUIRED = ["slug", "date", "title", "h1", "description", "lead", "keyword", "service"]

L = {
    "me": dict(prefix="", hreflang="sr-ME", html_lang="sr-Latn-ME", og="sr_ME", ref="kontakt/index.html",
               home="/", home_name="Početna", blog="Blog", contact="/kontakt/", contact_name="Kontakt",
               months=["januar", "februar", "mart", "april", "maj", "jun", "jul", "avgust", "septembar", "oktobar", "novembar", "decembar"],
               idx_title="Blog o projektovanju i gradnji u Crnoj Gori | Architeam",
               idx_desc="Savjeti o projektima kuća i vila, glavnom projektu, statici, instalacijama, legalizaciji i dozvoli za gradnju u Crnoj Gori — blog projektnog biroa Architeam.",
               idx_kicker="Blog · projektni biro", idx_h1="Projektovanje i gradnja u Crnoj Gori — praktično",
               idx_lead="Kako se planira kuća, šta sadrži glavni projekat, kako do dozvole ili legalizacije: odgovori iz prakse projektnog biroa.",
               all="Svi članci", read="Pročitajte →", more="Pročitajte još", faq="Česta pitanja",
               cta_h="Pošaljite skicu, fotografiju ili PDF", cta_p="Odgovaramo za 1 sat radnim danom. Skica na papiru, fotografija ili crtež iz interneta — sve je dobar početak.",
               cta_btn="Kontakt i upit", services="Usluge", empty="Prvi članci uskoro.", by="Architeam, projektni biro"),
    "ru": dict(prefix="/ru", hreflang="ru", html_lang="ru", og="ru_RU", ref="ru/kontakty/index.html",
               home="/ru/", home_name="Главная", blog="Блог", contact="/ru/kontakty/", contact_name="Контакты",
               months=["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"],
               idx_title="Блог о проектировании и строительстве в Черногории | Architeam",
               idx_desc="Проект дома и виллы, основной проект, расчёт конструкций, инженерные системы, легализация и разрешение на строительство в Черногории — блог проектного бюро Architeam.",
               idx_kicker="Блог · проектное бюро", idx_h1="Проектирование и строительство в Черногории — на практике",
               idx_lead="Как спланировать дом, что входит в основной проект, как получить разрешение или легализовать постройку: ответы из практики проектного бюро.",
               all="Все статьи", read="Читать →", more="Читайте также", faq="Частые вопросы",
               cta_h="Пришлите эскиз, фото или PDF", cta_p="Отвечаем в течение часа в рабочий день. Эскиз от руки, фотография или картинка из интернета — уже хорошее начало.",
               cta_btn="Контакты и запрос", services="Услуги", empty="Первые статьи скоро.", by="Architeam, проектное бюро"),
    "en": dict(prefix="/en", hreflang="en", html_lang="en", og="en_GB", ref="en/contact/index.html",
               home="/en/", home_name="Home", blog="Blog", contact="/en/contact/", contact_name="Contact",
               months=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
               idx_title="Blog on design and building in Montenegro | Architeam",
               idx_desc="House and villa design, main design (glavni projekat), structural design, MEP, legalisation and building permits in Montenegro — the Architeam design studio blog.",
               idx_kicker="Blog · design studio", idx_h1="Designing and building in Montenegro — in practice",
               idx_lead="How a house is planned, what the main design contains, how to get a permit or legalise a building: answers from a working design studio.",
               all="All articles", read="Read →", more="Read next", faq="FAQ",
               cta_h="Send a sketch, photo or PDF", cta_p="We reply within an hour on working days. A hand sketch, a photo or a picture from the internet is a good start.",
               cta_btn="Contact and enquiry", services="Services", empty="First articles coming soon.", by="Architeam design studio"),
}

BLOG_CSS = """
.blog-hero{padding:36px 0 40px}
.blog-hero h1{font-size:clamp(2rem,4.2vw,3.4rem);max-width:22ch}
.blog-hero .lead{max-width:62ch}
.blog-meta{font:500 .85rem/1.4 var(--mono);color:#b9cbe6;margin:0 0 18px;letter-spacing:.02em}
.blog-grid{display:grid;gap:32px;padding:44px 0 8px}
@media (width>=980px){.blog-grid{grid-template-columns:minmax(0,1fr) 340px;gap:48px}}
.blog-body{min-width:0;max-width:74ch}
.blog-body h2{font-size:clamp(1.6rem,2.8vw,2.2rem);margin-top:1.4em}
.blog-body h2:first-child{margin-top:0}
.blog-body h3{font-size:1.35rem;margin-top:1.1em}
.blog-body ul,.blog-body ol{padding-left:1.25em;margin:0 0 1em;display:grid;gap:6px}
.blog-body li::marker{color:var(--prussian-2)}
.blog-body .table-wrap{margin:8px 0 22px;border:1px solid var(--rule);border-radius:var(--r)}
.blog-body th{text-align:left;padding:12px 16px;background:var(--soft);font:600 .95rem/1.3 var(--font);border-bottom:1px solid var(--rule)}
.blog-body td{font-size:.97rem}
.blog-note{border-left:4px solid var(--chalk);background:var(--card);padding:16px 20px;border-radius:0 var(--r) var(--r) 0;margin:6px 0 22px}
.blog-note p{margin:0}
.blog-aside{display:grid;gap:16px;align-content:start}
@media (width>=980px){.blog-aside{position:sticky;top:110px}}
.blog-cta{padding:24px;display:grid;gap:12px}
.blog-cta h3{font-size:1.4rem;margin:0}
.blog-cta p{color:var(--slate);margin:0}
.blog-cta .btn{width:100%}
.blog-cards{display:grid;gap:20px}
@media (width>=700px){.blog-cards{grid-template-columns:repeat(2,1fr)}}
@media (width>=1050px){.blog-cards{grid-template-columns:repeat(3,1fr)}}
.blog-card{padding:22px;display:grid;gap:8px;align-content:start;text-decoration:none;color:var(--ink)}
.blog-card:hover{border-color:var(--prussian-2)}
.blog-card .d{font:500 .78rem/1.3 var(--mono);color:var(--slate)}
.blog-card b{font:700 1.3rem/1.15 var(--cond)}
.blog-card span{color:var(--slate);font-size:.95rem}
.blog-card em{font-style:normal;font-weight:600;color:var(--focus)}
.blog-links{display:flex;flex-wrap:wrap;gap:10px;padding:0;margin:0;list-style:none}
.blog-links a{display:inline-block;padding:8px 14px;border:1px solid var(--rule);border-radius:99px;background:var(--card);text-decoration:none;color:var(--ink);font-size:.95rem}
.blog-links a:hover{border-color:var(--prussian-2)}
"""


def esc(s):
    return html.escape(s, quote=True)


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def human_date(d, lang):
    y, m, dd = (int(x) for x in d.split("-"))
    mon = L[lang]["months"][m - 1]
    return f"{dd}. {mon} {y}." if lang == "me" else (f"{dd} {mon} {y}" if lang == "ru" else f"{dd} {mon} {y}")


def blog_url(lang, slug=None):
    base = f"{L[lang]['prefix']}/blog/"
    return base + (f"{slug}/" if slug else "")


# ---------------------------------------------------------------- posts

def load_posts():
    posts = {lg: [] for lg in LANGS}
    for lg in LANGS:
        d = os.path.join(SRC, lg)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".html"):
                continue
            raw = open(os.path.join(d, name), encoding="utf-8").read()
            m = re.match(r"\s*<!--META\s*(\{.*?\})\s*-->\s*(.*)\Z", raw, re.S)
            if not m:
                raise SystemExit(f"{lg}/{name}: missing <!--META {{...}} --> header")
            meta = json.loads(m.group(1))
            missing = [k for k in REQUIRED if not meta.get(k)]
            if missing:
                raise SystemExit(f"{lg}/{name}: missing meta fields {missing}")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", meta["slug"]):
                raise SystemExit(f"{lg}/{name}: bad slug {meta['slug']!r}")
            meta.update(body=m.group(2).strip(), file=f"{lg}/{name}", lang=lg)
            meta.setdefault("updated", meta["date"])
            meta.setdefault("faq", [])
            posts[lg].append(meta)
        slugs = [p["slug"] for p in posts[lg]]
        dup = {s for s in slugs if slugs.count(s) > 1}
        if dup:
            raise SystemExit(f"{lg}: duplicate slugs {sorted(dup)}")
        posts[lg].sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts


# ---------------------------------------------------------------- page chrome from a real page

def chrome(lang):
    s = open(os.path.join(ROOT, L[lang]["ref"]), encoding="utf-8").read()
    head = s[s.index("<head>") + 6:s.index("</head>")]
    keep_from = head.index('<script>document.documentElement')
    head_tail = head[keep_from:]
    # keep the organisation JSON-LD and the page CSS, drop page-specific JSON-LD
    lds = re.findall(r'<script type="application/ld\+json">.*?</script>', head_tail, re.S)
    org = [x for x in lds if '"#org"' in x or '/#org"' in x]
    for x in lds:
        head_tail = head_tail.replace(x, "")
    head_tail = head_tail.replace("</style>", BLOG_CSS + "</style>", 1) if "</style>" in head_tail else head_tail + f"<style>{BLOG_CSS}</style>"
    body = s[s.index("<body"):]
    header = body[:body.index('<nav class="crumbs')]
    after = body[body.index("</main>") + len("</main>"):]
    cid = re.search(r"<main id=\"main\"( data-astro-cid-\w+)?", body).group(1) or ""
    return dict(head=head_tail, org="".join(org[:1]), header=header, after=after, cid=cid)


def set_langs(header, lang, urls):
    """urls: {lang: href} for the language switcher."""
    def repl(m):
        a = m.group(0)
        hl = re.search(r'hreflang="([^"]+)"', a).group(1)
        lg = {"sr-ME": "me", "ru": "ru", "en": "en"}.get(hl)
        if lg is None:
            return a
        a = re.sub(r'href="[^"]*"', f'href="{urls[lg]}"', a, count=1)
        a = a.replace(' aria-current="true"', "")
        if lg == lang:
            a = a.replace(f'hreflang="{hl}"', f'hreflang="{hl}" aria-current="true"', 1)
        return a
    return re.sub(r'<a role="listitem"[^>]*>', repl, header)


def page(lang, title, desc, canonical, alternates, ld, crumbs, main_html, og_type="article", robots="index,follow,max-image-preview:large"):
    c = CHROME[lang]
    alt_links = "".join(f'<link rel="alternate" hreflang="{L[lg]["hreflang"]}" href="{SITE}{u}">' for lg, u in alternates.items())
    if "me" in alternates:
        alt_links += f'<link rel="alternate" hreflang="x-default" href="{SITE}{alternates["me"]}">'
    switch = {lg: alternates.get(lg, blog_url(lg)) for lg in LANGS}
    header = set_langs(c["header"], lang, switch)
    ldj = "".join(f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>' for b in ld)
    cr = "".join(f'<li{c["cid"]}><a href="{u}"{c["cid"]}>{esc(n)}</a></li>' for u, n in crumbs[:-1])
    cr += f'<li{c["cid"]}><span aria-current="page"{c["cid"]}>{esc(crumbs[-1][1])}</span></li>'
    return (f'<!DOCTYPE html><html lang="{L[lang]["html_lang"]}"{c["cid"]}><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">'
            f'<link rel="canonical" href="{SITE}{canonical}">{alt_links}'
            f'<link rel="alternate" type="application/rss+xml" title="Architeam blog" href="{SITE}{blog_url(lang)}rss.xml">'
            f'<meta name="robots" content="{robots}">'
            f'<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="Architeam">'
            f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">'
            f'<meta property="og:url" content="{SITE}{canonical}"><meta property="og:image" content="{SITE}/og.png">'
            f'<meta property="og:locale" content="{L[lang]["og"]}"><meta name="twitter:card" content="summary_large_image">'
            f'<meta name="theme-color" content="#0e2a4f">{c["head"]}{c["org"]}{ldj}</head>'
            f'{header}<nav class="crumbs wrap" aria-label="Breadcrumb"{c["cid"]}><ol{c["cid"]}>{cr}</ol></nav>'
            f'<main id="main"{c["cid"]}>{main_html}</main>{c["after"]}')


def cta_box(lang):
    t = L[lang]
    return (f'<div class="frame blog-cta"><h3>{esc(t["cta_h"])}</h3><p>{esc(t["cta_p"])}</p>'
            f'<a class="btn btn-primary" href="viber://chat?number=%2B38268610290" data-goal="viber">Viber</a>'
            f'<a class="btn btn-ghost" href="https://wa.me/38268610290" data-goal="whatsapp">WhatsApp</a>'
            f'<a class="btn btn-ghost" href="{t["contact"]}">{esc(t["cta_btn"])}</a></div>')


def card(p):
    t = L[p["lang"]]
    return (f'<a class="frame blog-card" href="{blog_url(p["lang"], p["slug"])}"><span class="d">{human_date(p["date"], p["lang"])}</span>'
            f'<b>{esc(strip_tags(p["h1"]))}</b><span>{esc(p["description"])}</span><em>{esc(t["read"])}</em></a>')


def render_post(p, lang_posts):
    lang, t = p["lang"], L[p["lang"]]
    url = blog_url(lang, p["slug"])
    h1 = strip_tags(p["h1"])
    ld = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": h1, "description": p["description"],
           "datePublished": p["date"], "dateModified": p["updated"], "inLanguage": t["hreflang"], "mainEntityOfPage": SITE + url,
           "author": {"@type": "Organization", "name": "Architeam", "url": SITE + "/"},
           "publisher": {"@id": SITE + "/#org"}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": t["home_name"], "item": SITE + t["home"]},
              {"@type": "ListItem", "position": 2, "name": t["blog"], "item": SITE + blog_url(lang)},
              {"@type": "ListItem", "position": 3, "name": h1, "item": SITE + url}]}]
    faq = ""
    if p["faq"]:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": strip_tags(f["q"]), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(f["a"])}} for f in p["faq"]]})
        items = "".join(f"<details><summary>{esc(strip_tags(f['q']))}</summary><p>{f['a']}</p></details>" for f in p["faq"])
        faq = f'<section class="section"><div class="wrap"><div class="section-head"><h2>{esc(t["faq"])}</h2></div><div class="faq">{items}</div></div></section>'
    others = [o for o in lang_posts if o["slug"] != p["slug"]][:3]
    rel = ""
    if others:
        rel = f'<section class="section"><div class="wrap"><div class="section-head"><h2>{esc(t["more"])}</h2></div><div class="blog-cards">{"".join(card(o) for o in others)}</div></div></section>'
    main = (f'<section class="on-blue blueprint-grid blog-hero"><div class="wrap"><p class="kicker">{esc(t["blog"])} · Architeam</p>'
            f'<h1>{p["h1"]}</h1><p class="lead">{p["lead"]}</p>'
            f'<p class="blog-meta"><time datetime="{p["date"]}">{human_date(p["date"], lang)}</time> · {esc(t["by"])}</p>'
            f'<div class="btn-row"><a class="btn btn-primary" href="viber://chat?number=%2B38268610290" data-goal="viber">Viber</a>'
            f'<a class="btn btn-ghost" href="https://wa.me/38268610290" data-goal="whatsapp">WhatsApp</a></div></div></section>'
            f'<div class="wrap blog-grid"><article class="blog-body">{p["body"]}</article>'
            f'<aside class="blog-aside">{cta_box(lang)}</aside></div>{faq}{rel}')
    title = p["title"] if "Architeam" in p["title"] else f'{p["title"]} | Architeam'
    crumbs = [(t["home"], t["home_name"]), (blog_url(lang), t["blog"]), (url, h1)]
    return page(lang, title, p["description"], url, {lang: url}, ld, crumbs, main)


def render_index(lang, lang_posts):
    t = L[lang]
    url = blog_url(lang)
    cards = "".join(card(p) for p in lang_posts) or f'<p class="lead">{esc(t["empty"])}</p>'
    ld = [{"@context": "https://schema.org", "@type": "Blog", "name": "Architeam blog", "url": SITE + url, "inLanguage": t["hreflang"],
           "blogPost": [{"@type": "BlogPosting", "headline": strip_tags(p["h1"]), "url": SITE + blog_url(lang, p["slug"]), "datePublished": p["date"]} for p in lang_posts[:30]]}]
    main = (f'<section class="on-blue blueprint-grid blog-hero"><div class="wrap"><p class="kicker">{esc(t["idx_kicker"])}</p>'
            f'<h1>{esc(t["idx_h1"])}</h1><p class="lead">{esc(t["idx_lead"])}</p></div></section>'
            f'<section class="section"><div class="wrap"><div class="section-head"><h2>{esc(t["all"])}</h2></div><div class="blog-cards">{cards}</div></div></section>')
    crumbs = [(t["home"], t["home_name"]), (url, t["blog"])]
    live = [lg for lg in LANGS if POSTS[lg]]
    alternates = {lg: blog_url(lg) for lg in (live if lang in live else [lang])}
    robots = "index,follow" if lang_posts else "noindex,follow"
    return page(lang, t["idx_title"], t["idx_desc"], url, alternates, ld, crumbs, main, og_type="website", robots=robots)


def render_rss(lang, lang_posts):
    items = "".join(f"<item><title>{esc(strip_tags(p['h1']))}</title><link>{SITE}{blog_url(lang, p['slug'])}</link><guid>{SITE}{blog_url(lang, p['slug'])}</guid>"
                    f"<pubDate>{date.fromisoformat(p['date']).strftime('%a, %d %b %Y')} 08:00:00 +0100</pubDate><description>{esc(p['description'])}</description></item>"
                    for p in lang_posts[:30])
    return (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Architeam blog ({lang.upper()})</title>'
            f'<link>{SITE}{blog_url(lang)}</link><description>{esc(L[lang]["idx_desc"])}</description><language>{L[lang]["hreflang"]}</language>{items}</channel></rss>\n')


# ---------------------------------------------------------------- site-wide wiring (idempotent)

NAV_LINK = {"me": ("/kontakt/", "/blog/", "Blog"), "ru": ("/ru/kontakty/", "/ru/blog/", "Блог"), "en": ("/en/contact/", "/en/blog/", "Blog")}


def add_nav_links():
    """Insert a Blog link before the Contact link in the desktop nav and the mobile nav only."""
    changed = 0
    for dirpath, _, files in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT)
        if rel.startswith((".git", "_blog", "_astro", ".github")):
            continue
        for f in files:
            if not f.endswith(".html"):
                continue
            path = os.path.join(dirpath, f)
            s = open(path, encoding="utf-8").read()
            o = s
            for start, end in (('<nav class="nav"', "</nav>"), ('<div class="mnav"', "</header>")):
                i = s.find(start)
                if i < 0:
                    continue
                j = s.find(end, i)
                seg = s[i:j]
                for contact, blog, label in NAV_LINK.values():
                    m = re.search(r'<a href="' + re.escape(contact) + r'"( data-astro-cid-\w+)?>', seg)
                    if m and f'<a href="{blog}"' not in seg:
                        seg = seg.replace(m.group(0), f'<a href="{blog}"{m.group(1) or ""}>{label}</a>' + m.group(0), 1)
                s = s[:i] + seg + s[j:]
            if s != o:
                open(path, "w", encoding="utf-8").write(s)
                changed += 1
    return changed


def write_sitemap(posts):
    urls = []
    live = [lg for lg in LANGS if posts[lg]]
    for lg in live:
        latest = posts[lg][0]["date"]
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{L[x]["hreflang"]}" href="{SITE}{blog_url(x)}"/>' for x in live)
        urls.append(f'<url><loc>{SITE}{blog_url(lg)}</loc><lastmod>{latest}</lastmod>{alts}</url>')
        for p in posts[lg]:
            u = SITE + blog_url(lg, p["slug"])
            urls.append(f'<url><loc>{u}</loc><lastmod>{p["updated"]}</lastmod><xhtml:link rel="alternate" hreflang="{L[lg]["hreflang"]}" href="{u}"/></url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
           + "".join(urls) + "</urlset>\n")
    open(os.path.join(ROOT, "sitemap-blog.xml"), "w", encoding="utf-8").write(xml)
    idx_path = os.path.join(ROOT, "sitemap-index.xml")
    idx = open(idx_path, encoding="utf-8").read()
    if "sitemap-blog.xml" not in idx:
        idx = idx.replace("</sitemapindex>", f"<sitemap><loc>{SITE}/sitemap-blog.xml</loc></sitemap></sitemapindex>")
        open(idx_path, "w", encoding="utf-8").write(idx)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)


# ---------------------------------------------------------------- checks

def stems(t):
    return {w[:5] for w in re.findall(r"\w+", strip_tags(t).lower()) if len(w) > 3}


def check(posts):
    problems = []
    known = set()
    for dirpath, _, files in os.walk(ROOT):
        if "index.html" in files:
            rel = os.path.relpath(dirpath, ROOT)
            known.add("/" if rel == "." else f"/{rel}/")
    for lg in LANGS:
        for p in posts[lg]:
            f = p["file"]
            blob = p["body"] + json.dumps(p["faq"], ensure_ascii=False)
            for href in re.findall(r'href="(/[^"#?]*)', blob):
                if href not in known:
                    problems.append(f"{f}: internal link {href} does not exist")
            if re.search(r"&lt;\w", p["body"]):
                problems.append(f"{f}: escaped HTML in body")
            if not 110 <= len(p["description"]) <= 170:
                problems.append(f"{f}: description is {len(p['description'])} chars (aim 120-160)")
            if len(strip_tags(p["title"])) > 70:
                problems.append(f"{f}: title is {len(p['title'])} chars (keep <= 65)")
            need = stems(p["keyword"])
            for field in ("title", "h1"):
                lacking = need - stems(p[field])
                if lacking:
                    problems.append(f"{f}: {field} does not contain the keyword '{p['keyword']}' (missing {sorted(lacking)})")
            links = re.findall(r'href="/', p["body"])
            if len(links) < 3:
                problems.append(f"{f}: only {len(links)} internal links in body (need 3+)")
            if f'href="{p["service"]}"' not in p["body"]:
                problems.append(f"{f}: body has no link to its service page {p['service']}")
            if p["service"] not in known:
                problems.append(f"{f}: service page {p['service']} does not exist")
            prefix = L[lg]["prefix"] + "/"
            for href in re.findall(r'href="(/[^"#?]*)', p["body"]):
                other = [x for x in LANGS if x != lg and L[x]["prefix"] and href.startswith(L[x]["prefix"] + "/")]
                if other or (lg != "me" and not href.startswith(prefix)):
                    problems.append(f"{f}: link {href} points to another language version")
    return problems


def main():
    global CHROME
    n = add_nav_links()
    CHROME = {lg: chrome(lg) for lg in LANGS}
    posts = load_posts()
    POSTS.update(posts)
    for lg in LANGS:
        base = os.path.join(ROOT, blog_url(lg).strip("/"))
        for p in posts[lg]:
            write(os.path.join(base, p["slug"], "index.html"), render_post(p, posts[lg]))
        write(os.path.join(base, "index.html"), render_index(lg, posts[lg]))
        write(os.path.join(base, "rss.xml"), render_rss(lg, posts[lg]))
    write_sitemap(posts)
    print("built: " + ", ".join(f"{lg}={len(posts[lg])}" for lg in LANGS) + (f"; nav links added to {n} page(s)" if n else ""))
    if "--check" in sys.argv:
        problems = check(posts)
        for pr in problems:
            print("PROBLEM:", pr)
        if problems:
            sys.exit(1)
        print("check OK")


CHROME = {}
POSTS = {}
if __name__ == "__main__":
    main()
