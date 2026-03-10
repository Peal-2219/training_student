from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, timedelta
import datetime as dt
from markupsafe import Markup


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

    # Tracks when the Confirm button was clicked
    confirmation_date = fields.Datetime(
        string="Confirmation Date",
        readonly=True,
        copy=False,
    )

    # Prevents duplicate emails from the cron
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

    def action_confirm(self):
        """Set state to confirmed and record the confirmation timestamp.
        A scheduled cron job will send the email after a set delay.
        """
        for rec in self:
            rec.write({
                'state': 'confirmed',
                'confirmation_date': fields.Datetime.now(),
                'confirmation_email_sent': False,
            })
            # Notify in chatter that confirmation is pending email
            rec.message_post(
                body=Markup("""
                    <div style="font-family:Arial,sans-serif;font-size:14px;">
                        <p style="margin:0 0 8px;">&#9989; <strong>Admission Confirmed</strong></p>
                        <table style="border-collapse:collapse;width:100%;max-width:400px;">
                            <tr>
                                <td style="padding:4px 10px 4px 0;color:#555;">Student</td>
                                <td style="padding:4px 0;"><strong>{name}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding:4px 10px 4px 0;color:#555;">Email</td>
                                <td style="padding:4px 0;">{email}</td>
                            </tr>
                        </table>
                        <p style="margin:10px 0 0;color:#888;font-size:12px;">
                            &#128231; A confirmation email will be sent to this address shortly.
                        </p>
                    </div>
                """).format(name=rec.name, email=rec.email),
                subtype_xmlid='mail.mt_note',
            )

    @api.model
    def cron_send_confirmation_email(self):
        """Scheduled action: send confirmation email to students who were
        confirmed at least EMAIL_DELAY_MINUTES ago and haven't received it yet.
        Configure the cron interval to match the desired delay (e.g. 5 min).
        """
        EMAIL_DELAY_MINUTES = 5  # wait 5 minutes after confirmation before sending

        send_before = fields.Datetime.now() - dt.timedelta(minutes=EMAIL_DELAY_MINUTES)

        pending_students = self.search([
            ('state', '=', 'confirmed'),
            ('confirmation_email_sent', '=', False),
            ('confirmation_date', '!=', False),
            ('confirmation_date', '<=', send_before),
        ])

        template = self.env.ref(
            'training_student.student_email_template',
            raise_if_not_found=False
        )

        for student in pending_students:
            # Determine recipient email: use student.email field
            recipient_email = student.email
            if not recipient_email:
                continue

            if template:
                # Send the email using the template; email_to in template
                # already points to ${object.email} so it uses student.email
                template.send_mail(
                    student.id,
                    force_send=True,
                    email_layout_xmlid='mail.mail_notification_light',
                )

            # Mark email as sent
            student.confirmation_email_sent = True

            # Log in the chatter
            student.message_post(
                body=Markup("""
                    <div style="font-family:Arial,sans-serif;font-size:14px;">
                        <p style="margin:0 0 8px;">&#128231; <strong>Confirmation Email Sent</strong></p>
                        <table style="border-collapse:collapse;width:100%;max-width:400px;">
                            <tr>
                                <td style="padding:4px 10px 4px 0;color:#555;">Student</td>
                                <td style="padding:4px 0;"><strong>{name}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding:4px 10px 4px 0;color:#555;">Sent To</td>
                                <td style="padding:4px 0;">{email}</td>
                            </tr>
                        </table>
                    </div>
                """).format(name=student.name, email=recipient_email),
                subject="Admission Confirmed - {}".format(student.name),
                message_type='email',
                subtype_xmlid='mail.mt_comment',
            )
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

    def write(self, vals):
        if 'course_id' in vals:
            if not self.env.user.has_group('training_student.group_training_manager'):
                raise UserError("Only Manager can assign course.")
        return super().write(vals)

    @api.model
    def cron_auto_update_student_state(self):

        today = date.today()

        students = self.search([])

        for student in students:

            if student.state == 'draft' and student.admission_date:
                if student.admission_date <= today - timedelta(days=3):
                    student.state = 'cancelled'

            if student.state == 'confirmed' and student.admission_date:
                if student.admission_date <= today - timedelta(days=7):
                    student.state = 'approved'