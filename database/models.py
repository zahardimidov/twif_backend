import enum
import uuid

from config import BASE_DIR, AVATARS_DIR
from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy import BigInteger, Enum, ForeignKey, Integer, String, Float, DateTime, Boolean, Date
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone

folder_for_logo = FileSystemStorage(
    path=BASE_DIR.joinpath('media').joinpath('logos'))
folder_for_message = FileSystemStorage(
    path=BASE_DIR.joinpath('media').joinpath('message'))
folder_for_avatar = FileSystemStorage(
    path=BASE_DIR.joinpath('media').joinpath('avatars'))


class MemberStatusEnum(enum.Enum):
    creator = 'creator'
    founder = 'founder'
    member = 'member'
    project = 'project'
    voter = 'voter'


def generate_uuid():
    return str(uuid.uuid4())


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = mapped_column(BigInteger, primary_key=True)  # Telegram User ID
    username = mapped_column(String(50), nullable=True)  # Telegram Username
    fullname = mapped_column(String, nullable=True, default='Guest')
    avatar = mapped_column(String)

    points = mapped_column(BigInteger, default=0)
    stars = mapped_column(Integer, default=0)
    last_attempt = mapped_column(DateTime, nullable=True)

    referrer_id = mapped_column(ForeignKey('users.id'), nullable=True)
    referrer: Mapped['User'] = relationship()

    def __repr__(self) -> str:
        return self.username if self.username else self.id

    def __init__(self, **kw):
        self.avatar = f'{kw["id"]}.png'
        super().__init__(**kw)

    @property
    def avatarURL(self):
        return AVATARS_DIR.joinpath(self.avatar)


class Party(Base):
    __tablename__ = 'parties'

    id = mapped_column(String, primary_key=True, default=generate_uuid)

    title = mapped_column(String)
    logo = mapped_column(FileType(storage=folder_for_logo))
    quantity = mapped_column(Integer)

    founder_share = mapped_column(Float)
    members_share = mapped_column(Float)
    project_share = mapped_column(Float)
    voters_share = mapped_column(Float)

    level = mapped_column(Integer, default=0)

    nft_requirement = mapped_column(String, nullable=True, default=None)
    twif_requirement = mapped_column(Integer, nullable=True, default=None)

    def generate_filename(self):
        return f'{self.id}.png'

    def __repr__(self) -> str:
        return self.title


class PartyMember(Base):
    __tablename__ = 'party_members'

    party_id = mapped_column(ForeignKey(
        'parties.id', ondelete='CASCADE'), primary_key=True)
    party: Mapped['Party'] = relationship()

    member_id = mapped_column(ForeignKey(
        'users.id', ondelete='CASCADE'), primary_key=True)
    member: Mapped['User'] = relationship()

    member_status = mapped_column(Enum(MemberStatusEnum))

    def __repr__(self) -> str:
        return str(self.member) + ' - ' + str(self.party)


class Wallet(Base):
    __tablename__ = 'wallets'

    id = mapped_column(String, primary_key=True, default=generate_uuid)
    address = mapped_column(String)

    user_id = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    user: Mapped['User'] = relationship()

    def __repr__(self) -> str:
        return str(self.user) + ' - ' + str(self.address)


class Transaction(Base):
    __tablename__ = 'transactions'

    boc = mapped_column(String, primary_key=True)

    wallet_id = mapped_column(ForeignKey('wallets.id', ondelete='CASCADE'))
    wallet: Mapped['Wallet'] = relationship()

    
class Message(Base):
    __tablename__ = 'messages'

    id = mapped_column(String, primary_key=True, default=generate_uuid)

    text = mapped_column(String)
    photo = mapped_column(FileType(storage=folder_for_message))

    buttons = relationship("Button", back_populates="message", cascade="all, delete-orphan", lazy='subquery')
    
    def generate_filename(self):
        return f'{self.id}.png'
    
class Button(Base):
    __tablename__ = 'buttons'

    id = mapped_column(String, primary_key=True, default=generate_uuid)
    label = mapped_column(String)
    url = mapped_column(String)  # URL или любое другое поле для кнопки

    message_id = mapped_column(ForeignKey('messages.id', ondelete='CASCADE'))
    message: Mapped['Message'] = relationship()

    def __repr__(self) -> str:
        return self.label
    
class DailyBoost(Base):
    __tablename__ = 'dailyboost'

    id = mapped_column(String, primary_key=True, default=generate_uuid)
    stars = mapped_column(Integer)
    multiplier = mapped_column(Float)
    nolimit = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        if self.nolimit:
            return f'{self.stars} - nolimit'
        return f'{self.stars} - {self.multiplier}'

class StarsOffer(Base):
    __tablename__ = 'store'

    id = mapped_column(String, primary_key=True, default=generate_uuid)
    amount = mapped_column(Integer)
    ton = mapped_column(Float)

    def __repr__(self) -> str:
        return f'{self.amount} - {self.ton}'


class UserDailyBoost(Base):
    __tablename__ = 'userdailyboost'

    id = mapped_column(String, primary_key=True, default=generate_uuid)

    boost_id = mapped_column(ForeignKey('dailyboost.id', ondelete='CASCADE'))
    boost: Mapped['DailyBoost'] = relationship(lazy='subquery')

    user_id = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    user: Mapped['User'] = relationship(lazy='subquery')

    date = mapped_column(Date, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f'{self.user} - {self.boost}'
    
class Task(Base):
    __tablename__ = 'tasks'

    id = mapped_column(String, primary_key=True, default=generate_uuid)

    text = mapped_column(String)
    url = mapped_column(String)

    reward = mapped_column(Integer)

    def __repr__(self) -> str:
        return self.text
    
class UserTaskCompleted(Base):
    __tablename__ = 'completed_task'

    id = mapped_column(String, primary_key=True, default=generate_uuid)

    task_id = mapped_column(ForeignKey('tasks.id', ondelete='CASCADE'))
    task: Mapped['Task'] = relationship(lazy='subquery')

    user_id = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    user: Mapped['User'] = relationship(lazy='subquery')

    def __repr__(self) -> str:
        return f'{self.user} - {self.task}'