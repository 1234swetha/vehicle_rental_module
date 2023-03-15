from odoo import http
from odoo.http import content_disposition, request
from odoo.tools.misc import xlsxwriter
import io


class RentalExcelReportController(http.Controller):
    @http.route([
        '/vehicle_rental/rental_report/<model("rental.report.wizard"):report_id>',
    ], type='http', auth="user", csrf=False)
    def get_rental_excel_report(self, report_id=None, **args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('rental_report_wizard' + '.xlsx'))
            ]
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        report_lines = report_id.get_report_lines()
        sql_data = report_lines.get('sql_data')
        sheet = workbook.add_worksheet()
        head = workbook.add_format({'align': 'center', 'bold': True})
        text = workbook.add_format({'align': 'center'})
        sheet.merge_range('A2:E1', 'VEHICLE RENTAL REPORT', head)
        if report_lines.get('vehicle_name'):
            sheet.merge_range('A4:E4', 'Vehicle Name:' + report_lines.get('vehicle_name'))
        if report_lines.get('from_date'):
            sheet.merge_range('A5:E5', 'From Date - ' + str(report_lines.get('from_date')))
        if report_lines.get('to_date'):
            sheet.merge_range('A6:E6', 'To Date - ' + str(report_lines.get('to_date')))
        sheet.write(7, 0, 'Sl no.', head)
        sheet.write(7, 1, 'Customer', head)
        sheet.write(7, 2, 'Period', head)
        sheet.write(7, 3, 'Model', head)
        sheet.write(7, 4, 'State', head)
        row = 8
        number = 1
        for line in sql_data:
            sheet.set_row(row, 20)
            sheet.write(row, 0, number, text)
            sheet.write(row, 1, line['customer'], text)
            sheet.write(row, 2, line['period'], text)
            sheet.write(row, 3, line['model'], text)
            sheet.write(row, 4, line['state'], text)
            row += 1
            number += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response
