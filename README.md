# Simulateur de prêt relais

    pip install -r requirements.txt
    streamlit run app.py
    pytest

Variantes : intérêts payés mensuellement (capital in fine) ou différés, avec ou sans prêt complémentaire.
Hypothèses : frais d'agence nuls ; taux proportionnel (annuel/12) ; assurance sur capital initial ; le taux d'usure est à saisir. Le solde de la vente n'est pas réinjecté dans le prêt complémentaire (il reste de la trésorerie) ; le taux d'endettement est contrôlé sur la mensualité après la vente.
