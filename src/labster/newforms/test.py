from __future__ import annotations

from labster.newforms.rh import DemandeRHForm


def test_export_empty_rh_form_as_dict(db_session):
    form = DemandeRHForm()
    exported = form.to_dict()
    assert "fieldsets" in exported
    fieldsets = exported["fieldsets"]
    assert any(lambda x: x["name"] == "nature" for x in fieldsets)


def test_export_rh_form_with_data_as_dict(db_session):
    model = {"type_de_demande": "Renouvellement"}
    form = DemandeRHForm(model=model)
    exported = form.to_dict()
    assert "fieldsets" in exported
