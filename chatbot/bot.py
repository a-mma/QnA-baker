from __future__ import print_function

from database.database import DB
from utils import vectors as lalg
import numpy as np

class Bot:
	'bot class'

	def __init__(self, args):
		self.args = args
		
		self.context_limit = self.args['context_limit']
		self.message_context = []
		# create database instance
		self.db = DB(self.args['files'], self.args['dim'], self.context_limit)

	def preloadDB(self):
		# preload vectors
		self.db.preloadDB(self.args['lang'])

	def fillContext(self, message_vec):
		self.message_context.append(message_vec)
		self.message_context = self.message_context[-self.context_limit:]

	def answer(self, question):
		message_vec = self.db.string2contextvec(question, self.args['dim'])

		# add question to the message context
		self.fillContext(message_vec)
		
		# build question index
		question_index = self.db.loadQuestionIndex(question)

		bot_dialog_context = np.divide(np.sum(np.array(self.message_context), axis=0), self.context_limit)
		# sort question index based on similarity to asked question
		sortedQI = lalg.getSortedQuestionIndex(bot_dialog_context, question_index)

		# print(sortedQI)

		if len(sortedQI) > 0:
			final_answer = self.db.loadAnswerByIndex(sortedQI[0])
		else:
			final_answer = "hmm.. hmm.."


		
		# fetch top 10 Q&A pair for sorted QIndex
		# fetched_pairs = []
		# for i in range(10):
		# 	fetched_pairs.append(self.db.dialog_pair[sortedQI[i]].split('\t'))
		
		# # create context vectors for each fetched pair
		# fetched_pairs_context_vec = []
		# for pair in fetched_pairs:
		# 	sum_ = np.zeros((self.args['dim'],), dtype=float)
		# 	count = 0
		# 	for w_question_ in pair:
		# 		for w_question in w_question_.split(' '):
		# 			try:
		# 				tmp = np.array(self.db.context_vectors[w_question], dtype=float)
		# 				if w_question is not '':
		# 					count = count + 1
		# 					sum_ = np.add(sum_, tmp)
		# 			except:
		# 				print(w_question)
		# 	if count > 0:
		# 		sum_ = np.divide(sum_, count)
		# 	fetched_pairs_context_vec.append(sum_)

		# # create context vector for user messages including last one
		# input_message_context_vec = np.zeros((self.args['dim'],), dtype=float)
		# count = 0

		# for input_m in self.message_context:
		# 	for w_question in input_m.split(' '):
		# 		try:
		# 			tmp = np.array(self.db.context_vectors[w_question], dtype=float)
		# 			if w_question is not '':
		# 				count = count + 1
		# 				input_message_context_vec = np.add(input_message_context_vec, tmp)
		# 		except:
		# 			print(w_question)
		# if count > 0:
		# 	input_message_context_vec = np.divide(input_message_context_vec, count)

		# # sort question pairs based on similarity to user messages context
		# final_answer_order = lalg.getSortedQuestionIndex(input_message_context_vec, np.array(fetched_pairs_context_vec))
		# final_answer = fetched_pairs[final_answer_order[0]][1]

		# add question to the message context
		message_vec = self.db.string2contextvec(final_answer, self.args['dim'])
		self.fillContext(message_vec)
		return final_answer