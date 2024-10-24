from datetime import datetime, timezone
from typing import List, Tuple

from database.models import (DailyBoost, MemberStatusEnum, Message, Party,
                             PartyMember, StarsOffer, Task, Transaction, User,
                             UserDailyBoost, UserTaskCompleted, Wallet)
from database.session import async_session
from sqlalchemy import delete, desc, func, or_, select, update, and_, case


async def get_user(user_id) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))

        return user


async def get_users() -> List[User]:
    async with async_session() as session:
        users = await session.scalars(select(User))

        return users


async def get_users_ids() -> List[int]:
    async with async_session() as session:
        users = await session.scalars(select(User.id))

        return users


async def get_party(party_id) -> Party:
    async with async_session() as session:
        party = await session.scalar(select(Party).where(Party.id == party_id))

        return party


async def get_party_related_users(party_id, voter=True) -> List[User]:
    async with async_session() as session:
        status = [MemberStatusEnum.creator,
                  MemberStatusEnum.founder, MemberStatusEnum.member]

        if voter:
            status.append(MemberStatusEnum.voter)

        participants = await session.scalars(select(User).join(PartyMember).filter(PartyMember.party_id == party_id, PartyMember.member_status.in_(status)))

        return list(participants)


async def get_party_points(party_id) -> List[User]:
    async with async_session() as session:
        status = [MemberStatusEnum.creator, MemberStatusEnum.founder,
                  MemberStatusEnum.member, MemberStatusEnum.voter]

        result = await session.execute(
            select(
                Party,
                func.sum(case((User.voted_points != None, User.voted_points), else_=User.points)
                ).label('total_points')
            )
            .join(PartyMember, and_(Party.id == PartyMember.party_id, PartyMember.member_status.in_(status)))
            .join(User, PartyMember.member_id == User.id)
            .where(Party.id == party_id)
            .group_by(Party.id)
        )

        return result.one()


async def get_party_leaderboard(limit=10) -> List[Tuple[Party, int]]:
    async with async_session() as session:
        status = [MemberStatusEnum.creator, MemberStatusEnum.founder,
                  MemberStatusEnum.member, MemberStatusEnum.voter]

        result = await session.execute(
            select(
                Party,
                func.sum(case((User.voted_points != None, User.voted_points), else_=User.points)
                ).label('total_points')
            )
            .join(PartyMember, and_(Party.id == PartyMember.party_id, PartyMember.member_status.in_(status)))
            .join(User, PartyMember.member_id == User.id)
            .group_by(Party.id)
            .order_by(func.sum(case((User.voted_points != None, User.voted_points), else_=User.points)
            ).desc())
            .limit(limit)
        )

        '''result = await session.execute(
            select(
                Party,
                func.sum(User.points).label('total_points')
            )
            .join(PartyMember, and_(Party.id == PartyMember.party_id, PartyMember.member_status.in_(status)))
            .join(User, PartyMember.member_id == User.id)
            .group_by(Party.id)
            .order_by(func.sum(User.points).desc())
            .limit(limit)
        )'''

        leaderboard = result.all()  # Получаем все результаты
    return [(party,  total_points) for party, total_points in leaderboard]


async def search_users(query) -> List[User]:
    async with async_session() as session:
        users = await session.scalars(select(User).filter(or_(User.username.ilike(f'%{query}%'), User.fullname.ilike(f'%{query}%'))))

    return list(users)


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


async def create_party(**party_data):
    async with async_session() as session:
        logo = party_data.pop('logo')

        party = Party(**party_data)
        session.add(party)

        await session.commit()
        await session.refresh(party)

        logo.filename = party.generate_filename()
        await update_party(party.id, {'logo': logo})

        return party


async def update_party(party_id, data_dict):
    async with async_session() as session:
        await session.execute(update(Party).where(Party.id == party_id).values(**data_dict))
        await session.commit()


async def join_party(party_id, user_id, status=MemberStatusEnum.member):
    async with async_session() as session:
        member = PartyMember(
            party_id=party_id, member_id=user_id, member_status=status)
        session.add(member)

        await session.commit()


async def delete_invite(user_id, party_id):
    async with async_session() as session:
        await session.execute(delete(PartyMember).where(PartyMember.member_id == user_id, PartyMember.party_id == party_id))
        await session.commit()


async def vote_party(party_id, user_id):
    await join_party(party_id, user_id, status=MemberStatusEnum.voter)


async def get_user_vote(user_id):
    async with async_session() as session:
        vote = await session.scalar(select(PartyMember).where(
            PartyMember.member_id == user_id, PartyMember.member_status == MemberStatusEnum.voter))

        return vote


async def get_user_party(user_id):
    async with async_session() as session:
        party = await session.scalar(select(PartyMember).where(
            PartyMember.member_id == user_id, PartyMember.member_status != MemberStatusEnum.invited))

        return party


async def get_user_invites(user_id):
    async with async_session() as session:
        invites = await session.scalars(select(PartyMember).where(
            PartyMember.member_id == user_id, PartyMember.member_status == MemberStatusEnum.invited))

        return invites


async def get_party_member(party_id, user_id):
    async with async_session() as session:
        member: PartyMember = await session.scalar(select(PartyMember).where(PartyMember.member_id == user_id, Party.id == party_id, PartyMember.member_status.in_([
            MemberStatusEnum.creator, MemberStatusEnum.founder, MemberStatusEnum.member])))

        if member:
            return member.member_status


async def get_party_members(party_id):
    async with async_session() as session:
        members: PartyMember = await session.scalars(select(PartyMember).where(Party.id == party_id, PartyMember.member_status.in_([
            MemberStatusEnum.creator, MemberStatusEnum.founder, MemberStatusEnum.member])))

        return list(members)


async def get_leaderboard(limit=20, offset=0):
    async with async_session() as session:
        leaders = await session.scalars(select(User).order_by(desc(User.points)).limit(limit).offset(offset))

        return list(leaders)


async def get_top_parties(limit=10, offset=0):
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


async def get_user_wallet(user_id):
    async with async_session() as session:
        wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id))

        return wallet


async def get_daily_boost(boost_id) -> DailyBoost:
    async with async_session() as session:
        boost = await session.scalar(select(DailyBoost).where(DailyBoost.id == boost_id))

        return boost


async def get_user_daily_boost(user_id):
    async with async_session() as session:
        boost = await session.scalar(select(UserDailyBoost).where(UserDailyBoost.user_id == user_id, UserDailyBoost.date == datetime.now(timezone.utc).date()))

        return boost


async def get_daily_boosts() -> List[DailyBoost]:
    async with async_session() as session:
        boosts = await session.scalars(select(DailyBoost))

        return list(boosts)


async def set_user_daily_boost(boost_id, user_id) -> UserDailyBoost:
    async with async_session() as session:
        boost = UserDailyBoost(boost_id=boost_id, user_id=user_id)
        session.add(boost)
        await session.commit()
        await session.refresh(boost)

        return boost


async def get_transaction(boc):
    async with async_session() as session:
        transaction = await session.scalar(select(Transaction).where(Transaction.boc == boc))

        return transaction


async def get_stars_offers():
    async with async_session() as session:
        offer = await session.scalars(select(StarsOffer).order_by(desc(StarsOffer.amount)))

        return offer


async def get_stars_offer(offer_id):
    async with async_session() as session:
        offer = await session.scalar(select(StarsOffer).where(StarsOffer.id == offer_id))

        return offer


async def set_user_wallet(user_id, address):
    wallet = await get_user_wallet(user_id=user_id)

    async with async_session() as session:
        if wallet:
            await session.execute(update(Wallet).where(Wallet.user_id == user_id).values(address=address))
        else:
            wallet = Wallet(user_id=user_id, address=address)
            session.add(wallet)
        await session.commit()


async def delete_user_wallet(user_id):
    async with async_session() as session:
        await session.execute(delete(Wallet).where(Wallet.user_id == user_id))
        await session.commit()


async def get_message_by_id(message_id):
    async with async_session() as session:
        message = await session.scalar(select(Message).where(Message.id == message_id))

        return message


async def complete_task(user_id, task_id):
    async with async_session() as session:
        complete = UserTaskCompleted(task_id=task_id, user_id=user_id)

        session.add(complete)
        await session.commit()
        await session.refresh(complete)

    return complete.task


async def users_complete_tasks(user_id) -> List[UserTaskCompleted]:
    async with async_session() as session:
        tasks = await session.scalars(select(UserTaskCompleted).where(UserTaskCompleted.user_id == user_id))

        return list(tasks)


async def get_user_task(user_id, task_id) -> UserTaskCompleted:
    async with async_session() as session:
        task = await session.scalar(select(UserTaskCompleted).where(UserTaskCompleted.user_id == user_id, UserTaskCompleted.task_id == task_id))

        return task


async def get_tasks() -> List[Task]:
    async with async_session() as session:
        tasks = await session.scalars(select(Task))

        return list(tasks)


async def get_referres(user: User) -> List[User]:
    async with async_session() as session:
        referrer1 = await session.scalar(select(User).where(User.id == user.referrer_id))

        if not referrer1:
            return []

        referrer2 = await session.scalar(select(User).where(User.id == referrer1.referrer_id))

        if not referrer2:
            return [referrer1]

        referrer3 = await session.scalar(select(User).where(User.id == referrer2.referrer_id))

        if not referrer3:
            return [referrer1, referrer2]
        return [referrer1, referrer2, referrer3]


async def get_all_referals(user: User):
    async with async_session() as session:
        referrals = await session.scalars(select(User).where(User.referrer_id == user.id))

        return referrals
