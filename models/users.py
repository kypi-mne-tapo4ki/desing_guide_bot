from beanie import Document


class User(Document):
    user_id: int
    discount: int = 0
    utp: str | None = None
    pain: str | None = None

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "discount": self.discount,
            "utp": self.utp,
            "pain": self.pain
        }


async def increment_discount(user_id: int):
    user = await get_user_data(user_id=user_id)

    if user:
        discount = user.to_dict().get("discount", 0) + 10
        setattr(user, "discount", discount)

        await user.save()


async def get_user_data(user_id: int):
    user = await User.find_one({"user_id": user_id})
    return user


async def update_user_data(user_id: int, **kwargs):
    user = await get_user_data(user_id=user_id)

    if user:
        for key, value in kwargs.items():
            setattr(user, key, value)

        await user.save()


async def clear_user_data(user_id: int):
    await update_user_data(user_id=user_id, discount=0, utp=None, pain=None)