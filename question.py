import os
import spacy
import sys
import re
from preprocess import preprocess_docs



root_dir = "data/"
questions = []
set_list = ["test_set","set1","set2","set3","set4"]

#Call the spacy preprocess module
def preprocess(setlist, nlp):
	set_dict = preprocess_docs(root_dir,setlist,nlp)
	return set_dict

#Removes all excess whitespace in each question in the global list questions
def refine_questions():
	for i in range(len(questions)):
		q = questions[i]
		q_ = re.sub(' +',' ',q)
		questions[i] = q_

def concat_subphrase(node, word_list):
	#print word_list
	word_list.append(node)
	for child in node.children:
		concat_subphrase(child,word_list)

def tree_questions(doc):
	sents = doc.sents
	for s in sents:

		mv = s.root
		if mv.pos_!="VERB":
			continue

		aux = neg = subj = number = None	
		position = int(mv.i)
		#NOTE: For now, assume a sentence has max of one aux, one neg
		for child in mv.children:
			
			if child.dep_ == "nsubj":
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

			elif child.dep_ == "aux":
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
			questions.append(Q)
		
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
				questions.append(Q)
			#Modify the verb
			else:
				verb = mv.lemma_
				aux = aux.capitalize()
				Q = str(aux+" "+subj+" "+verb+" "+remaining+"?")
				questions.append(Q)


def main():
	setlist = ["test_set"]
	nlp = spacy.load("en")
	set_dict = preprocess(setlist, nlp)
	print "Questions for doc0 (the first doc) in test_set: "
	print "------------------------------------------------"
	doc1 = set_dict[set_list[0]]
	tree_questions(doc1[0])
	refine_questions()
	for q in questions:
		print q



main()