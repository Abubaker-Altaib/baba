from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from datetime import date, datetime
import operator
from dateutil.relativedelta import relativedelta

def gregorian_to_hijri(self, year, month, day):
    year = '%04d'%int(year)
    month = '%02d'%int(month)
    day = '%02d'%int(day)
        
    dates_ids = self.env['date.log'].search([('g_year', '=', year),('g_month', '=', month),('g_day', '=', day)])
    h_date = dates_ids and dates_ids[0]

    if h_date:
        return {
            'year': h_date.h_year,
            'month': h_date.h_month,
            'day': h_date.h_day,
        }
    
    return False

def gregorian_to_hijri(self, g_date):
    year = '%04d'%int(g_date.year)
    month = '%02d'%int(g_date.month)
    day = '%02d'%int(g_date.day)
        
    dates_ids = self.env['date.log'].search([('g_year', '=', year),('g_month', '=', month),('g_day', '=', day)])
    h_date = dates_ids and dates_ids[0]

    if h_date:
        return {
            'year': h_date.h_year,
            'month': h_date.h_month,
            'day': h_date.h_day,
        }
    
    return False

def hijri_to_gregorian(self, year, month, day):
    year = '%04d'%int(year)
    month = '%02d'%int(month)
    day = '%02d'%int(day)
        
    dates_ids = self.env['date.log'].search([('h_year', '=', year),('h_month', '=', month),('h_day', '=', day)])
    g_date = dates_ids and dates_ids[0]

    if g_date:
        c_date = date(year=int(g_date.g_year), month=int(g_date.g_month), day=int(g_date.g_day))
        c_date = date.strftime(c_date, DATE_FORMAT)
        c_date = datetime.strptime(c_date, DATE_FORMAT).date()

        return c_date
    
    return False


def hijri_to_gregorian(self, h_date):
    year = '%04d'%int(h_date['year'])
    month = '%02d'%int(h_date['month'])
    day = '%02d'%int(h_date['day'])
        
    dates_ids = self.env['date.log'].search([('h_year', '=', year),('h_month', '=', month),('h_day', '=', day)])
    g_date = dates_ids and dates_ids[0]

    if g_date:
        c_date = date(year=int(g_date.g_year), month=int(g_date.g_month), day=int(g_date.g_day))
        c_date = date.strftime(c_date, DATE_FORMAT)
        c_date = datetime.strptime(c_date, DATE_FORMAT).date()

        return c_date
    
    return False

def hijri_next_month(self, h_date, delta = 0, interval = 1):
    count = 0
    while count < interval:
        year = int(h_date['year'])
        month = int(h_date['month'])
        day = int(h_date['day'])
        if month != 12:
            month += 1
        elif month == 12:
            month = 1
            year += 1

        year = '%04d'%int(year)
        month = '%02d'%int(month)
        day = '%02d'%int(day)
        dates_ids = self.env['date.log'].search([('h_year', '=', year),('h_month', '=', month),('h_day', '=', day)])
        h_date = dates_ids and dates_ids[0]
        if not h_date:
            day = int(day)
            day -= 1
            day = '%02d'%int(day)
        
        dates_ids = self.env['date.log'].search([('h_year', '=', year),('h_month', '=', month),('h_day', '=', day)])
        h_date = dates_ids and dates_ids[0]

        h_date = {
            'year': h_date.h_year,
            'month': h_date.h_month,
            'day': h_date.h_day,
        }


        
        count += 1
    if h_date:
        dates_ids = self.env['date.log'].search([('h_year', '=', h_date['year']),('h_month', '=', h_date['month']),('h_day', '=', h_date['day'])])
        h_date = dates_ids and dates_ids[0]
        new_id = h_date.id - delta
        dates_ids = self.env['date.log'].search([('id', '=', new_id)])
        h_date = dates_ids and dates_ids[0]
        h_date = {
            'year': h_date.h_year,
            'month': h_date.h_month,
            'day': h_date.h_day,
        }

        return h_date
    
    return False



class date_log(models.Model):
    _name = 'date.log'

    g_date = fields.Char('Gregorian Date')
    h_date = fields.Char('Hijri Date')

    g_day = fields.Char('Gregorian Day')
    g_month = fields.Char('Gregorian Month')
    g_year = fields.Char('Gregorian Year')

    h_day = fields.Char('Hijri Day')
    h_month = fields.Char('Hijri Month')
    h_year = fields.Char('Hijri Year')

    @api.multi
    def get_all_dates_dict(self):
        dates_ids = self.search([])

        if dates_ids:
            data = {}
            for x in dates_ids:
                data[str(int(x.h_year))+'-'+str(int(x.h_month))+'-'+str(int(x.h_day))+'h'] = x.id
                data[str(int(x.g_year))+'-'+str(int(x.g_month))+'-'+str(int(x.g_day))+'g'] = x.id

            return data
        return False

    @api.multi
    def from_hijri_to_gregorian(self, h_year, h_month, h_day):
        h_year = '%04d'%int(h_year)
        h_month = '%02d'%int(h_month)
        h_day = '%02d'%int(h_day)

        dates_ids = self.search([('h_year', '=', h_year),('h_month', '=', h_month),('h_day', '=', h_day)])
        g_date = dates_ids and dates_ids[0]


        if g_date:
            return {
                'year': g_date.g_year,
                'month': g_date.g_month,
                'day': g_date.g_day,
            }
        
        return False

    @api.multi
    def from_gregorian_to_hijri(self, g_year, g_month, g_day):
        g_year = '%04d'%int(g_year)
        g_month = '%02d'%int(g_month)
        g_day = '%02d'%int(g_day)

        
        dates_ids = self.search([('g_year', '=', g_year),('g_month', '=', g_month),('g_day', '=', g_day)])
        h_date = dates_ids and dates_ids[0]


        if h_date:
            return {
                'year': h_date.h_year,
                'month': h_date.h_month,
                'day': h_date.h_day,
            }
        
        return False


class date_log_milestone(models.Model):
    _name = 'date.log.milestone'

    g_day = fields.Char('Gregorian Day')
    g_month = fields.Char('Gregorian Month')
    g_year = fields.Char('Gregorian Year')

    place = fields.Char('|', default='|')

    h_day = fields.Char('Hijri Day')
    h_month = fields.Char('Hijri Month')
    h_year = fields.Char('Hijri Year')

    def get_next(self, str_hjry_date):
        if str_hjry_date:
            hjry_year = int(str_hjry_date.split('-')[0])
            hjry_month = int(str_hjry_date.split('-')[1])
            hjry_day = int(str_hjry_date.split('-')[2])

            if hjry_day < 30:
                hjry_day += 1
            elif hjry_day == 30 and hjry_month != 12:
                hjry_day = 1
                hjry_month += 1
            elif hjry_day == 30 and hjry_month == 12:
                hjry_day = 1
                hjry_month = 1
                hjry_year += 1
            return "%04d-%02d-%02d" % (int(hjry_year), int(hjry_month), int(hjry_day))

    # @api.model
    def update_log(self):
        self.env['date.log'].search([]).unlink()
        milestones = self.search([('id', '!=', self.id)])
        self.unlink()
        milestones_dates = {}
        for milestone in milestones:
            c_date = date(year=int(milestone.g_year), month=int(milestone.g_month), day=int(milestone.g_day))
            c_date = date.strftime(c_date, DATE_FORMAT)
            c_date = datetime.strptime(c_date, DATE_FORMAT).date()
            milestones_dates[c_date] = "%04d-%02d-%02d" % (int(milestone.h_year),
                                                           int(milestone.h_month), int(milestone.h_day))

        all_dates = []
        if milestones_dates:
            milestones_dates = dict(sorted(milestones_dates.items(), key=operator.itemgetter(0)))

            keys = sorted(list(milestones_dates.keys()))

            first_date = keys[0]
            last_date = keys[-1]
            start_date = first_date

            end_date = last_date

            end_date += relativedelta(years=10)

            c_hjry = ''
            while start_date <= end_date:
                if start_date in milestones_dates:
                    c_hjry = milestones_dates[start_date]
                else:
                    c_hjry = self.get_next(c_hjry)

                #all_dates[start_date] = c_hjry

                self.env['date.log'].create({
                    'g_date': str(start_date),
                    'h_date': c_hjry,
                    'h_day':c_hjry.split('-')[2],
                    'h_month':c_hjry.split('-')[1],
                    'h_year':c_hjry.split('-')[0],
                    'g_day': str('%02d'%start_date.day),
                    'g_month': str('%02d'%start_date.month),
                    'g_year': str('%04d'%start_date.year),
                })
                start_date += relativedelta(days=1)

        self.unlink()
