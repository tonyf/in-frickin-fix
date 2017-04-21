import spacy
import os
import sys
import re
import traceback
import random
# import language_check
import copy
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.preprocess import *
from lib.antonyms import *

root_dir = "data/"
questions_yn = []
questions_wh = []
questions_subj_verb_obj = []
set_list = ["test_set","set1","set2","set3","set4"]
nlp = spacy.load("en")
testing = False
question_answers = {}

#Dict of final questions and their scores
final_questions = {}

#Call the spacy preprocess module
def preprocess_question(setlist, nlp):
	set_dict = preprocess_docs(root_dir,setlist,nlp)
	return set_dict

#Removes all excess whitespace in the sentence passed to it
def refine(q):
	q_ = re.sub(' +',' ',q)
	q1 = q_.replace(" 's ","'s ")
	q2 = q1.replace(" , ",", ")
	q3 = q2.replace(".?","?")
	q4 = q3.replace(" ?","?")
	q5 = q4.replace("Who,","Who")
	q6 = q5.replace("What,","What")
	q7 = q6.replace("When,","When")
	return q7

def get_subphrase(node, word_list, sent):
	begin = sent[0].i
	word_list.append(node)
	for child in node.children:
		get_subphrase(child,word_list,sent)
	min_pos = float('inf')
	max_pos = -float('inf')
	for word in word_list:
		if word.i < min_pos:
			min_pos = word.i
		if word.i > max_pos:
			max_pos = word.i
	new_word_list = []
	for i in xrange(max_pos - min_pos + 1):
		new_word_list.append(sent[i+min_pos - begin])
	return new_word_list

def concat_subphrase(node, word_list):
	#print word_list
	word_list.append(node)
	for child in node.children:
		concat_subphrase(child,word_list)

def wh_questions(doc):
	sents = doc.sents
	for s in sents:

		try:
			mv = s.root
			if mv.pos_!="VERB":
				continue

			wh1 = aux = None

			for child in mv.children:
				if child.dep_ == "nsubj":
					subj_list = []
					subj_list = get_subphrase(child,subj_list,s)
					# subj_list.reverse()
					for node in subj_list:
						if node.ent_type_ in ["PERSON","ORG"]:
							wh = "Who"
						elif node.ent_type_ == "GPE":
							wh = "Which place"
						else:
							wh = "What"

				elif child.dep_ == "nsubjpass":
					subj_list = []
					subj_list = get_subphrase(child,subj_list,s)
					# subj_list.reverse()
					for node in subj_list:
						if node.ent_type_ in ["PERSON","ORG"]:
							wh = "Who"
						elif node.ent_type_ == "GPE":
							wh = "Which place"
						else:
							wh = "What"

				elif child.dep_ == "aux" or child.dep_=="auxpass":
					aux = child.string

				if child.dep_ == "prep":
					subj_list_prep = []
					subj_list = get_subphrase(child,subj_list_prep,s)
					for node in subj_list_prep:
						if node.ent_type_ == "DATE":
							wh1 = "When"

			rem2 = " "
			flag = 0
			subj_size = len(subj_list)
			for word in s:
				if str(word).isspace():
					continue
				if word == subj_list[subj_size-1]:
					flag = 1
					continue
				if flag==1:
					rem2 += word.string

			Q = wh+rem2
			if Q.strip().endswith('.'):
				Q = Q[:-1]
				Q+="?"
			Q = refine(Q)

			questions_wh.append(Q)
			question_answers[Q] = s

			#wh1 - When questions
			list_of_rem = rem2.strip().split(' ',1)
			if wh1 is not None and len(list_of_rem)>1:
				rem_when = " "
				remaining = rem2.strip().split(' ', 1)[1]
				if remaining.strip().endswith('.'):
					remaining = remaining[:-1]
					remaining+="?"

				subject = ""
				for s1 in subj_list:
					s1 = str(s1)
					subject+=s1+" "

				#Questions of type "On 25th Nov, SUBJ was blah blah blah" -> "When was SUBJ blah..?"
				if aux:
					Q1 = str(wh1+" "+aux+" "+subject+" "+remaining)
					Q1 = refine(Q1)
					questions_wh.append(Q1)
					question_answers[Q1] = s

				#Questions of type "On 25th Nov, SUBJ played blah blah blah" -> "When did SUBJ play blah..?"
				else:
					tense = None
					if mv.tag_=="VBD" or mv.tag_=="VBN":
					       tense = "past"
					else:
					       tense = "present"

					if tense == "past":
					       aux = "did"

					verb = mv.string

					#Modify the verb
					verb = mv.lemma_
					Q1 = str(wh1+" "+aux+" "+subject+" "+verb+" "+remaining)
					Q1 = refine(Q1)
					questions_wh.append(Q1)
					question_answers[Q1] = s

		except Exception:
			pass		



def yesno_questions(doc):
	sents = doc.sents
	for s in sents:
		mv = s.root
		if mv.pos_!="VERB":
			continue

		aux = neg = subj =  number = None
		position = int(mv.i)
		#NOTE: For now, assume a sentence has max of one aux, one neg
		for child in mv.children:

			if child.dep_ == "nsubj" or child.dep_ == "nsubjpass":
				if child.tag_ == "NNP" or child.tag_ == "NN":
					number = "sing"
				else:
					number = "plural"

				subj_list = []
				subj_list = get_subphrase(child,subj_list,s)
				#Go through every word in sub phrase and remove caps if not a named entity
				new_subj_list = []
				for node in subj_list:
					if node.ent_type_:
						sub_word = str(node.string.capitalize())
					else:
						sub_word = str(node.string.lower())
					new_subj_list.append(sub_word)

				# new_subj_list.reverse()
				subj = " ".join(new_subj_list)

			elif child.dep_ == "neg":
				neg = child.string

			elif child.dep_ == "aux" or child.dep_=="auxpass":
				aux = child.string

		if subj is None:
			continue

		#Using the position of the root verb, retrieve the rest of the sentence
		#NOTE: How to prevent coref resolution from happening here?
		position = mv.i + 1
		remaining = ""
		while str(doc[position]) != ".":
			remaining += " " + str(doc[position])
			position += 1

		#NOTE: Add capitalization -- DONE
		#NOTE: If the subj is not a named entity, remove capitalization --DONE
		#Use the not to generate more questions and to store the right answer
		if aux:
			aux = aux.capitalize()
			Q = str(aux+" "+subj+" "+mv.string+" "+remaining+"?")
			Q = refine(Q)
			questions_yn.append(Q)
			question_answers[Q] = s

		else:
			tense = None
			isToBe = False
			if mv.tag_=="VBD" or mv.tag_=="VBN":
				tense = "past"
			else:
				tense = "present"
			if mv.lemma_=="be":
				isToBe = True

			if tense == "present" and number == "sing":
				aux = "Does"
			elif tense == "present" and number == "plural":
				aux = "Do"
			elif tense == "past":
				aux = "Did"

			verb = mv.string

			if isToBe:
				verb = verb.capitalize()
				Q = str(verb+" "+subj+" "+remaining+"?")
				Q = refine(Q)
				questions_yn.append(Q)
				question_answers[Q] = s
			#Modify the verb
			else:
				verb = mv.lemma_
				aux = aux.capitalize()
				prob = random.randint(0,100)
				if prob > 50:
					Q = str(aux+" "+subj+" not "+verb+" "+remaining+"?")
				else:
					Q = str(aux+" "+subj+" "+verb+" "+remaining+"?")
				Q = refine(Q)
				questions_yn.append(Q)
				question_answers[Q] = s


"""
Function to convert yes questions to no 
questions by fudging dates/numbers
(with a 50% prob of converting) - TBD
"""
def fudge_questions(questions):

	months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
	new_qs = []
	ords = ['1st','14th','72nd','90th']

	for quest in questions:
		old_q = quest
		n = quest
		try:
			n = unicode(quest, encoding = 'ascii', errors = 'ignore')
		except Exception:
			pass
		doc = nlp(n)
		for q in doc.sents:
			try:
				for word in q:
					# print word,word.ent_type_
					if word.ent_type_ == "ORDINAL":
						ran = random.randint(0,3)
						num = str(ords[ran])
						quest = quest.replace(str(word),num)

					if word.ent_type_ in ["CARDINAL","MONEY"]:
						numb = int(word.string)
						new_numb = str(numb + 1)
						quest = quest.replace(str(word),new_numb)

					if word.ent_type_ == "DATE":
						if str(word) in months:
							pos = word.i
							ind = months.index(str(word))
							new_ind = ind + 3
							if new_ind > 11:
								new_ind = new_ind % 11
							new_month = months[new_ind]
							quest = quest.replace(str(word),new_month)
			except:
				pass

		new_qs.append(quest)
		s = question_answers[old_q]
		del question_answers[old_q]
		question_answers[quest] = s

	questions_yn = []
	questions_yn = copy.deepcopy(new_qs)
	return new_qs


def subj_verb_obj_questions(doc):
	sents = doc.sents
	for s in sents:
		mv = s.root
		# print "-----------"
		# print s
		if mv.pos_!="VERB":
			continue

		aux = neg = subj = obj = iobj = pobj = number = prep = None

		for child in mv.children:

			if child.dep_ == "nsubj" or child.dep_ == "nsubjpass":
				if child.tag_ == "NNP" or child.tag_ == "NN":
					number = "sing"
				else:
					number = "plural"

				subj_list = []
				subj_list = get_subphrase(child,subj_list,s)
				#Go through every word in sub phrase and remove caps if not a named entity
				new_subj_list = []
				for node in subj_list:
					if node.ent_type_:
						sub_word = str(node.string.capitalize())
					else:
						sub_word = str(node.string.lower())
					new_subj_list.append(sub_word)

				# new_subj_list.reverse()
				subj = " ".join(new_subj_list)

			elif child.dep_ == "dobj":
				if child.tag_ == "NNP" or child.tag_ == "NN" or child.tag_ == "NNPS" or child.tag_ == "NNS":
					dobj = child.string
					obj_list = []
					obj_list = get_subphrase(child,obj_list,s)
					new_obj_list = []
					for node in obj_list:
						if node.ent_type_:
							obj_word = str(node.string.capitalize())
						else:
							obj_word = str(node.string.lower())
						new_obj_list.append(obj_word)
					# new_obj_list.reverse()
					obj = " ".join(new_obj_list)

			elif child.dep_ == "prep":
				prep = child.string
				prep_list = []
				prep_list = get_subphrase(child,prep_list,s)
				new_prep_list = []
				for node in prep_list:
					if node.ent_type_:
						prep_word = str(node.string.capitalize())
					else:
						prep_word = str(node.string.lower())
					new_prep_list.append(prep_word)
				prep = " ".join(new_prep_list)

			elif child.dep_ == "neg":
				neg = child.string

			elif child.dep_ == "aux" or child.dep_=="auxpass":
				aux = child.string

			# TODO: deal with this better
			elif child.dep_ == 'iobj' or child.dep_ == 'dative':
				iobj = "exists"

			elif child.dep_ == 'pobj':
				pobj = "exists"

		if subj is None or obj is None or not (iobj is None) or not (pobj is None):
			continue

		if aux:
			#aux = aux.capitalize()
			if prep is None:
				Q = str("What "+aux+" "+subj+" "+mv.string+"?")
			else:
				Q = str("What "+aux+" "+subj+" "+mv.string+" "+prep+"?")
			Q = refine(Q)
			questions_subj_verb_obj.append(Q)
			question_answers[Q] = s

		else:
			tense = None
			isToBe = False
			if mv.tag_=="VBD" or mv.tag_=="VBN":
				tense = "past"
			else:
				tense = "present"
			if mv.lemma_=="be":
				isToBe = True

			if tense == "present" and number == "sing":
				aux = "does"
			elif tense == "present" and number == "plural":
				aux = "do"
			elif tense == "past":
				aux = "did"

			verb = mv.string

			if isToBe:
				#verb = verb.capitalize()
				if prep is None:
					Q = str("What "+verb+" "+subj+"?")
				else:
					Q = str("What "+verb+" "+subj+" "+prep+"?")

				Q = refine(Q)
				questions_subj_verb_obj.append(Q)
				question_answers[Q] = s
			#Modify the verb
			else:
				verb = mv.lemma_
				#aux = aux.capitalize()
				if prep is None:
					Q = str("What "+aux+" "+subj+" "+verb+"?")
				else:
					Q = str("What "+aux+" "+subj+" "+verb+" "+prep+"?")
				Q = refine(Q)
				questions_subj_verb_obj.append(Q)
				question_answers[Q] = s


def replace_superlatives_comparatives():
	thresh = 0.25
	sups_dict = get_superlatives()
	comps_dict = get_comparatives()
	new_questions = {}
	for question, score in final_questions.iteritems():
		old_q = question
		sup = False
		split_question = question.split()
	# TODO: make better
		if score == 1:
			for i, word in enumerate(split_question):
				if word in sups_dict:
					sup = True
					if random.random() > thresh:
						split_question[i] = sups_dict[word]
				if word in comps_dict:
					comp = True
					if random.random() > thresh:
						split_question[i] = comps_dict[word]
		new_q = (" ").join(split_question)
		new_questions[new_q] = score
		s = question_answers[old_q]
		del question_answers[old_q]
		question_answers[new_q] = s
		# if sup:
		# 	print (" ").join(split_question)
	return new_questions


"""
Function that determines if a question needs to be removed
RETURN 1 IF QN SHOULD BE REMOVED
Current criteria for removing are:
1. Too short (< 5) or too long (> 20)
2. If the subject is: "he/she/him/her/it/its/it's/"
"""
def remove(question):
	pronouns = ['he','him','his','she','her','hers','they','them','these','this','theirs','it','its']
	puncs = [',',';']

	pronoun_present = 0
	person_present = 0
	pronoun_position = 0
	person_postion = 0
	who = 0
	num_puncs = 0

	if question.split()[0] == "Who":
		who = 1

	for char in question:
		if char in puncs:
			num_puncs += 1

	if num_puncs > 3:
		return 1

	pos = 0
	for word in question.split():
		pos += 1
		if word.lower() in pronouns:
			pronoun_present = 1
			pronoun_position = pos

	n = question
	try:
			n = unicode(question, encoding = 'ascii', errors = 'ignore')
	except Exception:
			pass

	doc = nlp(n)
	for q in doc.sents:
		first = 0
		pos = 0
		for word in q:
			pos += 1
			if word.ent_type_ == "PERSON":
				person_present = 1
				person_postion = pos
				break

			if first == 0:
				first = 1
				continue

			if word.string.islower() == False:
				person_present = 1
				person_postion = pos
				break

	#If NE-person is present after the pronoun - remove!
	if person_present == 1 and pronoun_present == 1:
		if pronoun_position < person_postion and who == 0:
			return 1

	#If no NE - person is present, but a pronoun is present, remove!
	if person_present == 0 and pronoun_present == 1 and who == 0:
		return 1

	if len(question.split()) < 5 or len(question.split()) >= 20:
		return 1

	return 0


"""
If y/n question, score is 1
If when question, score is 4
If sub_verb question, score is 3
Questions that need to be REMOVED are given a score of 0
Default score is 5
"""
def score(question,id):

	#Check qn length and presence of pronouns
	if remove(question) == 1:
		return 0

	if id == 3:
		return 3

	if id == 2:
		return 2

	if id == 1:
		return 1

	if "when" in question.split():
		return 4

	return 5



def evaluate_questions(qn_set,id):
	for question in qn_set:
		sc = score(question,id)
		final_questions[question] = sc



def main():
	random.seed(17)
	global testing
	global questions_yn
	_,doc = read_doc(sys.argv[1])
	doc = preprocess(doc, nlp)
	num_questions = int(sys.argv[2])

	if sys.argv[0].startswith("python"):
		if len(sys.argv) > 3:
			testing = bool(sys.argv[3])
	else:
		if len(sys.argv) > 2:
			testing = bool(sys.argv[2])

	try:
		yesno_questions(doc)
		questions_yn = fudge_questions(questions_yn)
		evaluate_questions(questions_yn,1)
		wh_questions(doc)
		evaluate_questions(questions_wh,2)
		subj_verb_obj_questions(doc)
		evaluate_questions(questions_subj_verb_obj,3)
	except Exception,e:
		print(traceback.format_exc())

	final_questions = replace_superlatives_comparatives()


	final_q = []
	count = 0
	for key, value in sorted(final_questions.items(), key=lambda x: random.random()):
		if value != 0:
			count += 1
			if count > num_questions:
				break
			print key
			final_q.append(key)
			if count == num_questions:
				break

	if testing:
		f = open("lib/questions_answers.txt", "w")
		for i in range(num_questions):
			if (i >= len(final_q)):
				break
			f.write(final_q[i] + "\n" + str(question_answers[final_q[i]]) + "\n")


main()
