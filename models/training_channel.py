from odoo import fields, models


class TrainingChannel(models.Model):
    _name = "training.channel"
    _description = "Canal"
    _order = "name"

    name = fields.Char(
        string="Canal",
        required=True,
    )
