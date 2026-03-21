from models.user import User
from models.article import Article
from db.database import engine, Base

def init_db():
    print("Creation des Tables dans la base de donnees...")
    Base.metadata.create_all(bind=engine)
    print("Table crees avec succes !")
    
if __name__ == "__main__":
    init_db()    