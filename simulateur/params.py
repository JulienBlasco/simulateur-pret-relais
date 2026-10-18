"""Constantes légales et valeurs par défaut : source unique pour l'UI, le calcul et le PDF."""
from dataclasses import dataclass

# --- Constantes canoniques (non modifiables dans l'interface) ---
DUREE_MAX_MOIS = 24
QUOTITE_MIN, QUOTITE_MAX = 0.50, 0.80
SEUIL_ENDETTEMENT = 0.35  # recommandation HCSF
NOTAIRE_ANCIEN, NOTAIRE_NEUF = 0.075, 0.025

TYPES_RELAIS = {
    "in_fine": "Intérêts payés chaque mois, capital in fine",
    "differe": "Intérêts différés (capitalisés, payés à la vente)",
}

MENTIONS = (
    "Simulation indicative, non contractuelle. Un crédit vous engage et doit être remboursé. "
    "Vérifiez vos capacités de remboursement avant de vous engager. "
    "Délai de réflexion de 10 jours après réception de l'offre ; faculté de rétractation de 14 jours. "
    "Le taux d'usure applicable (catégorie prêts relais) est publié chaque trimestre par la Banque de France."
)


@dataclass
class Params:
    # Bien à vendre (frais d'agence supposés nuls)
    valeur_vente: float = 300_000
    crd: float = 80_000
    quotite: float = 0.70
    # Bien à acheter
    prix_achat: float = 400_000
    taux_notaire: float = NOTAIRE_ANCIEN
    travaux: float = 0
    apport: float = 30_000
    # Prêt relais
    type_relais: str = "in_fine"
    duree_relais: int = 12
    taux_relais: float = 0.045
    assurance_relais: float = 0.003
    montant_relais: float | None = None  # None = maximum autorisé
    frais_dossier: float | None = None  # None = 0,5 % du montant
    frais_garantie_pct: float = 0.015
    # Prêt complémentaire
    avec_complementaire: bool = True
    taux_compl: float = 0.038
    duree_compl_ans: int = 20
    assurance_compl: float = 0.003
    # Contrôles
    revenus: float | None = None
    seuil_usure: float = 0.0  # taux d'usure BdF en vigueur, à saisir (0 = pas de contrôle)
