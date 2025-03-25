from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime,ForeignKey,BigInteger,Boolean, DATE ,select, Date
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from value import DATABASE_URL


# Подключение к SQLite через SQLAlchemy

engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData()
metadata.bind = engine

# Маппинг таблицы UserTg
UserTgTable = Table(
    'manageappfish_usertg',  # Имя таблицы, созданной Django
    metadata,
    Column('id', Integer, primary_key=True),
    Column('userid', BigInteger, nullable=False),
    Column('username', String, nullable=True),
    Column('first_name', String, nullable=True),
    Column('last_name', String, nullable=True),
    Column('phone_number', Integer, nullable=True),
    Column('metod_catch', String, nullable=True),
    Column('gear_main', String, nullable=True),
    Column('bio', String, nullable=True),
    Column('image', String, nullable=True),
    Column('alias', String, nullable=True),
    Column('birth_date', Date, nullable=True),
    Column('profile_create', Boolean, nullable=True, default=False),
    Column('profile_change', Boolean, nullable=True, default=False),
    Column('created_at', DateTime, default=datetime.utcnow),

    extend_existing=True
) 


CatchTgTable = Table(
    'manageappfish_cacthtg',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('image', String, nullable=True),
    Column('about', String, nullable=True),
    Column('weight', Integer, nullable=True),
    Column('bait', String, nullable=True),
    Column('location_name', String, nullable=True),
    Column('fish', String, nullable=True),
    Column('created_at', DateTime,default=datetime.utcnow,  nullable=False),
    Column('user_id', BigInteger, ForeignKey('manageappfish_usertg.id'),  nullable=False),
    Column('message_id', String,  nullable=False, default="0"),
    Column('image_hash', String, nullable=True),
    Column('post_add', Boolean, nullable=True, default=False),
    
    extend_existing=True
)

UserTable = Table(
    'auth_user',
    metadata,
    autoload_with=engine,
)


CatchTgImage = Table(
    'manageappfish_cacthtgimage',
    metadata,
    autoload_with=engine,
)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()



def get_user_id_by_userid(userid_value):
    # Создаем запрос: выбрать id, где userid = значение
    stmt = select(UserTgTable.c.id).where(UserTgTable.c.userid == userid_value)
    
    with engine.connect() as conn:
        result = conn.execute(stmt)
        user = result.scalar()  # Возвращает первое значение (id) или None

    return user
