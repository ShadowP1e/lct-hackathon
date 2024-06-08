from utils.unitofwork import UnitOfWork
from services.user import UserService
from schemas.user import UserRegisterRequest


async def create_default_user(email: str, password: str) -> None:
    uow = UnitOfWork()
    async with uow:
        user = await UserService().get(uow, email=email)
        if user is None:
            schema = UserRegisterRequest(
                email=email,
                password=password,
            )
            await UserService().create(uow, schema)
        else:
            print('User already exist')
