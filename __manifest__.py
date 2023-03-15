{
    'name': 'Vehicle Rental',
    'version': '16.0.1.0.0',
    'sequence': 1,
    'depends': [
        'fleet',
        'mail',
        'account',
        'website'
      ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/rental_report_wizard_views.xml',
        'report/vehicle_rental_report.xml',
        'views/rent_vehicle_views.xml',
        'views/rent_request_views.xml',
        'views/rent_fleet_inherit_views.xml',
        'views/rent_invoicing_inherit_views.xml',
        'views/rent_charge_views.xml',
        'views/rent_vehicle_menus.xml',
        'views/online_rent_request.xml',
        'views/online_create_user.xml',
        'views/rent_req_successful.xml',
        'views/website_preview.xml',
        'data/online_rental_req.xml'
    ],
    'assets': {
         'web.assets_frontend': [
               'vehicle_rental/static/src/js/online_req.js'
         ]
    },
    'installable': True,
    'application': True,
    'auto_install': False
}

