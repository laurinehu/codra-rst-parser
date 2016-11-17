"""
import statements. 
"""
from mallethon.crfs import *
import getopt, sys
#import java.lang.String
#from edu.umass.cs.mallet.base.fst import MultiSegmentationEvaluator

def main():
    """ Default values for options """
    testFileName = "CRFtest"
    modelFileName = "CRFmodel"
    targetProcessing = 1
    printFeatures = 0
    """ Read in the command line options to override these """
    try:
        opts,args = getopt.getopt(sys.argv[1:], "hnf:m:v",
                ["help","testfile=","model=","notarget"]);
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
        if o in ("-n", "--notarget"):
	    targetProcessing = 0
        if o in ("-v"):
            printFeatures = 1

    """ load the model """
    crf = loadModel(modelFileName)
                                                                                
    """ get the input pipe for the testing data """
    p = crf.getInputPipe()
                                                                                
    """ set target processing to true (i.e. expect labels on the input data) --
    not having labels on the data makes no sense in the context of testing """
    p.setTargetProcessing(targetProcessing)
                                                                                
    """ read in the testing data """
    testingData = LineGroupInstanceList(p, testFileName)

    """
    Finally, we perform the labelling, printing the results on standard out.
    If you want a different format, modifying this is probably easiest. 
    """ """
    First we get the data alphabet.  This will let us print the names of the
    features. 
    """
    alphabet = testingData.getDataAlphabet()
    """ for each instance """
    for i in range(0,testingData.size()):
	""" input is the current instance, output is the viterbi path through
        the crf """
        input = testingData.getInstance(i).getData()
        output = crf.viterbiPath(input).output()
        """ for each node in the path """
        for j in range(0,output.size()):
	    """ vals is a list of the indices in the alphabet of the feature
	    vector for this node """ 
            vals = input.get(j).getIndices()
	    """ print the symbol for each feature followed by the label """
            if (printFeatures):
                for k in range(0,len(vals)):
                    print(alphabet.lookupObject(vals[k])),
            print (output.get(j).encode())
        """Print a blank line after each instance"""
        print

""" Print usage information """
def usage():
    print "Usage:"
    print "     jython ",sys.argv[0]," [options]"
    print "-h,--help \n\tprint this help message"
    print "-f,--testfile <name>\n\tset the testing file"
    print "-m,--model <name>\n\tset the model file name"
    print "-n,--no-target\n\tUse this option if file does not include the true labels" 
    print "-v\n\tprint the features as well as the predicted labels"
                                                                                
""" Call the main method if this was called as a script """
if __name__ == "__main__":
    main()

