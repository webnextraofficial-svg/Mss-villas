import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent / "public_html"
TEMPLATE = ROOT / "blog" / "ac-not-cooling-properly.html"
DATE = "2026-10-15"
DATE_LABEL = "15 Oct 2026"
EMAIL = "info@gharupgrade.com"
ADDRESS_LINES = ["2nd Floor, Survey No 34,", "Kothaguda Junction, Kondapur,", "Hyderabad, Telangana 500084"]
MAP_QUERY = "Kothaguda+Junction+Kondapur+Hyderabad+Telangana+500084"
FA_LINK = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />'

AREAS = [
    {
        "slug": "kukatpally",
        "name": "Kukatpally &amp; KPHB",
        "short": "Kukatpally",
        "image": "service-painting.jpg",
        "lead": "Our office at Kothaguda Junction, Kondapur is a short drive away — so Kukatpally homes get quick site visits and follow-ups.",
        "about": "Kukatpally and KPHB are full of 10–25 year old apartments and independent houses. The most common jobs we see here are repainting tired walls, fixing terrace and bathroom leaks before the monsoon, and refreshing interiors for families moving in.",
        "problems": [
            ("Damp walls after the monsoon", "older KPHB buildings often have cracked terraces and failed bathroom joints that push water into bedroom walls."),
            ("Faded exterior paint", "west-facing walls take harsh afternoon sun and start chalking within a few years."),
            ("Weak AC cooling in summer", "top-floor flats need a pre-summer deep service to keep up in April and May."),
        ],
        "nearby": "KPHB Colony, JNTU, Vivekananda Nagar, Moosapet, Balanagar and Allwyn Colony",
    },
    {
        "slug": "secunderabad",
        "name": "Secunderabad",
        "short": "Secunderabad",
        "image": "wp-terrace.jpg",
        "lead": "Painting, waterproofing, interiors and AC service for independent houses and apartments across Secunderabad.",
        "about": "Secunderabad has many older independent houses and bungalows alongside newer apartments. Flat RCC roofs, lime-plastered walls and decades of repainting mean the job usually starts with proper surface repair, not just a fresh coat.",
        "problems": [
            ("Terrace leakage in old houses", "aged roofs develop hairline cracks and need a full waterproofing system, not patchwork."),
            ("Peeling layers of old paint", "multiple past coats lose grip and need scraping, putty and primer before repainting."),
            ("Outdated kitchens and wardrobes", "older homes benefit most from modular kitchen and storage upgrades."),
        ],
        "nearby": "Marredpally, Tirumalgherry, Alwal, Bowenpally, Trimulgherry and Sainikpuri",
    },
    {
        "slug": "shamirpet",
        "name": "Shamirpet",
        "short": "Shamirpet",
        "image": "painting-exterior.jpg",
        "lead": "Exterior painting, terrace waterproofing and interiors for villas and gated communities in Shamirpet.",
        "about": "Shamirpet is home to villas, gated communities and weekend homes in open surroundings. Exposed walls face strong sun, wind and rain, so exterior coatings and roof waterproofing need to be chosen for durability.",
        "problems": [
            ("Exterior walls fading fast", "open plots get full-day sun — weather-resistant exterior emulsions last much longer."),
            ("Leaking terraces and sunshades", "large villa roofs need seamless waterproofing with proper slope and drainage."),
            ("Furnishing a new villa", "full-home interiors, from wardrobes to lighting, planned in one package."),
        ],
        "nearby": "Shamirpet Lake, Turkapally, Thumkunta, Medchal and Genome Valley",
    },
    {
        "slug": "miyapur",
        "name": "Miyapur",
        "short": "Miyapur",
        "image": "service-ac-service.jpg",
        "lead": "Fast painting, waterproofing and AC service for apartments and independent homes in Miyapur.",
        "about": "Miyapur has grown with large gated apartments and rental flats. Owners usually want quick, clean turnarounds — repainting between tenants, fixing bathroom leaks and keeping ACs serviced before summer.",
        "problems": [
            ("Repainting between tenants", "quick 2BHK and 3BHK repaints with minimal downtime."),
            ("Bathroom and balcony leaks", "tile joint gaps let water seep into the flat below — epoxy grouting fixes it."),
            ("AC servicing before summer", "deep cleaning and gas checks to avoid breakdowns in peak heat."),
        ],
        "nearby": "Madinaguda, Hafeezpet, Chandanagar, Bachupally and Allwyn Colony",
    },
    {
        "slug": "nizampet",
        "name": "Nizampet",
        "short": "Nizampet",
        "image": "id-full-home.jpg",
        "lead": "Interiors, painting and waterproofing for new apartments and independent houses in Nizampet.",
        "about": "Nizampet has many newly built apartments where families are moving in for the first time. That means full-home interiors, first-time painting touch-ups and early waterproofing to protect the new home.",
        "problems": [
            ("Setting up a new flat", "modular kitchens, wardrobes and TV units designed for compact rooms."),
            ("Hairline cracks in new walls", "settlement cracks need filling and putty before the first repaint."),
            ("Early seepage in bathrooms", "fixing waterproofing early avoids damage to new interiors."),
        ],
        "nearby": "Bachupally, Pragathi Nagar, Pragathi Enclave and JNTU",
    },
    {
        "slug": "gachibowli",
        "name": "Gachibowli",
        "short": "Gachibowli",
        "image": "id-kitchen.jpg",
        "lead": "Premium interiors, painting and AC service for apartments and villas in Gachibowli.",
        "about": "Gachibowli’s high-rise apartments and villas often need premium finishes — designer paints, modular kitchens and well-maintained split and VRF air conditioning for work-from-home comfort.",
        "problems": [
            ("Premium interior upgrades", "modular kitchens, wardrobes and decor with a clean modern finish."),
            ("Designer and texture paints", "feature walls and low-VOC paints for occupied homes."),
            ("Multi-AC maintenance", "regular servicing for split, cassette and VRF systems."),
        ],
        "nearby": "Kondapur, Madhapur, Nanakramguda, Financial District and Lingampally",
    },
]


def area_href(slug):
    return f"blog/home-services-in-{slug}.html"


def footer_grid(prefix, current):
    def link(href, icon, label, extra=""):
        cur = ' aria-current="page"' if href == current else ""
        return f'<li><a href="{prefix}{href}"{cur}{extra}><i class="{icon}" aria-hidden="true"></i>{label}</a></li>'

    services = [
        ("services/painting.html", "fa-solid fa-paint-roller", "Painting"),
        ("services/waterproofing-solutions.html", "fa-solid fa-umbrella", "Waterproofing"),
        ("services/interior-design-solutions.html", "fa-solid fa-couch", "Interior Design"),
        ("services/ac-works.html", "fa-solid fa-snowflake", "AC Service"),
    ]
    company = [
        ("why-choose.html", "fa-solid fa-circle-info", "About Us"),
        ("contact.html", "fa-solid fa-headset", "Contact"),
        ("partner.html", "fa-solid fa-handshake", "Become a partner"),
        ("blog.html", "fa-solid fa-newspaper", "Blog"),
        ("index.html#faq", "fa-solid fa-circle-question", "FAQs"),
    ]
    L = "\n          "
    services_html = L.join(link(h, i, t) for h, i, t in services)
    areas_html = L.join(link(area_href(a["slug"]), "fa-solid fa-location-dot", a["short"]) for a in AREAS)
    company_html = L.join(link(h, i, t) for h, i, t in company)
    address_html = "<br />".join(ADDRESS_LINES)

    return f'''<div class="wrap ap-footer-grid">
      <div class="footer-brand">
        <a class="brand" href="{prefix}index.html"><img class="brand-logo" src="{prefix}assets/ghar-upgrade-logo.png?v=3" alt="GharUpgrade" width="180" height="37" /></a>
        <p class="footer-tagline">DESIGN. BUILD. ELEVATE.</p>
        <p class="footer-area">Painting, waterproofing, interior design and AC services in Hyderabad.</p>
        <address class="footer-address"><i class="fa-solid fa-location-dot" aria-hidden="true"></i><span>{address_html}</span></address>
        <div class="footer-map">
          <iframe title="Ghar Upgrade location — Kothaguda Junction, Kondapur" src="https://maps.google.com/maps?q={MAP_QUERY}&amp;z=15&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
        </div>
      </div>
      <nav class="footer-col" aria-label="Services">
        <h2 class="footer-title">Services</h2>
        <ul class="footer-links">
          {services_html}
        </ul>
      </nav>
      <nav class="footer-col" aria-label="Areas we serve">
        <h2 class="footer-title">Areas we serve</h2>
        <ul class="footer-links">
          {areas_html}
        </ul>
      </nav>
      <nav class="footer-col" aria-label="Company">
        <h2 class="footer-title">Company</h2>
        <ul class="footer-links">
          {company_html}
        </ul>
      </nav>
      <div class="footer-col">
        <h2 class="footer-title">Get in touch</h2>
        <ul class="footer-links">
          <li><a href="tel:+916302660352"><i class="fa-solid fa-phone" aria-hidden="true"></i>+91 63026 60352</a></li>
          <li><a href="mailto:{EMAIL}"><i class="fa-solid fa-envelope" aria-hidden="true"></i>{EMAIL}</a></li>
          <li><a href="https://wa.me/916302660352" target="_blank" rel="noopener"><i class="fa-brands fa-whatsapp" aria-hidden="true"></i>WhatsApp</a></li>
          <li><a href="https://www.google.com/maps/search/?api=1&amp;query={MAP_QUERY}" target="_blank" rel="noopener"><i class="fa-solid fa-diamond-turn-right" aria-hidden="true"></i>Get directions</a></li>        </ul>
'''


def update_footer(path):
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()
    prefix = "../" if "/" in rel else ""
    start = text.find('<div class="wrap ap-footer-grid">')
    bottom = text.find('<div class="footer-bottom">', start)
    if start == -1 or bottom == -1:
        print("skip (no footer):", rel)
        return
    social = text.find('<ul class="social-list">', start, bottom)
    current = "blog.html" if rel.startswith("blog/") and not rel.startswith("blog/home-services-in-") else rel
    if social != -1:
        rest = "        " + text[social:]
    else:
        rest = "      </div>\n    </div>\n    " + text[bottom:]
    text = text[:start] + footer_grid(prefix, current) + rest

    if "font-awesome" not in text:
        text = text.replace("</head>", f"  {FA_LINK}\n</head>", 1)
    text = text.replace("home-upgrade.css?v=ap-clone-30", "home-upgrade.css?v=ap-clone-31")
    path.write_text(text, encoding="utf-8")
    print("updated:", rel)


def build_area_page(area, template):
    slug, name, short = area["slug"], area["name"], area["short"]
    url = f"https://gharupgrade.com/{area_href(slug)}"
    plain_name = html.unescape(name)
    title = f"Home Services in {plain_name}, Hyderabad | Ghar Upgrade"
    h1 = f"Painting, Waterproofing, Interiors &amp; AC Service in {name}"
    plain_h1 = html.unescape(h1)
    desc = f"Ghar Upgrade serves homes in {plain_name}, Hyderabad — house painting, waterproofing, interior design and AC service with free site visits and itemised quotes."
    faqs = [
        (f"Do you offer free site visits in {plain_name}?", f"Yes. Our team visits homes in {plain_name} and nearby areas to inspect and share an itemised quote at no cost."),
        (f"How soon can you start work in {plain_name}?", "Most painting, waterproofing and AC jobs can start within 2–5 days of confirming the quote. Interior projects are scheduled after design sign-off."),
    ]

    t = template
    head_end = t.index("</head>")
    head = t[:head_end]
    head = re.sub(r'<meta name="description" content="[^"]*" />', f'<meta name="description" content="{html.escape(desc)}" />', head)
    head = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", head)
    head = re.sub(r'<link rel="canonical" href="[^"]*" />', f'<link rel="canonical" href="{url}" />', head)
    head = re.sub(r'<meta property="og:title" content="[^"]*" />', f'<meta property="og:title" content="{html.escape(title)}" />', head)
    head = re.sub(r'<meta property="og:description" content="[^"]*" />', f'<meta property="og:description" content="{html.escape(desc)}" />', head)
    head = re.sub(r'<meta property="og:url" content="[^"]*" />', f'<meta property="og:url" content="{url}" />', head)
    head = re.sub(r'<meta property="og:image" content="[^"]*" />', f'<meta property="og:image" content="https://gharupgrade.com/assets/{area["image"]}" />', head)
    head = re.sub(r'  <script type="application/ld\+json">.*?</script>\n', "", head, flags=re.S)
    ld = [
        {"@context": "https://schema.org", "@type": "BlogPosting", "headline": plain_h1, "description": desc,
         "image": f"https://gharupgrade.com/assets/{area['image']}", "datePublished": DATE, "dateModified": DATE,
         "author": {"@type": "Organization", "name": "Ghar Upgrade"},
         "publisher": {"@type": "Organization", "name": "Ghar Upgrade", "logo": {"@type": "ImageObject", "url": "https://gharupgrade.com/assets/ghar-upgrade-logo.png"}},
         "mainEntityOfPage": url, "keywords": f"home services {plain_name}, painting {plain_name}, waterproofing {plain_name}"},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://gharupgrade.com/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://gharupgrade.com/blog.html"},
            {"@type": "ListItem", "position": 3, "name": plain_h1, "item": url}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
    ]
    head += "".join(f'  <script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)

    problems = "\n".join(f"<li><strong>{p}:</strong> {d}</li>" for p, d in area["problems"])
    faq_html = "\n".join(f'''          <details>
            <summary>{html.escape(q)}</summary>
            <p>{html.escape(a)}</p>
          </details>''' for q, a in faqs)
    related = "\n".join(
        f'          <li><a href="home-services-in-{o["slug"]}.html"><span>Local Service</span>Home services in {o["name"]}</a></li>'
        for o in AREAS if o["slug"] != slug
    )

    main = f'''  <main id="main">

    <section class="post-hero">
      <div class="wrap post-wrap">
        <nav class="post-crumbs" aria-label="Breadcrumb">
          <a href="../index.html">Home</a> <span aria-hidden="true">›</span>
          <a href="../blog.html">Blog</a> <span aria-hidden="true">›</span>
          <a href="../blog.html#areas">Areas we serve</a>
        </nav>
        <p class="blog-meta"><span>Local Service</span> · <time datetime="{DATE}">{DATE_LABEL}</time> · 3 min read</p>
        <h1>{h1}</h1>
        <p class="post-lead">{area["lead"]}</p>
      </div>
    </section>

    <article class="post">
      <div class="wrap post-wrap">
        <figure class="post-cover">
          <img src="../assets/{area["image"]}" alt="Home services in {name}" width="1024" height="640" />
          <span class="img-rights">© All rights reserved</span>
        </figure>

        <div class="post-body">
        <h2>Homes we serve in {name}</h2>
<p>{area["about"]}</p>
        <h2>Our services in {name}</h2>
<ul>
<li><strong><a href="../services/painting.html">House painting</a>:</strong> interior and exterior painting, putty, texture and waterproof exterior coatings.</li>
<li><strong><a href="../services/waterproofing-solutions.html">Waterproofing</a>:</strong> terrace, bathroom, balcony, wall dampness and tank waterproofing.</li>
<li><strong><a href="../services/interior-design-solutions.html">Interior design</a>:</strong> modular kitchens, wardrobes, TV units, puja units and full-home interiors.</li>
<li><strong><a href="../services/ac-works.html">AC service</a>:</strong> deep cleaning, gas refilling, repairs and installation for split, window, cassette and VRF systems.</li>
</ul>
        <h2>Common home problems we fix in {name}</h2>
<ul>
{problems}
</ul>
        <h2>Nearby localities</h2>
<p>We also cover {area["nearby"]}. Our office is at Kothaguda Junction, Kondapur — call <a href="tel:+916302660352">+91 63026 60352</a> or email <a href="mailto:{EMAIL}">{EMAIL}</a> to book a visit.</p>
        </div>

        <aside class="post-cta">
          <div>
            <h2>Book a free site visit in {name}</h2>
            <p>Our team inspects your home and shares a clear, itemised quote.</p>
          </div>
          <div class="post-cta-actions">
            <a class="btn btn-accent" href="#" data-open-quote>Book a site visit</a>
            <a class="btn btn-outline" href="../contact.html">Contact us</a>
          </div>
        </aside>

        <section class="post-faq" aria-labelledby="post-faq-title">
          <h2 id="post-faq-title">Frequently asked questions</h2>
          <div class="bh-faq" data-faq>
{faq_html}
          </div>
        </section>

        <section class="post-related" aria-labelledby="post-related-title">
          <h2 id="post-related-title">Other areas we serve</h2>
          <ul>
{related}
          </ul>
        </section>
      </div>
    </article>

  </main>'''

    body = t[head_end:]
    body = re.sub(r"  <main id=\"main\">.*?</main>", lambda _: main, body, flags=re.S)
    return head + body


def update_blog_index():
    path = ROOT / "blog.html"
    text = path.read_text(encoding="utf-8")
    if 'id="areas"' in text:
        return
    text = text.replace(
        '<a href="#ac">AC Service</a>\n',
        '<a href="#ac">AC Service</a>\n          <a href="#areas">Areas we serve</a>\n', 1)
    cards = "\n".join(f'''          <article class="blog-card">
            <a class="blog-card-link" href="{area_href(a["slug"])}">
              <img src="assets/{a["image"]}" alt="Home services in {a["name"]}" width="800" height="500" loading="lazy" />
              <div class="blog-card-body">
                <p class="blog-meta"><span>Local Service</span> · <time datetime="{DATE}">{DATE_LABEL}</time></p>
                <h3>Home services in {a["name"]}</h3>
                <p>{a["lead"]}</p>
                <span class="blog-card-more">Read article →</span>
              </div>
            </a>
          </article>''' for a in AREAS)
    section = f'''    <section class="blog-section blog-cluster" id="areas">
      <div class="wrap">
        <header class="blog-cluster-head">
          <div>
            <h2>Areas we serve</h2>
            <p>Local guides for the Hyderabad neighbourhoods where we paint, waterproof, design and service homes.</p>
          </div>
          <a class="apc-link" href="contact.html">Contact us →</a>
        </header>
        <div class="blog-grid">
{cards}
        </div>
      </div>
    </section>

  </main>'''
    text = text.replace("\n  </main>", "\n" + section, 1)
    path.write_text(text, encoding="utf-8")
    print("updated: blog.html (areas section)")


def update_sitemap():
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    entries = ""
    for a in AREAS:
        loc = f"https://gharupgrade.com/{area_href(a['slug'])}"
        if loc in text:
            continue
        entries += f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n"
    if entries:
        text = text.replace("</urlset>", entries + "</urlset>")
        path.write_text(text, encoding="utf-8")
        print("updated: sitemap.xml")


def main():
    template = TEMPLATE.read_text(encoding="utf-8")
    for area in AREAS:
        out = ROOT / area_href(area["slug"])
        out.write_text(build_area_page(area, template), encoding="utf-8")
        print("created:", out.relative_to(ROOT))
    update_blog_index()
    update_sitemap()
    for path in sorted(ROOT.rglob("*.html")):
        update_footer(path)


if __name__ == "__main__":
    main()
