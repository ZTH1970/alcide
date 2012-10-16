import datetime

from django.shortcuts import redirect

def redirect_today(request, service):
    '''If not date is given we redirect on the agenda for today'''
    return redirect('agenda', date=datetime.date.today().strftime('%Y-%m-%d'),
            service=service)
