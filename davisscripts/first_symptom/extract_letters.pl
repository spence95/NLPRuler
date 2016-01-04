#!/usr/bin/perl

use DBI;

#open(OUT, ">letters.txt");

##Connect to database
$dsn = "DBI:mysql:database=MFD_MS;host=127.0.0.1;port=3306";

my $dbh = DBI->connect($dsn, davismf, Nh37Kg13) || die "Couldn't connect to DB: " . DBI->errstr; 


##Make header for output file
print OUT "Grouper\tRUID\tDate\tNote_begin\n";

$query = "select * from notes where grouper != 5 and sub_type = 'LETTER' limit 10000000;";
$sthead = $dbh->prepare($query); 
$sthead->execute();

while (my @refhead = $sthead->fetchrow_array())
{
	#how many more useful notes would it capture if "clinic" wasn't required?
    if($refhead[4] =~/multiple\ssclerosis\s/i)
	{
		if($refhead[4] =~ /dear.{0,1000}/i)
		{
			$firstphrases = $&;
			open(OUT, ">$refhead[7]_$refhead[0]_$refhead[3]_kmap.txt");
				#labeled grouper_RUID_dateofnote_kmap.txt
			print OUT "$firstphrases\n";
			close(OUT);
		}
	}
}	