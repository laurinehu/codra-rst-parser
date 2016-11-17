""" import statements.  """
from mallethon.crfs import *
from edu.umass.cs.mallet.base.fst import CRF4
from edu.umass.cs.mallet.base.pipe.iterator import LineGroupIterator
from edu.umass.cs.mallet.base.pipe import SimpleTaggerSentence2TokenSequence
from edu.umass.cs.mallet.base.pipe import TokenSequence2FeatureVectorSequence
import jarray, getopt, sys

def main():
    """ Default values for options """
    defaultLabel = "O"
    orders = jarray.array(range(1,2),"i")
    iterations = 500
    variance = 10
    trainingFileName = "CRFtrain"
    modelFileName = "CRFmodel"
    try:
        opts,args = getopt.getopt(sys.argv[1:], "hl:o:i:v:f:m:", 
				["help", "label=","order=","iterations=",
				 "variance=","trainfile=","model="]);
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
        if o in ("-l", "--label"):
            defaultLabel = a
        if o in ("-o", "--order"):
	    orders = jarray.array(range(1,a+1),i)
        if o in ("-i", "--iterations"):
	    iterations = int(a)
        if o in ("-v", "--variance"):
	    variance = a
        if o in ("-f", "--trainfile"):
	    trainingFileName = a
        if o in ("-m", "--model"):
	    modelFileName = a
    """
    Create a pipe to read in the training data, add the default feature to that
    pipe's alphabet, and tell the pipe to expect labels on the input
    """
    p = List2Pipe(( SimpleTaggerSentence2TokenSequence(), 
    	            TokenSequence2FeatureVectorSequence()), 
    		  defaultLabel)
    p.setTargetProcessing(1) 
    trainingData = LineGroupInstanceList(p, trainingFileName)
    printDataInfo(p)
    crf = initNewCRF(trainingData, orders, defaultLabel, variance)
    crf.train(trainingData,None, None, None, iterations)
    saveModel(crf,modelFileName)

def usage():
    print "Usage:"
    print "	jython ",sys.argv[0]," [options]"
    print "-h,--help \n\tprint this help message"
    print "-l,--label <lab> \n\tset the default label to the argument given"
    print "-o,--order <int> \n\tset the max order of the CRF"
    print "-i,--iterations <int> \n\tmax number of training iterations"
    print "-v,--variance <var> \n\tvariance of gaussian prior"
    print "-f,--trainfile <name> \n\ttraining (input) file name"
    print "-m,--model <name> \n\tmodel (output) file name"

if __name__ == "__main__":
    main()


