#!/usr/bin/perl
use DBI;
open(OUT, ">timedwalk_secs_comb032613.txt");
##Connect to database
$dsn = "DBI:mysql:database=MFD_MS;host=127.0.0.1;port=3306";
my $dbh = DBI->connect($dsn, davismf, Nh37Kg13) || die "Couldn't connect to DB: " . DBI->errstr;
 
##Make header for output file
print OUT "Grouper\tRUID\tDate\tStatement\tMinutes\tSeconds\tRefer_to_Previous\tCane\tWalker\tWheelchair\tTotal_Seconds\n";
## This just makes a string for the query and stores it in $query 
$query = "select * from notes where grouper != 5 limit 10000000;";
## This is a fancy way of calling a function to prepare the SQL for a query to the database
$sthead = $dbh->prepare($query); 
## This actually sends the query to the database and stores the results in the $sthead object
$sthead->execute();
while (my @refhead = $sthead->fetchrow_array())
{
 ##Make spaces optional or - 032613
      if($refhead[4] =~ /timed?[\s-]*walk/i || $refhead[4] =~ /25[\s-]*feet/i || $refhead[4] =~ /25[\s-]*foot/i)
     # if ($refhead[4]=~ /(.{0,300}(?:timed?\s+walk|25\sf[oe]{0,2}t).{0,300})/ ) {
#       $text = $1;
#       if ($text =~ /min|sec....
      {
      
        ##substitute all of the extra new lines and tabs for spaces
        $refhead[4] =~ s/\s+|\n+/ /g;
 
        @rec_lines = split(/\.\s+/, $refhead[4]);
        foreach $line (@rec_lines) 
        {
		##Make spaces optional 032613
                if($line  =~ /timed[\s-]*walk/i || $line =~ /25[\s-]*feet/i || $line =~ /25[\s-]*foot/i)
                {
                        $minute = 0;
                        $seconds = 0;

                        ##Print out the note_id, lid, date, and statement
                        print OUT "$refhead[7]\t$refhead[0]\t$refhead[3]\t$line\t";
                        ##Print out a number if minutes are mentioned
                        if($line =~ /([0-9][0-9]?)\s*minute/i)
                        {
                                print OUT "$1\t";
                                $minute = $1;
                        }elsif($line =~ /a\s+minute/i)
                        {
                                print OUT "1\t";
                                $minute = 1;
                        }elsif($line =~ /one\s+minute/i)
                        {
                                print OUT "1\t";
                                $minute = 1;
                        }else
                        {
                                print OUT "0\t";
                                $minute = 0;
                        }
                        ##Print out the seconds or else print 0, also note if there appears to be a statement stating the time is the same as the previous measurement
                        if($line =~ /([0-9][0-9]?.?[0-9]*)\s*sec/i)
                        {
                                print OUT "$1\t-\t";
                                $seconds = $1;
                        }else
                        {
                                print OUT "0\t";
                                $seconds = 0;
                                if($line =~ /same/i || $line =~ /[un|not\s+]changed/i)
                                {
                                        print OUT "1\t";
                                }else
                                {
                                        print OUT "0\t";
                                }
                        }

                        ##Print out if a cane is mentioned in this statement (0 for No, 1 for Yes)
                        if($line =~ /cane/i)
                        {
                                if($line =~ /without [a|the] cane/i)
                                {
                                        print OUT "0\t";
                                }else
                                {
                                        print OUT "1\t";
                                }
                        }else
                        {
                                print OUT "0\t";
                        }
                        ##Print out if a walker is mentioned in this statement (0 for No, 1 for Yes)
                       if($line =~ /walker/i)
                        {
                                print OUT "1\t";
                        }else 
                        {
                                print OUT "0\t";
                        }
                        ##Print out if a wheelchair is mentioned in this statement with a new line at the end (0 for No, 1 for Yes)
                        if($line =~ /wheelchair/i)
                        {
                                print OUT "1\t";
                        }else 
                        {
                                print OUT "0\t";
                        }

                        ##Print out the total number of seconds

                        $total = (60 * $minute) + $seconds;
                        print OUT "$total\n";
                }
        }
      }
###Want to include capitalized letter at the beginning of the sentences.
###Want to remove new lines in the middle of the sentences.
###Want to include a tab between the record number and the statement.
 
}

