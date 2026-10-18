import pytest

from simulateur.calcul import Loan, echeancier, simuler, taeg, total
from simulateur.params import Params


def test_in_fine():
    rows = echeancier(Loan(100_000, 0.06, 0, 12, "in_fine"))
    assert sum(r["interets"] for r in rows) == pytest.approx(6_000)
    assert sum(r["capital"] for r in rows) == 100_000
    assert rows[-1]["capital"] == 100_000 and rows[0]["capital"] == 0


def test_differe():
    rows = echeancier(Loan(100_000, 0.06, 0, 12, "differe"))
    assert sum(r["interets"] for r in rows) == pytest.approx(100_000 * (1.005**12 - 1))
    assert all(total(r) == 0 for r in rows[:-1])


def test_amortissable():
    rows = echeancier(Loan(200_000, 0.04, 0, 240, "amortissable"))
    assert sum(r["capital"] for r in rows) == pytest.approx(200_000)
    assert total(rows[0]) == pytest.approx(1211.96, abs=0.01)


def test_taeg_sans_frais():
    assert taeg(Loan(100_000, 0.06, 0, 12, "amortissable"), 0) == pytest.approx(1.005**12 - 1, abs=1e-9)


def test_taeg_frais_augmentent():
    loan = Loan(100_000, 0.045, 0.003, 12, "in_fine")
    assert taeg(loan, 2_000) > taeg(loan, 0) > 0.045


def test_defauts():
    r = simuler(Params())
    assert r["montant_max_relais"] == pytest.approx(130_000)
    assert r["montant_relais"] == pytest.approx(130_000)
    assert r["frais_dossier"] == pytest.approx(650)
    assert r["besoin"] == pytest.approx(430_000)
    assert r["complementaire"] == pytest.approx(430_000 - 30_000 - 130_000)
    assert r["remboursement_vente"] == pytest.approx(130_000)
    assert r["reste_vente"] == pytest.approx(300_000 - 80_000 - 130_000)
    assert len(r["calendrier"]) == 240


def test_sans_complementaire_manque():
    r = simuler(Params(avec_complementaire=False))
    assert r["complementaire"] == 0 and r["manque"] == pytest.approx(270_000)
