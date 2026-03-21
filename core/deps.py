import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.security import SECRET_KEY, ALGORITHM
from db.database import get_db
from models.user_model import User 

# Indique à FastAPI (et Swagger) où envoyer le formulaire de connexion
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Cette fonction est appelée à chaque fois qu'une route est protégée.
    Elle lit le token, vérifie sa validité, et retourne l'utilisateur.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # On décode le token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") # "sub" (subject) contient généralement l'username ou l'ID
        if username is None:
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Le token a expiré")
    except jwt.InvalidTokenError:
        raise credentials_exception
        
    # On cherche l'utilisateur dans la base de données
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
        
    return user