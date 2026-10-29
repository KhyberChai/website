#!/usr/bin/env python3
"""Collect candidates, merge explicitly approved CSV rows, and build an upload ZIP.
Standard library only. No website scraping, public writes or credential files.
"""
import argparse,csv,datetime as dt,hashlib,html,json,os,re,shutil,tempfile,urllib.parse,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LOCATIONS={'vancouver':('Khyber Chai House, Vancouver','ChIJUSS2bRBxhlQRrllHGRZrZ14'),'surrey':('Khyber Chai & Grill, Surrey','ChIJK1TG32rbhVQRJ9A0Xxss09U')}
FIELDS=['kind','id','location_key','reviewer','rating','excerpt','url','title','image','remote_image','handle','category','approved','source','published','expires']
def request(url,token=None,form=None):
 headers={'User-Agent':'KhyberWebsiteRefresh/1.0'}
 if token:headers['Authorization']='Bearer '+token
 data=urllib.parse.urlencode(form).encode() if form else None
 with urllib.request.urlopen(urllib.request.Request(url,data=data,headers=headers),timeout=30) as r:return json.load(r)
def truth(v):return str(v).lower()=='true'
def valid_url(v):
 u=urllib.parse.urlparse(v or '')
 return u.scheme=='https' and bool(u.netloc) and not u.username and not u.password
def local_image(v):
 p=(ROOT/'assets'/v).resolve()
 return bool(v) and p.is_file() and p.is_relative_to((ROOT/'assets').resolve()) and p.suffix.lower() in ['.jpg','.jpeg','.png','.webp']
def collect(days):
 rows=[];status=[];cutoff=dt.datetime.now(dt.timezone.utc)-dt.timedelta(days=days)
 token=os.getenv('GBP_ACCESS_TOKEN')
 if not token and all(os.getenv(k) for k in ['GOOGLE_CLIENT_ID','GOOGLE_CLIENT_SECRET','GOOGLE_REFRESH_TOKEN']):
  try:token=request('https://oauth2.googleapis.com/token',form={'client_id':os.environ['GOOGLE_CLIENT_ID'],'client_secret':os.environ['GOOGLE_CLIENT_SECRET'],'refresh_token':os.environ['GOOGLE_REFRESH_TOKEN'],'grant_type':'refresh_token'})['access_token']
  except Exception:status.append('Google OAuth failed; existing content preserved.')
 for key,(name,place) in LOCATIONS.items():
  parent=os.getenv('GBP_'+key.upper()+'_PARENT','')
  if not token or not re.fullmatch(r'accounts/\d+/locations/\d+',parent):status.append(key+': Google reviews skipped; credentials/location resource missing.');continue
  try:
   page='';seen=set();count=0
   while True:
    q={'pageSize':50,'orderBy':'updateTime desc'}
    if page:q['pageToken']=page
    data=request('https://mybusiness.googleapis.com/v4/'+parent+'/reviews?'+urllib.parse.urlencode(q),token)
    reviews=data.get('reviews',[]);older=False
    for r in reviews:
     stamp=r.get('updateTime') or r.get('createTime','')
     if stamp and dt.datetime.fromisoformat(stamp.replace('Z','+00:00'))<cutoff:older=True;continue
     if r.get('starRating')!='FIVE' or not r.get('comment','').strip():continue
     rows.append({'kind':'review','id':'gbp-'+key+'-'+r['reviewId'],'location_key':key,'reviewer':r.get('reviewer',{}).get('displayName','Google reviewer'),'rating':5,'excerpt':r['comment'],'url':'https://www.google.com/maps/place/?q=place_id:'+place,'approved':'false','source':'Google Business Profile API','published':r.get('createTime','')});count+=1
    page=data.get('nextPageToken','')
    if older or not page:break
    if page in seen:raise ValueError('Repeated page token')
    seen.add(page)
   status.append(key+': fetched '+str(count)+' recent five-star review candidates.')
  except Exception:status.append(key+': Google fetch failed; existing content preserved. Check API access and credentials.')
 for key in LOCATIONS:
  prefix='IG_'+key.upper();token=os.getenv(prefix+'_TOKEN');uid=os.getenv(prefix+'_USER_ID');version=os.getenv('INSTAGRAM_GRAPH_VERSION')
  if not token or not uid or not version:status.append(key+': Instagram skipped; connection missing. CSV import remains available.');continue
  if not re.fullmatch(r'\d+',uid) or not re.fullmatch(r'v\d+\.\d+',version):status.append(key+': invalid Instagram ID/version.');continue
  try:
   after='';seen=set();count=0
   while True:
    q={'fields':'id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,username','limit':50}
    if after:q['after']=after
    data=request('https://graph.instagram.com/'+version+'/'+uid+'/media?'+urllib.parse.urlencode(q),token);older=False
    for m in data.get('data',[]):
     stamp=m.get('timestamp','')
     if stamp and dt.datetime.fromisoformat(stamp.replace('Z','+00:00'))<cutoff:older=True;continue
     rows.append({'kind':'photo','id':'ig-'+m['id'],'location_key':key,'url':m.get('permalink',''),'title':m.get('caption','')[:160],'remote_image':m.get('thumbnail_url') or m.get('media_url',''),'handle':m.get('username',''),'category':'instagram','approved':'false','source':'Instagram API; review image, caption, expiry and reuse rights before approval','published':stamp});count+=1
    page=data.get('paging',{});after=page.get('cursors',{}).get('after','')
    if older or not page.get('next') or not after:break
    if after in seen:raise ValueError('Repeated cursor')
    seen.add(after)
   status.append(key+': fetched '+str(count)+' recent Instagram candidates.')
  except Exception:status.append(key+': Instagram fetch failed; existing content preserved. Check token, API version and permissions.')
 return rows,status
def review_html(r):
 e=html.escape;stars='<p class="review-stars" aria-label="5 out of 5 stars">★★★★★</p>' if r.get('rating')==5 else ''
 return '<figure class="location-card" style="margin:0">'+stars+'<blockquote>“'+e(r['excerpt'])+'”</blockquote><figcaption class="review-attribution"><a href="'+e(r['url'],quote=True)+'" target="_blank" rel="noopener">'+e(r['reviewer'])+' · Google review</a><div>'+e(r['location'])+'</div></figcaption></figure>'
def apply(rows,data):
 report=[]
 for r in rows:
  if not truth(r.get('approved')):continue
  key=r.get('location_key');kind=r.get('kind')
  if key not in LOCATIONS or kind not in ['photo','review'] or not r.get('id') or not valid_url(r.get('url')):raise ValueError('Approved row has invalid kind, ID, location or HTTPS URL')
  common={'id':r['id'],'approved':True,'url':r['url'],'location_key':key,'location':LOCATIONS[key][0],'source':r.get('source') or 'Owner-supplied verified public material','published':r.get('published','')}
  if kind=='review':
   if str(r.get('rating'))!='5' or not r.get('reviewer') or not r.get('excerpt'):raise ValueError('Only verified five-star reviews with reviewer and excerpt can be imported')
   item={**common,'rating':5,'reviewer':r['reviewer'],'excerpt':r['excerpt']};bucket='reviews'
  else:
   if not r.get('title') or not r.get('handle') or not local_image(r.get('image')):raise ValueError('Photo needs title, handle and an existing local image in assets/')
   expires=r.get('expires','')
   if expires and dt.date.fromisoformat(expires)<dt.date.today():report.append('Skipped expired item '+r['id']);continue
   item={**common,'image':r['image'],'title':r['title'],'alt':r['title'],'handle':r['handle'].lstrip('@'),'category':r.get('category') or 'instagram','expires':expires};bucket='photos'
  existing=next((i for i,x in enumerate(data[bucket]) if x.get('id')==item['id'] or x.get('url')==item['url'] and bucket=='photos'),None)
  if existing is None:data[bucket].append(item)
  else:data[bucket][existing]=item
  report.append('Merged '+item['id'])
 return report
def main():
 p=argparse.ArgumentParser();p.add_argument('--days',type=int,default=14);p.add_argument('--apply-approved',action='store_true');p.add_argument('--output',default='weekly-output');args=p.parse_args()
 out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
 (out/'weekly-upload.zip').unlink(missing_ok=True)
 rows,status=collect(args.days)
 with (out/'candidates.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
 data=json.loads((ROOT/'assets/community-content.json').read_text());before=json.dumps(data,sort_keys=True)
 if args.apply_approved:
  for file in sorted((ROOT/'content/inbox').glob('*.csv')):
   with file.open(newline='',encoding='utf-8-sig') as f:status+=apply(list(csv.DictReader(f)),data)
 if before!=json.dumps(data,sort_keys=True):
  # Stage a complete validated update before touching files.
  writes={'assets/community-content.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n'}
  for name,key in [('index.html','all'),('chai/index.html','vancouver'),('grill/index.html','surrey')]:
   s=(ROOT/name).read_text();selected=[]
   for loc in (LOCATIONS if key=='all' else [key]):selected += [r for r in data['reviews'] if r.get('approved') and r.get('rating')==5 and r.get('location_key')==loc][-4:]
   old=re.search(r'<section class="wrap section reviews".*?</section>',s,re.S)
   if not old:raise ValueError('Review section missing in '+name)
   block=old.group();start=block.index('<div class="locations">');block=block[:start]+'<div class="locations">'+''.join(review_html(r) for r in selected)+'</div></section>'
   writes[name]=s[:old.start()]+block+s[old.end():]
  for name,text in writes.items():(ROOT/name).write_text(text)
  status.append('Approved content applied; HTML review fallbacks synchronized.')
 else:status.append('No approved content changes. Existing website content preserved.')
 if before!=json.dumps(data,sort_keys=True):
  # Only publish approved website files; never include tokens, reports or CSV candidates.
  with zipfile.ZipFile(out/'weekly-upload.zip','w',zipfile.ZIP_DEFLATED) as z:
   for name in ['index.html','chai/index.html','grill/index.html','assets/community-content.json']:
    z.write(ROOT/name,name)
   for r in data['photos']:
    if r.get('approved') and local_image(r.get('image')):z.write(ROOT/'assets'/r['image'],'assets/'+r['image'])
 (out/'REPORT.txt').write_text('\n'.join(status)+'\nCandidates are not automatically approved or published.\n')
 connected=any('fetched ' in line for line in status)
 errors=any('failed' in line for line in status)
 changed=before!=json.dumps(data,sort_keys=True)
 state='UPDATE READY' if changed else ('CONNECTION ERROR' if errors else ('CANDIDATES READY' if rows else ('NO NEW CANDIDATES' if connected else 'NO SOURCES CONNECTED')))
 summary='# Weekly content refresh: '+state+'\n\n'+str(len(rows))+' candidate items found. '+('Upload ZIP created.' if changed else 'No upload ZIP created because no approved content changed.')+'\n\n'+'\n'.join('- '+line for line in status)+'\n'
 (out/'SUMMARY.md').write_text(summary)
 (out/'REPORT.txt').write_text(state+'\n\n'+'\n'.join(status)+'\n'+('Upload ZIP created.' if changed else 'No approved changes; no upload ZIP created.')+'\n')
 if os.getenv('GITHUB_STEP_SUMMARY'):
  with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write(summary)
 if state in ['NO SOURCES CONNECTED','CONNECTION ERROR']:print('::warning::'+state+' — open SUMMARY.md for setup status; no discovery completed for missing/failed sources.')
 print(summary);print('Output: '+str(out))
if __name__=='__main__':main()
