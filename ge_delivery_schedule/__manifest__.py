# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo ERP ,Open Source Management Solution
#    Copyright (C) 2021-2022
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Ge Delivery Schedule',
    'version': '15.0.1.0.0',
    'summary': """Custom Module for Handling the delivery schedule""",
    'description': 'Custom Module for Handling the delivery schedule',
    'author': 'WMSSoft Pty Ltd',
    'company': 'WMSSoft Pty Ltd',
    'maintainer': 'WMSSoft Pty Ltd',
    'website': "https://www.wmssoft.com.au/",
    'depends': ['sale','stock','web_gantt'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/do_date_finder_wizard_view.xml',
        'views/res_config_settings.xml',
        'views/estimated_delivery_view.xml',
        'views/schedule_summary_view.xml',
        'views/sale_view.xml',
        
    ],
   
    'installable': True,
    'auto_install': False,
    'application': False,
}
