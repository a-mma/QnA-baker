from __future__ import print_function
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def getSortedQuestionIndex(sentance_vec_in, question_index_in):
	if not (len(question_index_in) == 0 or len(sentance_vec_in) == 0):
		similarity = cosine_similarity([sentance_vec_in], question_index_in)
		sorted_question_index = np.argsort(-similarity)
		return sorted_question_index[0]
	else:
		return []