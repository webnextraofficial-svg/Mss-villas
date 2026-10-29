"""Build insights.html and insights/<slug>.html from posts.py.

The header and footer are copied from public_html/contact.html, so re-run this
after changing the shared site chrome.

Run: python3 tools/insights/build_insights.py
"""
import html
import json
import re
from pathlib import Path

from posts import POSTS, PUBLISHED, PUBLISHED_LABEL

ROOT = Path(__file__).resolve().parent.parent.parent / "public_html"
SITE = "https://www.mssrealtors.com"
TEMPLATE = ROOT / "contact.html"

LOCAL_URL = re.compile(r'((?:href|src)=")(?!https?:|#|mailto:|tel:|/|data:|javascript:)')


def chrome() -> tuple:
    src = TEMPLATE.read_text()
    head, rest = src.split('<main id="main">', 1)
    _, tail = rest.split("</main>", 1)
    head = head.replace('class="page-contact page-ap"', 'class="page-insights page-ap"')
    head = re.sub(r'<meta name="description"[^>]*>\n', "", head)
    head = re.sub(r"<title>.*?</title>\n", "", head)
    head = head.replace(' class="is-active" aria-current="page"', "")
    tail = tail.replace(' aria-current="page"', "")
    head = head.replace('<li><a href="insights.html">', '<li><a href="insights.html" class="is-active" aria-current="page">', 1)
    return head, tail


def page(head: str, tail: str, meta: str, main: str, depth: int) -> str:
    doc = head.replace("</head>", meta + "</head>", 1) + '<main id="main">\n' + main + "\n  </main>" + tail
    if depth:
        doc = LOCAL_URL.sub(r"\1" + "../" * depth, doc)
    return doc


def meta_tags(title: str, description: str, url: str, image: str, ld: dict) -> str:
    e = html.escape
    return (
        f"  <title>{e(title)}</title>\n"
        f'  <meta name="description" content="{e(description)}" />\n'
        f'  <link rel="canonical" href="{url}" />\n'
        f'  <meta property="og:type" content="article" />\n'
        f'  <meta property="og:title" content="{e(title)}" />\n'
        f'  <meta property="og:description" content="{e(description)}" />\n'
        f'  <meta property="og:url" content="{url}" />\n'
        f'  <meta property="og:image" content="{SITE}/assets/{image}" />\n'
        f'  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n'
    )


def card(post: dict, prefix: str) -> str:
    return f"""          <article class="blog-card">
            <a class="blog-card-link" href="{prefix}insights/{post['slug']}.html">
              <img src="{prefix}assets/{post['image']}?v=2" alt="{html.escape(post['image_alt'])}" width="1152" height="864" loading="lazy" />
              <div class="blog-card-body">
                <p class="blog-meta"><span>{post['category']}</span> · {post['read']} min read</p>
                <h2>{html.escape(post['title'])}</h2>
                <p>{html.escape(post['lead'])}</p>
                <span class="blog-card-more">Read article →</span>
              </div>
            </a>
          </article>"""


def build_index(head: str, tail: str) -> None:
    title = "Insights | Home Buying in Anantapur — MSS Builders"
    description = "Guides for home buyers in Anantapur: 2 BHK and duplex houses, gated communities, Vastu and house facing, and living on Kalyandurgam Road."
    url = f"{SITE}/insights.html"
    ld = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "MSS Builders Insights",
        "url": url,
        "publisher": {"@type": "Organization", "name": "MSS Builders"},
        "blogPost": [
            {"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/insights/{p['slug']}.html"}
            for p in POSTS
        ],
    }
    cards = "\n".join(card(p, "") for p in POSTS)
    main = f"""
    <section class="page-hero">
      <div class="wrap page-hero-inner">
        <p class="eyebrow">Insights</p>
        <h1>Home buying in Anantapur, made simple.</h1>
        <p class="page-hero-lead">Practical guides for families buying a house in <strong>Anantapur, Andhra Pradesh</strong> — from 2 BHK and duplex homes to gated communities, Vastu and the neighbourhood.</p>
      </div>
    </section>

    <section class="blog-section">
      <div class="wrap">
        <div class="blog-grid">
{cards}
        </div>
      </div>
    </section>
"""
    meta = meta_tags(title, description, url, POSTS[0]["image"], ld).replace('content="article"', 'content="website"')
    (ROOT / "insights.html").write_text(page(head, tail, meta, main, 0))
    print("insights.html")


def build_post(head: str, tail: str, post: dict) -> None:
    url = f"{SITE}/insights/{post['slug']}.html"
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting",
                "headline": post["title"],
                "description": post["meta"],
                "image": f"{SITE}/assets/{post['image']}",
                "datePublished": PUBLISHED,
                "dateModified": PUBLISHED,
                "author": {"@type": "Organization", "name": "MSS Builders"},
                "publisher": {"@type": "Organization", "name": "MSS Builders",
                              "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/mss-builders-logo.png"}},
                "mainEntityOfPage": url,
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in post["faq"]
                ],
            },
        ],
    }
    faq = "\n".join(
        f"            <details{' open' if i == 0 else ''}>\n"
        f"              <summary>{html.escape(q)}</summary>\n"
        f"              <p>{html.escape(a)}</p>\n"
        f"            </details>"
        for i, (q, a) in enumerate(post["faq"])
    )
    related = "\n".join(
        f'            <li><a href="insights/{p["slug"]}.html"><span>{p["category"]}</span>{html.escape(p["title"])}</a></li>'
        for p in POSTS if p is not post
    )
    body = post["body"].replace("{root}", "").strip()
    main = f"""
    <section class="post-hero">
      <div class="wrap post-wrap">
        <nav class="post-crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a> / <a href="insights.html">Insights</a> / <span>{post['category']}</span></nav>
        <h1>{html.escape(post['title'])}</h1>
        <p class="post-lead">{html.escape(post['lead'])}</p>
        <p class="blog-meta post-meta"><span>{post['category']}</span> · {post['read']} min read · {PUBLISHED_LABEL}</p>
      </div>
    </section>

    <article class="post">
      <div class="wrap post-wrap">
        <figure class="post-cover">
          <img src="assets/{post['image']}?v=2" alt="{html.escape(post['image_alt'])}" width="1152" height="864" />
          <span class="img-rights">© All rights reserved</span>
        </figure>

        <div class="post-body">
{body}
        </div>

        <aside class="post-cta">
          <div>
            <h2>See MSS Balaji Grandeur in person</h2>
            <p>2 BHK homes from ₹64 Lakhs and duplex homes from ₹81 Lakhs in Anantapur — prices negotiable.</p>
          </div>
          <div class="post-cta-actions">
            <a class="btn btn-accent" href="#" data-open-quote data-quote-type="booking">Book a site visit</a>
            <a class="btn btn-outline" href="tel:+919297975656">Call 92979 75656</a>
          </div>
        </aside>

        <section class="post-faq">
          <h2>Frequently asked questions</h2>
          <div class="apc-faq-list" data-faq>
{faq}
          </div>
        </section>

        <nav class="post-related" aria-label="More insights">
          <h2>More insights</h2>
          <ul>
{related}
          </ul>
        </nav>
      </div>
    </article>
"""
    meta = meta_tags(f"{post['title']} | MSS Builders", post["meta"], url, post["image"], ld)
    doc = page(head, tail, meta, main, 1)
    out = ROOT / "insights" / f"{post['slug']}.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(doc)
    print(out.relative_to(ROOT))


def main() -> None:
    head, tail = chrome()
    build_index(head, tail)
    for post in POSTS:
        build_post(head, tail, post)


if __name__ == "__main__":
    main()
