import subprocess, collections, os, random
from symper import settings
from comparisons.models import Image, TaskSet, Task, Distance

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

class Graph:
	def __init__(self):
		self.nodes = set()
		self.edges = collections.defaultdict(list)
		self.distances = {}
 
	def add_node(self, value):
		self.nodes.add(value)
 
	def add_edge(self, from_node, to_node, distance):
		self.edges[from_node].append(to_node)
		self.edges[to_node].append(from_node)
		self.distances[(from_node, to_node)] = distance
		self.distances[(to_node, from_node)] = distance

def init_sym_graph():
	sym = Graph()
	sym.add_node(Image.P1)
	sym.add_node(Image.P2)
	sym.add_node(Image.P3)
	sym.add_node(Image.P6)
	sym.add_node(Image.P6M)
	sym.add_node(Image.P3M1)
	sym.add_node(Image.P31M)
	sym.add_node(Image.CMM)
	sym.add_node(Image.PMM)
	sym.add_node(Image.PMG)
	sym.add_node(Image.P4)
	sym.add_node(Image.P4G)
	sym.add_node(Image.P4M)
	sym.add_node(Image.PGG)
	sym.add_node(Image.PG)
	sym.add_node(Image.PM)
	sym.add_node(Image.CM)
	sym.add_edge(Image.P4M, Image.P4G, 1)
	sym.add_edge(Image.P4G, Image.P4, 1)
	sym.add_edge(Image.P4G, Image.CMM, 1)
	sym.add_edge(Image.P4, Image.P2, 1)
	sym.add_edge(Image.P2, Image.P1, 1)
	sym.add_edge(Image.CMM, Image.PMM, 1)
	sym.add_edge(Image.PMM, Image.PMG, 1)
	sym.add_edge(Image.PMG, Image.PGG, 1)
	sym.add_edge(Image.PGG, Image.PG, 1)
	sym.add_edge(Image.PG, Image.PM, 1)
	sym.add_edge(Image.PG, Image.P1, 1)
	sym.add_edge(Image.PMG, Image.CM, 1)
	sym.add_edge(Image.CM, Image.PM, 1)
	sym.add_edge(Image.P6M, Image.P6, 1)
	sym.add_edge(Image.P6M, Image.CMM, 1)
	sym.add_edge(Image.P6M, Image.P3M1, 1)
	sym.add_edge(Image.P6M, Image.P31M, 1)
	sym.add_edge(Image.P6, Image.P2, 1)
	sym.add_edge(Image.P6, Image.P3, 1)
	sym.add_edge(Image.P3M1, Image.P3, 1)
	sym.add_edge(Image.P3M1, Image.CM, 1)
	sym.add_edge(Image.P3M1, Image.P31M, 1)
	sym.add_edge(Image.P31M, Image.P3, 1)
	sym.add_edge(Image.P31M, Image.CM, 1)
	sym.add_edge(Image.P3, Image.P1, 1)
	return sym

def init_sample_graph():
	sym = Graph()
	sym.add_node("hi")
	sym.add_node("bye")
	sym.add_node("trees")
	sym.add_edge("hi", "bye", 5)
	sym.add_edge("hi", "trees", 4)
	return sym

def dijsktra(graph, initial):	
	visited = {initial: 0}
	path = {}
 
	nodes = set(graph.nodes)

	while nodes: 
		min_node = None
		for node in nodes:
			if node in visited:
				if min_node is None:
					min_node = node
				elif visited[node] < visited[min_node]:
					min_node = node
 
		if min_node is None:
			break
 
		nodes.remove(min_node)
		current_weight = visited[min_node]
 
		for edge in graph.edges[min_node]:
			weight = current_weight + graph.distances[(min_node, edge)]
			if edge not in visited or weight < visited[edge]:
				visited[edge] = weight
				path[edge] = min_node
 
	return visited, path

def all_dijsktra(graph):
	visited = {}
	path = {}
	nodes = set(graph.nodes)
	for node in nodes:
		visited[node], path[node] = dijsktra(graph, node)
	return visited, path

def make_dist_fixtures():
	fw = open('dist_fixtures.json', 'w')
	sym = init_sym_graph()
	distances, paths = all_dijsktra(sym)
	#we are now iterating over every node's dictionary
	lines = []
	lines.append('[\n')
	i = 1
	for init_node, dic in distances.items():
		for end_node, dist in dic.items():
	#		d = Distance(from_group = init_node, to_group = end_node, distance = dist)
	#		d.save()
			lines.append('\t{\n')
			lines.append('\t\t"model": "comparisons.distance",\n')
			lines.append('\t\t"pk": '+str(i)+',\n')
			lines.append('\t\t"fields": {\n')
			lines.append('\t\t\t"from_group": "'+init_node+'",\n')
			lines.append('\t\t\t"to_group": "'+end_node+'",\n')
			lines.append('\t\t\t"distance": "'+str(dist)+'"\n')
			lines.append('\t\t}\n')
			lines.append('\t},\n')
			i = i + 1
	lines[len(lines)-1] = lines[len(lines)-1][:-2] + "\n"
	lines.append(']') 
	fw.writelines(lines)
	fw.close()


def make_dist():
	sym = init_sym_graph()
	distances, paths = all_dijsktra(sym)
	for init_node, dic in distances.items():
		for end_node, dist in dic.items():
			d = Distance(from_group = init_node, to_group = end_node, distance = dist)
			d.save()

def make_img_fixtures():
	fw = open('img_fixtures.json', 'w')
	lines = []
	lines.append('[\n')
	i = 1
	sym_folder = "new_images"
	baseDir = settings.MEDIA_ROOT
	for dirName, subDirList, fileList in os.walk(baseDir):
		if (sym_folder not in dirName):
			continue
		for image in fileList:
			image_group = image.split('_')[0]
			lines.append('\t{\n')
			lines.append('\t\t"model": "comparisons.image",\n')
			lines.append('\t\t"pk": '+str(i)+',\n')
			lines.append('\t\t"fields": {\n')
			lines.append('\t\t\t"group": "'+image_group+'",\n')
			lines.append('\t\t\t"image": "'+settings.MEDIA_URL+'/'+sym_folder+'/'+image+'"\n')
			lines.append('\t\t}\n')
			lines.append('\t},\n')
			i = i + 1
	lines[len(lines)-1] = lines[len(lines)-1][:-2] + "\n"
	lines.append(']')
	fw.writelines(lines)
	fw.close()

def make_images():
	baseDir = settings.MEDIA_ROOT
	sym_folder = "final"
	for dirName, subdirList, fileList in os.walk(baseDir):
		if sym_folder not in dirName:
			continue
		for image in fileList:
			image_group = image.split('_')[0]
			image_obj = Image(group = image_group, image=settings.MEDIA_URL+"/"+sym_folder+"/"+image)
			image_obj.save()

def make_tasks():
	for group in Image.GROUPS:
		sett = list(Image.objects.filter(group = group[0]))
		for imag in sett:
			for other_group in Image.GROUPS:
				if group == other_group:
					continue
				otherSett = list(Image.objects.filter(group = other_group[0]))
				for other_imag in sett:
					if other_imag == imag:
						continue
					for third_imag in otherSett:
						task_obj = Task(test_image = imag, choice1 = third_imag, choice2 = other_imag)
						task_obj.save()
						task_obj_r = Task(test_image = imag, choice1 = other_imag, choice2 = third_imag)
						task_obj_r.save()

def make_sets():
	for i in range(100):
		taskset = TaskSet()
		taskset.save()
		for group in Image.GROUPS:
			qset = Task.objects.filter(test_image__group = group[0])
			for other_group in Image.GROUPS:
				if group == other_group:
					continue
				queryset = qset.filter(choice1__group = other_group[0]) | qset.filter(choice2__group = other_group[0])
				choose = random.randint(0, queryset.count()-1)
				taskset.tasks.add(queryset[choose])
				taskset.save()	

def make_all():
	#make_images()
	#make_tasks()
	make_sets()
	#make_dist()
