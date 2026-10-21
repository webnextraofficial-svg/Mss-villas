"""Generate blog article pages, the blog index and sitemap entries.

Run from anywhere:  python3 tools/blog/build_blog.py
Edit article content in posts_*.py, then re-run.
"""
import html
import json
import re
from datetime import date
from pathlib import Path

import posts_ac
import posts_interior
import posts_painting
import posts_waterproofing

ROOT = Path(__file__).resolve().parents[2] / "public_html"
SITE = "https://gharupgrade.com"
CLUSTERS = [posts_painting, posts_waterproofing, posts_interior, posts_ac]
AREAS = [
    "Kukatpally", "KPHB", "Miyapur", "Nizampet", "Hafeezpet", "Chandanagar",
    "Lingampally", "Kondapur", "Madhapur", "Gachibowli", "Pragathi Nagar",
]
MAIN_RE = re.compile(r'(<main id="main">)(.*?)(</main>)', re.S)


def esc(text):
    return html.escape(text, quote=True)


def fmt_date(iso):
    return date.fromisoformat(iso).strftime("%d %b %Y").lstrip("0")


def read_minutes(post):
    text = " ".join(body for _, body in post["sections"])
    words = len(re.sub(r"<[^>]+>", " ", text).split())
    return max(3, round(words / 200))


def prefix_paths(markup):
    return re.sub(
        r'(href|src)="(?!https?:|#|mailto:|tel:|/|\.\./)([^"]+)"',
        r'\1="../\2"',
        markup,
    )


def split_template():
    page = (ROOT / "blog.html").read_text()
    head_end = page.index("</head>")
    main_start = page.index('<main id="main">')
    main_end = page.index("</main>") + len("</main>")
    return page, page[:head_end], page[head_end:main_start], page[main_end:]


def head_block(head, title, description, canonical, extra=""):
    head = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", head, flags=re.S)
    head = re.sub(
        r'<meta name="description" content="[^"]*" />',
        f'<meta name="description" content="{esc(description)}" />',
        head,
    )
    head = re.sub(r'\s*<link rel="canonical"[^>]*>', "", head)
    head = re.sub(r'\s*<meta property="og:[^>]*>', "", head)
    head = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', "", head, flags=re.S)
    tags = (
        f'\n  <link rel="canonical" href="{canonical}" />'
        f'\n  <meta property="og:type" content="article" />'
        f'\n  <meta property="og:title" content="{esc(title)}" />'
        f'\n  <meta property="og:description" content="{esc(description)}" />'
        f'\n  <meta property="og:url" content="{canonical}" />'
        f"{extra}\n"
    )
    return head.rstrip() + tags


def area_paragraph(cluster, idx):
    lead = AREAS[(idx * 3) % len(AREAS)]
    rest = [a for a in AREAS if a != lead]
    areas = ", ".join(rest[:-1]) + f" and {rest[-1]}"
    return (
        f'<p>Ghar Upgrade provides <a href="../{cluster.CLUSTER["service_url"]}">'
        f'{esc(cluster.CLUSTER["service_name"])}</a> for homes in {esc(lead)} and across '
        f"{esc(areas)} — all within our 18 km service area.</p>"
    )


def build_post(cluster, post, idx, head, pre_main, post_main):
    c = cluster.CLUSTER
    url = f"{SITE}/blog/{post['slug']}.html"
    image_url = f"{SITE}/assets/{post['image']}"
    minutes = read_minutes(post)

    ld = [
        {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post["title"],
            "description": post["description"],
            "image": image_url,
            "datePublished": post["date"],
            "dateModified": post["date"],
            "author": {"@type": "Organization", "name": "Ghar Upgrade"},
            "publisher": {
                "@type": "Organization",
                "name": "Ghar Upgrade",
                "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/ghar-upgrade-logo.png"},
            },
            "mainEntityOfPage": url,
            "keywords": post["keyword"],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog.html"},
                {"@type": "ListItem", "position": 3, "name": post["title"], "item": url},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in post["faqs"]
            ],
        },
    ]
    extra = (
        f'\n  <meta property="og:image" content="{image_url}" />'
        + "".join(
            f'\n  <script type="application/ld+json">{json.dumps(block, ensure_ascii=False)}</script>'
            for block in ld
        )
    )

    sections = "\n".join(
        f'        <h2>{esc(h)}</h2>\n{body.strip()}' for h, body in post["sections"]
    )
    faqs = "\n".join(
        f"          <details>\n            <summary>{esc(q)}</summary>\n            <p>{esc(a)}</p>\n          </details>"
        for q, a in post["faqs"]
    )
    related = "\n".join(
        f'          <li><a href="{p["slug"]}.html"><span>{esc(c["label"])}</span>{esc(p["title"])}</a></li>'
        for p in cluster.POSTS
        if p["slug"] != post["slug"]
    )

    main = f"""<main id="main">

    <section class="post-hero">
      <div class="wrap post-wrap">
        <nav class="post-crumbs" aria-label="Breadcrumb">
          <a href="../index.html">Home</a> <span aria-hidden="true">›</span>
          <a href="../blog.html">Blog</a> <span aria-hidden="true">›</span>
          <a href="../blog.html#{c['key']}">{esc(c['label'])}</a>
        </nav>
        <p class="blog-meta"><span>{esc(c['label'])}</span> · <time datetime="{post['date']}">{fmt_date(post['date'])}</time> · {minutes} min read</p>
        <h1>{esc(post['title'])}</h1>
        <p class="post-lead">{esc(post['summary'])}</p>
      </div>
    </section>

    <article class="post">
      <div class="wrap post-wrap">
        <figure class="post-cover">
          <img src="../assets/{post['image']}" alt="{esc(post['title'])}" width="1024" height="640" />
          <span class="img-rights">© All rights reserved</span>
        </figure>

        <div class="post-body">
{sections}
        <h2>Serving homes near you</h2>
        {area_paragraph(cluster, idx)}
        </div>

        <aside class="post-cta">
          <div>
            <h2>Need help with this?</h2>
            <p>Book a free site visit — our team inspects your home and shares a clear, itemised quote.</p>
          </div>
          <div class="post-cta-actions">
            <a class="btn btn-accent" href="#" data-open-quote>Book a site visit</a>
            <a class="btn btn-outline" href="../{c['service_url']}">Explore {esc(c['label'])}</a>
          </div>
        </aside>

        <section class="post-faq" aria-labelledby="post-faq-title">
          <h2 id="post-faq-title">Frequently asked questions</h2>
          <div class="bh-faq" data-faq>
{faqs}
          </div>
        </section>

        <section class="post-related" aria-labelledby="post-related-title">
          <h2 id="post-related-title">More {esc(c['label'])} guides</h2>
          <ul>
{related}
          </ul>
        </section>
      </div>
    </article>

  </main>"""

    page = (
        prefix_paths(head_block(head, post["seo_title"], post["description"], url, extra))
        + prefix_paths(pre_main)
        + main
        + prefix_paths(post_main)
    )
    page = page.replace('<body class="page-contact page-blog page-ap">', '<body class="page-contact page-blog page-post page-ap">')
    out = ROOT / "blog" / f"{post['slug']}.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page)


def build_index(page):
    nav = "\n".join(
        f'          <a href="#{c.CLUSTER["key"]}">{esc(c.CLUSTER["label"])}</a>' for c in CLUSTERS
    )
    clusters = []
    for c in CLUSTERS:
        cards = []
        for p in c.POSTS:
            cards.append(f"""          <article class="blog-card">
            <a class="blog-card-link" href="blog/{p['slug']}.html">
              <img src="assets/{p['image']}" alt="{esc(p['title'])}" width="800" height="500" loading="lazy" />
              <div class="blog-card-body">
                <p class="blog-meta"><span>{esc(c.CLUSTER['label'])}</span> · <time datetime="{p['date']}">{fmt_date(p['date'])}</time></p>
                <h3>{esc(p['title'])}</h3>
                <p>{esc(p['summary'])}</p>
                <span class="blog-card-more">Read article →</span>
              </div>
            </a>
          </article>""")
        clusters.append(f"""    <section class="blog-section blog-cluster" id="{c.CLUSTER['key']}">
      <div class="wrap">
        <header class="blog-cluster-head">
          <div>
            <h2>{esc(c.CLUSTER['label'])} guides</h2>
            <p>{esc(c.CLUSTER['intro'])}</p>
          </div>
          <a class="apc-link" href="{c.CLUSTER['service_url']}">Visit {esc(c.CLUSTER['label'])} page →</a>
        </header>
        <div class="blog-grid">
{chr(10).join(cards)}
        </div>
      </div>
    </section>""")

    main = f"""<main id="main">

    <section class="page-hero">
      <div class="wrap page-hero-inner">
        <p class="eyebrow">Blog</p>
        <h1>Home improvement guides for Hyderabad</h1>
        <p class="page-hero-lead">Practical advice on painting, waterproofing, interiors and AC service from the Ghar Upgrade team — for homes across Kukatpally, Miyapur, Kondapur, Gachibowli and nearby areas.</p>
        <nav class="blog-cluster-nav" aria-label="Blog topics">
{nav}
        </nav>
      </div>
    </section>

{chr(10).join(clusters)}

  </main>"""
    page = MAIN_RE.sub(lambda m: main, page, count=1)
    page = re.sub(
        r'<meta name="description" content="[^"]*" />',
        '<meta name="description" content="Guides on house painting, AC service, waterproofing and interior design for Hyderabad homes — costs, fixes and planning tips from Ghar Upgrade." />',
        page,
    )
    page = page.replace("<title>Blog | Ghar Upgrade</title>", "<title>Home Improvement Blog Hyderabad | Ghar Upgrade</title>")
    if 'rel="canonical"' not in page:
        page = page.replace("</head>", f'  <link rel="canonical" href="{SITE}/blog.html" />\n</head>', 1)
    (ROOT / "blog.html").write_text(page)


def build_sitemap():
    path = ROOT / "sitemap.xml"
    xml = path.read_text()
    xml = re.sub(r"\s*<url>\s*<loc>[^<]*/blog/[^<]*</loc>.*?</url>", "", xml, flags=re.S)
    entries = "".join(
        f"\n  <url>\n    <loc>{SITE}/blog/{p['slug']}.html</loc>\n    <lastmod>{p['date']}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>"
        for c in CLUSTERS
        for p in c.POSTS
    )
    xml = xml.replace("\n</urlset>", entries + "\n</urlset>")
    path.write_text(xml)


def main():
    page, head, pre_main, post_main = split_template()
    for cluster in CLUSTERS:
        for idx, post in enumerate(cluster.POSTS):
            build_post(cluster, post, idx, head, pre_main, post_main)
    build_index(page)
    build_sitemap()
    print(f"Built {sum(len(c.POSTS) for c in CLUSTERS)} posts")


if __name__ == "__main__":
    main()
