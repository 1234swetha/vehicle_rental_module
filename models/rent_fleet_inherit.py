from odoo import models, fields


class RentalModel(models.Model):
    _inherit = "fleet.vehicle"

    registration_date = fields.Date("Registration Date", default=lambda self: fields.Date.today())
