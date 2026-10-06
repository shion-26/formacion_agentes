from odoo import fields, models


class TrainingTrainer(models.Model):
    _name = "training.trainer"
    _description = "Formador"
    _order = "name"

    _sql_constraints = [
        (
            "unique_trainer_name",
            "unique(name)",
            "Ya existe un formador con ese nombre.",
        ),
    ]

    name = fields.Char(
        string="Nombre",
        required=True,
    )
