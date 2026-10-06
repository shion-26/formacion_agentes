from odoo import fields, models


class TrainingGroup(models.Model):
    _name = "training.group"
    _description = "Grupo de formación"
    _order = "name"

    name = fields.Char(
        string="Grupo de formación",
        required=True,
    )
