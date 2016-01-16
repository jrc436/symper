#!/usr/bin/python2.6

import time
import psu_conn
import math
from hit_info import get_comparisons
from boto.mturk import price, qualification

conn = psu_conn.make_con()

hours = 60 * 60 
days = 24 * hours

def get_worker_qualifications(approval_rate, total_approved):
	reqs = qualification.Qualifications()
	reqs.add(qualification.PercentAssignmentsApprovedRequirement(comparator = "GreaterThan", integer_value = str(approval_rate), required_to_preview=True))
	reqs.add(qualification.LocaleRequirement(comparator = "EqualTo", locale ="US", required_to_preview=True))
	reqs.add(qualification.NumberHitsApprovedRequirement(comparator = "GreaterThan", integer_value = str(total_approved), required_to_preview=True))
	return reqs                         

def make_all_hits(num_subjects):
	print("Publishing "+str(int(math.ceil(float(num_subjects) / 9.0)))+" batches with a max of 9 participants each")
	while (num_subjects >= 9):
		make_hit(min(num_subjects, 9))
		num_subjects = num_subjects - 9

def make_hit(num_subjects):
	hit = get_comparisons(psu_conn.get_comparisons_layout())
	conn.create_hit(title = hit.title, description=hit.description, keywords=hit.keywords, max_assignments=num_subjects, hit_layout=hit.layoutid, lifetime=7*days, duration=6*hours, approval_delay=2*days, reward=price.Price(amount=hit.reward),qualifications=get_worker_qualifications(95,100))

for i in range(0,3):
	print("Creating HITs")
	make_all_hits(9)
	print("Waiting...")
	time.sleep(1*hours)  # wait to prevent server overload 
