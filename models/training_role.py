from odoo import fields, models

class TrainingRole(models.Model):
    _name = "training.role"
    _description = "Cargo / Rol"
    _order = "name"

    name = fields.Char(
        string="Cargo",
        required=True,
    )
