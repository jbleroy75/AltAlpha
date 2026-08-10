import requests,json,re,time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ..config import settings
from ..util import put_event,dt,num
SEC="https://www.sec.gov";H=lambda:{"User-Agent":settings.sec_user_agent,"Accept-Encoding":"gzip, deflate"}
def company_tickers():
    r=requests.get(SEC+"/files/company_tickers.json",headers=H(),timeout=30);r.raise_for_status();return {str(v["cik_str"]).zfill(10):v["ticker"].upper() for v in r.json().values()}
def collect_form4(s,count=40):
    u=SEC+f"/cgi-bin/browse-edgar?action=getcurrent&type=4&owner=include&count={count}&output=atom";r=requests.get(u,headers=H(),timeout=30);r.raise_for_status();feed=BeautifulSoup(r.content,"xml");cmap=company_tickers();n=0
    for en in feed.find_all("entry"):
        link=en.find("link");furl=link.get("href") if link else None;upd=en.find("updated")
        if not furl or not upd:continue
        pub=dt(upd.get_text(strip=True));accession=re.search(r"acc-no=([0-9-]+)",furl);acc=accession.group(1) if accession else furl.split("/")[-1];page=requests.get(furl,headers=H(),timeout=30);page.raise_for_status();soup=BeautifulSoup(page.text,"html.parser");xml=None
        for a in soup.select("a[href]"):
            href=a.get("href","")
            if href.lower().endswith(".xml") and ("ownership" in href.lower() or "form4" in href.lower()):xml=urljoin(SEC,href);break
        if not xml:continue
        xr=requests.get(xml,headers=H(),timeout=30);xr.raise_for_status();x=BeautifulSoup(xr.content,"xml");get=lambda node,tag:(node.find(tag).get_text(strip=True) if node.find(tag) else None);cik=get(x,"issuerCik");ticker=cmap.get((cik or "").zfill(10));issuer=get(x,"issuerName");actor=get(x,"rptOwnerName")
        for i,t in enumerate(x.find_all("nonDerivativeTransaction")):
            code=get(t,"transactionCode");side="purchase" if code=="P" else "sale" if code=="S" else (code or "other").lower();q=num(get(t,"transactionShares"));p=num(get(t,"transactionPricePerShare"));n+=put_event(s,source="sec_form4",source_id=f"{acc}:{i}",event_type="insider_trade",ticker=ticker,entity_name=issuer,actor_name=actor,side=side,value=q*p if q and p else None,quantity=q,price=p,score=None,event_at=dt(get(t,"transactionDate")),published_at=pub,url=furl,raw_json=json.dumps({"code":code,"xml":xml}))
        time.sleep(.11)
    return n

def collect_13f(s,cik):
    cik=str(cik).zfill(10);sub=requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json",headers=H(),timeout=30);sub.raise_for_status();j=sub.json();recent=j["filings"]["recent"];n=0
    for i,form in enumerate(recent["form"]):
        if form not in ("13F-HR","13F-HR/A"):continue
        acc=recent["accessionNumber"][i];primary=recent["primaryDocument"][i];filed=recent["filingDate"][i];base=f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-','')}/";idx=requests.get(base,headers=H(),timeout=30);idx.raise_for_status();soup=BeautifulSoup(idx.text,"html.parser");xmls=[urljoin(base,a.get("href")) for a in soup.select("a[href]") if a.get("href","").lower().endswith(".xml")];info=None
        for xu in xmls:
            tx=requests.get(xu,headers=H(),timeout=30)
            if b"infoTable" in tx.content:info=BeautifulSoup(tx.content,"xml");break
        if not info:continue
        for k,row in enumerate(info.find_all("infoTable")):
            g=lambda tag:(row.find(tag).get_text(strip=True) if row.find(tag) else None);issuer=g("nameOfIssuer");val=num(g("value"));shares=num(g("sshPrnamt"));cusip=g("cusip");n+=put_event(s,source="sec_13f",source_id=f"{acc}:{k}",event_type="institutional_holding",ticker=None,entity_name=issuer,actor_name=j.get("name"),side="holding",value=val,quantity=shares,price=None,score=None,event_at=dt(recent.get("reportDate",[filed]*len(recent["form"]))[i] or filed),published_at=dt(filed),url=base+primary,raw_json=json.dumps({"cusip":cusip,"cik":cik}))
    return n

def collect_recent_13f(s,count=20):
    u=SEC+f"/cgi-bin/browse-edgar?action=getcurrent&type=13F-HR&owner=include&count={count}&output=atom";r=requests.get(u,headers=H(),timeout=30);r.raise_for_status();feed=BeautifulSoup(r.content,"xml");ciks=[]
    for en in feed.find_all("entry"):
        link=en.find("link");href=link.get("href") if link else "";title=en.find("title").get_text(" ",strip=True) if en.find("title") else "";m=re.search(r"CIK[ =:]*(\d+)",title,re.I) or re.search(r"/data/(\d+)/",href)
        if m and m.group(1) not in ciks:ciks.append(m.group(1))
    n=0
    for cik in ciks[:count]:
        try:n+=collect_13f(s,cik)
        except Exception:pass
        time.sleep(.11)
    return n
