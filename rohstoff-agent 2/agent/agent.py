#!/usr/bin/env python3
"""Rohstoff-Agent: holt Kurse (Yahoo Finance), berechnet Signale, schreibt app/report.json.
Taeglich ausfuehren:  python3 agent/agent.py   (cron / GitHub Actions, siehe README)"""
import json, urllib.request, datetime as dt, random, math, os
UNI = {"GC=F":"Gold","SI=F":"Silber","PL=F":"Platin","HG=F":"Kupfer","ALI=F":"Aluminium",
 "CL=F":"WTI Öl","BZ=F":"Brent Öl","NG=F":"Erdgas","ZW=F":"Weizen","ZC=F":"Mais",
 "ZS=F":"Sojabohnen","KC=F":"Kaffee","SB=F":"Zucker","CC=F":"Kakao"}
def fetch(t):
    u=f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=1y&interval=1d"
    r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=6)
    c=json.load(r)["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    return [x for x in c if x is not None]
def demo(t):
    random.seed(t); p=100; o=[]
    for _ in range(250): p*=1+random.gauss(0.0003,0.015); o.append(p)
    return o
sma=lambda c,n:sum(c[-n:])/n
def rsi(c,n=14):
    d=[c[i]-c[i-1] for i in range(-n,0)]; g=sum(x for x in d if x>0)/n; l=-sum(x for x in d if x<0)/n
    return 100 if l==0 else 100-100/(1+g/l)
def analyse(t,c):
    p=c[-1]; ch=(p/c[-2]-1)*100; m20=(p/c[-21]-1)*100
    s20,s50,s200=sma(c,20),sma(c,50),sma(c,min(200,len(c))); r=rsi(c)
    vol=(sum(((c[i]/c[i-1]-1)**2) for i in range(-20,0))/20)**.5
    short=(1 if p>s20 else -1)+(1 if m20>0 else -1)+(-1 if r>70 else 1 if r<30 else 0)
    long_=(1 if p>s200 else -1)+(1 if s50>s200 else -1)
    sc=short+long_
    sig="BUY" if sc>0 else "SELL" if sc<0 else "HOLD"
    d=1 if sig=="BUY" else -1
    return dict(ticker=t,name=UNI[t],price=round(p,2),chg1d=round(ch,2),mom20d=round(m20,2),rsi=round(r,1),
      short_trend="aufwärts" if short>0 else "abwärts" if short<0 else "seitwärts",
      long_trend="aufwärts" if long_>0 else "abwärts",signal=sig,score=sc,
      confidence=min(90,50+abs(sc)*8),
      entry=round(p,2),stop=round(p*(1-d*2.5*vol),2),target=round(p*(1+d*5*vol),2),
      rationale=f"Kurs {'über' if p>s20 else 'unter'} SMA20, {'über' if p>s200 else 'unter'} SMA200, RSI {r:.0f}, 20T-Momentum {m20:+.1f}%")
def main():
    res=[];isdemo=False;live=True
    for t in UNI:
        try:
            if not live: raise RuntimeError
            c=fetch(t)
        except Exception: c=demo(t); isdemo=True; live=False
        if len(c)>60: res.append(analyse(t,c))
    res.sort(key=lambda x:-abs(x["score"]))
    sigs=[x for x in res if x["signal"]!="HOLD"]
    sigs+= [x for x in res if x["signal"]=="HOLD"][:max(0,5-len(sigs))]
    mv=sorted(res,key=lambda x:-abs(x["chg1d"]))
    rep=dict(date=dt.date.today().isoformat(),demo=isdemo,
      summary=f"Größte Bewegung: {mv[0]['name']} {mv[0]['chg1d']:+.1f}%, {mv[1]['name']} {mv[1]['chg1d']:+.1f}%. "
              f"{sum(x['signal']=='BUY' for x in res)} Buy- / {sum(x['signal']=='SELL' for x in res)} Sell-Signale.",
      signals=sigs,markets=res,
      disclaimer="Keine Anlageberatung. Technische Signale, keine Gewinngarantie.")
    json.dump(rep,open(os.path.join(os.path.dirname(__file__),"..","app","report.json"),"w"),ensure_ascii=False,indent=1)
    print("OK",len(sigs),"Signale","(DEMO-Daten)" if isdemo else "")
main()
