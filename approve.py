#!/usr/bin/env python2.6


import os
#for django 1.7:
#import django
import sys
import getpass

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "symper.settings")
    from django.conf import settings
    
from boto.mturk import connection, price
from comparisons import models
import datetime
from django.utils import timezone

if getpass.getuser() == "dreitter":
    from credentials.reitter import *
else:
    from credentials.cole import *

#host = "mechanicalturk.sandbox.amazonaws.com"
host = "mechanicalturk.amazonaws.com"

conn = connection.MTurkConnection(aws_access_key_id=access, aws_secret_access_key=secret, host=host)

dry_run = True
if "-r" in sys.argv:
    dry_run = False 
total_bonus=0.0
total_appr=0

def print_totals():
    global total_appr
    global total_bonus
    print(str(total_appr)+" workers approved.")
    print("Total bonus: $"+str(total_bonus))
    total_bonus = 0
    total_appr = 0

def approve_by_worker(worker):
	global conn
	global dry_run
	global total_bonus
        global total_appr
	payout = models.Payout.objects.get(pk=worker)
	user = models.PUser.objects.get(pk=worker)
	paid_check = models.Paid.objects.filter(pk=worker).exists()
	if not paid_check:
		try:
			print("Approving worker "+worker)
			total_appr += 1
			if not dry_run:
				conn.approve_assignment(user.assignment_id)
		except connection.MTurkRequestError as e:
			#expected errors when in sandbox 
			print("exception when approving: ")
			print(e)
	bonus = float(payout.bonus) / 100.0
	if bonus>5:
		print("bonus too high - rejected.")
		return
	bonus_price = price.Price(amount = bonus, currency_code="USD")
	print("  Bonus "+str(bonus))
	total_bonus += bonus
	if (not dry_run and not paid_check):
		try:
			conn.grant_bonus(user.pk, user.assignment_id, bonus_price, "correct answers")
                        paid = models.Paid(pk=worker, pay_date=timezone.now())
                        paid.save()
		except connection.MTurkRequestError as e:
			print("exception when bonusing: ")
			print(e)

def bonus_worker(worker, amount):
    pass

#takes a string as YYYY-MM-DD. Day is assumed to be in EST
def approve_by_date(date):
	sections = date.split("-")
	start = timezone.make_aware(datetime.datetime(int(sections[0]), int(sections[1]), int(sections[2]), 0, 0, 0), timezone.get_default_timezone())
	end = start + datetime.timedelta(days=1)
	todayUsers = models.PUser.objects.filter(date__gte = start, date__lte = end, dead = True, provisional = False)
	for user in todayUsers:
		approve_by_worker(user.pk)
        print_totals()

def approve_by_hit(hit):
	hit_users = models.PUser.objects.filter(hit_id=hit)
	for user in hit_users:
		approve_by_worker(user.pk)
        print_totals()
