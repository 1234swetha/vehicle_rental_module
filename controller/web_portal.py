from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class UserPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        Rentrequest = request.env['rent.request']
        if 'rental_count' in counters:
            values['rental_count'] = Rentrequest.search_count([('partner_id', '=', partner.id)])
        return values


    @http.route(['/my/requests'], type='http', auth="user", website=True)
    def request_view(self):
        partner = request.env.user.partner_id
        requests = request.env['rent.request'].sudo().search([('partner_id', '=', partner.id)])
        values = {}
        values.update({
            'partners': partner,
            'requests': requests,
        })
        print(values)
        return request.render("vehicle_rental.portal_my_requests", values)
