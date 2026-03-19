from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, timedelta
import datetime as dt
from markupsafe import Markup
import io
import base64
import xlsxwriter

from odoo import models, fields

# class SchoolClass(models.Model):
#     _name = 'school.class'
#
#     name = fields.Char(string="Class Name")
#     student_ids = fields.One2many(
#         'school.student',
#         'class_id',
#         string="Students",
#         ondelete='cascade'
#     )
class TrainingStudent(models.Model):
    _name = 'training.student'
    _description = 'Training Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True)

    name = fields.Char(required=True, tracking=True)
    email = fields.Char(required=True, tracking=True)
    dob = fields.Date(tracking=True)

    student_age = fields.Integer(
        compute="_compute_student_age",
        store=True
    )

    admission_date = fields.Date()
    active = fields.Boolean(default=True)

    confirmation_date = fields.Datetime(
        string="Confirmation Date",
        readonly=True,
        copy=False,
    )

    confirmation_email_sent = fields.Boolean(
        string="Confirmation Email Sent",
        default=False,
        copy=False,
    )

    user_id = fields.Many2one(
        'res.users',
        string="Assigned User",
        default=lambda self: self.env.user,
        tracking=True
    )

    course_id = fields.Many2one(
        'training.course',
        string="Course",
        tracking=True
    )

    enrollment_ids = fields.One2many(
        'training.enrollment',
        'student_id',
        string="Enrollments"
    )

    # SMART BUTTON COUNT
    enrollment_count = fields.Integer(
        compute="_compute_enrollment_count"
    )

    def _compute_enrollment_count(self):
        for rec in self:
            rec.enrollment_count = len(rec.enrollment_ids)

    # SMART BUTTON ACTION
    def action_view_enrollments(self):
        return {
            'name': 'Enrollments',
            'type': 'ir.actions.act_window',
            'res_model': 'training.enrollment',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id}
        }

    # ================================
    # EXCEL EXPORT
    # ================================
    def action_export_students_xlsx(self):

        students = self.search([])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet("Students")

        headers = [
            "Name",
            "Email",
            "Age",
            "Course",
            "State",
            "Admission Date"
        ]

        for col, header in enumerate(headers):
            sheet.write(0, col, header)

        row = 1

        for student in students:
            sheet.write(row, 0, student.name or '')
            sheet.write(row, 1, student.email or '')
            sheet.write(row, 2, student.student_age or '')
            sheet.write(row, 3, student.course_id.name or '')
            sheet.write(row, 4, student.state or '')
            sheet.write(row, 5, str(student.admission_date or ''))

            row += 1

        workbook.close()

        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': 'students.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }

    # ================================
    # EXISTING METHODS (UNCHANGED)
    # ================================

    def action_confirm(self):
        for rec in self:
            rec.write({
                'state': 'confirmed',
                'confirmation_date': fields.Datetime.now(),
                'confirmation_email_sent': False,
            })

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    @api.depends('dob')
    def _compute_student_age(self):
        for rec in self:
            if rec.dob:
                today = date.today()
                rec.student_age = today.year - rec.dob.year - (
                    (today.month, today.day) < (rec.dob.month, rec.dob.day)
                )
            else:
                rec.student_age = 0