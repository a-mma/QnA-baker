from __future__ import print_function
import numpy as np
from database.whooshDB import WhooshDB as wDB

class DB:
	'database class'

	def __init__(self, files, dim, context_limit):
		self.files = files
		self.dim = dim
		self.context_limit = context_limit
		# create used DBs
		self.dialogsDB = wDB(self.files['whoosh_index'], "dialogs", self.files['schema_index'])
		self.contextvecDB = wDB(self.files['whoosh_index'], "embedding", self.files['context_vec_index'])
		# references
		self.question_index = []

	def loadContextVectors(self, file, dim):
		print('INITIALIZING: loading context vectors')
		with open(file) as fp:  
			for context_v in fp:
				split = context_v.strip(' ').strip('\n').split('\t')
				self.contextvecDB.writeData([{"key":split[0], "vector": split[1:dim+1]}])
		print('INITIALIZING: finished loading context vectors')

	def commitContextVectors(self):
		self.contextvecDB.commitData()
		print('context commit done')

	def string2contextvec(self, string, dim):
		sum_ = np.zeros((dim,), dtype=float)
		count = 0
		for word in string.lower().split(' '):
			result = self.contextvecDB.readData({"query_str":word, "query_field":u"key"})
			if len(result) > 0:
				vector = np.array(result[0]["vector"]).astype(np.float)
				sum_ = np.add(sum_, vector)
				count = count + 1
			else:
				print(word, result)
		if count > 0:
				sum_ = np.divide(sum_, count)
		return sum_

	def loadDialogs(self, file, lang, dim):
		print('INITIALIZING: loading dialogs')
		turn = 0
		diag = 0
		context_t = []
		with open(file) as fp:  
			for dialog in fp:
				dialog = dialog.strip(' ').strip('\n')
				if dialog != '':
					vector_t = self.string2contextvec(dialog, dim)
					context_t.append(vector_t)
					# limit context
					context_t = context_t[-self.context_limit:]
					# create dialog context vector
					vector = np.divide(np.sum(np.array(context_t), axis=0), self.context_limit)
					# write data to DB
					self.dialogsDB.writeData([{
						"dialog": dialog,
						"lang": lang,
						"turn": turn,
						"vector": vector
					}])
					turn = turn + 1
				else:
					# limit context
					# context_t = []
					diag = diag + 1
				# print(turn, diag)
		print('INITIALIZING: finished loading dialogs')

	def commitDialogs(self):
		self.dialogsDB.commitData()
		print('dialog commit done')

	def buildQuestionIndex(self, query):
		self.question_index = self.dialogsDB.readData({"query_str":query, "query_field":u"dialog"})
		print([d["dialog"] for d in self.question_index])
		return np.array([d["vector"] for d in self.question_index])

	def preloadDB(self, lang):
		self.loadContextVectors(self.files['vContext'] , self.dim)
		self.commitContextVectors()
		self.loadDialogs(self.files['dialogs'], lang, self.dim)
		self.commitDialogs()

	def loadQuestionIndex(self, question):
		return self.buildQuestionIndex(question)

	def loadAnswerByIndex(self, index):
		index_ = self.question_index[index]["turn"]
		answer = self.dialogsDB.readData({"query_str":str(index_+1), "query_field":u"turn"})
		return answer[0]["dialog"]
