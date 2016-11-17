# extract syntactic features
# written by Shafiq Joty Nov 26, 2011

import re
import subprocess


def extractDomSets(infile1, infile2):
    """ extract dominance sets """

    cmd = "./dependencies"
    outfile  = "tmp.dom" 
    output = subprocess.check_output([cmd, infile1, infile2])      

    if not output:
        print "\n Error!!" + str (output)
        raw_input("handle it")

    else:
        F_W = open(outfile, 'w')
        F_W.write(output)
        F_W.close()
        
def getDomFeatures(domEle, astruct):

    m = re.search("(.*?)\[(.*)\/(.*?)\]<(.*?)\[(.*)\/(.*?)\]", domEle)                                

    if not m:
        print "Error in extracting dom. features.."
        raw_input(' ')
                                        
    m1 = re.search("\((\d+):(\d+),(\d+):(\d+)\)", astruct)
    
    if m.group(1) == m1.group(2) and m.group(4) == m1.group(3):
        whichspan = "2"
                                
    elif m.group(4) == m1.group(2) and m.group(1) == m1.group(3):
        whichspan = "1"
                                
    else:
        print "Error in finding dom. relation"
        raw_input(' ')         

    [n_h_pos, n_a_pos]  = [m.group(3), m.group(6)]
    [n_h_lex, n_a_lex]  = [m.group(2).lower(), m.group(5).lower()]
    
    s1eduNb = int (m1.group(2)) - int (m1.group(1))  + 1
    s2eduNb = int (m1.group(4)) - int (m1.group(2))                            

    return [n_h_pos, n_a_pos, n_h_lex, n_a_lex, whichspan, s1eduNb, s2eduNb]
        

def getRelatedDomSet(astruct, domline):
    """ get the relevant dom. set for the struct from the domline"""

    mg = re.search( "\((.*?)\:(.*?),(.*?)\:(.*?)\)", astruct)

    if mg:
        v1 = mg.group(2)
        v2 = mg.group(3)
    else:
        print "error in struct" + astruct
        raw_input(' ')

    domSet = domline.split()

    for element in domSet:
        m = re.search("(.*?)\{(.*?):(.*?)\}\[(.*)\/(.*?)\]<\[(.*?)\](.*?)\{(.*?):(.*?)\}\[(.*)\/(.*?)\]", element)
        
        if m:
            if (v1 == m.group(1) and v2 == m.group(7) ) or (v1 == m.group(7) and v2 == m.group(1)) :
                domEle = str (m.group(1)) + "[" + str(m.group(4)) + "/" + str(m.group(5)) + "]" + "<" + str(m.group(7)) + "[" + str(m.group(10)) + "/" + str(m.group(11)) + "]"
                return domEle
        
        else:
            print "error in domset format" + element
            raw_input(' ') 
  
