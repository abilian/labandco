from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy.orm.scoping import scoped_session

from labster.domain2.services.constants import get_constant, get_constants, \
    update_constants


def test_get_constant(db_session: scoped_session) -> None:
    val = get_constant("faq_categories")
    assert len(val) >= 1
    assert get_constant("nom_bureaux_dgrtt.MSAR").startswith("Moyens")

    with pytest.raises(KeyError):
        get_constant("foo.bar")


def test_update_constants(db_session: scoped_session) -> None:
    constants: dict[str, Any] = {}
    real_constants = get_constants()
    assert update_constants(constants) == real_constants

    missing_one = real_constants
    missing_one["faq_categories"] = []
    assert update_constants(missing_one) == real_constants
