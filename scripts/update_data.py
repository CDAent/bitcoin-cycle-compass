#!/usr/bin/env python3
import csv, io, json, math, re, statistics, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'live.json'
UA={'User-Agent':'BitcoinCycleCompass/6.0 (+GitHub Pages)','Accept':'application/json,text/html,*/*'}

def get(url, timeout=25):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=timeout) as r: return r.read().decode('utf-8','replace')
def jget(url): return json.loads(get(url))
def clamp(x,a=0,b=100): return max(a,min(b,x))
def pct(a,b): return ((a/b)-1)*100 if b else 0

def safe(fn, default=None):
    try:return fn()
    except Exception as e:return default

def price_sources():
    vals=[]; detail=[]
    def add(name,v):
        v=float(v)
        if 1000<v<1000000: vals.append(v);detail.append({'name':name,'usd':v})
    c=safe(lambda:jget('https://api.exchange.coinbase.com/products/BTC-USD/ticker'))
    if c:add('Coinbase',c['price'])
    k=safe(lambda:jget('https://api.kraken.com/0/public/Ticker?pair=XBTUSD'))
    if k:
        row=next(iter(k['result'].values()));add('Kraken',row['c'][0])
    b=safe(lambda:jget('https://www.bitstamp.net/api/v2/ticker/btcusd/'))
    if b:add('Bitstamp',b['last'])
    g=safe(lambda:jget('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true'))
    if g:add('CoinGecko index',g['bitcoin']['usd'])
    if not vals: raise RuntimeError('No BTC source')
    med=statistics.median(vals)
    kept=[v for v in vals if abs(v/med-1)<0.025]
    avg=sum(kept)/len(kept)
    return avg,detail,(g or {}).get('bitcoin',{}).get('usd_24h_change')

def fx():
    d=jget('https://api.frankfurter.app/latest?from=USD&to=AUD')
    return float(d['rates']['AUD'])

def fear():
    d=jget('https://api.alternative.me/fng/?limit=2&format=json')['data']
    now=float(d[0]['value']); prev=float(d[1]['value']) if len(d)>1 else now
    return {'value':now,'label':d[0]['value_classification'],'change24h':now-prev}

def stablecoins():
    d=jget('https://stablecoins.llama.fi/stablecoincharts/all')
    pts=[]
    for x in d:
        total=x.get('totalCirculatingUSD',{}).get('peggedUSD')
        if total: pts.append((int(x['date']),float(total)))
    pts.sort(); now=pts[-1][1]
    def nearest(days):
        target=pts[-1][0]-days*86400
        return min(pts,key=lambda p:abs(p[0]-target))[1]
    return {'marketCapUsd':now,'change1d':pct(now,nearest(1)),'change7d':pct(now,nearest(7)),'change30d':pct(now,nearest(30))}

def fred(series):
    txt=get('https://fred.stlouisfed.org/graph/fredgraph.csv?id='+series)
    rows=list(csv.reader(io.StringIO(txt)))[1:]
    vals=[]
    for r in rows:
        try: vals.append((r[0],float(r[1])))
        except: pass
    return vals

def macro():
    out={}
    for s in ['WALCL','M2SL','DGS10','DTWEXBGS','VIXCLS']:
        vals=safe(lambda s=s:fred(s),[]) or []
        if vals:
            out[s]={'value':vals[-1][1],'date':vals[-1][0],'change20':pct(vals[-1][1],vals[-min(21,len(vals))][1])}
    score=50
    score+=clamp((out.get('WALCL',{}).get('change20',0))*3,-10,10)
    score+=clamp((out.get('M2SL',{}).get('change20',0))*4,-10,10)
    score-=clamp((out.get('DTWEXBGS',{}).get('change20',0))*3,-8,8)
    score-=clamp((out.get('DGS10',{}).get('change20',0))*1.5,-8,8)
    score-=clamp((out.get('VIXCLS',{}).get('value',20)-20)*0.8,-10,15)
    out['score']=round(clamp(score))
    return out

def chain():
    charts={}
    for name in ['hash-rate','n-transactions','mempool-size']:
        u=f'https://api.blockchain.info/charts/{name}?timespan=30days&format=json&sampled=true'
        d=safe(lambda u=u:jget(u),{}) or {}
        vals=[float(x['y']) for x in d.get('values',[]) if x.get('y') is not None]
        if vals: charts[name]={'latest':vals[-1],'change30d':pct(vals[-1],vals[0])}
    score=50+clamp(charts.get('hash-rate',{}).get('change30d',0)*0.5,-12,12)+clamp(charts.get('n-transactions',{}).get('change30d',0)*0.4,-12,12)-clamp(charts.get('mempool-size',{}).get('change30d',0)*0.1,-6,6)
    return {'score':round(clamp(score)),'metrics':charts}

def stooq(symbol):
    txt=get(f'https://stooq.com/q/d/l/?s={symbol}&i=d')
    rows=list(csv.DictReader(io.StringIO(txt)))
    closes=[float(r['Close']) for r in rows if r.get('Close') not in ('','N/D')]
    return {'last':closes[-1],'change20d':pct(closes[-1],closes[-min(21,len(closes))])}

def etf_flow():
    # Best-effort live public table extraction. If layout changes, status is unavailable rather than manual.
    html=get('https://farside.co.uk/btc/')
    text=re.sub('<[^>]+>',' ',html); text=re.sub(r'\s+',' ',text)
    nums=[]
    for m in re.finditer(r'(\d{1,2}\s+[A-Z][a-z]{2}\s+20\d{2}).{0,500}?Total.{0,80}?([\-\(]?[\d,]+(?:\.\d+)?\)?)',text,re.I):
        raw=m.group(2).replace(',','').replace('(','-').replace(')','')
        try: nums.append({'date':m.group(1),'usdMillions':float(raw)})
        except: pass
    if not nums:return {'status':'unavailable','dailyUsdMillions':None,'score':50}
    v=nums[-1]['usdMillions']; return {'status':'live','dailyUsdMillions':v,'date':nums[-1]['date'],'score':round(clamp(50+v/15))}

def news():
    q='(bitcoin OR Federal Reserve OR inflation OR interest rates OR oil OR tariffs OR recession) markets'
    url='https://api.gdeltproject.org/api/v2/doc/doc?'+urllib.parse.urlencode({'query':q,'mode':'artlist','maxrecords':12,'format':'json','sort':'datedesc','timespan':'3d'})
    d=jget(url); items=[]
    for a in d.get('articles',[]):
        title=a.get('title','').strip(); link=a.get('url','');
        if title and link: items.append({'title':title,'url':link,'source':a.get('domain',''),'date':a.get('seendate','')})
    return items[:8]

def main():
    btc,exchanges,btc24=price_sources(); aud=fx(); fg=fear(); st=stablecoins(); ma=macro(); ch=chain(); etf=safe(etf_flow,{'status':'unavailable','dailyUsdMillions':None,'score':50})
    proxies={}
    for name,sym in [('gold','gld.us'),('equities','qqq.us'),('silver','slv.us'),('emerging','eem.us')]: proxies[name]=safe(lambda sym=sym:stooq(sym),{'change20d':0})
    sentiment=round(clamp(fg['value']))
    btc_score=round(clamp(0.22*etf['score']+0.20*ma['score']+0.18*ch['score']+0.20*sentiment+0.20*clamp(50+st['change7d']*8)))
    scores={
      'Bitcoin & digital assets':btc_score,
      'Gold & precious metals':round(clamp(55+proxies['gold']['change20d']*3+(100-ma['score'])*0.12)),
      'US AI & technology equities':round(clamp(55+proxies['equities']['change20d']*3+ma['score']*0.15)),
      'Silver':round(clamp(52+proxies['silver']['change20d']*3+proxies['gold']['change20d'])),
      'Emerging markets':round(clamp(50+proxies['emerging']['change20d']*3+(ma['score']-50)*0.2)),
    }
    out={'generatedAt':datetime.now(timezone.utc).isoformat(),'btc':{'usd':btc,'aud':btc*aud,'change24h':btc24,'method':'trimmed average / median check','sources':exchanges},'fx':{'usdAud':aud,'audUsd':1/aud},'fearGreed':fg,'stablecoins':st,'etf':etf,'macro':ma,'onchain':ch,'liquidityScores':scores,'proxies':proxies,'news':safe(news,[]) or []}
    OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out,indent=2),encoding='utf-8')
if __name__=='__main__': main()
