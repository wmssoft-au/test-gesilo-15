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
from odoo.exceptions import Warning, UserError,ValidationError
from encodings import ptcp154

from dateutil.relativedelta import relativedelta


class DoDateFinder(models.TransientModel):
    _name = "delivery.date.finder"
    _description="Model for finding the delivery order date"
    
                
    @api.model
    def default_get(self,fields):
        res = super(DoDateFinder, self).default_get(fields)
        order_pool = self.env['sale.order']
        if self._context.get('active_ids') and self._context.get('active_model') =='sale.order':
            order_obj = order_pool.search([('id','in',self._context.get('active_ids'))],limit=1)
            if order_obj:
                res['order_id'] = order_obj.id
                res['order_date'] = order_obj.date_order
        return res
   
    order_id = fields.Many2one('sale.order',string="Order #")
    order_date = fields.Date(string="Order Date")
    expected_do_date = fields.Date(string="Expected Delivery Date")
    build_by_date = fields.Date(string="Build By Date")
   
   
   

    
            

    

    
    