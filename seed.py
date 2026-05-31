import asyncio
import logging
from sqlalchemy import select, insert
from app import (
    AsyncSessionLocal, 
    Role, 
    Permission, 
    RolePermission, 
    User, 
    role_permission_constants,
    hash_password,
    settings
)


async def seed():
    async with AsyncSessionLocal() as db:
        try:
            is_permission_seeded = True
            is_role_seeded = True
            print("Entering")
            result = await db.execute(select(Permission).limit(1))
            print("Outside")
            if not result.scalar_one_or_none(): 
                logging.info("Permission table is empty. Seeding data...")
                permissions = [Permission(name=name, display_name=display_name) for name, display_name in role_permission_constants.ALL_PERMISSIONS ]
                db.add_all(permissions)
                await db.flush()
                logging.info("Permission table seeded successfully.")
            else:
                logging.info("Permission table already has data. Skipping seeding.")
                is_permission_seeded = False

            result = await db.execute(select(Role).limit(1))
            if not result.scalar_one_or_none():
                logging.info("Role table is empty. Seeding data...")
                roles = [Role(name=name) for name in role_permission_constants.ROLES]
                db.add_all(roles)
                await db.flush()
                logging.info("Role table seeded successfully.")
            else:
                logging.info("Role table already has data. Skipping seeding.")
                is_role_seeded = False


            if is_permission_seeded and is_role_seeded:
                logging.info("Assigning permissions to roles...")
                permissions = await db.execute(select(Permission))
                permissions = permissions.scalars().all()
                permissions_map = {permission.name: permission for permission in permissions}
                logging.info(f"Permissions map: {permissions_map}")

                roles = await db.execute(select(Role))
                roles = roles.scalars().all()
                roles_map = {role.name: role for role in roles}
                logging.info(f"Roles map: {roles_map}")
                role_permissions_data = [
                    {'role_id': roles_map["ADMIN"].id, 'permission_id': permissions_map[permission_name].id}
                    for permission_name, _ in role_permission_constants.ADMIN_PERMISSIONS
                ] + [
                    {'role_id': roles_map["MANAGER"].id, 'permission_id': permissions_map[permission_name].id}
                    for permission_name, _ in role_permission_constants.MANAGER_PERMISSIONS
                ] + [
                    {'role_id': roles_map["USER"].id, 'permission_id': permissions_map[permission_name].id}
                    for permission_name, _ in role_permission_constants.USER_PERMISSIONS
                ]
                await db.execute(insert(RolePermission), role_permissions_data)
                await db.flush()
                logging.info("Permissions assigned to roles successfully.")
        
            result = await db.execute(select(User).where(User.email=="info@admin.com").limit(1))
            result = result.scalar_one_or_none()
            if not result:
                logging.info("Admin user does not exist. Seeding data...")
                admin_user = User(
                    email=settings.admin_email,
                    password=hash_password(settings.admin_password),
                    first_name="Admin",
                    last_name="User",
                    is_active=True,
                    role_id=roles_map["ADMIN"].id
                )
                db.add(admin_user)
                await db.flush()
                logging.info("Admin user seeded successfully.")

                manager = User(
                    email="manager@example.com",
                    password=hash_password("manager123"),
                    first_name="John",
                    last_name="Smith",
                    is_active=True,
                    role_id=roles_map["MANAGER"].id,
                )
                db.add(manager)
                await db.flush()  # gets manager.id
                logging.info("Manager user seeded successfully.")

                users = [
                    User(
                        email="user1@example.com",
                        password=hash_password("user123"),
                        first_name="Alice",
                        last_name="Johnson",
                        is_active=True,
                        role_id=roles_map["USER"].id,
                        manager_id=manager.id,  # reports to manager
                    ),
                    User(
                        email="user2@example.com",
                        password=hash_password("user123"),
                        first_name="Bob",
                        last_name="Williams",
                        is_active=True,
                        role_id=roles_map["USER"].id,
                        manager_id=manager.id,  # reports to manager
                    ),
                ]
                db.add_all(users)
                await db.flush()
                logging.info("Regular users seeded successfully.")

            else:
                logging.info("Admin user already exists. Skipping seeding.")
            
            await db.commit()

        except Exception as e:
            logging.exception(f"Error seeding data: {e}")
            await db.rollback()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed())