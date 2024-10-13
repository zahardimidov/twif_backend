import enum
import uuid

from config import BASE_DIR, AVATARS_DIR
from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy import BigInteger, Enum, ForeignKey, Integer, String, Float
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

folder_for_logo = FileSystemStorage(
    path=BASE_DIR.joinpath('media').joinpath('logos'))
folder_for_nft = FileSystemStorage(
    path=BASE_DIR.joinpath('media').joinpath('nft'))
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

    nft_requirement = mapped_column(String, nullable=True, default=None)
    twif_requirement = mapped_column(Integer, nullable=True, default=None)

    def __repr__(self) -> str:
        return self.title

class PartyMember(Base):
    __tablename__ = 'party_members'

    party_id = mapped_column(ForeignKey('parties.id'), primary_key=True)
    party: Mapped['Party'] = relationship()

    member_id = mapped_column(ForeignKey('users.id'), primary_key=True)
    member: Mapped['User'] = relationship()

    member_status = mapped_column(Enum(MemberStatusEnum))

    def __repr__(self) -> str:
        return str(self.member) + ' - ' + str(self.party)



class Wallet(Base):
    __tablename__ = 'wallets'

    address = mapped_column(String, primary_key=True)

    user_id = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship()

    def __repr__(self) -> str:
        return str(self.user) + ' - ' + str(self.address)

