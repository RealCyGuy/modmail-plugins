import random
import re
from typing import Tuple

import aiohttp


async def request_oeis() -> Tuple[str, str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://oeis.org/webcam",
            params={"fromjavascript": 1, "q": "", "random": random.random()},
        ) as resp:
            text = await resp.text()
            sequence = re.search(r"(?<=<tt>).*(?=</tt>)", text).group()
            oeis_id = re.search(r'(?<=href="/).*(?=">)', text).group()
    return sequence, oeis_id
