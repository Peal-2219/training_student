from odoo import http

class TrainingStudent(http.Controller):
    @http.route('/students', type='http', auth='public', website=True)
    def students_page(self, **kw):
        students = http.request.env['training.student'].sudo().search([])
        return http.request.render('training_student.student_website_page', {
            'students': students,
        })
