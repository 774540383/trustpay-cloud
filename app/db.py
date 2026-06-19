import sqlite3, secrets, string, os
from datetime import datetime
from .config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
 telegram_id INTEGER PRIMARY KEY,
 username TEXT,
 full_name TEXT,
 is_active INTEGER DEFAULT 0,
 level TEXT DEFAULT 'عادي',
 balance_usdt REAL DEFAULT 0,
 created_at TEXT
);
CREATE TABLE IF NOT EXISTS kyc_requests(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 request_no TEXT UNIQUE,
 telegram_id INTEGER,
 full_name TEXT,
 phone TEXT,
 address TEXT,
 purpose TEXT,
 details TEXT,
 id_image TEXT,
 selfie_image TEXT,
 status TEXT DEFAULT 'قيد المراجعة',
 reject_reason TEXT,
 created_at TEXT,
 reviewed_at TEXT
);
CREATE TABLE IF NOT EXISTS operations(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 telegram_id INTEGER,
 op_type TEXT,
 amount REAL,
 network TEXT,
 wallet TEXT,
 proof TEXT,
 status TEXT DEFAULT 'قيد المراجعة',
 created_at TEXT
);
CREATE TABLE IF NOT EXISTS tickets(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 telegram_id INTEGER,
 message TEXT,
 status TEXT DEFAULT 'مفتوحة',
 created_at TEXT
);
CREATE TABLE IF NOT EXISTS audit_logs(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 actor TEXT,
 action TEXT,
 target TEXT,
 created_at TEXT
);
"""

def conn():
    os.makedirs(os.path.dirname(settings.database_path), exist_ok=True)
    c=sqlite3.connect(settings.database_path)
    c.row_factory=sqlite3.Row
    return c

def init_db():
    with conn() as c:
        c.executescript(SCHEMA)

def now(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def ensure_user(tid:int, username='', full_name=''):
    with conn() as c:
        c.execute("INSERT OR IGNORE INTO users(telegram_id,username,full_name,created_at) VALUES(?,?,?,?)",(tid,username,full_name,now()))
        c.execute("UPDATE users SET username=?, full_name=? WHERE telegram_id=?",(username,full_name,tid))

def user(tid:int):
    with conn() as c:
        return c.execute("SELECT * FROM users WHERE telegram_id=?",(tid,)).fetchone()

def rand_no(prefix='KYC'):
    code=''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(8))
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{code}"

def active_kyc(tid:int):
    with conn() as c:
        return c.execute("SELECT * FROM kyc_requests WHERE telegram_id=? AND status IN ('قيد المراجعة','مقبول') ORDER BY id DESC LIMIT 1",(tid,)).fetchone()

def create_kyc(data:dict):
    no=rand_no('KYC')
    with conn() as c:
        c.execute("""INSERT INTO kyc_requests(request_no,telegram_id,full_name,phone,address,purpose,details,id_image,selfie_image,created_at)
        VALUES(?,?,?,?,?,?,?,?,?,?)""",(no,data['telegram_id'],data['full_name'],data['phone'],data['address'],data['purpose'],data.get('details',''),data['id_image'],data['selfie_image'],now()))
    return no

def list_kyc(status=None):
    with conn() as c:
        if status:
            return c.execute("SELECT * FROM kyc_requests WHERE status=? ORDER BY id DESC",(status,)).fetchall()
        return c.execute("SELECT * FROM kyc_requests ORDER BY id DESC LIMIT 200").fetchall()

def get_kyc(rid:int):
    with conn() as c: return c.execute("SELECT * FROM kyc_requests WHERE id=?",(rid,)).fetchone()

def review_kyc(rid:int, status:str, reason='', actor='admin'):
    with conn() as c:
        req=c.execute("SELECT * FROM kyc_requests WHERE id=?",(rid,)).fetchone()
        if not req: return None
        c.execute("UPDATE kyc_requests SET status=?, reject_reason=?, reviewed_at=? WHERE id=?",(status,reason,now(),rid))
        if status=='مقبول':
            c.execute("UPDATE users SET is_active=1 WHERE telegram_id=?",(req['telegram_id'],))
        c.execute("INSERT INTO audit_logs(actor,action,target,created_at) VALUES(?,?,?,?)",(actor,status,req['request_no'],now()))
        return req

def create_operation(tid:int, op_type:str, amount:float, network='', wallet='', proof=''):
    with conn() as c:
        c.execute("INSERT INTO operations(telegram_id,op_type,amount,network,wallet,proof,created_at) VALUES(?,?,?,?,?,?,?)",(tid,op_type,amount,network,wallet,proof,now()))

def list_ops():
    with conn() as c: return c.execute("SELECT * FROM operations ORDER BY id DESC LIMIT 200").fetchall()

def add_ticket(tid:int, msg:str):
    with conn() as c: c.execute("INSERT INTO tickets(telegram_id,message,created_at) VALUES(?,?,?)",(tid,msg,now()))
