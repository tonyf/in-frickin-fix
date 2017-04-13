import os
# Import pexpect
if os.name == 'nt':
    import winpexpect
else:
    import pexpect
class parser:
    def __init__(self, jar_path, grammar_path):
        # Check input
        if not jar_path.endswith('.jar') or not os.path.isfile(jar_path):
            raise Exception("Invalid jar file")
        if not grammar_path.endswith('.gr') or \
           not os.path.isfile(grammar_path):
            raise Exception("Invalid grammar file")

        cmd = 'java -jar %s -gr %s' % (jar_path, grammar_path)
        if os.name == 'nt':
            self.parser = winpexpect.winspawn(cmd)
        else:
            self.parser = pexpect.spawn(cmd)

        # Pass in a dumb sentence to fully initialize
        tmp = self.parse('')

    def parse(self, sent):
	#print "Parsing.."
        self.parser.sendline(sent)
        if os.name == 'nt':
            pattern = '.*'
        else:
            pattern = '\r\n.*\r\n'
        self.parser.expect(pattern)
        return self.parser.after.strip()

    def terminate(self):
        self.parser.terminate()


"""_____________________NOTE_____________________
- The parser assumes that the jar file and the english grammar file in in home/bin/berkeleyparser/
- If you keep them elsewhere, change the path names jar and gr
- In order to parse, pass a list of sentences to b_parse( )
_________________________________________________"""

def b_parse(s):
    import os
    if os.name == 'nt':
        home = os.environ['HOMEPATH']
    else:
        home = os.environ['HOME']
    jar = os.path.join(home,
                       'bin', 'berkeley_parser', 'BerkeleyParser-1.7.jar')
    gr = os.path.join(home,
                      'bin', 'berkeley_parser', 'eng_sm6.gr')

    #print "Initializing the parser...\n"
    p = parser(jar, gr)
    #print "Initialization complete."

    print p.parse(s)

    p.terminate()

