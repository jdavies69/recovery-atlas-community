#!/usr/bin/env python3
"""Run a bounded Recovery Atlas job using Python 3 and public data."""
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

REPO = 'jdavies69/recovery-atlas-community'
ROOT = Path(__file__).resolve().parent
JOBS = json.loads((ROOT / 'jobs/catalog.json').read_text())
DATA = 'https://data.lacity.org/resource/9w5z-rg2h.json'
COLUMNS = 'address,permit,inspection_date,inspection,inspection_result'

def load(url):
    request = Request(url, headers={'User-Agent': 'RecoveryAtlas-Community/1.0'})
    with urlopen(request, timeout=40) as response:
        return json.load(response)

def run_job(job):
    results = []
    for home in job['homes']:
        permit = home['permit'].replace('-', ' ')
        query = {'permit': permit, '$select': COLUMNS, '$limit': 1000,
                 '$order': 'inspection_date,inspection,inspection_result',
                 '$where': "inspection_date < '2026-11-25T00:00:00'"}
        url = DATA + '?' + urlencode(query)
        rows = load(url)
        if not isinstance(rows, list) or len(rows) >= 1000:
            raise ValueError('Unexpected or incomplete city response.')
        events = []
        for row in rows:
            if row['permit'] != permit or row['address'].strip().upper() != home['address']:
                raise ValueError('Address or permit mismatch. Flag the job for review.')
            day = row['inspection_date'][:10]
            date.fromisoformat(day)
            events.append({'date': day, 'inspection': row['inspection'],
                           'result': row.get('inspection_result') or 'No result published'})
        results.append({**home, 'source': url, 'events': events})
    return {'job': job['id'], 'through': '2026-11-24', 'homes': results}

def command(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()

def submit(job, path):
    if not shutil.which('gh') or not shutil.which('git'):
        raise SystemExit('Install Git and GitHub CLI, or submit the result through the job issue.')
    login = command('gh','api','user','--jq','.login')
    head = 'contribute/' + job['id']
    fork = REPO if login == REPO.split('/')[0] else login+'/'+REPO.split('/')[1]
    if fork != REPO:
        command('gh','repo','fork',REPO,'--clone=false','--remote=false')
    with tempfile.TemporaryDirectory() as tmp:
        command('git','clone','--quiet','--depth','1','https://github.com/'+REPO+'.git',tmp)
        output = Path(tmp)/'results'/path.name
        if output.exists():
            raise SystemExit('This job already has an accepted result. Pick another job.')
        command('git','switch','-c',head,cwd=tmp)
        shutil.copyfile(path,output)
        command('git','add','--','results/'+path.name,cwd=tmp)
        command('git','-c','user.name='+login,'-c','user.email='+login+'@users.noreply.github.com',
                'commit','-m','Submit '+job['id'],cwd=tmp)
        command('git','-c','credential.helper=','-c','credential.helper=!gh auth git-credential',
                'push','https://github.com/'+fork+'.git','HEAD:refs/heads/'+head,cwd=tmp)
        print(command('gh','pr','create','--repo',REPO,'--base','main','--head',
                      (login+':' if fork!=REPO else '')+head,'--title',job['title'],
                      '--body','Contributed public inspection records. Run the job from trusted main to verify.\n\nCloses #'+str(job['issue']),cwd=tmp))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job',nargs='?',help='Job ID. Defaults to an available inspection job.')
    parser.add_argument('--list',action='store_true')
    parser.add_argument('--submit',action='store_true',help='Open a GitHub pull request with your own gh login.')
    args=parser.parse_args()
    if args.list:
        for job in JOBS:
            print(job['id'], '—', job['title'], '· https://github.com/'+REPO+'/issues/'+str(job['issue']))
        return
    if args.job:
        job=next((j for j in JOBS if j['id']==args.job),None)
        if not job: raise SystemExit('Unknown job. Use --list.')
    else:
        issues=load('https://api.github.com/repos/'+REPO+'/issues?state=open&per_page=100')
        available={i['number'] for i in issues if 'pull_request' not in i}
        prs=load('https://api.github.com/repos/'+REPO+'/pulls?state=open&per_page=100')
        pending={p['head']['ref'] for p in prs}
        jobs=[j for j in JOBS if j['type']=='inspection' and j['issue'] in available
              and 'contribute/'+j['id'] not in pending and not (ROOT/'results'/(j['id']+'.json')).exists()]
        if not jobs: raise SystemExit('No unsubmitted inspection jobs. See --list for image briefs.')
        job=jobs[0]
    if job['type']=='image':
        print((ROOT/'jobs'/(job['id']+'.md')).read_text())
        return
    data=run_job(job)
    out=Path('out');out.mkdir(exist_ok=True)
    path=out/(job['id']+'.json')
    with tempfile.NamedTemporaryFile(mode='w',dir=out,delete=False) as f:
        json.dump(data,f,indent=2,ensure_ascii=False);f.write('\n')
    os.replace(f.name,path)
    print(path,'·',sum(len(h['events']) for h in data['homes']),'dated inspection entries.')
    if args.submit:submit(job,path)
    else:print('Review the result. To submit: python3 contribute.py '+job['id']+' --submit')

if __name__=='__main__':
    main()
