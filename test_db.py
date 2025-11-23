import os
from dotenv import load_dotenv
load_dotenv()

print("DATABASE_URL:", os.getenv('DATABASE_URL'))

from services.core.database.service import DatabaseService
from services.core.database.models import Cultura

db = DatabaseService()
with db.get_session() as session:
    culturas = session.query(Cultura).all()
    print(f"Total culturas: {len(culturas)}")
    for c in culturas:
        print(f"  - {c.nome_cultura}")
