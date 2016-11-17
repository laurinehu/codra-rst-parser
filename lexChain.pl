#!/usr/bin/perl

use warnings;
use WordNet::QueryData;
use Word;  						

my $infile  = $ARGV[0];
my $outfile = $ARGV[1];


# globals ---- @words and %hashTable
my $wn = WordNet::QueryData->new;
my %synsetGloss = ();
my %proper_noun = ();

#read the nouns from the file and create objects
my $wNb = 0;
readWords("$infile");
findRelation();
buildLexChain();
printChain();


##################  #read the nouns from the source file ##################
sub readWords{

		# Opening a source file..
		my $file = shift;
		open FILE, $file	or die "couldn't open file $file for reading:$!";

		while(<FILE>){
		   my $sen = $_; chomp($sen);
		   my @senNb = ($sen =~ m/^Sen:\s+(\d+)/g); $sen =~ s/^Sen:\s+\d+\s+//gi;

		   #take the nouns
		   my @nouns = split (/ /, $sen);
			
			foreach my $noun (@nouns){ #create an obj for each noun
				
				next if ( ! ($noun =~ /\w+/) );
							
				my $word = $noun."#n";

				$wordObject[$wNb] = new Word($word, $wNb, $senNb[0]);
				my @senses = $wn->querySense($word);
				my @synsetid=();

				foreach my $sense(@senses){
					my $temp = $wn-> offset($sense);
					my @gloss = $wn->querySense($sense,"glos");
					$synsetGloss{$temp} = $gloss[0];
					push @synsetid,$temp;
					buildHash($sense,$temp);				
				}

				$wordObject[$wNb++] -> assignSynsetids(\@synsetid);
				if ( scalar (@synsetid) == 0) {
					push @{$proper_noun{$word}}, $senNb[0];
				}	
			}
		}
#		print "\n ", %proper_noun;
#		my $wt = <STDIN>;
		close FILE;
}

#########################################################################
#############################build the hash #################################

	sub buildHash{
		my $word = shift;
		my $id = shift;

			if (!exists $hashTable{$id}){
				 $hashTable{$id} = {$word => 1};
			}
			else{
				$hashTable{$id}->{$word}++;
			
			}
		
	}


############################################################################
#########...........printing the word objects..........................

	sub printWords{
		foreach $i(0..$#wordObject){
			$wordObject[$i]->printInfo();
		}			
	}

##########################################################################
#..........finding relation in the wordNet.................................


	sub findRelation{
		#print "\nFinding the relations:::::::::::";
		foreach my $i(keys %hashTable){
			
			#1. repitition
			getRepitition($i);

			#2.Synonym
			getSynonym($i);
			
			#3.Hypernym or Hyponym
			
			my @temp = keys %{$hashTable{$i}}; 
			getHyp($temp[0]);

			#4. Gloss  including it needs longer time........
			#getGloss($i);
			
		}
		#print "\nfinding relations is completed";
	}
	
##########################################################################
	# get gloss relation
##########################################################################

sub getGloss{
	my $synsetid = shift;
#	print "\nFor synset id: $synsetid";

	#get the gloss definition for this synset
	my $gloss = $synsetGloss{$synsetid};
	
	foreach my $i(0..$#wordObject){
		my $tmp =$wordObject[$i]->{originalWord}; 
		$tmp =~ s/(\w+)#n/$1/;
		my @ids = keys %{$wordObject[$i]->{senses}};
		if($gloss =~ /$tmp/ && !(isExist($synsetid,\@ids))){
		
			my @k = keys %{$hashTable{$synsetid}}; 
			#get the synsetids of the word
			setGloss(\@k,$synsetid,\@ids);
			foreach my $id(@ids){
				$wordObject[$i]->{score} += 0.33;
				$wordObject[$i]->assignRelation($id,'g',0.33,$synsetid);
			
			} #end of for
			
		} #end of if	
	}#end of for
	
}

################............................................................
sub isExist{
	my $targetid = shift;
	my $list = shift;
	
	foreach my $ele(@$list){
		if($ele == $targetid){
			return 1;
		}
	}

	return 0;

}

#############...............................................................
sub setGloss{

	my $words = shift;
	my $synset = shift;
	my $ids = shift;

	foreach my $wr(@$words){
		foreach my $i(0..$#wordObject){
			my $tmp =$wordObject[$i]->{originalWord}; 
			$tmp =~ s/(\w+)#n/$1/;
		
			if($wr =~ m/$tmp/){
				foreach my $id(@$ids){
					$wordObject[$i]->{score} += 0.33;					
					$wordObject[$i]->assignRelation($synset,'g',0.33,$id);
			
				}
			}	
		}

	}


}
############...............................................................


#................................................................................................
		        #HYPERNYM AND HYPONYM COUNT
#................................................................................................

	sub getHyp{
		#synset word....		
		my $synset=shift;
		
		my ($hyperset,$hyposet) = getHyperset($synset);
		
		
		if((my $length = @$hyperset) != 0){
			
			foreach my $sense(@$hyperset){
				if(exists $hashTable{$sense}){
					my $synsetid = $wn->offset($synset,"syns");
				setHyperRelation($synsetid,$sense,0);	
				}
			}
		}
		
		if((my $length = @$hyposet) != 0){
			foreach my $sense(@$hyposet){
				if(exists $hashTable{$sense}){
					my $synsetid = $wn->offset($synset,"syns");
					setHyperRelation($synsetid,$sense,1);	
				}
			}
		}	
	}


#......................................................................	
	sub setHyperRelation{

		my $synset = shift;
		my $dest=shift;
		my $flag= shift;
		foreach $i(0..$#wordObject){
			if (exists ${$wordObject[$i]->{senses}}{$synset}){
				$wordObject[$i]->{score} += 0.5;
				$wordObject[$i]->assignRelation($synset,'hyper',0.5,$dest) if ($flag == 0);
				$wordObject[$i]->assignRelation($synset,'hypon',0.5,$dest) if ($flag == 1);
								
			}

	 	}		
	}	

#............................................................................
	sub getHyperset{
		my $synset = shift;
		my @value1=();
		my @value2=();
		my @senses = $wn->querySense($synset,"hype");


		foreach my $sense(@senses){
			push @value1,$wn->offset($sense);
		}
		

		@senses = $wn->querySense($synset,"hypo");

			
		foreach my $sense(@senses){
			push @value2,$wn->offset($sense);
		}
		
		return (\@value1,\@value2);
	}
########################################################################
		#Synonym Count
########################################################################

	sub getSynonym{

		my $synset=shift;

		my @words = keys %{$hashTable{$synset}};
			
		my $value = 0;
		foreach my $word(@words){
			$value += $hashTable{$synset}->{$word};

		}
	
		my $wordNo = @words;
		if ($wordNo > 1){
			
			foreach my $i(0..$#wordObject){
						
				if (exists ${$wordObject[$i]->{senses}}{$synset}){
					
					$wordObject[$i]->{score} += $wordNo-1;
					my @k = keys %{$hashTable{$synset}}; 
					my $k="";
					foreach $k(@k){
							my $tmp =$wordObject[$i]->{originalWord}; 
							if($k =~ /$tmp#\d+/){
								$v = $k;
								last;
							}
					 }
					
					my $temp = $hashTable{$synset}->{$v};
					$wordObject[$i]->assignRelation($synset,'s',$value-$temp,$synset);
				}


	 		}	
		}				
	

	}
##########################################################################
			#REPITITION COUNT
#####################.repitition.#########################################

	sub getRepitition{

		my $synset=shift;
		foreach $word(keys %{$hashTable{$synset}}){
			#repition.........
		
			if( (my $temp= ($hashTable{$synset}->{$word}) ) > 1){
				setRepititionScore($word,$temp,$synset);
			}
			
		}
	}


	sub setRepititionScore{

		my $word=shift;
		my $times=shift;
		my $synset=shift;

		foreach $i(0..$#wordObject){
			my  $temp = $wordObject[$i]->{originalWord};
			if($word =~ /$temp#\d+/){
				$wordObject[$i]->{score} += $times-1;
				$wordObject[$i]->assignRelation($synset,'r',$times-1,$synset);			
			}
	 	}

	}

#######################################################################
			#### BUILD THE CHIANS
########################################################################

sub buildLexChain{

	%lexChain = ();
	%lexChain_sen = ();

	foreach my $i(0..$#wordObject){

				
		my $max=0;
		my @tempVar=keys %{$wordObject[$i]->{senses}};
		my $maxSense=$tempVar[0];

		#finding out the maximum sense..............................
		my $len = @tempVar;
		
		if($len >0){
			foreach my $sense(@tempVar){
				my $score=0;
				my $temp = @{$wordObject[$i]->{senses}->{$sense}};
				 
				foreach my $k(0..$temp-1){
					$score += $wordObject[$i]->{senses}->{$sense}->[$k][1];
				}
		
				if($max < $score){
					$max=$score;
					$maxSense=$sense;
				}			
				$wordObject[$i]->{senseScore}={$sense=>$score};		
			}
		
		$wordObject[$i]->assignFinalSense($maxSense,$max);

		if(exists $lexChain{$maxSense}){
			if (!($lexChain{$maxSense}->[0] =~ /^\d\d*\d$/)) {
				push @{$lexChain{$maxSense}},$wordObject[$i]->{originalWord};
				push @{$lexChain_sen{$maxSense}},$wordObject[$i]->{senNb};
			}

			else{

				my $t = $lexChain{$maxSense}->[0];
				push @{$lexChain{$t}},$wordObject[$i]->{originalWord};
				push @{$lexChain_sen{$t}},$wordObject[$i]->{senNb};
			}
		}
	
		else{
			my $flag=0;
			my $size = @{$wordObject[$i]->{senses}->{$maxSense}};

			foreach my $j(0..$size-1){	
				
				my $temp = $wordObject[$i]->{senses}->{$maxSense}->[$j][2];
				if(exists $lexChain{$temp}){
					
					if(!($lexChain{$temp}->[0] =~ /^\d\d*\d$/)){
				
						push  @{$lexChain{$temp}},$wordObject[$i]->{originalWord};
						push  @{$lexChain_sen{$temp}},$wordObject[$i]->{senNb};
						push @{$lexChain{$maxSense}},$temp; #putting sense?

						$flag=1;
						last;
					}
				 					
					else
					{
						my $t = $lexChain{$temp}->[0];
						push @{$lexChain{$t}},$wordObject[$i]->{originalWord};
						push @{$lexChain_sen{$t}},$wordObject[$i]->{senNb};

						push @{$lexChain{$maxSense}},$t; #why putting sense?
						$flag = 1;
						last;
					}
				}
								
			}
			
		   if($flag == 0){
					$lexChain{$maxSense}=[];

					push @{$lexChain{$maxSense}},$wordObject[$i]->{originalWord};
					push @{$lexChain_sen{$maxSense}},$wordObject[$i]->{senNb};
			}
		
	    }			
	  }	

	}
}
#############################################################################
	#PRINT THE CHAINS AND STORE IT IN A FILE
#############################################################################
sub printChain{

	open FW, ">$outfile" or die "couldn't open file for writing:$!";
	foreach my $key (keys %lexChain){

		my @tmp = @{$lexChain{$key}};
		
		if(!($tmp[0] =~ /^\d\d*\d$/)){
			my @tmp2 = @{$lexChain_sen{$key}};
			my @line = map { "$tmp[$_]:$tmp2[$_]"} 0 .. $#tmp;
			print FW "\nSense: $key\t ","@line";
		} 
	}
	
	#print the proper nouns
	foreach my $pn (keys %proper_noun){
		my @line = map { "$pn:$_" } @{$proper_noun{$pn}};
#		print "@line";
		print FW "\nPN:\t ","@line";
	}
	close FW;
}
#############################################################################
		#SORT THE CHIANS TO GET TOP CHAINS
##############################################################################
sub sortLexChains{

	my $noOflexChain=shift;
	my %sortHash=();
	foreach my $key (keys %lexChain){		
			my @tmp = @{$lexChain{$key}};
			if(!($tmp[0] =~ /\d+/)){
				$sortHash{$key}=@{$lexChain{$key}}; 
			} 


	}

	# get top no of lexChain members
	my $count=0;
	my @topLexChains=();
	foreach my $key (sort {$sortHash{$b} <=> $sortHash{$a}} keys %sortHash){
		if($count < $noOflexChain){
			print "\n $key => @{$lexChain{$key}}";
			push @topLexChains, $lexChain{$key}; 
			$count++;
		}
	} 
	return @topLexChains;

}	

#############################################################################
