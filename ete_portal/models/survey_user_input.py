# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
# from turtle import done


class SurveyUserInput(models.Model):

    _inherit = "survey.user_input"

    @api.model
    def create_portal_result(self, values):
        user = self.env.user
        self = self.sudo()
        if not (values['class_id'] and values['school_id'] and values['student_id'] and values['subject_id'] and values['survey_id']):
            return {
                'errors': _('All fields are required!')
            }
        if values['student_id']:
            student_id = self.env['student.student'].sudo().browse(values['student_id']).partner_id
        lst = []
        for key,value in values.get('question_id').items():
            domain = []
            if int(value) == 1:
                domain = [('question_id', '=', int(key)), ('is_correct', '=', True)]
            else:
                domain = [('question_id', '=', int(key))]
            question_answer = self.env['survey.question.answer'].search(domain)
            vals = [0, 0, {
                'question_id': key,
                'display_name': value,
                'suggested_answer_id': question_answer and question_answer[0].id,
                'answer_type': 'suggestion',
            }]
            lst.append(vals)
        values = {
            'survey_id': values['survey_id'],
            'partner_id': student_id.id,
            'state': 'done',
            'user_input_line_ids': lst
        }
        survey_user_input = self.create(values)
        return {
            'id': survey_user_input.id,
        }