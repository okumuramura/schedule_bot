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
def logout_user(uid: int, session: Session = None) -> None:
    session.query(db.ActiveUser).filter(db.ActiveUser.tid == uid).update(
        {"group_id": None, "state": 0}
    )
    session.commit()


@orm_function
def login_user(
    uid: int,
    group,
    state: int = 1,
    session: Session = None,
) -> None:
    group = session.query(db.Group).filter(db.Group.group == group).first()
    session.query(db.ActiveUser).filter(db.ActiveUser.tid == uid).update(
        {"group_id": group.id, "state": state}
    )
    session.commit()


@orm_function
def get_user_state(uid: int, session: Session = None) -> int:
    return (
        session.query(db.ActiveUser.state)
        .filter(db.ActiveUser.tid == uid)
        .first()[0]
    )


@orm_function
def set_user_state(
    uid: int, state: int, commit: bool = True, session: Session = None
) -> None:
    session.query(db.ActiveUser).filter(db.ActiveUser.tid == uid).update(
        {"state": state}
    )
    if commit:
        session.commit()
