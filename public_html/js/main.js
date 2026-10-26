(function () {
  "use strict";

  var year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  var toggle = document.querySelector(".nav-toggle");
  var closeBtn = document.querySelector(".nav-close");
  var backdrop = document.getElementById("nav-backdrop");
  var nav = document.getElementById("site-nav");

  function setNavOpen(open) {
    if (!toggle || !nav) return;
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    nav.classList.toggle("is-open", open);
    document.body.classList.toggle("nav-open", open);
    if (backdrop) {
      if (open) backdrop.removeAttribute("hidden");
      else backdrop.setAttribute("hidden", "");
    }
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      setNavOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      setNavOpen(false);
    });
  }

  if (backdrop) {
    backdrop.addEventListener("click", function () {
      setNavOpen(false);
    });
  }

  if (nav) {
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setNavOpen(false);
        closeAllSubmenus();
      });
    });
  }

  function closeAllSubmenus() {
    document.querySelectorAll(".nav-item.has-submenu").forEach(function (item) {
      item.classList.remove("is-open");
      var btn = item.querySelector(".nav-submenu-toggle");
      if (btn) btn.setAttribute("aria-expanded", "false");
    });
  }

  document.querySelectorAll(".nav-submenu-toggle").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      var item = btn.closest(".nav-item.has-submenu");
      if (!item) return;
      var willOpen = !item.classList.contains("is-open");
      closeAllSubmenus();
      if (willOpen) {
        item.classList.add("is-open");
        btn.setAttribute("aria-expanded", "true");
      }
    });
  });

  document.addEventListener("click", function (e) {
    if (!e.target.closest(".nav-item.has-submenu")) closeAllSubmenus();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      setNavOpen(false);
      closeAllSubmenus();
    }
  });

  /* Hero slider */
  var slides = Array.prototype.slice.call(document.querySelectorAll(".hero-slide"));
  var dots = Array.prototype.slice.call(document.querySelectorAll(".hero-dot"));
  var index = 0;
  var timer = null;

  function goTo(i) {
    if (!slides.length) return;
    index = (i + slides.length) % slides.length;
    slides.forEach(function (slide, n) {
      slide.classList.toggle("is-active", n === index);
    });
    dots.forEach(function (dot, n) {
      dot.classList.toggle("is-active", n === index);
    });
  }

  function next() {
    goTo(index + 1);
  }

  function startAuto() {
    stopAuto();
    if (slides.length < 2) return;
    timer = window.setInterval(next, 6000);
  }

  function stopAuto() {
    if (timer) window.clearInterval(timer);
    timer = null;
  }

  dots.forEach(function (dot) {
    dot.addEventListener("click", function () {
      goTo(Number(dot.getAttribute("data-slide-to")));
      startAuto();
    });
  });

  var slider = document.querySelector("[data-slider]");
  if (slider) {
    slider.addEventListener("mouseenter", stopAuto);
    slider.addEventListener("mouseleave", startAuto);

    var touchStartX = 0;
    slider.addEventListener(
      "touchstart",
      function (e) {
        touchStartX = e.changedTouches[0].screenX;
        stopAuto();
      },
      { passive: true }
    );
    slider.addEventListener(
      "touchend",
      function (e) {
        var dx = e.changedTouches[0].screenX - touchStartX;
        if (Math.abs(dx) > 40) goTo(index + (dx < 0 ? 1 : -1));
        startAuto();
      },
      { passive: true }
    );
  }

  goTo(0);
  startAuto();

  /* Homepage hero slideshow */
  document.querySelectorAll("[data-gu-slider]").forEach(function (slider) {
    var slides = Array.prototype.slice.call(
      slider.querySelectorAll(".gu-hero-pro-slide, .gu-banner-slide, .gu-slide, .apc-hero-slide")
    );
    if (slides.length < 2) return;

    var dots = Array.prototype.slice.call(slider.querySelectorAll(".gu-dot"));
    var strips = Array.prototype.slice.call(slider.querySelectorAll(".gu-strip"));
    var prev = slider.querySelector("[data-gu-prev]");
    var nextBtn = slider.querySelector("[data-gu-next]");
    var progress = slider.querySelector(".gu-hero-progress > span");
    var i = 0;
    var t = null;
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function restartProgress() {
      if (!progress) return;
      slider.classList.remove("is-playing");
      void progress.offsetWidth;
      if (!reduced) slider.classList.add("is-playing");
    }

    function show(n) {
      i = (n + slides.length) % slides.length;
      slides.forEach(function (slide, idx) {
        slide.classList.toggle("is-active", idx === i);
      });
      dots.forEach(function (dot, idx) {
        dot.classList.toggle("is-active", idx === i);
      });
      strips.forEach(function (strip, idx) {
        strip.classList.toggle("is-active", idx === i);
      });
      restartProgress();
    }

    function play() {
      stop();
      if (reduced) return;
      restartProgress();
      t = window.setInterval(function () {
        show(i + 1);
      }, 5000);
    }

    function stop() {
      if (t) window.clearInterval(t);
      t = null;
      slider.classList.remove("is-playing");
    }

    dots.forEach(function (dot) {
      dot.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        show(Number(dot.getAttribute("data-gu-to")));
        play();
      });
    });

    strips.forEach(function (strip, idx) {
      strip.style.pointerEvents = "auto";
      strip.style.cursor = "pointer";
      strip.addEventListener("click", function () {
        show(idx);
        play();
      });
    });

    if (prev) {
      prev.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        show(i - 1);
        play();
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        show(i + 1);
        play();
      });
    }

    slider.addEventListener("mouseenter", stop);
    slider.addEventListener("mouseleave", play);

    var touchX = 0;
    slider.addEventListener(
      "touchstart",
      function (e) {
        touchX = e.changedTouches[0].screenX;
        stop();
      },
      { passive: true }
    );
    slider.addEventListener(
      "touchend",
      function (e) {
        var dx = e.changedTouches[0].screenX - touchX;
        if (Math.abs(dx) > 40) show(i + (dx < 0 ? 1 : -1));
        play();
      },
      { passive: true }
    );

    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stop();
      else play();
    });

    show(0);
    play();
  });

  /* Sticky header scrolled state */
  var siteHeader = document.getElementById("site-header");
  if (siteHeader) {
    var onScrollHeader = function () {
      siteHeader.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    onScrollHeader();
    window.addEventListener("scroll", onScrollHeader, { passive: true });
  }

  /* Scroll reveal */
  var revealEls = document.querySelectorAll(".gu-reveal");
  if (revealEls.length && "IntersectionObserver" in window) {
    var revealObs = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-in");
            revealObs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    revealEls.forEach(function (el) {
      revealObs.observe(el);
    });
  } else {
    revealEls.forEach(function (el) {
      el.classList.add("is-in");
    });
  }

  /* Journey: reveal steps one by one, then auto-highlight each step in turn */
  var journey = document.querySelector(".bh-journey");
  if (journey && "IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var steps = journey.querySelectorAll("li");
    var stepIndex = -1;
    var stepTimer = null;
    var paused = false;

    var showStep = function (i) {
      steps.forEach(function (li, n) {
        li.classList.toggle("is-active", n === i);
      });
      stepIndex = i;
    };

    var startCycle = function () {
      clearInterval(stepTimer);
      stepTimer = setInterval(function () {
        if (!paused) showStep((stepIndex + 1) % steps.length);
      }, 2200);
    };

    journey.classList.add("is-flow");
    var journeyObs = new IntersectionObserver(
      function (entries) {
        if (!entries[0].isIntersecting) return;
        journeyObs.disconnect();
        steps.forEach(function (li, n) {
          setTimeout(function () {
            li.classList.add("is-shown");
            showStep(n);
            if (n === steps.length - 1) startCycle();
          }, n * 450);
        });
      },
      { threshold: 0.25 }
    );
    journeyObs.observe(journey);

    journey.addEventListener("mouseenter", function () { paused = true; });
    journey.addEventListener("mouseleave", function () { paused = false; });
    steps.forEach(function (li, n) {
      li.addEventListener("mouseenter", function () {
        if (li.classList.contains("is-shown")) showStep(n);
      });
    });
  }

  /* Reviews train: duplicate cards so the row loops seamlessly */
  if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    document.querySelectorAll(".bh-reviews-marquee").forEach(function (marquee) {
      var list = marquee.querySelector(".bh-reviews");
      if (!list || marquee.classList.contains("is-train")) return;
      var cards = Array.prototype.slice.call(list.children);
      cards.forEach(function (card) {
        var clone = card.cloneNode(true);
        clone.setAttribute("aria-hidden", "true");
        list.appendChild(clone);
      });
      marquee.style.setProperty("--train-duration", cards.length * 7 + "s");
      marquee.classList.add("is-train");
    });
  }

  /* Soft hero parallax on pointer move */
  var heroPro = document.querySelector(".gu-hero-pro");
  if (heroPro && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var frame = heroPro.querySelector(".gu-hero-pro-slide.is-active .gu-hero-visual-frame");
    heroPro.addEventListener(
      "pointermove",
      function (e) {
        var rect = heroPro.getBoundingClientRect();
        var x = (e.clientX - rect.left) / rect.width - 0.5;
        var y = (e.clientY - rect.top) / rect.height - 0.5;
        frame = heroPro.querySelector(".gu-hero-pro-slide.is-active .gu-hero-visual-frame");
        if (!frame) return;
        frame.style.transform =
          "translate(" + (x * 10) + "px, " + (y * 8) + "px) scale(1.01)";
      },
      { passive: true }
    );
    heroPro.addEventListener("pointerleave", function () {
      frame = heroPro.querySelector(".gu-hero-pro-slide.is-active .gu-hero-visual-frame");
      if (frame) frame.style.transform = "";
    });
  }

  /* FAQ: only one open at a time */
  document.querySelectorAll(".gu-faq-item").forEach(function (item) {
    item.addEventListener("toggle", function () {
      if (!item.open) return;
      document.querySelectorAll(".gu-faq-item").forEach(function (other) {
        if (other !== item) other.open = false;
      });
    });
  });

  /* Lead submission → Google Apps Script (Sheet + email to MSS Builders inboxes) */
  var LEAD_ENDPOINT =
    "https://script.google.com/macros/s/AKfycbwZsmVWXwgwKq6gJnGTGTtW1lYaoFq6JsgcUI5bjWahNHOfYF7CzaHQW-nEHi2f_on-/exec";

  function getLeadStatusEl(form) {
    var el = form.querySelector("[data-lead-status]");
    if (!el) {
      el = document.createElement("p");
      el.className = "form-hint";
      el.setAttribute("data-lead-status", "");
      el.setAttribute("role", "status");
      el.setAttribute("aria-live", "polite");
      form.appendChild(el);
    }
    return el;
  }

  var LEAD_DEDUPE_MS = 24 * 60 * 60 * 1000;
  var FAKE_NAMES = /^(test|testing|asdf|qwerty|abc|abcd|xyz|fake|demo|sample|none|na|n\/a|null|admin|user|name|aaa+|xxx+)$/i;
  var FAKE_EMAIL_USERS = /^(admin|test|testing|demo|fake|sample|abc|xyz|asdf|qwerty|none|null|noreply|no-reply|example|user|info|mail|email)\d*$/i;
  var FAKE_EMAIL_DOMAINS = /(^|\.)(example\.(com|org|net)|test\.com|domain\.com|email\.com|mailinator\.com|yopmail\.com|tempmail\.com|temp-mail\.org|guerrillamail\.com|10minutemail\.com|trashmail\.com|sharklasers\.com|fakeinbox\.com|getnada\.com|dispostable\.com)$/i;

  function toIndianMobile(raw) {
    var d = String(raw || "").replace(/\D/g, "");
    if (d.length === 12 && d.indexOf("91") === 0) d = d.slice(2);
    else if (d.length === 11 && d.charAt(0) === "0") d = d.slice(1);
    return d;
  }

  function phoneError(raw) {
    var d = toIndianMobile(raw);
    if (d.length !== 10) return "Enter a valid 10-digit mobile number.";
    if (!/^[6-9]/.test(d)) return "Mobile number should start with 6, 7, 8 or 9.";
    if (/^(\d)\1{9}$/.test(d)) return "Please enter your real mobile number.";
    if ("01234567890123456789".indexOf(d) !== -1 || "98765432109876543210".indexOf(d) !== -1) {
      return "Please enter your real mobile number.";
    }
    var unique = {};
    for (var i = 0; i < d.length; i++) unique[d.charAt(i)] = true;
    if (Object.keys(unique).length < 3) return "Please enter your real mobile number.";
    return "";
  }

  function emailError(raw) {
    var v = String(raw || "").trim().toLowerCase();
    if (!v) return "";
    if (!/^[^\s@]+@[^\s@]+\.[a-z]{2,}$/.test(v)) return "Enter a valid email address.";
    var parts = v.split("@");
    if (FAKE_EMAIL_USERS.test(parts[0]) || FAKE_EMAIL_DOMAINS.test(parts[1])) {
      return "Please use your personal email address.";
    }
    return "";
  }

  function nameError(raw) {
    var v = String(raw || "").trim();
    if (v.replace(/[^A-Za-z]/g, "").length < 2) return "Please enter your full name.";
    if (!/^[A-Za-z][A-Za-z .'-]*$/.test(v)) return "Name should contain letters only.";
    if (FAKE_NAMES.test(v.replace(/\s+/g, ""))) return "Please enter your real name.";
    return "";
  }

  function validateLead(data) {
    var err = nameError(data.name);
    if (err) return { field: "name", message: err };
    err = phoneError(data.phone);
    if (err) return { field: "phone", message: err };
    if (data.email) {
      err = emailError(data.email);
      if (err) return { field: "email", message: err };
    }
    return null;
  }

  function wasRecentlySubmitted(mobile) {
    try {
      var seen = JSON.parse(localStorage.getItem("gu_leads") || "{}");
      return seen[mobile] && Date.now() - seen[mobile] < LEAD_DEDUPE_MS;
    } catch (err) {
      return false;
    }
  }

  function rememberSubmission(mobile) {
    try {
      var seen = JSON.parse(localStorage.getItem("gu_leads") || "{}");
      seen[mobile] = Date.now();
      localStorage.setItem("gu_leads", JSON.stringify(seen));
    } catch (err) {}
  }

  document.querySelectorAll('input[name="phone"]').forEach(function (input) {
    input.setAttribute("inputmode", "numeric");
    input.setAttribute("autocomplete", "tel-national");
    input.removeAttribute("maxlength");
    if (/X{5}/.test(input.getAttribute("placeholder") || "")) {
      input.setAttribute("placeholder", "10-digit mobile number");
    }
    input.addEventListener("input", function () {
      var d = toIndianMobile(input.value);
      if (input.value !== d.slice(0, 10)) input.value = d.slice(0, 10);
    });
  });

  /* Live location capture for address / locality fields */
  var PIN_SVG =
    '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>';

  function mapLink(lat, lng) {
    return "https://www.google.com/maps?q=" + lat + "," + lng;
  }

  function reverseGeocode(lat, lng) {
    var url =
      "https://nominatim.openstreetmap.org/reverse?format=jsonv2&addressdetails=1&accept-language=en&lat=" +
      encodeURIComponent(lat) +
      "&lon=" +
      encodeURIComponent(lng);
    return fetch(url, { headers: { Accept: "application/json" } }).then(function (res) {
      if (!res.ok) throw new Error("geocode failed");
      return res.json();
    });
  }

  function clearFormLocation(form) {
    delete form.dataset.geoLat;
    delete form.dataset.geoLng;
    delete form.dataset.geoAcc;
    form.querySelectorAll("[data-loc-status]").forEach(function (el) {
      el.textContent = "";
    });
  }

  function setupLocationField(input) {
    var form = input.form || input.closest("form");
    if (!form || input.dataset.locReady) return;
    input.dataset.locReady = "1";

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "loc-btn";
    btn.innerHTML = PIN_SVG + "<span>Use my current location</span>";

    var status = document.createElement("span");
    status.className = "loc-status";
    status.setAttribute("data-loc-status", "");
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");

    var wrap = document.createElement("span");
    wrap.className = "loc-row";
    wrap.appendChild(btn);
    wrap.appendChild(status);
    input.insertAdjacentElement("afterend", wrap);

    if (!("geolocation" in navigator)) {
      btn.disabled = true;
      status.textContent = "Location isn’t supported on this browser — please type your address.";
      return;
    }

    btn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      btn.disabled = true;
      btn.classList.add("is-loading");
      status.textContent = "Getting your location…";

      navigator.geolocation.getCurrentPosition(
        function (pos) {
          var lat = pos.coords.latitude.toFixed(6);
          var lng = pos.coords.longitude.toFixed(6);
          var acc = Math.round(pos.coords.accuracy);
          form.dataset.geoLat = lat;
          form.dataset.geoLng = lng;
          form.dataset.geoAcc = String(acc);

          var done = function (msg) {
            btn.disabled = false;
            btn.classList.remove("is-loading");
            status.innerHTML = "";
            status.appendChild(document.createTextNode(msg + " (±" + acc + " m) · "));
            var a = document.createElement("a");
            a.href = mapLink(lat, lng);
            a.target = "_blank";
            a.rel = "noopener";
            a.textContent = "View on map";
            status.appendChild(a);
          };

          reverseGeocode(lat, lng)
            .then(function (geo) {
              if (geo && geo.display_name) input.value = geo.display_name;
              done("Location captured");
            })
            .catch(function () {
              if (!input.value) input.value = lat + ", " + lng;
              done("Location captured — please check the address");
            });
        },
        function (err) {
          btn.disabled = false;
          btn.classList.remove("is-loading");
          status.textContent =
            err && err.code === 1
              ? "Location permission denied — please allow location access or type your address."
              : "Couldn’t get your location — please try again or type your address.";
        },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
      );
    });
  }

  document
    .querySelectorAll('form input[name="address"], form input[name="locality"]')
    .forEach(setupLocationField);

  function attachLocation(form, data) {
    var lat = form.dataset.geoLat;
    var lng = form.dataset.geoLng;
    if (!lat || !lng) return;
    var link = mapLink(lat, lng);
    var note = "Live location: " + link + " (±" + form.dataset.geoAcc + " m)";
    data.latitude = lat;
    data.longitude = lng;
    data.location_accuracy_m = form.dataset.geoAcc;
    data.map_link = link;
    ["address", "locality"].forEach(function (key) {
      if (key in data) data[key] = (data[key] ? data[key] + " | " : "") + note;
    });
    if (!("address" in data) && !("locality" in data)) {
      data.message = (data.message ? data.message + "\n" : "") + note;
    }
  }

  function submitLead(form, data, statusEl, onSuccess) {
    var status = statusEl || getLeadStatusEl(form);

    var invalid = validateLead(data);
    if (invalid) {
      status.textContent = invalid.message;
      var badField = form.querySelector('[name="' + invalid.field + '"]');
      if (badField) badField.focus();
      return;
    }

    var mobile = toIndianMobile(data.phone);
    data.phone = "+91 " + mobile.slice(0, 5) + " " + mobile.slice(5);
    if (wasRecentlySubmitted(mobile)) {
      status.textContent =
        "We already have your request from this number — our team will call you shortly.";
      return;
    }

    var btn = form.querySelector('[type="submit"]');
    var btnText = btn ? btn.textContent : "";
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Sending…";
    }
    status.textContent = "Sending your details…";

    data.page_url = window.location.href;
    attachLocation(form, data);
    var body = new URLSearchParams();
    Object.keys(data).forEach(function (key) {
      var val = data[key];
      if (val !== undefined && val !== null && String(val).trim() !== "") {
        body.append(key, String(val).trim());
      }
    });

    /* no-cors: Apps Script redirects, so the response is opaque — a resolved fetch means it was delivered */
    fetch(LEAD_ENDPOINT, { method: "POST", mode: "no-cors", body: body })
      .then(function () {
        rememberSubmission(mobile);
        status.textContent =
          "Thank you! The MSS Grandeur team will contact you shortly.";
        form.reset();
        clearFormLocation(form);
        if (typeof onSuccess === "function") onSuccess();
      })
      .catch(function () {
        status.textContent =
          "Couldn’t send right now. Please call or WhatsApp us, or try again.";
      })
      .then(function () {
        if (btn) {
          btn.disabled = false;
          btn.textContent = btnText;
        }
      });
  }

  function fieldVal(form, name) {
    var el = form.querySelector('[name="' + name + '"]');
    return el ? el.value || "" : "";
  }

  function checkedVal(form, name) {
    var el = form.querySelector('[name="' + name + '"]');
    if (!el) return "";
    return el.checked ? "Yes" : "No";
  }

  window.guSubmitLead = submitLead;
  window.guCheckedVal = checkedVal;

  /* Quote popup */
  var quoteModal = document.getElementById("quote-modal");
  var quoteForm = document.getElementById("quote-modal-form");
  var quoteService = document.getElementById("quote-service");
  var quoteStatus = document.getElementById("quote-form-status");
  var lastFocus = null;
  var quoteType = "";

  var quoteModes = {
    booking: {
      title: "Book a site visit",
      lead: "Share your details — we’ll call to confirm a visit time.",
      button: "Confirm booking",
      status: "We’ll call you to confirm your visit.",
    },
    quote: {
      title: "Get a free quote",
      lead: "Tell us what you need — we’ll call you back with a quote.",
      button: "Get my quote",
      status: "We’ll call you back with your quote.",
    },
  };

  var quoteTitle = quoteModal ? quoteModal.querySelector("#quote-modal-title") : null;
  var quoteLead = quoteModal ? quoteModal.querySelector(".quote-modal-lead") : null;
  var quoteSubmit = quoteForm ? quoteForm.querySelector('button[type="submit"]') : null;
  var quoteMessage = quoteForm ? quoteForm.querySelector('[name="message"]') : null;
  var quoteDefaults = {
    title: quoteTitle ? quoteTitle.textContent : "",
    lead: quoteLead ? quoteLead.textContent : "",
    button: quoteSubmit ? quoteSubmit.textContent : "",
    status: "We’ll call you back within business hours.",
  };

  function openQuote(service, type, topic, auto) {
    if (!quoteModal) return;
    lastFocus = document.activeElement;
    quoteType = quoteModes[type] ? type : "";
    var mode = quoteModes[quoteType] || quoteDefaults;
    if (quoteTitle) quoteTitle.textContent = mode.title;
    if (quoteLead) quoteLead.textContent = mode.lead;
    if (quoteSubmit) quoteSubmit.textContent = mode.button;
    if (quoteMessage && topic) {
      quoteMessage.value = (quoteType === "booking" ? "Site visit for: " : "Quote for: ") + topic;
    }
    quoteModal.hidden = false;
    document.body.classList.add("quote-open");
    setNavOpen(false);
    if (quoteService) {
      quoteService.value = service || "";
    }
    if (quoteStatus) {
      quoteStatus.textContent = mode.status;
    }
    if (auto) return;
    var first = quoteModal.querySelector("input, select, textarea, button");
    if (first) first.focus();
  }

  function closeQuote() {
    if (!quoteModal) return;
    quoteModal.hidden = true;
    document.body.classList.remove("quote-open");
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }

  document.addEventListener("click", function (e) {
    var trigger = e.target.closest("[data-open-quote]");
    if (trigger) {
      e.preventDefault();
      openQuote(
        trigger.getAttribute("data-service") || "",
        trigger.getAttribute("data-quote-type") || "",
        trigger.getAttribute("data-topic") || ""
      );
      return;
    }
    if (e.target.closest("[data-close-quote]")) {
      e.preventDefault();
      closeQuote();
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && quoteModal && !quoteModal.hidden) {
      closeQuote();
    }
  });

  document.querySelectorAll("[data-close-hero-form]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var form = btn.closest("form");
      if (!form) return;
      form.hidden = true;
      var inner = form.closest(".apc-hero-inner");
      if (inner) inner.classList.add("is-form-closed");
    });
  });

  /* Hero form drag: floating (desktop) moves anywhere in the viewport by its heading or
     empty space; in-flow (mobile) moves within the hero by its heading only, so
     touch-scrolling over the rest of the form still scrolls the page. */
  document.querySelectorAll(".apc-hero-form").forEach(function (form) {
    var drag = null;
    var tx = 0;
    var ty = 0;
    var MARGIN = 8;
    var hero = form.closest(".apc-hero");

    function clamp(v, min, max) {
      return Math.min(Math.max(v, min), Math.max(min, max));
    }

    function isFloating() {
      return getComputedStyle(form).position === "fixed";
    }

    function resetFlowOffset() {
      tx = 0;
      ty = 0;
      form.style.transform = "";
    }

    form.addEventListener("pointerdown", function (e) {
      if (e.button !== 0) return;
      var floating = isFloating();
      if (floating) {
        if (e.target.closest("input, select, textarea, button, a, label")) return;
      } else if (!e.target.closest("h2")) {
        return;
      }
      var rect = form.getBoundingClientRect();
      if (floating) {
        drag = { id: e.pointerId, floating: true, dx: e.clientX - rect.left, dy: e.clientY - rect.top };
        form.style.animation = "none";
        form.style.right = "auto";
        form.style.left = rect.left + "px";
        form.style.top = rect.top + "px";
      } else {
        var bounds = (hero || document.documentElement).getBoundingClientRect();
        drag = {
          id: e.pointerId,
          floating: false,
          x: e.clientX,
          y: e.clientY,
          tx: tx,
          ty: ty,
          minX: bounds.left + MARGIN - rect.left,
          maxX: bounds.right - MARGIN - rect.right,
          minY: bounds.top + MARGIN - rect.top,
          maxY: bounds.bottom - MARGIN - rect.bottom
        };
      }
      form.classList.add("is-dragging");
      form.setPointerCapture(e.pointerId);
      e.preventDefault();
    });

    form.addEventListener("pointermove", function (e) {
      if (!drag || e.pointerId !== drag.id) return;
      if (drag.floating) {
        var w = form.offsetWidth;
        var h = form.offsetHeight;
        form.style.left = clamp(e.clientX - drag.dx, MARGIN, window.innerWidth - w - MARGIN) + "px";
        form.style.top = clamp(e.clientY - drag.dy, MARGIN, window.innerHeight - h - MARGIN) + "px";
        return;
      }
      var mx = clamp(e.clientX - drag.x, drag.minX, drag.maxX);
      var my = clamp(e.clientY - drag.y, drag.minY, drag.maxY);
      tx = drag.tx + mx;
      ty = drag.ty + my;
      form.style.transform = "translate(" + tx + "px, " + ty + "px)";
    });

    function endDrag(e) {
      if (!drag || e.pointerId !== drag.id) return;
      drag = null;
      form.classList.remove("is-dragging");
    }
    form.addEventListener("pointerup", endDrag);
    form.addEventListener("pointercancel", endDrag);

    window.addEventListener("resize", function () {
      if (isFloating()) {
        resetFlowOffset();
        if (!form.style.left) return;
        var rect = form.getBoundingClientRect();
        form.style.left = clamp(rect.left, MARGIN, window.innerWidth - rect.width - MARGIN) + "px";
        form.style.top = clamp(rect.top, MARGIN, window.innerHeight - rect.height - MARGIN) + "px";
      } else if (form.style.left) {
        form.style.left = "";
        form.style.top = "";
        form.style.right = "";
      }
    });
  });

  /* Home page: open the enquiry popup once per visit; close it after 1 minute if untouched */
  var AUTO_POPUP_DELAY = 4000;
  var AUTO_POPUP_CLOSE = 60000;
  if (quoteModal && document.body.classList.contains("page-home")) {
    var autoSeen = false;
    try {
      autoSeen = sessionStorage.getItem("gu_auto_popup") === "1";
    } catch (err) {}
    if (!autoSeen) {
      window.setTimeout(function () {
        if (!quoteModal.hidden || document.body.classList.contains("nav-open")) return;
        try {
          sessionStorage.setItem("gu_auto_popup", "1");
        } catch (err) {}
        openQuote("", "", "", true);
        var touched = false;
        var markTouched = function () {
          touched = true;
        };
        quoteModal.addEventListener("input", markTouched, { once: true });
        quoteModal.addEventListener("focusin", markTouched, { once: true });
        window.setTimeout(function () {
          if (!touched && !quoteModal.hidden) closeQuote();
        }, AUTO_POPUP_CLOSE);
      }, AUTO_POPUP_DELAY);
    }
  }

  if (quoteForm) {
    quoteForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var service = fieldVal(quoteForm, "service");
      submitLead(
        quoteForm,
        {
          name: fieldVal(quoteForm, "name"),
          phone: fieldVal(quoteForm, "phone"),
          email: fieldVal(quoteForm, "email"),
          locality: fieldVal(quoteForm, "locality"),
          service: service,
          message: fieldVal(quoteForm, "message"),
          request_type: quoteType || "enquiry",
          source: "quote-popup",
        },
        quoteStatus,
        function () {
          if (quoteService && service) quoteService.value = service;
          window.setTimeout(closeQuote, 1800);
        }
      );
    });
  }

  var contactForm = document.getElementById("contact-form");
  if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();
      submitLead(contactForm, {
        name: fieldVal(contactForm, "name"),
        phone: fieldVal(contactForm, "phone"),
        email: fieldVal(contactForm, "email"),
        locality: fieldVal(contactForm, "locality"),
        service: fieldVal(contactForm, "service"),
        request_type: fieldVal(contactForm, "request_type"),
        message: fieldVal(contactForm, "message"),
        whatsapp: checkedVal(contactForm, "whatsapp"),
        source: "contact-form",
      });
    });
  }

  /* Careers: Agent and Tele Caller applications */
  document.querySelectorAll("[data-career-form]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var role = form.getAttribute("data-role") || "Careers";
      var languages = Array.prototype.map
        .call(form.querySelectorAll('[name="languages"]:checked'), function (el) {
          return el.value;
        })
        .join(", ");
      var status = getLeadStatusEl(form);
      var summary = [
        ["Role", role],
        ["Type", fieldVal(form, "partner_type")],
        ["Qualification", fieldVal(form, "qualification")],
        ["Experience", fieldVal(form, "experience")],
        ["Languages", languages],
        ["Availability", fieldVal(form, "availability")],
      ]
        .filter(function (pair) {
          return pair[1];
        })
        .map(function (pair) {
          return pair[0] + ": " + pair[1];
        })
        .join(" | ");
      var note = fieldVal(form, "message").trim();
      submitLead(
        form,
        {
          name: fieldVal(form, "name"),
          phone: fieldVal(form, "phone"),
          email: fieldVal(form, "email"),
          locality: fieldVal(form, "locality"),
          service: "Job application – " + role,
          request_type: "Career application",
          role: role,
          partner_type: fieldVal(form, "partner_type"),
          qualification: fieldVal(form, "qualification"),
          experience: fieldVal(form, "experience"),
          languages: languages,
          availability: fieldVal(form, "availability"),
          message: summary + (note ? "\n" + note : ""),
          whatsapp: checkedVal(form, "whatsapp"),
          source: form.getAttribute("data-source") || "careers",
        },
        status,
        function () {
          status.textContent =
            "Thank you for applying! The MSS Builders hiring team will call you shortly.";
        }
      );
    });
  });

  /* Lead hero site-visit forms */
  document.querySelectorAll("[data-lead-form]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var service = form.getAttribute("data-service") || "Site visit";
      submitLead(form, {
        name: fieldVal(form, "name"),
        phone: fieldVal(form, "phone"),
        address: fieldVal(form, "address"),
        service: service,
        need: fieldVal(form, "need"),
        whatsapp: checkedVal(form, "whatsapp"),
        source: "site-visit-" + service.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
      });
    });
  });

  /* Links to the hero lead form: the form is often already on screen, so scroll, highlight and focus it */
  var heroLeadForm = document.getElementById("lead-form");
  if (heroLeadForm) {
    document.querySelectorAll('a[href="#lead-form"]').forEach(function (link) {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        var need = link.getAttribute("data-need");
        var needSelect = heroLeadForm.querySelector('[name="need"]');
        if (need && needSelect) needSelect.value = need;
        var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        heroLeadForm.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
        heroLeadForm.classList.remove("is-highlight");
        void heroLeadForm.offsetWidth;
        heroLeadForm.classList.add("is-highlight");
        clearTimeout(heroLeadForm._highlightTimer);
        heroLeadForm._highlightTimer = setTimeout(function () {
          heroLeadForm.classList.remove("is-highlight");
        }, 1600);
        var first = heroLeadForm.querySelector('[name="name"]');
        if (first) first.focus({ preventScroll: true });
      });
    });
  }

  /* FAQ: only one open at a time */
  document.querySelectorAll("[data-faq]").forEach(function (root) {
    root.querySelectorAll("details").forEach(function (item) {
      item.addEventListener("toggle", function () {
        if (!item.open) return;
        root.querySelectorAll("details").forEach(function (other) {
          if (other !== item) other.open = false;
        });
      });
    });
  });

  /* FAQ: show the first 5, rest behind a "View all" button */
  var FAQ_VISIBLE = 5;
  document.querySelectorAll("[data-faq]").forEach(function (root) {
    var items = Array.prototype.slice.call(root.querySelectorAll("details"));
    if (items.length <= FAQ_VISIBLE) return;
    var extra = items.slice(FAQ_VISIBLE);
    var groups = root.querySelectorAll(".bh-faq-group");
    var cols = root.querySelectorAll(".bh-faq-col, .apc-faq-col");

    var more = document.createElement("div");
    more.className = "faq-more";
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "faq-more-btn";
    btn.setAttribute("aria-expanded", "false");
    more.appendChild(btn);
    root.parentNode.insertBefore(more, root.nextSibling);

    function hasVisibleItem(el) {
      return Array.prototype.some.call(el.querySelectorAll("details"), function (d) {
        return !d.hidden;
      });
    }

    function setExpanded(expanded) {
      extra.forEach(function (d) {
        d.hidden = !expanded;
        if (!expanded) d.open = false;
      });
      groups.forEach(function (g) {
        var next = g.nextElementSibling;
        var visible = false;
        while (next && !next.classList.contains("bh-faq-group")) {
          if (next.tagName === "DETAILS" && !next.hidden) visible = true;
          else if (next.querySelector && next.querySelector("details") && hasVisibleItem(next)) visible = true;
          next = next.nextElementSibling;
        }
        g.hidden = !visible;
      });
      cols.forEach(function (c) {
        c.hidden = !hasVisibleItem(c);
      });
      root.classList.toggle("is-faq-collapsed", !expanded);
      btn.setAttribute("aria-expanded", expanded ? "true" : "false");
      btn.textContent = expanded ? "Show fewer FAQs" : "View all FAQs (" + extra.length + " more)";
    }

    btn.addEventListener("click", function () {
      var expand = btn.getAttribute("aria-expanded") !== "true";
      setExpanded(expand);
      if (!expand) root.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    setExpanded(false);
  });

  /* Floating quote tab: show after first scroll, hide over the footer */
  var quoteTab = document.querySelector(".quote-tab");
  if (quoteTab) {
    var footerEl = document.querySelector(".site-footer");
    var updateQuoteTab = function () {
      var scrolled = window.scrollY > 240;
      var overFooter = footerEl && footerEl.getBoundingClientRect().top < window.innerHeight * 0.6;
      quoteTab.classList.toggle("is-visible", scrolled && !overFooter);
    };
    window.addEventListener("scroll", updateQuoteTab, { passive: true });
    window.addEventListener("resize", updateQuoteTab);
    updateQuoteTab();
  }

  /* Before / after drag sliders */
  document.querySelectorAll("[data-ba-slider]").forEach(function (slider) {
    var range = slider.querySelector(".ba-range");
    var dragging = false;

    var setPos = function (pct) {
      pct = Math.max(0, Math.min(100, pct));
      slider.style.setProperty("--pos", pct + "%");
      slider.dataset.near = pct < 15 ? "left" : pct > 85 ? "right" : "";
      if (range) range.value = String(Math.round(pct));
    };

    var fromEvent = function (e) {
      var rect = slider.getBoundingClientRect();
      setPos(((e.clientX - rect.left) / rect.width) * 100);
    };

    slider.addEventListener("pointerdown", function (e) {
      dragging = true;
      slider.classList.remove("is-hinting");
      slider.classList.add("is-dragging");
      slider.setPointerCapture(e.pointerId);
      fromEvent(e);
      if (range) range.focus({ preventScroll: true });
    });
    slider.addEventListener("pointermove", function (e) {
      if (dragging) fromEvent(e);
    });
    var stop = function () {
      dragging = false;
      slider.classList.remove("is-dragging");
    };
    slider.addEventListener("pointerup", stop);
    slider.addEventListener("pointercancel", stop);

    if (range) {
      range.addEventListener("input", function () {
        setPos(Number(range.value));
      });
    }

    if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          io.disconnect();
          slider.classList.add("is-hinting");
          setPos(30);
          setTimeout(function () { if (!dragging) setPos(70); }, 650);
          setTimeout(function () {
            if (!dragging) setPos(50);
            setTimeout(function () { slider.classList.remove("is-hinting"); }, 650);
          }, 1300);
        });
      }, { threshold: 0.6 });
      io.observe(slider);
    }
  });
})();
