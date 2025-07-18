from app.db.models import User


def build_profile_text(user: User) -> str:
    username_part = f'@{user.username}' if user.username else '—'
    return (
        'Твой профиль 🗒\n\n'
        f'*Имя:* {user.first_name}\n'
        f'*Фамилия:* {user.last_name}\n'
        f'*Офис:* {user.office.value}\n'
        f'*Пользовательское имя:* {username_part}\n'
        f'*Telegram-ID:* {user.tg_id}\n\n'
        f'*Количество встреч:* __{user.meetings_count}__'
    )