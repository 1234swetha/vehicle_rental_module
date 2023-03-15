from odoo import models, fields


class RentChargeModel(models.Model):
    _name = "rent.charge"
    _rec_name = "time"
    _description = "Rent Charge"

    time = fields.Selection(string="Time", selection=[('hour', 'Hour'), ('day', 'Day'), ('week', 'Week'),
                                                      ('month', 'Month')])
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    amount = fields.Monetary()
    vehicle_name_id = fields.Many2one("vehicle.rental", string="Vehicle", required=True)

    def check_period(self, vehicle_id):
        val = self.search([('vehicle_name_id', '=', int(vehicle_id))])
        lst = []
        for rec in val:
            lst.append({rec.id: rec.time})
        return lst


