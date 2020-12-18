import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
admin_id = os.getenv("ADMIN_ID")
host = os.getenv("PGHOST")
db_user = os.getenv("PG_USER")
db_pass = os.getenv("PG_PASS")
redis_pass = os.getenv("REDIS_PASS")