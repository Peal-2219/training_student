# -*- coding: utf-8 -*-
# from odoo import http


# class TrainingStudent(http.Controller):
#     @http.route('/training_student/training_student', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/training_student/training_student/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('training_student.listing', {
#             'root': '/training_student/training_student',
#             'objects': http.request.env['training_student.training_student'].search([]),
#         })

#     @http.route('/training_student/training_student/objects/<model("training_student.training_student"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('training_student.object', {
#             'object': obj
#         })

