from value import *
from db_connect import UserTgTable, session, engine
from back_for_yarik.bot_tg.bot_regist import *
from bot_delete import *
from bot_edit import *
from bot_show import *


def user_exists(user_id: int) -> bool:
    """Проверяет, существует ли пользователь с указанным ID."""
    query = UserTgTable.select().where(UserTgTable.c.userid == user_id)
    result = session.execute(query).fetchone()
    return result is not None