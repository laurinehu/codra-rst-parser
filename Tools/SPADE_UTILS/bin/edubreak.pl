#!/local/bin/perl -w

$output = `Tools/SPADE_UTILS/bin/edubreak $ARGV[0]`;

if( $output eq "" ){
    print STDERR "Error (no ouput): edubreak $ARGV[0]\n" and exit;
}

else{
    print $output;
}



