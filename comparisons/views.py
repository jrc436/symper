from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from comparisons import models
import os, random, time, subprocess, decimal
from symper import settings
from util import git_describe
from django.views.generic import TemplateView, DetailView
from django.views.generic.list import ListView
from django.forms.models import model_to_dict
from itertools import chain
from boto.mturk import connection
from boto.mturk.price import Price
from decimal import Decimal
from django.db.models import Count, Max

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
		context['correct_timeout'] = complete.filter(correct=0).filter(tech_correct=1).count()
		context['basepay'] = self.getBasePay()
		context['bonus'] = self.getBonus(user)
		context['dead'] = user.dead 
		return context
	def post(self, request):
		if request.POST.get("submission"):
			user = models.PUser.objects.get(pk=request.session['turk_id'])
			user.dead = True
			user.save()
		#in this portion, we need to do something with the mturk api
		#we want to make absolutely sure that we don't pay the same person twice obviously
			if not user.provisional and not models.Payout.objects.filter(pk=user.pk).exists():
				p = self.getBasePay()*100
				b = self.getBonus(user)*100
				payout = models.Payout(turk_id = user.turk_id, pay = p, bonus = b) 
				payout.save()
				#conn = MTurkConnection()
				#conn.approve_assignment(user.assignment_id)
				#grant_bonus(user.turk_id, user.assignment_id, Price(amount =  p.bonus), "performance bonus")
		return HttpResponseRedirect("https://www.mturk.com/mturk/")
	def getBasePay(self):
		return 2.00
	def getBonus(self, user):
		complete = models.Result.objects.filter(selector=user)
		correct = complete.filter(correct=1).count()
		pCor = float(correct) / float(correct + complete.filter(correct=0).count() + complete.filter(correct=2).count())
		return max(0.0, round(4.0 * (pCor - 0.5), 2))


class IntroView(TemplateView):
	template_name = 'intro.html'
	def dispatch(self, *args, **kwargs):
		if ('turk_id' in self.request.session and 'task' in self.request.session):
                        return HttpResponseRedirect(reverse_lazy('task'))
		return super(IntroView, self).dispatch(*args, **kwargs)

	def get(self, request):
		if request.GET.get("hit_id") and request.GET.get("mturk_id") and request.GET.get("ass_id"):
			hitid = request.GET["hit_id"]
			turkid = request.GET["mturk_id"]
			assid = request.GET["ass_id"]
			provisional = False
		else:
			hitid = self.genID()
			turkid = self.genID()
			assid = self.genID()
			provisional = True
		if (models.PUser.objects.filter(pk=turkid).exists()):
			user = models.PUser.objects.get(pk=turkid)
		else:
			user = self.initialize_new_user(turkid, hitid, assid, provisional)
		if user is None:
			new_context = dict()
			new_context['user'] = None
			#new_context['redir_url'] = reverse_lazy('init3')
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
	def initialize_new_user(self, turkid, hitid, assid,  provisional):
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
		new_user = models.PUser(turk_id = turkid, hit_id = hitid, provisional = provisional, assignment_id = assid, git_revision = git_describe(), taskset = remaining.all()[index])
		new_user.save()
		return new_user 
		

class ValidationView(TemplateView):
	template_name = 'validation.html'
	def get_context_data(self, **kwargs):
		context = super(ValidationView, self).get_context_data(**kwargs)
		paidUsers = models.PUser.objects.exclude(provisional=True)
		#newestUser = paidUsers.latest('date')#get(date=paidUsers.aggregate(newest=Max("date"))['newest'])
		#curUsers = paidUsers.filter(hit_id = newestUser.hit_id)
		finishedUsers = paidUsers.filter(dead=True)
		#newestUser = finishedUsers.latest('date')
		#curUsers = finishedUsers.filter(hit_id = newestUser.hit_id) 
		curUsers = finishedUsers
		userinfo = []
		for user in curUsers:
			complete = models.Result.objects.filter(selector=user)
			numCorrect = complete.filter(correct = 1).count()
			numIncorrect = complete.filter(correct = 2).count()
			numTimeout = complete.filter(correct = 0).count()
			pCorrect = Decimal(numCorrect) / Decimal(numCorrect + numIncorrect + numTimeout)
			pTimeout = Decimal(numTimeout) / Decimal(numCorrect + numIncorrect + numTimeout)
			numTop = complete.filter(choice="TOP").count()
			numBottom = complete.filter(choice="BOT").count()
			pTop = Decimal(numTop) / Decimal(numTop + numBottom)
			pBot = Decimal(numBottom) / Decimal(numTop + numBottom)
			if (models.Validation.objects.filter(turk_id = user.pk).exists()):
				models.Validation.objects.filter(pk = user.pk).update(percentCorrect = pCorrect, percentTop = pTop, percentBottom = pBot, percentTimeout = pTimeout)
			else:
				models.Validation.objects.create(turk_id = user.pk, percentCorrect = pCorrect, percentTop = pTop, percentBottom = pBot, percentTimeout = pTimeout)
			pay = models.Payout.objects.get(pk=user.pk)
			pennies = pay.pay + pay.bonus
			this_user = (user.pk, complete.count(), user.hit_id, models.Validation.objects.get(pk=user.pk), pennies)
			userinfo.append(this_user)
		context['userinfo'] = userinfo
		#we want to know each user who is paid, their bonus, the percent they clicked top, the percent they clicked bottom, their number of timeouts, and their percent correct
		return context		

class ResultsView(TemplateView):
	template_name = 'result.html'
	def get_context_data(self, **kwargs):
		context = super(ResultsView, self).get_context_data(**kwargs)
		#there are, effectively, 272 types of results.... so let's just progrma this shite
		filteredUsers = self.getFilteredUsers()
		#context['hitid'] = list(filteredUsers[:1])[0].hit_id
		context['numParticipants'] = filteredUsers.count()
		csv = []
		csv.append("target,comparison,accuracy")
		relResults = models.Result.objects.filter(selector__in=[user for user in filteredUsers])
		for t in range(0,len(models.Image.GROUPS)):
			for c in range(t+1,len(models.Image.GROUPS)):
				qset0 = relResults.filter(task__test_image__group = models.Image.GROUPS[t][0])
				qset0r = relResults.filter(task__choice1__group = models.Image.GROUPS[t][0]) | relResults.filter(task__choice2__group = models.Image.GROUPS[t][0])
				qset1 = qset0.filter(task__choice1__group = models.Image.GROUPS[c][0]) |  qset0.filter(task__choice2__group = models.Image.GROUPS[c][0])
				qset1r = qset0r.filter(task__test_image__group = models.Image.GROUPS[c][0])
				numCorrect = qset1.filter(correct = 1).count() + qset1r.filter(correct = 1).count()
				totalNum = qset1.all().count() + qset1r.all().count()
				accuracy = float(numCorrect) / float(totalNum) 
				csv.append(models.Image.GROUPS[t][0] + "," + models.Image.GROUPS[c][0] +"," + "%2.3f" % accuracy)
		context['csv'] = csv
		return context
	def getFilteredUsers(self):
		paidUsers = models.PUser.objects.filter(provisional=False)
		clicked_corrects = paidUsers.annotate(Count('result')).exclude(result__count__lt=272).exclude(result__count__gte=340)
		validations = models.Validation.objects.filter(pk__in=[user.pk for user in clicked_corrects])
		unrandom_vals = validations.exclude(percentTop__gte=Decimal("0.6")).exclude(percentBottom__gte=Decimal("0.6"))
		timedout_vals = unrandom_vals.exclude(percentTimeout__gte=Decimal("0.2"))
		return clicked_corrects.filter(pk__in=[v.pk for v in timedout_vals])
	def filterResults(self, filteredUsers):
		exclude = set()
		relResults = models.Result.objects.filter(selector__in=[user for user in filteredUsers])
		for res in relResults:
			for res2 in relResults:
				if (res.pk not == res2.pk) and (res.selector.pk == res2.selector.pk) and (res.task.pk == res2.task.pk):
					exclude.add(res2)
		return relResults.exclude(pk__in=[item.pk for item in exclude])
					


class RotResultsView(ResultsView):
	def get_context_data(self, **kwargs):
		context = super(RotResultsView, self).get_context_data(**kwargs)
		filteredUsers = self.getFilteredUsers()
		csv = []
		csv.append('group_target,group_comp,same2fold,same3fold,same4fold,same6fold,user_id,task_id,accuracy')
		relResults = models.Result.objects.filter(selector__in=[user for user in filteredUsers])
		for result in relResults:
			target_group = result.task.test_image
			comp_group = result.task.choice2 if result.task.test_image.group == result.task.choice1.group else result.task.choice1
			same2fold = comp_group.has_rotation_group(2) == target_group.has_rotation_group(2)
			same3fold = comp_group.has_rotation_group(3) == target_group.has_rotation_group(3)
			same4fold = comp_group.has_rotation_group(4) == target_group.has_rotation_group(4)
			same6fold = comp_group.has_rotation_group(6) == target_group.has_rotation_group(6)
			correct = 1 if result.correct == 1 else 0
			user_id = result.selector.pk
			task_id = result.task.id
			csv.append(target_group.group+","+comp_group.group+","+str(same2fold)+","+str(same3fold)+","+str(same4fold)+","+str(same6fold)+","+str(user_id)+","+str(task_id)+","+str(correct))
		context['csv'] = csv
		return context

class ReflResultsView(ResultsView):
	def get_context_data(self, **kwargs):
		context = super(ReflResultsView, self).get_context_data(**kwargs)
		filteredUsers = self.getFilteredUsers()
		csv = []
		csv.append('group_target,group_comp,T1_same,T2_same,D1_same,D2_same,user_id,task_id,accuracy')
		relResults = models.Result.objects.filter(selector__in=[user for user in filteredUsers])	
		for result in relResults:
			target_group = result.task.test_image
			comp_group = result.task.choice2 if result.task.test_image.group == result.task.choice1.group else result.task.choice1
			T1_same = comp_group.get_T1() == target_group.get_T1()
			T2_same = comp_group.get_T2() == target_group.get_T2()
			D1_same = comp_group.get_D1() == target_group.get_D1()
			D2_same = comp_group.get_D2() == target_group.get_D2()
			correct = 1 if result.correct == 1 else 0
			user_id = result.selector.pk
			task_id = result.task.id
			csv.append(target_group.group+","+comp_group.group+","+str(T1_same)+","+str(T2_same)+","+str(D1_same)+","+str(D2_same)+","+str(user_id)+","+str(task_id)+","+str(correct))
		context['csv'] = csv
		return context

class AllResultsView(ResultsView):
	def get_context_data(self, **kwargs):
		context = super(AllResultsView, self).get_context_data(**kwargs)
		filteredUsers = self.getFilteredUsers()
		csv = []
		csv.append('group_target,group_comp,tile_same,T1_same,T2_same,D1_same,D2_same,same2fold,same3fold,same4fold,same6fold,distance,user_id,task_id,accuracy')
		relResults = self.filterResults(filteredUsers)
		for result in relResults:
			target_group = result.task.test_image
			comp_group = result.task.choice2 if result.task.test_image.group == result.task.choice1.group else result.task.choice1
			T1_same = comp_group.get_T1() == target_group.get_T1()
			T2_same = comp_group.get_T2() == target_group.get_T2()
			D1_same = comp_group.get_D1() == target_group.get_D1()
			D2_same = comp_group.get_D2() == target_group.get_D2()
			tile_same = tile_target == tile_comp
			same2fold = comp_group.has_rotation_group(2) == target_group.has_rotation_group(2)
			same3fold = comp_group.has_rotation_group(3) == target_group.has_rotation_group(3)
			same4fold = comp_group.has_rotation_group(4) == target_group.has_rotation_group(4)
			same6fold = comp_group.has_rotation_group(6) == target_group.has_rotation_group(6)
			distance = target_group.distance(comp_group)
			correct = 1 if result.correct == 1 else 0
			user_id = result.selector.pk
			task_id = result.task.pk
			csv.append(target_group.group+","+comp_group.group+","+str(tile_same)+","+str(T1_same)+","+str(T2_same)+","+str(D1_same)+","+str(D2_same)+","+str(same2fold)+","+str(same3fold)+","+str(same4fold)+","+str(same6fold)+","+str(distance)+","+str(user_id)+","+str(task_id)+","+str(accuracy))
		context['csv'] = csv
		return context	

class FDResultsView(ResultsView):
	template_name = "result.html"
	def get_context_data(self, **kwargs):
		context = super(FDResultsView, self).get_context_data(**kwargs)
		filteredUsers = self.getFilteredUsers()
		csv = []
		csv.append('group_target,group_comp,rot_same,ref_same,gref_same,tile_same,user_id,task_id,distance,accuracy')
		relResults = models.Result.objects.filter(selector__in=[user for user in filteredUsers])
		#graph = init_sym_graph()
		#dji_struct = all_dijsktra(graph) 
		for result in relResults:
			target_group = result.task.test_image
			comp_group = result.task.choice2 if result.task.test_image.group == result.task.choice1.group else result.task.choice1
			rot_target = target_group.rotation_group()
			rot_comp = comp_group.rotation_group()
			ref_target = target_group.has_reflection()
			ref_comp = comp_group.has_reflection()
			gref_target = target_group.has_glide()
			gref_comp = comp_group.has_glide()
			tile_target = target_group.tile()
			tile_comp = comp_group.tile()
			user_id = result.selector.pk
			task_id = result.task.id
			distance = target_group.distance(comp_group)
			rot_same = rot_target == rot_comp
			ref_same = ref_target == ref_comp
			gref_same = gref_target == gref_comp
			tile_same = tile_target == tile_comp
			correct = 1 if result.correct == 1 else 0  
			csv.append(target_group.group+","+comp_group.group+","+str(rot_same)+","+str(ref_same)+","+str(gref_same)+","+str(tile_same)+","+user_id+","+str(task_id)+","+str(distance)+","+str(correct))
		context['csv'] = csv
		return context

class BreakView(TemplateView):
	template_name = 'break.html'
	def dispatch(self, *args, **kwargs):
		if ('turk_id' not in self.request.session or 'task' not in self.request.session):
			return HttpResponseRedirect(reverse_lazy('intro'))
		user = models.PUser.objects.get(pk = self.request.session['turk_id'])
		if not user.breakTime:
			return HttpResponseRedirect(reverse_lazy('task'))
		else:
			user.breakTime = None
			user.save()
		return super(BreakView, self).dispatch(*args, **kwargs)
	def get_context_data(self, **kwargs):
		context = super(BreakView, self).get_context_data(**kwargs)
		context['return_url'] = reverse_lazy('task')
		return context


class TaskView(TemplateView):
	template_name = 'task.html'
	def dispatch(self, *args, **kwargs):
		if ('turk_id' not in self.request.session or 'task' not in self.request.session):
			return HttpResponseRedirect(reverse_lazy('intro'))
		if self.getNumTasks() == 0 or models.PUser.objects.get(pk=self.request.session['turk_id']).dead is True:
			return HttpResponseRedirect(reverse_lazy('end'))
		elif self.getNumTasks() == 136 and models.PUser.objects.get(pk=self.request.session['turk_id']).breakTime is False:
			if 'stime' in self.request.session:
				self.request.session.pop('stime', None)
			user = models.PUser.objects.get(pk=self.request.session['turk_id']) 
			user.breakTime = True
			user.save()
			return HttpResponseRedirect(reverse_lazy('break'))
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
		user = models.PUser.objects.get(pk = request.session['turk_id'])
		thisTask = self.dicToTask(self.request.session['task'])
		if request.POST.get("top.x"): #and not self.taskDone(user, thisTask):
			result = models.Result(selector=user, task=thisTask, choice=models.Result.CHOICES[0][0], elapsedTime=ttime)
			result.setCorrect()
		elif request.POST.get("bottom.x"):# and not self.taskDone(user, thisTask):
			result = models.Result(selector=user, task=thisTask, choice=models.Result.CHOICES[1][0], elapsedTime=ttime)
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
		kwargs = dict()
		kwargs['numTasks'] = numTasks
		return render(request, self.template_name, self.get_context_data(**kwargs))
	def taskDone(self, user, thisTask):
		return models.Result.objects.filter(selector=user, task=thisTask).exists()
	def getIncomplete(self):
		return models.PUser.objects.get(pk=self.request.session['turk_id']).taskset.getIncompleteTasks().all()
	def getNumTasks(self):
		incompleteTasks = self.getIncomplete()
		return incompleteTasks.count()

	def dicToTask(self, taskjson):
		return models.Task.objects.get(choice1__id=taskjson['choice1'], choice2__id=taskjson['choice2'], test_image__id=taskjson['test_image'])
	

class InitView(TemplateView):
	#first, need to initialize the images. Next, need to initialize the tasks.
	#the images is just a simple matter of performing manual insertions 	
	template_name = 'init.html'
	def get_context_data(self, **kwargs):
		#print("we are calling a thing")
		context = super(InitView, self).get_context_data(**kwargs)
		context['expected_images'] = 85
		context['actual_images'] = models.Image.objects.all().count()
		context['expected_tasks'] = 54400 #17 * 100 * 16 * 99 * 100 * 2
		context['actual_tasks'] = models.Task.objects.all().count()
		context['expected_distances'] = 289
		context['actual_distances'] = models.Distance.objects.all().count()
		context['numsets'] = models.TaskSet.objects.filter(puser=None).count()
		return context
