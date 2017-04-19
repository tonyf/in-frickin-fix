def main():
	expected_actual = {}
	
	f_expected = open("lib/questions_answers.txt", "r")
	f_actual = open("lib/answers.txt", "r")

	l_actual = f_actual.readline()
	l_expected = f_expected.readline()
	if l_expected == "":
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

		l_actual = f_actual.readline()
		if l_actual == "":
			break
		l_expected = f_expected.readline()
		if l_expected == "":
			print "Failed: Answer Key incorrectly formatted"
			break
		l_expected = f_expected.readline()

	print count_correct, " out of ", count_total, " correct."
	for expected, actual in expected_actual.iteritems():
		print "Expected: ", expected, "Actual: ", actual		

main()