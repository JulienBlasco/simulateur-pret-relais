"""Calculs purs : échéanciers, TAEG, montants et bilan de vente."""
from dataclasses import dataclass

from .params import Params, QUOTITE_MAX


@dataclass
class Loan:
    montant: float
    taux: float  # nominal annuel, proportionnel (taux/12 par mois)
    assurance: float  # % annuel du capital initial, payé chaque mois
    mois: int
    type: str  # "in_fine" | "differe" | "amortissable"


def echeancier(loan: Loan) -> list[dict]:
    """Une ligne par mois : interets, assurance, capital."""
    i, n, m = loan.taux / 12, loan.mois, loan.montant
    ass = m * loan.assurance / 12
    rows = []
    restant = m
    annuite = m / n if i == 0 else m * i / (1 - (1 + i) ** -n)
    for k in range(1, n + 1):
        if loan.type == "amortissable":
            interets = restant * i
            capital = annuite - interets
        elif loan.type == "in_fine":
            interets, capital = m * i, (m if k == n else 0)
        else:  # différé : intérêts capitalisés, tout est dû au dernier mois
            interets = m * ((1 + i) ** n - 1) if k == n else 0
            capital = m if k == n else 0
        restant -= capital
        rows.append({"mois": k, "interets": interets, "assurance": ass, "capital": capital})
    return rows


def total(row: dict) -> float:
    return row["interets"] + row["assurance"] + row["capital"]


def taeg(loan: Loan, frais: float) -> float:
    """TAEG actuariel annualisé : (1+i)^12 - 1, i solution de l'équation des flux."""
    flux = [total(r) for r in echeancier(loan)]
    net = loan.montant - frais

    def valeur(i):
        return sum(f / (1 + i) ** k for k, f in enumerate(flux, 1)) - net

    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if valeur(mid) > 0 else (lo, mid)
    return (1 + lo) ** 12 - 1


def montant_max_relais(p: Params) -> float:
    return max(0.0, p.valeur_vente * min(p.quotite, QUOTITE_MAX) - p.crd)


def simuler(p: Params) -> dict:
    """Résultat complet d'une simulation."""
    max_relais = montant_max_relais(p)
    montant = max_relais if p.montant_relais is None else p.montant_relais
    frais_dossier = 0.005 * montant if p.frais_dossier is None else p.frais_dossier
    frais_garantie = montant * p.frais_garantie_pct
    frais_relais = frais_dossier + frais_garantie

    besoin = (p.prix_achat * (1 + p.taux_notaire)) + p.travaux
    compl_montant = max(0.0, besoin - p.apport - montant) if p.avec_complementaire else 0.0
    manque = 0.0 if p.avec_complementaire else max(0.0, besoin - p.apport - montant)

    relais = Loan(montant, p.taux_relais, p.assurance_relais, p.duree_relais, p.type_relais)
    lignes_relais = echeancier(relais)
    lignes_compl = []
    if compl_montant > 0:
        compl = Loan(compl_montant, p.taux_compl, p.assurance_compl, p.duree_compl_ans * 12, "amortissable")
        lignes_compl = echeancier(compl)

    # Calendrier combiné : la vente rembourse le capital (et intérêts différés) du relais au dernier mois.
    calendrier = []
    for k in range(1, max(p.duree_relais, len(lignes_compl)) + 1):
        r = lignes_relais[k - 1] if k <= p.duree_relais else None
        c = lignes_compl[k - 1] if k <= len(lignes_compl) else None
        mens_relais = r["assurance"] + (r["interets"] if p.type_relais == "in_fine" else 0) if r else 0
        mens_compl = total(c) if c else 0
        calendrier.append({
            "mois": k,
            "relais": mens_relais,
            "complementaire": mens_compl,
            "mensualite": mens_relais + mens_compl,
        })

    solde_relais = sum(r["capital"] + (r["interets"] if p.type_relais == "differe" else 0) for r in lignes_relais)
    vente_nette = p.valeur_vente  # hypothèse : vente au prix estimé (décote < marge de la quotité)
    reste_vente = vente_nette - p.crd - solde_relais  # argent disponible après la vente

    interets_relais = sum(r["interets"] for r in lignes_relais)
    assurance_relais = sum(r["assurance"] for r in lignes_relais)
    cout_relais = interets_relais + assurance_relais + frais_relais
    cout_compl = sum(r["interets"] + r["assurance"] for r in lignes_compl)

    mens_pendant = calendrier[0]["mensualite"]
    mens_apres = total(lignes_compl[0]) if lignes_compl else 0
    return {
        "montant_relais": montant, "montant_max_relais": max_relais,
        "frais_dossier": frais_dossier, "frais_garantie": frais_garantie,
        "besoin": besoin, "complementaire": compl_montant, "manque": manque,
        "interets_relais": interets_relais, "assurance_relais": assurance_relais,
        "cout_relais": cout_relais, "cout_compl": cout_compl, "cout_total": cout_relais + cout_compl,
        "taeg_relais": taeg(relais, frais_relais) if montant > 0 else 0.0,
        "mensualite_pendant": mens_pendant, "mensualite_apres": mens_apres,
        "remboursement_vente": solde_relais, "reste_vente": reste_vente,
        "calendrier": calendrier,
        "endettement_apres": mens_apres / p.revenus if p.revenus else None,
    }
