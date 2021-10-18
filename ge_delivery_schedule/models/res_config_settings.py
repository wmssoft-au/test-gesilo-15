# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo ERP ,Open Source Management Solution
#    Copyright (C)2021-2022
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

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    monthly_target = fields.Integer(string="Weekly Target Schedules")
    

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    
    set_monthly_target = fields.Boolean(string="Set Weekly Schedule Target")
    monthly_target = fields.Integer(related='company_id.monthly_target', readonly=False)

   
