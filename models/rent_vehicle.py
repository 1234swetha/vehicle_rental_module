from odoo import models, fields, api


class RentalModel(models.Model):
    _name = "vehicle.rental"
    _description = "Vehicle Rental"
    _rec_name = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute="_compute_name", store=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle", domain="[('state_id.name', '=','Registered' )]",
                                 required=True)
    brand = fields.Text(compute="_compute_brand", store=True)
    registration_date = fields.Date("Registration Date", related='vehicle_id.registration_date',
                                    default=lambda self: fields.Date.today(), readonly=False)
    model_year = fields.Char(string="Model Year", compute="_compute_model_year")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    rent = fields.Monetary()
    state = fields.Selection(string="State", selection=[('available', 'Available'), ('not available', 'Not Available'),
                                                        ('sold', 'Sold')], default="available")
    rent_req_ids = fields.One2many("rent.request", 'vehicle_id', string="Request", readonly=True,
                                   domain=['|', ('state', '=', 'Confirmed'), ('state', '=', 'Invoiced')])
    charge_ids = fields.One2many("rent.charge", "vehicle_name_id", string="Rent charges")
    rent_request_count = fields.Integer(compute='_compute_rent_request_count')
    warning = fields.Boolean(string="Warning", default=False)
    late = fields.Boolean(string="Late", default=False)
    image = fields.Binary()

    @api.depends("vehicle_id.brand_id.name")
    def _compute_brand(self):
        if self.vehicle_id:
            self.brand = self.vehicle_id.brand_id.name
        else:
            self.brand = False

    @api.depends("registration_date")
    def _compute_model_year(self):
        for record in self:
            if record.registration_date:
                record.model_year = record.registration_date.year

    @api.depends("vehicle_id.name", "model_year")
    def _compute_name(self):
        for record in self:
            if record.vehicle_id.name and record.model_year:
                record.name = str(record.vehicle_id.name) + "/" + str(record.model_year)
            else:
                record.name = False

    def button_available(self):
        self.write({'state': "available"})

    def button_not_available(self):
        self.write({'state': "not available"})

    def button_sold(self):
        self.write({'state': "sold"})

    def button_confirmed(self):
        self.write({'state': "not available"})

    def get_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rent request',
            'view_mode': 'tree',
            'res_model': 'rent.request',
            'domain': [('vehicle_id', '=', self.name)],
            'context': "{'create': False}"
        }

    def _compute_rent_request_count(self):
        for record in self:
            record.rent_request_count = self.env['rent.request'].search_count([('vehicle_id.id', '=', self.id)])

    @api.onchange('vehicle_id')
    def onchange_name(self):
        obj = self.search([])
        available_ids = []
        for i in obj:
            available_ids.append(i.vehicle_id.id)
        return {'domain': {'vehicle_id': [('id', 'not in', available_ids)]}}
