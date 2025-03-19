from app.database import SessionLocal
from app.models import User
from app.auth_utils import get_password_hash
import sys


def fix_admin_user():
    with SessionLocal() as db:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@hospital.com").first()

        if admin:
            print(
                f"Admin user found: {admin.email}, ID: {admin.id}, Role: {admin.role}"
            )
            # Update password
            admin.hashed_password = get_password_hash("admin123")
            db.commit()
            print("Admin password updated")
        else:
            print("Admin user not found, creating...")
            # Create admin user
            new_admin = User(
                email="admin@hospital.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Hospital Administrator",
                role="general_manager",
                is_active=True,
            )
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            print(f"Created new admin: {new_admin.email}, ID: {new_admin.id}")


if __name__ == "__main__":
    fix_admin_user()
