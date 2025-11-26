import asyncio
from datetime import datetime


def catsay(text: str) -> str:
    bubble = f"< {text} >"
    inner_len = len(text)
    left_padding = " " * 2
    border = f"{left_padding}{'-' * inner_len}"
    cat = r"""
    /\_/\
   ( o.o )
    > ^ <
"""
    return f"{border}\n{bubble}\n{border}{cat}"


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
