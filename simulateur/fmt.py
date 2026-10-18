"""Formatage et lecture des nombres à la française (espace des milliers, virgule décimale)."""


def nombre(x: float, nd: int = 0) -> str:
    return f"{x:,.{nd}f}".replace(",", " ").replace(".", ",")


def eur(x: float) -> str:
    return nombre(x) + " €"


def eur2(x: float) -> str:
    return nombre(x, 2) + " €"


def pct(x: float, nd: int = 2) -> str:
    return nombre(x * 100, nd) + " %"


def lire(texte: str) -> float | None:
    """'1 234,5' -> 1234.5 ; None si illisible ou négatif."""
    try:
        x = float("".join(texte.split()).replace(",", "."))
    except ValueError:
        return None
    return x if x >= 0 else None
