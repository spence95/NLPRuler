#!/usr/bin/perl
use DBI;
open(OUT, ">comb_edss2_032613.txt");
##Connect to database
$dsn = "DBI:mysql:database=MFD_MS;host=127.0.0.1;port=3306";
my $dbh = DBI->connect($dsn, davismf, Nh37Kg13) || die "Couldn't connect to DB: " . DBI->errstr;
 
##Make header for output file
print OUT "Grouper\tRUID\tDate\tStatement\tEDSS\n";
## This just makes a string for the query and stores it in $query
 
$query = "select * from notes where grouper != 5 limit 10000000;";
## This is a fancy way of calling a function to prepare the SQL for a query to the database
$sthead = $dbh->prepare($query);
 
## This actually sends the query to the database and stores the results in the $sthead object
$sthead->execute();
 
while (my @refhead = $sthead->fetchrow_array())
{
        if($refhead[4] =~ /edss/i)
        {
  
        ##substitute all of the extra new lines and tabs for spaces
        $refhead[4] =~ s/\s+|\n+/ /g;

        @rec_lines = split(/(?:\.\s+)|(?:-(?:\s+)?){2,5}|(?:>\s?<)|\\n/, $refhead[4]);
        foreach $line (@rec_lines) 
        {
                if($line  =~ /\bedss\b.{0,50}/i)
                {
                        $phrase = $&;
                        ##Print out the EDSS 
						##Allowed for 's' before score--ie was1.5, is2.0
                        if($phrase =~ /(?:[^A-Za-z]|s)([\d][\d]?(?:\.[\d])?)/i)
                        {
                                if($1 <= 10)
                                {
                                        $score = $1;
                                        ##Print out the note_id, ruid, date, and statement
                                        print OUT "$refhead[7]\t$refhead[0]\t$refhead[3]\t$line\t";
                                        if($score =~ /\./)
                                        {
                                                print OUT "$score\n";
                                        }else
                                        {
                                                print OUT $score . ".0\n";
                                        }
                                }#else
                                #{
                                #               print OUT "-1\n";
                                #}
                        }elsif($phrase =~ /is\s+(zero|one|two|three|four|five|six|seven|eight|nine|ten)/)
                        {
                                ##Print out the note_id, ruid, date, and statement
                                print OUT "$refhead[7]\t$refhead[0]\t$refhead[3]\t$line\t";
                                if($1 eq zero)
                                {
                                        print OUT "0.0\n";
                                }elsif($1 eq one)
                                {
                                        print OUT "1.0\n";
                                }elsif($1 eq two)
                                {
                                        print OUT "2.0\n";
                                }elsif($1 eq three)
                                {
                                        print OUT "3.0\n";
                                }elsif($1 eq four)
                                {
                                        print OUT "4.0\n";
                                }elsif($1 eq five)
                                {
                                        print OUT "5.0\n";
                                }elsif($1 eq six)
                                {
                                        print OUT "6.0\n";
                                }elsif($1 eq seven)
                                {
                                        print OUT "7.0\n";
                                }elsif($1 eq eight)
                                {
                                        print OUT "8.0\n";
                                }elsif($1 eq nine)
                                {
                                        print OUT "9.0\n";
                                }elsif($1 eq ten)
                                {
                                        print OUT "10.0\n";
                                }
                        }#else
                        #{
                        #       print OUT "-1\n";
                        #}

                }
        }
  }
}

close(OUT);
system("cut -f 1,2,3,5 comb_edss2_032613.txt | sort -u > unique_comb_edss_all_032613.txt");

