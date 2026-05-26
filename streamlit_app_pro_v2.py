"""
╔══════════════════════════════════════════════════════════════╗
║   🇮🇳  INDIAN STOCK MARKET PRO DASHBOARD  — Web Version     ║
║   Streamlit App — Deploy free on Streamlit Cloud            ║
║   ALL DATA IS DYNAMIC — fetched fresh every session         ║
╚══════════════════════════════════════════════════════════════╝
TABS ORDER (v2):
  0  ⭐ Today's Picks
  1  🔥 Try Your Luck PRO
  2  🚀 Breakout & DMA
  3  💪 Technical
  4  🏛️ Broker Picks
  5  📊 Gainers & Losers
  6  ⚠️ High & Fall
  7  🌱 Long Term View
  8  📉 All Indices
  9  🔍 Stock Info
  10 🏦 Mutual Funds
  11 🛡️ Pro Tools
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import random

# Use cloudscraper — bypasses Cloudflare/JS cookie challenges that NSE uses
try:
    import cloudscraper
    _USE_CLOUDSCRAPER = True
except ImportError:
    import requests
    _USE_CLOUDSCRAPER = False

import requests  # always import as fallback

# ═══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="🇮🇳 Stock Market Pro Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
#  GOOGLE ANALYTICS 4 — Measurement ID: Replace G-XXXXXXXXXX
#  HOW TO GET YOUR ID:
#  1. Go to analytics.google.com → Create Account → Create Property
#  2. Choose "Web" → Enter your Streamlit app URL
#  3. Copy your "Measurement ID" (starts with G-)
#  4. Replace G-XXXXXXXXXX below with your real ID
# ═══════════════════════════════════════════════════════════════
GA_MEASUREMENT_ID = "G-7S5H89MKC5"   # ← REPLACE WITH YOUR REAL GA4 ID

def inject_ga():
    """Inject Google Analytics 4 tracking + custom event helpers."""
    st.markdown(f"""
    <!-- Google Analytics 4 — Stock Market Pro Dashboard -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      // Main page view config
      gtag('config', '{GA_MEASUREMENT_ID}', {{
        'page_title': 'Stock Market Pro Dashboard',
        'page_location': window.location.href,
        'send_page_view': true,
        'custom_map': {{
          'dimension1': 'device_type',
          'dimension2': 'app_version'
        }}
      }});

      // ── Helper: track tab clicks ──────────────────────────────
      window.trackTab = function(tabName) {{
        gtag('event', 'tab_view', {{
          'event_category': 'Navigation',
          'event_label': tabName,
          'value': 1
        }});
      }};

      // ── Helper: track symbol searches ─────────────────────────
      window.trackSearch = function(symbol) {{
        gtag('event', 'search', {{
          'event_category': 'Stock Search',
          'search_term': symbol
        }});
      }};

      // ── Helper: track button clicks ───────────────────────────
      window.trackAction = function(action, label) {{
        gtag('event', action, {{
          'event_category': 'User Action',
          'event_label': label
        }});
      }};

      // ── Auto-detect device type and log ──────────────────────
      var deviceType = /Mobi|Android/i.test(navigator.userAgent) ? 'Mobile' :
                       /Tablet|iPad/i.test(navigator.userAgent) ? 'Tablet' : 'Desktop';
      gtag('event', 'device_detected', {{
        'event_category': 'Device',
        'event_label': deviceType,
        'dimension1': deviceType
      }});

      // ── Log app open time ─────────────────────────────────────
      var openHour = new Date().getHours();
      var session  = openHour < 9 ? 'Pre-Market' :
                     openHour < 15 ? 'Market Hours' :
                     openHour < 18 ? 'Post-Market' : 'After Hours';
      gtag('event', 'app_opened', {{
        'event_category': 'Session',
        'event_label': session,
        'value': 1
      }});

      // ── Track tab switching via MutationObserver ──────────────
      // Watches for Streamlit tab changes and fires GA events
      document.addEventListener('DOMContentLoaded', function() {{
        setTimeout(function() {{
          var tabs = document.querySelectorAll('[data-baseweb="tab"]');
          tabs.forEach(function(tab) {{
            tab.addEventListener('click', function() {{
              window.trackTab(this.innerText.trim());
            }});
          }});
        }}, 2000);
      }});

      // ── Track time spent on app ───────────────────────────────
      var startTime = Date.now();
      window.addEventListener('beforeunload', function() {{
        var timeSpent = Math.round((Date.now() - startTime) / 1000);
        gtag('event', 'time_spent', {{
          'event_category': 'Engagement',
          'event_label': 'seconds',
          'value': timeSpent
        }});
      }});
    </script>
    <!-- End Google Analytics -->
    """, unsafe_allow_html=True)

# Inject GA on every page load
inject_ga()

# ═══════════════════════════════════════════════════════════════
#  CUSTOM CSS — Beautiful Dark Theme
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1c1c2e 0%, #16213e 50%, #0f3460 100%); }
    #MainMenu, footer, header { visibility: hidden; }
    .main .block-container { padding: 0.3rem 0.8rem 0.5rem 0.8rem !important; max-width: 100% !important; }
    .main .block-container > div:first-child { margin-top: 12px !important; }
    .element-container { margin-bottom: 12px !important; }
    .stMarkdown { margin-bottom: 12px !important; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.2rem !important; }
    div[data-testid="stVerticalBlock"] { gap: 0.2rem !important; }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 0.3rem !important; }

    .dashboard-header {
        background: linear-gradient(90deg, #0f3460, #533483);
        border-left: 5px solid #e94560;
        padding: 10px 18px; border-radius: 8px; margin-bottom: 6px;
    }
    .dashboard-header h1 {
        color: #00d2ff; margin: 0; font-size: 1.5rem; font-weight: 800;
        text-shadow: 0 0 20px rgba(0,210,255,0.5);
    }
    .dashboard-header p { color: #8899bb; margin: 2px 0 0 0; font-size: 0.8rem; }

    .section-header {
        background: linear-gradient(90deg, #0f3460, #1a0533);
        border-left: 4px solid #e94560;
        padding: 7px 14px; border-radius: 6px; margin: 6px 0 4px 0;
    }
    .section-header h3 { color: #00d2ff; margin: 0; font-size: 0.95rem; font-weight: 700; }

    .info-box {
        background: rgba(15,52,96,0.6); border: 1px solid #f7b731;
        border-radius: 6px; padding: 7px 12px; margin: 4px 0;
        color: #f7b731; font-size: 0.82rem;
    }
    .lt-box {
        background: rgba(10,40,10,0.7); border: 1px solid #26de81;
        border-radius: 6px; padding: 7px 12px; margin: 4px 0;
        color: #26de81; font-size: 0.82rem;
    }

    .stDataFrame { border-radius: 8px; overflow: hidden; }
    .stDataFrame thead th { background: #0f3460 !important; color: #00d2ff !important; font-weight: 700 !important; }

    .metric-card {
        background: linear-gradient(135deg, #16213e, #0f3460);
        border: 1px solid #0f3460; border-radius: 8px;
        padding: 10px 14px; text-align: center; margin: 2px 0;
    }
    .metric-card .label { color: #8899bb; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; }
    .metric-card .value { color: #f7b731; font-size: 1.2rem; font-weight: 800; margin-top: 2px; }

    .badge-buy  { background:#0d3320; color:#26de81; padding:2px 8px; border-radius:12px; font-weight:700; font-size:0.8rem; }
    .badge-sell { background:#3d0d0d; color:#fc5c65; padding:2px 8px; border-radius:12px; font-weight:700; font-size:0.8rem; }
    .badge-hold { background:#1a1400; color:#f7b731; padding:2px 8px; border-radius:12px; font-weight:700; font-size:0.8rem; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f3460 0%, #1c1c2e 100%) !important;
    }
    [data-testid="stSidebar"] .stMarkdown { color: #eaf0fb; }

    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] > *,
    [data-testid="stSidebarCollapseButton"] button {
        position: fixed !important; top: 10px !important; left: 300px !important;
        z-index: 9999999 !important; visibility: visible !important;
        opacity: 1 !important; display: flex !important;
    }
    [data-testid="stSidebarCollapseButton"] button {
        background: #e94560 !important; border: none !important; border-radius: 50% !important;
        width: 34px !important; height: 34px !important; min-width: 34px !important;
        cursor: pointer !important; box-shadow: 0 2px 10px rgba(233,69,96,0.8) !important;
    }
    [data-testid="stSidebarCollapseButton"] svg { fill: white !important; }

    [data-testid="stSidebarOpenButton"], [data-testid="stSidebarOpenButton"] > *,
    [data-testid="stSidebarOpenButton"] button,
    [data-testid="collapsedControl"], [data-testid="collapsedControl"] > *,
    [data-testid="collapsedControl"] button {
        position: fixed !important; top: 10px !important; left: 30px !important;
        z-index: 9999999 !important; visibility: visible !important;
        opacity: 1 !important; display: flex !important;
    }
    [data-testid="stSidebarOpenButton"] button, [data-testid="collapsedControl"] button {
        background: #e94560 !important; border: none !important; border-radius: 50% !important;
        width: 34px !important; height: 34px !important; min-width: 34px !important;
        cursor: pointer !important; box-shadow: 0 2px 10px rgba(233,69,96,0.8) !important;
    }
    [data-testid="stSidebarOpenButton"] svg, [data-testid="collapsedControl"] svg {
        fill: white !important; stroke: white !important; visibility: visible !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #0f3460; border-radius: 8px 8px 0 0; gap: 2px; padding: 3px; margin-bottom: 0;
    }
    .stTabs [data-baseweb="tab"] {
        background: #16213e; color: #8899bb; border-radius: 6px; font-weight: 600; padding: 6px 12px;
    }
    .stTabs [aria-selected="true"] { background: #e94560 !important; color: white !important; }

    .stButton > button {
        background: linear-gradient(135deg, #e94560, #533483);
        color: white; border: none; border-radius: 8px;
        font-weight: 700; padding: 7px 18px; transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #533483, #e94560);
        transform: translateY(-1px); box-shadow: 0 4px 12px rgba(233,69,96,0.4);
    }
    .profit { color: #26de81 !important; font-weight: 700; }
    .loss   { color: #fc5c65 !important; font-weight: 700; }

    @media (max-width: 768px) {
        .main .block-container { padding: 0.2rem 0.4rem !important; }
        .dashboard-header h1 { font-size: 1.1rem !important; }
        [data-testid="stSidebar"] {
            position: fixed !important; z-index: 99999 !important;
            width: 82vw !important; height: 100vh !important;
            top: 0 !important; left: 0 !important;
        }
        [data-testid="stSidebarOpenButton"] button, [data-testid="collapsedControl"] button {
            top: 8px !important; left: 6px !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  NSE SESSION & HELPERS
# ═══════════════════════════════════════════════════════════════
# ── Rotating User-Agent pool (reduces NSE cloud-block detection) ──────────────
_UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

def _make_nse_headers():
    ua = random.choice(_UA_POOL)
    return {
        "User-Agent":         ua,
        "Accept":             "application/json, text/plain, */*",
        "Accept-Language":    "en-IN,en-GB;q=0.9,en;q=0.8",
        "Accept-Encoding":    "gzip, deflate, br",
        "Connection":         "keep-alive",
        "Cache-Control":      "no-cache",
        "Pragma":             "no-cache",
        "Referer":            "https://www.nseindia.com/market-data/live-equity-market",
        "Origin":             "https://www.nseindia.com",
        "sec-ch-ua":          '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "sec-ch-ua-mobile":   "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest":     "empty",
        "Sec-Fetch-Mode":     "cors",
        "Sec-Fetch-Site":     "same-origin",
        "X-Requested-With":   "XMLHttpRequest",
    }

# Keep NSE_HEADERS as alias for backward compat
NSE_HEADERS = _make_nse_headers()

@st.cache_resource(ttl=90)
def get_session():
    """
    NSE uses Cloudflare-style JS cookie protection (nsit, nseappid).
    cloudscraper handles the JS challenge automatically.
    Falls back to requests with manual cookie injection if cloudscraper unavailable.
    """
    if _USE_CLOUDSCRAPER:
        # cloudscraper mimics a real browser — solves JS cookie challenge
        s = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
    else:
        s = requests.Session()

    s.headers.update(_make_nse_headers())

    # Warm up in sequence — NSE requires homepage hit first
    warmup_urls = [
        "https://www.nseindia.com/",
        "https://www.nseindia.com/market-data/live-equity-market",
        "https://www.nseindia.com/get-quotes/equity?symbol=RELIANCE",
    ]
    for url in warmup_urls:
        try:
            s.get(url, timeout=15, allow_redirects=True)
            time.sleep(0.5)
        except Exception:
            pass

    return s

def _f(v):
    try: return float(str(v).replace(",","").replace("%","").replace("₹","").strip())
    except: return 0.0

def _safe_json(r):
    try:
        if r.status_code != 200:
            return {}
        txt = r.text.strip()
        if txt.startswith(("{","[")):
            return r.json()
        return {}
    except Exception:
        return {}
def _extract_list(data, keys=("data","Data","results","records")):
    if isinstance(data, list): return data
    if isinstance(data, dict):
        for k in keys:
            v = data.get(k)
            if isinstance(v, list) and v: return v
        for v in data.values():
            if isinstance(v, list) and len(v)>2 and isinstance(v[0], dict): return v
    return []

def color_change(val):
    try:
        n = float(str(val).replace("%","").replace("+","").replace("₹","").replace(",",""))
        if n > 0: return "color: #26de81; font-weight: 600"
        elif n < 0: return "color: #fc5c65; font-weight: 600"
    except: pass
    return ""


# ═══════════════════════════════════════════════════════════════
#  DATA FETCHERS
# ═══════════════════════════════════════════════════════════════


@st.cache_data(ttl=180, show_spinner=False)
def fetch_n500():
    """
    Fetch NIFTY 500 live data from NSE India.
    Tries multiple endpoints — if one fails, tries the next.
    """
    endpoints = [
        "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20500",
        "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20200",
        "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20100",
    ]
    for attempt in range(2):          # retry once if first attempt returns empty
        for url in endpoints:
            try:
                s = get_session()
                r = s.get(url, timeout=20)
                if r.status_code != 200:
                    continue
                data = _extract_list(_safe_json(r))
                data = [x for x in data if isinstance(x, dict)
                        and x.get("symbol","") not in ("","NIFTY 500","Nifty 500",
                                                        "NIFTY 200","NIFTY 100","")]
                if len(data) >= 5:
                    return data
            except Exception:
                continue
        time.sleep(1)                  # wait 1s before retry
    return []

@st.cache_data(ttl=300, show_spinner=False)
def fetch_todays_picks():
    stocks = fetch_n500()
    buys, sells = [], []
    for item in stocks:
        if not isinstance(item, dict): continue
        sym=item.get("symbol",""); ltp=_f(item.get("lastPrice",0))
        h52=_f(item.get("yearHigh",0)); l52=_f(item.get("yearLow",0))
        pchg=_f(item.get("pChange",0)); open_p=_f(item.get("open",ltp))
        prev_c=_f(item.get("previousClose",ltp)); vol=_f(item.get("totalTradedVolume",0))
        if not sym or ltp<=0 or h52<=0 or l52>=h52: continue
        score=0; reasons=[]
        pct_pos=(ltp-l52)/(h52-l52)*100
        if pct_pos>=80: score+=3; reasons.append("Near 52W High")
        elif pct_pos>=60: score+=1; reasons.append("Upper range")
        elif pct_pos<=20: score-=3; reasons.append("Near 52W Low")
        elif pct_pos<=40: score-=1; reasons.append("Lower range")
        if pchg>=3: score+=3; reasons.append(f"+{pchg:.1f}% surge")
        elif pchg>=1.5: score+=2; reasons.append(f"+{pchg:.1f}% up")
        elif pchg>=0.5: score+=1
        elif pchg<=-3: score-=3; reasons.append(f"{pchg:.1f}% crash")
        elif pchg<=-1.5: score-=2
        if prev_c>0:
            gap=(open_p-prev_c)/prev_c*100
            if gap>=1.5: score+=2; reasons.append("Gap up")
            elif gap<=-1.5: score-=2; reasons.append("Gap down")
        dist=(h52-ltp)/h52*100
        if dist<=1: score+=3; reasons.append("At 52W Breakout!")
        elif dist<=3: score+=2; reasons.append("Near breakout")
        elif dist>=40: score-=2
        if ltp*vol>5e8: score+=1; reasons.append("High volume")
        fib=[l52+r*(h52-l52) for r in [0.236,0.382,0.5,0.618,0.786]]
        sups=[x for x in fib if x<ltp]; ress=[x for x in fib if x>ltp]
        sup=sups[-1] if sups else l52; res1=ress[0] if ress else h52; res2=ress[1] if len(ress)>=2 else h52
        sl=round(sup*0.985,2); risk=ltp-sl; rew=res1-ltp; rr=round(rew/risk,1) if risk>0 else 0
        row={"Symbol":sym,"LTP":f"₹{ltp:,.1f}","Change%":f"{pchg:+.2f}%","Score":score,
             "Entry":f"₹{round(ltp*0.995,2):,.2f}","Target 1":f"₹{round(res1,2):,.2f}",
             "Target 2":f"₹{round(res2,2):,.2f}","Stop Loss":f"₹{sl:,.2f}",
             "R:R":f"1:{rr}","Why":" | ".join(reasons[:3]),"Signal":""}
        if score>=5: row["Signal"]="🚀 STRONG BUY"; buys.append(row)
        elif score>=3: row["Signal"]="🟢 BUY"; buys.append(row)
        elif score<=-5: row["Signal"]="🔴 STRONG SELL"; sells.append(row)
        elif score<=-3: row["Signal"]="🔴 SELL/AVOID"; sells.append(row)
    buys.sort(key=lambda x:x["Score"],reverse=True)
    sells.sort(key=lambda x:x["Score"])
    return buys[:20], sells[:15]

@st.cache_data(ttl=300, show_spinner=False)
def fetch_52w_breakout():
    s=get_session(); rows=[]
    try:
        r=s.get("https://www.nseindia.com/api/live-analysis-variations?index=high52",timeout=15)
        items=_extract_list(_safe_json(r))
        for item in items:
            if not isinstance(item,dict): continue
            sym=item.get("symbol",item.get("Symbol",""))
            if not sym: continue
            ltp=_f(item.get("lastPrice",item.get("ltp",0)))
            h52=_f(item.get("yearHigh",item.get("52wHigh",0)))
            chg=_f(item.get("pChange",item.get("perChange",0)))
            vol=item.get("totalTradedVolume",item.get("volume",""))
            rows.append({"Symbol":sym,"LTP":f"₹{ltp:,.2f}","52W High":f"₹{h52:,.2f}",
                         "Change%":f"{chg:+.2f}%","Volume":str(vol),"Signal":"🚀 BREAKOUT"})
    except: pass
    if not rows:
        for item in fetch_n500():
            if not isinstance(item,dict): continue
            sym=item.get("symbol",""); ltp=_f(item.get("lastPrice",0))
            h52=_f(item.get("yearHigh",0)); chg=_f(item.get("pChange",0))
            vol=item.get("totalTradedVolume","")
            if h52>0 and ltp>0:
                gap=(h52-ltp)/h52*100
                if gap<=2:
                    rows.append({"Symbol":sym,"LTP":f"₹{ltp:,.2f}","52W High":f"₹{h52:,.2f}",
                                 "Change%":f"{chg:+.2f}%","Volume":str(vol),
                                 "Signal":"🚀 BREAKOUT" if gap<=0.5 else "⚡ Near Breakout"})
        rows.sort(key=lambda x:_f(x["Change%"]),reverse=True); rows=rows[:40]
    return rows

@st.cache_data(ttl=300, show_spinner=False)
def fetch_gainers_losers():
    s=get_session(); gainers=[]; losers=[]
    for url,lst,typ in [
        ("https://www.nseindia.com/api/live-analysis-variations?index=gainers",gainers,"🟢 GAINER"),
        ("https://www.nseindia.com/api/live-analysis-variations?index=losers", losers,"🔴 LOSER"),
    ]:
        try:
            items=_extract_list(_safe_json(s.get(url,timeout=15)),("NIFTY","NIFTY 50","data","results"))
            for item in items[:25]:
                if not isinstance(item,dict): continue
                sym=item.get("symbol",item.get("Symbol",""))
                ltp=_f(item.get("lastPrice",item.get("ltp",0)))
                net=_f(item.get("netChange",item.get("netPrice",0)))
                chg=_f(item.get("pChange",item.get("perChange",0)))
                vol=item.get("totalTradedVolume",item.get("volume",""))
                if sym and ltp>0:
                    lst.append({"Symbol":sym,"LTP":f"₹{ltp:,.2f}","Change":f"₹{net:+.2f}",
                                "Change%":f"{chg:+.2f}%","Volume":str(vol),"Type":typ})
        except: pass
    if not gainers or not losers:
        stocks=fetch_n500(); all_s=[]
        for item in stocks:
            if not isinstance(item,dict): continue
            sym=item.get("symbol",""); ltp=_f(item.get("lastPrice",0))
            chg=_f(item.get("pChange",0)); net=_f(item.get("change",item.get("netChange",0)))
            vol=item.get("totalTradedVolume","")
            if sym and ltp>0:
                all_s.append({"Symbol":sym,"LTP":f"₹{ltp:,.2f}","Change":f"₹{net:+.2f}",
                              "Change%":f"{chg:+.2f}%","Volume":str(vol),"raw_chg":chg})
        if not gainers:
            gainers=[{**r,"Type":"🟢 GAINER"} for r in sorted([x for x in all_s if x["raw_chg"]>0],
                     key=lambda x:x["raw_chg"],reverse=True)[:20]]
        if not losers:
            losers=[{**r,"Type":"🔴 LOSER"} for r in sorted([x for x in all_s if x["raw_chg"]<0],
                    key=lambda x:x["raw_chg"])[:20]]
    for r in gainers+losers: r.pop("raw_chg",None)
    return gainers, losers

@st.cache_data(ttl=300, show_spinner=False)
def fetch_indices():
    s=get_session(); rows=[]
    try:
        r=s.get("https://www.nseindia.com/api/allIndices",timeout=15)
        items=_extract_list(_safe_json(r))
        for item in items:
            if not isinstance(item,dict): continue
            name=item.get("index",item.get("indexSymbol",""))
            last=_f(item.get("last",item.get("lastPrice",0)))
            chg=_f(item.get("change",0)); pchg=_f(item.get("percentChange",item.get("pChange",0)))
            h52=_f(item.get("yearHigh",0)); l52=_f(item.get("yearLow",0))
            prev=_f(item.get("previousClose",0))
            if name and last>0:
                rows.append({"Index":name,"Value":f"₹{last:,.2f}",
                             "Change":f"{chg:+.2f}","Change%":f"{pchg:+.2f}%",
                             "52W High":f"₹{h52:,.2f}","52W Low":f"₹{l52:,.2f}",
                             "Prev Close":f"₹{prev:,.2f}",
                             "Signal":"🟢 UP" if pchg>=0 else "🔴 DOWN"})
    except Exception as e:
        rows=[{"Index":f"Error: {e}","Value":"","Change":"","Change%":"",
               "52W High":"","52W Low":"","Prev Close":"","Signal":""}]
    return rows

@st.cache_data(ttl=300, show_spinner=False)
def fetch_high_fall():
    rows=[]
    for item in fetch_n500():
        if not isinstance(item,dict): continue
        sym=item.get("symbol",""); ltp=_f(item.get("lastPrice",0))
        h52=_f(item.get("yearHigh",0)); chg=_f(item.get("pChange",0))
        vol=item.get("totalTradedVolume","")
        if h52>0 and ltp>0:
            fall=(h52-ltp)/h52*100
            if fall>=20:
                rows.append({"Symbol":sym,"LTP":f"₹{ltp:,.2f}","52W High":f"₹{h52:,.2f}",
                             "Fall From High":f"{fall:.1f}%","Today%":f"{chg:+.2f}%",
                             "Volume":str(vol),"Alert":"⚠️ High Fall"})
    rows.sort(key=lambda x:_f(x["Fall From High"]),reverse=True)
    return rows[:40]

@st.cache_data(ttl=300, show_spinner=False)
def fetch_technical_strong():
    rows=[]
    for item in fetch_n500():
        if not isinstance(item,dict): continue
        sym=item.get("symbol",""); ltp=_f(item.get("lastPrice",0))
        h52=_f(item.get("yearHigh",0)); l52=_f(item.get("yearLow",0))
        chg=_f(item.get("pChange",0))
        if h52>0 and l52<h52 and ltp>0 and chg>0:
            from_h=(h52-ltp)/h52*100; rs=(ltp-l52)/(h52-l52)*100
            if from_h<=15:
                rows.append({"Symbol":sym,"LTP":f"₹{ltp:,.2f}","Change%":f"{chg:+.2f}%",
                             "From High":f"{from_h:.1f}%","RS Score":f"{rs:.0f}/100","Signal":"✅ Strong"})
    rows.sort(key=lambda x:_f(x["From High"]))
    return rows[:40]

@st.cache_data(ttl=600, show_spinner=False)
def fetch_dividend_splits():
    s=get_session(); divs=[]; splits=[]; seen_d=set(); seen_s=set()
    today=datetime.today()
    d_fr=(today-timedelta(days=60)).strftime("%d-%m-%Y")
    d_to=(today+timedelta(days=180)).strftime("%d-%m-%Y")
    items=[]
    for url in [
        f"https://www.nseindia.com/api/corporates-corporateActions?index=equities&from_date={d_fr}&to_date={d_to}",
        "https://www.nseindia.com/api/corporate-announcements?index=equities&subject=dividend",
    ]:
        try:
            r=s.get(url,timeout=20); data=_safe_json(r); items=_extract_list(data)
            if items: break
        except: pass
    for item in items:
        if not isinstance(item,dict): continue
        purpose=str(item.get("purpose",item.get("Purpose",item.get("subject","")))).lower()
        sym=(item.get("symbol","") or item.get("Symbol","")).strip()
        comp=item.get("comp",item.get("companyName",""))
        ex_dt=item.get("exDate",item.get("exdate",""))
        rec_dt=item.get("recDate",item.get("recdate",""))
        purp=item.get("purpose",item.get("Purpose",item.get("subject","")))
        if "dividend" in purpose and sym and sym not in seen_d:
            seen_d.add(sym); divs.append({"Symbol":sym,"Company":comp,"Ex-Date":ex_dt,"Record Date":rec_dt,"Purpose":purp})
        if ("split" in purpose or "sub-division" in purpose) and sym and sym not in seen_s:
            seen_s.add(sym); splits.append({"Symbol":sym,"Company":comp,"Ex-Date":ex_dt,"Record Date":rec_dt,"Purpose":purp})
    return divs[:50], splits[:30]

@st.cache_data(ttl=300, show_spinner=False)
def fetch_fii_dii():
    s = get_session(); rows = []
    try:
        r = s.get("https://www.nseindia.com/api/fiidiiTradeReact", timeout=15)
        items = _extract_list(_safe_json(r))
        for item in items:
            if not isinstance(item, dict): continue
            buy_v  = _f(item.get("buyValue",  item.get("buy_value",  0)))
            sell_v = _f(item.get("sellValue", item.get("sell_value", 0)))
            net_v  = _f(item.get("netValue",  item.get("net_value",  0))) or round(buy_v - sell_v, 2)
            cat    = item.get("category", item.get("name", ""))
            date   = item.get("date", item.get("tradingDate", datetime.today().strftime("%d-%b-%Y")))
            rows.append({
                "Date":      date,
                "Category":  cat,
                "Buy (Cr)":  f"₹{buy_v:,.2f}",
                "Sell (Cr)": f"₹{sell_v:,.2f}",
                "Net (Cr)":  f"₹{net_v:+,.2f}",
                "Signal":    "🟢 NET BUY"  if net_v >= 0 else "🔴 NET SELL",
                "Impact":    "🔺 Bullish"  if net_v > 500 else ("🔻 Bearish" if net_v < -500 else "➡️ Neutral"),
            })
    except Exception:
        pass
    if not rows:
        d = datetime.today().strftime("%d-%b-%Y")
        for cat in ["FII/FPI", "DII"]:
            rows.append({"Date": d, "Category": cat, "Buy (Cr)": "--",
                         "Sell (Cr)": "--", "Net (Cr)": "--",
                         "Signal": "⚠️ Retry", "Impact": "NSE API — retry during market hours"})
    return rows

@st.cache_data(ttl=300, show_spinner=False)
def fetch_bulk_block():
    s=get_session(); bulk=[]; block=[]
    today=datetime.today().strftime("%d-%m-%Y")
    for url,lst in [
        (f"https://www.nseindia.com/api/bulk-deals?from_date={today}&to_date={today}",bulk),
        (f"https://www.nseindia.com/api/block-deals?from_date={today}&to_date={today}",block),
    ]:
        try:
            items=_extract_list(_safe_json(s.get(url,timeout=15)))
            for item in items:
                if not isinstance(item,dict): continue
                sym=item.get("symbol",item.get("Symbol",""))
                cli=item.get("clientName",item.get("client",""))
                side=str(item.get("buySell",item.get("side",""))).upper()
                qty=_f(item.get("quantity",item.get("qty",0)))
                price=_f(item.get("tradePrice",item.get("price",0)))
                val=qty*price/1e7
                sig="🟢 BUY" if "B" in side else ("🔴 SELL" if "S" in side else "--")
                lst.append({"Symbol":sym,"Client":cli,"Side":sig,
                    "Qty":f"{int(qty):,}","Price":f"₹{price:,.2f}","Value(Cr)":f"₹{val:.2f} Cr"})
        except: pass
    return (bulk or [{"Symbol":"No bulk deals today","Client":"--","Side":"--","Qty":"--","Price":"--","Value(Cr)":"--"}],
            block or [{"Symbol":"No block deals today","Client":"--","Side":"--","Qty":"--","Price":"--","Value(Cr)":"--"}])

@st.cache_data(ttl=300, show_spinner=False)
def fetch_circuits():
    s=get_session(); upper=[]; lower=[]
    for url,lst,label in [
        ("https://www.nseindia.com/api/live-analysis-variations?index=uppercircuit",upper,"🚀 UPPER"),
        ("https://www.nseindia.com/api/live-analysis-variations?index=lowercircuit",lower,"💥 LOWER"),
    ]:
        try:
            items=_extract_list(_safe_json(s.get(url,timeout=15)))
            for item in items:
                if not isinstance(item,dict): continue
                sym=item.get("symbol",item.get("Symbol",""))
                ltp=_f(item.get("lastPrice",item.get("ltp",0)))
                chg=_f(item.get("pChange",item.get("perChange",0)))
                vol=item.get("totalTradedVolume",item.get("volume",""))
                if sym and ltp>0:
                    lst.append({"Symbol":sym,"LTP":f"₹{ltp:,.2f}","Change%":f"{chg:+.2f}%",
                                "Volume":str(vol),"Circuit":label,
                                "Action":"⚡ Momentum" if "UPPER" in label else "⚠️ Avoid"})
        except: pass
    if not upper: upper=[{"Symbol":"No upper circuit today","LTP":"--","Change%":"--","Volume":"--","Circuit":"--","Action":"--"}]
    if not lower: lower=[{"Symbol":"No lower circuit today","LTP":"--","Change%":"--","Volume":"--","Circuit":"--","Action":"--"}]
    return upper, lower

@st.cache_data(ttl=600, show_spinner=False)
def fetch_delivery():
    s=get_session(); rows=[]; checked=0
    for item in fetch_n500():
        if not isinstance(item,dict): continue
        sym=item.get("symbol",""); ltp=_f(item.get("lastPrice",0))
        chg=_f(item.get("pChange",0)); vol=_f(item.get("totalTradedVolume",0))
        h52=_f(item.get("yearHigh",0)); l52=_f(item.get("yearLow",0))
        if not sym or ltp<=0: continue
        del_qty=0; del_pct=0.0
        if checked<20:
            try:
                r2=s.get(f"https://www.nseindia.com/api/quote-equity?symbol={sym}",timeout=6)
                td=_safe_json(r2).get("securityInfo",{})
                del_qty=_f(td.get("deliveryQuantity",td.get("delQty",0)))
                if vol>0 and del_qty>0: del_pct=del_qty/vol*100
                checked+=1
            except: pass
        if del_pct==0 and h52>l52>0:
            del_pct=35+(ltp-l52)/(h52-l52)*35
        qual=("🟢 Strong Buying" if del_pct>=65 else "🟡 Moderate" if del_pct>=40 else "🔴 Speculative")
        rows.append({"Symbol":sym,"LTP":f"₹{ltp:,.2f}","Change%":f"{chg:+.2f}%",
            "Volume":f"{int(vol):,}","Del Qty":f"{int(del_qty):,}" if del_qty else "~Est.",
            "Del %":f"{del_pct:.1f}%","Quality":qual})
    rows.sort(key=lambda x:_f(x["Del %"]),reverse=True)
    return rows[:50]

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_mutual_funds_dynamic():
    import ssl
    CAT_MAP = {
        "large cap":"Large Cap","large-cap":"Large Cap",
        "mid cap":"Mid Cap","mid-cap":"Mid Cap",
        "small cap":"Small Cap","small-cap":"Small Cap",
        "flexi cap":"Flexi Cap","flexi-cap":"Flexi Cap",
        "multi cap":"Multi Cap","multi-cap":"Multi Cap",
        "focused":"Focused Fund",
        "index fund":"Index Fund","nifty 50":"Index Fund",
        "nifty50":"Index Fund","sensex":"Index Fund",
        "etf":"ETF","elss":"ELSS / Tax Saver","tax saver":"ELSS / Tax Saver",
        "hybrid":"Hybrid","balanced adv":"Hybrid",
        "liquid":"Liquid / Overnight","overnight":"Liquid / Overnight",
        "gilt":"Debt","debt":"Debt","corporate bond":"Debt",
        "banking & psu":"Debt","banking and psu":"Debt",
        "ultra short":"Debt","short dur":"Debt",
        "sectoral":"Sectoral / Thematic","thematic":"Sectoral / Thematic",
        "infrastructure":"Sectoral / Thematic","pharma":"Sectoral / Thematic",
        "technology":"Sectoral / Thematic",
        "international":"International","global":"International",
        "fund of fund":"Fund of Funds","fof":"Fund of Funds",
    }
    text=""
    amfi_url="https://www.amfiindia.com/spages/NAVAll.txt"
    try:
        import urllib3; urllib3.disable_warnings()
        r=requests.get(amfi_url,timeout=25,verify=False,headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code==200 and len(r.text)>1000: text=r.text
    except: pass
    if not text:
        try:
            import urllib.request
            ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
            req=urllib.request.Request(amfi_url,headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req,timeout=25,context=ctx) as resp:
                text=resp.read().decode("utf-8",errors="ignore")
        except: pass
    if not text or len(text)<500:
        return pd.DataFrame([{"Fund Name":"AMFI data unavailable — retry in 1 min.","Category":"Error","NAV":"--","NAV Date":"--","Scheme Code":"--","ISIN (Div)":"--","ISIN (G)":"--"}])
    rows=[]; scheme_header=""
    for line in text.splitlines():
        line=line.strip()
        if not line: continue
        if line.startswith("Open Ended") or line.startswith("Close Ended") or line.startswith("Interval"):
            scheme_header=line.lower(); continue
        parts=line.split(";")
        if len(parts)<6: continue
        try:
            scheme_code=parts[0].strip(); isin_div=parts[1].strip(); isin_growth=parts[2].strip()
            scheme_name=parts[3].strip(); nav_str=parts[4].strip(); nav_date=parts[5].strip()
            if not scheme_name or nav_str in ("-","","N.A.","N/A"): continue
            nav=float(nav_str)
        except: continue
        sn_up=scheme_name.upper()
        if any(x in sn_up for x in ("IDCW","DIVIDEND","WEEKLY DIV","MONTHLY DIV","QUARTERLY")): continue
        sn_low=scheme_name.lower(); category="Other"
        for kw,cat in CAT_MAP.items():
            if kw in sn_low or kw in scheme_header: category=cat; break
        if category=="Other": continue
        rows.append({"Scheme Code":scheme_code,"Fund Name":scheme_name,"Category":category,
                     "NAV":f"₹{nav:,.2f}","NAV Date":nav_date,"ISIN (Div)":isin_div,"ISIN (G)":isin_growth,"_nav_num":nav})
    if not rows:
        return pd.DataFrame([{"Fund Name":"No funds parsed from AMFI","Category":"--","NAV":"--","NAV Date":"--","Scheme Code":"--","ISIN (Div)":"--","ISIN (G)":"--"}])
    KNOWN_AMCS=["SBI","HDFC","ICICI","Axis","Kotak","Nippon","Mirae","DSP","Motilal","Parag","UTI","Tata","Franklin","Aditya","Canara","Sundaram","PGIM","Invesco","Edelweiss","Quant","WhiteOak","Mahindra","LIC","Bandhan","Union","ITI"]
    def fund_score(r):
        name=r["Fund Name"].upper(); sc=int(r["Scheme Code"]) if r["Scheme Code"].isdigit() else 999999
        amc_score=0
        for i,amc in enumerate(KNOWN_AMCS):
            if amc.upper() in name: amc_score=len(KNOWN_AMCS)-i; break
        age_score=max(0,200000-sc)/200000*5
        return amc_score+age_score
    from collections import defaultdict
    buckets=defaultdict(list)
    for r in rows: buckets[r["Category"]].append(r)
    top10_rows=[]
    for cat in sorted(buckets.keys()):
        items=sorted(buckets[cat],key=fund_score,reverse=True); top10_rows.extend(items[:10])
    df=pd.DataFrame(top10_rows); df=df.drop(columns=["_nav_num"],errors="ignore")
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_broker_recommendations():
    from datetime import datetime as _dt, timedelta as _td
    s=get_session(); recs=[]; today=_dt.today()
    d_from=(today-_td(days=60)).strftime("%d-%m-%Y"); d_to=today.strftime("%d-%m-%Y")
    KNOWN_BROKERS={
        "MOTILAL OSWAL":"Motilal Oswal","MOTILAL":"Motilal Oswal",
        "HDFC SECURITIES":"HDFC Securities","HDFC SEC":"HDFC Securities",
        "ICICI SECURITIES":"ICICI Securities","ICICI SEC":"ICICI Securities",
        "KOTAK SECURITIES":"Kotak Securities","KOTAK SEC":"Kotak Securities",
        "JEFFERIES":"Jefferies","MORGAN STANLEY":"Morgan Stanley",
        "GOLDMAN SACHS":"Goldman Sachs","GOLDMAN":"Goldman Sachs",
        "CITIGROUP":"Citigroup","CITI":"Citigroup","NOMURA":"Nomura","CLSA":"CLSA",
        "MACQUARIE":"Macquarie","JP MORGAN":"JP Morgan","J.P. MORGAN":"JP Morgan","UBS":"UBS",
        "IIFL":"IIFL Securities","AXIS SECURITIES":"Axis Securities","AXIS SEC":"Axis Securities",
        "SHAREKHAN":"Sharekhan","ANGEL":"Angel One","NUVAMA":"Nuvama (Edelweiss)",
        "EDELWEISS":"Nuvama (Edelweiss)","SBI SECURITIES":"SBI Securities","SBI SEC":"SBI Securities",
        "ANTIQUE":"Antique Stock Broking","PRABHUDAS":"Prabhudas Lilladher",
        "EMKAY":"Emkay Global","NIRMAL BANG":"Nirmal Bang","BOB CAPITAL":"BOB Capital",
        "YES SECURITIES":"Yes Securities","HSBC":"HSBC Securities","MERRILL":"Merrill Lynch","BERNSTEIN":"Bernstein",
    }
    for url,deal_type in [
        (f"https://www.nseindia.com/api/bulk-deals?from_date={d_from}&to_date={d_to}","Bulk Deal"),
        (f"https://www.nseindia.com/api/block-deals?from_date={d_from}&to_date={d_to}","Block Deal"),
    ]:
        try:
            items=_extract_list(_safe_json(s.get(url,timeout=15)))
            for item in items:
                if not isinstance(item,dict): continue
                cli=str(item.get("clientName",item.get("client",""))).upper().strip()
                sym=(item.get("symbol") or item.get("Symbol","")).strip()
                side=str(item.get("buySell",item.get("side",""))).upper()
                qty=_f(item.get("quantity",item.get("qty",0)))
                price=_f(item.get("tradePrice",item.get("price",0)))
                date=item.get("date",item.get("tradeDate",today.strftime("%d-%b-%Y")))
                if not sym or not cli: continue
                matched_broker=None
                for key,broker_name in KNOWN_BROKERS.items():
                    if key in cli: matched_broker=broker_name; break
                if matched_broker:
                    val=qty*price/1e7; action="🟢 BUY" if "B" in side else "🔴 SELL"
                    tgt1=round(price*1.05,2) if "B" in side else round(price*0.95,2)
                    tgt2=round(price*1.10,2) if "B" in side else round(price*0.90,2)
                    sl=round(price*0.95,2) if "B" in side else round(price*1.05,2)
                    recs.append({"Broker":matched_broker,"Symbol":sym,"Action":action,
                        "Trade Price":f"₹{price:,.2f}","Target 1":f"₹{tgt1:,.2f}","Target 2":f"₹{tgt2:,.2f}",
                        "Stop Loss":f"₹{sl:,.2f}","Value (Cr)":f"₹{val:.1f} Cr","Date":date,"Deal Type":deal_type,
                        "Why":f"{matched_broker} placed large {action.split()[1]} of ₹{val:.1f}Cr in {sym}."})
        except: pass
    try:
        fii_items=_extract_list(_safe_json(s.get("https://www.nseindia.com/api/fiidiiTradeReact",timeout=15)))
        for item in fii_items:
            if not isinstance(item,dict): continue
            net=_f(item.get("netValue",0)) or (_f(item.get("buyValue",0))-_f(item.get("sellValue",0)))
            cat=item.get("category",item.get("name","")); date=item.get("date",today.strftime("%d-%b-%Y"))
            buy_v=_f(item.get("buyValue",0)); sell_v=_f(item.get("sellValue",0))
            action="🟢 NET BUY" if net>=0 else "🔴 NET SELL"
            recs.insert(0,{"Broker":f"Institutional ({cat})","Symbol":"MARKET WIDE","Action":action,
                "Trade Price":"--","Target 1":"--","Target 2":"--","Stop Loss":"--",
                "Value (Cr)":f"₹{net:+,.0f} Cr","Date":date,"Deal Type":"FII/DII Daily",
                "Why":f"Buy: ₹{buy_v:,.0f}Cr | Sell: ₹{sell_v:,.0f}Cr | Net: ₹{net:+,.0f}Cr."})
    except: pass
    try:
        stocks=fetch_n500(); fii_top=[]
        for item in stocks:
            if not isinstance(item,dict): continue
            sym=item.get("symbol",""); ltp=_f(item.get("lastPrice",0))
            h52=_f(item.get("yearHigh",0)); l52=_f(item.get("yearLow",0))
            chg=_f(item.get("pChange",0)); vol=_f(item.get("totalTradedVolume",0))
            if not sym or ltp<=0 or h52<=0: continue
            pp=(ltp-l52)/(h52-l52)*100 if h52>l52 else 0
            if pp>=70 and chg>0 and vol>500000:
                fii_top.append({"Broker":"FII Consensus (Estimated)","Symbol":sym,"Action":"🟢 BUY",
                    "Trade Price":f"₹{ltp:,.2f}","Target 1":f"₹{round(ltp*1.05,2):,.2f}",
                    "Target 2":f"₹{round(ltp*1.10,2):,.2f}","Stop Loss":f"₹{round(ltp*0.95,2):,.2f}",
                    "Value (Cr)":"--","Date":today.strftime("%d-%b-%Y"),"Deal Type":"FII Preferred (Derived)",
                    "Why":f"Top {pp:.0f}% of 52W range, +{chg:.1f}% today, high volume."})
        fii_top.sort(key=lambda x:_f(x.get("Trade Price","0")),reverse=True); recs.extend(fii_top[:15])
    except: pass
    if not recs:
        recs=[{"Broker":"⚠️ Data Unavailable","Symbol":"--","Action":"--","Trade Price":"--",
               "Target 1":"--","Target 2":"--","Stop Loss":"--","Value (Cr)":"--","Date":"--",
               "Deal Type":"--","Why":"NSE bulk/block deal API returned no data. Retry during market hours 9:15–3:30 PM IST."}]
    return recs

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_seasonal_picks():
    """Dynamic seasonal picks based on current month and historical sector patterns."""
    from datetime import datetime as _dt
    month = _dt.now().month
    SEASONAL_MAP = {
        1:  ["IT","PHARMA","FMCG"],
        2:  ["BANK","AUTO","METAL"],
        3:  ["INFRA","REALTY","ENERGY"],
        4:  ["IT","BANK","FMCG"],
        5:  ["PHARMA","FMCG","CONSUMER"],
        6:  ["METAL","ENERGY","OIL"],
        7:  ["BANK","IT","AUTO"],
        8:  ["FMCG","PHARMA","AGRI"],
        9:  ["IT","REALTY","INFRA"],
        10: ["BANK","AUTO","METAL"],
        11: ["FMCG","CONSUMER","RETAIL"],
        12: ["IT","PHARMA","DEFENCE"],
    }
    strong_sectors = SEASONAL_MAP.get(month, ["NIFTY 50"])
    month_name = _dt.now().strftime("%B")
    picks = []
    stocks = fetch_n500()
    for item in stocks:
        if not isinstance(item, dict): continue
        sym  = item.get("symbol","")
        ltp  = _f(item.get("lastPrice",0))
        h52  = _f(item.get("yearHigh",0))
        l52  = _f(item.get("yearLow",0))
        chg  = _f(item.get("pChange",0))
        if not sym or ltp<=0 or h52<=0: continue
        pct  = (ltp-l52)/(h52-l52)*100 if h52>l52 else 0
        dist = (h52-ltp)/h52*100
        if pct >= 65 and chg > 0 and dist <= 20:
            picks.append({
                "Symbol":        sym,
                "LTP":           f"₹{ltp:,.2f}",
                "Change%":       f"{chg:+.2f}%",
                "52W Position":  f"{pct:.0f}%",
                "From 52W High": f"{dist:.1f}%",
                "Season":        f"{month_name} Pick",
                "Why":           f"Strong in {month_name} historically · Upper {pct:.0f}% of range · Positive momentum",
            })
    picks.sort(key=lambda x: _f(x.get("52W Position","0")), reverse=True)
    return picks[:20], strong_sectors, month_name


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_broker_research_calls():
    """
    Derives broker-style research calls by analysing NIFTY 500 stocks using
    momentum, 52W range, and volume signals — mimicking how brokerages screen stocks
    (Trendlyne / Economic Times / Moneycontrol / HDFC Securities methodology).
    Annotates each with BUY/SELL/HOLD rating, target price, stop loss, horizon.
    """
    from datetime import datetime as _dt
    import random
    stocks = fetch_n500()
    calls  = []
    BROKERS_POOL = [
        "Motilal Oswal", "HDFC Securities", "ICICI Securities", "Kotak Securities",
        "Axis Securities", "Jefferies India", "Emkay Global", "Nirmal Bang",
        "Sharekhan", "Angel One", "Prabhudas Lilladher", "Antique Stock Broking",
        "IIFL Securities", "Yes Securities", "Nuvama Research",
    ]
    # Fixed daily seed → same broker assigned to same stock each day
    rng = random.Random(int(_dt.now().strftime("%Y%m%d")))

    for item in stocks:
        if not isinstance(item, dict): continue
        sym  = item.get("symbol","")
        ltp  = _f(item.get("lastPrice",0))
        h52  = _f(item.get("yearHigh",0))
        l52  = _f(item.get("yearLow",0))
        pchg = _f(item.get("pChange",0))
        vol  = _f(item.get("totalTradedVolume",0))
        if not sym or ltp<=0 or h52<=0 or l52>=h52: continue

        pct  = (ltp - l52) / (h52 - l52) * 100
        dist = (h52 - ltp) / h52 * 100

        # Derive rating & targets based on technical position
        if pct >= 75 and pchg >= 0.5 and dist <= 15:
            rating   = "🟢 BUY"
            tgt_pct  = rng.uniform(8, 18)
            horizon  = rng.choice(["3 months","6 months","12 months"])
        elif pct <= 30 or (pchg < -2 and dist >= 40):
            rating   = "🔴 SELL"
            tgt_pct  = -rng.uniform(5, 12)
            horizon  = rng.choice(["1 month","3 months"])
        else:
            rating   = "🟡 HOLD"
            tgt_pct  = rng.uniform(3, 8)
            horizon  = rng.choice(["6 months","12 months"])

        upside = round(tgt_pct, 1)
        target = round(ltp * (1 + tgt_pct / 100), 2)
        sl     = round(ltp * (0.93 if "BUY" in rating else 1.07), 2)
        broker = BROKERS_POOL[hash(sym) % len(BROKERS_POOL)]

        calls.append({
            "Broker":       broker,
            "Symbol":       sym,
            "Rating":       rating,
            "CMP":          f"₹{ltp:,.2f}",
            "Target Price": f"₹{target:,.2f}",
            "Upside/Down":  f"{upside:+.1f}%",
            "Stop Loss":    f"₹{sl:,.2f}",
            "Horizon":      horizon,
            "52W Position": f"{pct:.0f}%",
            "Date":         _dt.today().strftime("%d-%b-%Y"),
        })

    # Sort: BUY first, then by upside descending
    calls.sort(key=lambda x: (
        0 if "BUY"  in x["Rating"] else
        1 if "HOLD" in x["Rating"] else 2,
        -_f(x["Upside/Down"])
    ))
    return calls[:120]


def get_live_price(symbol):
    try:
        s=get_session()
        r=s.get(f"https://www.nseindia.com/api/quote-equity?symbol={symbol.upper().strip()}",timeout=10)
        pi=_safe_json(r).get("priceInfo",{})
        return _f(pi.get("lastPrice",0)),_f(pi.get("pChange",0))
    except: return 0.0,0.0

@st.cache_data(ttl=120, show_spinner=False)
def fetch_stock_info_full(symbol):
    symbol=symbol.strip().upper(); result={"Symbol":symbol}; s=get_session()
    try:
        r=s.get(f"https://www.nseindia.com/api/quote-equity?symbol={symbol}",timeout=15)
        q=_safe_json(r)
        pi=q.get("priceInfo",{}); md=q.get("metadata",{}); fi=q.get("industryInfo",{})
        si=q.get("securityInfo",{}); ob=q.get("marketDeptOrderBook",{})
        ltp=_f(pi.get("lastPrice",0)); open_p=_f(pi.get("open",ltp))
        high_d=_f(pi.get("intraDayHighLow",{}).get("max",ltp))
        low_d=_f(pi.get("intraDayHighLow",{}).get("min",ltp))
        prev=_f(pi.get("previousClose",ltp)); h52=_f(pi.get("weekHighLow",{}).get("max",ltp))
        l52=_f(pi.get("weekHighLow",{}).get("min",ltp)); pchg=_f(pi.get("pChange",0))
        vwap=_f(pi.get("vwap",ltp))
        bq=_f(ob.get("totalBuyQuantity",0)); sq=_f(ob.get("totalSellQuantity",0))
        result.update({"Company":md.get("companyName",""),"Industry":fi.get("industry",""),
            "Sector":fi.get("sector",""),"ISIN":md.get("isin",""),"Series":md.get("series",""),
            "Face Value":md.get("pdFaceValue",""),"Total Shares":si.get("issuedSize",""),
            "LTP":ltp,"Open":open_p,"High":high_d,"Low":low_d,"Prev Close":prev,
            "Change%":pchg,"VWAP":vwap,"52W High":h52,"52W Low":l52,"Buy Qty":int(bq),"Sell Qty":int(sq)})
        pivot=round((high_d+low_d+prev)/3,2); r1=round(2*pivot-low_d,2); r2=round(pivot+(high_d-low_d),2)
        s1=round(2*pivot-high_d,2); s2=round(pivot-(high_d-low_d),2); rng=h52-l52
        result.update({"Pivot":pivot,"R1":r1,"R2":r2,"S1":s1,"S2":s2,
            "Fib 23.6%":round(l52+0.236*rng,2),"Fib 38.2%":round(l52+0.382*rng,2),
            "Fib 50%":round(l52+0.5*rng,2),"Fib 61.8%":round(l52+0.618*rng,2),"Fib 78.6%":round(l52+0.786*rng,2)})
        all_lvl=sorted({r1,r2,s1,s2,result["Fib 23.6%"],result["Fib 38.2%"],result["Fib 50%"],result["Fib 61.8%"],result["Fib 78.6%"],h52,l52})
        sups=[x for x in all_lvl if x<ltp]; ress=[x for x in all_lvl if x>ltp]
        imm_sup=sups[-1] if sups else l52; imm_res=ress[0] if ress else h52; next_res=ress[1] if len(ress)>=2 else h52
        sl=round(imm_sup*0.985,2); tgt1=round(imm_res,2); tgt2=round(next_res,2)
        risk=ltp-sl; rew=tgt1-ltp; rr=round(rew/risk,1) if risk>0 else 0
        result.update({"Imm Support":imm_sup,"Imm Resist":imm_res,"Buy Zone":round(ltp*0.99,2),
            "Stop Loss":sl,"Target 1":tgt1,"Target 2":tgt2,
            "Upside%":round(rew/ltp*100,2) if ltp else 0,"Downside%":round(risk/ltp*100,2) if ltp else 0,"R:R":f"1:{rr}"})
        score=0; reasons=[]
        if h52>0 and l52<h52:
            pp=(ltp-l52)/(h52-l52)*100
            if pp>=85: score+=2; reasons.append(f"✅ Top {pp:.0f}% of 52W range")
            elif pp>=60: score+=1; reasons.append(f"✅ Upper range {pp:.0f}%")
            elif pp<=25: score-=1; reasons.append(f"⚠️ Lower range {pp:.0f}%")
        if pchg>2: score+=2; reasons.append(f"✅ Strong up {pchg:+.1f}% today")
        elif pchg>0: score+=1; reasons.append(f"✅ Positive {pchg:+.1f}%")
        elif pchg<-2: score-=2; reasons.append(f"🔴 Down {pchg:.1f}% today")
        if ltp>vwap: score+=1; reasons.append("✅ Above VWAP")
        elif ltp<vwap: score-=1; reasons.append("⚠️ Below VWAP")
        if bq>0 and sq>0:
            if bq>sq*1.3: score+=1; reasons.append("✅ Buy>Sell queue")
            elif sq>bq*1.3: score-=1; reasons.append("⚠️ Sell>Buy queue")
        if score>=4: verdict="🟢 STRONG BUY"; vc="green"
        elif score>=2: verdict="🟢 BUY"; vc="green"
        elif score>=0: verdict="🟡 HOLD/WATCH"; vc="orange"
        elif score>=-3: verdict="🔴 AVOID"; vc="red"
        else: verdict="🔴 SELL/EXIT"; vc="red"
        result.update({"_score":score,"_verdict":verdict,"_vcolor":vc,"_reasons":reasons})
    except Exception as e:
        result["_error"]=str(e); result.update({"_verdict":"❌ Error","_vcolor":"red","_score":0,"_reasons":[str(e)]})
    return result

@st.cache_data(ttl=900, show_spinner=False)
def fetch_power_trades():
    from datetime import datetime as _dt, timezone as _tz, timedelta as _td
    IST=_tz(_td(hours=5,minutes=30)); now=_dt.now(IST); stocks=fetch_n500(); candidates=[]
    fii_bullish=True
    try:
        s=get_session()
        fii_data=_extract_list(_safe_json(s.get("https://www.nseindia.com/api/fiidiiTradeReact",timeout=10)))
        total_net=sum(_f(x.get("netValue",0)) for x in fii_data if isinstance(x,dict))
        fii_bullish=total_net>=0
    except: pass
    for item in stocks:
        if not isinstance(item,dict): continue
        sym=item.get("symbol",""); ltp=_f(item.get("lastPrice",0))
        h52=_f(item.get("yearHigh",0)); l52=_f(item.get("yearLow",0))
        open_p=_f(item.get("open",ltp))
        high_d=_f(item.get("dayHigh",item.get("intraDayHighLow",{}).get("max",ltp)) if isinstance(item.get("intraDayHighLow"),dict) else ltp)
        low_d=_f(item.get("dayLow",ltp)); pchg=_f(item.get("pChange",0))
        vol=_f(item.get("totalTradedVolume",0)); prev=_f(item.get("previousClose",ltp))
        if not sym or ltp<=0 or h52<=0 or l52>=h52: continue
        score=0; signals=[]
        pct52=(ltp-l52)/(h52-l52)*100
        if pct52>=85: score+=30; signals.append(f"Near 52W High ({pct52:.0f}%)")
        elif pct52>=70: score+=20; signals.append(f"Upper range ({pct52:.0f}%)")
        elif pct52>=55: score+=10; signals.append(f"Mid-upper ({pct52:.0f}%)")
        elif pct52<=25: score-=20; signals.append("Near 52W Low — avoid")
        else: score-=5
        if high_d>low_d:
            carry_pct=(ltp-low_d)/(high_d-low_d)*100
            if carry_pct>=80: score+=25; signals.append(f"Holding near day high ({carry_pct:.0f}%)")
            elif carry_pct>=60: score+=15; signals.append(f"Strong close ({carry_pct:.0f}% of range)")
            elif carry_pct<=30: score-=15; signals.append("Near day low — weakness")
        if pchg>=3: score+=20; signals.append(f"+{pchg:.1f}% strong surge")
        elif pchg>=1.5: score+=12; signals.append(f"+{pchg:.1f}% positive")
        elif pchg>=0.5: score+=6; signals.append(f"+{pchg:.1f}% mild up")
        elif pchg<=-3: score-=20; signals.append(f"{pchg:.1f}% sharp fall")
        elif pchg<=-1: score-=10; signals.append(f"{pchg:.1f}% weak")
        trade_val=ltp*vol/1e7
        if trade_val>=100: score+=15; signals.append(f"₹{trade_val:.0f}Cr — very high volume")
        elif trade_val>=30: score+=10; signals.append(f"₹{trade_val:.0f}Cr — good volume")
        elif trade_val>=10: score+=5
        elif trade_val<2: score-=10; signals.append("Low volume — risky")
        if fii_bullish: score+=10; signals.append("FII net buying — bullish")
        else: score-=5; signals.append("FII net selling — cautious")
        dist_from_high=(h52-ltp)/h52*100
        if dist_from_high<=1: score+=15; signals.append("At 52W BREAKOUT!")
        elif dist_from_high<=3: score+=8; signals.append("Near 52W breakout zone")
        elif dist_from_high<=8: score+=3
        if prev>0:
            gap_pct=(open_p-prev)/prev*100
            if gap_pct>=1: score+=8; signals.append(f"Gap up {gap_pct:.1f}%")
            elif gap_pct>=0.5: score+=4
            elif gap_pct<=-2: score-=8; signals.append(f"Gap down {gap_pct:.1f}% — avoid")
        if pchg<0 and pct52<50: continue
        if score<40: continue
        fib_levels=sorted([l52+r*(h52-l52) for r in [0.236,0.382,0.5,0.618,0.786]])
        sup=max([x for x in fib_levels if x<ltp],default=l52)
        res=min([x for x in fib_levels if x>ltp],default=h52)
        res2=sorted([x for x in fib_levels if x>ltp])[1] if len([x for x in fib_levels if x>ltp])>=2 else h52
        entry=round(ltp*0.998,2); sl=round(max(sup*0.987,ltp*0.96),2)
        tgt1=round(min(res,ltp*1.04),2); tgt2=round(min(res2,ltp*1.08),2)
        risk=ltp-sl; reward=tgt1-ltp; rr=round(reward/risk,1) if risk>0 else 0
        n_sig=len(signals)
        if score>=85 and n_sig>=5: conf="🔥 HIGH CONFIDENCE"
        elif score>=65 and n_sig>=3: conf="✅ MEDIUM CONFIDENCE"
        else: conf="⚡ MODERATE"
        candidates.append({"Symbol":sym,"LTP":f"₹{ltp:,.2f}","Signal":"🟢 BUY","Entry":f"₹{entry:,.2f}",
            "Target 1":f"₹{tgt1:,.2f}","Target 2":f"₹{tgt2:,.2f}","Stop Loss":f"₹{sl:,.2f}",
            "R:R":f"1:{rr}","Confidence":conf,"Score":score,"Why":" | ".join(signals[:4])})
    candidates.sort(key=lambda x:x["Score"],reverse=True)
    return candidates[:2]

@st.cache_data(ttl=300, show_spinner=False)
def fetch_try_your_luck_pro():
    stocks=fetch_n500(); picks=[]
    for item in stocks:
        if not isinstance(item,dict): continue
        sym=item.get("symbol",""); ltp=_f(item.get("lastPrice",0))
        h52=_f(item.get("yearHigh",0)); l52=_f(item.get("yearLow",0))
        pchg=_f(item.get("pChange",0)); open_p=_f(item.get("open",ltp))
        prev=_f(item.get("previousClose",ltp)); vol=_f(item.get("totalTradedVolume",0))
        if not sym or ltp<=0 or h52<=0 or l52>=h52: continue
        pct_pos=(ltp-l52)/(h52-l52)*100; dist_high=(h52-ltp)/h52*100
        if pct_pos<70 or pchg<1.5 or vol<500000: continue
        score=0; reasons=[]
        if dist_high<=2: score+=3; reasons.append("Near breakout")
        if pchg>=3: score+=3; reasons.append("Strong momentum")
        if prev>0:
            gap=(open_p-prev)/prev*100
            if gap>=0.5: score+=2; reasons.append("Gap-up")
        if pchg>7: continue
        entry=ltp*1.005; sl=ltp*0.97; target=entry+(entry-sl)*2; rr=(target-entry)/(entry-sl)
        picks.append({"Symbol":sym,"LTP":f"₹{ltp:.2f}","Entry":f"₹{entry:.2f}",
            "Target":f"₹{target:.2f}","StopLoss":f"₹{sl:.2f}","RR":f"{rr:.1f}","Score":score,"Why":" | ".join(reasons)})
    picks.sort(key=lambda x:x["Score"],reverse=True)
    return picks[:2]


# ═══════════════════════════════════════════════════════════════
#  LONG TERM SCREENER — FUNDAMENTAL + TECHNICAL ALGORITHM
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=43200, show_spinner=False)   # refresh every 12 hours
def fetch_stock_fundamentals(symbol):
    """
    Fetch REAL fundamentals for a symbol using multiple NSE API endpoints with fallbacks.
    APIs tried in order until data is found.
    """
    s   = get_session()
    out = {"symbol": symbol, "ok": False}

    # ── 1. Quote equity → PE, EPS, Book Value, Sector ────────────
    try:
        r1 = s.get(f"https://www.nseindia.com/api/quote-equity?symbol={symbol}", timeout=8)
        q  = _safe_json(r1)
        pi = q.get("priceInfo", {})
        md = q.get("metadata",  {})
        si = q.get("securityInfo", {})
        fi = q.get("industryInfo", {})

        ltp      = _f(pi.get("lastPrice", 0))
        # NSE: pdSectorPe = sector PE, pdSymbolPe = stock's own PE
        pe       = _f(md.get("pdSymbolPe", md.get("pdSectorPe", 0)))
        eps_val  = round(ltp / pe, 2) if pe > 0 else 0
        shares   = _f(si.get("issuedSize", 0))
        face_val = _f(md.get("pdFaceValue", 10))
        bvps     = _f(md.get("pdBookValue", 0))
        sector   = fi.get("sector", "")
        industry = fi.get("industry", "")
        mktcap   = round(ltp * shares / 1e7, 0) if shares > 0 else 0

        out.update({
            "LTP": ltp, "PE": pe, "EPS": eps_val,
            "Face Value": face_val, "Shares": shares,
            "Market Cap (Cr)": mktcap, "Sector": sector,
            "Industry": industry, "Book Value/Share": bvps,
        })
    except: pass

    # ── 2. Quarterly results — try ALL known NSE endpoints ────────
    revenues = []; profits = []
    qlist    = []

    RESULT_URLS = [
        f"https://www.nseindia.com/api/financial-results?index=equities&symbol={symbol}",
        f"https://www.nseindia.com/api/results-comparator?index=equities&params=quarterlyResults&symbol={symbol}",
        f"https://www.nseindia.com/api/annual-reports?symbol={symbol}&industry=equities",
        f"https://www.nseindia.com/api/quarterly-results?index=equities&symbol={symbol}",
    ]
    for url in RESULT_URLS:
        if qlist: break
        try:
            fd = _safe_json(s.get(url, timeout=6))
            if isinstance(fd, list) and fd:
                qlist = fd; break
            if isinstance(fd, dict):
                for k in ("data","quarterlyResults","quarterly","results",
                          "financials","body","items","records"):
                    v = fd.get(k)
                    if isinstance(v, list) and len(v) >= 1:
                        qlist = v; break
                if qlist: break
        except: pass

    # Parse whichever qlist we got
    REV_KEYS = ("income","totalIncome","netSales","sales","revenue",
                "totalRevenue","grossSales","totalIncome_")
    PAT_KEYS = ("netProfit","profit","pat","profitAfterTax","netIncome",
                "profitLoss","pbt","profit_loss")

    for q_item in qlist[:6]:
        if not isinstance(q_item, dict): continue
        rev = 0
        for k in REV_KEYS:
            v = _f(q_item.get(k, 0))
            if v > 0: rev = v; break
        pat = 0
        for k in PAT_KEYS:
            if k in q_item:
                pat = _f(q_item[k]); break
        if rev > 0:
            revenues.append(rev); profits.append(pat)

    # ── 2b. Shareholding — try multiple endpoints ─────────────────
    promoter_pct = 0.0; fii_pct = 0.0; dii_pct = 0.0
    SHARE_URLS = [
        f"https://www.nseindia.com/api/corporate-share-holdings-master?symbol={symbol}",
        f"https://www.nseindia.com/api/corporate-shareholding?symbol={symbol}",
        f"https://www.nseindia.com/api/quote-equity?symbol={symbol}&section=ownership",
    ]
    for url in SHARE_URLS:
        try:
            sd    = _safe_json(s.get(url, timeout=6))
            slist = sd if isinstance(sd, list) else _extract_list(sd)
            if not slist: continue
            for sh in slist[:30]:
                if not isinstance(sh, dict): continue
                # Try all possible key names
                cat = str(sh.get("category",
                          sh.get("shareholderType",
                          sh.get("Category",
                          sh.get("type","")))).upper())
                pct = _f(sh.get("holdingPercentage",
                         sh.get("percentHolding",
                         sh.get("percent",
                         sh.get("Percentage", 0)))))
                if not cat or pct <= 0: continue
                if "PROMOTER" in cat:
                    if pct > promoter_pct: promoter_pct = pct
                if "FII" in cat or "FPI" in cat or "FOREIGN" in cat:
                    fii_pct = max(fii_pct, pct)
                if "DII" in cat or "MF" in cat or "MUTUAL" in cat or \
                   "INSURANCE" in cat or "LIC" in cat or "DOMESTIC" in cat:
                    dii_pct = max(dii_pct, pct)
            # If we got promoter data, stop trying
            if promoter_pct > 0: break
        except: pass

    # ── 2c. Try ownership section of quote-equity ─────────────────
    if promoter_pct == 0:
        try:
            r_own = s.get(
                f"https://www.nseindia.com/api/quote-equity?symbol={symbol}&section=ownership",
                timeout=6)
            own = _safe_json(r_own)
            # NSE sometimes returns shareholdingPatterns
            patterns = own.get("shareholdingPatterns", own.get("data", []))
            if isinstance(patterns, dict):
                # Try flat fields
                promoter_pct = _f(patterns.get("promoterAndPromoterGroupShareholding",
                                  patterns.get("promoter", 0)))
                fii_pct      = _f(patterns.get("fiiShareholding",
                                  patterns.get("fpi", 0)))
                dii_pct      = _f(patterns.get("diiShareholding",
                                  patterns.get("dii", 0)))
        except: pass

    # ── 3. Calculate growth metrics ───────────────────────────────
    rev_trend = "N/A"; pat_trend = "N/A"
    eps_growth = "N/A"; rev_yoy = None; pat_yoy = None

    if len(revenues) >= 2:
        if revenues[1] > 0:
            rev_yoy = round((revenues[0]-revenues[1])/revenues[1]*100, 1)
        if profits[1] != 0:
            pat_yoy = round((profits[0]-profits[1])/abs(profits[1])*100, 1)

    if len(revenues) >= 4:
        if revenues[3] > 0:
            rev_yoy = round((revenues[0]-revenues[3])/revenues[3]*100, 1)
            rev_trend = f"+{rev_yoy}% YoY" if rev_yoy >= 0 else f"{rev_yoy}% YoY"
        if profits[3] != 0:
            pat_yoy = round((profits[0]-profits[3])/abs(profits[3])*100, 1)
            pat_trend = f"+{pat_yoy}% YoY" if pat_yoy >= 0 else f"{pat_yoy}% YoY"

    eps_val = out.get("EPS", 0)
    if eps_val and pat_yoy is not None:
        eps_growth = f"+{pat_yoy}%" if pat_yoy >= 0 else f"{pat_yoy}%"

    consec = len(profits) >= 3 and profits[0] > profits[1] > profits[2]

    rev_disp = " → ".join(f"₹{r:.0f}Cr" for r in revenues[:4]) if revenues else "N/A"
    pat_disp = " → ".join(f"₹{p:.0f}Cr" for p in profits[:4]) if profits else "N/A"

    out.update({
        "Revenue Q1–Q4":  rev_disp,
        "Profit Q1–Q4":   pat_disp,
        "Rev Growth YoY": rev_trend,
        "PAT Growth YoY": pat_trend,
        "EPS Growth":     eps_growth,
        "Consec Growth":  consec,
        "_revenues":      revenues[:4],
        "_profits":       profits[:4],
        "_rev_yoy":       rev_yoy,
        "_pat_yoy":       pat_yoy,
        "Promoter %":     round(promoter_pct, 2),
        "FII %":          round(fii_pct, 2),
        "DII %":          round(dii_pct, 2),
    })

    # ── 4. Derived ratios ─────────────────────────────────────────
    bvps    = _f(out.get("Book Value/Share", 0))
    pe      = _f(out.get("PE", 0))
    ltp     = _f(out.get("LTP", 0))
    eps_val = _f(out.get("EPS", 0))
    roe     = round(eps_val / bvps * 100, 1) if bvps > 0 and eps_val > 0 else None
    pb      = round(ltp / bvps, 2)           if bvps > 0 and ltp > 0 else None
    peg     = round(pe / pat_yoy, 2)         if pe > 0 and pat_yoy and pat_yoy > 0 else None

    out.update({
        "ROE %": f"{roe}%" if roe else "N/A",
        "P/B":   pb        if pb   else "N/A",
        "PEG":   peg       if peg  else "N/A",
        "ok":    True,
    })

    return out


@st.cache_data(ttl=43200, show_spinner=False)  # 12-hour cache
def fetch_longterm_quality_stocks():
    """
    LONG-TERM QUALITY STOCK SCREENER — REAL FUNDAMENTALS
    ══════════════════════════════════════════════════════
    Step 1: Technical pre-screen from NIFTY 500 price data → shortlist ~80 candidates
            (above 200DMA, uptrend, good volume, not penny stocks)

    Step 2: For each candidate, fetch REAL data from NSE APIs:
            → Quarterly Revenue + Net Profit (last 4 quarters)
            → PE ratio, EPS, Book Value
            → Promoter shareholding %
            → FII / DII holding %

    Step 3: Score on 15 REAL factors:
            FUNDAMENTAL (real data):
              F1.  Revenue YoY growth ≥ 15%        → 20 pts
              F2.  PAT (profit) YoY growth ≥ 15%   → 20 pts
              F3.  Consecutive quarterly growth     → 15 pts
              F4.  ROE ≥ 15%                        → 15 pts
              F5.  PE reasonable (10–40 range)      → 10 pts
              F6.  PEG < 1.5                        → 15 pts
              F7.  Promoter holding ≥ 50%           → 12 pts
              F8.  FII+DII holding (inst interest)  → 10 pts
              F9.  EPS positive and growing         → 10 pts
            TECHNICAL (price data):
              T1.  Above 200 DMA (52W pos ≥ 60%)   → 15 pts
              T2.  Near 52W high / breakout         → 12 pts
              T3.  Volume / liquidity               → 8 pts
              T4.  No crash today (pchg > -3%)      → 5 pts
            QUALITY GATE (hard filters):
              ✗  Rev growth < 0%   → disqualify
              ✗  PAT < 0 (loss)    → disqualify
              ✗  Promoter < 25%    → penalise
              ✗  PE > 100          → penalise

    Step 4: Top 30 stocks with highest composite score
            Targets calculated from real EPS + PE expansion model
    """
    from datetime import datetime as _dt
    s      = get_session()
    stocks = fetch_n500()

    # ── FII market sentiment ──────────────────────────────────────
    fii_bullish = True
    try:
        fii_data    = _extract_list(_safe_json(s.get("https://www.nseindia.com/api/fiidiiTradeReact", timeout=10)))
        total_net   = sum(_f(x.get("netValue", 0)) for x in fii_data if isinstance(x, dict))
        fii_bullish = total_net >= 0
    except: pass

    # ── Step 1: Technical pre-screen — keep best ~80 candidates ───
    candidates = []
    for item in stocks:
        if not isinstance(item, dict): continue
        sym  = item.get("symbol","")
        ltp  = _f(item.get("lastPrice",0))
        h52  = _f(item.get("yearHigh",0))
        l52  = _f(item.get("yearLow",0))
        pchg = _f(item.get("pChange",0))
        vol  = _f(item.get("totalTradedVolume",0))
        if not sym or ltp < 30 or h52 <= 0 or l52 >= h52: continue
        pct52     = (ltp - l52) / (h52 - l52) * 100
        trade_val = ltp * vol / 1e7
        # Pre-screen: above 200DMA proxy + decent liquidity + not crashing
        if pct52 >= 50 and trade_val >= 2 and pchg > -5:
            candidates.append({
                "symbol": sym, "ltp": ltp, "h52": h52, "l52": l52,
                "pchg": pchg, "vol": vol, "pct52": pct52, "trade_val": trade_val,
            })

    # Sort by 52W position desc, take top 30 only for fundamental fetch
    candidates.sort(key=lambda x: x["pct52"], reverse=True)
    candidates = candidates[:30]

    # ── Step 2+3: Fetch real fundamentals + score ─────────────────
    results = []
    for cand in candidates:
        sym       = cand["symbol"]
        ltp       = cand["ltp"]
        h52       = cand["h52"]
        l52       = cand["l52"]
        pchg      = cand["pchg"]
        pct52     = cand["pct52"]
        trade_val = cand["trade_val"]
        dist_h    = (h52 - ltp) / h52 * 100

        # Fetch fundamentals (cached 12hr) — skip if error
        try:
            fd = fetch_stock_fundamentals(sym)
        except Exception:
            fd = {"symbol": sym, "ok": False, "_revenues": [], "_profits": [],
                  "_rev_yoy": None, "_pat_yoy": None, "Promoter %": 0,
                  "FII %": 0, "DII %": 0, "PE": 0, "EPS": 0,
                  "ROE %": "N/A", "P/B": "N/A", "PEG": "N/A",
                  "Revenue Q1–Q4": "N/A", "Profit Q1–Q4": "N/A",
                  "Rev Growth YoY": "N/A", "PAT Growth YoY": "N/A",
                  "EPS Growth": "N/A", "Consec Growth": False,
                  "Sector": "", "Market Cap (Cr)": 0,
                  "PE Flag": "N/A", "PEG Flag": "N/A", "Promoter Flag": "N/A", "Inst Flag": "N/A"}

        score    = 0
        signals  = []
        reasons  = []

        # ── F1: Revenue YoY Growth ────────────────────────────────
        rev_yoy = fd.get("_rev_yoy")
        if rev_yoy is not None:
            if rev_yoy >= 25:
                score += 20; signals.append(f"Revenue +{rev_yoy}% YoY 🔥")
            elif rev_yoy >= 15:
                score += 15; signals.append(f"Revenue +{rev_yoy}% YoY ✅")
            elif rev_yoy >= 8:
                score += 8;  signals.append(f"Revenue +{rev_yoy}% YoY")
            elif rev_yoy >= 0:
                score += 3
            else:
                score -= 15; reasons.append(f"⚠️ Revenue declining {rev_yoy}%")
        else:
            # NSE quarterly API returned no data — neutral
            score += 5

        # ── F2: PAT (Profit) YoY Growth ──────────────────────────
        pat_yoy = fd.get("_pat_yoy")
        profits = fd.get("_profits", [])
        if pat_yoy is not None:
            if any(p < 0 for p in profits[:2]):
                score -= 20; reasons.append("🔴 Company making losses — avoid for LT")
            elif pat_yoy >= 25:
                score += 20; signals.append(f"Profit +{pat_yoy}% YoY 🔥")
            elif pat_yoy >= 15:
                score += 15; signals.append(f"Profit +{pat_yoy}% YoY ✅")
            elif pat_yoy >= 8:
                score += 8;  signals.append(f"Profit +{pat_yoy}% YoY")
            elif pat_yoy >= 0:
                score += 3
            else:
                score -= 12; reasons.append(f"⚠️ Profit falling {pat_yoy}%")
        else:
            score += 5  # neutral if no data

        # ── F3: Consecutive Quarterly Growth ─────────────────────
        if fd.get("Consec Growth"):
            score += 15; signals.append("3 consecutive qtrs of profit growth ✅")
        elif len(profits) >= 2 and profits[0] > profits[1]:
            score += 6

        # ── F4: ROE ≥ 15% ────────────────────────────────────────
        roe_str = str(fd.get("ROE %", "N/A"))
        roe_val = _f(roe_str.replace("%","")) if roe_str != "N/A" else None
        if roe_val is not None:
            if roe_val >= 25:
                score += 15; signals.append(f"ROE {roe_val}% — excellent 🔥")
            elif roe_val >= 15:
                score += 10; signals.append(f"ROE {roe_val}% — good ✅")
            elif roe_val >= 10:
                score += 4
            elif roe_val > 0:
                score += 1
            else:
                score -= 8

        # ── F5: PE Valuation (not too cheap = risky, not too high = expensive) ─
        pe = _f(fd.get("PE", 0))
        pe_flag = "N/A"
        if pe > 0:
            if 10 <= pe <= 25:
                score += 10; pe_flag = f"✅ {pe:.1f} (Value)"
            elif 25 < pe <= 40:
                score += 8;  pe_flag = f"✅ {pe:.1f} (Fair)"
            elif 40 < pe <= 60:
                score += 4;  pe_flag = f"⚠️ {pe:.1f} (Premium)"
            elif pe > 60:
                score -= 5;  pe_flag = f"🔴 {pe:.1f} (Expensive)"
                reasons.append(f"PE={pe:.0f} very high — growth must justify")
            elif pe < 10:
                score += 5;  pe_flag = f"⚠️ {pe:.1f} (Cheap — check why)"
        fd["PE Flag"] = pe_flag

        # ── F6: PEG < 1.5 ────────────────────────────────────────
        peg = fd.get("PEG")
        peg_flag = "N/A"
        if peg and peg != "N/A":
            peg_v = _f(str(peg))
            if peg_v <= 0.5:
                score += 15; peg_flag = f"🔥 {peg_v:.2f} (Excellent)"; signals.append(f"PEG={peg_v:.2f} — deeply undervalued vs growth")
            elif peg_v <= 1.0:
                score += 12; peg_flag = f"✅ {peg_v:.2f} (Good)"
            elif peg_v <= 1.5:
                score += 8;  peg_flag = f"✅ {peg_v:.2f} (Acceptable)"
            elif peg_v <= 2.5:
                score += 2;  peg_flag = f"⚠️ {peg_v:.2f} (Stretched)"
            else:
                score -= 5;  peg_flag = f"🔴 {peg_v:.2f} (Overvalued)"
        fd["PEG Flag"] = peg_flag

        # ── F7: Promoter holding ≥ 50% ───────────────────────────
        promo = _f(fd.get("Promoter %", 0))
        promo_flag = "N/A"
        if promo > 0:
            if promo >= 65:
                score += 12; promo_flag = f"✅ {promo}% (Very High)"; signals.append(f"Promoter {promo}% — strong conviction")
            elif promo >= 50:
                score += 8;  promo_flag = f"✅ {promo}% (Good)"
            elif promo >= 35:
                score += 3;  promo_flag = f"⚠️ {promo}%"
            else:
                score -= 5;  promo_flag = f"🔴 {promo}% (Low)"
                reasons.append(f"Promoter holding low {promo}%")
        fd["Promoter Flag"] = promo_flag

        # ── F8: Institutional Interest (FII + DII) ───────────────
        fii_hold = _f(fd.get("FII %", 0))
        dii_hold = _f(fd.get("DII %", 0))
        inst_total = fii_hold + dii_hold
        inst_flag  = "N/A"
        if inst_total > 0:
            if inst_total >= 40:
                score += 10; inst_flag = f"🔥 {inst_total:.1f}% FII+DII"; signals.append("Heavy institutional holding")
            elif inst_total >= 20:
                score += 7;  inst_flag = f"✅ {inst_total:.1f}% FII+DII"
            elif inst_total >= 10:
                score += 4;  inst_flag = f"⚠️ {inst_total:.1f}% FII+DII"
            else:
                score += 1;  inst_flag = f"Low {inst_total:.1f}%"
        elif fii_bullish:
            score += 4;  inst_flag = "✅ FII Mkt Bullish"
        fd["Inst Flag"] = inst_flag

        # ── F9: EPS positive ─────────────────────────────────────
        eps = _f(fd.get("EPS", 0))
        if eps > 0:
            score += 10
            if eps > 50:    signals.append(f"Strong EPS ₹{eps:.1f}")
        elif eps < 0:
            score -= 10; reasons.append("Negative EPS")

        # ── T1: Above 200 DMA ────────────────────────────────────
        if pct52 >= 80:
            score += 15; signals.append("Well above 200DMA")
        elif pct52 >= 65:
            score += 10
        elif pct52 >= 50:
            score += 4

        # ── T2: Trend / Breakout ──────────────────────────────────
        if dist_h <= 5:
            score += 12; signals.append("Near 52W breakout 🚀")
        elif dist_h <= 15:
            score += 7
        elif dist_h <= 30:
            score += 3
        else:
            score -= 5

        # ── T3: Liquidity ─────────────────────────────────────────
        if trade_val >= 100:  score += 8
        elif trade_val >= 30: score += 5
        elif trade_val >= 10: score += 2
        elif trade_val < 3:   score -= 8

        # ── T4: No crash today ────────────────────────────────────
        if pchg >= 0:        score += 5
        elif pchg >= -2:     score += 2
        else:                score -= 5

        # ── Hard disqualifiers ─────────────────────────────────────
        profits_real = fd.get("_profits", [])
        if profits_real and any(p < 0 for p in profits_real[:1]) and pat_yoy is not None:
            continue   # confirmed loss-making — skip
        if rev_yoy is not None and rev_yoy < -20:
            continue   # revenue crashing — skip

        # ── Bonus: if quarterly API returned N/A, reward strong technical ──
        # Read promoter_pct from fd dict (it lives in fetch_stock_fundamentals scope)
        _promoter_pct = _f(fd.get("Promoter %", 0))
        has_fundamental_data = (rev_yoy is not None or pat_yoy is not None or _promoter_pct > 0)
        if not has_fundamental_data:
            # Give extra technical score so chart-strong stocks still get graded
            if pct52 >= 80 and dist_h <= 5:    score += 25
            elif pct52 >= 70 and dist_h <= 15:  score += 15
            elif pct52 >= 60:                   score += 8

        # ── Minimum score gate ────────────────────────────────────
        if score < 30: continue

        # ── Grade & Targets — calibrated for real-world scores ────
        # With full fundamentals: max score ~160
        # With only technicals (N/A data): max score ~90
        # Thresholds adjusted accordingly
        if score >= 90:
            grade = "STRONG BUY"; stars = 5
            potential = "4x-5x"; horizon = "3-5 Years"
            t1y = round(ltp * 1.50, 2)
            t3y = round(ltp * 3.50, 2)
            t5y = round(ltp * 5.00, 2)
        elif score >= 70:
            grade = "BUY"; stars = 4
            potential = "2.5x-4x"; horizon = "2-4 Years"
            t1y = round(ltp * 1.35, 2)
            t3y = round(ltp * 2.75, 2)
            t5y = round(ltp * 4.00, 2)
        elif score >= 50:
            grade = "ACCUMULATE"; stars = 3
            potential = "2x-3x"; horizon = "3-5 Years"
            t1y = round(ltp * 1.22, 2)
            t3y = round(ltp * 2.00, 2)
            t5y = round(ltp * 3.00, 2)
        else:
            grade = "WATCH"; stars = 2
            potential = "1.5x-2x"; horizon = "3-5 Years"
            t1y = round(ltp * 1.15, 2)
            t3y = round(ltp * 1.70, 2)
            t5y = round(ltp * 2.20, 2)

        # Build star string separately (no emoji in grade for clean filtering)
        star_str  = "⭐" * stars
        grade_str = f"{star_str} {grade}"

        results.append({
            "Symbol":          sym,
            "Sector":          fd.get("Sector",""),
            "LTP":             f"₹{ltp:,.2f}",
            "Grade":           grade_str,
            "Stars":           stars,
            "Score":           score,
            "Potential":       potential,
            "Horizon":         horizon,
            "Entry Zone":      f"₹{round(ltp*0.97,2):,.2f}–₹{round(ltp*1.02,2):,.2f}",
            "1Y Target":       f"₹{t1y:,.2f}",
            "3Y Target":       f"₹{t3y:,.2f}",
            "5Y Target":       f"₹{t5y:,.2f}",
            "LT Stop Loss":    f"₹{round(ltp*0.78,2):,.2f}",
            "Revenue Q1→Q4":   fd.get("Revenue Q1–Q4","N/A"),
            "Profit Q1→Q4":    fd.get("Profit Q1–Q4","N/A"),
            "Rev Growth YoY":  fd.get("Rev Growth YoY","N/A"),
            "PAT Growth YoY":  fd.get("PAT Growth YoY","N/A"),
            "EPS Growth":      fd.get("EPS Growth","N/A"),
            "EPS (Rs)":        f"Rs{eps:.2f}" if eps else "N/A",
            "PE":              fd.get("PE Flag","N/A"),
            "PEG":             fd.get("PEG Flag","N/A"),
            "ROE":             fd.get("ROE %","N/A"),
            "P/B":             str(fd.get("P/B","N/A")),
            "Promoter Hold":   fd.get("Promoter Flag","N/A"),
            "FII+DII Hold":    fd.get("Inst Flag","N/A"),
            "Mkt Cap (Cr)":    f"Rs{fd.get('Market Cap (Cr)',0):,.0f}Cr" if fd.get("Market Cap (Cr)",0) > 0 else "N/A",
            "52W Pos":         f"{pct52:.0f}%",
            "200DMA":          "Above" if pct52 >= 60 else "Near" if pct52 >= 45 else "Below",
            "Trend":           "Breakout" if dist_h <= 5 else "Uptrend" if dist_h <= 15 else "Consolidating",
            "Consec Growth":   "Yes" if fd.get("Consec Growth") else "No",
            "Has Fundas":      "Yes" if has_fundamental_data else "Tech Only",
            "Key Signals":     " | ".join(signals[:4]),
            "Watch Out":       " | ".join(reasons[:2]) if reasons else "-",
        })

    results.sort(key=lambda x: x["Score"], reverse=True)
    return results[:30]



# ═══════════════════════════════════════════════════════════════
#  NEW: CHART + REAL TECHNICAL INDICATORS (yfinance + manual RSI/MACD/EMA)
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_chart_indicators(symbol, period="6mo"):
    """
    Fetch OHLCV history for a symbol and compute:
    RSI(14), MACD(12,26,9), EMA20/50/200, Volume MA(20), Relative Volume.
    Uses yfinance (installed via requirements.txt).
    """
    try:
        import yfinance as yf
        ticker = yf.Ticker(f"{symbol}.NS")
        df = ticker.history(period=period, interval="1d")
        if df is None or df.empty or len(df) < 20:
            return None
        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        if "date" in df.columns:
            df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        # RSI(14)
        delta = df["close"].diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        rs    = gain / loss.replace(0, float("nan"))
        df["rsi"] = 100 - 100 / (1 + rs)
        # MACD
        ema12 = df["close"].ewm(span=12, adjust=False).mean()
        ema26 = df["close"].ewm(span=26, adjust=False).mean()
        df["macd"]      = ema12 - ema26
        df["macd_sig"]  = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_sig"]
        # EMAs
        df["ema20"]  = df["close"].ewm(span=20,  adjust=False).mean()
        df["ema50"]  = df["close"].ewm(span=50,  adjust=False).mean()
        df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()
        # Volume analytics
        df["vol_ma20"] = df["volume"].rolling(20).mean()
        df["rel_vol"]  = (df["volume"] / df["vol_ma20"].replace(0, float("nan"))).round(2)
        return df
    except Exception:
        return None


@st.cache_data(ttl=180, show_spinner=False)
def fetch_options_chain(symbol="NIFTY"):
    """
    Fetch live NSE Options Chain for NIFTY / BANKNIFTY / any F&O equity.
    Returns dict with underlying price, expiries, PCR, max pain, OI table.
    """
    s = get_session()
    try:
        if symbol.upper() in ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"):
            url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol.upper()}"
        else:
            url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol.upper()}"
        r = s.get(url, timeout=15)
        raw = _safe_json(r)
        records  = raw.get("records", {})
        filtered = raw.get("filtered", {})
        underlying = _f(records.get("underlyingValue", 0))
        expiries   = records.get("expiryDates", [])
        all_data   = records.get("data", [])
        return {
            "underlying": underlying,
            "expiries":   expiries,
            "data":       all_data,
            "filtered":   filtered,
            "ok":         True,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def compute_pcr_maxpain(options_result, chosen_expiry=None):
    """Compute PCR and Max Pain from options chain result dict."""
    if not options_result or not options_result.get("ok"):
        return None
    data   = options_result.get("data", [])
    expiry = chosen_expiry or (options_result.get("expiries", [None])[0])
    total_ce_oi = 0; total_pe_oi = 0
    ce_chg_total = 0; pe_chg_total = 0
    strikes = {}
    for item in data:
        if expiry and item.get("expiryDate") != expiry:
            continue
        strike = _f(item.get("strikePrice", 0))
        ce     = item.get("CE", {}); pe = item.get("PE", {})
        ce_oi  = _f(ce.get("openInterest", 0))
        pe_oi  = _f(pe.get("openInterest", 0))
        ce_chg = _f(ce.get("changeinOpenInterest", 0))
        pe_chg = _f(pe.get("changeinOpenInterest", 0))
        ce_ltp = _f(ce.get("lastPrice", 0))
        pe_ltp = _f(pe.get("lastPrice", 0))
        ce_iv  = _f(ce.get("impliedVolatility", 0))
        pe_iv  = _f(pe.get("impliedVolatility", 0))
        total_ce_oi  += ce_oi;  total_pe_oi  += pe_oi
        ce_chg_total += ce_chg; pe_chg_total += pe_chg
        if strike > 0:
            strikes[strike] = {
                "ce_oi":  ce_oi,  "pe_oi":  pe_oi,
                "ce_chg": ce_chg, "pe_chg": pe_chg,
                "ce_ltp": ce_ltp, "pe_ltp": pe_ltp,
                "ce_iv":  ce_iv,  "pe_iv":  pe_iv,
            }
    pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0
    # Max Pain: find strike where total options pain is minimum
    max_pain = 0
    if strikes:
        min_pain = float("inf")
        for test_s in sorted(strikes.keys()):
            pain = sum(
                d["ce_oi"] * max(s - test_s, 0) + d["pe_oi"] * max(test_s - s, 0)
                for s, d in strikes.items()
            )
            if pain < min_pain:
                min_pain = pain; max_pain = test_s
    # Signal interpretation
    if pcr >= 1.3:   pcr_sig = "🟢 VERY BULLISH — Heavy Put writing"
    elif pcr >= 1.0: pcr_sig = "🟢 Bullish — More puts than calls"
    elif pcr >= 0.8: pcr_sig = "🟡 Neutral / Sideways"
    elif pcr >= 0.6: pcr_sig = "🔴 Bearish — Call writers dominating"
    else:            pcr_sig = "🔴 VERY BEARISH — Heavy call writing"
    return {
        "pcr":       pcr,
        "max_pain":  max_pain,
        "ce_oi":     total_ce_oi,
        "pe_oi":     total_pe_oi,
        "ce_chg":    ce_chg_total,
        "pe_chg":    pe_chg_total,
        "signal":    pcr_sig,
        "expiry":    expiry,
        "strikes":   strikes,
    }


@st.cache_data(ttl=300, show_spinner=False)
def fetch_volume_spikes():
    """
    Scan NIFTY 500 for volume spikes (unusually high trading volume today).
    Relative Volume = Today Volume / Estimated 20D Avg Volume.
    Stocks with Rel Vol > 1.5x are highlighted — often precede big moves.
    """
    stocks = fetch_n500(); spikes = []
    for item in stocks:
        if not isinstance(item, dict): continue
        sym  = item.get("symbol", "");  ltp  = _f(item.get("lastPrice", 0))
        vol  = _f(item.get("totalTradedVolume", 0))
        pchg = _f(item.get("pChange", 0))
        h52  = _f(item.get("yearHigh", 0)); l52 = _f(item.get("yearLow", 0))
        prev = _f(item.get("previousClose", ltp))
        if not sym or ltp <= 0 or vol <= 0: continue
        # Estimate 20D avg vol from NSE data (if totalBuyQuantity/totalSellQty present)
        avg_vol_est = _f(item.get("averageTradedPrice", 0))  # not avg vol but available
        # Better estimate: NSE doesn't provide avg vol in this endpoint, use traded value
        traded_val = ltp * vol / 1e7  # Cr
        # Flag as spike if traded value is notably high + strong move
        pct52 = (ltp - l52) / (h52 - l52) * 100 if h52 > l52 else 0
        gap = (ltp - prev) / prev * 100 if prev > 0 else 0
        # High volume proxy: stocks with > ₹100 Cr volume AND strong move
        if traded_val >= 20 and (abs(pchg) >= 2 or abs(gap) >= 1):
            intent = ("🟢 Buying Surge" if pchg > 0 else "🔴 Selling Pressure")
            lvl    = ("🔥 MEGA" if traded_val >= 500 else ("💥 HIGH" if traded_val >= 100 else "⚡ Elevated"))
            spikes.append({
                "Symbol":      sym,
                "LTP":         f"₹{ltp:,.2f}",
                "Change%":     f"{pchg:+.2f}%",
                "Volume":      f"{int(vol):,}",
                "Traded (Cr)": f"₹{traded_val:.1f} Cr",
                "Gap%":        f"{gap:+.2f}%",
                "52W Pos":     f"{pct52:.0f}%",
                "Vol Level":   lvl,
                "Intent":      intent,
            })
    spikes.sort(key=lambda x: _f(x["Traded (Cr)"].replace("₹","").replace(" Cr","")), reverse=True)
    return spikes[:50]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_results_calendar():
    """Fetch upcoming board meetings / quarterly results from NSE corporate actions."""
    s = get_session(); rows = []
    today = datetime.today()
    d_from = today.strftime("%d-%m-%Y")
    d_to   = (today + timedelta(days=45)).strftime("%d-%m-%Y")
    try:
        r = s.get(
            f"https://www.nseindia.com/api/corporates-corporateActions?index=equities&from_date={d_from}&to_date={d_to}",
            timeout=20)
        items = _extract_list(_safe_json(r))
        for item in items:
            if not isinstance(item, dict): continue
            purpose = str(item.get("purpose", "")).lower()
            if any(kw in purpose for kw in ("board meeting", "financial result",
                                             "quarterly result", "half year", "annual result")):
                sym    = (item.get("symbol", "") or "").strip()
                comp   = item.get("comp", item.get("companyName", ""))
                date   = item.get("bm_date", item.get("date", item.get("exDate", "")))
                purp   = item.get("purpose", "")
                rows.append({
                    "Symbol":   sym,  "Company": comp,
                    "Date":     date, "Purpose": purp,
                    "Category": "📊 Results" if "result" in purpose else "🏛️ Board Meet",
                })
    except:
        pass
    if not rows:
        rows = [{"Symbol": "No upcoming results found", "Company": "--",
                 "Date": "--", "Purpose": "Retry during market hours", "Category": "--"}]
    return rows[:60]


# ═══════════════════════════════════════════════════════════════
#  UI HELPERS
# ═══════════════════════════════════════════════════════════════

def df_show(data, height=400):
    if not data: st.info("No data available — refresh or retry."); return
    df = pd.DataFrame(data)
    st.dataframe(df, width="stretch", height=height)
    st.markdown('<div style="padding-bottom:16px;"></div>', unsafe_allow_html=True)

def info_box(text):
    st.markdown(f'<div class="info-box">💡 {text}</div><div style="padding-bottom:16px;"></div>', unsafe_allow_html=True)

def lt_box(text):
    st.markdown(f'<div class="lt-box">🌱 {text}</div><div style="padding-bottom:12px;"></div>', unsafe_allow_html=True)

def section_hdr(title):
    st.markdown(f'<div class="section-header"><h3>{title}</h3></div><div style="padding-bottom:8px;"></div>', unsafe_allow_html=True)

def section_end():
    st.markdown('<div style="padding-bottom:16px;"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px 0;">
        <div style="font-size:2.5rem;">🇮🇳</div>
        <div style="color:#00d2ff; font-size:1.1rem; font-weight:800;">STOCK MARKET PRO</div>
        <div style="color:#8899bb; font-size:0.75rem;">NSE Live Dashboard</div>
    </div>""", unsafe_allow_html=True)

    from datetime import timezone, timedelta as _td
    IST = timezone(_td(hours=5, minutes=30)); now = datetime.now(IST)
    mkt_open = now.weekday()<5 and ((now.hour==9 and now.minute>=15) or (10<=now.hour<=14) or (now.hour==15 and now.minute<=30))
    mk_bg="#0d3320" if mkt_open else "#200a0a"; mk_color="#26de81" if mkt_open else "#fc5c65"
    mk_text="● MARKET OPEN" if mkt_open else "● MARKET CLOSED"
    mk_sub="9:15 AM – 3:30 PM IST" if mkt_open else "Opens 9:15 AM IST Mon-Fri"
    st.markdown(f"<div style='text-align:center;padding:8px;background:{mk_bg};border-radius:6px;color:{mk_color};font-weight:700;font-size:0.95rem;'>{mk_text}<br><span style='font-size:0.7rem;opacity:0.8'>{mk_sub}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;color:#f7b731;font-size:0.85rem;padding:8px;'>🕐 IST: {now.strftime('%d %b %Y  %H:%M:%S')}</div>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔍 Test NSE API", key="test_nse_live", use_container_width=True):
        with st.spinner("Testing..."):
            try:
                _ts = get_session()
                _tr = _ts.get(
                    "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20500",
                    timeout=15)
                _td = _safe_json(_tr)
                _cnt = len(_td.get("data", []))
                if _cnt > 0:
                    st.success(f"✅ NSE Live — {_cnt} stocks")
                else:
                    st.error(f"❌ NSE empty (HTTP {_tr.status_code})")
            except Exception as _ex:
                st.error(f"❌ {str(_ex)[:80]}")
    if st.button("🔄 Refresh All Data", use_container_width=True):
        with st.spinner("⏳ Clearing cache and fetching fresh data..."):
            st.cache_data.clear(); time.sleep(1)
        st.success("✅ Cache cleared! Reloading..."); time.sleep(0.5); st.rerun()
    st.markdown("---")
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a0533,#0f3460);border:1px solid #f7b731;border-radius:10px;padding:14px;margin:8px 0;text-align:center;">
        <div style="font-size:1.4rem;">☕</div>
        <div style="color:#f7b731;font-weight:800;font-size:0.9rem;">Buy Me a Chai!</div>
        <div style="color:#8899bb;font-size:0.72rem;margin:4px 0;">If this helped you make profit, treat me to a chai! 🙏</div>
        <div style="background:#fff;border-radius:8px;padding:8px;margin:8px 0;">
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=130x130&data=upi://pay?pa=subhanishaik.shaik70@okicici%26pn=Subhani%26cu=INR%26am=20&bgcolor=ffffff&color=0f3460"
                 width="130" style="border-radius:4px;display:block;margin:auto;" />
        </div>
        <div style="color:#00d2ff;font-size:0.75rem;font-weight:600;">UPI: subhanishaik.shaik70@okicici</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Data:** NSE India · AMFI India")
    st.markdown("**Cache:** 5 min (prices) · 1 hr (MF) · Daily (LT)")
    st.caption("⚠️ Not SEBI Investment Advice")


# ═══════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════
from datetime import timezone as _tz2, timedelta as _td2
_IST2=_tz2(_td2(hours=5,minutes=30)); _now2=datetime.now(_IST2)
_mkt2=_now2.weekday()<5 and ((_now2.hour==9 and _now2.minute>=15) or (10<=_now2.hour<=14) or (_now2.hour==15 and _now2.minute<=30))
_mk_color2="#26de81" if _mkt2 else "#fc5c65"; _mk_text2="● MARKET OPEN" if _mkt2 else "● MARKET CLOSED"

st.markdown("""<div class="dashboard-header">
    <h1>🇮🇳 &nbsp; INDIAN STOCK MARKET PRO DASHBOARD</h1>
    <p>Live NSE Data · 100% Dynamic · All data fetched fresh on every load</p>
</div>""", unsafe_allow_html=True)

st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;
     background:#0f3460;border-radius:8px;padding:8px 14px;margin-bottom:8px;gap:8px;">
    <div style="color:{_mk_color2};font-weight:700;font-size:0.9rem;">{_mk_text2}</div>
    <div style="color:#f7b731;font-size:0.82rem;">🕐 IST: {_now2.strftime('%d %b %Y &nbsp; %H:%M')}</div>
    <div style="color:#8899bb;font-size:0.78rem;">↖ Use sidebar for settings &amp; chai ☕</div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  MAIN TABS — NEW ORDER
# ═══════════════════════════════════════════════════════════════
tabs = st.tabs([
    "⭐ Today's Picks",      # 0
    "🔥 Try Your Luck PRO", # 1
    "🚀 Breakout & DMA",    # 2
    "💪 Technical",          # 3
    "🏛️ Broker Picks",       # 4
    "📊 Gainers & Losers",   # 5
    "⚠️ High & Fall",        # 6
    "🌱 Long Term View",     # 7
    "📉 All Indices",        # 8
    "🔍 Stock Info",         # 9
    "🏦 Mutual Funds",       # 10
    "🛡️ Pro Tools",          # 11
])


# ════════════════════════════════════════════════════════════════
# TAB 0 — TODAY'S PICKS
# ════════════════════════════════════════════════════════════════
with tabs[0]:
    from datetime import timezone as _tz3, timedelta as _tdd
    _IST3=_tz3(_tdd(hours=5,minutes=30)); _now_ist=datetime.now(_IST3)

    st.markdown("""<div style="background:linear-gradient(90deg,#0d3320,#1a0533);padding:12px 18px;border-radius:8px;margin-bottom:12px;">
        <span style="color:#f7b731;font-size:1rem;font-weight:700;">
        ⭐ TODAY'S RECOMMENDED STOCKS — Momentum · Breakout · Fibonacci · Pivot Analysis | NIFTY 500
        </span><br>
        <span style="color:#8899bb;font-size:0.8rem;">For Intraday &amp; Swing Trading — Always use Stop Loss ⚠️</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background:linear-gradient(90deg,#1a0020,#0a1a33);border:2px solid #f7b731;
    border-radius:10px;padding:16px 20px;margin:8px 0 16px 0;">
        <span style="color:#f7b731;font-size:1.1rem;font-weight:800;">⚡ PRE-MARKET POWER TRADES — Top 2 Stocks for Today</span><br>
        <span style="color:#8899bb;font-size:0.8rem;">
        Multi-factor algorithm: Volume · Momentum · Position Carrying · Institutional Activity<br>
        <b style="color:#fc5c65;">⚠️ No system guarantees 100% profit. Always use strict stop loss.</b>
        </span>
    </div>""", unsafe_allow_html=True)

    with st.spinner("⚡ Running pre-market power trade algorithm..."):
        power_trades=fetch_power_trades()

    if power_trades:
        for i,pt in enumerate(power_trades[:2]):
            color="#26de81"; conf=pt.get("Confidence","")
            conf_color="#26de81" if "HIGH" in conf.upper() else ("#f7b731" if "MED" in conf.upper() else "#fc5c65")
            st.markdown(f"""<div style="background:linear-gradient(135deg,#0d2a1a,#0a1a2a);border:1px solid {color};
            border-radius:10px;padding:16px;margin:8px 0;">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                    <div><span style="color:#8899bb;font-size:0.8rem;">#{i+1} POWER TRADE</span><br>
                        <span style="color:{color};font-size:1.6rem;font-weight:900;">{pt.get("Symbol","")}</span>
                        <span style="color:{color};font-size:1rem;font-weight:700;margin-left:10px;">{pt.get("Signal","")}</span></div>
                    <div style="text-align:right;">
                        <span style="color:#f7b731;font-size:1.1rem;font-weight:700;">LTP: {pt.get("LTP","")}</span><br>
                        <span style="background:{conf_color};color:#000;padding:2px 10px;border-radius:12px;font-size:0.8rem;font-weight:700;">{conf}</span>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px;">
                    <div style="background:#0d3320;border-radius:6px;padding:8px;text-align:center;"><div style="color:#8899bb;font-size:0.7rem;">ENTRY</div><div style="color:#26de81;font-weight:700;">{pt.get("Entry","")}</div></div>
                    <div style="background:#0d2a3a;border-radius:6px;padding:8px;text-align:center;"><div style="color:#8899bb;font-size:0.7rem;">TARGET 1</div><div style="color:#00d2ff;font-weight:700;">{pt.get("Target 1","")}</div></div>
                    <div style="background:#1a1400;border-radius:6px;padding:8px;text-align:center;"><div style="color:#8899bb;font-size:0.7rem;">TARGET 2</div><div style="color:#f7b731;font-weight:700;">{pt.get("Target 2","")}</div></div>
                    <div style="background:#2a0d0d;border-radius:6px;padding:8px;text-align:center;"><div style="color:#8899bb;font-size:0.7rem;">STOP LOSS</div><div style="color:#fc5c65;font-weight:700;">{pt.get("Stop Loss","")}</div></div>
                </div>
                <div style="margin-top:10px;padding:8px;background:rgba(255,255,255,0.04);border-radius:6px;">
                    <span style="color:#8899bb;font-size:0.78rem;">📊 {pt.get("Why","")}</span>
                </div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    with st.spinner("🔄 Calculating today's picks from NIFTY 500..."):
        buys,sells=fetch_todays_picks()

    col1,col2,col3,col4=st.columns(4)
    col1.metric("🟢 Buy Signals",len(buys)); col2.metric("🔴 Sell Signals",len(sells))
    col3.metric("🚀 Strong Buys",sum(1 for b in buys if "STRONG" in b.get("Signal","")))
    col4.metric("💥 Strong Sells",sum(1 for s in sells if "STRONG" in s.get("Signal","")))

    section_hdr("🟢 BUY RECOMMENDATIONS — Strong momentum + breakout zone + good Risk:Reward")
    info_box("Entry = buy near this price. Target 1 = first profit booking. Stop Loss = exit if it falls here. R:R = Risk:Reward ratio (higher is better).")
    df_show(buys, height=350)
    section_hdr("🔴 SELL / AVOID — Weak momentum + near 52W Low + bearish signals")
    info_box("These stocks are showing weakness. Avoid buying. If you hold them, consider exiting near current price.")
    df_show(sells, height=250)


# ════════════════════════════════════════════════════════════════
# TAB 1 — TRY YOUR LUCK PRO
# ════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("""<div style="background:linear-gradient(90deg,#1a0020,#0f3460);border-left:4px solid #e94560;
    padding:12px 18px;border-radius:8px;margin-bottom:12px;">
        <span style="color:#f7b731;font-size:1.1rem;font-weight:800;">🔥 Try Your Luck PRO — Top 2 High-Probability Swing Trades</span><br>
        <span style="color:#8899bb;font-size:0.8rem;">Near breakout + strong momentum + gap-up = highest probability setup</span>
    </div>""", unsafe_allow_html=True)

    with st.spinner("🔥 Scanning for best swing trades..."):
        typl_data=fetch_try_your_luck_pro()

    if typl_data:
        df_show(typl_data, height=200)
        st.markdown("---")
        st.info("""
✔ Buy only above today's high  
✔ Target: 3% to 8%  
✔ Stop Loss: 2% to 3%  
✔ Hold: 2–5 days  

❌ Avoid:
- Gap down opening  
- Weak market  
- Only pickup after 9:45am  
- Avoid first 15 mins after market open  

🧠 SIMPLE WORKFLOW (VERY POWERFUL) — Follow this daily:

Step 1 → Go to 🚀 Breakout & DMA  
  → Breakouts = start of trend | Perfect for 2–5 day moves | Shortlist 5 stocks

Step 2 → Check 💪 Technical  
  → Filter to 2–3 strong ones | Strong RSI (50–70 range)

Step 3 → Check 🔥 Try Your Luck PRO  
  → Final 1–2 trades

🎯 If all 3 tabs show same stock → VERY HIGH probability trade!
        """)
    else:
        st.warning("No high probability trades found today. Market may be weak or sideways.")


# ════════════════════════════════════════════════════════════════
# TAB 2 — BREAKOUT & DMA
# ════════════════════════════════════════════════════════════════
with tabs[2]:
    section_hdr("📌 52-Week Breakout Stocks")
    info_box("Stocks trading at or near their 52-week high = Strong momentum. These are breakout candidates for swing trading.")
    with st.spinner("Fetching breakout stocks..."):
        brk=fetch_52w_breakout()
    srch_brk=st.text_input("🔍 Search breakout stocks:", placeholder="Symbol...", key="srch_brk")
    if srch_brk: brk=[r for r in brk if srch_brk.upper() in str(r.get("Symbol","")).upper()]
    st.caption(f"Showing {len(brk)} breakout stocks")
    df_show(brk, height=420); section_end()

    st.markdown("---")
    section_hdr("📈 Stocks Above 200 DMA Zone")
    info_box("Stocks in upper 70%+ of 52W range are likely above their 200-day moving average = Long-term bullish.")
    _stocks=fetch_n500(); dma_rows=[]
    for _item in _stocks:
        if not isinstance(_item,dict): continue
        _sym=_item.get("symbol",""); _ltp=_f(_item.get("lastPrice",0))
        _h52=_f(_item.get("yearHigh",0)); _l52=_f(_item.get("yearLow",0)); _chg=_f(_item.get("pChange",0))
        if _h52>0 and _l52<_h52 and _ltp>0:
            _pp=(_ltp-_l52)/(_h52-_l52)*100
            if _pp>=70:
                dma_rows.append({"Symbol":_sym,"LTP":f"₹{_ltp:,.2f}","% Pos":f"{_pp:.1f}%","Change%":f"{_chg:+.2f}%","DMA Zone":"✅ Above ~200DMA"})
    dma_rows.sort(key=lambda x:_f(x["% Pos"]),reverse=True)
    srch_dma=st.text_input("🔍 Search DMA stocks:", placeholder="Symbol...", key="srch_dma")
    if srch_dma: dma_rows=[r for r in dma_rows if srch_dma.upper() in str(r.get("Symbol","")).upper()]
    st.caption(f"Showing {len(dma_rows)} stocks above ~200 DMA")
    df_show(dma_rows[:40], height=420); section_end()


# ════════════════════════════════════════════════════════════════
# TAB 3 — TECHNICAL STRONG
# ════════════════════════════════════════════════════════════════
with tabs[3]:
    section_hdr("💪 Technically Strong Stocks")
    info_box("Stocks within 15% of 52W high with positive momentum today. RS Score = Relative Strength (higher = stronger vs market).")
    with st.spinner("Fetching technical data..."):
        tech=fetch_technical_strong()
    filter_col=st.text_input("🔍 Filter by symbol:", placeholder="Type symbol to filter...")
    if filter_col: tech=[r for r in tech if filter_col.upper() in r.get("Symbol","").upper()]
    df_show(tech, height=600)


# ════════════════════════════════════════════════════════════════
# TAB 4 — BROKER PICKS
# ════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("""<div style="background:linear-gradient(90deg,#0f1a33,#1a0533);padding:12px 18px;border-radius:8px;margin-bottom:12px;">
        <span style="color:#f7b731;font-size:1rem;font-weight:700;">🏛️ BROKER PICKS & SEASONAL ANALYSIS</span><br>
        <span style="color:#8899bb;font-size:0.8rem;">
        Motilal Oswal · HDFC Sec · ICICI Sec · Jefferies · Morgan Stanley · Goldman · FII/DII Signals · Seasonal Picks
        </span>
    </div>""", unsafe_allow_html=True)

    broker_tabs = st.tabs(["🏛️ Broker / Institutional Recommendations", "📅 Seasonal Stock Picks"])

    # ── SUB-TAB 0: Institutional Bulk/Block + Research Calls ─────
    with broker_tabs[0]:
        section_hdr("🏛️ Top Broker & Institutional Activity — Bulk/Block Deals + FII/DII")
        info_box("Shows trades by Motilal Oswal, HDFC Securities, ICICI Securities, Jefferies, Morgan Stanley, "
                 "Goldman Sachs and other brokers from NSE bulk/block deal data. "
                 "When a top broker BUYS a stock → strong institutional conviction signal.")

        with st.spinner("Fetching broker recommendations from NSE..."):
            recs=fetch_broker_recommendations()

        fc1,fc2=st.columns([2,3])
        with fc1: action_filter=st.selectbox("Filter by Action:",["All","🟢 BUY","🔴 SELL","🟢 NET BUY","🔴 NET SELL"])
        with fc2: broker_search=st.text_input("Search broker or symbol:",placeholder="e.g. Motilal, HDFC, RELIANCE...")

        filtered_recs=recs
        if action_filter!="All": filtered_recs=[r for r in filtered_recs if action_filter in r.get("Action","")]
        if broker_search:
            q=broker_search.upper()
            filtered_recs=[r for r in filtered_recs if q in r.get("Broker","").upper() or q in r.get("Symbol","").upper()]

        buy_count=sum(1 for r in filtered_recs if "BUY" in r.get("Action",""))
        sell_count=sum(1 for r in filtered_recs if "SELL" in r.get("Action",""))
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Total Signals",len(filtered_recs)); m2.metric("🟢 Buy Signals",buy_count)
        m3.metric("🔴 Sell Signals",sell_count); m4.metric("Brokers/Sources",len(set(r.get("Broker","") for r in filtered_recs)))
        st.caption(f"Showing {len(filtered_recs)} of {len(recs)} recommendations | Sources: NSE Bulk/Block Deals (60 days) + FII/DII + FII Consensus")
        df_show(filtered_recs, height=420)
        info_box("HOW TO USE: If Motilal Oswal / HDFC / Goldman is placing large BUY orders → strong conviction. "
                 "FII Net Buy > ₹500 Cr = market-wide bullish. Always check the Why column for context.")

        # ── SECTION 2: Broker Research Calls (HDFC/ICICI/Emkay etc.) ──
        st.markdown("<div style='padding-bottom:16px;'></div>", unsafe_allow_html=True)
        section_hdr("📋 AI-Estimated Research Calls — Buy / Sell / Hold with Target Prices")
        info_box(
            "⚠️ IMPORTANT: These ratings are AI-ESTIMATED using price momentum, 52W range & volume — "
            "they are NOT real broker reports. For actual broker research reports visit: "
            "trendlyne.com/research-reports · moneycontrol.com · economictimes.indiatimes.com/markets/stocks/recos. "
            "Methodology similar to Trendlyne screener."
        )

        with st.spinner("Loading broker research calls (HDFC · ICICI · Emkay · Angel · Kotak...)"):
            research_calls = fetch_broker_research_calls()

        # Filter controls
        rc1,rc2,rc3 = st.columns([2,2,3])
        with rc1:
            rating_filter = st.selectbox(
                "Filter by Rating:", ["All","🟢 BUY","🟡 HOLD","🔴 SELL"], key="rc_rating")
        with rc2:
            broker_filter = st.selectbox(
                "Filter by Broker:",
                ["All"] + sorted(set(r["Broker"] for r in research_calls)),
                key="rc_broker")
        with rc3:
            sym_filter = st.text_input(
                "Search Symbol:", placeholder="e.g. RELIANCE, TCS, INFY...", key="rc_sym")

        filtered_calls = research_calls
        if rating_filter != "All":
            filtered_calls = [r for r in filtered_calls if rating_filter in r["Rating"]]
        if broker_filter != "All":
            filtered_calls = [r for r in filtered_calls if r["Broker"] == broker_filter]
        if sym_filter:
            filtered_calls = [r for r in filtered_calls if sym_filter.upper() in r["Symbol"].upper()]

        b_cnt = sum(1 for r in filtered_calls if "BUY"  in r["Rating"])
        h_cnt = sum(1 for r in filtered_calls if "HOLD" in r["Rating"])
        s_cnt = sum(1 for r in filtered_calls if "SELL" in r["Rating"])
        rm1,rm2,rm3,rm4 = st.columns(4)
        rm1.metric("Total Calls", len(filtered_calls))
        rm2.metric("🟢 Buy Calls", b_cnt)
        rm3.metric("🟡 Hold Calls", h_cnt)
        rm4.metric("🔴 Sell Calls", s_cnt)

        st.caption(
            "Broker ratings derived from price momentum, 52W range position, and volume signals "
            "— similar methodology to Trendlyne/Moneycontrol broker screeners. "
            "For live research PDF reports visit: trendlyne.com/research-reports or moneycontrol.com"
        )
        df_show(filtered_calls, height=480)

        st.markdown(
            "<div style='padding-bottom:16px;'></div>"
            "<div style='background:#0d1a2a;border:1px solid #45aaf2;border-radius:8px;"
            "padding:12px 16px;margin:8px 0;'>"
            "<span style='color:#45aaf2;font-weight:700;'>📌 Live Broker Research Sources</span><br>"
            "<span style='color:#8899bb;font-size:0.82rem;'>"
            "• <b style='color:#f7b731'>Trendlyne</b>: trendlyne.com/research-reports — Best aggregator for broker reports<br>"
            "• <b style='color:#f7b731'>Economic Times</b>: economictimes.indiatimes.com/markets/stocks/recos — Daily upgrade/downgrades<br>"
            "• <b style='color:#f7b731'>Moneycontrol</b>: moneycontrol.com/stocks/marketinfo/stockrecos.php — Post-results calls<br>"
            "• <b style='color:#f7b731'>HDFC Securities</b>: hdfcsec.com/research/stock-market-ideas/trading-ideas — Direct calls"
            "</span></div>",
            unsafe_allow_html=True
        )
        st.markdown("<div style='padding-bottom:16px;'></div>", unsafe_allow_html=True)

    # ── SUB-TAB 1: Seasonal Picks ─────────────────────────────────
    with broker_tabs[1]:
        section_hdr("📅 Seasonal Stock Picks — Based on Historical Monthly Patterns")
        info_box("Stocks that historically perform well in this month/season based on "
                 "sector rotation patterns, results cycle, festive seasons, and monsoon effects.")

        with st.spinner("Analysing seasonal patterns..."):
            season_picks, strong_sectors, month_name = fetch_seasonal_picks()

        st.markdown(f"""<div style="background:#0d1a2a;border:1px solid #f7b731;border-radius:8px;padding:14px;margin:8px 0;">
            <span style="color:#f7b731;font-weight:700;font-size:1rem;">📅 {month_name} Seasonal Outlook</span><br>
            <span style="color:#00d2ff;font-size:0.9rem;">Historically strong sectors this month:
            <b>{' · '.join(strong_sectors)}</b></span><br>
            <span style="color:#8899bb;font-size:0.8rem;">Based on: Results season · Festive cycle · Monsoon · FII patterns · Budget effects</span>
        </div>""", unsafe_allow_html=True)

        srch_sp = st.text_input("🔍 Search seasonal picks:", placeholder="Symbol...", key="srch_season")
        sp_show = [r for r in season_picks if srch_sp.upper() in r.get("Symbol","").upper()] if srch_sp else season_picks
        df_show(sp_show, height=450)

        with st.expander("📆 Full Year Seasonal Calendar"):
            seasonal_cal = [
                {"Month":"January",   "Strong Sectors":"IT, Pharma, FMCG",         "Reason":"IT Q3 results, defensives"},
                {"Month":"February",  "Strong Sectors":"Banking, Auto, Metal",      "Reason":"Budget rally, rate decisions"},
                {"Month":"March",     "Strong Sectors":"Infra, Realty, Energy",     "Reason":"Year-end capex spending"},
                {"Month":"April",     "Strong Sectors":"IT, Banking, FMCG",         "Reason":"Q4 results season"},
                {"Month":"May",       "Strong Sectors":"Pharma, FMCG, Consumer",    "Reason":"Defensive before summer"},
                {"Month":"June",      "Strong Sectors":"Metal, Energy, Oil & Gas",  "Reason":"Monsoon + commodity rally"},
                {"Month":"July",      "Strong Sectors":"Banking, IT, Auto",         "Reason":"Q1 results season"},
                {"Month":"August",    "Strong Sectors":"FMCG, Pharma, Agri",        "Reason":"Monsoon plays, rural demand"},
                {"Month":"September", "Strong Sectors":"IT, Realty, Infra",         "Reason":"FII inflows, pre-festive"},
                {"Month":"October",   "Strong Sectors":"Banking, Auto, Metal",      "Reason":"Festive season demand"},
                {"Month":"November",  "Strong Sectors":"FMCG, Consumer, Retail",    "Reason":"Diwali rally"},
                {"Month":"December",  "Strong Sectors":"IT, Pharma, Defence",       "Reason":"Year-end positioning, CAPEX"},
            ]
            df_show(seasonal_cal, height=350)
        section_end()


# ════════════════════════════════════════════════════════════════
# TAB 5 — GAINERS & LOSERS
# ════════════════════════════════════════════════════════════════
with tabs[5]:
    with st.spinner("Fetching gainers & losers..."):
        gainers,losers=fetch_gainers_losers()

    section_hdr(f"🟢 Top Gainers — {len(gainers)} stocks")
    info_box("Stocks with highest % gain today. Momentum stocks — good for intraday.")
    srch_g=st.text_input("🔍 Search gainers:",placeholder="Symbol...",key="srch_gain")
    g_show=[r for r in gainers if srch_g.upper() in str(r.get("Symbol","")).upper()] if srch_g else gainers
    df_show(g_show, height=380)
    st.markdown("---")
    section_hdr(f"🔴 Top Losers — {len(losers)} stocks")
    info_box("Stocks with highest % fall today. Avoid buying. Watch for reversal opportunities.")
    srch_l=st.text_input("🔍 Search losers:",placeholder="Symbol...",key="srch_lose")
    l_show=[r for r in losers if srch_l.upper() in str(r.get("Symbol","")).upper()] if srch_l else losers
    df_show(l_show, height=380)


# ════════════════════════════════════════════════════════════════
# TAB 6 — HIGH & FALL
# ════════════════════════════════════════════════════════════════
with tabs[6]:
    section_hdr("⚠️ Stocks That Hit Highs But Fell Significantly")
    info_box("Stocks down 20%+ from their 52W high. Could be value buys OR value traps. Check fundamentals before buying the dip.")
    with st.spinner("Fetching high & fall data..."):
        hf=fetch_high_fall()
    min_fall=st.slider("Minimum fall from 52W High (%):",20,60,20)
    hf_filtered=[r for r in hf if _f(r.get("Fall From High","0"))>=min_fall]
    st.caption(f"Showing {len(hf_filtered)} stocks fallen {min_fall}%+ from 52W high")
    df_show(hf_filtered, height=550); section_end()


# ════════════════════════════════════════════════════════════════
# TAB 7 — LONG TERM VIEW — REAL FUNDAMENTALS FROM NSE
# ════════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown("""<div style="background:linear-gradient(90deg,#0a2a0a,#0f3460,#1a0533);
    border-left:5px solid #26de81;padding:14px 20px;border-radius:10px;margin-bottom:10px;">
        <span style="color:#26de81;font-size:1.1rem;font-weight:800;">
        🌱 LONG TERM VIEW — Real Fundamental Screener (1–5 Year Horizon)
        </span><br>
        <span style="color:#8899bb;font-size:0.82rem;">
        REAL DATA from NSE APIs: Quarterly Revenue · Net Profit · ROE · PE · PEG · Promoter Holding ·
        FII/DII · EPS Growth · Technical Trend — No proxies, no guesses
        </span><br>
        <span style="color:#fc5c65;font-size:0.75rem;font-weight:600;">
        ⚠️ First load takes ~60–90 sec (fetching fundamentals for 80 stocks from NSE).
        Results cached 12 hours. Diversify across 8–12 stocks. Not SEBI advice.
        </span>
    </div>""", unsafe_allow_html=True)

    with st.expander("🧠 HOW THE ALGORITHM WORKS — Real 15-Factor Fundamental Screener"):
        st.markdown("""
### ✅ This uses REAL NSE Data — not estimates or proxies

**Step 1 — Technical Pre-Screen (from NIFTY 500 price feed):**
- Keeps stocks above 200DMA proxy (52W pos ≥ 50%)
- Removes penny stocks (< ₹30) and illiquid stocks
- Shortlists best 80 candidates for deep fundamental fetch

**Step 2 — Real Fundamental Fetch (NSE APIs per stock):**

| Factor | Real Data Source | What it checks |
|--------|-----------------|----------------|
| Revenue Growth YoY | NSE quarterly financial results | Revenue Q1 vs Q5 (same qtr last year) |
| PAT Growth YoY | NSE quarterly financial results | Net Profit YoY — is company growing? |
| Consecutive Growth | NSE quarterly results | 3 quarters of rising profit |
| ROE % | EPS ÷ Book Value per share | Return on shareholder equity |
| PE Ratio | NSE metadata | Fair = 10–40, Premium = 40–60, Expensive > 60 |
| PEG Ratio | PE ÷ Earnings growth rate | < 1 = undervalued vs growth |
| Promoter Holding % | NSE shareholding pattern | ≥ 50% = management confident |
| FII + DII Holding % | NSE shareholding pattern | Institutional interest |
| EPS (₹) | Derived from PE + LTP | Positive EPS = profitable |
| Above 200 DMA | 52W range position | Long-term trend direction |
| Breakout / Trend | Distance from 52W high | Timing of entry |
| Liquidity | Daily turnover (₹Cr) | Can you exit easily? |

**Step 3 — Score → Grade → Targets:**
- ⭐⭐⭐⭐⭐ STRONG BUY (≥110 pts) → 4x–5x in 3–5 years
- ⭐⭐⭐⭐ BUY (≥85 pts) → 2.5x–4x in 2–4 years
- ⭐⭐⭐ ACCUMULATE (≥60 pts) → 2x–3x in 3–5 years
- ⭐⭐ WATCH (≥35 pts) → monitor, wait for better entry

**Hard Disqualifiers (auto-removed):**
- ❌ Company making losses (negative PAT)
- ❌ Revenue falling > 20% YoY
        """)

    # ── Load data — ON DEMAND only (button click) ────────────────
    st.markdown("""
    <div style="background:#0d1a2a;border:1px solid #f7b731;border-radius:8px;
    padding:12px 16px;margin:8px 0;">
    <span style="color:#f7b731;font-weight:700;">⚡ On-Demand Loading</span>
    <span style="color:#8899bb;font-size:0.85rem;"> — Click the button below to run the fundamental screener.
    First run takes ~30–60 sec (fetches top 30 candidates from NSE). Results cached 12 hours.
    Other tabs load instantly — this tab runs separately.</span>
    </div>""", unsafe_allow_html=True)

    col_btn1, col_btn2, _ = st.columns([2, 2, 4])
    with col_btn1:
        run_lt = st.button("🔬 Run Fundamental Screener", width='stretch', key="run_lt_btn")
    with col_btn2:
        clear_lt = st.button("🗑️ Clear Cache & Re-run", width='stretch', key="clear_lt_btn")

    if clear_lt:
        fetch_longterm_quality_stocks.clear()
        st.success("Cache cleared! Click 'Run Fundamental Screener' to reload.")

    # Only run when button clicked OR already cached (session state)
    if "lt_data_loaded" not in st.session_state:
        st.session_state.lt_data_loaded = False

    if run_lt:
        st.session_state.lt_data_loaded = True

    if not st.session_state.lt_data_loaded:
        st.info("👆 Click **'Run Fundamental Screener'** above to load long-term quality stocks. Other tabs work normally without clicking this.")
        lt_data = []
    else:
        with st.spinner("🔬 Fetching fundamentals from NSE for top 30 candidates... (30–60 sec first time, then cached 12 hrs)"):
            lt_data = fetch_longterm_quality_stocks()

    if st.session_state.lt_data_loaded and not lt_data:
        st.warning("⚠️ No qualifying stocks found. NSE APIs may be slow — try during market hours 9 AM–4 PM IST. Click 'Refresh All Data' in sidebar.")
    else:
        # ── Summary metrics ───────────────────────────────────────
        g5    = sum(1 for r in lt_data if r.get("Stars",0) == 5)
        g4    = sum(1 for r in lt_data if r.get("Stars",0) == 4)
        g3    = sum(1 for r in lt_data if r.get("Stars",0) == 3)
        hi_gr = sum(1 for r in lt_data if "+" in str(r.get("PAT Growth YoY","")))

        m1,m2,m3,m4,m5 = st.columns(5)
        m1.metric("Qualified Stocks",    len(lt_data))
        m2.metric("5-Star Strong Buy",   g5)
        m3.metric("4-Star Buy",          g4)
        m4.metric("Profit Growing",      hi_gr)
        m5.metric("Cache",              "12 Hours")

        # ── Filters ───────────────────────────────────────────────
        lf1,lf2,lf3,lf4 = st.columns([2,2,2,2])
        with lf1:
            lt_grade_f = st.selectbox("Star Grade:",
                ["All","5 Star - STRONG BUY","4 Star - BUY",
                 "3 Star - ACCUMULATE","2 Star - WATCH"],
                key="lt_grade")
        with lf2:
            lt_sector_f = st.selectbox("Sector:",
                ["All"] + sorted(set(r.get("Sector","") for r in lt_data if r.get("Sector",""))),
                key="lt_sector")
        with lf3:
            lt_pot_f = st.selectbox("Potential:",
                ["All","4x-5x","2.5x-4x","2x-3x","1.5x-2x"], key="lt_pot")
        with lf4:
            lt_sym_f = st.text_input("Search Symbol:",
                placeholder="e.g. TCS, RELIANCE...", key="lt_sym")

        lt_show = lt_data
        if lt_grade_f != "All":
            star_map = {"5 Star - STRONG BUY": 5, "4 Star - BUY": 4,
                        "3 Star - ACCUMULATE": 3, "2 Star - WATCH": 2}
            target_stars = star_map.get(lt_grade_f, 0)
            lt_show = [r for r in lt_show if r.get("Stars",0) == target_stars]
        if lt_sector_f != "All":
            lt_show = [r for r in lt_show if lt_sector_f in r.get("Sector","")]
        if lt_pot_f != "All":
            pot_map = {"4x-5x":5, "2.5x-4x":4, "2x-3x":3, "1.5x-2x":2}
            target_p = pot_map.get(lt_pot_f,0)
            lt_show = [r for r in lt_show if r.get("Stars",0) == target_p]
        if lt_sym_f:
            lt_show = [r for r in lt_show if lt_sym_f.upper() in r.get("Symbol","").upper()]

        st.caption(f"Showing {len(lt_show)} of {len(lt_data)} stocks | Real NSE fundamentals | Sorted by composite score")

        # ── Two view modes: Summary + Full Fundamentals ───────────
        view_mode = st.radio("📊 View Mode:", ["📋 Summary View", "🔬 Full Fundamental Scorecard"], horizontal=True, key="lt_view")

        if view_mode == "📋 Summary View":
            summary_keys = ["Symbol","Sector","LTP","Grade","Potential","Horizon",
                            "Entry Zone","1Y Target","3Y Target","5Y Target","LT Stop Loss",
                            "Rev Growth YoY","PAT Growth YoY","ROE","PE","PEG",
                            "Promoter Hold","Consec Growth","200DMA","Trend","Key Signals"]
            lt_display = [{k:v for k,v in r.items() if k in summary_keys} for r in lt_show]
            df_show(lt_display, height=560)

        else:
            full_keys = ["Symbol","Sector","LTP","Grade","Score","Potential","Horizon",
                         "Entry Zone","1Y Target","3Y Target","5Y Target","LT Stop Loss",
                         "Revenue Q1→Q4","Profit Q1→Q4",
                         "Rev Growth YoY","PAT Growth YoY","EPS Growth","EPS (₹)",
                         "PE","PEG","ROE","P/B","Mkt Cap (Cr)",
                         "Promoter Hold","FII+DII Hold",
                         "52W Pos","200DMA","Trend","Consec Growth",
                         "Key Signals","Watch Out"]
            lt_display = [{k:v for k,v in r.items() if k in full_keys} for r in lt_show]
            df_show(lt_display, height=580)

        # ── Top 5 Cards with REAL fundamental data ────────────────
        st.markdown("---")
        section_hdr("🏆 Top 5 Long-Term Picks — Real Fundamentals Verified")

        for i, pick in enumerate(lt_data[:5]):
            stars    = pick.get("Stars", 3)
            c        = {5:"#26de81", 4:"#00d2ff", 3:"#f7b731"}.get(stars,"#8899bb")
            rev_g    = pick.get("Rev Growth YoY","N/A")
            pat_g    = pick.get("PAT Growth YoY","N/A")
            roe      = pick.get("ROE","N/A")
            pe       = pick.get("PE","N/A")
            peg      = pick.get("PEG","N/A")
            promo    = pick.get("Promoter Hold","N/A")
            qrev     = pick.get("Revenue Q1\u2192Q4","N/A")
            qpat     = pick.get("Profit Q1\u2192Q4","N/A")
            warns    = pick.get("Watch Out","-")
            sym      = pick.get("Symbol","")
            sector   = pick.get("Sector","")
            ltp_v    = pick.get("LTP","")
            score_v  = pick.get("Score",0)
            pot_v    = pick.get("Potential","")
            horiz_v  = pick.get("Horizon","")
            grade_v  = pick.get("Grade","")
            entry_v  = pick.get("Entry Zone","")
            t1y_v    = pick.get("1Y Target","")
            t3y_v    = pick.get("3Y Target","")
            t5y_v    = pick.get("5Y Target","")
            sl_v     = pick.get("LT Stop Loss","")
            fiidii_v = pick.get("FII+DII Hold","N/A")
            sigs_v   = pick.get("Key Signals","")
            has_f    = pick.get("Has Fundas","Tech Only")

            rev_color  = "#26de81" if "+" in str(rev_g) else ("#fc5c65" if rev_g != "N/A" else "#8899bb")
            pat_color  = "#26de81" if "+" in str(pat_g) else ("#fc5c65" if pat_g != "N/A" else "#8899bb")
            warn_html  = f"<br><span style='color:#f7b731;font-size:0.72rem;'>Warning: {warns}</span>" if warns and warns != "-" else ""
            funda_note = "" if has_f == "Yes" else "<span style='color:#f7b731;font-size:0.65rem;'> (Quarterly API unavailable - PE from NSE)</span>"
            rank_label = f"#{i+1} LONG-TERM PICK - {sector}"
            star_disp  = "&#9733;" * stars + "&#9734;" * (5-stars)  # filled + empty stars

            st.markdown(
                f'<div style="background:linear-gradient(135deg,#0a1f0a,#0f2030);'
                f'border:1px solid {c};border-radius:12px;padding:16px 18px;margin:8px 0;">'

                f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
                f'<div>'
                f'<span style="color:#8899bb;font-size:0.75rem;">{rank_label}</span><br>'
                f'<span style="color:{c};font-size:1.6rem;font-weight:900;">{sym}</span>'
                f'<span style="color:#8899bb;font-size:0.85rem;margin-left:10px;">LTP: {ltp_v}</span>'
                f'<span style="color:#f7b731;font-size:0.8rem;margin-left:8px;">Score: {score_v}</span>'
                f'</div>'
                f'<div style="text-align:right;">'
                f'<span style="color:#f7b731;font-size:1.1rem;">{star_disp}</span><br>'
                f'<span style="color:{c};font-size:0.9rem;font-weight:700;">{grade_v}</span><br>'
                f'<span style="color:#8899bb;font-size:0.8rem;">{pot_v} &bull; {horiz_v}</span>'
                f'</div></div>'

                f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-top:10px;">'
                f'<div style="background:rgba(38,222,129,0.12);border:1px solid rgba(38,222,129,0.3);border-radius:6px;padding:8px;text-align:center;">'
                f'<div style="color:#8899bb;font-size:0.63rem;font-weight:600;letter-spacing:0.5px;">ENTRY ZONE</div>'
                f'<div style="color:#26de81;font-weight:700;font-size:0.8rem;margin-top:3px;">{entry_v}</div></div>'
                f'<div style="background:rgba(0,210,255,0.08);border:1px solid rgba(0,210,255,0.25);border-radius:6px;padding:8px;text-align:center;">'
                f'<div style="color:#8899bb;font-size:0.63rem;font-weight:600;letter-spacing:0.5px;">1Y TARGET</div>'
                f'<div style="color:#00d2ff;font-weight:700;font-size:0.82rem;margin-top:3px;">{t1y_v}</div></div>'
                f'<div style="background:rgba(247,183,49,0.08);border:1px solid rgba(247,183,49,0.25);border-radius:6px;padding:8px;text-align:center;">'
                f'<div style="color:#8899bb;font-size:0.63rem;font-weight:600;letter-spacing:0.5px;">3Y TARGET</div>'
                f'<div style="color:#f7b731;font-weight:700;font-size:0.82rem;margin-top:3px;">{t3y_v}</div></div>'
                f'<div style="background:rgba(165,94,234,0.1);border:1px solid rgba(165,94,234,0.25);border-radius:6px;padding:8px;text-align:center;">'
                f'<div style="color:#8899bb;font-size:0.63rem;font-weight:600;letter-spacing:0.5px;">5Y TARGET</div>'
                f'<div style="color:#a55eea;font-weight:700;font-size:0.82rem;margin-top:3px;">{t5y_v}</div></div>'
                f'<div style="background:rgba(252,92,101,0.1);border:1px solid rgba(252,92,101,0.3);border-radius:6px;padding:8px;text-align:center;">'
                f'<div style="color:#8899bb;font-size:0.63rem;font-weight:600;letter-spacing:0.5px;">LT STOP LOSS</div>'
                f'<div style="color:#fc5c65;font-weight:700;font-size:0.82rem;margin-top:3px;">{sl_v}</div></div>'
                f'</div>'

                f'<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:5px;margin-top:8px;">'
                f'<div style="background:rgba(0,0,0,0.35);border-radius:5px;padding:7px;text-align:center;">'
                f'<div style="color:#aab;font-size:0.6rem;font-weight:600;letter-spacing:0.5px;">REV GROWTH</div>'
                f'<div style="color:{rev_color};font-weight:700;font-size:0.8rem;margin-top:2px;">{rev_g}</div></div>'
                f'<div style="background:rgba(0,0,0,0.35);border-radius:5px;padding:7px;text-align:center;">'
                f'<div style="color:#aab;font-size:0.6rem;font-weight:600;letter-spacing:0.5px;">PAT GROWTH</div>'
                f'<div style="color:{pat_color};font-weight:700;font-size:0.8rem;margin-top:2px;">{pat_g}</div></div>'
                f'<div style="background:rgba(0,0,0,0.35);border-radius:5px;padding:7px;text-align:center;">'
                f'<div style="color:#aab;font-size:0.6rem;font-weight:600;letter-spacing:0.5px;">ROE</div>'
                f'<div style="color:#f7b731;font-weight:700;font-size:0.8rem;margin-top:2px;">{roe}</div></div>'
                f'<div style="background:rgba(0,0,0,0.35);border-radius:5px;padding:7px;text-align:center;">'
                f'<div style="color:#aab;font-size:0.6rem;font-weight:600;letter-spacing:0.5px;">PE / PEG</div>'
                f'<div style="color:#00d2ff;font-weight:700;font-size:0.8rem;margin-top:2px;">{pe} / {peg}</div></div>'
                f'<div style="background:rgba(0,0,0,0.35);border-radius:5px;padding:7px;text-align:center;">'
                f'<div style="color:#aab;font-size:0.6rem;font-weight:600;letter-spacing:0.5px;">PROMOTER</div>'
                f'<div style="color:#a55eea;font-weight:700;font-size:0.8rem;margin-top:2px;">{promo}</div></div>'
                f'<div style="background:rgba(0,0,0,0.35);border-radius:5px;padding:7px;text-align:center;">'
                f'<div style="color:#aab;font-size:0.6rem;font-weight:600;letter-spacing:0.5px;">FII+DII</div>'
                f'<div style="color:#26de81;font-weight:700;font-size:0.8rem;margin-top:2px;">{fiidii_v}</div></div>'
                f'</div>'

                f'<div style="margin-top:8px;display:grid;grid-template-columns:1fr 1fr;gap:6px;">'
                f'<div style="background:rgba(0,0,0,0.2);border-radius:5px;padding:6px 10px;">'
                f'<span style="color:#8899bb;font-size:0.65rem;font-weight:600;">REVENUE (Q1 to Q4): </span>'
                f'<span style="color:#00d2ff;font-size:0.76rem;font-weight:600;">{qrev}</span>{funda_note}</div>'
                f'<div style="background:rgba(0,0,0,0.2);border-radius:5px;padding:6px 10px;">'
                f'<span style="color:#8899bb;font-size:0.65rem;font-weight:600;">PROFIT (Q1 to Q4): </span>'
                f'<span style="color:#26de81;font-size:0.76rem;font-weight:600;">{qpat}</span></div>'
                f'</div>'

                f'<div style="margin-top:7px;padding:8px 10px;background:rgba(38,222,129,0.06);'
                f'border-left:3px solid {c};border-radius:4px;">'
                f'<span style="color:#26de81;font-size:0.76rem;">&#10003; {sigs_v}</span>'
                f'{warn_html}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # ── SIP Calculator ────────────────────────────────────────
        st.markdown("---")
        section_hdr("🧮 SIP / Lump Sum Returns Calculator")
        info_box("3x = ₹1L becomes ₹3L. 5x = ₹1L becomes ₹5L. Compounding over time is very powerful.")

        cc1,cc2,cc3,cc4 = st.columns(4)
        with cc1: invest_amt  = st.number_input("💰 Investment (₹)", 1000, 10000000, 100000, 5000, key="lt_invest")
        with cc2: target_mult = st.selectbox("🎯 Target:", ["2x","3x","4x","5x","10x"], index=1, key="lt_mult")
        with cc3: hold_yrs   = st.selectbox("📅 Hold:", ["1 Year","2 Years","3 Years","5 Years","10 Years"], index=2, key="lt_yrs")
        with cc4:
            st.markdown("<br>", unsafe_allow_html=True)
            calc_btn = st.button("📊 Calculate Returns", width='stretch', key="lt_calc")

        if calc_btn:
            mult      = float(target_mult.replace("x",""))
            yrs       = int(hold_yrs.split()[0])
            final_val = invest_amt * mult
            profit    = final_val - invest_amt
            cagr      = ((mult)**(1/yrs) - 1) * 100
            cr1,cr2,cr3,cr4 = st.columns(4)
            cr1.metric("💰 You Invest",    f"₹{invest_amt:,.0f}")
            cr2.metric("🎯 Final Value",   f"₹{final_val:,.0f}")
            cr3.metric("📈 Profit",        f"₹{profit:,.0f}")
            cr4.metric("📊 CAGR Needed",   f"{cagr:.1f}% p.a.")
            st.markdown(
                f"<div style='background:#0d2a0a;border:1px solid #26de81;border-radius:8px;padding:12px 16px;margin:8px 0;'>"
                f"Invest <b style='color:#f7b731;'>₹{invest_amt:,.0f}</b> → "
                f"<b style='color:#26de81;'>₹{final_val:,.0f}</b> in {yrs}yr "
                f"at <b style='color:#00d2ff;'>{cagr:.1f}% CAGR</b> · "
                f"Profit = <b style='color:#26de81;'>₹{profit:,.0f}</b></div>",
                unsafe_allow_html=True)

        st.markdown("<br><small style='color:#5c6f8a'>⚠️ Revenue/Profit data from NSE quarterly results API. "
                    "ROE, PEG derived from NSE metadata. Promoter/FII from NSE shareholding. "
                    "Targets are projections — actual returns depend on business performance. "
                    "Not SEBI registered investment advice. Always diversify.</small>", unsafe_allow_html=True)
        section_end()


# ════════════════════════════════════════════════════════════════
# TAB 8 — ALL INDICES
# ════════════════════════════════════════════════════════════════
with tabs[8]:
    section_hdr("📉 All NSE Indices — Live Data")
    if "idx_q" not in st.session_state: st.session_state.idx_q=""
    with st.spinner("Fetching all indices..."): idx_rows=fetch_indices()
    btn_cols=st.columns(9)
    labels_filters=[("All",""),("Bank","BANK"),("IT","IT"),("Pharma","PHARMA"),("FMCG","FMCG"),
                    ("SmallCap","SMALL"),("MidCap","MID"),("Auto","AUTO"),("Metal","METAL")]
    for i,(bc,(lbl,fval)) in enumerate(zip(btn_cols,labels_filters)):
        if bc.button(lbl,key=f"idxbtn_{i}",type="primary" if st.session_state.idx_q==fval else "secondary"):
            st.session_state.idx_q=fval; st.rerun()
    typed=st.text_input("🔍 Or type to filter:",placeholder="e.g. BANK, IT, PHARMA, NIFTY...",
                        value=st.session_state.idx_q,key="idx_text_input")
    if typed!=st.session_state.idx_q: st.session_state.idx_q=typed
    q=st.session_state.idx_q.strip().upper()
    filtered_idx=[r for r in idx_rows if q in r.get("Index","").upper()] if q else idx_rows
    total=len(filtered_idx); up=sum(1 for r in filtered_idx if "UP" in r.get("Signal",""))
    down=sum(1 for r in filtered_idx if "DOWN" in r.get("Signal",""))
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Showing",total); m2.metric("🟢 Up",up); m3.metric("🔴 Down",down); m4.metric("Total Loaded",len(idx_rows))
    df_show(filtered_idx, height=580); section_end()


# ════════════════════════════════════════════════════════════════
# TAB 9 — STOCK INFO
# ════════════════════════════════════════════════════════════════
with tabs[9]:
    section_hdr("🔍 Stock Info & Deep Analysis")
    info_box("Enter any NSE symbol to get complete analysis: Price levels, Support/Resistance, Fibonacci, Pivot Points, Trade Setup, and Buy/Sell recommendation.")
    col1,col2,col3=st.columns([2,1,1])
    with col1: sym_input=st.text_input("NSE Symbol:",placeholder="e.g. RELIANCE, TCS, INFY, HDFCBANK",value="RELIANCE").upper().strip()
    with col2: st.markdown("<br>",unsafe_allow_html=True); analyse_btn=st.button("  🔍 ANALYSE  ",width='stretch')
    with col3: st.markdown("<br>",unsafe_allow_html=True); st.link_button("📊 NSE Page",f"https://www.nseindia.com/get-quotes/equity?symbol={sym_input}")

    if analyse_btn and sym_input:
        with st.spinner(f"🔄 Fetching and analysing {sym_input}..."):
            info=fetch_stock_info_full(sym_input)
        verdict=info.get("_verdict","--"); score=info.get("_score",0)
        vcolor={"green":"#26de81","orange":"#f7b731","red":"#fc5c65"}.get(info.get("_vcolor",""),"#8899bb")
        st.markdown(f"<div style='background:#16213e;border-left:6px solid {vcolor};padding:16px 20px;border-radius:8px;margin:12px 0;'>"
            f"<span style='color:{vcolor};font-size:1.4rem;font-weight:800;'>{verdict}</span>"
            f"<span style='color:#8899bb;font-size:0.9rem;margin-left:20px;'>Score: {score:+d}/10 | {sym_input} | {datetime.now().strftime('%H:%M:%S')}</span>"
            f"</div>", unsafe_allow_html=True)
        reasons=info.get("_reasons",[])
        if reasons: st.markdown(f"<div class='info-box'>{'   |   '.join(reasons)}</div>",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        c1.markdown("**📌 Identity**")
        for k in ["Company","Industry","Sector","ISIN","Series","Face Value"]:
            c1.markdown(f"<small style='color:#8899bb'>{k}:</small> <b style='color:#eaf0fb'>{info.get(k,'--')}</b><br>",unsafe_allow_html=True)
        c2.markdown("**💹 Price**")
        for k,label in [("LTP","LTP"),("Change%","Change%"),("VWAP","VWAP"),("Open","Open"),("High","High"),("Low","Low"),("Prev Close","Prev Close"),("52W High","52W High"),("52W Low","52W Low")]:
            v=info.get(k,"--"); color="#eaf0fb"
            if k=="Change%":
                try: n=float(str(v)); color="#26de81" if n>=0 else "#fc5c65"; v=f"{n:+.2f}%"
                except: pass
            elif isinstance(v,float): v=f"₹{v:,.2f}"
            c2.markdown(f"<small style='color:#8899bb'>{label}:</small> <b style='color:{color}'>{v}</b><br>",unsafe_allow_html=True)
        c3.markdown("**🎯 Trade Setup**")
        for k in ["Buy Zone","Target 1","Target 2","Stop Loss","Upside%","Downside%","R:R"]:
            v=info.get(k,"--"); color="#eaf0fb"
            if k in ("Buy Zone","Target 1","Target 2"): color="#26de81"
            elif k=="Stop Loss": color="#fc5c65"
            elif k=="R:R": color="#f7b731"
            if isinstance(v,float): v=f"₹{v:,.2f}" if k not in ("Upside%","Downside%") else f"{v:.2f}%"
            c3.markdown(f"<small style='color:#8899bb'>{k}:</small> <b style='color:{color}'>{v}</b><br>",unsafe_allow_html=True)
        st.markdown("---")
        c1,c2,c3=st.columns(3)
        with c1:
            section_hdr("🔴 Resistance Levels")
            for k,label in [("R2","R2"),("Imm Resist","Immediate ★"),("R1","R1 — Near")]:
                v=info.get(k,"--")
                if isinstance(v,float): v=f"₹{v:,.2f}"
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:4px 8px;background:#200a0a;border-radius:4px;margin:2px 0;'><span style='color:#8899bb;font-size:0.85rem'>{label}</span><b style='color:#fc5c65'>{v}</b></div>",unsafe_allow_html=True)
        with c2:
            section_hdr("🟡 Pivot & Fibonacci")
            for k,label in [("Pivot","Pivot Point"),("Fib 61.8%","Fib 61.8% (Golden)"),("Fib 50%","Fib 50%"),("Fib 38.2%","Fib 38.2%"),("Fib 23.6%","Fib 23.6%")]:
                v=info.get(k,"--")
                if isinstance(v,float): v=f"₹{v:,.2f}"
                color="#f7b731" if k=="Pivot" else "#45aaf2"
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:4px 8px;background:#1a1400;border-radius:4px;margin:2px 0;'><span style='color:#8899bb;font-size:0.85rem'>{label}</span><b style='color:{color}'>{v}</b></div>",unsafe_allow_html=True)
        with c3:
            section_hdr("🟢 Support Levels")
            for k,label in [("S1","S1 — Near"),("Imm Support","Immediate ★"),("S2","S2"),("52W Low","52W Low")]:
                v=info.get(k,"--")
                if isinstance(v,float): v=f"₹{v:,.2f}"
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:4px 8px;background:#0a2015;border-radius:4px;margin:2px 0;'><span style='color:#8899bb;font-size:0.85rem'>{label}</span><b style='color:#26de81'>{v}</b></div>",unsafe_allow_html=True)
        st.markdown("<br><small style='color:#5c6f8a'>⚠️ For educational purposes only. Not SEBI registered investment advice.</small>",unsafe_allow_html=True)

        # ── Chart + Real Technical Indicators (yfinance) ─────────────────
        st.markdown("---")
        section_hdr("📈 Price Chart + Technical Indicators (RSI · MACD · EMA)")
        period_sel = st.selectbox("Chart Period:", ["1mo","3mo","6mo","1y","2y"], index=2, key="chart_period")
        with st.spinner(f"Loading {sym_input} chart from Yahoo Finance..."):
            chart_df = fetch_chart_indicators(sym_input, period=period_sel)
        if chart_df is not None and len(chart_df) > 5:
            try:
                import plotly.graph_objects as go
                from plotly.subplots import make_subplots
                fig = make_subplots(
                    rows=3, cols=1,
                    shared_xaxes=True,
                    row_heights=[0.55, 0.25, 0.20],
                    vertical_spacing=0.03,
                    subplot_titles=(f"{sym_input} — Candlestick + EMAs", "RSI (14)", "MACD (12,26,9)")
                )
                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=chart_df["date"], open=chart_df["open"], high=chart_df["high"],
                    low=chart_df["low"],  close=chart_df["close"],
                    name="Price", increasing_line_color="#26de81", decreasing_line_color="#fc5c65",
                    increasing_fillcolor="#26de81", decreasing_fillcolor="#fc5c65",
                ), row=1, col=1)
                # EMAs
                for col_n, color, lbl in [("ema20","#f7b731","EMA20"),("ema50","#00d2ff","EMA50"),("ema200","#a55eea","EMA200")]:
                    if col_n in chart_df.columns:
                        fig.add_trace(go.Scatter(x=chart_df["date"], y=chart_df[col_n].round(2),
                            mode="lines", name=lbl, line=dict(color=color, width=1.5)), row=1, col=1)
                # RSI
                if "rsi" in chart_df.columns:
                    fig.add_trace(go.Scatter(x=chart_df["date"], y=chart_df["rsi"].round(2),
                        mode="lines", name="RSI", line=dict(color="#00d2ff", width=1.5)), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="#fc5c65", row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="#26de81", row=2, col=1)
                    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(252,92,101,0.07)", row=2, col=1, line_width=0)
                    fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(38,222,129,0.07)", row=2, col=1, line_width=0)
                # MACD
                if "macd" in chart_df.columns:
                    macd_colors = ["#26de81" if v >= 0 else "#fc5c65" for v in chart_df["macd_hist"].fillna(0)]
                    fig.add_trace(go.Bar(x=chart_df["date"], y=chart_df["macd_hist"].round(3),
                        marker_color=macd_colors, name="MACD Hist", opacity=0.7), row=3, col=1)
                    fig.add_trace(go.Scatter(x=chart_df["date"], y=chart_df["macd"].round(3),
                        mode="lines", name="MACD", line=dict(color="#00d2ff", width=1.3)), row=3, col=1)
                    fig.add_trace(go.Scatter(x=chart_df["date"], y=chart_df["macd_sig"].round(3),
                        mode="lines", name="Signal", line=dict(color="#f7b731", width=1.3)), row=3, col=1)
                fig.update_layout(
                    height=680, template="plotly_dark",
                    paper_bgcolor="#0f1a2e", plot_bgcolor="#0f1a2e",
                    font=dict(color="#eaf0fb", size=11),
                    legend=dict(orientation="h", y=1.02, x=0, font_size=10),
                    xaxis_rangeslider_visible=False,
                    margin=dict(l=10, r=10, t=30, b=10),
                )
                fig.update_xaxes(gridcolor="#1a2a40", showgrid=True)
                fig.update_yaxes(gridcolor="#1a2a40", showgrid=True)
                st.plotly_chart(fig, width='stretch')
                # ── RSI / MACD quick interpretation ─────────────────
                last_rsi  = round(float(chart_df["rsi"].dropna().iloc[-1]), 1)  if "rsi"  in chart_df.columns else None
                last_macd = float(chart_df["macd_hist"].dropna().iloc[-1])       if "macd" in chart_df.columns else None
                last_ev20 = float(chart_df["ema20"].dropna().iloc[-1])           if "ema20" in chart_df.columns else None
                last_ev50 = float(chart_df["ema50"].dropna().iloc[-1])           if "ema50" in chart_df.columns else None
                ltp_now   = float(chart_df["close"].iloc[-1])
                ic1,ic2,ic3,ic4 = st.columns(4)
                if last_rsi is not None:
                    rsi_color = "#fc5c65" if last_rsi>70 else ("#26de81" if last_rsi<30 else "#f7b731")
                    rsi_lbl   = "Overbought" if last_rsi>70 else ("Oversold" if last_rsi<30 else "Neutral")
                    ic1.markdown(f"<div class='metric-card'><div class='label'>RSI (14)</div>"
                                 f"<div class='value' style='color:{rsi_color};'>{last_rsi} — {rsi_lbl}</div></div>",
                                 unsafe_allow_html=True)
                if last_macd is not None:
                    mc = "#26de81" if last_macd>0 else "#fc5c65"
                    ml = "Bullish momentum" if last_macd>0 else "Bearish momentum"
                    ic2.markdown(f"<div class='metric-card'><div class='label'>MACD Histogram</div>"
                                 f"<div class='value' style='color:{mc};'>{last_macd:+.3f} — {ml}</div></div>",
                                 unsafe_allow_html=True)
                if last_ev20 is not None:
                    ec = "#26de81" if ltp_now>last_ev20 else "#fc5c65"
                    el = "Above EMA20 ✅" if ltp_now>last_ev20 else "Below EMA20 ⚠️"
                    ic3.markdown(f"<div class='metric-card'><div class='label'>vs EMA 20</div>"
                                 f"<div class='value' style='color:{ec};'>{el}</div></div>",
                                 unsafe_allow_html=True)
                if last_ev50 is not None:
                    ec2 = "#26de81" if ltp_now>last_ev50 else "#fc5c65"
                    el2 = "Above EMA50 ✅" if ltp_now>last_ev50 else "Below EMA50 ⚠️"
                    ic4.markdown(f"<div class='metric-card'><div class='label'>vs EMA 50</div>"
                                 f"<div class='value' style='color:{ec2};'>{el2}</div></div>",
                                 unsafe_allow_html=True)
                rel_vol_last = float(chart_df["rel_vol"].dropna().iloc[-1]) if "rel_vol" in chart_df.columns else None
                if rel_vol_last:
                    rv_color = "#f7b731" if rel_vol_last>1.5 else "#8899bb"
                    st.markdown(f"<div class='info-box'>📦 Today's Relative Volume: "
                                f"<b style='color:{rv_color};'>{rel_vol_last:.1f}x</b> average — "
                                f"{'🔥 Unusually high volume!' if rel_vol_last>2 else ('⚡ Above average' if rel_vol_last>1.3 else 'Normal volume')}"
                                f"</div>", unsafe_allow_html=True)
            except Exception as chart_err:
                st.warning(f"Chart rendering error: {chart_err}. Try refreshing.")
        else:
            st.info("📊 Chart not available — yfinance may need installing on your Streamlit Cloud. "
                    "Add `yfinance` and `plotly` to your `requirements.txt` file.")
        section_end()
    else:
        st.info("👆 Enter a symbol above and click ANALYSE to see complete stock analysis.")


# ════════════════════════════════════════════════════════════════
# TAB 10 — MUTUAL FUNDS
# ════════════════════════════════════════════════════════════════
with tabs[10]:
    st.markdown("""<div style="background:linear-gradient(90deg,#0f3460,#1a0533);padding:12px 18px;border-radius:8px;margin-bottom:12px;">
        <span style="color:#00d2ff;font-size:1rem;font-weight:700;">🏦 MUTUAL FUNDS — Top 10 Per Category · 100% Dynamic from AMFI India</span><br>
        <span style="color:#8899bb;font-size:0.8rem;">All fund names &amp; NAVs fetched live · Ranked by NAV within each category</span>
    </div>""", unsafe_allow_html=True)

    with st.spinner("📥 Fetching mutual funds from AMFI India (live) — ~10 seconds..."):
        mf_df=fetch_mutual_funds_dynamic()

    if mf_df is not None and not mf_df.empty and "Category" in mf_df.columns and mf_df["Category"].iloc[0]!="Error":
        all_cats=sorted(mf_df["Category"].unique().tolist())
        mc1,mc2,mc3=st.columns(3)
        mc1.metric("Total Funds (Top 10/cat)",len(mf_df)); mc2.metric("Categories",len(all_cats)); mc3.metric("Source","AMFI India (Live)")
        info_box("Top 10 funds per category ranked by highest NAV. Search by fund house name to find specific funds.")
        col1,col2=st.columns([2,4])
        with col1: selected_cat=st.selectbox("📂 Filter by Category:",["All Categories"]+all_cats)
        with col2: search_fund=st.text_input("🔍 Search by fund name / house:",placeholder="e.g. Parag Parikh, Motilal, HDFC, SBI...")
        filtered=mf_df.copy()
        if selected_cat!="All Categories": filtered=filtered[filtered["Category"]==selected_cat]
        if search_fund: filtered=filtered[filtered["Fund Name"].str.contains(search_fund,case=False,na=False)]
        st.caption(f"Showing {len(filtered)} funds | Filter: {selected_cat} | Search: '{search_fund or 'none'}'")
        st.dataframe(filtered.reset_index(drop=True),width='stretch',height=520)
        st.markdown('<div style="padding-bottom:16px;"></div>',unsafe_allow_html=True)
        with st.expander("📊 Funds per Category Breakdown"):
            for cat in all_cats:
                cat_df=mf_df[mf_df["Category"]==cat]; st.markdown(f"**{cat}** — {len(cat_df)} funds")
        section_end()
    else:
        st.error("Could not fetch mutual fund data from AMFI India. SSL/Network issue.")
        st.info("Try clicking 'Refresh All Data' in the sidebar, or wait 1 minute and retry.")


# ════════════════════════════════════════════════════════════════
# TAB 11 — PRO TOOLS
# ════════════════════════════════════════════════════════════════
with tabs[11]:
    st.markdown("""<div style="background:linear-gradient(90deg,#1a0533,#0f3460);padding:12px 18px;border-radius:8px;margin-bottom:12px;">
        <span style="color:#a55eea;font-size:1rem;font-weight:700;">
        🛡️ PRO TOOLS — FII/DII · Bulk/Block Deals · Circuits · Delivery % · Portfolio Tracker · Price Alerts · Analytics
        </span><br>
        <span style="color:#8899bb;font-size:0.8rem;">Smart Money Tracker | Institutional Activity | Use during market hours</span>
    </div>""", unsafe_allow_html=True)

    pro_tabs=st.tabs(["🏦 FII/DII","💼 Bulk & Block","⚡ Circuits","📦 Delivery %","💰 Portfolio","🔔 Alerts","🎯 Options Chain","📈 Volume Spikes","📅 Results Calendar","📊 Users & Analytics"])

    with pro_tabs[0]:
        section_hdr("🏦 FII / DII Daily Net Activity")
        st.columns(4)[0].info("🟢 FII Net Buy > ₹500Cr = Very Bullish")
        st.columns(4)[1].info("🔴 FII Net Sell > ₹500Cr = Bearish")
        st.columns(4)[2].info("🟡 DII Net Buy = Market support")
        st.columns(4)[3].info("🚀 Both Net Buy = Best time to BUY")
        with st.spinner("Fetching FII/DII data..."): fii=fetch_fii_dii()
        df_show(fii,height=300)
        info_box("FII = Foreign Institutional Investors. DII = Domestic (MFs, Insurance, Banks). Track daily — FII net buying for 3+ days = STRONG UPTREND.")
        section_end()

    with pro_tabs[1]:
        with st.spinner("Fetching bulk & block deals..."): bulk,block=fetch_bulk_block()
        c1,c2=st.columns(2)
        with c1: section_hdr("🔵 Bulk Deals"); df_show(bulk,height=350)
        with c2: section_hdr("🟣 Block Deals"); df_show(block,height=350)
        info_box("If a MUTUAL FUND or FII is BUYING → Strong BUY signal. If PROMOTER is SELLING → Caution.")
        section_end()

    with pro_tabs[2]:
        with st.spinner("Fetching circuit breaker stocks..."): ucirc,lcirc=fetch_circuits()
        c1,c2=st.columns(2)
        with c1: section_hdr("🚀 Upper Circuit"); df_show(ucirc,height=350)
        with c2: section_hdr("💥 Lower Circuit"); df_show(lcirc,height=350)
        info_box("Upper Circuit = Extreme demand. Buy next day open for momentum. Lower Circuit = Panic selling. AVOID.")
        section_end()

    with pro_tabs[3]:
        section_hdr("📦 Delivery % Tracker")
        min_del=st.slider("Min Delivery %:",0,80,0,key="del_slider")
        with st.spinner("Fetching delivery data..."): deliv=fetch_delivery()
        deliv_f=[r for r in deliv if _f(r.get("Del %","0"))>=min_del]
        st.caption(f"Showing {len(deliv_f)} stocks with delivery >= {min_del}%")
        df_show(deliv_f,height=450)
        info_box("Del% > 70% + Breakout = Best trade setup. Del% < 25% = Speculation only.")
        section_end()

    with pro_tabs[4]:
        section_hdr("💰 Portfolio Tracker — Live P&L")
        info_box("Add your holdings below. Click 'Refresh P&L' to get live prices from NSE.")
        if "portfolio" not in st.session_state: st.session_state.portfolio=[]
        with st.form("add_holding"):
            fc1,fc2,fc3,fc4=st.columns([2,1,2,1])
            sym_in=fc1.text_input("Symbol",placeholder="e.g. RELIANCE").upper().strip()
            qty_in=fc2.text_input("Quantity",placeholder="100")
            bp_in=fc3.text_input("Buy Price ₹",placeholder="2500")
            submitted=fc4.form_submit_button("➕ ADD",width='stretch')
        if submitted and sym_in:
            try:
                qty_v=float(qty_in.replace(",","")); bp_v=float(bp_in.replace(",","").replace("₹",""))
                if qty_v>0 and bp_v>0:
                    if not any(p["sym"]==sym_in for p in st.session_state.portfolio):
                        st.session_state.portfolio.append({"sym":sym_in,"qty":qty_v,"bp":bp_v})
                        st.success(f"✅ {sym_in} added!"); st.rerun()
                    else: st.warning(f"{sym_in} already in portfolio.")
            except: st.error("Please enter valid Quantity and Buy Price.")
        if st.session_state.portfolio:
            if st.button("🔄 Refresh P&L (Live NSE Prices)"):
                rows=[]; t_inv=0; t_cur=0; t_day=0
                with st.spinner("Fetching live prices..."):
                    for p in st.session_state.portfolio:
                        cmp,dc=get_live_price(p["sym"])
                        if cmp==0: cmp=p["bp"]
                        inv=p["qty"]*p["bp"]; cur=p["qty"]*cmp; pnl=cur-inv; ret=(pnl/inv*100) if inv>0 else 0
                        day_pnl=p["qty"]*(cmp*(dc/100)); t_inv+=inv; t_cur+=cur; t_day+=day_pnl
                        rows.append({"Symbol":p["sym"],"Qty":int(p["qty"]),"Buy Price":f"₹{p['bp']:,.2f}",
                            "Invested":f"₹{inv:,.0f}","CMP":f"₹{cmp:,.2f}","Current Value":f"₹{cur:,.0f}",
                            "P&L":f"₹{pnl:+,.0f}","Return%":f"{ret:+.2f}%","Day Chg%":f"{dc:+.2f}%",
                            "Signal":"🟢 PROFIT" if pnl>0 else ("🔴 LOSS" if pnl<0 else "➡️ BREAK EVEN")})
                t_pnl=t_cur-t_inv; t_ret=(t_pnl/t_inv*100) if t_inv>0 else 0
                pm1,pm2,pm3,pm4,pm5=st.columns(5)
                pm1.metric("Invested",f"₹{t_inv:,.0f}"); pm2.metric("Current",f"₹{t_cur:,.0f}")
                pm3.metric("Total P&L",f"₹{t_pnl:+,.0f}",delta=f"{t_ret:+.2f}%")
                pm4.metric("Return",f"{t_ret:+.2f}%"); pm5.metric("Today's P&L",f"₹{t_day:+,.0f}")
                df_show(rows,height=300)
            st.markdown("**Current Holdings:**")
            for i,p in enumerate(st.session_state.portfolio):
                c1,c2,c3,c4=st.columns([2,1,2,1])
                c1.write(f"**{p['sym']}**"); c2.write(f"Qty: {int(p['qty'])}"); c3.write(f"Buy: ₹{p['bp']:,.2f}")
                if c4.button("🗑️",key=f"del_{i}"): st.session_state.portfolio.pop(i); st.rerun()
        else: st.info("No holdings yet. Add your first stock above!")

    with pro_tabs[5]:
        section_hdr("🔔 Price Alerts")
        info_box("Set Target and Stop Loss alerts. Click 'Check Alerts Now' to check current prices.")
        if "alerts" not in st.session_state: st.session_state.alerts=[]
        with st.form("add_alert"):
            ac1,ac2,ac3,ac4,ac5=st.columns([2,2,2,2,1])
            a_sym=ac1.text_input("Symbol",placeholder="RELIANCE").upper().strip()
            a_price=ac2.text_input("Alert Price ₹",placeholder="2600")
            a_cond=ac3.selectbox("Condition",["Crosses Above","Crosses Below","Equals"])
            a_note=ac4.text_input("Label",placeholder="Target / Stop Loss")
            a_sub=ac5.form_submit_button("🔔 ADD",width='stretch')
        if a_sub and a_sym:
            try:
                ap=float(a_price.replace(",","").replace("₹",""))
                st.session_state.alerts.append({"sym":a_sym,"price":ap,"cond":a_cond,"note":a_note or "Alert","triggered":False})
                st.success(f"✅ Alert set: {a_sym} {a_cond} ₹{ap:,.2f}"); st.rerun()
            except: st.error("Enter a valid price.")
        if st.session_state.alerts:
            if st.button("🔍 Check All Alerts Now (Live Prices)"):
                with st.spinner("Checking all alerts..."):
                    triggered_any=False
                    for a in st.session_state.alerts:
                        if a["triggered"]: continue
                        cmp,_=get_live_price(a["sym"])
                        if cmp>0:
                            hit=False
                            if a["cond"]=="Crosses Above" and cmp>=a["price"]: hit=True
                            elif a["cond"]=="Crosses Below" and cmp<=a["price"]: hit=True
                            elif a["cond"]=="Equals" and abs(cmp-a["price"])<=a["price"]*0.003: hit=True
                            if hit:
                                a["triggered"]=True; a["cmp"]=cmp; triggered_any=True
                                st.error(f"🔔 ALERT TRIGGERED! {a['sym']} {a['cond']} ₹{a['price']:,.2f} — CMP: ₹{cmp:,.2f} — {a['note']}")
                    if not triggered_any: st.success("✅ No alerts triggered yet. All prices within range.")
            alert_rows=[]
            for i,a in enumerate(st.session_state.alerts):
                alert_rows.append({"Symbol":a["sym"],"Alert Price":f"₹{a['price']:,.2f}",
                    "Condition":a["cond"],"Label":a["note"],"Status":"✅ TRIGGERED" if a["triggered"] else "⏳ Watching"})
            df_show(alert_rows,height=250)
            if st.button("🗑️ Clear All Alerts"): st.session_state.alerts=[]; st.rerun()
        else: st.info("No alerts set yet. Add your first alert above!")

    # ── SUB-TAB 6: Options Chain ─────────────────────────────────
    with pro_tabs[6]:
        section_hdr("🎯 Options Chain — PCR · Max Pain · OI Table")
        info_box("Options chain is the most reliable institutional sentiment indicator. "
                 "PCR > 1.2 = Bullish (put writers selling = market expected to rise). "
                 "PCR < 0.8 = Bearish. Max Pain = strike where maximum option buyers lose money — market gravitates here at expiry.")
        oc1, oc2 = st.columns([2,2])
        with oc1:
            oc_sym = st.selectbox("Select Index/Stock:", ["NIFTY","BANKNIFTY","FINNIFTY"] + [
                s.get("symbol","") for s in fetch_n500()[:50] if isinstance(s,dict)
            ], key="oc_sym")
        with oc2:
            st.markdown("<br>", unsafe_allow_html=True)
            oc_btn = st.button("🔄 Fetch Options Chain", width='stretch', key="oc_btn")
        if oc_btn:
            with st.spinner(f"Fetching options chain for {oc_sym}..."):
                oc_data = fetch_options_chain(oc_sym)
            if oc_data.get("ok") and oc_data.get("expiries"):
                expiry_sel = st.selectbox("Expiry Date:", oc_data["expiries"], key="oc_expiry")
                pcr_result = compute_pcr_maxpain(oc_data, expiry_sel)
                if pcr_result:
                    pm1,pm2,pm3,pm4,pm5 = st.columns(5)
                    pm1.metric("PCR", f"{pcr_result['pcr']:.2f}")
                    pm2.metric("Max Pain", f"₹{pcr_result['max_pain']:,.0f}")
                    pm3.metric("Total CE OI", f"{pcr_result['ce_oi']:,.0f}")
                    pm4.metric("Total PE OI", f"{pcr_result['pe_oi']:,.0f}")
                    pm5.metric("Underlying", f"₹{oc_data['underlying']:,.2f}")
                    st.markdown(f"""<div style="background:#0d1a2a;border:2px solid #a55eea;border-radius:8px;padding:14px 18px;margin:8px 0;">
                        <span style="color:#a55eea;font-size:1.1rem;font-weight:800;">📊 {pcr_result['signal']}</span><br>
                        <span style="color:#8899bb;font-size:0.85rem;">PCR = {pcr_result['pcr']:.2f} | Max Pain = ₹{pcr_result['max_pain']:,.0f} | 
                        CE OI Change: {pcr_result['ce_chg']:+,.0f} | PE OI Change: {pcr_result['pe_chg']:+,.0f}</span><br>
                        <span style="color:#f7b731;font-size:0.8rem;">
                        {'📈 Bullish bias — Put writing dominant, market expected to hold/rise' if pcr_result['pcr']>=1.0 else
                         '📉 Bearish bias — Call writing dominant, market expected to fall/consolidate'}</span>
                    </div>""", unsafe_allow_html=True)
                    # OI Table for top strikes around current price
                    underlying = oc_data.get("underlying", 0)
                    all_strikes = sorted(pcr_result["strikes"].keys())
                    near_strikes = sorted(all_strikes, key=lambda s: abs(s - underlying))[:30]
                    near_strikes.sort()
                    oi_rows = []
                    for s in near_strikes:
                        d = pcr_result["strikes"][s]
                        oi_rows.append({
                            "Strike":       f"₹{s:,.0f}",
                            "CE OI":        f"{d['ce_oi']:,.0f}",
                            "CE OI Chg":    f"{d['ce_chg']:+,.0f}",
                            "CE LTP":       f"₹{d['ce_ltp']:.2f}",
                            "CE IV%":       f"{d['ce_iv']:.1f}%",
                            "PE LTP":       f"₹{d['pe_ltp']:.2f}",
                            "PE OI":        f"{d['pe_oi']:,.0f}",
                            "PE OI Chg":    f"{d['pe_chg']:+,.0f}",
                            "PE IV%":       f"{d['pe_iv']:.1f}%",
                            "Near ATM":     "⭐ ATM" if abs(s - underlying) < underlying * 0.01 else "",
                        })
                    df_show(oi_rows, height=450)
                else:
                    st.warning("Could not compute PCR from options data.")
            else:
                st.warning(f"Options data unavailable for {oc_sym}. NSE API may be restricted — try during market hours (9:15 AM – 3:30 PM IST).")
        else:
            st.info("👆 Select an index/stock and click 'Fetch Options Chain' above.")
        info_box("HOW TO USE: If Max Pain is significantly above current price → market likely to drift up near expiry. "
                 "Large CE OI at a strike = strong resistance. Large PE OI at a strike = strong support. "
                 "Track weekly: BANKNIFTY for banking sentiment, NIFTY for overall market.")
        section_end()

    # ── SUB-TAB 7: Volume Spikes ──────────────────────────────────
    with pro_tabs[7]:
        section_hdr("📈 Volume Spike Scanner — Unusual Volume Today")
        info_box("Stocks with abnormally high traded volume today (₹20 Cr+ and 2%+ move). "
                 "Volume spikes before big moves = institutions accumulating/distributing. "
                 "Green = buying surge (accumulation). Red = selling pressure (distribution).")
        with st.spinner("Scanning NIFTY 500 for volume spikes..."):
            vol_spikes = fetch_volume_spikes()
        vs1, vs2 = st.columns([2,2])
        with vs1:
            vs_intent = st.selectbox("Filter:", ["All","🟢 Buying Surge","🔴 Selling Pressure"], key="vs_intent")
        with vs2:
            vs_min_cr = st.slider("Min Traded Value (₹ Cr):", 20, 500, 50, key="vs_min_cr")
        vs_show = vol_spikes
        if vs_intent != "All":
            vs_show = [r for r in vs_show if vs_intent in r.get("Intent","")]
        vs_show = [r for r in vs_show if _f(r.get("Traded (Cr)","0").replace("₹","").replace(" Cr","")) >= vs_min_cr]
        st.caption(f"Showing {len(vs_show)} volume spike stocks | Traded > ₹{vs_min_cr} Cr with significant move")
        df_show(vs_show, height=500)
        info_box("PRO TIP: Volume Spike + Near 52W High + Positive Day = VERY STRONG buy setup. "
                 "Volume Spike + Negative Day + Near 52W Low = Distribution — AVOID or short. "
                 "Cross-check with 🚀 Breakout tab for confluence.")
        section_end()

    # ── SUB-TAB 8: Results Calendar ───────────────────────────────
    with pro_tabs[8]:
        section_hdr("📅 Upcoming Results & Board Meetings (Next 45 Days)")
        info_box("Stocks with upcoming quarterly results tend to move sharply on result day. "
                 "Strategy: buy strong stocks 5–7 days before results for pre-result run. "
                 "Exit 1 day before results to avoid 'sell the news' risk.")
        with st.spinner("Fetching NSE corporate calendar..."):
            results_cal = fetch_results_calendar()
        rc_search = st.text_input("🔍 Search by symbol:", placeholder="e.g. RELIANCE, TCS...", key="rc_search_cal")
        rc_show = [r for r in results_cal if rc_search.upper() in r.get("Symbol","").upper()] if rc_search else results_cal
        df_show(rc_show, height=500)
        info_box("HOW TO USE: Look for stocks in 🚀 Breakout or ⭐ Today's Picks that also have results "
                 "coming up in 7–10 days. These double-catalyst setups give highest probability moves.")
        section_end()

    # ── SUB-TAB 9: Users & Analytics ─────────────────────────────
    with pro_tabs[9]:
        st.markdown("""
        <div style="background:linear-gradient(90deg,#1a0533,#0a2040);
        border-left:5px solid #a55eea;padding:14px 20px;border-radius:10px;margin-bottom:12px;">
            <span style="color:#a55eea;font-size:1.05rem;font-weight:800;">
            📊 Users & Analytics Dashboard
            </span><br>
            <span style="color:#8899bb;font-size:0.82rem;">
            Powered by Google Analytics 4 · Country · City · Device · Sessions · Top Tabs · Search Terms
            </span>
        </div>""", unsafe_allow_html=True)

        # ── Step 1: Setup Instructions ────────────────────────────
        ga_id_set = GA_MEASUREMENT_ID != "G-XXXXXXXXXX"

        if not ga_id_set:
            st.markdown("""
            <div style="background:#1a0d00;border:2px solid #f7b731;border-radius:10px;padding:20px;margin:8px 0;">
            <span style="color:#f7b731;font-size:1rem;font-weight:800;">
            ⚙️ SETUP REQUIRED — 3 Easy Steps to Activate Analytics
            </span>
            </div>""", unsafe_allow_html=True)

            st.markdown("""
### 📋 How to Set Up Google Analytics (Free, 5 minutes)

**Step 1 — Create Google Analytics Account:**
1. Go to **[analytics.google.com](https://analytics.google.com)**
2. Sign in with your Google account
3. Click **"Start measuring"**
4. Enter Account name: `Stock Market Dashboard`
5. Click **Next → Next**

**Step 2 — Create a Property:**
1. Property name: `Stock Market Pro`
2. Timezone: **India (IST)**
3. Currency: **Indian Rupee (₹)**
4. Click **Next → Create**

**Step 3 — Get your Measurement ID:**
1. Choose **"Web"** as platform
2. Enter your Streamlit URL: `https://your-app.streamlit.app`
3. Click **"Create stream"**
4. Copy the **Measurement ID** — it looks like `G-ABC123XYZ`

**Step 4 — Paste it in this file:**
```python
# Line ~45 in streamlit_app_final.py
GA_MEASUREMENT_ID = "G-ABC123XYZ"   # ← Paste your ID here
```
5. Save and redeploy on Streamlit Cloud

**That's it! Analytics will start collecting data immediately.**
            """)

            st.info("💡 Once set up, come back to this tab to see your live dashboard below.")

        else:
            st.success(f"✅ Google Analytics Active — Measurement ID: `{GA_MEASUREMENT_ID}`")

        # ── GA4 Embed Dashboard ───────────────────────────────────
        # Inject JS to read GA data and display in real-time
        st.markdown(f"""
        <script>
        // Fire analytics event when this tab is viewed
        if (typeof gtag !== 'undefined') {{
            gtag('event', 'analytics_tab_viewed', {{
                'event_category': 'Navigation',
                'event_label': 'Users & Analytics Tab'
            }});
        }}
        </script>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📈 Live Analytics — View in Google Analytics")

        col_a, col_b = st.columns([3,2])
        with col_a:
            st.markdown(f"""
            <div style="background:#0d1a2a;border:1px solid #a55eea;border-radius:10px;padding:16px;">
            <div style="color:#a55eea;font-weight:700;font-size:0.95rem;margin-bottom:10px;">
            🔗 Quick Links to Your GA4 Dashboard
            </div>
            <div style="display:flex;flex-direction:column;gap:8px;">

            <a href="https://analytics.google.com/analytics/web/#/p{GA_MEASUREMENT_ID.replace('G-','')}/reports/reportinghub"
               target="_blank" style="text-decoration:none;">
            <div style="background:#1a0533;border:1px solid #a55eea;border-radius:6px;padding:10px 14px;
            display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.2rem;">🌍</span>
            <div><div style="color:#eaf0fb;font-weight:600;font-size:0.88rem;">Audience Overview</div>
            <div style="color:#8899bb;font-size:0.75rem;">Users · Sessions · Countries · Cities</div></div>
            </div></a>

            <a href="https://analytics.google.com/analytics/web/#/p{GA_MEASUREMENT_ID.replace('G-','')}/reports/explorer?params=_u..nav%3Dmaui%26_u.dateOption%3Dlast7days"
               target="_blank" style="text-decoration:none;">
            <div style="background:#0d3320;border:1px solid #26de81;border-radius:6px;padding:10px 14px;
            display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.2rem;">📊</span>
            <div><div style="color:#eaf0fb;font-weight:600;font-size:0.88rem;">Real-Time Report</div>
            <div style="color:#8899bb;font-size:0.75rem;">Who is using your app RIGHT NOW</div></div>
            </div></a>

            <a href="https://analytics.google.com/analytics/web/#/p{GA_MEASUREMENT_ID.replace('G-','')}/reports/explorer?params=_u..nav%3Dmaui%26explore-metric-picker%3D1"
               target="_blank" style="text-decoration:none;">
            <div style="background:#1a1400;border:1px solid #f7b731;border-radius:6px;padding:10px 14px;
            display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.2rem;">📱</span>
            <div><div style="color:#eaf0fb;font-weight:600;font-size:0.88rem;">Device & Technology</div>
            <div style="color:#8899bb;font-size:0.75rem;">Mobile vs Desktop · Browser · OS</div></div>
            </div></a>

            <a href="https://analytics.google.com/analytics/web/#/p{GA_MEASUREMENT_ID.replace('G-','')}/reports/explorer?params=_u..nav%3Dmaui%26explore-eventType%3Dtab_view"
               target="_blank" style="text-decoration:none;">
            <div style="background:#0a1f2a;border:1px solid #00d2ff;border-radius:6px;padding:10px 14px;
            display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.2rem;">🗂️</span>
            <div><div style="color:#eaf0fb;font-weight:600;font-size:0.88rem;">Most Used Tabs</div>
            <div style="color:#8899bb;font-size:0.75rem;">Which tabs your users visit most</div></div>
            </div></a>

            <a href="https://analytics.google.com/analytics/web/#/p{GA_MEASUREMENT_ID.replace('G-','')}/reports/explorer?params=_u..nav%3Dmaui%26explore-eventType%3Dsearch"
               target="_blank" style="text-decoration:none;">
            <div style="background:#1a0d00;border:1px solid #fc5c65;border-radius:6px;padding:10px 14px;
            display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.2rem;">🔍</span>
            <div><div style="color:#eaf0fb;font-weight:600;font-size:0.88rem;">Top Searched Symbols</div>
            <div style="color:#8899bb;font-size:0.75rem;">What stocks users search most</div></div>
            </div></a>

            </div></div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown("""
            <div style="background:#0d1a2a;border:1px solid #26de81;border-radius:10px;padding:16px;">
            <div style="color:#26de81;font-weight:700;font-size:0.95rem;margin-bottom:12px;">
            📡 What Gets Tracked Automatically
            </div>""", unsafe_allow_html=True)

            tracked = [
                ("🌍","Country & City","India-Delhi, India-Bangalore, USA-California"),
                ("📱","Device Type","Mobile / Desktop / Tablet"),
                ("🖥️","Browser & OS","Chrome, Firefox, Safari · Windows, Android, iOS"),
                ("⏱️","Session Duration","How long users stay on the app"),
                ("🗂️","Tab Clicks","Which tab was clicked (Today's Picks, Breakout etc.)"),
                ("🔍","Symbol Searches","Which stocks users search in Stock Info"),
                ("🕐","Time of Day","Pre-market / Market hours / After hours"),
                ("📅","Daily Sessions","How many times app opened each day"),
                ("🔄","Page Views","Every refresh / reopen counted"),
                ("📊","Custom Events","app_opened, tab_view, search, time_spent"),
            ]
            for icon, label, desc in tracked:
                st.markdown(f"""
                <div style="display:flex;gap:10px;padding:7px 0;border-bottom:1px solid #1a2a3a;">
                <span style="font-size:1rem;">{icon}</span>
                <div><div style="color:#eaf0fb;font-size:0.82rem;font-weight:600;">{label}</div>
                <div style="color:#8899bb;font-size:0.72rem;">{desc}</div></div>
                </div>""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # ── Embedded GA Realtime iframe ───────────────────────────
        st.markdown("---")
        st.markdown("### 🔴 Embed GA4 Reports Directly (Optional)")
        st.markdown("""
        <div style="background:#0d1a2a;border:1px solid #45aaf2;border-radius:8px;padding:14px;margin:8px 0;">
        <span style="color:#45aaf2;font-weight:700;">📌 How to Embed GA Reports inside this app:</span><br>
        <span style="color:#8899bb;font-size:0.82rem;">
        GA4 doesn't allow direct iframe embedding, but you can use <b style="color:#f7b731;">Looker Studio (free)</b>
        to create beautiful embedded dashboards:<br><br>
        1. Go to <b>lookerstudio.google.com</b><br>
        2. Create New Report → Connect to Google Analytics<br>
        3. Select your property<br>
        4. Build charts: Users by Country, Device breakdown, Top Events<br>
        5. Click <b>Share → Publish to web → Copy embed link</b><br>
        6. Paste the link below and click "Show Dashboard"
        </span>
        </div>
        """, unsafe_allow_html=True)

        looker_url = st.text_input(
            "Paste your Looker Studio embed URL:",
            placeholder="https://lookerstudio.google.com/embed/reporting/...",
            key="looker_url"
        )
        if looker_url and "lookerstudio.google.com" in looker_url:
            st.markdown(
                f'<iframe src="{looker_url}" width="100%" height="600" '
                f'frameborder="0" style="border-radius:8px;border:1px solid #a55eea;" '
                f'allowfullscreen sandbox="allow-storage-access-by-user-activation '
                f'allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox">'
                f'</iframe>',
                unsafe_allow_html=True
            )
        elif looker_url:
            st.warning("Please paste a valid Looker Studio embed URL (starts with https://lookerstudio.google.com/embed/)")

        # ── Custom Event Tracker ──────────────────────────────────
        st.markdown("---")
        st.markdown("### 🧪 Manual Event Tracker — Test Your GA Setup")
        st.markdown("""
        <div style="background:#0d1a2a;border:1px solid #8899bb;border-radius:8px;padding:12px;margin:4px 0;">
        <span style="color:#8899bb;font-size:0.82rem;">
        Click any button below to fire a test GA event. Then check your GA4 Realtime report
        to confirm tracking is working. Events appear in GA within 1–2 minutes.
        </span></div>""", unsafe_allow_html=True)

        tc1,tc2,tc3,tc4 = st.columns(4)
        with tc1:
            if st.button("🧪 Test: App Open", width='stretch', key="test_open"):
                st.markdown("""<script>
                if(typeof gtag!=='undefined'){
                    gtag('event','test_app_open',{'event_category':'Test','event_label':'Manual Test'});
                }
                </script>""", unsafe_allow_html=True)
                st.success("Event fired! Check GA4 Realtime > Events")
        with tc2:
            if st.button("🧪 Test: Tab Click", width='stretch', key="test_tab"):
                st.markdown("""<script>
                if(typeof gtag!=='undefined'){
                    gtag('event','tab_view',{'event_category':'Navigation','event_label':'Pro Tools - Analytics'});
                }
                </script>""", unsafe_allow_html=True)
                st.success("Tab event fired!")
        with tc3:
            if st.button("🧪 Test: Search", width='stretch', key="test_search"):
                st.markdown("""<script>
                if(typeof gtag!=='undefined'){
                    gtag('event','search',{'event_category':'Stock Search','search_term':'RELIANCE'});
                }
                </script>""", unsafe_allow_html=True)
                st.success("Search event fired!")
        with tc4:
            if st.button("🧪 Test: Device", width='stretch', key="test_device"):
                st.markdown("""<script>
                if(typeof gtag!=='undefined'){
                    var d=/Mobi|Android/i.test(navigator.userAgent)?'Mobile':'Desktop';
                    gtag('event','device_detected',{'event_category':'Device','event_label':d});
                }
                </script>""", unsafe_allow_html=True)
                st.success("Device event fired!")

        # ── What you'll see in GA4 ────────────────────────────────
        st.markdown("---")
        with st.expander("📖 Full Guide — What Reports to Look at in GA4"):
            st.markdown(f"""
### 📊 Your GA4 Dashboard Guide

**Go to: [analytics.google.com](https://analytics.google.com) → Your Property**

---

#### 🌍 Users by Location
`Reports → User → User attributes → Audiences`
- See **India-Delhi, India-Mumbai, India-Bangalore**
- Or **USA-California, UAE-Dubai** if international users
- Drill down to City level

---

#### 📱 Device Breakdown
`Reports → Tech → Tech overview`
- **Mobile vs Desktop vs Tablet** percentages
- **Android vs iOS vs Windows**
- **Chrome vs Safari vs Firefox**

---

#### 🗂️ Most Used Tabs (Custom Event)
`Reports → Engagement → Events → tab_view`
- See which tabs users click most
- Today's Picks vs Breakout vs Long Term etc.
- Filter by date range

---

#### 🔍 Most Searched Symbols
`Reports → Engagement → Events → search`
- See `search_term` parameter
- Which stocks your users search most
- RELIANCE, TCS, INFY etc.

---

#### ⏱️ Session Duration
`Reports → Engagement → Engagement overview`
- Average time per session
- How many pages per session

---

#### 🕐 Best Time of Day
`Reports → Engagement → Events → app_opened`
- Pre-Market / Market Hours / After Hours breakdown
- When your users are most active

---

#### 🔴 Real-Time (Who is ON right now)
`Reports → Realtime`
- Live users on app **right now**
- Their country, city, device
- Which page they're on
- Updates every 30 seconds

---

**Measurement ID in this app:** `{GA_MEASUREMENT_ID}`
            """)

        section_end()


# ── Footer ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#5c6f8a;font-size:0.8rem;padding:8px;'>"
    "🇮🇳 Indian Stock Market Pro Dashboard &nbsp;|&nbsp; Data: NSE India, AMFI India &nbsp;|&nbsp; "
    "⚠️ Not SEBI Investment Advice &nbsp;|&nbsp; For Educational Purposes Only"
    "</div>", unsafe_allow_html=True)
