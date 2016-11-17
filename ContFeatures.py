# extract contextual features
# written by Shafiq Joty Dec 15, 2011

import re

    
def getDifferentFeaturesForUGM(line, fhash):
    
    line = re.sub(".* ----\s+", "", line) 
    features = line.split()
    
    for afeat in features:        
        #tex. org feature
        if re.match("S(1|2)ENb=", afeat) or re.match("S(1|2)(e|t|s|p)n=", afeat) or re.match("sp=", afeat)  or re.match("S(1|2)ed(B|E)=", afeat):
            fhash['to'].append(afeat)

        #ngram features
        else:
            fhash['ng'].append(afeat)

def getFeatureVector(l_feat, pre):
    
    feat = ""
    pre  = " " + pre + "_"            

    for fclass in sorted(l_feat.keys()):
        if fclass == 'to':
            feat += pre
            feat += pre.join(l_feat['to'])
        if fclass == 'ng':
            feat += pre
            feat += pre.join(l_feat['ng'])
    
    return feat


def getDifferentFeatures(line, fhash):
    
    line = re.sub(".* ----\s+", "", line) 
    features = line.split()
    
    for afeat in features:        
        #dom. features
        if re.match("dr=", afeat) or re.match("(h|a)(p|l)=", afeat):    
            fhash['dom'].append(afeat)
        
        #tex. org feature
        elif re.match("S(1|2)ENb=", afeat) or re.match("S(1|2)en2?=", afeat) or re.match("S(1|2)tn2?=", afeat)  or re.match("S(1|2)ed(B|E)=", afeat):
            fhash['to'].append(afeat)
        
        #ngram features
        else:
            fhash['ng'].append(afeat)

def writeContFeatures(F_W, line1, l1_feat, line0, l0_feat, line2, l2_feat):
    
    if not line1:
        print >>F_W
        return
    
    else:
        all_feat = line1
        
        if line0:
            p_feat = ""
            
            for fclass in sorted (l0_feat.keys()):
                if fclass == 'dom':
                    p_feat += " P_"
                    p_feat += " P_".join(l0_feat['dom'])
                            
                if fclass == 'to':
                    p_feat += " P_"
                    p_feat += " P_".join(l0_feat['to'])

                if fclass == 'ng':
                    p_feat += " P_"
                    p_feat += " P_".join(l0_feat['ng'])
            
            all_feat += p_feat        

        if line2:
            n_feat = ""
            
            for fclass in sorted(l2_feat.keys()):
                if fclass == 'dom':
                    n_feat += " N_"
                    n_feat += " N_".join(l2_feat['dom'])
                            
                if fclass == 'to':
                    n_feat += " N_"
                    n_feat += " N_".join(l2_feat['to'])

                if fclass == 'ng':
                    n_feat += " N_"
                    n_feat += " N_".join(l2_feat['ng'])

            all_feat += n_feat        
        print >>F_W, all_feat

def extract_sent_level_contextual_features(fdom_sen, fdomorg_sen):
        
    [F_DOM_sen, F_W]  = [open(fdom_sen, 'r'), open(fdomorg_sen, 'w')]
    [line0, l0_feat] = ["", {'dom':[], 'to':[], 'ng':[]}]

    line1 = F_DOM_sen.readline()               
    line1 = line1.strip()
    l1_feat = {'dom':[], 'to':[], 'ng':[]}
    
    
    if line1:
        getDifferentFeatures(line1, l1_feat)

    while 1:
        line2 = F_DOM_sen.readline()

        if not line2: #end of file
            break
        
        line2 = line2.strip()            
        l2_feat = {'dom':[], 'to':[], 'ng':[]}

        if line2:
            getDifferentFeatures(line2, l2_feat)

        writeContFeatures(F_W, line1, l1_feat, line0, l0_feat, line2, l2_feat)

        line0 = line1
        line1 = line2
        
        l0_feat = dict(l1_feat.items())
        l1_feat = dict(l2_feat.items())

    F_DOM_sen.close()
    F_W.close()
    
