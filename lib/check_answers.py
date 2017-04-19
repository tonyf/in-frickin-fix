def main():
	expected_actual = {}
	expected_question = {}
	
	f_expected = open("lib/questions_answers.txt", "r")
	f_actual = open("lib/answers.txt", "r")

	l_actual = f_actual.readline()
	question = f_expected.readline()
	if question == "":
		print "Failed: Answer Key incorrectly formatted"
		return
	l_expected = f_expected.readline()

	count_correct = 0
	count_total = 0

	while l_actual != "" and l_expected != "":
		count_total += 1

		if l_actual == l_expected:
			count_correct += 1
		else:
			expected_actual[l_expected] = l_actual
			expected_question[l_expected] = question

		l_actual = f_actual.readline()
		if l_actual == "":
			break
		question = f_expected.readline()
		if question == "":
			print "Failed: Answer Key incorrectly formatted"
			break
		l_expected = f_expected.readline()

	print count_correct, " out of ", count_total, " correct."
	for expected, actual in expected_actual.iteritems():
		print "Question: ", expected_question[expected], "Expected: ", expected, "Actual: ", actual		

main()
