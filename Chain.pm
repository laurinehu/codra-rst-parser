#!/usr/bin/perl
use warnings;

package lexChain::Chain;
use WordNet::QueryData;

my $wn = WordNet::QueryData->new;
my $ver = $wn->version();




# this method is used by the question processor module. here for lex chain its not used
sub getFirstSynonym{

	my $word=shift;
	#print "for word:$word";
	$word = "$word"."#n#1";
	my @results = $wn->querySense($word,"syns");
	my @synonyms=();
	foreach my $wrd(@results){
		if($wrd =~ m/(\w+)/ && (!($word =~ m/$wrd/i))){
			push @synonyms, $1;
		}
		
	}
	
	return @synonyms;
		
}


1;
