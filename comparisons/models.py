from django.db import models
from datetime import datetime

class Image(models.Model):
	image = models.ImageField(upload_to = "sym_images")
	P1 = "p1"
	P2 = "p2"
	PM = "pm"
	PG = "pg"
	CM = "cm"
	PMM = "pmm"
	PMG = "pmg"
	PGG = "pgg"
	CMM = "cmm"
	P4 = "p4"
	P4M = "p4m"
	P4G = "p4g"
	P3 = "p3"
	P3M1 = "p3m1"
	P31M = "p31m"
	P6 = "p6"
	P6M = "p6m"
	GROUPS = ( (P6M, P6M), (P6, P6), (P31M, P31M), (P3M1, P3M1), (P3, P3), (P4G, P4G), (P4M, P4M), (P4, P4), (CMM, CMM), (PGG, PGG), (PMG, PMG), (PMM, PMM), (CM, CM), (PG, PG), (PM, PM), (P2, P2), (P1, P1) )
	group = models.CharField(max_length=4, choices=GROUPS)
	def rotation_group(self):
		if self.group == P1 or self.group == PM or self.group == CM or self.group == PG:
			return 1
		elif self.group == P2 or self.group == PMM or self.group == PMG or self.group == PGG or self.group == CMM:
			return 2
		elif self.group == P4 or self.group == P4M or self.group == P4G:
			return 4
		elif self.group == P3 or self.group == P31M or self.group == P3M1:
			return 3
		elif self.group == P6 or self.group == P6M:
			return 6
	def has_reflection(self):
		if self.group == P1 or self.group == P2 or self.group == PG or self.group == PGG or self.group == P4 or self.group == P3 or self.group == P6:
			return False
		else:
			return True
	def has_glide(self):
		if self.group == P1 or self.group == P2 or self.group == PM or self.group == PMM or self.group == P4 or self.group == P3 or self.group == P6: 
			return False
		else:
			return True
	def has_rotation_group(self, order):
		if order != 1 and order != 2 and order != 3 and order != 4 and order != 6:
			raise "Invalid rotation order"
		gr = self.rotation_group
		if order == 1 and gr == 1:
			return True
		elif order == 2 and (gr == 2 or gr == 4 or gr == 6):
			return True
		elif order == 4 and gr == 4:
			return True
		elif order == 3 and (gr == 3 or gr == 6):
			return True
		elif order == 6 and gr == 6:
			return True
		else:
			return False

class Task(models.Model):
        test_image = models.ForeignKey(Image, related_name='testset')
        choice1 = models.ForeignKey(Image, related_name='oneset')
        choice2 = models.ForeignKey(Image, related_name='twoset')

class TaskSet(models.Model):
	tasks = models.ManyToManyField(Task)
	def getIncompleteTasks(self):
		user = PUser.objects.get(taskset__id = self.id)
		results = Result.objects.filter(selector__turk_id = user.turk_id)
		return self.tasks.exclude(id__in=[result.task.id for result in results])


class Payout(models.Model):
	turk_id = models.CharField(primary_key=True, max_length=40)
	pay = models.PositiveIntegerField() 
	bonus = models.PositiveIntegerField()

class Validation(models.Model):
	turk_id = models.CharField(primary_key=True, max_length=40)
	percentCorrect = models.DecimalField(max_digits = 3, decimal_places = 3)
	percentTop = models.DecimalField(max_digits = 3, decimal_places = 3)
	percentBottom = models.DecimalField(max_digits = 3, decimal_places = 3)
	percentTimeout = models.DecimalField(max_digits = 3, decimal_places = 3)	

class PUser(models.Model):
	breakTime = models.NullBooleanField(default=False)
	turk_id = models.CharField(primary_key=True, max_length=40)
	taskset = models.OneToOneField(TaskSet)
	dead = models.BooleanField(default=False)
	hit_id = models.CharField(default=1, max_length=40) #the "HIT" this user participated in
	assignment_id = models.CharField(default=1, max_length=40) #hits are the whole assignment, assignments are an individual user's slice of the cake, unique given hit_id and turk_id
	date = models.DateTimeField(auto_now_add=True)
	git_revision = models.CharField(max_length=30) #populated automatically with bash looking at the git revision num
	provisional = models.BooleanField(default=True) #hit_id and turk_id are randomly generated

class Result(models.Model):
	selector = models.ForeignKey(PUser)
	task = models.ForeignKey(Task)
	CHOICES = ( ("TOP", "choice1"), ("BOT", "choice2") )
	choice = models.CharField(max_length=3, choices=CHOICES)
	CORRECTNESS = ( (1, "correct"), (0, "timeout"), (2, "incorrect") )
	TECH_CORRECTNESS = ( ( 1, "correct"), (2, "incorrect") )
	correct = models.SmallIntegerField(default = 0, choices=CORRECTNESS)
	tech_correct = models.SmallIntegerField(default = 0, choices=TECH_CORRECTNESS)
	elapsedTime = models.PositiveIntegerField(default=3)
	def setCorrect(self):
		if (self.choice == self.CHOICES[0][0] and self.task.choice1.group == self.task.test_image.group):
			self.correct = 1
			self.tech_correct = 1
		elif (self.choice == self.CHOICES[1][0] and self.task.choice2.group == self.task.test_image.group):
			self.correct = 1
			self.tech_correct = 1
		else:
			self.correct = 2
			self.tech_correct = 2
		if (self.elapsedTime > 5):
			self.correct = 0
		self.save()
