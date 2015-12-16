from django.db import models
from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
#from util import Graph
#from util import dijsktra
#from util import all_dijsktra

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
		if self.group.lower() == Image.P1 or self.group.lower() == Image.PM or self.group.lower() == Image.CM or self.group.lower() == Image.PG:
			return 1
		elif self.group.lower() == Image.P2 or self.group.lower() == Image.PMM or self.group.lower() == Image.PMG or self.group.lower() == Image.PGG or self.group.lower() == Image.CMM:
			return 2
		elif self.group.lower() == Image.P4 or self.group.lower() == Image.P4M or self.group.lower() == Image.P4G:
			return 4
		elif self.group.lower() == Image.P3 or self.group.lower() == Image.P31M or self.group.lower() == Image.P3M1:
			return 3
		elif self.group.lower() == Image.P6 or self.group.lower() == Image.P6M:
			return 6
		else:
			return "NOPE"
	def has_reflection(self):
		if self.group.lower() == Image.P1 or self.group.lower() == Image.P2 or self.group.lower() == Image.PG or self.group.lower() == Image.PGG or self.group.lower() == Image.P4 or self.group.lower() == Image.P3 or self.group.lower() == Image.P6:
			return False
		else:
			return True
	def has_glide(self):
		if self.group.lower() == Image.P1 or self.group.lower() == Image.P2 or self.group.lower() == Image.PM or self.group.lower() == Image.PMM or self.group.lower() == Image.P4 or self.group.lower() == Image.P3 or self.group.lower() == Image.P6: 
			return False
		else:
			return True
	def has_rotation_group(self, order):
		if order != 1 and order != 2 and order != 3 and order != 4 and order != 6:
			raise "Invalid rotation order"
		gr = self.rotation_group()
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
	def get_T1(self):
		if (self.group.lower() == Image.PM or self.group.lower() == Image.PMM or self.group.lower() == Image.P4M or self.group.lower() == Image.P31M or self.group.lower() == Image.P6M):
			return "Y"
		elif (self.group.lower() == Image.PG or self.group.lower() == Image.PMG or self.group.lower() == Image.PGG or self.group.lower() == Image.P4G):
			return "G"
		else:
			return "N"
	def get_T2(self):
		gr = self.group.lower()
		if (gr == Image.PMM or gr == Image.PMG or gr == Image.P4M or gr == Image.P31M or gr == Image.P6M):
			return "Y"
		elif (gr == Image.PGG or gr == Image.P4G):
			return "G"
		else:
			return "N"

	def get_D1(self):
		gr = self.group.lower()
		if (gr == Image.CM or gr == Image.CMM or gr == Image.P4M or gr == Image.P4G or gr == Image.P3M1 or gr == Image.P6M):
			return "Y"
		else:
			return "N"

	def get_D2(self):
		gr = self.group.lower()
		if (gr == Image.CMM or gr == Image.P4M or gr == Image.P4G or gr == Image.P6M):
			return "Y"
		else:
			return "N"


	def tile(self):
		if self.group.lower() == Image.P1 or self.group.lower() == Image.P2:
			return "oblique"
		elif self.group.lower() == Image.PM or self.group.lower() == Image.PG or self.group.lower() == Image.PMM or self.group.lower() == Image.PMG or self.group.lower() == Image.PGG:
			return "rectangular"
		elif self.group.lower() == Image.CM or self.group.lower() == Image.CMM:
			return "rhombic"
		elif self.group.lower() == Image.P4 or self.group.lower() == Image.P4M or self.group.lower() == Image.P4G:
			return "square"
		else:
			return "hexagonal"

	def distance(self, other):
		distance = Distance.objects.filter(from_group = self.group).filter(to_group = other.group).get()
		return distance.distance



class Task(models.Model):
        test_image = models.ForeignKey(Image, related_name='testset')
        choice1 = models.ForeignKey(Image, related_name='oneset')
        choice2 = models.ForeignKey(Image, related_name='twoset')

class Distance(models.Model):
	from_group = models.CharField(max_length=4, choices=Image.GROUPS)
	to_group = models.CharField(max_length=4, choices=Image.GROUPS)	
	distance = models.PositiveIntegerField()

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
	
class Paid(models.Model):
	turk_id = models.CharField(primary_key=True, max_length=40)
	pay_date = models.DateTimeField()

class Validation(models.Model):
	turk_id = models.CharField(primary_key=True, max_length=40)
	percentCorrect = models.DecimalField(max_digits = 3, decimal_places = 3)
	percentTop = models.DecimalField(max_digits = 3, decimal_places = 3)
	percentBottom = models.DecimalField(max_digits = 3, decimal_places = 3)
	percentTimeout = models.DecimalField(max_digits = 3, decimal_places = 3)	

class Demographics(models.Model):
	turk_id = models.CharField(primary_key=True, max_length=40)
	GENDERS = ( ( "M", "Male"), ("F", "Female"), ("O", "Other") )
	gender = models.CharField(max_length=1, choices=GENDERS)
	age = models.PositiveSmallIntegerField(validators=[MaxValueValidator(120), MinValueValidator(1)])
	education_years = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(25)])
	languages = ( ( "EN", "English"), ("AR", "Arabic"), ("ES", "Spanish"), ("ZH", "Chinese"), ("JA", "Japanese"), ("FR", "French"), ("FA", "Farsi"), ("VI", "Vietnamese"), ("TL", "Tagalog"), ("DE", "German"), ("KO", "Korean"), ("RU", "Russian"), ("OT", "Other") )
	first_language = models.CharField(max_length=2, choices=languages)

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
