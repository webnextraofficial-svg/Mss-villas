/**
 * MSS Builders — MSS Balaji Grandeur lead webhook: Google Sheet row + email notifications
 *
 * TIP: Create this script from your Google Sheet:
 * Extensions → Apps Script (then SPREADSHEET_ID can stay empty)
 *
 * After paste: Deploy → Manage deployments → Edit → New version → Deploy
 *
 * Sheet columns (row 1):
 * Date & Time | Name | Phone | Email | Service / Requirement | Message | Lead Source | Submission Type | Page URL | Status | Location
 */

var CONFIG = {
  SPREADSHEET_ID: '',
  SHEET_NAME: 'Sheet1',
  RECIPIENTS: ['mssrealtorsdigital@gmail.com', 'mssrealtorsbusiness@gmail.com'],
  DEFAULT_STATUS: 'New',
  TIMEZONE: 'Asia/Kolkata',
  BRAND_NAME: 'MSS Builders',
  PROJECT_NAME: 'MSS Balaji Grandeur',
  BRAND_SITE: 'https://www.mssrealtors.com',
  BRAND_SITE_LABEL: 'mssrealtors.com',
  // PNG (not SVG/WebP) so Gmail and Outlook both render it.
  BRAND_LOGO: 'https://www.mssrealtors.com/assets/mss-builders-logo.png',
  SALES_PHONE: '+91 92979 75656',
  ADDRESS: 'Kalyandurgam Road, near Intell College, Anantapur, Andhra Pradesh',
  // Only catches double-clicks / retries of the same form on the same page.
  // The website already blocks repeat submissions from the same phone.
  DEDUPE_SECONDS: 120,
};

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(15000);
  } catch (err) {
    return jsonOutput_({
      ok: false,
      message: 'Server busy. Please try again in a moment.',
    });
  }

  try {
    var data = parsePostBody_(e);

    var name = clean_(data.name, 100);
    var phone = clean_(data.phone, 30);

    if (!name || !phone) {
      return jsonOutput_({ ok: false, message: 'Name and phone are required.' });
    }

    var phoneKey = normalizePhone_(phone);
    if (phoneKey.length < 10) {
      return jsonOutput_({ ok: false, message: 'Enter a valid phone number.' });
    }

    var source = clean_(data.source, 100) || 'website';
    var email = clean_(data.email, 160) || 'Not Provided';
    // Site-visit forms send the home type as "need"; enquiry/contact forms send it as "service".
    var homeType = clean_(data.need, 120) || clean_(data.service, 120) || 'Not Provided';
    var requestType = labelRequestType_(clean_(data.request_type, 120), source);
    var message = clean_(data.message, 2000) || 'General Enquiry';
    var location =
      clean_(data.address, 300) || clean_(data.locality, 300) || 'Not Provided';
    var mapLink = clean_(data.map_link, 300);
    var whatsapp = clean_(data.whatsapp, 10) || 'Not Provided';
    var pageUrl = clean_(data.page_url || data.pageUrl, 500) || 'Not Provided';

    var dedupeKey = buildDedupeKey_(phoneKey, source, pageUrl);
    if (isDuplicateLead_(dedupeKey)) {
      return jsonOutput_({
        ok: true,
        message: 'Thank you! The ' + CONFIG.PROJECT_NAME + ' team will contact you shortly.',
        duplicate: true,
        sheet_saved: false,
        email_sent: false,
      });
    }

    var submissionType = mapSubmissionType_(source);
    var serviceRequirement = buildServiceRequirement_(homeType, requestType);

    var tz = CONFIG.TIMEZONE || Session.getScriptTimeZone() || 'Asia/Kolkata';
    var dateTimeLabel = Utilities.formatDate(new Date(), tz, 'dd/MM/yyyy hh:mm:ss a');

    var row = [
      dateTimeLabel,
      name,
      phone,
      email,
      serviceRequirement,
      message,
      source,
      submissionType,
      pageUrl,
      CONFIG.DEFAULT_STATUS,
      location,
    ];

    var sheetOk = false;
    var sheetError = '';

    try {
      appendToSheet_(row);
      sheetOk = true;
    } catch (err) {
      sheetError = err && err.message ? String(err.message) : String(err);
      Logger.log('Sheet append failed: ' + sheetError);
    }

    var emailOk = false;
    try {
      sendLeadEmails_({
        name: name,
        phone: phone,
        email: email,
        homeType: homeType,
        requestType: requestType,
        message: message,
        location: location,
        mapLink: mapLink,
        whatsapp: whatsapp,
        source: source,
        pageUrl: pageUrl,
        submissionType: submissionType,
        dateTimeLabel: dateTimeLabel,
        sheetOk: sheetOk,
        sheetError: sheetError,
      });
      emailOk = true;
    } catch (err) {
      Logger.log(
        'Email failed: ' + err + ' (remaining quota: ' + MailApp.getRemainingDailyQuota() + ')'
      );
    }

    if (sheetOk || emailOk) {
      markLeadSeen_(dedupeKey);
    }

    if (!sheetOk && !emailOk) {
      return jsonOutput_({
        ok: false,
        message: 'Could not save lead. Check SPREADSHEET_ID and script permissions.',
      });
    }

    return jsonOutput_({
      ok: true,
      message: 'Thank you! The ' + CONFIG.PROJECT_NAME + ' team will contact you shortly.',
      sheet_saved: sheetOk,
      email_sent: emailOk,
    });
  } finally {
    lock.releaseLock();
  }
}

function doGet() {
  return jsonOutput_({
    ok: true,
    message: CONFIG.PROJECT_NAME + ' lead webhook is running.',
  });
}

function normalizePhone_(phone) {
  return String(phone || '').replace(/\D/g, '');
}

function buildDedupeKey_(phoneKey, source, pageUrl) {
  var path = String(pageUrl || '')
    .replace(/^https?:\/\/[^/]+/i, '')
    .split('?')[0]
    .split('#')[0];
  var raw = phoneKey + '|' + String(source || '') + '|' + path;
  var digest = Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, raw);
  return 'lead_' + Utilities.base64EncodeWebSafe(digest);
}

function isDuplicateLead_(dedupeKey) {
  return Boolean(CacheService.getScriptCache().get(dedupeKey));
}

function markLeadSeen_(dedupeKey) {
  CacheService.getScriptCache().put(dedupeKey, '1', CONFIG.DEDUPE_SECONDS);
}

function getSpreadsheet_() {
  if (CONFIG.SPREADSHEET_ID && CONFIG.SPREADSHEET_ID.indexOf('PASTE_') !== 0) {
    return SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  }
  return SpreadsheetApp.getActiveSpreadsheet();
}

function mapSubmissionType_(source) {
  var s = String(source || '').toLowerCase();
  if (s.indexOf('site-visit') !== -1) return 'Site Visit Booking';
  if (s.indexOf('quote') !== -1) return 'Enquiry Popup';
  if (s.indexOf('contact') !== -1) return 'Contact Form';
  if (s.indexOf('career') !== -1) return 'Career Application';
  return 'Website Form';
}

// The enquiry popup sends short codes; the site-visit forms send no request type at all.
function labelRequestType_(requestType, source) {
  var t = String(requestType || '').toLowerCase();
  if (t === 'booking') return 'Site visit booking';
  if (t === 'quote') return 'Price quote';
  if (t === 'enquiry') return 'General enquiry';
  if (!t && String(source || '').toLowerCase().indexOf('site-visit') !== -1) {
    return 'Site visit booking';
  }
  return requestType || 'Not Provided';
}

function buildServiceRequirement_(homeType, requestType) {
  var parts = [];
  if (homeType && homeType !== 'Not Provided') parts.push(homeType);
  if (requestType && requestType !== 'Not Provided') parts.push(requestType);
  return parts.join(' · ') || 'Not Provided';
}

function appendToSheet_(row) {
  var ss = getSpreadsheet_();
  if (!ss) {
    throw new Error('No spreadsheet found. Open sheet → Extensions → Apps Script and bind script there, or set SPREADSHEET_ID.');
  }
  var sheet = ss.getSheetByName(CONFIG.SHEET_NAME) || ss.getSheets()[0];
  sheet.appendRow(row);
}

function sendLeadEmails_(lead) {
  var subject =
    'New Lead — ' + lead.name + ' (' + lead.submissionType + ') · ' + CONFIG.PROJECT_NAME;

  var options = {
    to: CONFIG.RECIPIENTS.join(','),
    subject: subject,
    body: buildLeadEmailPlain_(lead),
    htmlBody: buildLeadEmailHtml_(lead),
    name: CONFIG.BRAND_NAME + ' Leads',
  };
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email)) {
    options.replyTo = lead.email;
  }
  MailApp.sendEmail(options);
}

function escapeHtml_(text) {
  return String(text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function buildLeadEmailPlain_(lead) {
  var body =
    'A new lead was submitted on ' + CONFIG.BRAND_SITE_LABEL + ' (' + CONFIG.PROJECT_NAME + ')\n\n' +
    'Date & Time: ' + lead.dateTimeLabel + '\n' +
    'Name: ' + lead.name + '\n' +
    'Phone: ' + lead.phone + '\n' +
    'Email: ' + lead.email + '\n' +
    'Home type: ' + lead.homeType + '\n' +
    'Request: ' + lead.requestType + '\n' +
    'Location: ' + lead.location + '\n' +
    (lead.mapLink ? 'Map: ' + lead.mapLink + '\n' : '') +
    'WhatsApp updates: ' + lead.whatsapp + '\n' +
    'Message: ' + lead.message + '\n' +
    'Lead Source: ' + lead.source + '\n' +
    'Submission Type: ' + lead.submissionType + '\n' +
    'Page URL: ' + lead.pageUrl + '\n' +
    'Sheet saved: ' + (lead.sheetOk ? 'Yes' : 'No') + '\n';
  if (lead.sheetError) {
    body += 'Sheet error: ' + lead.sheetError + '\n';
  }
  return body;
}

function buildLeadEmailHtml_(lead) {
  var site = escapeHtml_(CONFIG.BRAND_SITE);
  var siteLabel = escapeHtml_(CONFIG.BRAND_SITE_LABEL);
  var brand = escapeHtml_(CONFIG.BRAND_NAME);
  var project = escapeHtml_(CONFIG.PROJECT_NAME);
  var logo = escapeHtml_(CONFIG.BRAND_LOGO);
  var address = escapeHtml_(CONFIG.ADDRESS);
  var name = escapeHtml_(lead.name);
  var phone = escapeHtml_(lead.phone);
  var phoneHref = escapeHtml_('+' + normalizePhone_(lead.phone));
  var waHref = escapeHtml_('https://wa.me/' + normalizePhone_(lead.phone));
  var email = escapeHtml_(lead.email);
  var homeType = escapeHtml_(lead.homeType);
  var requestType = escapeHtml_(lead.requestType);
  var location = escapeHtml_(lead.location);
  var mapLink = escapeHtml_(lead.mapLink);
  var whatsapp = escapeHtml_(lead.whatsapp);
  var message = escapeHtml_(lead.message).replace(/\n/g, '<br>');
  var source = escapeHtml_(lead.source);
  var submissionType = escapeHtml_(lead.submissionType);
  var pageUrl = escapeHtml_(lead.pageUrl);
  var dateTimeLabel = escapeHtml_(lead.dateTimeLabel);
  var sheetStatus = lead.sheetOk
    ? '<span style="color:#059669;font-weight:700;">Saved to sheet</span>'
    : '<span style="color:#DC2626;font-weight:700;">Sheet not saved</span>';

  var row = function (label, value) {
    return (
      '<tr>' +
      '<td style="padding:12px 16px;border-bottom:1px solid #EFE8DC;width:34%;font-size:12px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.06em;vertical-align:top;">' +
      label +
      '</td>' +
      '<td style="padding:12px 16px;border-bottom:1px solid #EFE8DC;font-size:14px;color:#0B1626;line-height:1.5;vertical-align:top;">' +
      value +
      '</td>' +
      '</tr>'
    );
  };

  return (
    '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>' +
    '<body style="margin:0;padding:0;background:#F4F1EC;font-family:Arial,Helvetica,sans-serif;color:#0B1626;">' +
    '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#F4F1EC;padding:24px 12px;">' +
    '<tr><td align="center">' +
    '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:620px;background:#FFFFFF;border-radius:16px;overflow:hidden;border:1px solid #E5DCCB;box-shadow:0 16px 40px rgba(11,22,38,0.08);">' +
    '<tr><td bgcolor="#0B1626" style="background-color:#0B1626;background:linear-gradient(135deg,#0B1626 0%,#1B2A40 60%,#0B1626 100%);padding:26px 24px 22px;text-align:center;">' +
    '<table role="presentation" align="center" cellspacing="0" cellpadding="0" style="margin:0 auto 16px;">' +
    '<tr><td bgcolor="#FFFFFF" style="background:#FFFFFF;border-radius:14px;padding:10px 18px;border:1px solid rgba(184,147,90,0.6);box-shadow:0 10px 24px rgba(0,0,0,0.25);">' +
    '<a href="' + site + '" style="text-decoration:none;">' +
    '<img src="' + logo + '" alt="' + brand + '" width="184" height="49" style="display:block;width:184px;max-width:100%;height:auto;border:0;outline:none;">' +
    '</a>' +
    '</td></tr></table>' +
    '<p style="margin:0 0 10px;font-size:11px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:rgba(255,255,255,0.82);">New lead · ' + project + '</p>' +
    '<span style="display:inline-block;padding:8px 14px;border-radius:999px;background:#B8935A;color:#FFFFFF;font-size:12px;font-weight:700;letter-spacing:0.04em;">' +
    submissionType +
    '</span>' +
    '</td></tr>' +
    '<tr><td style="padding:22px 24px 8px;">' +
    '<p style="margin:0;font-size:16px;font-weight:700;color:#0B1626;">Lead from <span style="color:#B8935A;">' + name + '</span></p>' +
    '<p style="margin:8px 0 0;font-size:13px;color:#64748B;line-height:1.6;">Submitted on ' + siteLabel + ' · ' + dateTimeLabel + '</p>' +
    '</td></tr>' +
    '<tr><td style="padding:8px 24px 20px;">' +
    '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border:1px solid #EFE8DC;border-radius:12px;overflow:hidden;background:#FBF9F5;">' +
    row('Name', '<strong style="color:#0B1626;">' + name + '</strong>') +
    row('Phone', '<a href="tel:' + phoneHref + '" style="color:#0B1626;text-decoration:none;font-weight:700;">' + phone + '</a>') +
    row('Email', email === 'Not Provided' ? email : '<a href="mailto:' + email + '" style="color:#B8935A;text-decoration:none;">' + email + '</a>') +
    row('Home type', homeType) +
    row('Request', requestType) +
    row('Location', location + (mapLink ? '<br><a href="' + mapLink + '" style="color:#B8935A;text-decoration:none;">Open in Google Maps</a>' : '')) +
    row('WhatsApp updates', whatsapp) +
    row('Message', message) +
    row('Lead source', source) +
    row('Page URL', pageUrl === 'Not Provided' ? pageUrl : '<a href="' + pageUrl + '" style="color:#B8935A;text-decoration:none;word-break:break-all;">' + pageUrl + '</a>') +
    row('Sheet status', sheetStatus) +
    '</table>' +
    '</td></tr>' +
    '<tr><td style="padding:0 24px 24px;">' +
    '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#FBF6EE;border:1px solid #E5D3B3;border-radius:12px;">' +
    '<tr><td style="padding:16px 18px;text-align:center;">' +
    '<p style="margin:0 0 12px;font-size:13px;color:#475569;">Call back within business hours</p>' +
    '<a href="tel:' + phoneHref + '" style="display:inline-block;margin:0 6px 6px 0;padding:11px 18px;border-radius:999px;background:#B8935A;color:#FFFFFF;font-size:13px;font-weight:700;text-decoration:none;">Call lead</a>' +
    '<a href="' + waHref + '" style="display:inline-block;margin:0 6px 6px 0;padding:11px 18px;border-radius:999px;background:#25D366;color:#FFFFFF;font-size:13px;font-weight:700;text-decoration:none;">WhatsApp lead</a>' +
    '<a href="' + site + '" style="display:inline-block;margin:0 0 6px;padding:11px 18px;border-radius:999px;background:#0B1626;color:#FFFFFF;font-size:13px;font-weight:700;text-decoration:none;">Open website</a>' +
    '</td></tr></table>' +
    '</td></tr>' +
    '<tr><td style="padding:18px 24px 24px;border-top:1px solid #EFE8DC;background:#FCFBF8;text-align:center;">' +
    '<p style="margin:0;font-size:12px;color:#94A3B8;line-height:1.6;">' + brand + ' · ' + project + '<br>' + address + '<br>' +
    escapeHtml_(CONFIG.SALES_PHONE) + ' · <a href="' + site + '" style="color:#B8935A;text-decoration:none;">' + siteLabel + '</a></p>' +
    '</td></tr>' +
    '</table></td></tr></table></body></html>'
  );
}

function parsePostBody_(e) {
  if (!e) return {};

  if (e.parameter && (e.parameter.name || e.parameter.phone)) {
    return e.parameter;
  }

  if (e.postData && e.postData.contents) {
    var type = String(e.postData.type || '').toLowerCase();
    if (type.indexOf('application/x-www-form-urlencoded') !== -1) {
      var params = {};
      String(e.postData.contents)
        .split('&')
        .forEach(function (pair) {
          var parts = pair.split('=');
          if (!parts[0]) return;
          var key = decodeURIComponent(parts[0].replace(/\+/g, ' '));
          var val = decodeURIComponent((parts[1] || '').replace(/\+/g, ' '));
          params[key] = val;
        });
      return params;
    }
    if (type.indexOf('application/json') !== -1) {
      try {
        return JSON.parse(e.postData.contents);
      } catch (err) {
        return {};
      }
    }
  }

  return e.parameter || {};
}

function clean_(value, maxLen) {
  var s = String(value || '')
    .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '')
    .trim();
  if (maxLen && s.length > maxLen) s = s.slice(0, maxLen);
  return s;
}

function jsonOutput_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}
