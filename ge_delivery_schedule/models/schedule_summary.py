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
from datetime import datetime,date,timedelta

from collections import OrderedDict
import datetime
from calendar import monthrange
import calendar
from math import ceil
       
class Schedule_summary(models.Model):
    _name = 'schedule.summary'
    _description = "Model for storing the schedulesummary"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    def _compute_total(self):
        for rec in self:
            if rec.summary_line_ids:
                weekly_target = self.company_id.monthly_target or 6
                total_units_to_be = 0.0
                for line in rec.summary_line_ids:
                    total_units_to_be += line.unit_to_be
                if weekly_target > 0.0:
                    rec.no_of_week_per_target = (total_units_to_be/weekly_target)
                    rec.no_of_week_per_leadtime =  (total_units_to_be/weekly_target) +2
                else:
                    rec.no_of_week_per_target = 0.0
                    rec.no_of_week_per_leadtime = 0.0
                    
            else:
                rec.no_of_week_per_target = 0.0
                rec.no_of_week_per_leadtime = 0.0
                
    
    processing_year = fields.Char(string="Year")
    name = fields.Char(string="Remarks")
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company)
    color = fields.Integer(string="Color",default=10)
    summary_line_ids = fields.One2many('schedule.summary.line','schedule_summary_id',string="Details")
    weekly_target = fields.Float(string="Weekly Target",default=lambda self: self.env.company.monthly_target or 0.0)
    no_of_week_per_target = fields.Float(string="No of weeks to complete Target",compute="_compute_total")
    no_of_week_per_leadtime = fields.Float(string="No of weeks lead time ")
    no_of_silos_concrete = fields.Float(string="No of silos not built(Concreat Ready)")    
    state = fields.Selection([('draft','Draft'),('progress','Progress'),('closed','Closed')],default='draft',string="Status",required=True,tracking=True)
    
    

    def week_of_month(self,dt):
        """ Returns the week of the month for the specified date.
        """
    
        first_day = dt.replace(day=1)
    
        dom = dt.day
        adjusted_dom = dom + first_day.weekday()
    
        return int(ceil(adjusted_dom/7.0))
    
    def generate_data(self):
        schedule_pool = self.env['estimated.delivery']
        order_pool = self.env['sale.order']
        for rec in self:
            if len(rec.processing_year) != 4:
                raise ValidationError(_("Please enter valid year!"))
            if rec.summary_line_ids:
                rec.summary_line_ids.unlink()
            months = [datetime.date(2000, m, 1).strftime('%b') for m in range(1, 13)]
            digit = 1
            weekly_target = 0.0
            if not rec.company_id.monthly_target:
                raise ValidationError(_("Please set the Weekly Target Schedules in settings"))
            else:
                weekly_target = self.company_id.monthly_target
            for month in months:
                month_days = monthrange(int(rec.processing_year), digit)[1]# need to add weeek days only
                total_weeks = month_days/7
                today = fields.Date.today()
                current_month = int(today.strftime('%m'))
                if current_month == digit:
                    week_left = self.week_of_month(today)
                    week_left = total_weeks - week_left
                else:
                    week_left = total_weeks
                    
                first_day_month = datetime.datetime.strptime(str(str(rec.processing_year)+'-'+str(digit)+'-01'),"%Y-%m-%d").date()
                last_day = end_date_of_month = datetime.datetime(first_day_month.year, first_day_month.month, calendar.mdays[first_day_month.month])
                schedules_count = schedule_pool.search([('date','>=',first_day_month.strftime("%Y-%m-%d")),
                                                        ('date','<=',last_day.strftime("%Y-%m-%d")),
                                                        ('order_id','!=',False),
                                                        ('state','=','Booked')])
                
                total_orders = order_pool.search([('date_order','>=',first_day_month.strftime("%Y-%m-%d")),
                                                        ('date_order','<=',last_day.strftime("%Y-%m-%d")),
                                                        ('state','=','sale')])
                total_units = 0.0
                for item in total_orders:
                    if item.order_line:
                        for line in item.order_line:
                            total_units += line.product_uom_qty
                unit_week = unit_over = 0.0
                if weekly_target > 0.0 and total_orders != 0.0:
                    unit_week = total_units/weekly_target
                    unit_over = (weekly_target * week_left) - total_units
                vals = {
                    'months_name':month,
                    'month_in_digit':digit,
                    'schedule_summary_id':rec.id,
                    'total_weeks':total_weeks,
                    'weekly_target':weekly_target,
                    'week_left':week_left,
                    'silo_scheduled':len(schedules_count) or 0.0,
                    'silo_to_be':len(total_orders) or 0.0,
                    'unit_to_be':total_units or 0.0,
                    'unit_week':unit_week,
                    'unit_over':unit_over,
                    }
                digit +=1
                line_id = self.env['schedule.summary.line'].create(vals)
                rec.state='progress'
                
        return True
               
    def button_close(self):
        for rec in self:
            rec.state = 'closed'
            
    def unlink(self):
        for rec in self:
            if rec.state == 'closed':
                raise ValidationError(_("You cannot delete the records in closed status."))
            
        return super(Schedule_summary, self).unlink()
           
class ScheduleSummaryLine(models.Model):
    _name = 'schedule.summary.line'
    _description = "Model for storing the schedule summary lines"

    
    schedule_summary_id = fields.Many2one('schedule.summary',string="Summary#")
    months_name = fields.Selection([('Jan','January'),
                               ('Feb','February'),
                               ('Mar','March'),
                               ('Apr','April'),
                               ('May','May'),
                               ('Jun','June'),
                               ('Jul','July'),
                               ('Aug','August'),
                               ('Sep','September'),
                               ('Oct','October'),
                               ('Nov','November'),
                               ('Dec','December'),],string="Months")
    month_in_digit = fields.Char(string="Month")
    total_weeks = fields.Integer(string="Total Weeks")
    weekly_target = fields.Integer(string="Weekly Target",default=6)
    week_left = fields.Integer(string="Week Left in Month")
    silo_scheduled = fields.Integer(string="Silos in Schedule")
    silo_to_be = fields.Integer(string="Silos to be build in Month")
    unit_to_be = fields.Float(string="Units to Be Build")
    unit_week = fields.Float(string="Units/Week")
    unit_over = fields.Float(string="Units Spare/Overbooked")
    
    
    
    
    
    