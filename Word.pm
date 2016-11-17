		use warnings;
		package Word;


# class definition of Word..........................................

		# members................

		$originalWord="";
		$id=-1;
		$senses=();
		$score=0;
		$finalSense="";
		$finalSenseScore=0;
		$senseScore=();
		$senNb = 0;
		
		#methods' prototypes.................
		
		
		sub new;  			#constructor
		
		sub assingSynsetids;
		sub printInfo;
		sub assignFinalSense;		# assign synsetid of the word
		sub assignRelation;



#methods definitions.........................................................................		

		sub new{
		
			my $class = shift;

		
			my $self = {}; 

			$self->{originalWord} = shift;
			chomp $self->{originalWord};
			$self->{id}    = shift;
			$self->{senNb} = shift;
			
			$self->{score}=0;
			$self->{finalSense} = "";
			bless $self, $class;
		}
		

#.........................................................................................



		sub assignSynsetids{

			my $self = shift;
			my $ids = shift;
			#print "\n@$ids";
			foreach my $id(@$ids){
				$self -> {senses}->{$id} = [];							

			}

		}


#............................................................

		sub assignRelation{
			
			my $self = shift;
			my $synset=shift;
			my $relationType = shift;
			my $score= shift;
			my $destRelation = shift;
			
			push @{$self->{senses}->{$synset}},[$relationType,$score,$destRelation];

		}		


#.......................................................................................

		sub printInfo{

			$self = shift;
			
			print "\n\n\nword:",$self->{originalWord},"\t","id:  ",$self->{id},"\tscore: ",$self->{score},"\n\n";
					
			foreach $sense( keys %{$self->{senses}}){
				print "\nSense:\t",$sense,"\tRelation(s):";
				$temp = @{$self->{senses}->{$sense}}; 
				foreach $i(0..$temp-1){
					print @{$self->{senses}->{$sense}->[$i]};
				}
			}
			print "\n Appropriate Sense:", $self->{finalSense},"\tScore:",$self->{finalSenseScore};
			

			
		}
#........................................................................................
		sub assignFinalSense{

			$self = shift;
			$self -> {finalSense} = shift;
			$self -> {finalSenseScore} = shift;
		}






1;


