import re
import subprocess
#from nltk.stem import WordNetLemmatizer
import nltk
nltk.data.path.append('Tools/nltk_data/')
wnl2 = nltk.stem.WordNetLemmatizer()


def computeLexChains(tagfile):
    """ computes lexical chains """

    chfile_in = re.sub("\.tag", ".ch_in", tagfile)
    chfile_out = re.sub("\.ch_in", ".chn", chfile_in)

    [F_R, F_W] = [open(tagfile, 'r'), open(chfile_in, 'w')]
    senNb = 1

    for tagline in F_R:
        tagline = tagline.strip()
        parts = re.findall(r"\(([^)]+)\)", tagline)
        words = [ wnl2.lemmatize (re.sub("^[^\s]+\s", "", tag_wrd.lower())) for tag_wrd in parts if re.search("^NN", tag_wrd)]
#        words = [ re.sub("^[^\s]+\s", "", tag_wrd.lower()) for tag_wrd in parts if re.search("^NN", tag_wrd)]
        print >>F_W, "Sen: " + str(senNb) + " " + " ". join(words)
        senNb += 1
    
    print >>F_W
    F_R.close()
    F_W.close() 
    
    lex_ch  = "lexChain.pl"
    subprocess.check_output(['perl', lex_ch, chfile_in, chfile_out])
    


def read_chains(chfile, chains):

    """ read the significant chains """
    F_R = open(chfile, 'r')
    
    for line in F_R:
        line = line.strip()
        if not line:
            continue
        line = re.sub("^(Sense|PN):(\s+\d+)?\s+", "", line)
        words = [ re.sub("#n:", "#", w) for w in line.split() ]  #day#n:1 opportunity#n:40 street#n:40
        if len(words) > 1:
            chains.append(words)
    
    F_R.close()


def computeChainFeatures(chains, span1_sen, span2_sen):
    """ compute chain features """

    [ch_nb_span, ch_nb_ex_span, ch_nb_start_left, ch_nb_end_left, ch_nb_start_right, ch_nb_end_right, ch_nb_both_skip, ch_nb_left_skip, ch_nb_right_skip] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        
    for ach in chains:
        ch_start = re.search("#(\d+)$", ach[0])
        ch_end   = re.search("#(\d+)$", ach[-1])
        
        if int(ch_start.group(1)) > span2_sen[1] or int(ch_end.group(1)) < span1_sen[0]:    
            continue

        else:
            if int(ch_start.group(1)) <= span1_sen[1] and int(ch_end.group(1)) >= span2_sen[0]:
                ch_nb_span += 1
                
                [span1_hit, span2_hit]  = [0, 0]
                for wd in ach:
                    dummy  = re.search("#(\d+)$", wd)
                    wd_sen = int (dummy.group(1))
                    
                    if span1_sen[0] <= wd_sen <= span1_sen[1]:
                        span1_hit += 1
                    elif span2_sen[0] <= wd_sen <= span2_sen[1]:
                        span2_hit += 1    
                     
                if span1_hit == span2_hit == 0:
                    ch_nb_both_skip += 1

                if span1_hit == 0:
                    ch_nb_left_skip += 1
                
                if span2_hit == 0:
                    ch_nb_right_skip += 1

            if span1_sen[0] <= int(ch_start.group(1)) <= span1_sen[1] and span2_sen[0] <= int(ch_end.group(1)) <= span2_sen[1]:
                ch_nb_ex_span += 1
            
            if span1_sen[0] <= int(ch_start.group(1)) <= span1_sen[1]:
                ch_nb_start_left += 1

            if span1_sen[0] <= int(ch_end.group(1)) <= span1_sen[1]:
                ch_nb_end_left += 1
                 
            if span2_sen[0] <= int(ch_start.group(1)) <= span2_sen[1]:
                ch_nb_start_right += 1

            if span2_sen[0] <= int(ch_end.group(1)) <= span2_sen[1]:
                ch_nb_end_right += 1

    #continuous
    if ch_nb_span == 0:
        ch_nb_span = 100000 # to avoid divide by zero
        
    ch_feat2 = " ". join([ "ch_c" + str (i) + "=" + str( round ( af / float(ch_nb_span),  2) ) for i, af in enumerate ([ch_nb_ex_span, ch_nb_both_skip, ch_nb_left_skip, ch_nb_right_skip])])         

    ch_nb = len(chains)
    if ch_nb == 0:
        ch_nb = 100000 # to avoid divide by zero

    ch_feat3 = " ". join([ "ch_c" + str (i+4) + "=" + str( round ( af / float(ch_nb), 2) ) for i, af in enumerate ([ch_nb_start_left, ch_nb_end_left, ch_nb_start_right, ch_nb_end_right])])         

    return ch_feat2 + " " + ch_feat3 #only cont