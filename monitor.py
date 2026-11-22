#!/usr/bin/env python3
"""Vérifie les liens du répertoire et actualise les redirections sûres."""
from __future__ import annotations
import json, re, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import requests

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
STATUS = ROOT / "status.json"
TIMEOUT = 18
PAUSE = 0.15

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.urls=[]
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            href = dict(attrs).get("href", "")
            if href.startswith(("http://", "https://")):
                self.urls.append(href)

def host(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")

def check(session: requests.Session, url: str) -> dict:
    headers={"User-Agent":"RepertoireIA-LinkMonitor/1.0 (+weekly link health check)"}
    try:
        r=session.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True, stream=True)
        code=r.status_code; final=r.url
        r.close()
        if code >= 400:
            return {"url":url,"status":"broken","http_code":code,"final_url":final,"message":f"HTTP {code}","auto_updated":False}
        same_host = host(url) == host(final)
        redirected = final.rstrip('/') != url.rstrip('/')
        safe_update = bool(redirected and same_host and code < 400)
        return {"url":url,"status":"redirect" if redirected else "ok","http_code":code,"final_url":final,"message":"Redirection détectée" if redirected else "Lien accessible","auto_updated":False,"safe_update":safe_update}
    except requests.RequestException as e:
        return {"url":url,"status":"unknown","http_code":None,"final_url":None,"message":str(e)[:220],"auto_updated":False,"safe_update":False}

def main():
    html=HTML.read_text(encoding='utf-8')
    parser=LinkParser(); parser.feed(html)
    urls=list(dict.fromkeys(parser.urls))
    results=[]; replacements={}
    with requests.Session() as s:
        for i,url in enumerate(urls,1):
            item=check(s,url)
            if item.get('safe_update'):
                replacements[url]=item['final_url']; item['auto_updated']=True
            results.append(item)
            print(f"[{i}/{len(urls)}] {item['status']} {url}")
            time.sleep(PAUSE)
    # Remplacer uniquement les redirections HTTPS/HTTP qui restent sur le même domaine.
    if replacements:
        for old,new in replacements.items():
            html=html.replace('href="'+old+'"','href="'+new+'"').replace("href='"+old+"'", "href='"+new+"'")
        HTML.write_text(html,encoding='utf-8')
    counts={k:sum(1 for x in results if x['status']==k) for k in ('ok','redirect','broken','unknown')}
    payload={"checked_at":datetime.now(timezone.utc).isoformat(),"frequency":"weekly","total":len(results),"counts":counts,"auto_updates":len(replacements),"results":results}
    STATUS.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({"total":len(results),"counts":counts,"auto_updates":len(replacements)},ensure_ascii=False))

if __name__=='__main__': main()
