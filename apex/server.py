"""Local dashboard + JSON API. Binds to localhost, requires a secret token, checks Host header (DNS-rebinding), size-limits bodies."""
from __future__ import annotations
import json, logging, os, secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .app import App

log = logging.getLogger("apex.server")

PAGE = r"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>APEX TRADER</title><style>
:root{--bg:#0e1116;--fg:#e6edf3;--mut:#8b949e;--card:#161b22;--bd:#30363d;--g:#3fb950;--r:#f85149;--y:#d29922;--b:#58a6ff}
@media(prefers-color-scheme:light){:root{--bg:#f6f8fa;--fg:#1f2328;--mut:#656d76;--card:#fff;--bd:#d0d7de}}
body{margin:0;background:var(--bg);color:var(--fg);font:14px system-ui,sans-serif;padding:16px;max-width:1100px;margin:auto}
.card{background:var(--card);border:1px solid var(--bd);border-radius:8px;padding:12px;margin:10px 0}
button{border:1px solid var(--bd);background:var(--card);color:var(--fg);padding:8px 14px;border-radius:6px;cursor:pointer;font-size:14px}
button.go{background:var(--g);color:#fff;border-color:var(--g);font-weight:600}button.no{background:var(--r);color:#fff;border-color:var(--r)}
button:disabled{opacity:.4;cursor:not-allowed}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid var(--bd);padding:4px 6px;text-align:left}
.L{color:var(--g)}.S{color:var(--r)}.m{color:var(--mut)}.big{font-size:28px;font-weight:700}.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
pre{white-space:pre-wrap;font-size:12px;max-height:340px;overflow:auto}
</style></head><body>
<div class=row><h2 style=margin:0>APEX TRADER</h2><span id=st class=m></span></div>
<div class=row><button id=scan onclick=doScan()>Scan chart</button><button id=adv onclick=adv() style=display:none>Advance 4 bars (replay)</button>
<button class=no onclick=kill()>KILL SWITCH</button><span id=msg class=m></span></div>
<div class=card id=sum></div><div class=card id=prop style=display:none></div>
<div class=card><b>Methods</b><table id=tb></table></div>
<div class=card><b>Full report</b><pre id=rep></pre></div>
<script>
const T="__TOKEN__";let PID=null;
async function api(p,b){const r=await fetch(p,{method:b===undefined?'GET':'POST',headers:{'X-APEX-Token':T,'Content-Type':'application/json'},body:b===undefined?undefined:JSON.stringify(b)});return r.json()}
const $=id=>document.getElementById(id);function el(t,c,x){const e=document.createElement(t);if(c)e.className=c;if(x!==undefined)e.textContent=x;return e}
async function status(){const s=await api('/api/status');$('st').textContent=`${s.symbol} | ${s.mode} | broker ${s.broker}${s.real_account?' (REAL ACCOUNT)':''} | equity ${s.equity.toFixed(2)} | daily loss ${s.daily_loss_pct}% | open ${s.positions.length}${s.kill?' | KILL SWITCH ACTIVE':''}${s.calendar?'':' | no news calendar'}`;$('adv').style.display=s.feed==='csv'?'':'none'}
async function doScan(){$('msg').textContent='scanning...';const d=await api('/api/scan',{});$('msg').textContent='';render(d);status()}
function render(d){const s=$('sum');s.textContent='';if(d.error){s.append(el('div','S',d.error));return}
 const sc=d.scan;s.append(el('div','big',`${sc.long+sc.short} of ${sc.n_total} methods passed`));
 s.append(el('div','',`LONG ${sc.long} | SHORT ${sc.short} | neutral ${sc.neutral} | n/a ${sc.na} | errors ${sc.errors} | independent families LONG ${sc.fam_long} / SHORT ${sc.fam_short}`));
 s.append(el('div',d.decision==='BUY'?'L':d.decision==='SELL'?'S':'',`Decision: ${d.decision} (${d.classification}, score ${d.score}/100 - not a probability)`));
 s.append(el('div','m',`Consensus: ${sc.consensus||'none'}${sc.consensus?'':' - '+sc.why_not.join('; ')}`));
 if(d.why.length)s.append(el('div','m','Notes: '+d.why.join(' | ')));if(d.issues.length)s.append(el('div','S','Reconcile: '+d.issues.join('; ')));
 const tb=$('tb');tb.textContent='';const h=el('tr');['Method','Family','Result','Str','Detail'].forEach(x=>h.append(el('th','',x)));tb.append(h);
 sc.methods.forEach(m=>{const r=el('tr');r.append(el('td','',m.name),el('td','m',m.family),el('td',!m.applicable?'m':m.passed?(m.dir>0?'L':'S'):'m',!m.applicable?'n/a':m.passed?(m.dir>0?'LONG':'SHORT'):'neutral'),el('td','',m.strength.toFixed(2)),el('td','m',m.detail));tb.append(r)});
 $('rep').textContent=d.report;const p=$('prop');p.textContent='';PID=null;
 if(d.proposal){const x=d.proposal;PID=x.id;p.style.display='';p.append(el('div','big '+(x.side==='BUY'?'L':'S'),`${x.side} ${document.title.split(' ')[0]?d.symbol:''} proposal`));
  p.append(el('div','',`Entry ~${x.entry} | Stop ${x.sl} | TP1 ${x.tp1} | TP2 ${x.tp2} | TP3 ${x.tp3}`));
  p.append(el('div','',`Size ${x.size} | risk ${x.risk} (${x.risk_pct}% of equity) | net R:R ${x.rr_net} | margin ${x.margin}`));
  p.append(el('div','m',`Expires ${x.expires}. Allow re-checks price, spread, risk limits and R:R on a fresh quote before sending.`));
  const row=el('div','row');const a=el('button','go','ALLOW trade');a.onclick=allow;const r=el('button','no','Reject');r.onclick=rej;row.append(a,r);p.append(row)}
 else p.style.display='none'}
async function allow(){if(!PID)return;const d=await api('/api/allow',{id:PID});$('msg').textContent=d.ok?`FILLED ${d.size} @ ${d.fill} SL ${d.sl} TP ${d.tp}`:`NOT sent: ${d.error||d.detail}`;$('prop').style.display='none';PID=null;status()}
async function rej(){await api('/api/reject',{id:PID});$('prop').style.display='none';PID=null}
async function kill(){if(!confirm('Activate kill switch and close all positions?'))return;await api('/api/kill',{});status()}
async function adv(){await api('/api/advance',{n:4});status();doScan()}
status();setInterval(status,15000);
</script></body></html>"""


def make_handler(app: App, token: str):
    class H(BaseHTTPRequestHandler):
        def log_message(self, fmt, *a): log.info("%s %s", self.address_string(), fmt % a)

        def _host_ok(self):
            h = (self.headers.get("Host") or "").split(":")[0]
            return h in ("127.0.0.1", "localhost", "[::1]")

        def _send(self, code, body, ctype="application/json"):
            b = body.encode() if isinstance(body, str) else body
            self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b)))
            self.send_header("Cache-Control", "no-store"); self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'")
            self.end_headers(); self.wfile.write(b)

        def _auth(self):
            return self._host_ok() and secrets.compare_digest(self.headers.get("X-APEX-Token", ""), token)

        def do_GET(self):
            if not self._host_ok(): return self._send(403, '{"error":"bad host"}')
            if self.path == "/": return self._send(200, PAGE.replace("__TOKEN__", token), "text/html; charset=utf-8")
            if not self._auth(): return self._send(401, '{"error":"unauthorized"}')
            if self.path == "/api/status": return self._send(200, json.dumps(app.status(), default=str))
            self._send(404, '{"error":"not found"}')

        def do_POST(self):
            if not self._auth(): return self._send(401, '{"error":"unauthorized"}')
            n = int(self.headers.get("Content-Length") or 0)
            if n > 10_000: return self._send(413, '{"error":"too large"}')
            try: body = json.loads(self.rfile.read(n) or b"{}")
            except ValueError: return self._send(400, '{"error":"bad json"}')
            try:
                if self.path == "/api/scan": out = app.scan()
                elif self.path == "/api/allow": out = app.allow(str(body.get("id", "")), self.address_string())
                elif self.path == "/api/reject": out = app.reject(str(body.get("id", "")))
                elif self.path == "/api/kill": out = app.kill()
                elif self.path == "/api/advance": out = app.advance(max(1, min(int(body.get("n", 1)), 50)))
                else: return self._send(404, '{"error":"not found"}')
            except Exception as e:
                log.exception("handler error"); return self._send(500, json.dumps({"error": str(e)}))
            self._send(200, json.dumps(out, default=str))
    return H


def serve(app: App, host="127.0.0.1", port=8765, token=None):
    if host not in ("127.0.0.1", "localhost"): raise RuntimeError("refusing to bind to a non-local address")
    token = token or os.environ.get("APEX_TOKEN") or secrets.token_urlsafe(24)
    srv = ThreadingHTTPServer((host, port), make_handler(app, token))
    print(f"APEX dashboard: http://{host}:{port}/   (local only; token is embedded in the page)")
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
    finally: srv.server_close()
    return srv
