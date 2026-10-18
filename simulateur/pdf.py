"""Export PDF daté de la synthèse."""
from datetime import datetime

from fpdf import FPDF

from .fmt import eur, eur2, pct
from .params import MENTIONS, TYPES_RELAIS, Params


def _sections(p: Params, r: dict) -> list[tuple[str, list[tuple[str, str]]]]:
    return [
        ("Hypothèses", [
            ("Valeur estimée du bien à vendre", eur(p.valeur_vente)),
            ("Capital restant dû", eur(p.crd)),
            ("Décote à la vente", pct(p.decote, 1)),
            ("Prix du bien à acheter", eur(p.prix_achat)),
            ("Frais de notaire", pct(p.taux_notaire, 1)),
            ("Travaux", eur(p.travaux)),
            ("Apport personnel", eur(p.apport)),
        ]),
        ("Prêt relais", [
            ("Formule", TYPES_RELAIS[p.type_relais]),
            ("Montant (maximum autorisé : %s)" % eur(r["montant_max_relais"]), eur(r["montant_relais"])),
            ("Durée", f"{p.duree_relais} mois"),
            ("Taux nominal annuel", pct(p.taux_relais)),
            ("Assurance (annuelle)", pct(p.assurance_relais)),
            ("Frais de dossier", eur(r["frais_dossier"])),
            ("Frais de garantie", eur(r["frais_garantie"])),
            ("TAEG", pct(r["taeg_relais"])),
        ]),
        ("Prêt complémentaire", [
            ("Montant", eur(r["complementaire"])),
            ("Taux / durée", f"{pct(p.taux_compl)} / {p.duree_compl_ans} ans"),
        ] if r["complementaire"] else [("Aucun", "")]),
        ("Résultats", [
            ("Mensualité pendant le relais", eur2(r["mensualite_pendant"])),
            ("Mensualité après la vente", eur2(r["mensualite_apres"])),
            ("Remboursement du relais par la vente", eur(r["remboursement_vente"])),
            ("Solde après vente et remboursement du CRD", eur(r["reste_vente"])),
            ("Coût du prêt relais (intérêts, assurance, frais)", eur(r["cout_relais"])),
            ("Coût du prêt complémentaire (intérêts, assurance)", eur(r["cout_compl"])),
            ("Coût total du crédit", eur(r["cout_total"])),
        ]),
    ]


def _latin1(texte: str) -> str:
    """Police de base du PDF : pas de symbole € ni d'espace insécable."""
    return texte.replace("€", "EUR")


def synthese_pdf(p: Params, r: dict, maintenant: datetime | None = None) -> bytes:
    maintenant = maintenant or datetime.now()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Simulation de prêt relais", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Établie le {maintenant:%d/%m/%Y à %H:%M}", new_x="LMARGIN", new_y="NEXT")
    for titre, lignes in _sections(p, r):
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, titre, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for label, valeur in lignes:
            pdf.cell(130, 6, _latin1(label))
            pdf.cell(0, 6, _latin1(valeur), align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, MENTIONS)
    return bytes(pdf.output())
