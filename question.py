
import os
import sys
import re
from preprocess import preprocess_docs



root_dir = "data/"
questions_yn = []
questions_wh = []
set_list = ["test_set","set1","set2","set3","set4"]

#Call the spacy preprocess module
def preprocess(setlist):
	set_dict = preprocess_docs(root_dir,setlist)
	return set_dict

#Removes all excess whitespace in the sentence passed to it
def refine(q):
	q_ = re.sub(' +',' ',q)
	return q_

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
		if wh1 is not None:
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
					aux = "Did"

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


def main():
	setlist = ["test_set"]
	set_dict = preprocess(setlist)
	print "Questions for doc1 (the 2nd doc) in test_set: "
	print "------------------------------------------------"
	doc1 = set_dict[set_list[0]]
	print "---------"
	try:
		yesno_questions(doc1[1])
		wh_questions(doc1[1])
	except Exception,e:
		print e

	print "\nYes/No:"
	for q in questions_yn:
		print q
	print "\nWh Questions:"
	for q in questions_wh:
		print q



main()