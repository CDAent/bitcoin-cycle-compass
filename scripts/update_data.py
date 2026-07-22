#!/usr/bin/env python3
import csv, io, json, math, re, statistics, sys, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from html.parser import HTMLParser
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'live.json'
UA={'User-Agent':'BitcoinCycleCompass/6.0 (+GitHub Pages)','Accept':'application/json,text/html,*/*'}

# ---------------------------------------------------------------------------
# v8.4 SQLite historical data layer — imported after ROOT is defined so that
# relative paths in db_schema.py resolve correctly even if the script is run
# from a different working directory.
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))
try:
    from db_schema import init_db
    from history_service import get_daily_history, get_weekly_history
    import import_history as _import_history_mod
    _DB_AVAILABLE = True
except ImportError as _db_import_err:
    _DB_AVAILABLE = False
    print(f'Warning: DB modules not available: {_db_import_err}', file=sys.stderr)

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

def _num_cell(raw):
    raw=(raw or '').strip().replace(',','').replace('$','').replace('−','-')
    if raw in ('','-','—','N/A'): return None
    neg=raw.startswith('(') and raw.endswith(')')
    raw=raw.strip('()')
    try:
        v=float(raw)
        return -v if neg else v
    except: return None

class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows=[]; self.row=None; self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='tr': self.row=[]
        elif tag in ('td','th') and self.row is not None: self.cell=[]
    def handle_data(self,data):
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split())); self.cell=None
        elif tag=='tr' and self.row is not None:
            if self.row:self.rows.append(self.row)
            self.row=None

def _parse_farside(url):
    parser=_TableParser(); parser.feed(get(url))
    rows=[]
    for r in parser.rows:
        if not r: continue
        date=r[0].strip()
        if not re.search(r'\b20\d{2}\b',date): continue
        val=_num_cell(r[-1])
        if val is None: continue
        try: dt=datetime.strptime(date,'%d %b %Y')
        except:
            try: dt=datetime.strptime(date,'%d %B %Y')
            except: continue
        rows.append({'date':dt.strftime('%Y-%m-%d'),'usdMillions':val})
    rows.sort(key=lambda x:x['date'])
    return rows

def _yahoo_etf(ticker):
    url=f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1mo&interval=1d&events=history'
    d=jget(url)['chart']['result'][0]
    q=d['indicators']['quote'][0]; closes=q.get('close',[]); vols=q.get('volume',[])
    pts=[(float(c),float(v or 0)) for c,v in zip(closes,vols) if c is not None]
    if len(pts)<2: raise RuntimeError('insufficient ETF history')
    last,prev=pts[-1],pts[-2]
    ret=pct(last[0],prev[0]); avgvol=sum(v for _,v in pts[-20:])/max(1,len(pts[-20:]))
    vr=last[1]/avgvol if avgvol else 1
    return {'ticker':ticker,'close':last[0],'return1d':ret,'volume':last[1],'volumeVs20d':vr,'dollarVolumeUsd':last[0]*last[1]}

def etf_demand_proxy():
    funds=[]
    for t in ['IBIT','FBTC','ARKB','BITB','GBTC','BTC']:
        x=safe(lambda t=t:_yahoo_etf(t))
        if x: funds.append(x)
    if not funds:return {'status':'unavailable','score':50,'funds':[]}
    total=sum(x['dollarVolumeUsd'] for x in funds) or 1
    ret=sum(x['return1d']*x['dollarVolumeUsd'] for x in funds)/total
    vr=sum(x['volumeVs20d']*x['dollarVolumeUsd'] for x in funds)/total
    score=round(clamp(50+ret*5+(vr-1)*12))
    label='Strong demand' if score>=65 else 'Positive demand' if score>=55 else 'Balanced' if score>=45 else 'Weak demand' if score>=35 else 'Strong selling pressure'
    return {'status':'live proxy','score':score,'label':label,'return1d':ret,'volumeVs20d':vr,'aggregateDollarVolumeUsd':total,'funds':funds}

def etf_flow():
    rows=[]; source=None
    for url in ['https://farside.co.uk/bitcoin-etf-flow-all-data/','https://farside.co.uk/btc/']:
        try:
            rows=_parse_farside(url)
            if rows: source=url; break
        except: pass
    proxy=etf_demand_proxy()
    if rows:
        latest=rows[-1]; last5=sum(x['usdMillions'] for x in rows[-5:]); last20=sum(x['usdMillions'] for x in rows[-20:])
        flow_score=round(clamp(50+latest['usdMillions']/15))
        combined=round(clamp(flow_score*0.72+proxy.get('score',50)*0.28))
        return {'status':'live','source':'Farside','sourceUrl':source,'dailyUsdMillions':latest['usdMillions'],'date':latest['date'],'fiveDayUsdMillions':last5,'twentyDayUsdMillions':last20,'flowScore':flow_score,'proxy':proxy,'score':combined,'scoreSource':'confirmed flow + ETF demand proxy'}
    return {'status':'proxy only','dailyUsdMillions':None,'fiveDayUsdMillions':None,'twentyDayUsdMillions':None,'proxy':proxy,'score':proxy.get('score',50),'scoreSource':'ETF demand proxy only'}



def btc_daily_history_four_years():
    url='https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=4y&interval=1d&events=history'
    d=jget(url)['chart']['result'][0]
    ts=d.get('timestamp',[])
    quote=d.get('indicators',{}).get('quote',[{}])[0]
    closes=quote.get('close',[])
    rows=[]
    for t,c in zip(ts,closes):
        if c is None:
            continue
        rows.append({
            'day':datetime.fromtimestamp(int(t),tz=timezone.utc).strftime('%Y-%m-%d'),
            'usd':round(float(c),2)
        })
    return rows[-1465:]

def daily_btc_history():
    return btc_daily_history_four_years()

def weekly_btc_history():
    daily=btc_daily_history_four_years()
    weeks={}
    for row in daily:
        day=datetime.strptime(row['day'],'%Y-%m-%d')
        monday=(day-timedelta(days=day.weekday())).strftime('%Y-%m-%d')
        weeks[monday]={'week':monday,'usd':row['usd']}
    return list(weeks.values())[-208:]

def article_significance(title, source=''):
    t=(title or '').lower();score=18;tags=[];impact='';why='This story may affect market expectations, but its broader financial impact has not yet been confirmed.'
    rules=[
      (['federal reserve','fed rate','fomc','ecb','rba','bank of japan','interest rate decision'],38,['Macro','Bonds','Global Liquidity'],'Central-bank policy can alter borrowing costs, currencies, bond yields and global liquidity.'),
      (['inflation','cpi','pce','jobs report','payrolls','gdp','recession'],30,['Macro','Bonds','Equities'],'Major economic data can change interest-rate expectations and risk-asset pricing.'),
      (['sec','regulator','regulation','ban','approval','court ruling'],27,['Regulation','Bitcoin'],'Regulatory decisions can change market access, compliance costs and institutional participation.'),
      (['bitcoin etf','etf inflow','etf outflow','blackrock','fidelity'],25,['Bitcoin','Institutional'],'ETF developments can affect institutional demand and Bitcoin market liquidity.'),
      (['war','attack','sanctions','tariff','trade war','geopolitical'],30,['Macro','Gold','Equities'],'Geopolitical shocks can move energy, currencies, safe-haven assets and global risk appetite.'),
      (['bank failure','banking crisis','credit crisis','default'],34,['Banks','Bonds','Global Liquidity'],'Financial-system stress can tighten credit conditions and trigger broad risk repricing.'),
      (['oil','opec','energy prices'],18,['Commodities','Macro'],'Energy-price changes can influence inflation, corporate costs and monetary-policy expectations.'),
      (['earnings','nvidia','apple','microsoft','amazon','alphabet','meta'],13,['Equities','AI Technology'],'Large-company results can move major equity indices and technology-sector expectations.'),
      (['bitcoin','crypto','stablecoin'],12,['Bitcoin'],'Crypto-specific developments can affect digital-asset liquidity and sentiment.')
    ]
    for terms,points,new_tags,new_why in rules:
        if any(term in t for term in terms):
            score+=points;tags.extend(new_tags);why=new_why
    score=max(1,min(100,score));stars=5 if score>=82 else 4 if score>=65 else 3 if score>=45 else 2 if score>=28 else 1
    bullish=['cuts rates','rate cut','approval','inflows','inflation falls','inflation cools','stimulus','liquidity rises']
    bearish=['raises rates','rate hike','outflows','ban','recession','default','war','attack','inflation rises','inflation surges']
    if any(x in t for x in bullish):impact='Bullish'
    elif any(x in t for x in bearish):impact='Bearish'
    elif score>=65:impact=''
    else:impact='Neutral'
    return {'impactScore':score,'stars':stars,'impact':impact,'tags':list(dict.fromkeys(tags))[:4],'why':why}

def news():
    queries=['bitcoin markets when:3d','Federal Reserve inflation interest rates markets when:3d','global liquidity stocks gold markets when:3d']
    items=[];seen=set()
    for q in queries:
        try:
            url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':q,'hl':'en-AU','gl':'AU','ceid':'AU:en'})
            root=ET.fromstring(get(url))
            for node in root.findall('.//item'):
                title=(node.findtext('title') or '').strip();link=(node.findtext('link') or '').strip();date=(node.findtext('pubDate') or '').strip();source=node.findtext('source') or '';key=re.sub(r'[^a-z0-9 ]','',title.lower())
                if title and link and key not in seen:
                    seen.add(key);item={'title':title,'url':link,'source':source,'date':date};item.update(article_significance(title,source));items.append(item)
        except Exception:pass
    def parsed_date(item):
        try:return email.utils.parsedate_to_datetime(item.get('date','')).timestamp()
        except Exception:return 0
    items.sort(key=parsed_date,reverse=True)
    return items[:20]

def events():
    return [
      {'tag':'UPCOMING','title':'Federal Reserve policy meetings and releases','source':'Federal Reserve','url':'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'},
      {'tag':'UPCOMING','title':'US CPI and inflation release calendar','source':'U.S. Bureau of Labor Statistics','url':'https://www.bls.gov/schedule/news_release/cpi.htm'},
      {'tag':'UPCOMING','title':'US GDP and economic release schedule','source':'U.S. Bureau of Economic Analysis','url':'https://www.bea.gov/news/schedule'},
      {'tag':'LIVE','title':'Market-implied Federal Reserve rate probabilities','source':'CME FedWatch','url':'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html'}
    ]

def save_daily_to_db(conn, today, btc, aud, fg, st, etf, ma, ch, liq_scores, btc_score, proxies):
    """
    Upsert today's live data into all historical tables.
    Uses INSERT OR REPLACE so running the updater twice in one day is safe.
    Any individual table failure is logged but does not abort the others.
    """
    def _exec(sql, params):
        try:
            conn.execute(sql, params)
        except Exception as e:
            print(f'  DB insert warning ({sql[:40]}...): {e}', file=sys.stderr)

    try:
        if btc and aud:
            _exec(
                "INSERT OR REPLACE INTO btc_daily "
                "(date, price_usd, price_aud, source, updated_at) "
                "VALUES (?, ?, ?, 'live_update', strftime('%Y-%m-%dT%H:%M:%SZ','now'))",
                (today, round(float(btc), 2), round(float(btc * aud), 2))
            )
        fg_val = fg.get('value') if isinstance(fg, dict) else None
        if fg_val is not None:
            _exec(
                "INSERT OR REPLACE INTO fear_greed (date, value, label, change_24h) "
                "VALUES (?, ?, ?, ?)",
                (today, int(fg_val), fg.get('label', ''), fg.get('change24h', 0))
            )
        if isinstance(st, dict):
            _exec(
                "INSERT OR REPLACE INTO stablecoin_market_cap "
                "(date, market_cap_usd, change_1d, change_7d, change_30d) VALUES (?, ?, ?, ?, ?)",
                (today, st.get('marketCapUsd'), st.get('change1d', 0),
                 st.get('change7d', 0), st.get('change30d', 0))
            )
        if isinstance(etf, dict):
            _exec(
                "INSERT OR REPLACE INTO etf_flows "
                "(date, daily_usd_millions, five_day_usd_millions, twenty_day_usd_millions, "
                "flow_score, combined_score, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (today, etf.get('dailyUsdMillions'), etf.get('fiveDayUsdMillions'),
                 etf.get('twentyDayUsdMillions'), etf.get('flowScore'),
                 etf.get('score'), etf.get('source', etf.get('status', '')))
            )
        ma_score = ma.get('score') if isinstance(ma, dict) else None
        ch_score = ch.get('score') if isinstance(ch, dict) else None
        _exec(
            "INSERT OR REPLACE INTO scores "
            "(date, macro_score, onchain_score, btc_score, fear_greed_value) VALUES (?, ?, ?, ?, ?)",
            (today, ma_score, ch_score, btc_score,
             int(fg_val) if fg_val is not None else None)
        )
        if isinstance(liq_scores, dict):
            _exec(
                "INSERT OR REPLACE INTO capital_allocation "
                "(date, cash_bills, govt_bonds, global_equities, ai_technology, "
                "emerging_markets, bitcoin, stablecoins, gold, silver) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (today,
                 liq_scores.get('Cash & short-term bills'),
                 liq_scores.get('Government bonds & fixed income'),
                 liq_scores.get('Global equities'),
                 liq_scores.get('AI technology'),
                 liq_scores.get('Emerging markets'),
                 liq_scores.get('Bitcoin'),
                 liq_scores.get('Stablecoins'),
                 liq_scores.get('Gold'),
                 liq_scores.get('Silver'))
            )
        if isinstance(proxies, dict) and isinstance(ma, dict):
            def _mav(series, key):
                s = ma.get(series)
                return s.get(key) if isinstance(s, dict) else None
            _exec(
                "INSERT OR REPLACE INTO market_data "
                "(date, gold_price, gold_change_20d, sp500_change_20d, nasdaq_change_20d, "
                "dxy_value, dxy_change_20d, us_10y_yield, us_10y_change_20d) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (today,
                 proxies.get('gold', {}).get('last'),
                 proxies.get('gold', {}).get('change20d'),
                 proxies.get('equities', {}).get('change20d'),
                 proxies.get('ai', {}).get('change20d'),
                 _mav('DTWEXBGS', 'value'),
                 _mav('DTWEXBGS', 'change20'),
                 _mav('DGS10', 'value'),
                 _mav('DGS10', 'change20'))
            )
        conn.commit()
    except Exception as e:
        print(f'Warning: DB save failed, rolling back: {e}', file=sys.stderr)
        try:
            conn.rollback()
        except Exception:
            pass


def _db_history():
    """
    Return (daily_list, weekly_list) from SQLite.

    If the database is empty, runs the four-year import first so the
    History & Trends page has data on the very first updater run.
    Falls back to ([], []) on any error.
    """
    if not _DB_AVAILABLE:
        return [], []
    try:
        daily = get_daily_history()
        if not daily:
            print('DB empty -- importing four-year BTC history...', file=sys.stderr)
            _import_history_mod.import_history(verbose=True)
            daily = get_daily_history()
        weekly = get_weekly_history()
        return daily, weekly
    except Exception as e:
        print(f'Warning: DB history read failed: {e}', file=sys.stderr)
        return [], []


def main():
    previous={}
    try: previous=json.loads(OUT.read_text(encoding='utf-8'))
    except: pass

    price=safe(price_sources)
    if price:
        btc,exchanges,btc24=price
    else:
        old=previous.get('btc',{})
        btc=old.get('usd'); exchanges=old.get('sources',[]); btc24=old.get('change24h',0)
    aud=safe(fx, previous.get('fx',{}).get('usdAud',1.43))
    fg=safe(fear, previous.get('fearGreed',{'value':50,'label':'Neutral','change24h':0}))
    st=safe(stablecoins, previous.get('stablecoins',{'marketCapUsd':None,'change1d':0,'change7d':0,'change30d':0}))
    ma=safe(macro, previous.get('macro',{'score':50}))
    ch=safe(chain, previous.get('onchain',{'score':50}))
    etf=safe(etf_flow, previous.get('etf',{'status':'unavailable','dailyUsdMillions':None,'score':50}))

    # Guaranteed market-based indication when confirmed flow and ETF trading proxy fail.
    proxy=etf.get('proxy') or {}
    if proxy.get('status') not in ('live proxy',):
        market_score=round(clamp(50+(btc24 or 0)*3+(float(fg.get('value',50))-50)*0.25+(float(st.get('change7d') or 0))*4))
        label='Strong demand indication' if market_score>=65 else 'Positive demand indication' if market_score>=55 else 'Balanced demand indication' if market_score>=45 else 'Weak demand indication' if market_score>=35 else 'Strong selling indication'
        etf['proxy']={'status':'market proxy','score':market_score,'label':label,'return1d':btc24 or 0,'volumeVs20d':None,'funds':[]}
        if etf.get('status') in (None,'unavailable','proxy only'): etf['status']='market proxy only'
        if etf.get('score') in (None,50): etf['score']=market_score

    proxies={}
    for name,sym in [('gold','gld.us'),('silver','slv.us'),('equities','spy.us'),('ai','qqq.us'),('emerging','eem.us'),('bonds','tlt.us'),('cash','bil.us')]:
        proxies[name]=safe(lambda sym=sym:stooq(sym),previous.get('proxies',{}).get(name,{'change20d':0}))
    sentiment=round(clamp(float(fg.get('value',50))))
    btc_score=round(clamp(0.22*float(etf.get('score',50))+0.20*float(ma.get('score',50))+0.18*float(ch.get('score',50))+0.20*sentiment+0.20*clamp(50+float(st.get('change7d') or 0)*8)))
    risk_score=float(ma.get('score',50))
    scores={
      'Cash & short-term bills':round(clamp(58+proxies['cash'].get('change20d',0)*4+(50-sentiment)*0.30+(50-risk_score)*0.18)),
      'Government bonds & fixed income':round(clamp(52+proxies['bonds'].get('change20d',0)*4+(50-sentiment)*0.18+(50-risk_score)*0.12)),
      'Global equities':round(clamp(53+proxies['equities'].get('change20d',0)*3+risk_score*0.15+(sentiment-50)*0.18)),
      'AI technology':round(clamp(54+proxies['ai'].get('change20d',0)*3.5+risk_score*0.17+(sentiment-50)*0.20)),
      'Emerging markets':round(clamp(49+proxies['emerging'].get('change20d',0)*3+(risk_score-50)*0.16)),
      'Bitcoin':btc_score,
      'Stablecoins':round(clamp(55+(float(st.get('change7d') or 0)*4)+(50-sentiment)*0.10)),
      'Gold':round(clamp(55+proxies['gold'].get('change20d',0)*3+(100-risk_score)*0.12)),
      'Silver':round(clamp(51+proxies['silver'].get('change20d',0)*3+proxies['gold'].get('change20d',0)*0.8)),
    }
    trends={
      'Cash & short-term bills':float(proxies['cash'].get('change20d',0) or 0),
      'Government bonds & fixed income':float(proxies['bonds'].get('change20d',0) or 0),
      'Global equities':float(proxies['equities'].get('change20d',0) or 0),
      'AI technology':float(proxies['ai'].get('change20d',0) or 0),
      'Emerging markets':float(proxies['emerging'].get('change20d',0) or 0),
      'Bitcoin':float(btc24 or 0),
      'Stablecoins':float(st.get('change7d') or 0),
      'Gold':float(proxies['gold'].get('change20d',0) or 0),
      'Silver':float(proxies['silver'].get('change20d',0) or 0),
      'Other':0,
    }
    live_news=safe(news,[]) or previous.get('news',[]) or []

    # v8.4: persist today's data to SQLite and read history back from the DB.
    today=datetime.now(timezone.utc).strftime('%Y-%m-%d')
    if _DB_AVAILABLE:
        try:
            _db_conn=init_db()
            save_daily_to_db(_db_conn, today, btc, aud, fg, st, etf, ma, ch, scores, btc_score, proxies)
            _db_conn.close()
        except Exception as _db_err:
            print(f'Warning: DB daily save failed: {_db_err}', file=sys.stderr)

    # Retrieve history from SQLite; fall back to Yahoo Finance fetch if DB is empty.
    daily_hist, weekly_hist = _db_history()
    if not daily_hist:
        daily_hist=safe(daily_btc_history,[]) or []
    if not weekly_hist:
        weekly_hist=safe(weekly_btc_history,[]) or []

    out={'generatedAt':datetime.now(timezone.utc).isoformat(),'status':'Live scheduled research snapshot' if btc else 'Partial live snapshot • retained last BTC price','btc':{'usd':btc,'aud':btc*aud if btc else None,'change24h':btc24,'method':'trimmed average / median check','sources':exchanges},'fx':{'usdAud':aud,'audUsd':1/aud},'fearGreed':fg,'stablecoins':st,'etf':etf,'macro':ma,'onchain':ch,'liquidityScores':scores,'liquidityTrends':trends,'historyWeekly':weekly_hist,'historyDaily':daily_hist,'proxies':proxies,'news':live_news,'events':events()}
    OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out,indent=2),encoding='utf-8')
if __name__=='__main__': main()
