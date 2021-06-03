""""""
from __future__ import annotations

import datetime
from decimal import Decimal, ExtendedContext, localcontext

from babel.numbers import format_currency, format_decimal
from flask_babel import get_locale

from labster.domain2.services.constants import get_constant, get_constants

_PREC_1 = Decimal(".1")
_PREC_2 = Decimal(".01")

# Constantes
LOCALISATION_TO_IR = {
    "": Decimal(0),
    "Paris ou région parisienne": Decimal("0.03"),
    "Banyuls-sur-mer": Decimal(0),
    "Roscoff": Decimal(0),
    "Villefranche-sur-mer": Decimal("0.01"),
}


def POINT_INDICE() -> Decimal:
    try:
        return Decimal(get_constant("point_indice"))
    except RuntimeError:
        # For unit tests
        return Decimal("4.630291")


def get_ctx_for_demande(demande):
    try:
        locale = get_locale()
    except RuntimeError:
        locale = "fr"
    constants = get_constants()
    cst = constants["recrutement"]
    ctx = {
        "demande": demande,
        "today": datetime.date.today(),
        "contact": demande.gestionnaire or demande.porteur,
    }

    def format_eur(amount):
        return format_currency(amount, "EUR", locale=locale)

    with localcontext(ExtendedContext):
        salaire_brut_mensuel = demande.data.get("salaire_brut_mensuel", "")
        if salaire_brut_mensuel:
            salaire_brut = ctx["salaire_brut"] = Decimal(
                str_to_float(salaire_brut_mensuel)
            )
        else:
            salaire_brut = ctx["salaire_brut"] = Decimal("0")

        if demande.quotite_de_travail and demande.quotite_de_travail.endswith("%"):
            ctx["quotite_de_travail"] = str_to_int(demande.quotite_de_travail[0:-1])
        else:
            ctx["quotite_de_travail"] = 100

        # Cas particulier des 80% qui comptent pour 85.7%.
        if ctx["quotite_de_travail"] != 80:
            salaire_brut_etp = salaire_brut * 100 / ctx["quotite_de_travail"]
        else:
            salaire_brut_etp = salaire_brut * 1000 / 857

        ctx["salaire_brut_etp"] = Decimal(salaire_brut_etp)

        ctx["indice_majore"] = int(round(ctx["salaire_brut_etp"] / POINT_INDICE()))

        # if Doctorant, do not show indice_majore nor ir (thus ir to 0 for the rest).
        nature_du_recrutement = demande.data.get("nature_du_recrutement")
        ctx["is_doctorant"] = False
        if nature_du_recrutement == "Doctorant":
            ctx["ir"] = 0
            ctx["is_doctorant"] = True
        else:
            ctx["ir"] = LOCALISATION_TO_IR.get(demande.localisation, 0) * salaire_brut

        total_salaire_brut = ctx["total_salaire_brut"] = ctx["salaire_brut"] + ctx["ir"]

        if demande.indemnite_transport_en_commun == "oui":
            ctx["cout_transport"] = Decimal(cst["transport"])
        else:
            ctx["cout_transport"] = 0

        nombre_enfants_a_charge = str_to_int(demande.nombre_enfants_a_charge or 0)
        ctx["sft"] = sft(ctx["indice_majore"], nombre_enfants_a_charge)

        # Si la durée du contrat est supérieure ou égale à 12 mois =36%
        # Si la durée du contrat est inférieure à 12 mois = 37,5%
        # TODO: calculer la durée en mois
        if demande.duree_jours >= 365:
            coef_charges = Decimal(cst["charges_plus_12_mois"])
        else:
            coef_charges = Decimal(cst["charges_moins_12_mois"])
        coef_charges = coef_charges / 100

        ctx["coef_charges"] = coef_charges * 100
        ctx["montant_charges"] = (ctx["total_salaire_brut"] + ctx["sft"]) * coef_charges

        ctx["cout_mens_charges_comprises"] = (
            ctx["total_salaire_brut"]
            + ctx["cout_transport"]
            + ctx["sft"]
            + ctx["montant_charges"]
        )

        provision_risque_charge_employeur = cst["provision_risque_charge_employeur"]
        ctx["pourcentage_provision"] = provision_risque_charge_employeur
        ctx["provision_risque"] = ctx["cout_mens_charges_comprises"] * Decimal(
            provision_risque_charge_employeur / 100
        )
        ctx["cout_total"] = ctx["cout_mens_charges_comprises"] + ctx["provision_risque"]

        if salaire_brut:
            ctx["cout_total_proportion"] = ctx["cout_total"] / salaire_brut
        else:
            ctx["cout_total_proportion"] = Decimal(0)

        # cout periode
        date_debut = demande.date_debut
        date_fin = demande.date_fin
        cout_periode = ctx["cout_periode"] = []

        if date_debut and date_fin and date_fin > date_debut:
            ctx["nb_jours"] = (date_fin - date_debut).days + 1

            ctx["annees_cout_periode"] = range(date_debut.year, date_debut.year + 4)
            start = date_debut

            for year in range(date_debut.year, date_fin.year):
                end = start.replace(month=12, day=31)
                months = month_duration(start, end)
                cout_periode.append(
                    {
                        "months": months,
                        "brut": (total_salaire_brut * months),
                        "provision": (ctx["provision_risque"] * months),
                        "total": (ctx["cout_total"] * months),
                    }
                )
                start = datetime.date(year + 1, 1, 1)

            months = month_duration(start, date_fin)

            cout_periode.append(
                {
                    "months": months,
                    "brut": (total_salaire_brut * months),
                    "provision": (ctx["provision_risque"] * months),
                    "total": (ctx["cout_total"] * months),
                }
            )

            brut = sum(d["brut"] for d in cout_periode)
            provision = sum(d["provision"] for d in cout_periode)
            total = sum(d["total"] for d in cout_periode)
            total_months = sum(d["months"] for d in cout_periode)
            cp_total = {
                "months": format_decimal(total_months, locale=locale),
                "brut": format_eur(brut),
                "provision": format_eur(provision),
                "total": format_eur(total),
            }

            # round total to upper 500 unit
            total_arrondi = int(total)
            remainder = total_arrondi % 500
            if remainder:
                total_arrondi += 500 - remainder
            ctx["total_arrondi"] = format_eur(total_arrondi)

            # format values
            cp_total["total"] = format_eur(total)
            for d in cout_periode:
                d["months"] = format_decimal(d["months"], format="#0.#", locale=locale)
                d["brut"] = format_eur(d["brut"])
                d["provision"] = format_eur(d["provision"])
                d["total"] = format_eur(d["total"])

            # fill columns if needed
            while len(cout_periode) < 4:
                cout_periode.append({})
            cout_periode.append(cp_total)

        else:
            ctx["total_arrondi"] = Decimal(0)
            ctx["annees_cout_periode"] = []

    return ctx


def sft(indice_majore: int, nb_enfants_a_charge: int) -> Decimal:
    if indice_majore < 445:
        indice_base = 444
    elif indice_majore < 717:
        indice_base = indice_majore
    else:
        indice_base = 717

    salaire_base = indice_base * POINT_INDICE()

    if nb_enfants_a_charge == 0:
        result = Decimal(0)
    elif nb_enfants_a_charge == 1:
        result = Decimal("2.29")
    elif nb_enfants_a_charge == 2:
        result = Decimal("10.67") + Decimal("0.03") * salaire_base
    elif nb_enfants_a_charge == 3:
        result = Decimal("15.24") + Decimal("0.08") * salaire_base
    else:
        n = nb_enfants_a_charge - 3
        result = (
            Decimal("15.24")
            + n * Decimal("4.57")
            + (Decimal("0.08") + n * Decimal("0.06")) * salaire_base
        )
    return result.quantize(_PREC_2)


def cout_total_charge(demande):
    ctx = get_ctx_for_demande(demande)
    return ctx["total_arrondi"]


def days_in_month(dt):
    """Return the number of days in the month."""
    month = (dt.month % 12) + 1
    year = dt.year
    if month == 1:
        year += 1
    return (dt.replace(year=year, month=month, day=1) - datetime.timedelta(1)).day


def month_duration(start, end):
    """Duration in months with fractionnal part between 2 dates in same
    year."""
    assert start.year == end.year
    assert start <= end

    start_dim = Decimal(days_in_month(start))
    start_days = Decimal(1 + start_dim - start.day)

    if start.month == end.month:
        # special case
        days = Decimal(1 + end.day - start.day)
        return (days / start_dim).quantize(_PREC_1)

    months = start_days / start_dim

    start = start.replace(month=start.month + 1, day=1)
    months += end.month - start.month
    months += Decimal(end.day) / Decimal(days_in_month(end))

    return months.quantize(_PREC_1)


def str_to_int(s, default=0):
    if isinstance(s, int):
        return s
    if isinstance(s, float):
        return int(s)

    s = s or ""
    s = s.replace(" ", "")
    try:
        return int(s)
    except ValueError:
        return default


def str_to_float(s, default=0.0):
    if isinstance(s, float):
        return s
    if isinstance(s, int):
        return float(s)

    s = s or ""
    s = s.replace(" ", "")
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return default
