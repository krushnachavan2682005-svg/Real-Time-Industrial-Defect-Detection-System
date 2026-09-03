import sys
from pathlib import Path
import yaml

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.persistence.database import db
from src.persistence.repositories.user_repository import SQLAlchemyUserRepository
from src.auth.service import AuthService
from src.auth.models import Role
from src.auth.security import hash_password

def main():
    # Load config
    with open("configs/persistence/database.yaml", "r") as f:
        db_config = yaml.safe_load(f)
        
    db_url = db_config.get("database", {}).get("url")
    db.initialize(db_url)
    
    user_repo = SQLAlchemyUserRepository(db.get_session)
    auth_service = AuthService(user_repo)
    
    username = "testadmin"
    password = "TestAdmin@123"
    
    existing = user_repo.get_by_username(username)
    if existing:
        print(f"User {username} already exists, attempting to reset password.")
        session = db.get_session()
        # Have to fetch it from session to update
        from src.persistence.models.user_model import UserModel
        user = session.query(UserModel).filter(UserModel.username == username).first()
        user.password_hash = hash_password(password)
        session.commit()
        print("Password reset successfully.")
    else:
        auth_service.create_user(username, password, Role.ADMIN)
        print(f"User {username} created successfully.")
        
if __name__ == "__main__":
    main()
