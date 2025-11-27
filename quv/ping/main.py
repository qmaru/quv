import asyncio
from datetime import datetime

from quv.utils.catsay import catsay


def funny():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = "quv meow"
    say = f"{now}\n{catsay(msg)}"
    print(say)


def cli():
    asyncio.run(main())


async def main():
    funny()


if __name__ == "__main__":
    asyncio.run(main())
