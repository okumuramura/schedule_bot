from typing import List

from sqlalchemy.orm import Session

from schedule_bot import db
from schedule_bot.manager import orm_function


@orm_function
def get_all_users(session: Session = None) -> List[db.ActiveUser]:
    return session.query(db.ActiveUser).all()


@orm_function
def get_all_vip_users(session: Session = None) -> List[db.ActiveUser]:
    return (
        session.query(db.ActiveUser).filter(db.ActiveUser.vip.is_(True)).all()
    )


@orm_function
def get_users_in_groups(
    groups: List[str], session: Session = None
) -> List[db.ActiveUser]:
    return (
        session.query(db.ActiveUser)
        .join(db.Group)
        .filter(db.Group.group.in_(groups))
        .all()
    )


@orm_function
def get_user(tid: int, session: Session = None):
    return (
        session.query(db.ActiveUser, db.Group)
        .filter(db.ActiveUser.tid == tid)
        .outerjoin(db.Group, db.Group.id == db.ActiveUser.group_id)
        .first()
    )


@orm_function
def add_user(uid: int, session: Session = None) -> None:
    user = db.ActiveUser(uid)
    session.add(user)
    session.commit()


@orm_function
def drop_user_group(uid: int, session: Session = None) -> None:
    session.query(db.ActiveUser).filter(db.ActiveUser.tid == uid).update(
        {"group_id": None}
    )
    session.commit()
