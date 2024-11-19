from odoo import fields, models, api


class SurveySurvey(models.Model):
    """Defining a Exam information."""

    _inherit = "survey.survey"

    is_ete_survey = fields.Boolean()
    school_id = fields.Many2one('school.school', 'School')
    teacher_id = fields.Many2one('school.teacher', 'Teacher')
    teacher_ids = fields.Many2many('school.teacher', string='Teachers')
    class_id = fields.Many2one('school.standard', 'Class')
    standard_id = fields.Many2one('standard.standard', 'Standard')
    academic_year_id = fields.Many2one("academic.year", 'Academic Year', help="Select Academic Year")
    s_exam_id = fields.Many2one("exam.exam", "Examination", help="Select Exam")
    subject_id = fields.Many2one("subject.subject")
    exam_type = fields.Selection([
        ("two", "Two Way Correction"),
        ("four", "Four Way Correction"),
        ("online", "Online")
    ])
    option_count = fields.Char(string="No of options", placeholder="2 or 4", default="2")


class SurveyUserInput(models.Model):
    """Defining a Exam information."""

    _inherit = "survey.user_input"

    class_id = fields.Many2one(related='survey_id.class_id')
    standard_id = fields.Many2one(related='survey_id.standard_id')
    subject_id = fields.Many2one(related='survey_id.subject_id')
    class_store_id = fields.Many2one(related='survey_id.class_id', store=True, readonly=False)
    standard_store_id = fields.Many2one(related='survey_id.standard_id', store=True, readonly=False)
    subject_store_id = fields.Many2one(related='survey_id.subject_id', store=True, readonly=False)


class SurveyUserInputLine(models.Model):
    """Defining a Exam information."""

    _inherit = "survey.user_input.line"

    sub_category_store_id = fields.Many2one(related="question_id.sub_category_id", store=True, readonly=False)
    student_id = fields.Many2one("res.partner", compute="_compute_student_name", store=True)
    subject_store_id = fields.Many2one(related='user_input_id.subject_id', store=True, readonly=False)

    @api.depends("user_input_id")
    def _compute_student_name(self):
        for line in self:
            line.student_id =line.user_input_id.partner_id.id or False


class SurveyQuestion(models.Model):
    """Defining a Subject Category."""

    _inherit = 'survey.question'

    subject_id = fields.Many2one(related='survey_id.subject_id',store=True)
    sub_category_id = fields.Many2one('sub.category',domain=[])
