#!/usr/bin/perl
use DBI;
open(OUT, ">oligo.txt");
open(OUT2, ">oligo_simplified.txt");
##Connect to database
$dsn = "DBI:mysql:database=MFD_MS;host=127.0.0.1;port=3306";
my $dbh = DBI->connect($dsn, davismf, Nh37Kg13) || die "Couldn't connect to DB: " . DBI->errstr;
 
##Make header for output file
print OUT "Grouper\tRUID\tSub_type\tDate\tStatement\tOligo\n";
#print OUT2 "RUID\tOligo\n";
## This just makes a string for the query and stores it in $query
 
$query = "select * from notes where grouper != 5 and sub_type regexp 'LETTER|CLINIC[[:>:]]|NOTE|NEUROLOGY' limit 10000000;";
 
## This is a fancy way of calling a function to prepare the SQL for a query to the database
$sthead = $dbh->prepare($query);
 
## This actually sends the query to the database and stores the results in the $sthead object
$sthead->execute();
 
while (my @refhead = $sthead->fetchrow_array())
{
        if($refhead[4] =~ /oligo/i)
        {
      
        ##substitute all of the extra new lines and tabs for spaces
        $refhead[4] =~ s/\s+|\n+/ /g;
 
        @rec_lines = split(/(?:\.\s+)|(?:-(?:\s+)?){2,5}|(?:>\s?<)|\\n|<.?B>/, $refhead[4]);
        foreach $line (@rec_lines) 
        {
                if($line  =~ /.{0,100}oligoclonal.{0,100}/i)
                {
						$phrase = $&;
                        ##Print out the grouper number, ruid, date, and statement
                        print OUT "$refhead[7]\t$refhead[0]\t$refhead[2]\t$refhead[3]\t$phrase\t";

						if($phrase =~ /bands?\spending/i)
						{
							print OUT "0\n";
						}elsif($phrase =~ /(?:positive|\bpresent\b)(?:\s)?(?:\b\w{1,20}(?:\b\s)?){0,3}oligoclonal|oligoclonal.{0,15}(?:positive)|in(?:\s)?CSF(?:\s)?only/ix)
						{
							print OUT "2\n";
							print OUT2 "$refhead[0]\tpos\n";
						}elsif($phrase =~ /[1-9]\s?oligo|(?:two|three|four|five|six|seven|eight|nine|ten)\s?oligo|\+(?:\s)?oligo/ix)
						{
							print OUT "2\n";
							print OUT2 "$refhead[0]\tpos\n";
						}elsif($phrase=~ /no(?:\s)?oligo|not(?:\s)?show.{0,20}oligo|negative.{0,20}oligo|band.{0,20}negative|neg\s?oligo|band(?:s?\s?)neg/ix)
						{
							print OUT "1\n";
							print OUT2 "$refhead[0]\tneg\n";
						}else{
							print OUT "0\n";
						}
						
						
						
						
						#/\bnot\b|\bno\b|negative|\bneg\b/i)
						# {
							# print OUT "neg\n";
						# }else{
							# print OUT "0\n";
						# }
						
						 
						
						# if($phrase=~ /positive\s+oligo/i)
						# {
							# print OUT "pos\n";
						# }else{
							# print OUT "0\n";
						# }
						
						
						#Print out if there is a negative qualifier in the phrase
						# if($phrase=~ /\bnot\b|\bno\b|negative|\bneg\b/i)
						# {
							# print OUT "neg\n";
						# }else{
							# print OUT "0\n";
						# }


                }
        }
      }

 
}

close OUT;
close OUT2;

db_execute($dbh, qq{drop table `oligo_results`;});
db_execute($dbh, qq{create table `oligo_results` (`ruid` int, `oligo_result` varchar(3));});
db_execute($dbh, qq{load data local infile 'oligo_simplified.txt' 
	into table `oligo_results`
	fields terminated by '\t';});
db_execute($dbh, qq{drop table `condensed_oligo`;});
db_execute($dbh, qq{create table `condensed_oligo` select `ruid`, group_concat(
	distinct `oligo_result` order by `oligo_result` separator',')
	as `oligo_final`
	from `oligo_results`
	group by `ruid`;});

##Remove individuals who have both positive and negative oligoclonal bands reported
open(SQLfilter, ">rmambig.sql");
print SQLfilter "select * from condensed_oligo where oligo_final != 'neg,pos';";
close(SQLfilter);
system("mysql -h 127.0.0.1 -u davismf -pNh37Kg13 MFD_MS < rmambig.sql > final_oligo.txt");




##subroutine from Josh Denny`s script cidfiles2db.pl
sub db_execute {
    my ($dbh,$query) = @_;
    
    my $sth;
    #print $query;
    eval {$sth = $dbh->prepare ($query); };
    if ($@) {
        print "Error with query prepare: $query.\n";
        die "Error with query prepare: $query.\n";
    }
    
    eval { $sth->execute; };
    if ($@) {
        if (length($query) < 10000) {
		print "Error with query: $query.\n";
       		#warn "Error with query: $query.\n";
	} else {
		print "Error with query: (query suppressed due to length)\n";
        die;
	}
    }
    
    return ($sth);
}