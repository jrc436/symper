from comparisons import models
from django.db.models import Count, Max
from decimal import Decimal

def filteredUsers(trial):
    paidUsers = models.PUser.objects.filter(provisional=False)
    clicked_corrects = paidUsers.annotate(Count('result')).exclude(result__count__lt=272).exclude(result__count__gte=340)
    validations = models.Validation.objects.filter(pk__in=[ user.pk for user in clicked_corrects ])
    unrandom_vals = validations.exclude(percentTop__gte=Decimal('0.6')).exclude(percentBottom__gte=Decimal('0.6'))
    timedout_vals = unrandom_vals.exclude(percentTimeout__gte=Decimal('0.2'))
    secondfilter = clicked_corrects.filter(pk__in=[ v.pk for v in timedout_vals ])
    if trial == 1:
        demographics = models.Demographics.objects.all()
        thirdfilter = secondfilter.exclude(pk__in=[ dem.pk for dem in demographics ])
    elif trial == 2:
        demographics = models.Demographics.objects.all()
        thirdfilter = secondfilter.filter(pk__in=[ dem.pk for dem in demographics ])
    else:
        thirdfilter = secondfilter
    return thirdfilter



def filteredResults(filteredUsers):
    relResults = models.Result.objects.filter(selector__in=[ user for user in filteredUsers ])
    return relResults



def demoObj(filteredUsers):
    demographics = models.Demographics.objects.all()
    filtered = demographics.filter(pk__in=[ user.pk for user in filteredUsers ])
    return filtered



def getCSV(filteredUsers):
    csv = []
    csv.append('group-target,group-distracter,user_id,tech-correct,time\n')
    relResults = filteredResults(filteredUsers)
    for result in relResults:
        target_group = result.task.test_image
        comp_group = result.task.choice2 if result.task.test_image.group == result.task.choice1.group else result.task.choice1
        correct = 1 if result.tech_correct == 1 else 0
        user_id = result.selector.pk
	time = result.elapsedTime
        csv.append(target_group.group + ',' + comp_group.group + ',' + str(user_id) + ',' + str(correct)+","+str(time)+"\n")
    return csv

def getAccCsv(filteredUsers, reverse=False):
	relResults = filteredResults(filteredUsers)
	csv = []
	csv.append('group1,group2,correct\n')
	for t in range(0,len(models.Image.GROUPS)):
		for c in range(t+1,len(models.Image.GROUPS)):
			testTset = relResults.filter(task__test_image__group = models.Image.GROUPS[t][0])
			compareTCset = testTset.filter(task__choice1__group = models.Image.GROUPS[c][0]) | testTset.filter(task__choice2__group = models.Image.GROUPS[c][0])
			testCset = relResults.filter(task__test_image__group = models.Image.GROUPS[c][0])
			compareCTset = testCset.filter(task__choice1__group = models.Image.GROUPS[t][0]) | testCset.filter(task__choice2__group = models.Image.GROUPS[c][0])
		
			numCorrect = compareTCset.filter(correct = 1).count() 
			totalNum = compareTCset.all().count() 
			if reverse:
				numCorrect += compareCTset.filter(correct = 1).count()
				totalNum += compareCTset.all().count()
	
			accuracy = float(numCorrect) / float(totalNum)
			csv.append(models.Image.GROUPS[t][0]+","+models.Image.GROUPS[c][0]+","+str(accuracy)+"\n")
	return csv	


def getDemo(users):
    csv = []
    csv.append('user_id,first_lang,edu-years,gender,age\n')
    allDemo = demoObj(users)
    for demo in allDemo:
        csv.append(str(demo.turk_id) + ',' + demo.first_language + ',' + str(demo.education_years) + ',' + demo.gender + ',' + str(demo.age)+"\n")
    return csv

def accRun():
	fUsers = filteredUsers(0)
	csv = getAccCsv(fUsers)
	f = open('full-symacc.csv', 'w')
	f.writelines(csv)

def run():
    fUsers = filteredUsers(1)
    csv = getCSV(fUsers)
    f = open('trial1.csv', 'w')
    f.writelines(csv)
    fUsers = filteredUsers(2)
    csv = getCSV(fUsers)
    f = open('trial2.csv', 'w')
    f.writelines(csv)
    csv = getDemo(fUsers)
    f = open('demo-for-trial2.csv', 'w')
    f.writelines(csv)
