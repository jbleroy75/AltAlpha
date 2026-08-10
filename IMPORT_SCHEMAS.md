# Import schemas

Place optional legally obtained data exports in `data/imports/`.

- Congress: `id,member,asset,ticker,transaction_date,filing_date,type,amount,url`
- Patents: `patent_id,assignee,ticker,title,publication_date,url`
- Options: `id,ticker,timestamp,put_call,side,premium,size,price,score`
- Short interest: common FINRA export field names are accepted.
- Corporate movement data: `registration,departure_time,arrival_time,origin,destination,distance_km,published_at`
- Transcripts: `id,ticker,company,published_at,text,sentiment,url`

The synchronizer reports `missing_import` until an expected optional export is present.
