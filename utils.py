from storage import read_data

def is_admin(user_id: int) -> bool:
    data = read_data()
    return user_id in data.get('admins', [])
