import sys
import subprocess
import os
import re
import serialize
from numpy import *

def addContextualFeatures(words, wordFeatures, W_F1, W_F2):
    """ adds prev and next contextual features """
    
    all_zero = [0 for x in range(len(wordFeatures[0]))]
    
    for wnb, feat in enumerate (wordFeatures):

        if wnb == 0:
            [feat_2, feat_1] = [all_zero, all_zero]

        elif wnb == 1:
            [feat_2, feat_1] = [all_zero, wordFeatures[0]]
        
        else:
            [feat_2, feat_1] = [wordFeatures[wnb-2],wordFeatures[wnb-1]]     
            
        if wnb == len(wordFeatures) - 1:
            [feat1, feat2] = [all_zero, all_zero]
            
        elif wnb == len(wordFeatures) - 2:
            [feat1, feat2] = [wordFeatures[-1], all_zero]
        
        else:
            [feat1, feat2] = [wordFeatures[wnb+1], wordFeatures[wnb+2]]     

        all_feat = feat_2 + feat_1 + feat + feat1 + feat2 
        print >>W_F1, " ". join (map ( str, all_feat ))
        print >>W_F2, words[wnb] 

    print >>W_F2, "\n"



def do_preprocess(infile):
    """ return pos tag after running stanford tagger """
    
                    #POS tagging and tokenization    stanford not used.. uiuc used to keep consistency between train and test
                    #    pos_tagged = subprocess.check_output(['java', '-mx5000m', '-classpath', 'Tools/Stanford_POS_Tagger/stanford-postagger.jar', 'edu.stanford.nlp.tagger.maxent.MaxentTagger', '-model', 'Tools/Stanford_POS_Tagger/models/english-bidirectional-distsim.tagger', '-textFile', 'tmp.raw'])
                    #    tokenized = "<s> " + re.sub("\n", " </s>\n<s> ", re.sub("_[^\s_]+", "", pos_tagged).strip()) + " </s>"

    #POS taggind and chunking
    java_classpath = 'Tools/UIUC_TOOLS/LBJ2.jar:Tools/UIUC_TOOLS/LBJ2Library.jar:Tools/UIUC_TOOLS/LBJChunk.jar:Tools/UIUC_TOOLS/LBJPOS.jar'    
    chunked_pos = subprocess.check_output(['java', '-Xmx2000m', '-classpath', java_classpath, 'edu.illinois.cs.cogcomp.lbj.chunk.ChunksAndPOSTags', infile])

    W_F  = open("tmp.tag", 'w')
    W_F.write(chunked_pos.strip())
    W_F.close()    

    #prepared tokenized text
    tokenized = ""
    for sent in chunked_pos.strip().split("\n"):
        raw_sen = " ". join(re.findall("\(\S+\s(.+?)\)\s+", sent + " "))
        tokenized += "<s> " + raw_sen + " </s>\n"
        
    W_F  = open("tmp.tok", 'w')
    W_F.write(tokenized.strip())
    W_F.close()

    #syntactic parsing
    CHP = "Tools/CharniakParserRerank/parse.sh";
    ch_parsed = subprocess.check_output([CHP, "tmp.tok"])

    if not ch_parsed:
        print "ERROR IN PARSING .. tmp.tok"
        raw_input(' ')

    W_F  = open("tmp.chp", 'w')
    W_F.write(ch_parsed.strip())
    W_F.close()
    
    return ["tmp.tok", "tmp.tag", "tmp.chp"]    


def extractWordFeatures(spadeWords, wordFeatures, tokSen, nbOfRule):
    """ extract word features and returns a refined spadewords """

    tmpWords = []    
    tmpVec = [0 for x in range(4 * nbOfRule)]
     
    rulePattern = re.compile("_RULE_ID_:(\d+)")
    probPattern = re.compile("_PROB_:([\d.]+)")
    occPattern  = re.compile("_OCC_:(\d+)")

    l = len(tokSen.split(" ")) #length of the sentence
    wId = 0

    for i in range (len(spadeWords)):

        #if this is a rule
        rule = rulePattern.findall(spadeWords[i])

        if rule:
            prob = probPattern.findall(spadeWords[i])
            occ  = occPattern.findall(spadeWords[i])

            if tmpVec[ int(rule[0]) - 1 ] < float (prob[0]):
                tmpVec[ int(rule[0]) - 1 ] = float (prob[0]) #first 7 prob
                if float (prob[0]) > 0.5:
                    tmpVec[ (nbOfRule + int(rule[0])) - 1 ] = 1 #second 7 binary --spade rules
                    tmpVec[ ( (3 * nbOfRule) + int(rule[0])) - 1 ] += 1 # fourth 7 nb of spade rule occurence.
            
            tmpVec[ ( (2 * nbOfRule) + int(rule[0])) - 1 ] += 1 # third 7 nb of rule occurence.
            continue       
       
        #got a word
        elif i < len(spadeWords):
            tmpWords.append(spadeWords[i])

            if i > 0:
                wId += 1
                tmpVec[:0] = [round (float(wId)/l, 2), wId - 1, l - wId]
                wordFeatures.append(tmpVec)
                tmpVec = [0 for x in range(4 * nbOfRule)]            

    if len(tmpWords) != len(wordFeatures) + 1:
        print "\nError in extractWordFeatures"
        raw_input("handle it!!!")
        
    else:
        del tmpWords[-1]    
    
    return tmpWords


def extractTAGFeatures(line, wordFeatures, pos_dict, ch_dict):
    """ extract tag features """
   
    #WORD-CHUNK
    ch_line   = re.sub("\([^\s)]+?\s", "", line)
    ch_line   = re.sub("\)\s+", " ", ch_line)
    parts     = re.split("\s+", ch_line.strip())
    
    [wrd_chnks, isB, isI]  = [[], 0, 0]
        
    for part in parts:               
        part = part.strip()

        if re.search("^\[.+", part):
            chunk = re.sub("^\[", "", part)
            [isB, isI]   = [1, 1]                    
            continue
        
        elif isB and isI and part != ']':
            chunktag = "B-" + chunk
            isB = 0
            wrd_chnks.extend([part, chunktag])
            continue
        
        elif not isB and isI and part != ']':
            chunktag = "I-" + chunk
            wrd_chnks.extend([part, chunktag])
            continue

        elif not isB and isI and part == ']':
            [isB, isI] = [0, 0]
            continue
        
        elif not isB and not isI and part != ']':
            chunktag = "O" 
            wrd_chnks.extend([part, chunktag])

    #WORD-POS
    pos_words = re.findall("\(([^\)]+)\)\s?", line)            

    if len(pos_words) - 1 != len(wordFeatures):
        print "Error!!! lengths aren't equal..." + line
        print pos_words
        print len(wordFeatures)
        raw_input(' ')

    id = 0

    for wnb, pos_wrd in enumerate (pos_words[0:-1]):
        [pos, word]     = [ re.findall("^([^\s]+)\s", pos_wrd), re.findall("^[^\s]+\s(.+)", pos_wrd) ]
        [wrd_c, chnk]   = [wrd_chnks[id], wrd_chnks[id+1]]
        wordFeatures[wnb][:0] = [ ch_dict[chnk], pos_dict[pos[0]] ]
        id += 2




def extract_features(tok_f, par_f, tag_f, feat_f, word_f, edufile = "tmp.edu"):
    """ extract features for discourse segmentation """
    
    #  For Spade features
    spade_scr        = "Tools/SPADE_UTILS/bin/edubreak.pl"
    output = subprocess.check_output(['perl', spade_scr, par_f])
    sentences = output.splitlines()
    
    # For positional features
    R_F = open(tok_f, 'r')
    tok_sentences = R_F.read().split("\n")
    R_F.close()
    
    #For tag features
    pos_dict = serialize.loadData("PT_POS_TAGS")
    ch_dict  = serialize.loadData("UIUC_CH_TAGS")

    R_F = open(tag_f, 'r')
    tag_sentences = R_F.read().split("\n")
    R_F.close()    

    if len(tok_sentences) == 1 and len(tok_sentences[0].strip().split()) == 3:
        W_F = open(edufile, 'w')
        print >>W_F, tok_sentences[0].strip().split() [1]
        W_F.close()
        return -1 

    
    if len(sentences) != len(tok_sentences) and len(sentences) != len(tag_sentences):
        print "Error!!! the lengths aren't same in extract features"
        raw_input(' ')
   
    [All_words, All_features] = [dict(), dict()]

    W_F1 = open(feat_f, 'w') #for running the classifier
    W_F2 = open(word_f, 'w') #for saving the words
    
    for line, tokline, tagline in zip(sentences, tok_sentences, tag_sentences):
        spadeWords = re.split( '\s+', line.strip() )

        if (spadeWords[-1] == "<S>"):
            del spadeWords[-1]
        else:
            print "\n End of Sentence error!!!! doesn't end with <S>"
            raw_input("handle it!")

        tokline = re.sub("</?s>", "", tokline).strip()

        wordFeatures = [] # 2-d array #nbWords * nbFeatures
        words = extractWordFeatures(spadeWords, wordFeatures, tokline, nbOfRule=12)
        extractTAGFeatures(tagline, wordFeatures, pos_dict, ch_dict)
        addContextualFeatures(words, wordFeatures, W_F1, W_F2)

    W_F1.close()
    W_F2.close()

        
def train_model(train_f):
    """ train/learn the logistic regression model """

    import random
    from sklearn.linear_model import logistic
    
    train_data = loadtxt(train_f)
    [r, c] = train_data.shape
    pos_train   = train_data[train_data[:, c-1] == 1]
    neg_train_e = train_data[train_data[:, c-1] == 0]
    
    pos_ratio = 0.21;
    pos_nb    =  len(pos_train)
    neg_nb    = int(pos_nb / pos_ratio) - pos_nb
    neg_train = array(random.sample(neg_train_e, neg_nb))
    
    Xtrain  = vstack((pos_train[:, 0:c-1], neg_train[:, 0:c-1]))
    ytrain  = array (list(pos_train[:, c-1]) + list(neg_train[:, c-1]))

    clf = logistic.LogisticRegression().fit(Xtrain, ytrain)
    serialize.saveData("model", clf, where="./", suffix = ".seg")     

  
def apply_model(test_f):
    """ apply the model to the test_f """

    Xtest = loadtxt(test_f)
    clf = serialize.loadData("model", where="./", suffix=".seg")
    
    return clf.predict(Xtest)
    
   

def processLROutput(tok_f, word_f, pred, segOutfileTs):
    
    """ writes sentences with edu break (decisions got from LR) for further processing"""
        
    [INF1, INF3]  = [open(word_f,  'r'), open(tok_f,   'r')]
    [curSen, linetowrite, output] = ["", "", ""]
    [nbSen, wc1, wc2, wc3, w_id]  = [0, 0, 0, 0, 0]
        
    for word in INF1:
        word     = word.strip()
        if word:
            curSen += word + " "
            line2 = pred[w_id]
            wc1 += 1
            w_id += 1
            
            if line2 == 1:
                linetowrite += word + " \n"
                wc2 += 1
                
            else:
                linetowrite += word + " "
                wc2 += 1
            
            flag = 0    

        elif flag == 0:
            eduline = INF3.readline()
            eduline = eduline.strip()
            nbSen   += 1
            
            eduline = re.sub("\s*</?s>\s*", "", eduline)
            
            allTok  = eduline.split(' ')
            wc3 += len(allTok)                

            curSen += allTok[-1]
            wc1 += 1

            while curSen != eduline and len(allTok) == 1:
                output +=  eduline + " <S>\n"  
                wc2 += 1
                wc1 += 1
                
                curSen = re.sub(allTok[-1]+"$", "", curSen)
                wc1 -= 1
                
                eduline = INF3.readline()
                nbSen   += 1

                eduline = eduline.strip()
                eduline = eduline.replace(" EDU_BREAK ", " ")
                allTok  = eduline.split(' ')
                wc3 += len(allTok)    
                curSen += allTok[-1]
                wc1 += 1
                
            if curSen != eduline and len(allTok) != 1:                   

                print "\n Error!!! cursen and eduline aren't same"
                print curSen
                print eduline                    
                raw_input("handle it!!!")


            if curSen == eduline:
                linetowrite += allTok[-1]
                linetowrite += " <S>"
                wc2 += 1
                output += linetowrite + "\n"                
                
            else:
                print "\n should never execute..."
                raw_input("")
            
            
            curSen = ""
            linetowrite = ""
            flag   = 1                
    
    #sanity check    
    if wc1 != wc2 != wc3:
        print "Error! word counts aren't same"
        raw_input("handle")
        

    INF1.close()
    INF3.close()
    
    #apply rule based fix now
    intOutput = ruleBasedFix(output)

    EOSPAT     = re.compile("\s*\<S\>\n*")
    OUTF   = open(segOutfileTs, 'w')
    outputlines = EOSPAT.split(intOutput)

    nbSen2 = 0
        
    for line in outputlines:

        line = line.strip()

        if not line:
            continue
        
        nbSen2 += 1
        fstr = re.findall("--", line)
        
        if len (fstr) == 1 and (not re.search("^-- ", line)) and (not re.search("\n-- ", line)):
            line = re.sub(" -- \n?", " \n-- ", line)
               
        if len (fstr) == 2:
            line = re.sub("\n?-- ", "\n-- ", line, 1)                    
            
            if not re.search(" -- \n", line):        
                line = re.sub(" -- ", " -- \n", line, 1)
                                
            fstri = re.findall("(\n-- [^\s]+)\s", line)
            
            if len (fstri) == 2:
                rep = re.sub("\n-- ", "-- \n", fstri[1])                   
                line = re.sub(fstri[1], rep, line)

        line = line.strip()
        line = re.sub("\s*\n+\s*", " EDU_BREAK ", line)
        print line
        print >>OUTF, line  

    OUTF.close()
    
    #sanity check        
    if nbSen2 != nbSen:
        print "\n Error in nb of sentence!!!" + str (len(outputlines)) + " and " + str(nbSen)
        raw_input('handle it')
   

def ruleBasedFix (output):

    alllines  = output.split('\n')
    lines     = []
    intOutput = ""
    
    for line in alllines:

        if line:

            line = re.sub(" ` ` ", " `` ", line)
            line = re.sub("^` ` ",  "`` ", line)
            line = re.sub(" ' ' ", " '' ", line)
            line = re.sub(" ' '$",  " ''", line)
            line = re.sub("^' '",    "''", line)
            lines.append(line)
            

    skip = 0

    for k in range(len(lines)):
        
        if skip == 1:
            skip = 0
            continue
        
        if k+1 < len(lines):
            
            if re.search("^\:( *)$|^\<S\>( *)$|^\. \<S\>( *)$|^;( *)$|^,( *)$|^, ''( *)$", lines[k+1]):
                lines[k] += lines[k+1]
                skip = 1
                 
            elif re.search("(^, |^' )(.*)", lines[k+1]):
                m = re.search("(^, |^' )(.*)", lines[k+1])
                lines[k]  += m.group(1)
                lines[k+1] = m.group(2)
                lines[k] = re.sub(" ' ' $", " ''", lines[k])
                skip = 0


            elif re.search("-- ", lines[k]) and (not re.search("\<S\>$", lines[k])) and re.search("^(-- )(.+)", lines[k+1]):
                m = re.search("^(-- )(.+)", lines[k+1]) 
                lines[k]  += m.group(1)
                lines[k+1] = m.group(2)
                skip = 0

            elif re.search("-- ", lines[k])  and re.search("^--( *)$", lines[k+1]):
                lines[k] += lines[k+1]
                skip = 1

            elif ( not re.search("\<S\>$", lines[k]) ) and ( re.search("^--( *)$", lines[k+1])  or re.search("^-- \<S\>$", lines[k+1]) ):
                lines[k] += lines[k+1]
                skip = 1
            
            elif re.search("^--( *)$", lines[k]):
                lines[k+1] = lines[k] + lines[k+1]
                intOutput += lines[k+1] + "\n"               
                skip =1
                continue
            else:
                skip = 0
                        
            intOutput += lines[k] + "\n" 
        else:
            intOutput += lines[k] + "\n" 

    return intOutput


def do_segment(infile):
    """ this is the main segmentation module """
    
    [tok_f, tag_f, par_f] = do_preprocess(infile)
    has_one_word = extract_features(tok_f, par_f, tag_f, "tmp.feat", "tmp.words", edufile = "tmp.edu")   

    if has_one_word != -1:
        train_model("train.seg")
        pred = apply_model("tmp.feat")
        processLROutput("tmp.tok", "tmp.words", pred, "tmp.edu") 

        os.unlink("tmp.words")
        os.unlink("tmp.feat")

if __name__ == "__main__":    
    do_segment(sys.argv[1])
#    do_segment("tmp.raw")
   
