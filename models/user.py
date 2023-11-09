from pydantic import BaseModel
from bot import collection


class User(BaseModel):
    user_id: int
    discount: int = 0
    utp: str
    pain: str

    async def save_user_data(self, user_id, discount, user_answer):
        data = {"user_id": user_id, "discount": discount, "user_answer": user_answer}
        collection.update_one({"user_id": user_id}, {"$set": data}, upsert=True)

    async def get_user_data(self, user_id):
        user_data = collection.find_one({"user_id": user_id})
        if user_data:
            discount = user_data.get("discount", 0)
            user_answer = user_data.get("user_answer", "")
            return {"discount": discount, "user_answer": user_answer, "user_id": user_id}
        else:
            return {"discount": 0, "user_answer": "", "user_id": user_id}

    async def update_user_discount(self, user_id):
        user_data = await self.get_user_data(user_id)
        user_data["discount"] = user_data.get("discount", 0) + 10
        await self.save_user_data(**user_data)