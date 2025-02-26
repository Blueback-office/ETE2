
from collections import OrderedDict
from operator import itemgetter
from odoo import http
from odoo.http import request
from odoo.tools import groupby as groupbyelem
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.translate import _
from odoo.exceptions import ValidationError



class WebsiteMyAccount(CustomerPortal):

    def get_domain_my_results(self, user):
        teacher = request.env['school.teacher'].search([('user_id', '=', user.id)],
                                                limit=1)
        if (request.env.user.is_student):
            return [
                ('partner_id.student_id', '=', request.env.user.student_id and request.env.user.student_id.id or False),
            ]
        else:
            standard_ids = []
            if teacher:
                for standard in teacher.sudo().standard_ids:
                    standard_ids.append(standard.id)
            return [
                '|',  
                    ('partner_id.employee_ids.teacher_id', '=', teacher.id if teacher else False), 
                '|', 
                    '&',  
                        ('partner_id.student_id.standard_id', 'in', standard_ids if standard_ids else [False]),
                        ('partner_id.student_id.school_id', '=', teacher.school_id.id if teacher and teacher.school_id else False),  
                    '&','&', 
                        ('teacher_id', '=', teacher.id if teacher else False), 
                        ('teacher_id.standard_ids', 'in', standard_ids if standard_ids else [False]), 
                        ('teacher_id.school_id', '=', teacher.school_id.id if teacher and teacher.school_id else False), 
            ]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        # Leaves = request.env['hr.leave']
        if 'result_count' in counters:
            # values['leave_count'] = Leaves.search_count(self.get_domain_my_leaves(request.env.user)) if Leaves.check_access_rights('read', raise_exception=False) else 0
            values['result_count'] = '1'
        return values
    

    @http.route(['/result/class_infos/<int:standard>'], type='json', auth="public", methods=['POST'], website=True)
    def class_infos(self, standard, **kw):
        standard = request.env['school.standard'].sudo().browse(standard)
        return dict(
            students=[(st.id, st.name) for st in standard.get_result_class_students()],
            subjects=[(sub.id, sub.name) for sub in standard.get_result_class_subjects()],
            surveys=[(sur.id, sur.title) for sur in standard.get_result_class_survey()],
        )
        
    @http.route(['/result', '/result/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_results(self, date_begin=None, date_end=None, sortby=None, filterby=None, groupby='none', page=1, **kw):
        values = self._prepare_portal_layout_values()
        result_input_sudo = request.env['survey.user_input'].sudo()
        domain = self.get_domain_my_results(request.env.user)

        School_obj = request.env['school.school']
        Subject_obj = request.env['subject.subject']
        Survey_obj = request.env['survey.survey']

        # Filter and Sort Options
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'Passed': {'label': _('Passed'), 'domain': [('scoring_success', '=', True)]},
            'Failed': {'label': _('Failed'), 'domain': [('scoring_success', '=', False)]},
        }

        searchbar_sortings = {
            'create_date': {'label': _('Newest'), 'order': 'create_date desc'},
            'partner_id': {'label': _('Name'), 'order': 'partner_id'},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'Exam': {'input': 'Exam', 'label': _('Exam')},
        }

        # Default sortby and filterby
        if not sortby:
            sortby = 'partner_id'
            
        if groupby == 'Exam': 
            order = 'survey_id desc, ' + searchbar_sortings[sortby]['order']
        else:
            order = searchbar_sortings[sortby]['order']

        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
            
        user_teacher = request.env['school.teacher'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        school = School_obj.search([('id', '=', user_teacher.school_id.id)])
        standard = user_teacher.standard_ids
        student = standard.student_ids
        subject = Subject_obj.search([])
        surveys = Survey_obj.search([])
        total_results = result_input_sudo.search_count(domain)
        pager = request.website.pager(
            url='/result',
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'groupby': groupby},
            total=total_results,
            page=page,
            step=self._items_per_page,
        )

        Results = result_input_sudo.search(domain, order=order, limit=self._items_per_page, offset=(page - 1) * self._items_per_page)

        grouped_result = []
        if groupby == 'Exam':
            grouped_result = [result_input_sudo.concat(*g) for k, g in groupbyelem(Results, itemgetter('survey_id'))]
        else:
            grouped_result = [Results] if Results else []

        values.update({
            'date': date_begin,
            'results': Results,
            'schools': school,
            'standards': standard,
            'students': student,
            'subjects': subject,
            'surveys': surveys,
            'grouped_result': grouped_result,
            'page_name': 'result',
            'default_url': '/result',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
            'pager': pager,
        })

        return request.render("ete_portal.portal_my_result_details", values)

    @http.route('/get_survey_data', type='json', auth='user')
    def get_survey_data(self, survey_id):
        if not survey_id:
            raise ValidationError("Survey ID is required.")

        survey = http.request.env['survey.survey'].sudo().search([('id', '=', int(survey_id))], limit=1)

        if not survey:
            raise ValidationError("Survey not found.")

        question_and_page_data = {}
        for question_and_page in survey.question_and_page_ids:
            question_and_page_data[str(question_and_page.sequence)] = {
                'title': question_and_page.title,
                'question_type': question_and_page.question_type,
                'suggested_answer_ids': [answer.value for answer in question_and_page.suggested_answer_ids]
                # 'suggested_answer_ids': question_and_page.suggested_answer_ids.ids
                # Add other fields as needed
            }

        return {
            'question_and_page_data': question_and_page_data,
            'Survey': {
                'id': survey.id,
                'name': survey.title,
                'option_count': survey.option_count
                # Add other survey fields as needed
            }
            # Add other fields as needed
        }
