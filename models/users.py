from beanie import Document


class User(Document):
    user_id: int
    username: str
    discount: int = 0
    utp: str | None = None
    pain: str | None = None
    lvl_2_ans: dict = {}
    lvl_3_ans: dict = {}


async def increment_discount(user_id: int) -> None:
    user = await get_user_data(user_id=user_id)

    if user:
        discount = user.discount + 10
        setattr(user, "discount", discount)

        await user.save()


async def get_user_data(user_id: int) -> User | None:
    user = await User.find_one({"user_id": user_id})
    return user


async def update_user_data(user_id: int, **kwargs) -> None:
    user = await get_user_data(user_id=user_id)

    if user:
        for key, value in kwargs.items():
            setattr(user, key, value)

        await user.save()


async def clear_user_data(user_id: int, username: str) -> None:
    await update_user_data(
        user_id=user_id, username=username, discount=0, utp=None, pain=None
    )
