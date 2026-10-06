from odoo import fields, models


class TrainingEntryType(models.Model):
    _name = "training.entry.type"
    _description = "Tipo de ingreso"
    _order = "name"

    _sql_constraints = [
        (
            "unique_entry_type",
            "unique(name)",
            "Ya existe este tipo de ingreso.",
        ),
    ]

    name = fields.Char(
        string="Tipo de ingreso",
        required=True,
    )
