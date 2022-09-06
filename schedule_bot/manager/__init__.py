from functools import wraps
from typing import Any, Callable

from sqlalchemy.exc import SQLAlchemyError

from schedule_bot import Session as SessionCreator


def orm_function(func: Callable[..., Any]):  # type: ignore
    @wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore
        if kwargs.get('session') is None:
            with SessionCreator() as session:
                try:
                    return func(*args, session=session, **kwargs)
                except SQLAlchemyError:
                    session.rollback()
        return func(*args, **kwargs)

    return wrapper
