""" import statements.  """
from mallethon.crfs import *
from edu.umass.cs.mallet.base.util import PropertyList
from edu.umass.cs.mallet.base.fst import CRF4
from edu.umass.cs.mallet.base.pipe.iterator import LineGroupIterator
from edu.umass.cs.mallet.base.pipe import SimpleTaggerSentence2TokenSequence
from edu.umass.cs.mallet.base.pipe import TokenSequence2FeatureVectorSequence
from edu.umass.cs.mallet.base.pipe.tsf import *
import jarray, getopt, sys


def main():
    """ define some variables so we don't have to search to change them """
    defaultLabel = "O"
    inFile = "CRFtest"
    outFile = "pipe-out.txt"
    try:
        opts,args = getopt.getopt(sys.argv[1:], "hi:o:", 
				["help", "input=","output="]);
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
        if o in ("-i", "--input"):
            inFile = a
        if o in ("-o", "--output"):
	    outFile = a
    
    """
    Create a pipe to read in the training data, add the default feature to that
    pipe's alphabet, and tell the pipe to expect labels on the input
    """
    p = List2Pipe(( SimpleTaggerSentence2TokenSequence(0), 
                   TokenTextCharSuffix("S2-", 2),
                   TokenTextCharPrefix("P1-", 1),
                   FeaturesInWindow('Window-L-', -1, 0, Pattern.compile(".*"),1)),
    		  defaultLabel)
    p.setTargetProcessing(1) 
    instList = LineGroupInstanceList(p, inFile)
    
    try:
        out=open(outFile,"w")
    except IOError:
        print "There was an error writing to", outFile
        sys.exit()


    alphabet = instList.getDataAlphabet()
    for i in range(0,instList.size()):
        instance = instList.getInstance(i)
        input = instance.getData()
        labels = instance.target
        for j in range(0,input.size()):
	    token = input.getToken(j)
            out.write(token.getText())
            out.write(" ")
	    f = token.getFeatures()
            if (f != None):
               for s in f.iterator():
                  out.write(PropertyList.iterator(s).getKey())
                  out.write(" ")
            out.write(labels.get(j).encode())
            out.write("\n")
        out.write("\n")
     
    out.close()

def usage():
    print "Usage:"
    print "	jython ",sys.argv[0]," [options]"
    print "-h,--help \n\tprint this help message"
    print "-i,--infile <name> \n\ttraining (input) file name"
    print "-o,--outfile <name> \n\tmodel (output) file name"

if __name__ == "__main__":
    main()


