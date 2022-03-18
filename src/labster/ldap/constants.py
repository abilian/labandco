# Listes des DN des structures pour lesquelles on doit faire ca
# on importe les membres et pas les structures avec pour règle
# que les personnes qui sont dans AD sont affectées à la structure du dessus
from __future__ import annotations

import re

SU_DN = "ou=SU,ou=Affectations,dc=chapeau,dc=fr"
DRI_DN = "ou=0107,ou=SCUN,ou=SU,ou=Affectations,dc=chapeau,dc=fr"
DRV_DNS = {
    "FL": "ou=RE,ou=SG,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "FM": "ou=M0107,ou=FACM,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "FSI": "ou=S0107,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
}
DRI_ET_DRV_DNS = [DRI_DN] + list(DRV_DNS.values())

FAC_DNS = [
    "ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=FACM,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
]

ADMINS_DN = [
    "ou=0102,ou=988,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=0701,ou=907,ou=SCUN,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=1801,ou=918,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=1901,ou=919,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=2101,ou=929,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=2501,ou=925,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=2601,ou=926,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=2701,ou=927,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=3301,ou=933,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=3401,ou=934,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=3601,ou=936,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=3701,ou=937,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=3801,ou=938,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=3901,ou=939,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=4001,ou=940,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=S0101,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=67010,ou=967,ou=FACM,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=AA,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=AL,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=AN,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=AR,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=ES,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=GE,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=GR,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=HI,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=IB,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=IT,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=LA,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=LC,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=LC,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=LE,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=LF,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=MU,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=OM,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=PH,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=AD,ou=SH,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=OM,ou=HI,ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=DC,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=VPDP,ou=988,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=VPEI,ou=988,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=VPEN,ou=988,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=VPEU,ou=988,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=VPFO,ou=988,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=VPMD,ou=988,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=VPNM,ou=988,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=VPPC,ou=988,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=VPRE,ou=988,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=VPRI,ou=988,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
]

PRESIDENCE_DN = "ou=0101,ou=DUPMC,ou=SCUN,ou=SU,ou=Affectations,dc=chapeau,dc=fr"
CELSA_DN = "ou=DI,ou=CE,ou=EI,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr"


def get_parent_dn(dn: str) -> str:
    path = list(dn.split(","))
    parent_path: list[str] = path[1:]

    # Prise en compte de différents cas particuliers
    parent_dn = ",".join(parent_path)

    # Les services communs sont rattachés à l'université
    if parent_dn == "ou=SCUN,ou=SU,ou=Affectations,dc=chapeau,dc=fr":
        parent_path = parent_path[1:]

    # Les UFR de la fac de lettre sont rattachés à la fac
    if parent_dn == "ou=UF,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr":
        parent_path = parent_path[1:]

    # Les ED de la fac de lettre sont rattachés à l'institut de formation doctorale
    if parent_dn == "ou=ED,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr":
        parent_path = "ou=907,ou=SCUN,ou=SU,ou=Affectations,dc=chapeau,dc=fr".split(",")

    # Les DF de la fac de lettre sont rattachés à la fac
    if parent_dn == "ou=SG,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr":
        parent_path = parent_path[1:]

    # Cas particulier du CELSA:
    if dn == CELSA_DN:
        parent_path = parent_path[2:]

    # Les labos de la fac de lettre sont rattachés à une structure
    # "laboratoires de la fac de lettre"
    if re.match(
        "^ou=[0-9]+,ou=ED,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr$", parent_dn
    ):
        parent_path = ["ou=LABOS"] + parent_path[2:]

    return ",".join(parent_path)
