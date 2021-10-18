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
from datetime import datetime,date,timedelta

from dateutil.relativedelta import relativedelta       
       
class EstimatedDelivery(models.Model):
    _name = 'estimated.delivery'
    _description = "Model for storing the delivery schedule of sales orders"
    _rec_name = 'state'
    
    name = fields.Char(string="Remarks")
    date = fields.Date(string="Date Booked",required=True)
    date_production = fields.Date(string="Build Date")
    order_id = fields.Many2one('sale.order',string="Order ID")
    order_date = fields.Date(string="Order Date")
    user_id = fields.Many2one('res.users',string="Scheduled By")
    state = fields.Selection([('Free','Free'),('Booked','Booked')],default='Free',string="Status",required=True)
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company)
    color = fields.Integer(string="Color",default=10)
    
    @api.onchange('order_id')
    def onchange_order_id(self):
        if self.order_id:
            self.order_date = self.order_id.date_order
        else:
            self.order_date = False

    
    @api.onchange('state')
    def onchange_state(self):
        if self.state:
            if self.state == 'Booked':
                self.color = 9
                
    @api.onchange('date')
    def onchange_date_booked(self):
        if self.date and self.order_id:
            date_production = self.date - relativedelta(days=14)
            self.date_production = date_production
            formatted_date = date_production.strftime("%Y-%m-%d")
            formatted_date = datetime.strptime(formatted_date,"%Y-%m-%d")
            if formatted_date < self.order_id.date_order:
                raise ValidationError(_("Build by date should be greater than order date!"))
    
    def name_get(self):
        result = []
        for rec in self:
            name = rec.state
            if rec.order_id:
                name = rec.order_id.name + '-' + rec.state
            result.append((rec.id, name))
        return result
    
    def generate_days(self):
        
        sdate = date(2021, 1, 1)   # start date
        edate = date(2025, 12, 31)   # end date
        
        delta = edate - sdate       # as timedelta
        
        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            self.env['estimated.delivery'].create({'date':day,'state':'Free','color':10})
            
    
    def write(self,vals):
        if vals.get('date'):
            date_production = datetime.strptime(vals.get('date'),'%Y-%m-%d 00:00:00') - relativedelta(days=14)
            vals.update({'date_production':date_production})
            if self.order_id:
                if date_production < self.order_id.date_order:
                    raise ValidationError(_("Build by date should be greater than order date!"))
                self.order_id.expected_do_date = vals.get('date')
                self.order_id.build_by_date = date_production
                self.order_id.scheduled = True
                comment = "Schedule changed Successfully."
                self.order_id.message_post(body=_('%s') % (comment))
        return  super(EstimatedDelivery, self).write(vals)
    
    @api.model
    def create(self,vals):
        created_id = models.Model.create(self,vals)
        if created_id.order_id.expected_do_date:
            raise ValidationError(_("Schedule already created for this sale order!"))
        if created_id.order_id:
            created_id.order_id.expected_do_date = created_id.date
            created_id.order_id.build_by_date = created_id.date_production
            created_id.order_id.scheduled = True
            comment = "Schedule Created Successfully."
            created_id.order_id.message_post(body=_('%s') % (comment))
        return created_id
        
        
    def unlink(self):
        for rec in self:
            if rec.order_id and rec.order_id.expected_do_date:
                rec.order_id.expected_do_date = False
                rec.order_id.build_by_date = False
                rec.order_id.scheduled = False
                comment = "Schedule deleted Successfully."
                rec.order_id.message_post(body=_('%s') % (comment))
        return super(EstimatedDelivery, self).unlink()
    
    
    
    