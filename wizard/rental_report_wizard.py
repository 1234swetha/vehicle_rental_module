from odoo import models, fields


class RentalReportWizard(models.TransientModel):
    _name = 'rental.report.wizard'
    _description = "Rental Report Wizard"

    vehicle_id = fields.Many2one("vehicle.rental", string="Vehicle")
    from_date = fields.Datetime(default=fields.Datetime.today(), string="Date From")
    to_date = fields.Datetime(default=fields.Datetime.today(), string="Date To")

    def action_print(self):
        query = """
               select rent_request.state as state,res_partner.name as customer,
               rent_request.period as period,fleet_vehicle_model.name as model 
               from rent_request
               inner join res_partner
               on res_partner.id = rent_request.partner_id
               inner join vehicle_rental
               on vehicle_rental.id = rent_request.vehicle_id
               inner join fleet_vehicle
               on fleet_vehicle.id = vehicle_rental.vehicle_id
               inner join fleet_vehicle_model
               on fleet_vehicle_model.id = fleet_vehicle.model_id 
               """
        if self.vehicle_id:
            query += """where vehicle_rental.id  = %s """ % self.vehicle_id.id
        if self.from_date:
            query += """and rent_request.from_date >= '%s'""" % self.from_date
        if self.to_date:
            query += """and rent_request.to_date <= '%s'""" % self.to_date
        cr = self._cr
        cr.execute(query)
        sql_dict = self._cr.dictfetchall()

        data = {
            'vehicle_name': self.vehicle_id.name,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'sql_data': sql_dict
        }
        return self.env.ref('vehicle_rental.action_vehicle_rental_report').report_action(None, data=data)

    def action_print_xlsx(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/vehicle_rental/rental_report/%s' % (self.id),
            'target': 'new',
        }

    def get_report_lines(self):
        query = """
                       select rent_request.state as state,res_partner.name as customer,
                       rent_request.period as period,fleet_vehicle_model.name as model 
                       from rent_request
                       inner join res_partner
                       on res_partner.id = rent_request.partner_id
                       inner join vehicle_rental
                       on vehicle_rental.id = rent_request.vehicle_id
                       inner join fleet_vehicle
                       on fleet_vehicle.id = vehicle_rental.vehicle_id
                       inner join fleet_vehicle_model
                       on fleet_vehicle_model.id = fleet_vehicle.model_id 
                       """
        if self.vehicle_id:
            query += """where vehicle_rental.id  = %s """ % self.vehicle_id.id
        if self.from_date:
            query += """and rent_request.from_date >= '%s'""" % self.from_date
        if self.to_date:
            query += """and rent_request.to_date <= '%s'""" % self.to_date
        cr = self._cr
        cr.execute(query)
        sql_dict = self._cr.dictfetchall()
        data = {
            'vehicle_name': self.vehicle_id.name,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'sql_data': sql_dict
        }
        return data

