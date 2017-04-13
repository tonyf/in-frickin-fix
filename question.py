import spacy
import os
import sys
import spacy
import re
import traceback
import random
from preprocess import preprocess_docs




root_dir = "data/"
questions_yn = []
questions_wh = []
questions_subj_verb_obj = []
set_list = ["test_set","set1","set2","set3","set4"]
nlp = spacy.load("en")


#Dict of final questions and their scores
final_questions = {}

#Call the spacy preprocess module
def preprocess(setlist, nlp):
	set_dict = preprocess_docs(root_dir,setlist,nlp)
	return set_dict

#Removes all excess whitespace in the sentence passed to it
def refine(q):
	q_ = re.sub(' +',' ',q)
	return q_

def get_prep_phrase(node, word_list, sent):
	begin = sent[0].i
	word_list.append(node)
	for child in node.children:
		get_prep_phrase(child,word_list,sent)
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
		mv = s.root
		if mv.pos_!="VERB":
			continue

		wh1 = aux = None

		for child in mv.children:
			if child.dep_ == "nsubj":
				subj_list = []
				concat_subphrase(child,subj_list)
				subj_list.reverse()
				for node in subj_list:
					if node.ent_type_ == "PERSON":
						wh = "Who"
					elif node.ent_type_ == "GPE":
						wh = "Which place"
					else:
						wh = "What"

			elif child.dep_ == "nsubjpass":
				subj_list = []
				concat_subphrase(child,subj_list)
				subj_list.reverse()
				for node in subj_list:
					if node.ent_type_ == "PERSON":
						wh = "Who"
					elif node.ent_type_ == "GPE":
						wh = "Which place"
					else:
						wh = "What"

			elif child.dep_ == "aux" or child.dep_=="auxpass":
				aux = child.string

			if child.dep_ == "prep":
				subj_list_prep = []
				concat_subphrase(child,subj_list_prep)
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
		Q = Q.replace(".","?")
		Q = refine(Q)
		questions_wh.append(Q)

		#wh1 - When questions
		list_of_rem = rem2.strip().split(' ',1)
		if wh1 is not None and len(list_of_rem)>1:
			rem_when = " "
			remaining = rem2.strip().split(' ', 1)[1]
			remaining = remaining.replace(".","?")

			subject = ""
			for s1 in subj_list:
				s1 = str(s1)
				subject+=s1+" "

			#Questions of type "On 25th Nov, SUBJ was blah blah blah" -> "When was SUBJ blah..?"
			if aux:
				Q1 = str(wh1+" "+aux+" "+subject+" "+remaining)
				Q1 = refine(Q1)
				questions_wh.append(Q1)

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
				concat_subphrase(child,subj_list)				
				#Go through every word in sub phrase and remove caps if not a named entity
				new_subj_list = []
				for node in subj_list:
					if node.ent_type_:
						sub_word = str(node.string.capitalize())
					else:
						sub_word = str(node.string.lower())
					new_subj_list.append(sub_word)

				new_subj_list.reverse()
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
			#Modify the verb
			else:
				verb = mv.lemma_
				aux = aux.capitalize()
				Q = str(aux+" "+subj+" "+verb+" "+remaining+"?")
				Q = refine(Q)
				questions_yn.append(Q)
"""
Function that determines if a question needs to be removed
Current criteria for removing are:
1. Too short (< 5) or too long (> 20)
2. If the subject is: "he/she/him/her/it/its/it's/"
"""
def remove(question):
	pronouns = ['he','him','his','she','her','hers','they','them','theirs','it','its']
	#doc = nlp(unicode(question, encoding = 'ascii', errors = 'ignore'))
	# for q in doc.sents:
	# 	if q.root is not None:
	# 		mv = q.root
	# 	else:
	# 		print "this shouldn't even happen"
	# 		return 0

	# 	for child in mv.children:
	# 		if child.dep_ == "nsubj" or child.dep_ == "nsubjpass":
	# 			if child in pronouns:
	# 				return 0

	for word in question.split():
		if word in pronouns:
			return 1

	if len(question.split()) < 5 or len(question.split()) >= 20:
		return 1

	return 0

def subj_verb_obj_questions(doc):
	sents = doc.sents
	for s in sents:
		mv = s.root
		# print "-----------"
		# print s
		if mv.pos_!="VERB":
			continue

		aux = neg = subj = obj = iobj = number = prep = None
		
		for child in mv.children:
			
			if child.dep_ == "nsubj" or child.dep_ == "nsubjpass":
				if child.tag_ == "NNP" or child.tag_ == "NN":
					number = "sing"
				else:
					number = "plural"

				subj_list = []
				concat_subphrase(child,subj_list)				
				#Go through every word in sub phrase and remove caps if not a named entity
				new_subj_list = []
				for node in subj_list:
					if node.ent_type_:
						sub_word = str(node.string.capitalize())
					else:
						sub_word = str(node.string.lower())
					new_subj_list.append(sub_word)

				new_subj_list.reverse()
				subj = " ".join(new_subj_list)

			elif child.dep_ == "dobj":
				dobj = child.string
				obj_list = []
				concat_subphrase(child,obj_list)
				new_obj_list = []
				for node in obj_list:
					if node.ent_type_:
						obj_word = str(node.string.capitalize())
					else:
						obj_word = str(node.string.lower())
					new_obj_list.append(obj_word)
				new_obj_list.reverse()
				obj = " ".join(new_obj_list)

			elif child.dep_ == "prep":
				prep = child.string
				prep_list = []
				prep_list = get_prep_phrase(child,prep_list,s)
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

		if subj is None or obj is None or not (iobj is None):
			continue

		# TODO: need rest??

		if aux:
			#aux = aux.capitalize()
			if prep is None:
				Q = str("What "+aux+" "+subj+" "+mv.string+"?")
			else:
				Q = str("What "+aux+" "+subj+" "+mv.string+" "+prep+"?")
			Q = refine(Q)
			questions_subj_verb_obj.append(Q)
			# print "\t", Q
		
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
				# print "\t", Q
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
				# print "\t", Q


def replace_superlatives():
	sups_dict = get_superlatives()
	new_questions = {}
	for question, score in final_questions.iteritems():
		sup = False
		split_question = question.split()
	# TODO: make better
		if score == 1:
			for i, word in enumerate(split_question):
				if word in sups_dict:
					sup = True
					if random.random() > 0.5:
						split_question[i] = sups_dict[word]
		new_questions[(" ").join(split_question)] = score
		# if sup:
		# 	print (" ").join(split_question)
	return new_questions


def get_superlatives():
	f = open("superlatives.txt", "r")
	sups_dict = {}
	line = f.readline()
	while line != "":
		sups = line.split(",")
		sups_dict[sups[0]] = sups[1].strip()
		line = f.readline()
	return sups_dict


"""
If y/n question, score is 1
If when question, score is 4
If sub_verb question, score is 3
Questions that need to be REMOVED are given a score of 0
Default score is 5
"""
def score(question,id):
	if remove(question) == 1:
		return 0

	if id == 3:
		return 3

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
	setlist = ["test_set"]
	set_dict = preprocess(setlist,nlp)
	print "Questions for doc0 (the first doc) in test_set: "
	print "------------------------------------------------"
	# TODO: do this for all documents
	doc1 = set_dict[0]
	try:
		# superlative_questions(doc1)
		get_superlatives()
		yesno_questions(doc1)
		evaluate_questions(questions_yn,1)
		wh_questions(doc1)
		evaluate_questions(questions_wh,0)
		subj_verb_obj_questions(doc1)
		evaluate_questions(questions_subj_verb_obj,3)
	except Exception,e:
		print e

	# print "\nYes/No:"
	# for q in questions_yn:
	# 	print q
	# print "\nWh Questions:"
	# for q in questions_wh:
	# 	print q
	# for q in questions_subj_verb_obj:
	# 	print q

	final_questions = replace_superlatives()

	print "All questions & their scores:"
	for q in final_questions:
		if final_questions[q] != 0:
			print q,":",final_questions[q]

main()
