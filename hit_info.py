class hit_info():
	def __init__(self, url, title, description, keywords, layoutid, reward):
		self.title = title
		self.description = description
		self.keywords = keywords
		self.layoutid = layoutid
		self.reward = reward


def get_comparisons(layout_id):
	return hit_info(url = "http://cc.ist.psu.edu/symper/intro/", title = "Categorize images of patterns - up to $4 paid", description = "Find patterns that seem similar in this research study", keywords = ['images', 'bonus', 'patterns', 'research'], layoutid=layout_id, reward = 2.0)
	
