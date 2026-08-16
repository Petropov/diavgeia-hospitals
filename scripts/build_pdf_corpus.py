#!/usr/bin/env python3
"""Build a searchable SQLite corpus of every PDF we hold: full text + extracted amounts.

Tables:
  docs(ada PRIMARY KEY, org, source, path, chars, max_amount, amounts_json)
  fts  (FTS5 over text, joined by rowid)

Usage: python3 scripts/build_pdf_corpus.py            (incremental: skips known ADAs)
Query examples:
  sqlite3 data/_registry/pdf_corpus.sqlite "SELECT ada,org,max_amount FROM docs ORDER BY max_amount DESC LIMIT 20"
  sqlite3 data/_registry/pdf_corpus.sqlite "SELECT d.ada,d.org FROM fts JOIN docs d ON d.rowid=fts.rowid WHERE fts MATCH 'ΠΡΟΑΙΡΕΣΗ' LIMIT 10"
"""
import glob, json, os, re, sqlite3, subprocess, sys

DB = os.environ.get('CORPUS_DB', 'data/_registry/pdf_corpus.sqlite')
DIRS = glob.glob('data/*/*_pdfs') + glob.glob('data/_registry/*_pdfs') + \
       glob.glob('data/*/reconciliation_pdfs') + glob.glob('data/*/award_pdfs')
CUR = re.compile(r'\d{1,3}(?:\.\d{3})+,\d{2}|\d{1,3}(?:,\d{3})+\.\d{2}')

def num(s):
    if re.search(r',\d{2}$', s): return float(s.replace('.', '').replace(',', '.'))
    return float(s.replace(',', ''))

con = sqlite3.connect(DB)
con.execute('CREATE TABLE IF NOT EXISTS docs(ada TEXT PRIMARY KEY, org TEXT, source TEXT, path TEXT, chars INT, max_amount REAL, amounts_json TEXT)')
con.execute('CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(text)')
known = {r[0] for r in con.execute('SELECT ada FROM docs')}

files = []
for d in set(DIRS):
    files += glob.glob(os.path.join(d, '*.pdf'))
added = skipped = failed = 0
for fp in sorted(set(files)):
    base = os.path.basename(fp)[:-4]
    ada = base.split('__')[-1]
    org = base.split('__')[0] if '__' in base else ''
    if ada in known: skipped += 1; continue
    try:
        t = subprocess.run(['pdftotext', '-layout', fp, '-'],
                           capture_output=True, text=True, timeout=60).stdout
    except Exception:
        failed += 1; continue
    amts = sorted({num(m) for m in CUR.findall(t)}, reverse=True)[:30]
    cur = con.execute('INSERT OR REPLACE INTO docs VALUES(?,?,?,?,?,?,?)',
                      (ada, org, os.path.basename(os.path.dirname(fp)), fp,
                       len(t), amts[0] if amts else 0, json.dumps(amts)))
    con.execute('INSERT INTO fts(rowid,text) VALUES(?,?)', (cur.lastrowid, t))
    known.add(ada); added += 1
con.commit()
n, = con.execute('SELECT COUNT(*) FROM docs').fetchone()
print(f"corpus: {n} docs total (+{added} new, {skipped} known, {failed} failed) -> {DB}")
