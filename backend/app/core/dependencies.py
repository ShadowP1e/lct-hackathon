from typing import Annotated

from fastapi import Depends, Request

from core.exceptions import AuthError
from core.security import JWTBearer
from models import User
from services.jwt import JWTService
from services.user import UserService
from utils.time import timestamp_to_utc
from utils.unitofwork import IUnitOfWork, UnitOfWork

UOW = Annotated[IUnitOfWork, Depends(UnitOfWork)]


def get_user_ip(request: Request) -> str:
    return request.client.host


current_user_ip = Annotated[str, Depends(get_user_ip)]


async def get_current_user(
        uow: UOW,
        token: str = Depends(JWTBearer())
) -> User:
    if not token:
        raise AuthError(detail='Invalid authorization token.')

    token_data = JWTService().get_token_data(token)

    if not token_data or token_data.get('type') != 'access':
        raise AuthError(detail='Invalid authorization token.')

    user: User = await UserService().get(uow, id=token_data.get('sub'))

    if not user:
        raise AuthError(detail='Invalid authorization token.')

    if user.password_updated_at.replace(microsecond=0) > timestamp_to_utc(token_data['iat']):
        raise AuthError(detail='Invalid authorization token.')

    return user


current_user_or_error = Annotated[User, Depends(get_current_user)]
