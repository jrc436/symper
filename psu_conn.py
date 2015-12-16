import getpass
from boto.mturk import connection

if getpass.getuser() == "dreitter":
    from credentials.reitter import *
    host = "mechanicalturk.amazonaws.com"
    comparisons_layoutid = '321KFBXXMNLPCCOCN7EK7KTLU4WPJW'
else:
    from credentials.cole import *
    host = "mechanicalturk.sandbox.amazonaws.com"
    comparisons_layoutid = '3R7WSKJ9DZ5ZX8MAVXDW2WCECDZPTB'
def get_comparisons_layout():
	return comparisons_layoutid
def make_con():
	return connection.MTurkConnection(aws_access_key_id=access, aws_secret_access_key=secret, host=host)
