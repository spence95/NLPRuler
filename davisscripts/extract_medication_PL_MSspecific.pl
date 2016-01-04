#!/usr/bin/perl
use DBI;
open(OUT, ">PL_withmeds.txt");

##Connect to database
$dsn = "DBI:mysql:database=MFD_MS;host=127.0.0.1;port=3306";
my $dbh = DBI->connect($dsn, davismf, Nh37Kg13) || die "Couldn't connect to DB: " . DBI->errstr;
 
## This just makes a string for the query and stores it in $query
$query = "select * from notes where doc_type = 'PL' or sub_type regexp 'PROBLEM' and content regexp 'medication' limit 100000000;";
 
## This is a fancy way of calling a function to prepare the SQL for a query to the database
$sthead = $dbh->prepare($query);
 
## This actually sends the query to the database and stores the results in the $sthead object
$sthead->execute();
 
while (my @refhead = $sthead->fetchrow_array())
{
		if($refhead[4] =~ /(?:interferon\sbeta.{0,2}1[ab])|
							avonex|
							rebif|
							betaseron|
							extavia|
							glatiramer\sacetate|
							copaxone|
							fingolimod|
							gilenya|
							natalizumab|
							tysabri|
							mitoxantrone|
							novantrone|
							teriflunomide|
							aubagio/ixg)
		{
			print OUT "$refhead[0]\t$refhead[3]\t\L$&\n"
		}


}
close(OUT);

##Create a file without any full duplicate lines
open(OUT2, ">unique_dates_medications.txt");
print OUT2 "RUID\tDate\tMedication\n";
close(OUT2);
system("sort -u PL_withmeds.txt >> unique_dates_medications.txt");

##Create a file with only the RUIDs and medications, without any duplicates
open(OUT3, ">unique_medications.txt");
print OUT3 "RUID\tMedication\n";
close(OUT3);
system("cut -f 1,3 PL_withmeds.txt | sort -u >> unique_medications.txt");
