""" import statements.  """
from mallethon.crfs import *
from edu.umass.cs.mallet.base.fst import TokenAccuracyEvaluator
import getopt, sys

def main():
    """ Default values for options """ 
    testFileName = "CRFtest" 
    modelFileName = "CRFmodel"
    """ Read in the command line options to override these """
    try:
        opts,args = getopt.getopt(sys.argv[1:], "hf:m:", 
		["help","testfile=","model="]);
        if (len(args) > 0):
	    usage()
            sys.exit(2)
    except getopt.GetoptError:
        usage() 
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-f", "--testfile"):
            testFileName = a
        if o in ("-m", "--model"):
            modelFileName = a

    """ load the model """
    crf = loadModel(modelFileName)

    """ get the input pipe for the testing data """
    p = crf.getInputPipe()

    """ set target processing to true (i.e. expect labels on the input data) --
    not having labels on the data makes no sense in the context of testing """
    p.setTargetProcessing(1) 

    """ read in the testing data """
    testingData = LineGroupInstanceList(p, testFileName)

    """ perform the actual evaluation using a new TokenAccuracyEvaluator """
    TokenAccuracyEvaluator().test(crf, testingData, "Testing", None)

""" Print usage information """
def usage():
    print "Usage:"
    print "     jython ",sys.argv[0]," [options]"
    print "-h,--help \n\tprint this help message"
    print "-f,--testfile <name>\n\tset the testing file"
    print "-m,--model <name>\n\tset the model file name"

""" Call the main method if this was called as a script """
if __name__ == "__main__":
    main()

