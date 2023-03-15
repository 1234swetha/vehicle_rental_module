from odoo import models, fields, api


class RentInvoicingModel(models.Model):
    _inherit = "account.move"

    request_id = fields.Many2one('rent.request')

    @api.constrains('payment_state')
    def check_payment_state(self):
        for record in self:
            if record.payment_state == 'paid':
                record.request_id.paid = True
