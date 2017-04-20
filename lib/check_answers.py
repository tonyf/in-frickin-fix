def main():
	expected_actual = []
	
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

		if l_actual.strip() == l_expected.strip():
			count_correct += 1
		# 	expected_actual.append((question, l_expected, l_actual, True))
		else:
			expected_actual.append((question, l_expected, l_actual, False))

		l_actual = f_actual.readline()
		if l_actual == "":
			break
		question = f_expected.readline()
		if question == "":
			print "Failed: Answer Key incorrectly formatted. Question expected to go with answer"
			break
		l_expected = f_expected.readline()

	print count_correct, " out of ", count_total, " correct."
	for question, expected, actual, matched in expected_actual:
		print "Question: ", question, "Expected: ", expected, "Actual: ", actual, "Correct: ", matched, "\n"		

main()
