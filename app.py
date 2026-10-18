import pandas as pd
import streamlit as st

from simulateur.calcul import montant_max_relais, simuler
from simulateur.fmt import eur, eur2, pct
from simulateur.params import (DUREE_MAX_MOIS, MENTIONS, NOTAIRE_ANCIEN, NOTAIRE_NEUF, QUOTITE_MAX,
                               QUOTITE_MIN, SEUIL_ENDETTEMENT, TYPES_RELAIS, Params)
from simulateur.pdf import synthese_pdf

st.set_page_config(page_title="Simulateur de prêt relais", layout="wide")
st.title("Simulateur de prêt relais")
d = Params()


def euros(label, value, **kw):
    return st.number_input(label, value=float(value), min_value=0.0, step=1000.0, format="%.0f", **kw)


def taux(label, value, **kw):
    return st.number_input(label, value=value * 100, min_value=0.0, step=0.05, format="%.2f", **kw) / 100


with st.sidebar:
    st.header("Bien à vendre")
    valeur_vente = euros("Valeur estimée (€)", d.valeur_vente)
    crd = euros("Capital restant dû (€)", d.crd)
    quotite = st.slider("Quotité du relais (% de la valeur)", int(QUOTITE_MIN * 100), int(QUOTITE_MAX * 100),
                        int(d.quotite * 100), 5) / 100

    st.header("Bien à acheter")
    prix_achat = euros("Prix (€)", d.prix_achat)
    neuf = st.radio("Type de bien", ["Ancien", "Neuf"], horizontal=True) == "Neuf"
    taux_notaire = taux("Frais de notaire (%)", NOTAIRE_NEUF if neuf else NOTAIRE_ANCIEN, key=f"notaire_{neuf}")
    travaux = euros("Travaux (€)", d.travaux)
    apport = euros("Apport personnel (€)", d.apport)

    st.header("Prêt relais")
    max_relais = montant_max_relais(Params(valeur_vente=valeur_vente, crd=crd, quotite=quotite))
    montant_relais = euros(f"Montant (max {eur(max_relais)})", max_relais, max_value=max_relais,
                           key=f"relais_{max_relais}")
    type_relais = st.selectbox("Formule", list(TYPES_RELAIS), format_func=TYPES_RELAIS.get)
    duree_relais = st.slider("Durée (mois)", 1, DUREE_MAX_MOIS, d.duree_relais)
    taux_relais = taux("Taux nominal annuel (%)", d.taux_relais)
    assurance_relais = taux("Assurance annuelle (%)", d.assurance_relais)
    frais_dossier = st.number_input("Frais de dossier (€)", min_value=0.0, step=50.0, format="%.0f",
                                    value=float(round(0.005 * montant_relais)), key=f"dossier_{montant_relais}")
    frais_garantie_pct = taux("Frais de garantie (% du montant)", d.frais_garantie_pct)

    st.header("Prêt complémentaire")
    avec_compl = st.checkbox("Financer le solde par un prêt amortissable", value=d.avec_complementaire)
    if avec_compl:
        taux_compl = taux("Taux nominal annuel (%)", d.taux_compl, key="tc")
        duree_compl = st.slider("Durée (ans)", 5, 30, d.duree_compl_ans)
        assurance_compl = taux("Assurance annuelle (%)", d.assurance_compl, key="ac")
    else:
        taux_compl, duree_compl, assurance_compl = d.taux_compl, d.duree_compl_ans, d.assurance_compl

    st.header("Contrôles (facultatif)")
    revenus = euros("Revenus mensuels nets du foyer (€)", 0)
    seuil_usure = taux("Taux d'usure prêts relais (%, 0 = pas de contrôle)", d.seuil_usure)

p = Params(
    valeur_vente=valeur_vente, crd=crd, quotite=quotite,
    prix_achat=prix_achat, taux_notaire=taux_notaire, travaux=travaux, apport=apport,
    type_relais=type_relais, duree_relais=duree_relais, taux_relais=taux_relais,
    assurance_relais=assurance_relais, montant_relais=montant_relais, frais_dossier=frais_dossier,
    frais_garantie_pct=frais_garantie_pct, avec_complementaire=avec_compl, taux_compl=taux_compl,
    duree_compl_ans=duree_compl, assurance_compl=assurance_compl,
    revenus=revenus or None, seuil_usure=seuil_usure,
)
r = simuler(p)

c = st.columns(4)
c[0].metric("Mensualité pendant le relais", eur2(r["mensualite_pendant"]))
c[1].metric("Mensualité après la vente", eur2(r["mensualite_apres"]))
c[2].metric("Coût total du crédit", eur(r["cout_total"]))
c[3].metric("TAEG du prêt relais", pct(r["taeg_relais"]))

if r["manque"] > 0:
    st.warning(f"Financement incomplet : il manque {eur(r['manque'])} (activez le prêt complémentaire ou augmentez l'apport).")
if r["reste_vente"] < 0:
    st.error(f"La vente ne couvre pas le CRD et le relais : il manque {eur(-r['reste_vente'])}.")
if p.seuil_usure and r["taeg_relais"] > p.seuil_usure:
    st.error(f"Le TAEG ({pct(r['taeg_relais'])}) dépasse le taux d'usure renseigné ({pct(p.seuil_usure)}).")
if r["endettement_pendant"] and r["endettement_pendant"] > SEUIL_ENDETTEMENT:
    st.warning(f"Endettement pendant le relais : {pct(r['endettement_pendant'], 1)} (recommandation : {pct(SEUIL_ENDETTEMENT, 0)} maximum).")

left, right = st.columns(2)
with left:
    st.subheader("Plan de financement")
    st.table(pd.Series({
        "Coût d'acquisition (prix + notaire + travaux)": eur(r["besoin"]),
        "Apport personnel": eur(p.apport),
        "Prêt relais": eur(r["montant_relais"]),
        "Prêt complémentaire": eur(r["complementaire"]),
    }, name="Montant"))
with right:
    st.subheader("Coût du crédit")
    st.table(pd.Series({
        "Intérêts du relais": eur(r["interets_relais"]),
        "Assurance du relais": eur(r["assurance_relais"]),
        "Frais de dossier et de garantie": eur(r["frais_dossier"] + r["frais_garantie"]),
        "Intérêts et assurance du complémentaire": eur(r["cout_compl"]),
        "Total": eur(r["cout_total"]),
    }, name="Montant"))

st.subheader("À la vente")
st.write(
    f"Remboursement du relais : **{eur(r['remboursement_vente'])}** · "
    f"Solde après CRD : **{eur(r['reste_vente'])}**"
)

with st.expander("Échéancier mensuel"):
    st.dataframe(pd.DataFrame(r["calendrier"]).rename(columns={
        "mois": "Mois", "relais": "Relais", "complementaire": "Complémentaire", "mensualite": "Total"}).round(2),
        hide_index=True, use_container_width=True)

st.download_button("Exporter la synthèse en PDF", synthese_pdf(p, r), "simulation_pret_relais.pdf", "application/pdf")
st.caption(MENTIONS)
