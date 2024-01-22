from datetime import datetime

from beanie import Document
from beanie.odm.enums import SortDirection


class User(Document):
    user_id: int
    discount: int = 0
    username: str | None = None
    utp: str | None = None
    pain: str | None = None
    lvl_2_ans: dict = {}
    lvl_3_ans: dict = {}
    defer_discount: bool = False
    date: datetime | None = None

    def to_dict(self):
        return {
            "User ID": self.user_id,
            "Username": f"@{self.username}",
            "Discount": self.discount,
            "UTP": self.utp,
            "Pain": self.pain,
            "Defer discount": self.defer_discount,
            "Date": self.date.strftime("%d.%m.%Y")
        }


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
        user_id=user_id, username=username, discount=0, utp=None, pain=None, defer_discount=False
    )


async def get_users(
        fields: dict | None = None,
        limit: int = 0,
        skip: int = 0,
        sort: str | None = "date"
) -> list[User] | None:
    aggregator: list[dict] = []
    match: dict = {}

    if fields:
        match.update(fields)
    if len(match) > 0:
        aggregator.append({"$match": match})
    if limit:
        aggregator.append({"$limit": limit})
    if skip:
        aggregator.append({"$skip": skip})
    if sort:
        aggregator.append({"$sort": {sort: SortDirection.DESCENDING}})

    query = User.aggregate(aggregator)
    users_data = await query.to_list()

    return [User(**user) for user in users_data] if users_data else None
