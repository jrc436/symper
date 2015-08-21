import subprocess, collections, os, random
from symper import settings

def _check_output(list_of_args):
	#if 'stdout' in kwargs:
	#	raise ValueError('stdout argument not allowed, it will be overridden.')
	process = subprocess.Popen(list_of_args, stdout=subprocess.PIPE)
	output, unused_err = process.communicate()
	retcode = process.poll()
	if retcode:
		cmd = kwargs.get("args")
		if cmd is None:
			cmd = popenargs[0]
		raise subprocess.CalledProcessError(retcode, cmd)
	return output.strip()

def git_describe():
	return _check_output(["git", "--work-tree=/home/jrc436/symper", "--git-dir=/home/jrc436/symper/.git", "describe"])
	#return "v0.1"

