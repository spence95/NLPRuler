#!/usr/bin/perl

use DBI;

open(OUT, ">letters.txt");
open(SXY, ">symptom_year.txt");

##Connect to database
$dsn = "DBI:mysql:database=MFD_MS;host=127.0.0.1;port=3306";

my $dbh = DBI->connect($dsn, davismf, Nh37Kg13) || die "Couldn't connect to DB: " . DBI->errstr; 
my %months = ("Jan"=>1,"Feb"=>2,"Mar"=>3,"Apr"=>4,"May"=>5,"Jun"=>6,"Jul"=>7,"Aug"=>8,"Sep"=>9,"Oct"=>10,"Nov"=>11,"Dec"=>12);
my %numbers = ("zero"=>0,"one"=>1,"two"=>2,"three"=>3,"four"=>4,"five"=>5,"six"=>6,"seven"=>7,"eight"=>8,"nine"=>9,"ten"=>10,"fifteen"=>15,"twenty"=>20,"decade"=>10);


##Make header for output file
print OUT "Grouper\tRUID\tDate\tPhrase_match\tYear\tNote\n";

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
			@note_date = split(/-/,$refhead[3]);
			$firstphrases = $&;
			##also need to include "began" and "started" and "dating back" and "dates back"
			if($firstphrases =~ /.{0,50}(dat(?:e|ing)\s?back|began)(.{0,50})/i)
			{
				$symptomphrase = $&;
				$postphrase =$2;
				print OUT "$refhead[7]\t$refhead[0]\t$refhead[3]\t$1\t";
				if($postphrase =~ /\d{4}/i)
				{
						$onsetyear = $&;
						print OUT "$onsetyear\t$symptomphrase\n";
						print SXY "$refhead[7]\t$refhead[0]\t$refhead[3]\t$onsetyear\n";
				}elsif($postphrase =~ /DATE\[(.{3})/i) #if the physician references just a month for the symptoms, use
				{                                                                                       #use the letter date to determine the year of symptoms
						$monthnoted = $1;
						if(exists $months{$monthnoted})
						{
								$diff = $note_date[1] - $months{$monthnoted};
								if($diff>0)
								{
										print OUT "$note_date[0]\t$symptomphrase\n";
										print SXY "$refhead[7]\t$refhead[0]\t$refhead[3]\t$note_date[0]\n";
								}else{
										print OUT $note_date[0]-1, "\t$symptomphrase\n";
										print SXY "$refhead[7]\t$refhead[0]\t$refhead[3]\t", $note_date[0]-1, "\n";
								}
						}
				}elsif($postphrase =~ /\b(\w+)\s?years?/i)
				{
						if(exists $numbers{$1})
						{
								print OUT $note_date[0]-$numbers{$1}, "\t$symptomphrase\n";
								print SXY "$refhead[7]\t$refhead[0]\t$refhead[3]\t", $note_date[0]-$numbers{$1}, "\n";
						}elsif($1 =~ /\d{1,2}/)
						{
								print OUT $note_date[0]-$&, "\t$symptomphrase\n";
								print SXY "$refhead[7]\t$refhead[0]\t$refhead[3]\t", $note_date[0]-$&, "\n";
						}else{
								print OUT "0\t$symptomphrase\n";
						}
				}elsif($postphrase =~ /\b(\w+)\s?months?/i)
				{
					if(exists $numbers{$1})
					{
						$diff = $note_date[1] - $numbers{$1};
						if($diff>0)
						{
								print OUT "$note_date[0]\t$symptomphrase\n";
								print SXY "$refhead[7]\t$refhead[0]\t$refhead[3]\t$note_date[0]\n";
						}elsif($diff <= 0 && $diff >= -12)
						{
								print OUT $note_date[0]-1, "\t$symptomphrase\n";
								print SXY "$refhead[7]\t$refhead[0]\t$refhead[3]\t", $note_date[0]-1, "\n";
						}elsif($diff < -12 && $diff >= -24)
						{
								print OUT $note_date[0]-2, "\t$symptomphrase\n";
								print SXY "$refhead[7]\t$refhead[0]\t$refhead[3]\t", $note_date[0]-2, "\n";
						}else{
								print OUT "0\t$symptomphrase\n";
						}
					}else
					{
						$diff = $note_date[1] - $1;
						if($diff>0)
						{
								print OUT "$note_date[0]\t$symptomphrase\n";
								print SXY "$refhead[7]\t$refhead[0]\t$refhead[3]\t$note_date[0]\n";
						}elsif($diff <= 0 && $diff >= -12)
						{
								print OUT $note_date[0]-1, "\t$symptomphrase\n";
								print SXY "$refhead[7]\t$refhead[0]\t$refhead[3]\t", $note_date[0]-1, "\n";
						}elsif($diff < -12 && $diff >= -24)
						{
								print OUT $note_date[0]-2, "\t$symptomphrase\n";
								print SXY "$refhead[7]\t$refhead[0]\t$refhead[3]\t", $note_date[0]-2, "\n";
						}else{
								print OUT "0\t$symptomphrase\n";
						}
					}
				}else{
						print OUT "0\t$symptomphrase\n";
				}
			}
		}
    }
}         
