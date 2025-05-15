import asyncio
from mistralai import Mistral
import os
from config import AI_TOKEN


async def generate(content):
    s = Mistral(
        api_key='WqcQrPqcYoAHuVgeVDZLIF3X7c8NkV0L',
    )
    res = await s.chat.complete_async(model="mistral-large-latest", messages=[
        {
            "content": content,
            "role": "user",
        },
    ])

    if res is not None:
        return res
