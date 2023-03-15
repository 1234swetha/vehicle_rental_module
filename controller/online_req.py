from odoo import http
from odoo.http import request


class WebsiteForm(http.Controller):
    @http.route(['/rent_request'], type='http', auth="user", website=True)
    def request(self):
        partners = request.env['res.partner'].sudo().search([])
        vehicle_id = request.env['vehicle.rental'].sudo().search([('state', '=', 'available')])
        charge_id = request.env['rent.charge'].sudo().search([])
        values = {}
        values.update({
            'partners': partners,
            'vehicle': vehicle_id,
            'charge': charge_id
        })
        return request.render("vehicle_rental.online_req_form", values)

    @http.route(['/rent_request/submit'], type='http', auth="user", website=True)
    def submit(self, **kwargs):
        request.env['rent.request'].sudo().create([{
            'partner_id': kwargs.get('partner_id'),
            'vehicle_id': kwargs.get('vehicle_id'),
            'from_date': kwargs.get('from_date'),
            'charge_id': int(kwargs.get('charge_id')),
        }])
        return request.render("vehicle_rental.rent_req_successful")

    @http.route(['/rent_request/create'], type='http', auth="user", website=True)
    def create(self):
        return request.render("vehicle_rental.online_create_user_form")

    @http.route(['/rent_request/create/submit'], type='http', auth="user", website=True)
    def create_user(self, **kwargs):
        name = kwargs.get('name')
        address = kwargs.get('address')
        phone = kwargs.get('phone')
        email = kwargs.get('email')
        request.env['res.partner'].sudo().create({
            'name': name,
            'street': address,
            'phone': phone,
            'email': email
        })
        return request.render("vehicle_rental.rent_req_successful")
