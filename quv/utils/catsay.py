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
