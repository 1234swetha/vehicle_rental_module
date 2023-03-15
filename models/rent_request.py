from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RentRequestModel(models.Model):
    _name = "rent.request"
    _description = "Rent Request"
    _rec_name = "reference_no"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    reference_no = fields.Char(required=True,
                               readonly=True, default=lambda self: _('New'))
    partner_id = fields.Many2one("res.partner", string="Customer")
    partner_address = fields.Char(string="Address", related='partner_id.contact_address')
    request_date = fields.Datetime(default=lambda self: fields.Datetime.now(), string="Request date")
    vehicle_id = fields.Many2one("vehicle.rental", string="Vehicle", domain="[('state', '=','available' )]",
                                 required=True)
    from_date = fields.Datetime(default=lambda self: fields.Datetime.today())
    to_date = fields.Datetime(compute='_compute_to_date', store=True)
    period = fields.Char(compute="_compute_period", string="Period", store=True)
    state = fields.Selection(string="State", selection=[('Draft', 'Draft'), ('Confirmed', 'Confirmed'),
                                                        ('Invoiced', 'Invoiced'), ('Returned', 'Returned')],
                             default="Draft")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    rent = fields.Monetary(string="Rent", related='vehicle_id.rent')
    charge_id = fields.Many2one('rent.charge', string='Period Type', required=True)
    amount_id = fields.Monetary(compute='_compute_amount')
    paid = fields.Boolean(string="Paid", default=False)

    def button_confirmed(self):
        self.write({'state': "Confirmed"})
        self.vehicle_id.state = "not available"

    def button_invoice(self):
        self.state = "Invoiced"
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'payment_reference': self.reference_no,
            'request_id': self.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Rent Vehicle',
                'price_unit': self.amount_id})]
        })
        return {
            'name': "invoicing",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'domain': [('partner_id', '=', self.partner_id)]

        }

    def button_returned(self):
        self.write({'state': "Returned"})
        self.vehicle_id.state = "available"
        self.vehicle_id.warning = False
        self.vehicle_id.late = False

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        return {'domain': {'charge_id': [('id', 'in', self.vehicle_id.charge_ids.ids)]}}

    @api.depends('to_date', 'from_date')
    def _compute_period(self):
        for record in self:
            if record.to_date and record.from_date:
                record.period = (record.to_date - record.from_date).days

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'rent.request') or _('New')
        res = super(RentRequestModel, self).create(vals)
        return res

    @api.depends('charge_id', 'to_date')
    def _compute_to_date(self):
        for record in self:
            if record.charge_id.time == 'day':
                record.to_date = record.from_date + relativedelta(days=1)
            elif record.charge_id.time == 'hour':
                record.to_date = record.from_date + relativedelta(hours=1)
            elif record.charge_id.time == 'month':
                record.to_date = record.from_date + relativedelta(months=1)
            elif record.charge_id.time == 'week':
                record.to_date = record.from_date + relativedelta(weeks=1)
            else:
                record.to_date = record.from_date

    @api.constrains('to_date', 'from_date')
    def date_constrains(self):
        if self.to_date < self.from_date:
            raise UserError(' To Date Must be greater Than From Date')

    @api.depends('charge_id')
    def _compute_amount(self):
        for record in self:
            record.amount_id = record.charge_id.amount

    @api.onchange('from_date')
    def onchange_from_date(self):
        if self.to_date:
            if (self.to_date - relativedelta(days=2)) <= fields.Datetime.today():
                self.vehicle_id.warning = True
                if self.to_date < fields.Datetime.today():
                    self.vehicle_id.warning = False
                    self.vehicle_id.late = True
            else:
                self.vehicle_id.late = False

    def get_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('payment_reference', '=', self.reference_no)],
            'context': "{'create': False}"
        }

    def check_to_date(self, from_date, charge_id):
        charge = self.env['rent.charge'].sudo().search([('id', '=', charge_id)])
        from_dat = datetime.strptime(from_date, '%Y-%m-%d').date()
        if charge.time == 'day':
            to_date = from_dat + relativedelta(days=1)
        elif charge.time == 'hour':
            to_date = from_dat + relativedelta(hours=1)
        elif charge.time == 'month':
            to_date = from_dat + relativedelta(months=1)
        elif charge.time == 'week':
            to_date = from_dat + relativedelta(weeks=1)
        else:
            to_date = from_dat
        return to_date

    def check_amount(self, charge_id):
        charge = self.env['rent.charge'].sudo().search([('id', '=', charge_id)])
        amount = charge.amount
        return amount

