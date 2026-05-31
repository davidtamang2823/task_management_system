ALL_PERMISSIONS = (
    ("can_view_all_users", "Can view all users"),
    ("can_view_all_tasks", "Can view all tasks"),
    ("can_create_tasks", "Can create tasks"),
    ("can_assign_task_to_any_user", "Can assign task to any user"),
    ("can_assign_task_to_user", "Can assign task to user"),  
    ("can_update_any_task", "Can update any task"),
    ("can_delete_any_task", "Can delete any task"),
    ("can_update_task_status", "Can update task status"),
    ("can_create_roles", "Can create roles"),
    ("can_view_roles", "Can view roles"),
    ("can_update_roles", "Can update roles"),
    ("can_delete_roles", "Can delete roles"),
    ("can_view_tasks", "Can view tasks"),
    ("can_view_user", "Can view user"),
    ("can_update_task", "Can update task"),
    ("can_delete_task", "Can delete task"),
)

ADMIN_PERMISSIONS = (
    ("can_view_all_users", "Can view all users"),
    ("can_view_all_tasks", "Can view all tasks"),
    ("can_create_tasks", "Can create tasks"),
    ("can_assign_task_to_any_user", "Can assign task to any user"),
    ("can_update_any_task", "Can update any task"),
    ("can_delete_any_task", "Can delete any task"),
    ("can_update_task_status", "Can update task status"),
    ("can_create_roles", "Can create roles"),
    ("can_view_roles", "Can view roles"),
    ("can_update_roles", "Can update roles"),
    ("can_delete_roles", "Can delete roles")
)

MANAGER_PERMISSIONS = (
    ("can_view_tasks", "Can view tasks"),
    ("can_view_user", "Can view user"),
    ("can_assign_task_to_user", "Can assign task to user"),
    ("can_create_tasks", "Can create tasks"),
    ("can_update_task", "Can update task"),
    ("can_delete_task", "Can delete task"),
    ("can_update_task_status", "Can update task status")
)

USER_PERMISSIONS = (
    ("can_view_tasks", "Can view tasks"),
    ("can_update_task_status", "Can update task status")
)

ROLES = (
    "ADMIN",
    "MANAGER",
    "USER"
)