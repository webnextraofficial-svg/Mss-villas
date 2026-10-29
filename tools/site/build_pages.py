"""Build careers.html from the shared header and footer in contact.html.

Run after any header/footer change in contact.html:
    python3 tools/site/build_pages.py
"""
import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
SITE = ROOT / "public_html"
TEMPLATE = SITE / "contact.html"


def esc(text):
    return html.escape(text, quote=True)


def set_active(page, href):
    """Mark `href` as the current page in the primary nav and footer quick links."""
    page = page.replace(' class="is-active" aria-current="page"', "")
    page = page.replace(' aria-current="page"', "")
    if href:
        page = page.replace(
            f'<li><a href="{href}"><svg class="nav-icon"',
            f'<li><a href="{href}" class="is-active" aria-current="page"><svg class="nav-icon"',
            1,
        )
        page = re.sub(
            rf'(<ul class="pg-footer-links">(?:(?!</ul>).)*?<li><a href="{re.escape(href)}")',
            r'\1 aria-current="page"',
            page,
            count=1,
            flags=re.S,
        )
    return page



def render(template, *, title, description, body_class, main, active):
    page = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", template, count=1, flags=re.S)
    page = re.sub(
        r'<meta name="description" content="[^"]*" />',
        f'<meta name="description" content="{esc(description)}" />',
        page,
        count=1,
    )
    page = page.replace('<body class="page-contact page-ap">', f'<body class="{body_class} page-ap">', 1)
    page = re.sub(r"<main id=\"main\">.*?</main>", lambda _: f'<main id="main">\n{main}\n  </main>', page, count=1, flags=re.S)
    return set_active(page, active)


CAREERS_MAIN = """
    <section class="page-hero">
      <div class="wrap page-hero-inner">
        <p class="eyebrow">Careers</p>
        <h1>We’re hiring at MSS Builders</h1>
        <p class="page-hero-lead">Join the team behind MSS <span class="mss-balaji">Balaji</span> <span class="mss-script">Grandeur</span> in <strong>Anantapur, Andhra Pradesh</strong>. We’re looking for Channel Partners and Tele Callers.</p>
      </div>
    </section>

    <section class="contact">
      <div class="wrap contact-grid">
        <div class="contact-copy">
          <ul class="career-roles">
            <li class="career-role" id="channel-partner">
              <div class="career-role-head">
                <span class="career-role-icon"><i class="fa-solid fa-handshake" aria-hidden="true"></i></span>
                <div>
                  <h2>Channel Partner</h2>
                  <p class="career-role-type">Partnership · Anantapur</p>
                </div>
              </div>
              <p>Work with MSS Builders to connect homebuyers with MSS Balaji Grandeur — 2 BHK homes (₹64 Lakhs) and duplex homes (₹81 Lakhs) in a gated community.</p>
              <ul>
                <li>Real estate agents, brokers and consultants</li>
                <li>People with a strong local network in and around Anantapur</li>
                <li>Bring buyers for site visits and help them through the booking</li>
              </ul>
              <a class="btn btn-accent career-apply-btn" href="#careers-form" data-role="Channel Partner">Apply as Channel Partner</a>
            </li>
            <li class="career-role" id="tele-caller">
              <div class="career-role-head">
                <span class="career-role-icon"><i class="fa-solid fa-headset" aria-hidden="true"></i></span>
                <div>
                  <h2>Tele Caller</h2>
                  <p class="career-role-type">Sales support · Anantapur</p>
                </div>
              </div>
              <p>Call and follow up with homebuyer enquiries, share project details and schedule site visits to MSS Balaji Grandeur.</p>
              <ul>
                <li>Clear, polite communication on the phone</li>
                <li>Comfortable following up with leads every day</li>
                <li>Freshers and experienced candidates can apply</li>
              </ul>
              <a class="btn btn-accent career-apply-btn" href="#careers-form" data-role="Tele Caller">Apply as Tele Caller</a>
            </li>
          </ul>
        </div>

        <div class="contact-map">
          <form class="quote-form contact-form-card" id="careers-form" action="#" method="post" data-lead-form data-service="Careers application">
            <div class="contact-form-head">
              <p class="contact-form-eyebrow">Apply now</p>
              <h3>Join the MSS Builders team</h3>
              <p class="contact-form-lead">Share your details — our team will call you to discuss the role.</p>
            </div>

            <div class="form-row">
              <label>Name<input type="text" name="name" placeholder="Your full name" autocomplete="name" required /></label>
              <label>Phone<input type="tel" name="phone" placeholder="+91 XXXXX XXXXX" autocomplete="tel" required /></label>
            </div>
            <label>City / area<input type="text" name="address" placeholder="e.g. Anantapur" required /></label>
            <div class="form-row">
              <label>
                Applying for
                <select name="need" required>
                  <option value="">Select a role…</option>
                  <option>Channel Partner</option>
                  <option>Tele Caller</option>
                </select>
              </label>
              <label>
                Experience
                <select name="experience" required>
                  <option value="">Select…</option>
                  <option>Fresher</option>
                  <option>Less than 1 year</option>
                  <option>1–3 years</option>
                  <option>3+ years</option>
                </select>
              </label>
            </div>
            <label>About you<textarea name="message" rows="3" placeholder="Your current work, languages you speak, or your real estate network"></textarea></label>

            <label class="contact-wa-check">
              <input type="checkbox" name="whatsapp" checked />
              <span>Contact me on WhatsApp</span>
            </label>

            <button class="btn btn-accent btn-lg contact-submit" type="submit">Apply Now</button>
            <p class="form-hint" data-lead-status role="status" aria-live="polite">Prefer to talk? Call <a href="tel:+917337575162">73375 75162</a>.</p>
          </form>
        </div>
      </div>
    </section>
"""



def main():
    template = TEMPLATE.read_text()

    (SITE / "careers.html").write_text(render(
        template,
        title="Careers | Channel Partner & Tele Caller Jobs — MSS Builders, Anantapur",
        description="MSS Builders is hiring Channel Partners and Tele Callers in Anantapur for MSS Balaji Grandeur. Apply online or call 73375 75162.",
        body_class="page-contact page-careers",
        main=CAREERS_MAIN,
        active="careers.html",
    ))
    print("careers.html")


if __name__ == "__main__":
    main()
