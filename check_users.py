from app.database import SessionLocal
from app.models import User


def list_all_users():
    with SessionLocal() as db:
        users = db.query(User).all()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Role: {user.role}")


if __name__ == "__main__":
    list_all_users()
