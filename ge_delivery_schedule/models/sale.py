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
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError,Warning,AccessError
import datetime
from datetime import datetime,date

from dateutil.relativedelta import relativedelta    
       
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    expected_do_date = fields.Date(string="Expected Delivery Date",copy=False)
    build_by_date = fields.Date(string="Build By Date",copy=False)
    scheduled = fields.Boolean(string="Scheduled",default=False,copy=False)
    
    def find_delivery_slot(self):
        estimated_delivery_pool = self.env['estimated.delivery']
        for rec in self:
            expected_do_date = False
            if rec.date_order:
                expected_do_date = rec.date_order + relativedelta(days=15)
                delivery_found = estimated_delivery_pool.search([('date','=',expected_do_date),('state','=','Free')],limit=1)
                if delivery_found:
                    delivery_found.name = 'Automatic Allocation by System',
                    delivery_found.order_id = rec.id
                    delivery_found.color = 9
                    delivery_found.state='Booked'
                else:
                    no_of_days = 90
                    default_day = 15
                    day = default_day + 1 
                    while day < no_of_days:
                        expected_do_date = rec.date_order + relativedelta(days=day)
                        delivery_found = estimated_delivery_pool.search([('date','=',expected_do_date),('state','=','Free')],limit=1)
                        if delivery_found:
                            delivery_found.name = 'Automatic Allocation by System',
                            delivery_found.order_id = rec.id
                            delivery_found.color = 9
                            delivery_found.state='Booked'
                            break
                        else:
                              day += 1
                
               
            
    def open_availablity_calender(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ge_delivery_schedule.action_estimated_delivery")
        ctx = self._context.copy()
        ctx.update({
            'default_state': 'Booked',
            'default_order_id': self.id,
            'default_order_date':self.date_order,
            'default_user_id':self.env.user.id
        })
        action['context'] = ctx
        return action
                    
    