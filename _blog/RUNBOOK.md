# Architeam blog — runbook for each scheduled run

Site: https://architeam.me — Architeam, projektni biro (LEUSMAX DOO, Ulcinj): architectural design of houses, villas and apartment buildings, idejno rješenje, glavni projekat, structural design and calculations, steel structures and shop drawings, MEP, legalisation and as-built surveys, drawings on demand (AutoCAD/3D, barbecues, memorials). Signature and revision through licensed partners.
Blog: https://architeam.me/blog/ (ME), /ru/blog/ (RU), /en/blog/ (EN). One new article per run, Tue/Thu/Sat.
Languages: ME more often — pattern ME, ME, RU, ME, ME, EN (see `_blog/KEYWORDS.md`).
The owner chose to publish immediately (no manual approval step). That makes the self-review in step 6 mandatory.

Architeam is a separate brand from varimo.me (metal fabrication) and leustech.me. Never mention, link to or copy from them. Architeam writes about design, drawings, calculations and documents — not about making or installing metalwork.

## How publishing works
1. Article source: `_blog/posts/<lang>/YYYY-MM-DD-<slug>.html` (lang = me | ru | en): META JSON header + HTML body. Copy the structure of the newest existing post.
2. `python3 _blog/build.py --check` builds `/blog/…`, `/ru/blog/…`, `/en/blog/…` (pages reuse the real header/footer/styles of the contact page in that language), RSS per language, `sitemap-blog.xml`, and makes sure every page's menu has the Blog link. It must print `check OK`.
3. Commit everything and push to `main`. GitHub Actions (`.github/workflows/deploy.yml`) rebuilds, validates and uploads to Sprinthost over FTP. `send.php` (Telegram bot token) is not in the repo and must never be added.
4. The site has no Astro source in this repo: these HTML files ARE the site. Do not edit generated blog pages by hand; site-wide changes are made carefully in the HTML files.

## Steps for a run
1. Read `_blog/KEYWORDS.md` and `_blog/LOG.md`. Determine the language from the rotation (number of rows in LOG). ME → first `todo` cluster in section C; RU/EN → first `todo` topic in that language's list in section D. Never write about section A phrases (they belong to service/city pages) or section B (needs owner confirmation).
2. Read the target service page(s) on the site (e.g. `projekat-kuce/index.html`, `cijene/index.html`, `dozvola-za-gradnju-crna-gora/index.html`; RU/EN counterparts from the page map) so the article agrees with what the site says about services, process, prices and deadlines.
3. Research the topic with WebSearch (in the article's language and in ME/BS/HR/SR): what people ask, what competitors answer, what is missing. Find the natural search phrase for RU/EN. Use research for gaps and wording, never copy.
4. Write the article in `_blog/posts/<lang>/` following the SEO rules and article rules below.
5. Run `python3 _blog/build.py --check`. Fix every PROBLEM line.
6. **Self-review before publishing (Google requires manual review of AI-assisted content, Oct 2026).** Re-read as a sceptical licensed engineer and as a client:
   - Every factual or legal statement: certainly true and generally accepted in Montenegro? If not sure, remove it or phrase it as "zavisi od opštine/plana — provjeravamo za vaš slučaj". Procedures differ by municipality and object type; never state a law article, fee amount or official deadline unless you verified it in an official source during this run and cite the source in the text.
   - Numbers: prices and deadlines only exactly as published on the site's own pages (`/cijene/`, service pages) and with a link to that page. **If two site pages give different numbers for the same thing (e.g. glavni projekat deadline differs between /cijene/, /projekat-kuce/ and /dozvola-za-gradnju-crna-gora/), do not quote either — say it is confirmed in the offer.** No other prices, durations, code values, thicknesses or loads.
   - Same review for title, description, FAQ answers (they appear in search and structured data).
   - Language quality: ME ijekavica (no ekavica: mesto→mjesto, ceo→cio); RU natural, not a translation from ME; EN plain British/international English. No keyword stuffing, no repeated phrases.
   - Does it answer the intent better than a generic page? Would the reader still need to search again? Fix gaps.
7. Update `_blog/KEYWORDS.md` (status → `done YYYY-MM-DD <url>`) and add a row to `_blog/LOG.md` with status "not live".
8. `git add -A && git commit -m "Blog (<lang>): <title>" && git push origin main` (do `git fetch origin main` and rebase first if needed).
9. Wait for the deploy: `gh run list --repo orderfestion-creator/architeam-site --limit 1` every ~20 s until completed. On success set the LOG row to "live" (small extra commit + push). On failure `gh run view <id> --log-failed` and report.
10. Report to the owner in Russian, short: language, article title, link, primary keyword, one line about the content. If anything failed, say exactly what and what she needs to do.

## If something is broken
- `git push` fails or the repo is unreachable: do NOT write a second article. Tell the owner (in Russian) what failed and that the GitHub connection needs fixing (claude.ai → Settings → Connectors → GitHub, access to architeam-site). Put the article text in the message.
- Deploy fails on the FTP step: report the error line (most likely the FTP_PASSWORD secret was changed/removed, or the server folder differs). Retry at most once.
- A previous LOG row is "not live": fix/publish it first, no second article in the same run.
- Queues empty: report and stop (if RU/EN queue is empty, use ME for that slot).

## SEO rules (Google Search Central guidance as of October 2026)
Sources checked 2026-10-26: "Creating helpful, reliable, people-first content" (updated 2026-10-05), "Using generative AI content" (updated 2026-10-01: manual fact-check and review of all AI-generated content incl. titles, descriptions, structured data), spam policies (scaled content abuse, doorway pages), Google's generative-AI search guide (May 2026: SEO fundamentals, no special AI optimisation, synonyms understood), FAQ rich results discontinued (May 2026).

- People-first: write for someone in Montenegro (or a foreign buyer) who is about to order design work or documents. Leave them able to decide and to send a good enquiry.
- Show first-hand practice of a design studio: what we check first (plan, UTU, terrain, survey), what goes into each phase and each "sveska", where projects get returned and why, how to brief the architect. Concrete and specific — no filler that could be on any website in any country.
- YMYL-adjacent topics (permits, legalisation, structural safety, money): extra care with accuracy; when the answer depends on the municipality, plan or object type, say so plainly.
- No preferred word count: usually 4,000–9,000 characters of body text; never pad.
- One search intent per article; never two articles for the same intent or near-identical phrase variants.
- No city-specific blog articles (doorway pages); cities only where naturally true.
- Don't change dates or re-publish to look fresh. Don't chase topics outside Architeam's services.
- On-page: primary phrase in title (≤ 65 chars, near the start), H1, slug, first paragraph, META keyword, and naturally in one H2. Description 120–160 chars, click-worthy, includes the primary phrase. Secondary phrases in H2/H3/body where they fit, once or twice each.
- Structure: direct answer in the first paragraph; H2 sections matching real questions; a comparison/decision table where useful; numbered "common mistakes"; "what to send us" list.
- Internal links: 3–6 in the body, all in the SAME language. One to the cluster's main service page using a section-A phrase as anchor text; /cijene/ (or /ru/ceny/, /en/prices/) when price is discussed; 1–2 earlier blog posts of the same language when genuinely related (optionally add a link back from an older related post by editing its source). The build fails on non-existent links and on links to another language.
- FAQ in META: 4–6 real questions, short accurate answers (shown on page; no FAQ rich results in Google any more — write them for readers).
- Authorship: published as Architeam (organization). Never invent people, credentials, licences, projects, clients, reviews or statistics.

## Article rules
- Body HTML allowed: h2, h3, p, strong, em, a, ul, ol, li, `<div class="table-wrap"><table>…</table></div>`, `<div class="blog-note"><p>…</p></div>`. No images (the site has no photo library; the design is drawn graphics) — use tables, lists and notes for structure.
- ME: ijekavica, "vi". RU: «вы», терминология Черногории с пояснением (idejno rješenje — эскизный проект, glavni projekat — основной проект, UTU — градостроительно-технические условия). EN: explain local terms in brackets (idejno rješenje — concept design).
- Set META "service" to the cluster's main service page in the article's language.
- Contacts are in the template (Viber, WhatsApp, contact page); don't paste phone numbers into the body.
