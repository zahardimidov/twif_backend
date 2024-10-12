from database.models import MemberStatusEnum, Party, PartyMember, User
from database.session import async_session
from sqlalchemy import func, select, desc


async def get_user(user_id) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))

        return user


async def set_user(user_id, **kwargs) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))

        if not user:
            user = User(id=user_id, **kwargs)
            session.add(user)
        else:
            for k, v in kwargs.items():
                setattr(user, k, v)

        await session.commit()
        await session.refresh(user)

        return user


async def create_party(creator_id, **party_data):
    async with async_session() as session:
        party = Party(**party_data)
        session.add(party)

        await session.commit()
        await session.refresh(party)

        await join_party(party_id=party.id, user_id=creator_id, status=MemberStatusEnum.creator)

        return party


async def join_party(party_id, user_id, status=MemberStatusEnum.member):
    async with async_session() as session:
        member = PartyMember(
            party_id=party_id, member_id=user_id, member_status=status)
        session.add(member)

        await session.commit()


async def vote_party(party_id, user_id):
    await join_party(party_id, user_id, status=MemberStatusEnum.voter)


async def get_user_vote(user_id):
    async with async_session() as session:
        vote = session.scalar(select(PartyMember).where(PartyMember.member_id == user_id, PartyMember.member_status == MemberStatusEnum.voter))

        return vote

async def get_leaderboard(limit=20, offset = 0):
    async with async_session() as session:
        leaders = await session.scalars(select(User).order_by(desc(User.points)).limit(limit).offset(offset))

        return list(leaders)


async def get_top_parties(limit=10, offset = 0):
    query = (
        select(Party)
        .join(PartyMember)
        .filter(PartyMember.member_status == MemberStatusEnum.voter)
        .group_by(Party.id)
        .order_by(func.count(PartyMember.member_id).desc())
        .limit(limit)
        .offset(offset)
    )

    async with async_session() as session:
        leaders = await session.execute(query)

        return leaders.scalars().all()


async def save_game_results():
    ...

