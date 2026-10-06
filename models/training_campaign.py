from odoo import fields, models


class TrainingCampaign(models.Model):
    _name = "training.campaign"
    _description = "Campaña de Formación"
    _order = "name"

    _sql_constraints = [
        (
            "unique_campaign_name",
            "unique(name)",
            "Ya existe una campaña con ese nombre.",
        ),
    ]

    name = fields.Char(
        string="Nombre",
        required=True,
    )
