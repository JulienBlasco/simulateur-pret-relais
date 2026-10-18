"""Formatage à la française."""


def eur(x: float) -> str:
    return f"{x:,.0f} €".replace(",", " ")


def eur2(x: float) -> str:
    return f"{x:,.2f} €".replace(",", " ").replace(".", ",")


def pct(x: float, nd: int = 2) -> str:
    return f"{x * 100:.{nd}f} %".replace(".", ",")
