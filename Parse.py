import re

def getSeguence(i, k, j, eduNb, structs, thisSeq):
    
    for x in range(1, i):
        
        if x == i-1:
            astruct = "(" + str(x) + ":" + str(x) + "," + str(i) + ":" + str(k) + ")"
            if structs.has_key(astruct):
                thisSeq[:] = []
                return 1
                                        
            else:
                thisSeq.append(astruct) 

        else:
            astruct = "(" + str(x) + ":" + str(x) + "," + str(x+1) + ":" + str(x+1) + ")"
            if structs.has_key(astruct):
                print "this never executes..."
                raw_input(' ')
                thisSeq[:] = []
                return 1
            else:
                thisSeq.append(astruct) 
                                
    astruct = "(" + str(i) + ":" + str(k) + "," + str(k+1) + ":" + str(j) + ")"
    thisSeq.append(astruct)
                                
    if not structs.has_key(astruct):
        structs[astruct] = 1
    else:
        print astruct + " is a duplicate.. ERROR!!!"
        raw_input(' ')

    for x in range(j+1, eduNb+1):
                                     
        if x == j+1:
            astruct = "(" + str(k+1) + ":" + str(j) + "," + str(x) + ":" + str(x) + ")"
            if structs.has_key(astruct):
               print "this never executes..."
               raw_input(' ')
               thisSeq[:] = []
               return 1
                                        
            else:
                thisSeq.append(astruct)
                                    
        else:
            astruct = "(" + str(x-1) + ":" + str(x-1) + "," + str(x) + ":" + str(x) + ")"
            if structs.has_key(astruct):
               print "this never executes..."
               raw_input(' ')
               thisSeq[:] = []
               return 1 
            else:
                thisSeq.append(astruct)

    return 0

def readNewLine(F_FEAT, F_PROB):
    garbage = F_FEAT.readline()
    garbage = garbage.strip()
    garbage2 = F_PROB.readline()
    garbage2 = garbage2.strip()
    if garbage or garbage2:
        print "Error!! it should be empty.. " + garbage
        raw_input(' ')                                      
    
def readRelationsFromCRF_OUTPUT(crf_relf_Sen, crf_relf_Doc):
    """ read the relations for sent-level and doc-level """

    rel_labels_Sen = readRhRelations(crf_relf_Sen) #read the rhetorical relations numbered by CRF (including 'Unknown')
    rel_labels_Doc = readRhRelations(crf_relf_Doc) #read the rhetorical relations numbered by CRF (including 'Unknown')
        
    if rel_labels_Sen[0] != 'U' and rel_labels_Doc[0] != 'U':
        print "ERROR in relations.."
        raw_input(' ')
        
    return (rel_labels_Sen, rel_labels_Doc)     

def parse(crf_relf_Sen, probfile_Sen, featfile_Sen, dpfile_Sen, crf_relf_Doc, probfile_Doc, featfile_Doc, dpfile_Doc, edufile):
    
    """ discourse parse algorithm """    
    baseprob = 10 ** (-10)
    (rel_labels_Sen, rel_labels_Doc) = readRelationsFromCRF_OUTPUT(crf_relf_Sen, crf_relf_Doc)
    
    [F_FEAT_Doc, F_FEAT_Sen, F_PROB_Doc, F_PROB_Sen]  = [ open(featfile_Doc, 'r'), open(featfile_Sen, 'r'), open(probfile_Doc, 'r'), open(probfile_Sen, 'r') ]
    [F_DP_Doc, F_DP_Sen]      = [open(dpfile_Doc, 'w'), open(dpfile_Sen, 'w')]

    F_EDU = open(edufile, 'r')
    [eduIndex, eduNb, spans, spans_parse, spans_edus] = [0, 0, [], {}, {}]

    for edusen in F_EDU:
        edusen = edusen.strip()
        edus = re.split("\s*EDU_BREAK\s*", edusen)
        n    = len(edus) 
        
        prob   = [[0 if i != j else 1 for i in range(0, n)] for j in range(0, n)]
        struct = [[0 for i in range(0, n)] for j in range(0, n)]
        rel    = [[0 for i in range(0, n)] for j in range(0, n)]

        if n == 1: #if contains only one edu
            print >>F_DP_Sen, "( Root (span " + str(eduIndex + 1) + " " + str(eduIndex + 1) + ")\n  ( DUMMY (leaf " + str(eduIndex + 1) + ") (rel2par DUMMY) (text _!" + handleQuote(edusen) + "_!) )\n)"

        else:
            for s in range(2, n+1):                    
                [structs, str_prob] = [{}, {}]                    

                for i in range(1, n-s+2):
                    j = i+s-1                        

                    for k in range(i, j):
                        if (i == 1 and j == n) or s == 2:

                            astruct = "(" + str(i) + ":" + str(k) + "," + str(k+1) + ":" + str(j) + ")"

                            fline = F_FEAT_Sen.readline()
                            fline = fline.strip()
                            pline = F_PROB_Sen.readline()
                            pline = pline.strip()

                            if not fline or not pline:
                                print "\nError in reading features or posterior probs"
                                raw_input(' ')                                       

                            pline = re.sub("(\d+|MaxId):", "", pline)
                            probs = map(float, (pline.split())[len(rel_labels_Sen):-1])
                            maxp = max(probs)
                            argmax = probs.index(maxp)
                            
                            if argmax == 0:
                                print "Found Unknown relation.. which shouldn't come.. max prob: " + str(maxp)
                                maxp = max(probs[1:])
                                argmax = probs.index(maxp)

                            c_prob   = (baseprob + maxp) * prob[i-1][k-1] * prob[k][j-1] 
                            c_rel    = rel_labels_Sen[argmax]

                            if (c_prob > prob[i-1][j-1]):
                                prob[i-1][j-1]    = c_prob
                                struct[i-1][j-1]  = k
                                rel[i-1][j-1]     = c_rel
                                
                            if s!=2:
                                readNewLine(F_FEAT_Sen, F_PROB_Sen)

                        else:
                            thisSeq = []
                            isDup = getSeguence(i, k, j, n, structs, thisSeq)
                            tarStr = "(" + str(i) + ":" + str(k) + "," + str(k+1) + ":" + str(j) + ")"
                            
                            if not isDup:                                    
                                for st in thisSeq:
                                    fline = F_FEAT_Sen.readline()
                                    fline = fline.strip()
                                    pline = F_PROB_Sen.readline()
                                    pline = pline.strip()                                                                                
                                
                                    if not fline or not pline:
                                        print "\nError in reading features or posterior probs here"
                                        raw_input(' ')                                       

                                    str_prob[st] = pline                                       

                                    if tarStr == st:
                                        pline = re.sub("(\d+|MaxId):", "", pline)
                                        probs = map(float, (pline.split())[len(rel_labels_Sen):-1])
                                        maxp = max(probs)
                                        argmax = probs.index(maxp)
                    
                                        if argmax == 0:
                                            print "Found Unknown relation.. which shouldn't come.. max prob: " + str(maxp)
                                            maxp = max(probs[1:])
                                            argmax = probs.index(maxp)

                                        c_prob   = (baseprob + maxp) * prob[i-1][k-1] * prob[k][j-1]
                                        c_rel    = rel_labels_Sen[argmax]
                                        
                                        if (c_prob > prob[i-1][j-1]):
                                            prob[i-1][j-1]    = c_prob
                                            struct[i-1][j-1]  = k
                                            rel[i-1][j-1]     = c_rel
                                            

                                readNewLine(F_FEAT_Sen, F_PROB_Sen)

                            elif str_prob.has_key(tarStr):
                                pline = re.sub("(\d+|MaxId):", "", str_prob[tarStr])
                                probs = map(float, (pline.split())[len(rel_labels_Sen):-1])
                                maxp = max(probs)
                                argmax = probs.index(maxp)

                                if argmax == 0:
                                    print "Found Unknown relation.. which shouldn't come.. max prob: " + str(maxp)
                                    maxp = max(probs[1:])
                                    argmax = probs.index(maxp)

                                c_prob   = (baseprob + maxp) * prob[i-1][k-1] * prob[k][j-1] 
                                c_rel    = rel_labels_Sen[argmax]

                                if (c_prob > prob[i-1][j-1]):
                                    prob[i-1][j-1]    = c_prob
                                    struct[i-1][j-1]  = k
                                    rel[i-1][j-1]     = c_rel

                            else:
                                print "The struct wasn't found: " + tarStr                                    
                                raw_input(' ')    

                if s == 2:
                    readNewLine(F_FEAT_Sen, F_PROB_Sen)                                      

            if prob[0][n-1]==0:
                print "Cannot parse: solve ..."
                raw_input(' ')

            else:
                print >>F_DP_Sen, "( Root (span " + str(eduIndex + 1) + " " + str(eduIndex + n) + ")"
                writeParse(1, struct[0][n-1], n, rel, struct, edus, 2, F_DP_Sen, eduIndex)
                print >>F_DP_Sen, ")"

        #compute spans here
        span = str(eduIndex + 1) + ":" + str(eduIndex + n)
        spans.append(span)

        spans_parse[span] = [prob, struct, rel]
        spans_edus[span] = edus    
        eduIndex += n

    parseDocLevel(baseprob, spans, spans_parse, spans_edus, rel_labels_Doc, F_FEAT_Doc, F_PROB_Doc, F_DP_Doc)

    F_EDU.close()
    F_DP_Doc.close()
    F_DP_Sen.close()
    F_FEAT_Doc.close()
    F_FEAT_Sen.close()
    F_PROB_Doc.close()
    F_PROB_Sen.close()


def parseDocLevel(baseprob, spans, spans_parse, spans_edus, rel_labels, F_FEAT, F_PROB, F_DP): 
    """ parsing alg for doc-level"""
    
    n    = len(spans)
    
    if n == 1: #contains only one span

        the_span = spans[0]
        the_span_list = spans[0].split(':')
        [the_prob, the_struct, the_rel] = spans_parse[the_span]
        the_edus = spans_edus[the_span]
        b_e_id = int(the_span_list[0])
        e_e_id = int(the_span_list[1])
        
        if e_e_id - b_e_id == 0:#only one edu
            print >>F_DP, "( Root (span " + str(b_e_id) + " " + str(e_e_id) + ")\n  ( DUMMY (leaf " + str(b_e_id) + ") (rel2par DUMMY) (text _!" + handleQuote(the_edus[0]) + "_!) )\n)"
            
        else:
            print >>F_DP, "( Root (span " + str(b_e_id) + " " + str(e_e_id) + ")"
            writeParse(b_e_id, the_struct[0][e_e_id - 1], e_e_id, the_rel, the_struct, the_edus, 2, F_DP, 0)
            print >>F_DP, ")"
            
    else:
        prob   = [[0 if i != j else 1 for i in range(0, n)] for j in range(0, n)]
        struct = [[0 for i in range(0, n)] for j in range(0, n)]
        rel    = [[0 for i in range(0, n)] for j in range(0, n)]

        for s in range(2, n+1):
            for i in range(1, n-s+2): 
                j = i+s-1 
                for k in range(i, j):

                    fline = F_FEAT.readline()
                    fline = fline.strip()

                    pline = F_PROB.readline()
                    pline = pline.strip()

                    if not fline or not pline:
                        print "\nError in reading features or posterior probs"
                        raw_input(' ')                                       

                    pline  = re.sub("(\d+|MaxId):", "", pline)
                    probs  = map(float, (pline.split())[len(rel_labels):-1])
                    
                    maxp   = max(probs)
                    argmax = probs.index(maxp)
                                
                    if argmax == 0:
                        print "Found Unknown relation.. which shouldn't come.. max prob: " + str(maxp)
                        maxp = max(probs[1:])
                        argmax = probs.index(maxp)

                    c_prob   = (baseprob + maxp) * prob[i-1][k-1] * prob[k][j-1] 
                    c_rel    = rel_labels[argmax]
                                        
                    if (c_prob > prob[i-1][j-1]):
                        prob[i-1][j-1]    = c_prob
                        struct[i-1][j-1]  = k
                        rel[i-1][j-1]     = c_rel

                    readNewLine(F_FEAT, F_PROB)

        if prob[0][n-1]==0:
            print "Cannot parse: solve ..."
            raw_input(' ')

        else:
            lastEdu = spans[n-1].split(':') [1]
            print >>F_DP, "( Root (span 1 " + lastEdu + ")"
            writeDocLevelParse(1, struct[0][n-1], n, rel, struct, spans, spans_parse, spans_edus, 2, F_DP)
            print >>F_DP, ")"


def writeDocLevelParse(i, k, j, rel, struct, spans, spans_parse, spans_edus, offset, F_DP):
    """ print the parse tree """

    if i < j:
        m = re.search("^\((.*?)=(.*?),(.*?)=(.*?)\)$", rel[i-1][j-1])
        status1  = m.group(1)
        rel2par1 = m.group(2)
        status2  = m.group(3)
        rel2par2 = m.group(4)

        i_span = spans[i-1].split(':')                                                        
        k_span = spans[k-1].split(':')
        j_span = spans[j-1].split(':')
        
        if k-i > 0:
            print >>F_DP, offset * " " + "( " + status1 + " (span " + str(i_span[0]) + " " + str(k_span[1]) + ") (rel2par " + rel2par1 + ")"
            writeDocLevelParse(i, struct[i-1][k-1], k, rel, struct, spans, spans_parse, spans_edus, offset+2, F_DP)
            print >>F_DP, offset * " " + ")"

        else:
            writeSentLevelParse(F_DP, offset, status1, i_span, rel2par1, spans_parse, spans_edus)     

        if j-k-1 > 0:
            print >>F_DP, offset * " " + "( "+ status2 + " (span " + str(int(k_span[1])+1) + " " + str(j_span[1]) + ")" + " (rel2par " + rel2par2 + ")"
            writeDocLevelParse(k+1, struct[k][j-1], j, rel, struct, spans, spans_parse, spans_edus, offset+2, F_DP)
            print >>F_DP, offset * " " + ")"

        else:
            writeSentLevelParse(F_DP, offset, status2, j_span, rel2par2, spans_parse, spans_edus)

    else:
        print "error!! " + str(i) + " can't be equal to " + str(j)
        raw_input(' ')

  
def writeSentLevelParse(F_DP, offset, status1, i_span, rel2par1, spans_parse, spans_edus):

    thisSpan = ':'.join(i_span)
    eI = int (i_span[0]) - 1
    n = int(i_span[1]) - eI
    
    if int(i_span[1]) - int (i_span[0]) == 0:
        print >>F_DP, offset * " " + "( " + status1 + " (leaf " + str(i_span[0]) + ") (rel2par " + rel2par1 + ") (text _!" + handleQuote(spans_edus[thisSpan] [0]) + "_!) )"
    
    else:
        print >>F_DP, offset * " " + "( " + status1 + " (span " + str(i_span[0]) + " " + str(i_span[1]) + ") (rel2par " + rel2par1 + ")"
        thisSpanProb = spans_parse[thisSpan] [0]
        thisSpanStr  = spans_parse[thisSpan] [1]
        thisSpanRel  = spans_parse[thisSpan] [2]
        thisSpanEdus = spans_edus[thisSpan]
        writeParse(int(i_span[0]) - eI, thisSpanStr[0][n-1], int(i_span[1]) - eI, thisSpanRel, thisSpanStr, thisSpanEdus, offset+2, F_DP, eI)
        print >>F_DP, offset * " " + ")"


def writeParse(i, k, j, rel, struct, edus, offset, F_DP, eI):
    """ print the parse tree """
            
    if i < j:
        m = re.search("^\((.*?)=(.*?),(.*?)=(.*?)\)$", rel[i-1][j-1])
        status1  = m.group(1)
        rel2par1 = m.group(2)
        status2  = m.group(3)
        rel2par2 = m.group(4)

        if k-i > 0:
            print >>F_DP, offset * " " + "( " + status1 + " (span " + str(eI+i) + " " + str(eI+k) + ") (rel2par " + rel2par1 + ")"
            writeParse(i, struct[i-1][k-1], k, rel, struct, edus, offset+2, F_DP, eI)
            print >>F_DP, offset * " " + " )"
        
        else:
            print >>F_DP, offset * " " + "( " + status1 + " (leaf " + str(eI+i) + ") (rel2par " + rel2par1 + ") (text _!" + handleQuote(edus[i-1]) + "_!) )"
            
        if j-k-1 > 0:
            print >>F_DP, offset * " " + "( "+ status2 + " (span " + str(eI+k+1) + " " + str(eI+j) + ")" + " (rel2par " + rel2par2 + ")"
            writeParse(k+1, struct[k][j-1], j, rel, struct, edus, offset+2, F_DP, eI)
            print >>F_DP, offset * " " + " )"
            
        else:
            print >>F_DP, offset * " " + "( " + status2 + " (leaf " + str(eI+j) + ") (rel2par " + rel2par2 +") (text _!" + handleQuote(edus[j-1]) +"_!) )"
            

    else:
        print "error!! " + str(i) + " can't be equal to " + str(j)
        raw_input(' ')

        
def handleQuote(sent):

# required if we want to parse the output for example to evaluate
	
#    sent = re.sub("\(", "-LHB-", sent) 
#    sent = re.sub("\)", "-RHB-", sent)
    
    #for the visualization
    sent = re.sub(r"\"", r"\\\\\"", sent)
    return sent.strip()        
            

def readRhRelations(filename):
    """ read the rhetorical labels """
    
    F_R = open(filename, 'r')
    id  = 0
    hash = {}
    
    for line in F_R:
        line = line.strip()
        parts = line.split()
        
        if parts[2].strip():
            hash[id] = hash.get(id, parts[2].strip()) 
            id += 1
        else:
            print "\nError in reading rhetorical relations.."
            raw_input(' ')   
    
    F_R.close()
    return hash    


