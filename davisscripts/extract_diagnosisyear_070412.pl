#!/usr/bin/perl



use DBI;

open(OUT, ">diagnoseyear_allSD.txt");
open(RES, ">dxyr_SD.txt");

##Connect to database
$dsn = "DBI:mysql:database=MFD_MS;host=127.0.0.1;port=3306";
my $dbh = DBI->connect($dsn, davismf, Nh37Kg13) || die "Couldn't connect to DB: " . DBI->errstr;

#my %conv = (zero=>0, one=>1, two=>2, three=>3, four=>4, five=>5, six=>6, seven=>7, eight=>8, nine=>9, ten=>10);
#my %months = (Jan=>1,January=>1,);

 
##Make header for output file
print OUT "RUID\tDate\tStatement\tDx_year\tExact\n";

## This just makes a string for the query and stores it in $query
$query = "select * from notes limit 10000000;";


## This is a fancy way of calling a function to prepare the SQL for a query to the database
$sthead = $dbh->prepare($query);

## This actually sends the query to the database and stores the results in the $sthead object
$sthead->execute();


while (my @refhead = $sthead->fetchrow_array())
{
		##Pull out notes that mention diagnosis and multiple sclerosis in any variation
        if($refhead[4] =~ /diagnos(?:e[\sd]|is])/i && $refhead[4] =~ /multiple\ssclerosis|\bms\b/i)
        {     

                ##substitute all of the extra new lines and tabs for spaces
                $refhead[4] =~ s/\s+|\n+/ /g;

				

				##Split the note into sentences or phrases. ---- and >< were common things I found that displayed long lists 
				   ##instead of phrases and made my searching more difficult
                @rec_lines = split(/(?:\.\s+)|(?:-(?:\s+)?)+|(?:>\s?<)|\\n/, $refhead[4]);

                foreach $line (@rec_lines) 
                {
						##Pull out the actual phrase in the note that mentions diagnosis and multiple sclerosis
                        if($line  =~ /diagnos/i && $line =~ /multiple\ssclerosis|\bms\b/i)
                        {
						
							##Pull out 100 characters after diagnosis is mentioned--when I skipped this step
								##I got a lot of random dates that were not what I was looking for
							if($line =~ /diagnos.{1,70}/i) #decrease from 100 to 50 because too many false positives, but then increased to 70 because missing some "years ago" dx times
							{
							
							##phrase after "diagnosis"
							$phrase = $&;
						
							##select out the year of the clinic note
							@note_date = split(/-/,$refhead[3]);

								##Print out the year mentioned in the phrase after diagnosis or else print 0
									##Eventually I will want to ignore phrases that do not mention a year of diagnosis, 
									##but I left this in for now so I can review the statements by hand to see if I 
									##am missing information that I could pull out easily
								##This only pulls out a 4-digit year
								##Include 'XX and X/X/XX formats?								

								##If a four-digit value is found in the phrase after diagnosis, 
									#return it as the year of diagnosis
									#otherwise return 0
								if($phrase =~ /\d{4}/i)
								{
									$dx_yr = $&;
								
									##If the four-digit year is before the date of the clinic note, print it out
										#but if the infered diagnosis date is after the clinic note date,
										#return 0 because that is not possible
									if($dx_yr <= $note_date[0])
									{
									print OUT "$refhead[0]\t$refhead[3]\t$line\t$&\t1\n";
									}#else{
									#print OUT "-1\n";
									#}

								}elsif($phrase =~ /(\d{1,2})\s+years\s+ago/)
								{ 	##if diagnosis is written as "XX years ago" print out the estimated date

									$dx_yr_est = $note_date[0] - $1; # year of the clinic note minus the number of years ago dx was
									print OUT "$refhead[0]\t$refhead[3]\t$line\t$dx_yr_est\t0\n"

								}elsif($phrase =~ /(one|two|three|four|five|six|seven|eight|nine|ten)\s+years\s+ago/)
								{	##if the phrase has a number written out before "years ago", subtract the number
										#from the year the clinic note was written to calculate the estimated dx year

										if (exists $conv{$1}) { ###Exists where????????####
											$dx_yr_est = $note_date[0]-$conv{$1};
										}
										#if (exists $months{$1}) {
										#	$dx_yr_est = ($note_date[1]>$months{$1}) ? $note_date[1]-$months{$1} : $note_date[1]+12-$months{$1};
										#}
										
									print OUT "$refhead[0]\t$refhead[3]\t$line\t$dx_yr_est\t0\n";

									

								}#elsif($phrase =~ /years\s+ago/)
								#{
								#	print OUT "$&\n";

								#}else{
								#		print OUT "0\n";
								#}
							}
                        }
                }
        }
}
close OUT;

open(IN, "<./diagnoseyear_allSD.txt");

while(<IN>)
{
	chomp;
	@cols = split(/\t/,$_);
	if($cols[4] == 1) #$cols[4] is if the reference is exact (1) or relative (0)
	{
		$exact{$cols[0]}{$cols[3]}++; #$cols[0] is the RUID, $cols[3] is the year of diagnosis
				#count up the number of times a year is mentioned exactly for a specific person
	}else
	{
		$relative{$cols[0]}{$cols[3]}++; #$cols[0] is the RUID, $cols[3] is the year of diagnosis
					#count up the number of times a year is mentioned relatively a specific person
	}
}

@RUID_ex = keys %exact; ##these keys are RUIDs
@RUID_rel = keys %relative; ##these keys are RUIDs

foreach $RUID_ex (@RUID_ex)
{
	$yr_tally = 0;
	$top_yr = 0;
	@years_mentioned_exact = keys %{$exact{"$RUID_ex"}}; ##these keys are the dx years
	
	#calculate which year is mentioned the most
	foreach $dx_year (@years_mentioned_exact)
	{
		if($exact{$RUID_ex}{$dx_year} > $yr_tally)
		{
			$top_yr = $dx_year;
			$yr_tally = ($exact{$RUID_ex}{$dx_year});
		}
	}
	
	print RES "$RUID_ex\t$top_yr\t$yr_tally\n";
}

$exact_RUIDs = "@RUID_ex\n";

foreach $RUID_rel (@RUID_rel)
{
	if (($exact_RUID =~ /\s$RUID_rel\s/)) #if the RUID does not have any exact years mentioned, then use the relative year
	{
	}else
	{
		$yr_tally = 0;
		$top_yr = 0;
		@years_mentioned_relative = keys %{$relative{$RUID_rel}};
		
		#calculate which year is mentioned the most
		foreach $dx_year (@years_mentioned_relative)
		{
			if($relative{$RUID_rel}{$dx_year} > $yr_tally)
			{
				$top_yr = $dx_year;
				$yr_tally = $relative{$RUID_rel}{$dx_year};
			}
		}
		
		print RES "$RUID_rel\t$top_yr\t$yr_tally\n";
	}
}

##outputs 10 duplicate RUIDs




#print RES "$exact{$cols[0]}{$cols[3]}\n";

#if () {

#	$dx_date_est{$dx_yr_est}{exact}++
#} else {
#	$dx_date_est{$dx_yr_est}{relative}++="exact" 
#}
	



##Further goals: 

	#Tally how many times each year is recorded for dx per person, then output only the year that is most common. 

	#If there is more than one year reported and each are reported one, do not output a year.


