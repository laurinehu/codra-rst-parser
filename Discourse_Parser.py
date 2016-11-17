import sys
import re
import subprocess
import SynFeatures
import TopicFeatures
import ContFeatures
import serialize
import os
import Parse


def preprocess(ts_edufile):
    """ create .fmt to extract the dominance sets"""
    
    ts_fmtfile      = "tmp.fmt"
   
    F_EDU_TS_R = open(ts_edufile, 'r')
    F_FMT_TS_W = open(ts_fmtfile, 'w')
    
    for sen in F_EDU_TS_R:
        sen  = sen.strip()
        edus = re.split("\s*EDU_BREAK\s*", sen)
        
        if not edus:
            print "\n ERROR .. EMPTY EDUS.. " + sen
            raw_input(' ')
        
        print >>F_FMT_TS_W, len(edus)

        for edu in edus:
            edu = edu.strip()
            if edu:
                print >>F_FMT_TS_W, str(len(edu.split())) + " " + edu
                
            else:
                print "\n Error!!! empty edu"
                raw_input(' ')
             
            
    F_EDU_TS_R.close()
    F_FMT_TS_W.close()

    SynFeatures.extractDomSets("tmp.chp", "tmp.fmt")#okay
    TopicFeatures.computeLexChains("tmp.tag")
    
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

def getTaggedText(tagline, span1text, bEdu, eEdu, edu_tokNb):
    
    sWordNb = 0
    for i in range(bEdu-1):
        sWordNb += edu_tokNb[i]
        
    eWordNb = 0
    for i in range(eEdu):
        eWordNb += edu_tokNb[i]    
    
    parts = re.findall(r"\(([^)]+\)?\.?)\)\s", tagline + '\n')
    taggedText = " ". join([ re.sub(" ", "_/", apair) for apair in parts[sWordNb:eWordNb]])
    untaggedText = re.sub("[^_\s]+?_/", "", taggedText)
    
    
    if untaggedText != span1text:
        print tagline
        print taggedText
        print "Error!! texts aren't same.. " + untaggedText + "\n" + span1text
        raw_input(' ')
        
    return taggedText



def findFeaturesForUpperDTs(F_W, spans, span_text, span_text_ng, unigram, bigram, trigram, span_text_tag, span_sen):    
    """ find features (just edu nbs) for the upper-level DTs """

    chains = []
    TopicFeatures.read_chains("tmp.chn", chains) 
    
    spanNb = len(spans)
    totalEduNb = int (spans[spanNb - 1].split(":") [1])

    struct_featLine = {}

    if spanNb > 1:
        for s in range(2, spanNb+1):
            for i in range(1, spanNb-s+2): #ok
                j = i+s-1 #ok
                for k in range(i, j):
                        
                    i_span = re.search("(\d+):(\d+)", spans[i-1])                                                        
                    k_span = re.search("(\d+):(\d+)", spans[k-1])
                    j_span = re.search("(\d+):(\d+)", spans[j-1])

                    astruct = "(" + i_span.group(1) + ":" + k_span.group(2) + "," + str( int (k_span.group(2) ) + 1)  + ":" + j_span.group(2) + ")" #ok
                    
                    m1 = re.search("\((\d+):(\d+),(\d+):(\d+)\)", astruct)
                    s1eduNb = int (m1.group(2)) - int (m1.group(1))  + 1
                    s2eduNb = int (m1.group(4)) - int (m1.group(2)) 

                    # sentence nb and para nb and belong to same paragraph
                    [span1_text, span2_text, span1SenNb, span1ParNb, span2SenNb, span2ParNb, samePara] = ["", "", 0, 0, 0, 0, 1]
                    [span1_text_ng, span2_text_ng] = ["", ""]
                    [span1_text_tag, span2_text_tag] = ["", ""]

                    for x in range(i-1, k):
                        if re.search("\s*<S>$", span_text[spans[x]]):
                            span1SenNb += 1
                        if re.search("\s*<P>\s*<S>$", span_text[spans[x]]):
                            span1ParNb += 1
                        if x == k-1 and re.search("\s*<P>\s*<S>$", span_text[spans[x]]):
                            samePara = 0
                                                                                               
                        span1_text   += re.sub("(\s*<P>)?\s*<S>$", "", span_text[spans[x]]) 
                        span1_text   += " "
                        span1_text_ng   += span_text_ng[spans[x]] + " " 
                        span1_text_tag  += span_text_tag[spans[x]] + " "  

                    span1_text = span1_text.strip()
                    span1_text_ng  = span1_text_ng.strip()
                    span1_text_tag = span1_text_tag.strip()
                    span1tokNb_t = len(span1_text.split())

                    for x in range(k, j):
                        if re.search("\s*<S>$", span_text[spans[x]]):
                            span2SenNb += 1                                
                        if re.search("\s*<P>\s*<S>$", span_text[spans[x]]):
                            span2ParNb += 1

                        span2_text   += re.sub("(\s*<P>)?\s*<S>$", "", span_text[spans[x]]) 
                        span2_text   += " "                            
                        span2_text_ng += span_text_ng[spans[x]] + " "   
                        span2_text_tag += span_text_tag[spans[x]] + " "   

                    span2_text = span2_text.strip()
                    span2_text_ng = span2_text_ng.strip()
                    span2_text_tag = span2_text_tag.strip()
                    span2tokNb_t = len(span2_text.split())
                    
                        
                    #relative number of edus
                    span1EduNb = round( (int (k_span.group(2) ) - int (i_span.group(1) ) + 1 ) /  float ( int (j_span.group(2)) - int (i_span.group(1) ) + 1 ), 1) #ok
                    span2EduNb = round( (int (j_span.group(2) ) - int (k_span.group(2) )     ) /  float ( int (j_span.group(2)) - int (i_span.group(1) ) + 1 ), 1) #ok

                    #relative number of tokens
                    span1tokNb = round(span1tokNb_t / float (span1tokNb_t + span2tokNb_t), 1) 
                    span2tokNb = round(span2tokNb_t / float (span1tokNb_t + span2tokNb_t), 1) 

                    #relative number of sentence and paragraph breaks
                    span1SenNb_r = round(span1SenNb / float (span1SenNb + span2SenNb), 1) if span1SenNb + span2SenNb else 0.0
                    span2SenNb_r = round(span2SenNb / float (span1SenNb + span2SenNb), 1) if span1SenNb + span2SenNb else 0.0
                    span1ParNb_r = round(span1ParNb / float (span1ParNb + span2ParNb), 1) if span1ParNb + span2ParNb else 0.0
                    span2ParNb_r = round(span2ParNb / float (span1ParNb + span2ParNb), 1) if span1ParNb + span2ParNb else 0.0
                    
                    #distance/position
                    span1disEduFrmBeg = round( ( int (i_span.group(1) ) - 1)/ float(totalEduNb), 1)
                    span2disEduFrmBeg = round(   int (k_span.group(2) )     / float(totalEduNb), 1)
                    span1disEduFrmEnd = round( (totalEduNb - int (i_span.group(1) )) / float(totalEduNb), 1)
                    span2disEduFrmEnd = round( (totalEduNb - int (k_span.group(2)) - 1) / float(totalEduNb), 1)

                    #ngrams
                    span1words = span1_text_ng.split()
                    span2words = span2_text_ng.split()                            

                    #Unigram
                    fword_s1 = span1words[0].lower()  if unigram.has_key(span1words[0].lower())  else "u"
                    lword_s1 = span1words[-1].lower() if unigram.has_key(span1words[-1].lower()) else "u"
                    fword_s2 = span2words[0].lower()  if unigram.has_key(span2words[0].lower())  else "u"
                    lword_s2 = span2words[-1].lower() if unigram.has_key(span2words[-1].lower()) else "u"
                                    
                    #bigram
                    if len(span1words) > 1:
                        fbi_s1 = span1words[0].lower() + "_"  + span1words[1].lower()   if bigram.has_key(span1words[0].lower() + "_" + span1words[1].lower())   else   "u"
                        lbi_s1 = span1words[-2].lower() + "_" + span1words[-1].lower()  if bigram.has_key(span1words[-2].lower() + "_" + span1words[-1].lower()) else   "u"
                    else:
                        fbi_s1 = "u"
                        lbi_s1 = "u"
                    if len(span2words) > 1:
                        fbi_s2 = span2words[0].lower() + "_" + span2words[1].lower()   if bigram.has_key(span2words[0].lower() + "_" + span2words[1].lower())   else   "u"
                        lbi_s2 = span2words[-2].lower() + "_" + span2words[-1].lower() if bigram.has_key(span2words[-2].lower() + "_" + span2words[-1].lower()) else   "u"
                    else:
                        fbi_s2 = "u"
                        lbi_s2 = "u"
                                    
                    #trigram
                    if len(span1words) > 2:
                        ftri_s1 = span1words[0].lower()  + "_" + span1words[1].lower()  + "_" + span1words[2].lower()  if trigram.has_key(span1words[0].lower()  + "_" + span1words[1].lower()  + "_" + span1words[2].lower())    else   "u"
                        ltri_s1 = span1words[-3].lower() + "_" + span1words[-2].lower() + "_" + span1words[-1].lower() if trigram.has_key(span1words[-3].lower() + "_" + span1words[-2].lower() + "_" + span1words[-1].lower())   else   "u"
                    else:
                        ftri_s1 = "u"
                        ltri_s1 = "u"
                        
                    if len(span2words) > 2:
                        ftri_s2 = span2words[0].lower()  + "_" + span2words[1].lower()  + "_" + span2words[2].lower()  if trigram.has_key(span2words[0].lower()   + "_"  + span2words[1].lower()  + "_" + span2words[2].lower())    else  "u"
                        ltri_s2 = span2words[-3].lower() + "_" + span2words[-2].lower() + "_" + span2words[-1].lower() if trigram.has_key(span2words[-3].lower()  + "_" + span2words[-2].lower()  + "_" + span2words[-1].lower())   else  "u"
                    else:
                        ftri_s2 = "u"
                        ltri_s2 = "u"

                    #pos ngrams
                    span1tagwords = span1_text_tag.split()
                    span2tagwords = span2_text_tag.split()                            

                    #Unigram
                    fpos_s1 = re.sub("_/.*", "", span1tagwords[0])
                    lpos_s1 = re.sub("_/.*", "", span1tagwords[-1])
                    fpos_s2 = re.sub("_/.*", "", span2tagwords[0])
                    lpos_s2 = re.sub("_/.*", "", span2tagwords[-1])

                    #bigram
                    if len(span1tagwords) > 1:
                        fpos_bi_s1 = re.sub("_/.*", "", span1tagwords[0])  + "_" + re.sub("_/.*", "",span1tagwords[1])
                        lpos_bi_s1 = re.sub("_/.*", "", span1tagwords[-2]) + "_" + re.sub("_/.*", "",span1tagwords[-1])
                    else:
                        fpos_bi_s1 = "U_"  + fpos_s1
                        lpos_bi_s1 = lpos_s1 + "_U"
                                
                    if len(span2tagwords) > 1:
                        fpos_bi_s2 = re.sub("_/.*", "", span2tagwords[0])  + "_" + re.sub("_/.*", "", span2tagwords[1])
                        lpos_bi_s2 = re.sub("_/.*", "", span2tagwords[-2]) + "_" + re.sub("_/.*", "", span2tagwords[-1])
                    else:
                        fpos_bi_s2 = "U_" + fpos_s2 
                        lpos_bi_s2 = lpos_s2 + "_U" 

                    span1_sen = [span_sen[spans[i-1]], span_sen[spans[k-1]]]                          
                    span2_sen = [span_sen[spans[k]], span_sen[spans[j-1]]]
                    ch_feat = TopicFeatures.computeChainFeatures(chains, span1_sen, span2_sen)
                    
                    label = " ".join(map (str, [0, "U"])) #ok

                    fline = label + " ---- " + " S1ENb=" + str(s1eduNb) + " S2ENb=" + str(s2eduNb)
                    fline += " S1en=" + str(span1EduNb) + " S2en="  + str(span2EduNb)  + " S1tn=" + str(span1tokNb) + " S2tn=" + str(span2tokNb)  + " S1sn=" + str(span1SenNb_r) + " S2sn=" + str(span2SenNb_r) + " S1pn=" + str(span1ParNb_r) + " S2pn=" + str(span2ParNb_r) + " sp=" + str(samePara) + " S1edB=" + str(span1disEduFrmBeg) + " S1edE=" + str(span1disEduFrmEnd) + " S2edB=" + str(span2disEduFrmBeg) + " S2edE=" + str(span2disEduFrmEnd)
                    fline += " fws1=" + fword_s1 + " lws1=" + lword_s1 + " fws2=" + fword_s2 + " lws2=" + lword_s2 + " fbis1=" + fbi_s1 + " lbis1=" + lbi_s1 + " fbis2=" + fbi_s2 + " lbis2=" + lbi_s2 + " ftrs1=" + ftri_s1 + " ltrs1=" + ltri_s1 + " ftrs2=" + ftri_s2 + " ltrs2=" + ltri_s2
                    fline += " fps1=" + fpos_s1  + " lps1=" + lpos_s1  + " fps2=" + fpos_s2  + " lps2=" + lpos_s2  + " fpbis1=" + fpos_bi_s1 + " lpbis1=" + lpos_bi_s1 + " fpbis2=" + fpos_bi_s2 + " lpbis2=" + lpos_bi_s2
                    fline += " " + ch_feat
                    struct_featLine[astruct] = fline

        #now compute all (including contextual) features
        for s in range(2, spanNb+1):
            for i in range(1, spanNb-s+2): #ok
                j = i+s-1 #ok
                for k in range(i, j):

                    l1_feat = {'to':[], 'ng':[]}
                    l2_feat = {'to':[], 'ng':[]}
                    l0_feat = {'to':[], 'ng':[]}
                      
                    i_span = re.search("(\d+):(\d+)", spans[i-1])                                                        
                    k_span = re.search("(\d+):(\d+)", spans[k-1])
                    j_span = re.search("(\d+):(\d+)", spans[j-1])

                    astruct = "(" + i_span.group(1) + ":" + k_span.group(2) + "," + str( int (k_span.group(2) ) + 1)  + ":" + j_span.group(2) + ")" #ok
                    all_feat = struct_featLine[astruct]
                    
                    if j == spanNb: #last struct
                        pass                        

                    else:
                        nextstruct = "(" + str( int (k_span.group(2) ) + 1) + ":" + j_span.group(2) + "," + spans[j].split(':')[0] + ":" + spans[j].split(':')[1] + ")"
                        ContFeatures.getDifferentFeaturesForUGM(struct_featLine[nextstruct], l2_feat)
                        all_feat += ContFeatures.getFeatureVector(l2_feat, pre='N')
                    
                    if i == 1: #begining 
                        pass                    

                    else:
                        prevstruct = "(" + spans[i-2].split(':')[0] + ":" + spans[i-2].split(':')[1] + "," + i_span.group(1) + ":" + k_span.group(2) + ")"
                        ContFeatures.getDifferentFeaturesForUGM(struct_featLine[prevstruct], l0_feat)
                        all_feat += ContFeatures.getFeatureVector(l0_feat, pre='P')

                    print >>F_W, all_feat
                    print >>F_W        

    else:
        return "no"

    return "yes"

def extract_features():
    """ extract features for discourse parsing """

    [domfile, tokfile, edufile, tagfile]  = ["tmp.dom", "tmp.tok", "tmp.edu", "tmp.tag"]
    [F_DOM, F_TOK, F_EDU, F_TAG]       = [open(domfile, 'r'), open(tokfile, 'r'), open(edufile, 'r'), open(tagfile, 'r')]

    [feat_f_sen, feat_f_doc]   = ["sen_par.feat", "tmp_doc.feat"] #feature files
    [F_W, F_W2]       = [open(feat_f_sen, 'w'), open(feat_f_doc, 'w')]

    # load ngram dictionaries
    ngramDir = "ngrams/"    
    [unigram, bigram, trigram]  = [serialize.loadData("Unigram_sen", ngramDir), serialize.loadData("Bigram_sen",  ngramDir), serialize.loadData("Trigram_sen", ngramDir)]
    [unigram_doc, bigram_doc, trigram_doc]   = [serialize.loadData("Unigram_doc", ngramDir), serialize.loadData("Bigram_doc",  ngramDir), serialize.loadData("Trigram_doc", ngramDir)]

    [eduIndex, eduNb, spans, span_text, span_text_ng, span_text_tag, span_sen, senNb] = [0, 0, [], {}, {}, {}, {}, 0]
    
    flag = 0

    #do sentences first
    for tokline, eduline, tagline in zip(F_TOK, F_EDU, F_TAG):
        tokline = re.sub("</?s>", "", tokline).strip()

        tokNb = len(tokline.split())
        edus = re.split("\s*EDU_BREAK\s*", eduline.strip())    

        edu_tokNb = {}
        for id, edu in enumerate(edus):
            edu_tokNb.setdefault(id, len(edu.split()))

        firline = F_DOM.readline()
        tmp     = firline.split()
        eduNb   = int (tmp[0])
        garbage = F_DOM.readline() #the sentence
        domline = F_DOM.readline() #feature line
        domline = domline.strip()            
        garbage = F_DOM.readline()

        tagline = tagline.strip()            

        if not re.match("---", garbage):
            print "Error in reading .dom file"
            raw_input(' ')

        domline = re.sub("Depend:", "", domline)            
            
        if domline == "NONE" and eduNb != 1:    
            print "Error not synchronised.. "
            raw_input(' ')

        if eduNb > 1:
            flag = 1
                            
            for s in range(2, eduNb+1):                    
                structs = {}
                for i in range(1, eduNb-s+2):
                    j = i+s-1
                    for k in range(i, j):                                                
                        if (i == 1 and j == eduNb) or s == 2:                                                        
                            astruct = "(" + str(i) + ":" + str(k) + "," + str(k+1) + ":" + str(j) + ")"
                            
                            #syntactic features
                            domEle = SynFeatures.getRelatedDomSet(astruct, domline)

                            if domEle:
                                [n_h_pos, n_a_pos, n_h_lex, n_a_lex, whichspan, s1eduNb, s2eduNb] = SynFeatures.getDomFeatures(domEle, astruct) 
                            else:
                                m1 = re.search("\((\d+):(\d+),(\d+):(\d+)\)", astruct)
                                s1eduNb = int (m1.group(2)) - int (m1.group(1))  + 1
                                s2eduNb = int (m1.group(4)) - int (m1.group(2))                                     
                                [whichspan,n_h_pos,n_a_pos,n_h_lex,n_a_lex]  = ["u", "u", "u", "u", "u"]
                                
                            #textual orgnaizational features
                            [span1EduNb, span2EduNb, span1EduNb2, span2EduNb2]   = [round (float ( k - i + 1 ) / (j -i + 1), 1), round (float ( j - k ) / (j -i + 1), 1), round (float ( k - i + 1 ) / eduNb, 1), round (float ( j - k ) / eduNb, 1)]

                            [span1tokNb_t, span2tokNb_t, span1text, span2text] = [0, 0, "", ""]

                            for x in range(i-1, k):
                                span1tokNb_t += len(edus[x].split())
                                span1text  += edus[x] + " "

                            for x in range(k, j):
                                span2tokNb_t += len(edus[x].split())
                                span2text  += edus[x] + " "

                            [span1tokNb, span2tokNb]    = [round(span1tokNb_t / float (span1tokNb_t + span2tokNb_t), 1), round(span2tokNb_t / float (span1tokNb_t + span2tokNb_t), 1)] 
                            [span1tokNb2, span2tokNb2]  = [round(span1tokNb_t / float (tokNb), 1), round(span2tokNb_t / float (tokNb), 1)] 
                            [span1disEduFrmBeg, span2disEduFrmBeg, span1disEduFrmEnd, span2disEduFrmEnd] = [round( (i - 1)/ float(eduNb), 1), round( k / float(eduNb), 1), round( (eduNb - i) / float(eduNb), 1), round( (eduNb - k - 1) / float(eduNb), 1)]

                            span1tagtext = getTaggedText(tagline, span1text.strip(), i, k, edu_tokNb)    
                            span2tagtext = getTaggedText(tagline, span2text.strip(), k+1, j, edu_tokNb)
                            [span1tagwords, span2tagwords] = [span1tagtext.split(), span2tagtext.split()]

                            #ngram features
                            span1text = re.sub("\s*<P>$", "", span1text.strip())
                            span1text = "<s> " + span1text if i == 1 else "<e> " + span1text 
                            span1text = span1text + " </e>" 

                            span2text = re.sub("\s*<P>$", "", span2text.strip())
                            span2text = span2text + " </s>" if j == eduNb else span2text + " </e>"
                            span2text = "<e> " + span2text 

                            [span1words,span2words]  = [span1text.split(), span2text.split()]                            
                    
                            #Unigram
                            fword_s1 = span1words[0].lower()  if unigram.has_key(span1words[0].lower())  else "u"
                            lword_s1 = span1words[-1].lower() if unigram.has_key(span1words[-1].lower()) else "u"
                            fword_s2 = span2words[0].lower()  if unigram.has_key(span2words[0].lower())  else "u"
                            lword_s2 = span2words[-1].lower() if unigram.has_key(span2words[-1].lower()) else "u"
                            
                            #bigram
                            if len(span1words) > 1:
                                fbi_s1 = span1words[0].lower() + "_"  + span1words[1].lower()   if bigram.has_key(span1words[0].lower() + "_" + span1words[1].lower())   else   "u"
                                lbi_s1 = span1words[-2].lower() + "_" + span1words[-1].lower()  if bigram.has_key(span1words[-2].lower() + "_" + span1words[-1].lower()) else   "u"
                            else:
                                fbi_s1 = "u"
                                lbi_s1 = "u"
                            if len(span2words) > 1:
                                fbi_s2 = span2words[0].lower() + "_" + span2words[1].lower()   if bigram.has_key(span2words[0].lower() + "_" + span2words[1].lower())   else   "u"
                                lbi_s2 = span2words[-2].lower() + "_" + span2words[-1].lower() if bigram.has_key(span2words[-2].lower() + "_" + span2words[-1].lower()) else   "u"
                            else:
                                fbi_s2 = "u"
                                lbi_s2 = "u"

                            #trigram
                            if len(span1words) > 2:
                                ftri_s1 = span1words[0].lower()  + "_" + span1words[1].lower()  + "_" + span1words[2].lower()  if trigram.has_key(span1words[0].lower()  + "_" + span1words[1].lower()  + "_" + span1words[2].lower())    else   "u"
                                ltri_s1 = span1words[-3].lower() + "_" + span1words[-2].lower() + "_" + span1words[-1].lower() if trigram.has_key(span1words[-3].lower() + "_" + span1words[-2].lower() + "_" + span1words[-1].lower())   else   "u"
                            else:
                                ftri_s1 = "u"
                                ltri_s1 = "u"
                
                            if len(span2words) > 2:
                                ftri_s2 = span2words[0].lower()  + "_" + span2words[1].lower()  + "_" + span2words[2].lower()  if trigram.has_key(span2words[0].lower()   + "_"  + span2words[1].lower()  + "_" + span2words[2].lower())    else  "u"
                                ltri_s2 = span2words[-3].lower() + "_" + span2words[-2].lower() + "_" + span2words[-1].lower() if trigram.has_key(span2words[-3].lower()  + "_" + span2words[-2].lower()  + "_" + span2words[-1].lower())   else  "u"
                            else:
                                ftri_s2 = "u"
                                ltri_s2 = "u"

                            #Unigram
                            fpos_s1 = re.sub("_/.*", "", span1tagwords[0])
                            lpos_s1 = re.sub("_/.*", "", span1tagwords[-1])
                            fpos_s2 = re.sub("_/.*", "", span2tagwords[0])
                            lpos_s2 = re.sub("_/.*", "", span2tagwords[-1])

                            #bigram
                            if len(span1tagwords) > 1:
                                fpos_bi_s1 = re.sub("_/.*", "", span1tagwords[0])  + "_" + re.sub("_/.*", "",span1tagwords[1])
                                lpos_bi_s1 = re.sub("_/.*", "", span1tagwords[-2]) + "_" + re.sub("_/.*", "",span1tagwords[-1])
                            else:
                                fpos_bi_s1 = "U_"  + fpos_s1
                                lpos_bi_s1 = lpos_s1 + "_U"
                        
                            if len(span2tagwords) > 1:
                                fpos_bi_s2 = re.sub("_/.*", "", span2tagwords[0])  + "_" + re.sub("_/.*", "", span2tagwords[1])
                                lpos_bi_s2 = re.sub("_/.*", "", span2tagwords[-2]) + "_" + re.sub("_/.*", "", span2tagwords[-1])
                            else:
                                fpos_bi_s2 = "U_" + fpos_s2 
                                lpos_bi_s2 = lpos_s2 + "_U" 

                            label = " ".join(map (str, [0, "U"]))
                            print >>F_W, label + " ---- " + " dr=" + whichspan + " S1ENb=" + str(s1eduNb) + " S2ENb=" + str(s2eduNb) + " hp=" + n_h_pos + " hl=" + n_h_lex.lower() + " ap=" + n_a_pos + " al=" + n_a_lex.lower(),
                            print >>F_W, "S1en=" + str(span1EduNb) + " S1en2=" + str(span1EduNb2) + " S2en="  + str(span2EduNb)  + " S2en2=" + str(span2EduNb2) + " S1tn=" + str(span1tokNb) + " S1tn2=" + str(span1tokNb2) + " S2tn=" + str(span2tokNb) + " S2tn2=" + str(span2tokNb2) + " S1edB=" + str(span1disEduFrmBeg) + " S1edE=" + str(span1disEduFrmEnd) + " S2edB=" + str(span2disEduFrmBeg) + " S2edE=" + str(span2disEduFrmEnd),
                            print >>F_W, "fws1=" + fword_s1 + " lws1=" + lword_s1 + " fws2=" + fword_s2 + " lws2=" + lword_s2 + " fbis1=" + fbi_s1 + " lbis1=" + lbi_s1 + " fbis2=" + fbi_s2 + " lbis2=" + lbi_s2 + " ftrs1=" + ftri_s1 + " ltrs1=" + ltri_s1 + " ftrs2=" + ftri_s2 + " ltrs2=" + ltri_s2,
                            print >>F_W, "fps1=" + fpos_s1  + " lps1=" + lpos_s1  + " fps2=" + fpos_s2  + " lps2=" + lpos_s2  + " fpbis1=" + fpos_bi_s1 + " lpbis1=" + lpos_bi_s1 + " fpbis2=" + fpos_bi_s2 + " lpbis2=" + lpos_bi_s2

                            if s != 2:
                                print >>F_W

                        else:
                            thisSeq = []
                            isDup = getSeguence(i, k, j, eduNb, structs, thisSeq)

                            if not isDup: 
                                for st in thisSeq:
                                    
                                    #syntactic features
                                    domEle = SynFeatures.getRelatedDomSet(st, domline) 
                                    if domEle:
                                        [n_h_pos, n_a_pos, n_h_lex, n_a_lex, whichspan, s1eduNb, s2eduNb] = SynFeatures.getDomFeatures(domEle, st) 
                                    else:
                                        m1 = re.search("\((\d+):(\d+),(\d+):(\d+)\)", st)
                                        s1eduNb = int (m1.group(2)) - int (m1.group(1))  + 1
                                        s2eduNb = int (m1.group(4)) - int (m1.group(2))  
                                        [whichspan,n_h_pos,n_a_pos,n_h_lex,n_a_lex]  = ["u", "u", "u", "u", "u"]

                                    #textual orgnaizational features
                                    m1   = re.search("\((\d+):(\d+),(\d+):(\d+)\)", st)
                                    [ii,kk,jj]     = [int (m1.group(1)), int (m1.group(2)), int (m1.group(4))]
                                    [span1EduNb, span2EduNb]   = [round (float ( kk - ii + 1 ) / ( jj - ii + 1 ), 1), round (float ( jj - kk ) / ( jj - ii + 1 ), 1)]
                                    [span1EduNb2,span2EduNb2]  = [round (float ( kk - ii + 1 ) / eduNb, 1), round (float ( jj - kk ) / eduNb, 1)]

                                    [span1tokNb_t, span2tokNb_t, span1text, span2text] = [0, 0, "", ""]
                                    for x in range(ii-1, kk):
                                        span1tokNb_t += len(edus[x].split())
                                        span1text  += edus[x] + " "

                                    for x in range(kk, jj):
                                        span2tokNb_t += len(edus[x].split())
                                        span2text  += edus[x] + " "

                                    [span1tokNb,span2tokNb]   = [round(span1tokNb_t / float (span1tokNb_t + span2tokNb_t), 1), round(span2tokNb_t / float (span1tokNb_t + span2tokNb_t), 1) ]
                                    [span1tokNb2,span2tokNb2] = [round(span1tokNb_t / float (tokNb), 1), round(span2tokNb_t / float (tokNb), 1)] 
                                    [span1disEduFrmBeg, span2disEduFrmBeg, span1disEduFrmEnd, span2disEduFrmEnd] = [round( (ii - 1)/ float(eduNb), 1), round( kk / float(eduNb), 1), round( (eduNb - ii) / float(eduNb), 1), round( (eduNb - kk - 1) / float(eduNb), 1)]

                                    span1tagtext = getTaggedText(tagline, span1text.strip(), ii, kk, edu_tokNb)    
                                    span2tagtext = getTaggedText(tagline, span2text.strip(), kk+1, jj, edu_tokNb)    
                                    [span1tagwords, span2tagwords] = [span1tagtext.split(), span2tagtext.split()]

                                    #ngram features
                                    span1text = re.sub("\s*<P>$", "", span1text.strip())    
                                    span1text = "<s> " + span1text if ii == 1 else "<e> " + span1text            
                                    span1text = span1text + " </e>" 
                
                                    span2text = re.sub("\s*<P>$", "", span2text.strip())    
                                    span2text = span2text + " </s>" if jj == eduNb else span2text + " </e>"            
                                    span2text = "<e> " + span2text 

                                    [span1words, span2words]  = [span1text.split(), span2text.split()]

                                    #Unigram
                                    fword_s1 = span1words[0].lower()  if unigram.has_key(span1words[0].lower())  else "u"
                                    lword_s1 = span1words[-1].lower() if unigram.has_key(span1words[-1].lower()) else "u"
                                    fword_s2 = span2words[0].lower()  if unigram.has_key(span2words[0].lower())  else "u"
                                    lword_s2 = span2words[-1].lower() if unigram.has_key(span2words[-1].lower()) else "u"

                                    #bigram
                                    if len(span1words) > 1:
                                        fbi_s1 = span1words[0].lower() + "_"  + span1words[1].lower()   if bigram.has_key(span1words[0].lower() + "_" + span1words[1].lower())   else   "u"
                                        lbi_s1 = span1words[-2].lower() + "_" + span1words[-1].lower()  if bigram.has_key(span1words[-2].lower() + "_" + span1words[-1].lower()) else   "u"
                                    else:
                                        fbi_s1 = "u"
                                        lbi_s1 = "u"
                            
                                    if len(span2words) > 1:
                                        fbi_s2 = span2words[0].lower() + "_" + span2words[1].lower()   if bigram.has_key(span2words[0].lower() + "_" + span2words[1].lower())   else   "u"
                                        lbi_s2 = span2words[-2].lower() + "_" + span2words[-1].lower() if bigram.has_key(span2words[-2].lower() + "_" + span2words[-1].lower()) else   "u"
                                    else:
                                        fbi_s2 = "u"
                                        lbi_s2 = "u"

                                    #trigram
                                    if len(span1words) > 2:
                                        ftri_s1 = span1words[0].lower()  + "_" + span1words[1].lower()  + "_" + span1words[2].lower()  if trigram.has_key(span1words[0].lower()  + "_" + span1words[1].lower()  + "_" + span1words[2].lower())    else   "u"
                                        ltri_s1 = span1words[-3].lower() + "_" + span1words[-2].lower() + "_" + span1words[-1].lower() if trigram.has_key(span1words[-3].lower() + "_" + span1words[-2].lower() + "_" + span1words[-1].lower())   else   "u"
                                    else:
                                        ftri_s1 = "u"
                                        ltri_s1 = "u"
                
                                    if len(span2words) > 2:
                                        ftri_s2 = span2words[0].lower()  + "_" + span2words[1].lower()  + "_" + span2words[2].lower()  if trigram.has_key(span2words[0].lower()   + "_"  + span2words[1].lower()  + "_" + span2words[2].lower())    else  "u"
                                        ltri_s2 = span2words[-3].lower() + "_" + span2words[-2].lower() + "_" + span2words[-1].lower() if trigram.has_key(span2words[-3].lower()  + "_" + span2words[-2].lower()  + "_" + span2words[-1].lower())   else  "u"
                                    else:
                                        ftri_s2 = "u"
                                        ltri_s2 = "u"

                                    #Unigram
                                    fpos_s1 = re.sub("_/.*", "", span1tagwords[0])
                                    lpos_s1 = re.sub("_/.*", "", span1tagwords[-1])
                                    fpos_s2 = re.sub("_/.*", "", span2tagwords[0])
                                    lpos_s2 = re.sub("_/.*", "", span2tagwords[-1])

                                    #bigram
                                    if len(span1tagwords) > 1:
                                        fpos_bi_s1 = re.sub("_/.*", "", span1tagwords[0])  + "_" + re.sub("_/.*", "",span1tagwords[1])
                                        lpos_bi_s1 = re.sub("_/.*", "", span1tagwords[-2]) + "_" + re.sub("_/.*", "",span1tagwords[-1])
                                    else:
                                        fpos_bi_s1 = "U_"  + fpos_s1
                                        lpos_bi_s1 = lpos_s1 + "_U"
                        
                                    if len(span2tagwords) > 1:
                                        fpos_bi_s2 = re.sub("_/.*", "", span2tagwords[0])  + "_" + re.sub("_/.*", "", span2tagwords[1])
                                        lpos_bi_s2 = re.sub("_/.*", "", span2tagwords[-2]) + "_" + re.sub("_/.*", "", span2tagwords[-1])
                                    else:
                                        fpos_bi_s2 = "U_" + fpos_s2 
                                        lpos_bi_s2 = lpos_s2 + "_U" 

                                    label = " ".join(map (str, [0, "U"]))

                                    print >>F_W, label + " ---- " + " dr=" + whichspan + " S1ENb=" + str(s1eduNb) + " S2ENb=" + str(s2eduNb) + " hp=" + n_h_pos + " hl=" + n_h_lex.lower() + " ap=" + n_a_pos + " al=" + n_a_lex.lower(),
                                    print >>F_W, "S1en=" + str(span1EduNb) + " S1en2=" + str(span1EduNb2) + " S2en="  + str(span2EduNb)  + " S2en2=" + str(span2EduNb2) + " S1tn=" + str(span1tokNb) + " S1tn2=" + str(span1tokNb2) + " S2tn=" + str(span2tokNb) + " S2tn2=" + str(span2tokNb2) + " S1edB=" + str(span1disEduFrmBeg) + " S1edE=" + str(span1disEduFrmEnd) + " S2edB=" + str(span2disEduFrmBeg) + " S2edE=" + str(span2disEduFrmEnd),
                                    print >>F_W, "fws1=" + fword_s1 + " lws1=" + lword_s1 + " fws2=" + fword_s2 + " lws2=" + lword_s2 + " fbis1=" + fbi_s1 + " lbis1=" + lbi_s1 + " fbis2=" + fbi_s2 + " lbis2=" + lbi_s2 + " ftrs1=" + ftri_s1 + " ltrs1=" + ltri_s1 + " ftrs2=" + ftri_s2 + " ltrs2=" + ltri_s2,
                                    print >>F_W, "fps1="  + fpos_s1  + " lps1=" + lpos_s1  + " fps2=" + fpos_s2  + " lps2=" + lpos_s2  + " fpbis1=" + fpos_bi_s1 + " lpbis1=" + lpos_bi_s1 + " fpbis2=" + fpos_bi_s2 + " lpbis2=" + lpos_bi_s2

                                print >>F_W
                if s == 2:
                    print >>F_W

        span = str(eduIndex + 1) + ":" + str(eduIndex + eduNb)
        spans.append(span)   
        span_text[span] = tokline + " <S>"
        senNb += 1 
        span_sen [span] = senNb
        span_text_ng[span] = "<s> " + tokline + " </s>" if not re.search("\s*<P>$", tokline) else "<s> " + tokline
        span_text_tag[span] = getTaggedText(tagline, tokline, 1, eduNb, edu_tokNb)
        eduIndex += eduNb
        

    F_W.close() #must close here
    F_DOM.close()
    F_TOK.close()
    F_EDU.close()
    F_TAG.close()

    ContFeatures.extract_sent_level_contextual_features("sen_par.feat", "tmp_sen.feat")
    os.unlink("sen_par.feat")

    #doc-level
    ret = findFeaturesForUpperDTs(F_W2, spans, span_text, span_text_ng, unigram_doc, bigram_doc, trigram_doc, span_text_tag, span_sen) 
    F_W2.close()

    if flag == 0:    
        return ("no", ret)
    
    else:
        return ("yes", ret)
    
    
def apply_sent_model(test_f, java_classpath, java_prog):
    """ apply the sent-level model to the test_f """
    
    [F_W, F_W2] = [open('tmp_sen.prob', 'w'), open('tmp_sen.rel', 'w')]
    subprocess.check_call(['java', '-classpath', java_classpath, java_prog, '--testing', test_f, '--model-file', 'dcrf.sen.gz'], stdout=F_W, stderr=F_W2)
    F_W.close()
    F_W2.close()
    

def apply_doc_model(test_f, java_classpath, java_prog):
    """ apply the doc-level model to the test_f """
    
    [F_W, F_W2] = [open('tmp_doc.prob', 'w'), open('tmp_doc.rel', 'w')]
    subprocess.check_call(['java', '-classpath', java_classpath, java_prog, '--testing', test_f, '--model-file', 'dcrf.doc.gz'], stdout=F_W, stderr=F_W2)
    F_W.close()
    F_W2.close()


def do_parse(infile):
    """ this is the main parsing module """

    preprocess(infile) #okay
    (sen, doc) = extract_features()

    java_classpath = 'Tools/grmm/class:Tools/grmm/lib/mallet-deps.jar:Tools/grmm/lib/grmm-deps.jar'    
    java_prog = 'edu.umass.cs.mallet.grmm.learning.AcrfForTestJoty'

    if sen == "yes":
        apply_sent_model("tmp_sen.feat", java_classpath, java_prog)
    if doc == "yes":
        apply_doc_model("tmp_doc.feat", java_classpath, java_prog)

    Parse.parse('parse_sen.rel', 'tmp_sen.prob', "tmp_sen.feat", "tmp_sen.dis", 'parse_doc.rel', 'tmp_doc.prob', "tmp_doc.feat", "tmp_doc.dis", "tmp.edu")


if __name__ == "__main__":
    do_parse(sys.argv[1])
#    do_parse("tmp.edu")
   
