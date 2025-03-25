from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime,ForeignKey,BigInteger,Boolean,Float ,DATE ,select, Date,Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
from sqlalchemy.sql import func
from value import DATABASE_URL,DATABASE_URL_ASYNC


# Подключение к SQLite через SQLAlchemy

engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData()
metadata.bind = engine
engine_async = create_async_engine(DATABASE_URL_ASYNC, echo=True)
async_session = sessionmaker(
    engine_async,
    expire_on_commit=False,
    class_=AsyncSession
)




# Маппинг таблицы UserTg
UserTgTable = Table(
    'manageappfish_usertg',  # Имя таблицы, созданной Django
    metadata,
    Column('id', Integer, primary_key=True),
    Column('userid', BigInteger, nullable=False),
    Column('username', String, nullable=True),
    Column('first_name', String, nullable=True),
    Column('last_name', String, nullable=True),
    Column('phone_number', BigInteger, nullable=True),
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



#---------------------------------------ORM---------------------------------------


Base = declarative_base()

class UserTg(Base):
    __tablename__ = "manageappfish_usertg"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(BigInteger, unique=True, nullable=False, comment="id пользователя в телеграмм")
    username = Column(String(100), nullable=True, comment="username в TG")
    first_name = Column(String(100), nullable=True, comment="имя в TG")
    last_name = Column(String(100), nullable=True, comment="фамилия в TG")
    phone_number = Column(BigInteger, unique=True, nullable=True, comment="номер телефона в телеграмм")
    image = Column(String, nullable=True, comment="Аватар (путь к файлу)")
    metod_catch = Column(String(100), nullable=True, comment="основной метод ловли")
    gear_main = Column(String(100), nullable=True, comment="основная снасть")
    bio = Column(String(100), nullable=True, comment="о себе")
    alias = Column(String(100), nullable=True, comment="Кличка")
    birth_date = Column(DateTime, nullable=True, comment="Дата рождения")
    profile_create = Column(Boolean, default=False, nullable=True, comment="Создан ли профиль")
    profile_change = Column(Boolean, default=False, nullable=True, comment="Изменен ли профиль")
    created_at = Column(DateTime, server_default=func.now(), comment="Дата создания")

    catches = relationship("CacthTg", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserTg(first_name={self.first_name}, last_name={self.last_name}, userid={self.userid}, username={self.username})>"


class CacthTg(Base):
    __tablename__ = "manageappfish_cacthtg"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user_tg.id", ondelete="CASCADE"), nullable=False)
    about = Column(Text, nullable=True, comment="Описание")
    weight = Column(Integer, nullable=True, comment="Вес")
    bait = Column(Text, nullable=True, comment="Приманка")
    created_at = Column(DateTime, server_default=func.now(), comment="Дата создания")
    location_name = Column(String(200), nullable=True, comment="Локация")
    fish = Column(String(100), nullable=True, comment="Рыба")
    post_add = Column(Boolean, default=False, nullable=True, comment="Добавлен улов в основную базу")
    message_id = Column(Text, nullable=False, default="0", comment="id сообщения пользователя в канале")

    user = relationship("UserTg", back_populates="catches")
    images = relationship("CacthTgImage", back_populates="cacthtg", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CacthTg(user_id={self.user_id}, fish={self.fish}, weight={self.weight})>"


class CacthTgImage(Base):
    __tablename__ = "manageappfish_cacthtgimage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cacthtg_id = Column(Integer, ForeignKey("catch_tg.id", ondelete="CASCADE"), nullable=False)
    image = Column(String, nullable=True, comment="Путь к изображению")
    image_hash = Column(String(164), index=True, nullable=True, comment="Хеш изображения")

    cacthtg = relationship("CacthTg", back_populates="images")

    def __repr__(self):
        return f"<CacthTgImage(cacthtg_id={self.cacthtg_id}, image={self.image})>"


# Пользователь.
# Обрати внимание: здесь определена только базовая модель User,
# поскольку исходная модель Django не приведена.
class User(Base):
    __tablename__ = "auth_user"  # используем таблицу, существующую в Django

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(150), unique=True, nullable=False)
    first_name = Column(String(30))
    last_name = Column(String(150))
    email = Column(String(254))
    # Можно добавить и другие поля, если они нужны

    # Связи: например, у пользователя может быть много уловов (Catch)
    fishman_catch = relationship("Catch", back_populates="user", cascade="all, delete-orphan")
    # Связь один-к-одному с Profile
    profile = relationship("Profile", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

# Вид рыбы.
class Fish(Base):
    __tablename__ = "appfish_fish"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), unique=True, nullable=False, comment="Название")
    baitfish = Column(Float, default=1, comment="Порог для живца")
    threshold_small = Column(Float, comment="Порог для маленькой рыбы")
    threshold_medium = Column(Float, comment="Порог для средней рыбы")
    threshold_big = Column(Float, comment="Порог для большой рыбы")
    threshold_trophy = Column(Float, comment="Порог для трофейной рыбы")
    point = Column(Integer, default=0, nullable=False)
    description = Column(Text, nullable=True)
    
    # Обратная связь с уловами
    fish_catch = relationship("Catch", back_populates="fish_species")
    
    def __repr__(self):
        return f"<Fish(name={self.name})>"

# Место (локация).
class Place(Base):
    __tablename__ = "appfish_place"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    location_name = Column(String(100), nullable=False)
    location_geo = Column(String(100), nullable=True)
    about = Column(Text, nullable=True)
    
    # Связь с уловами, где используется эта локация
    catches = relationship("Catch", back_populates="location")
    
    def __repr__(self):
        return f"<Place(location_name={self.location_name})>"

# Модель для изображений, ранее описанная как CacthTgImage.
class CacthTgImage(Base):
    __tablename__ = "appfish_catchtgimage"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(String, nullable=True, comment="Путь к изображению")
    image_hash = Column(String(164), index=True, nullable=True, comment="Хеш изображения")
    
    # Обратная связь: изображение используется в улове (основное фото)
    fish_image_catch = relationship("Catch", back_populates="image_ref")
    
    def __repr__(self):
        return f"<CacthTgImage(id={self.id})>"

# Улов.
class Catch(Base):
    __tablename__ = "appfish_catch"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    fish_species_id = Column(Integer, ForeignKey("fish.id", ondelete="CASCADE"), nullable=False)
    location_name_id = Column(Integer, ForeignKey("place.id", ondelete="SET NULL"), nullable=True)
    image_id = Column(Integer, ForeignKey("catch_tg_image.id", ondelete="CASCADE"), nullable=True)
    bait = Column(Text, nullable=True)
    weight = Column(Integer, nullable=False)
    length = Column(Integer, nullable=True)
    size = Column(String(20), nullable=True, comment="Размер")
    about = Column(Text, nullable=True)
    date_catch = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), comment="Дата создания")
    
    user = relationship("User", back_populates="fishman_catch")
    fish_species = relationship("Fish", back_populates="fish_catch")
    location = relationship("Place", back_populates="catches")
    image_ref = relationship("CacthTgImage", back_populates="fish_image_catch")
    
    def __repr__(self):
        return f"<Catch(user_id={self.user_id}, fish_species_id={self.fish_species_id}, weight={self.weight})>"

# Снаряжение.
class Gear(Base):
    __tablename__ = "appfish_gear"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    
    # Обратная связь: профиль с основной снастью
    profiles = relationship("Profile", back_populates="gear_main")
    
    def __repr__(self):
        return f"<Gear(name={self.name})>"

# Метод ловли.
class Method(Base):
    __tablename__ = "appfish_method"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    
    # Обратная связь: профиль с основным методом ловли
    profiles = relationship("Profile", back_populates="metod_catch")
    
    def __repr__(self):
        return f"<Method(name={self.name})>"

# Профиль.
class Profile(Base):
    __tablename__ = "appfish_profile"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    gear_main_id = Column(Integer, ForeignKey("gear.id", ondelete="SET NULL"), nullable=True)
    metod_catch_id = Column(Integer, ForeignKey("method.id", ondelete="SET NULL"), nullable=True)
    bio = Column(Text, nullable=True, comment="Биография")
    alias = Column(Text, nullable=True, comment="Псевдоним")
    avatar = Column(String, nullable=True, comment="Путь к аватару")
    birth_date = Column(Date, nullable=True, comment="Дата рождения")
    created_at = Column(DateTime, server_default=func.now(), comment="Дата создания")
    slug = Column(String, unique=True, nullable=True, comment="URL Slug")
    
    user = relationship("User", back_populates="profile")
    gear_main = relationship("Gear", back_populates="profiles")
    metod_catch = relationship("Method", back_populates="profiles")
    
    def __repr__(self):
        return f"<Profile(user_id={self.user_id}, slug={self.slug})>"








#---------------------------------------------------------------------------------






def get_user_id_by_userid(userid_value):
    # Создаем запрос: выбрать id, где userid = значение
    stmt = select(UserTgTable.c.id).where(UserTgTable.c.userid == userid_value)
    
    with engine.connect() as conn:
        result = conn.execute(stmt)
        user = result.scalar()  # Возвращает первое значение (id) или None

    return user
