#! /bin/sh
# RERANKDATA=ec50-connll-ic-s5
# RERANKDATA=ec50-f050902-lics5
MODELDIR=second-stage/models/ec50spfinal
ESTIMATORNICKNAME=cvlm-l1c10P1
Tools/CharniakParserRerank/first-stage/PARSE/parseIt -l400 -N50 -K Tools/CharniakParserRerank/first-stage/DATA/EN/ $* | Tools/CharniakParserRerank/second-stage/programs/features/best-parses -l Tools/CharniakParserRerank/$MODELDIR/features.gz Tools/CharniakParserRerank/$MODELDIR/$ESTIMATORNICKNAME-weights.gz

