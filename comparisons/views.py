from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from comparisons import models
import os, random, time, subprocess
from symper import settings
from django.views.generic import TemplateView, DetailView
from django.views.generic.list import ListView
from django.forms.models import model_to_dict
from util import git_describe
from itertools import chain

class EndView(TemplateView):
	template_name = 'end.html'
	def dispatch(self, *args, **kwargs):
		if ('turk_id' not in self.request.session or 'task' not in self.request.session):
			return HttpResponseRedirect(reverse_lazy('intro'))
		return super(EndView, self).dispatch(*args, **kwargs)
	def get_context_data(self, **kwargs):
		context = super(EndView, self).get_context_data(**kwargs)
		user = models.PUser.objects.get(turk_id=self.request.session['turk_id'])
		incomplete = user.taskset.getIncompleteTasks().all().count()
		complete = models.Result.objects.filter(selector=user)
		context['numTasksIncomplete'] = incomplete
		context['numTasksComplete'] = complete.count()
		context['numCorrect'] = complete.filter(correct=1).count()
		context['numIncorrect'] = complete.filter(correct=2).count()
		context['numTimeOut'] = complete.filter(correct=0).count()
		context['basepay'] = 2.00
		context['bonus'] = round(2.00 * context['numCorrect'] / (context['numCorrect']+context['numIncorrect']+context['numTimeOut']), 2)
		context['dead'] = user.dead 
		return context
	def post(self, request):
		if request.POST.get("submission"):
			user = models.PUser.objects.get(pk=request.session['turk_id'])
			user.dead = True
			user.save()
		#in this portion, we need to do something with the mturk api
		return HttpResponseRedirect("https://www.amazon.com")


class IntroView(TemplateView):
	template_name = 'intro.html'
	def dispatch(self, *args, **kwargs):
		if ('turk_id' in self.request.session and 'task' in self.request.session):
                        return HttpResponseRedirect(reverse_lazy('task'))
		return super(IntroView, self).dispatch(*args, **kwargs)

	def get(self, request):
		if request.GET.get("hit_id") and request.GET.get("mturk_id"):
			hitid = request.GET["hit_id"]
			turkid = request.GET["mturk_id"]
			provisional = False
		else:
			hitid = self.genID()
			turkid = self.genID()
			provisional = True
		if (models.PUser.objects.filter(pk=turkid).exists()):
			user = models.PUser.objects.get(pk=turkid)
		else:
			user = self.initialize_new_user(turkid, hitid, provisional)
		if user is None:
			new_context = dict()
			new_context['user'] = None
			new_context['redir_url'] = reverse_lazy('init3')
			return render(request, self.template_name, new_context) 
		tasks = user.taskset.getIncompleteTasks()
		numTasks = tasks.count()
		if numTasks > 0:
			if numTasks == 1:
				index = 1
			else:
				index = random.randint(0, numTasks - 1)
			task = tasks[index]
			self.request.session['task'] = model_to_dict(task)
		else:
			self.request.session['task'] = None
		self.request.session['turk_id'] = turkid
		return render(request, self.template_name, self.get_context_data())
			
	def genID(self):
		return random.randint(0, 256000)
	def get_context_data(self, **kwargs):
		context = super(IntroView, self).get_context_data(**kwargs)
		user = models.PUser.objects.get(turk_id = self.request.session['turk_id'])
		context['exp_version'] = user.git_revision
		context['provisional'] = user.provisional
		context['hitid'] = user.hit_id
		context['turkid'] = user.turk_id
		return context
	def initialize_new_user(self, turkid, hitid, provisional):
		#retrieve a taskset that doesn't have a user yet
		#first, get all the ones that do?
		users = models.PUser.objects.all()
		remaining = models.TaskSet.objects.exclude(id__in=[user.taskset.id for user in users])
		if len(remaining) == 0:
			return None
		elif len(remaining) == 1:
			index = 0
		else:
			index = random.randint(0, len(remaining)-1)
		new_user = models.PUser(turk_id = turkid, hit_id = hitid, provisional = provisional, git_revision = git_describe(), taskset = remaining.all()[index])
		new_user.save()
		return new_user 
		

class ResultsView(TemplateView):
	template_name = 'result.html'
	def get_context_data(self, **kwargs):
		context = super(ResultsView, self).get_context_data(**kwargs)
		context['numParticipants'] = models.PUser.objects.all().count()
		#there are, effectively, 272 types of results.... so let's just progrma this shite
		csv = []
		csv.append("target,comparison,accuracy")
		for t in range(0,len(models.Image.GROUPS)):
			for c in range(t+1,len(models.Image.GROUPS)):
				qset0 = models.Result.objects.filter(task__test_image__group = models.Image.GROUPS[t][0])
				qset0r = models.Result.objects.filter(task__choice1__group = models.Image.GROUPS[t][0]) |  models.Result.objects.filter(task__choice2__group = models.Image.GROUPS[t][0])
				qset1 = qset0.filter(task__choice1__group = models.Image.GROUPS[c][0]) |  qset0.filter(task__choice2__group = models.Image.GROUPS[c][0])
				qset1r = qset0r.filter(task__test_image__group = models.Image.GROUPS[c][0])
				numCorrect = qset1.filter(correct = 1).count() + qset1r.filter(correct = 1).count()
				totalNum = qset1.all().count() + qset1r.all().count()
				accuracy = float(numCorrect) / float(totalNum) 
				csv.append(models.Image.GROUPS[t][0] + "," + models.Image.GROUPS[c][0] +"," + "%2.3f" % accuracy)
		context['csv'] = csv
		return context

class TaskView(TemplateView):
	template_name = 'task.html'
	def dispatch(self, *args, **kwargs):
		if ('turk_id' not in self.request.session or 'task' not in self.request.session):
			return HttpResponseRedirect(reverse_lazy('intro'))
		if self.getNumTasks() == 0 or models.PUser.objects.get(pk=self.request.session['turk_id']).dead is True:
			return HttpResponseRedirect(reverse_lazy('end'))
		if ('stime' not in self.request.session):
			self.request.session['stime'] = time.time()
		return super(TaskView, self).dispatch(*args, **kwargs)
	def get_context_data(self, **kwargs):
		context = super(TaskView, self).get_context_data(**kwargs)
		pid = self.request.session['turk_id']
		taskjson = self.request.session['task']
		context['task'] = self.dicToTask(taskjson)
		return context
	def post(self, request):
		newTime = time.time()
		ttime = round(newTime - request.session['stime'])
		if request.POST.get("top.x"):
			result = models.Result(selector=models.PUser.objects.get(pk=request.session['turk_id']), task=self.dicToTask(self.request.session['task']), choice=models.Result.CHOICES[0][0], elapsedTime=ttime)
			result.setCorrect()
		elif request.POST.get("bottom.x"):
			result = models.Result(selector=models.PUser.objects.get(pk=request.session['turk_id']), task=self.dicToTask(self.request.session['task']), choice=models.Result.CHOICES[1][0], elapsedTime=ttime)
			result.setCorrect()
		incompleteTasks = self.getIncomplete()
		numTasks = incompleteTasks.count()
		if numTasks == 0:
			#return render(request, EndView.template_name)
			return HttpResponseRedirect(reverse_lazy('end'))
		elif numTasks == 1:
			randomIndex = 0
		else:
			randomIndex = random.randint(0, incompleteTasks.count() - 1)
		self.request.session['task'] = model_to_dict(incompleteTasks[randomIndex])
		self.request.session['stime'] = time.time()
		kwargs['numTasks'] = numTasks
		return render(request, self.template_name, self.get_context_data(**kwargs))
	def getIncomplete(self):
		return models.PUser.objects.get(pk=self.request.session['turk_id']).taskset.getIncompleteTasks().all()
	def getNumTasks(self):
		incompleteTasks = self.getIncomplete()
		return incompleteTasks.count()

	def dicToTask(self, taskjson):
		return models.Task.objects.get(choice1__id=taskjson['choice1'], choice2__id=taskjson['choice2'], test_image__id=taskjson['test_image'])
	

class InitImagesView(TemplateView):
	#first, need to initialize the images. Next, need to initialize the tasks.
	#the images is just a simple matter of performing manual insertions 	
	template_name = 'init.html'
	def get_context_data(self, **kwargs):
		#print("we are calling a thing")
		self.initImages()
		context = super(InitImagesView, self).get_context_data(**kwargs)
		context['expected'] = 85
		context['actual'] = len(models.Image.objects.all())
		return context
	def initImages(self):
		baseDir = settings.MEDIA_ROOT
		#print(baseDir)
		sym_folder = "sym_images"
		for dirName, subdirList, fileList in os.walk(baseDir):
			print("At directory: %s" % dirName)
			if (sym_folder not in dirName):
				continue
	 		for image in fileList:
				print("Currently viewing Image: %s" % image)
				#do some regex magic to extract the wallpaper group
				image_group = image.split('_')[0]
				print("Image is of group: %s" % image_group)
				#path to the image on the server
				image_obj = models.Image(group = image_group, image = settings.MEDIA_URL +"/"+sym_folder+"/"+ image) 
				image_obj.save()

class InitTasksView(TemplateView):
	template_name= 'init2.html'
#ok, images initialized. presumably. Now we need to collect the images into tasks.
	#we want 16 tasks for each of the 17 images.
	
	def get_context_data(self, **kwargs):
		self.initGroups()
		context = super(InitTasksView, self).get_context_data(**kwargs)
		context['expected'] = 54400 #17 * 5 * 16 * 4 * 5 * 2
		context['actual'] = len(models.Task.objects.all())
		return context

	def initGroups(self):
		for group in models.Image.GROUPS:
			#Now we need to create 16*n tasks, to start.
			#print(group[0])
			sett = list(models.Image.objects.filter(group = group[0]))
			#print(len(sett))
			for imag in sett:
				for other_group in models.Image.GROUPS:
					if (group == other_group):
						continue
					otherSett = list(models.Image.objects.filter(group = other_group[0]))
						#every other image in the group
					for other_imag in sett:
						if other_imag == imag:
							continue
							#every image in the other group
						for third_imag in otherSett:
							task_obj = models.Task(test_image = imag, choice1 = third_imag, choice2 = other_imag)
							task_obj.save()
							task_obj2 = models.Task(test_image = imag, choice1 = other_imag, choice2 = third_imag)
							task_obj2.save()
	
class InitTaskSetView(TemplateView):
	template_name = 'init3.html'
	def dispatch(self, *args, **kwargs):
		self.initTaskSets()
		kwargs['numsets'] = len(models.TaskSet.objects.all())
		kwargs['redir_url'] = reverse_lazy('intro')
		#if kwargs['numsets'] > 1000:
		#	return HttpResponseRedirect(reverse_lazy('intro'))
		return render(self.request, self.template_name, self.get_context_data(**kwargs))
	def initTaskSets(self):	#initialize tasksets
		#print(i)
		taskset = models.TaskSet()
		taskset.save()
		for group in models.Image.GROUPS:
			#grab all of the tasks where the test image is group
			qset = models.Task.objects.filter(test_image__group = group[0])
			for other_group in models.Image.GROUPS:
				if (group == other_group):
					continue
				#this queryset is looking to see if either of the choices match "other_group"
				queryset = qset.filter(choice1__group = other_group[0]) | qset.filter(choice2__group = other_group[0])
				choose = random.randint(0, len(queryset)-1)
				taskset.tasks.add(queryset[choose])
				taskset.save()

