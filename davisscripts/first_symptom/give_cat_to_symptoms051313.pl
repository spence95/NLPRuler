#!/usr/bin/perl

use DBI;

open(IN, "<./significantonly_matched_concepts_ruid051313.txt");
open(OUT, ">categorized_firstsymptom051313.txt");


##Make header for output file
#051313 remove notenum
print OUT "RUID\tcui_pn\torig_text\torigin\n";

while(<IN>)
{
        chomp;
        @cols = split(/\t/,$_);

        ##Distinguish eye problems between BS and ON
        if($cols[6] =~ /eye\b/ix)
        {
                print OUT "$cols[0]\t$cols[4]\t$cols[6]\tON\n";
        }elsif($cols[4] =~ /optic\sneuritis/ix)
        {
                print OUT "$cols[0]\t$cols[4]\t$cols[6]\tON\n";
        }elsif($cols[4] =~ /vis/i && $cols[6] =~ /loss|
                                                                                                acuity|
                                                                                                diminish|
                                                                                                decreas/xi)
        {
                print OUT "$cols[0]\t$cols[4]\t$cols[6]\tON\n";
        } ##Sort out other BS symptoms
        elsif($cols[4] =~ /speech|
                                                dysphagia|
                                                face|
                                                diplopia|
                                                nystagmus/ix)
        {
                print OUT "$cols[0]\t$cols[4]\t$cols[6]\tBS\n";
        }elsif($cols[6] =~ /fac|
                                                trigeminal\sneuralgia|
                                                tic\sdouloureux|
                                                tremor/ix)
        {
                print OUT "$cols[0]\t$cols[4]\t$cols[6]\tBS\n";
        } ##Distinguish arm complaints between BS and SC
        elsif($cols[6] =~ /arm|
                                                leg/ix)
        {
                if($cols[6] =~ /incoor/ix)
                {
                        print OUT "$cols[0]\t$cols[4]\t$cols[6]\tBS\n";
                }elsif($cols[6] =~ /(weak|
                                                        numb)/ix)
                {
                        print OUT "$cols[0]\t$cols[4]\t$cols[6]\tSC\n";
                }
        } ##Sort out other SC symptoms
        elsif($cols[6] =~ /numb|
                                                tingl|
                                                band|
                                                hug|
                                                lhermitte/ix)
        {
                print OUT "$cols[0]\t$cols[4]\t$cols[6]\tSC\n";
        }elsif($cols[4] =~ /paresth/ix)
        {
                print OUT "$cols[0]\t$cols[4]\t$cols[6]\tSC\n";
        } ##Extract all urinary symptoms into a separate category
        elsif($cols[4] =~ /urin|incontinence|bladder|bowel/ix && $cols[4] !~ /infect/ix)
        {
                print OUT "$cols[0]\t$cols[4]\t$cols[6]\tUR\n";
        } ##Extract all walking/balance difficulties into a separate category
        elsif($cols[4] =~ /walk|
                                                ataxia|
                                                balance|
                                                dizz/ix)
        {
                print OUT "$cols[0]\t$cols[4]\t$cols[6]\tBS\n";
        }elsif($cols[4] =~ /vertigo/ix || $cols[6] =~ /vertigo/ix)
        {
                print OUT "$cols[0]\t$cols[4]\t$cols[6]\tBS\n";
        }
}
close(OUT);

##Create a file to assign origins to final classifications, including polysymptomatic
open(ORI, ">classifications.txt");
##if single symptom, the classification doesn`t change
print ORI "BS\tBS\nSC\tSC\nON\tON\nUR\tUR\n"; 
##if 2 symptoms per an individual, classify as polysymptomatic (PO)
print ORI "BS,SC\tPO\nBS,UR\tPO\nBS,ON\tPO\nON,SC\tPO\nON,UR\tPO\nSC,UR\tPO\n";
##if 3 symptoms classify as PO
print ORI "BS,ON,SC\tPO\nBS,ON,UR\tPO\nBS,SC,UR\tPO\nON,SC,UR\tPO\n";
##if 4 symptoms classify as PO
print ORI "BS,OR,SC,UR\tPO\n";

close(ORI);

##Connect to database
$dsn = "DBI:mysql:database=MFD_MS;host=127.0.0.1;port=3306";
my $dbh = DBI->connect($dsn, davismf, Nh37Kg13) || die "Couldn`t connect to DB: " . DBI->errstr;

db_execute($dbh, qq{drop table `cat_firstsymptom`;});
db_execute($dbh, qq{create table `cat_firstsymptom` (
        `ruid` int, `cui_pn` varchar(100), `orig_text` varchar(100), 
        `origin` varchar(2), INDEX (`ruid`));});
db_execute($dbh, qq{load data local infile 
        'categorized_firstsymptom051313.txt'
        into table `cat_firstsymptom`
        fields terminated by '\t'
        ignore 1 lines 
        (`ruid`, `cui_pn`, `orig_text`, `origin`);});
db_execute($dbh, qq{drop table `classifications`;});
db_execute($dbh, qq{create table `classifications` (
        `origin` varchar(50), `consensus` varchar(2));});
db_execute($dbh, qq{load data local infile 'classifications.txt'
        into table `classifications` 
        fields terminated by '\t';});
db_execute($dbh, qq{drop table `condensed_cat`;});
db_execute($dbh, qq{create table `condensed_cat` select `ruid`, group_concat(
        distinct `origin` order by `origin` separator',')
        as `origin` 
        from `cat_firstsymptom`
        group by `ruid`;});

##Create a file with the mysql command to output the final consensus origins
open(SQL, ">join.sql");
print SQL "select a.ruid, a.origin, b.consensus from condensed_cat a left join classifications b on a.origin=b.origin;\n";
close(SQL);
system("mysql -h 127.0.0.1 -u davismf -pNh37Kg13  MFD_MS < join.sql > final_origins051313.txt");

##Can't load classifications in from VGER1 server--look at how to make it in the MySQL
# db_execute($dbh, qq{drop table `classifications`;});
# db_execute($dbh, qq{create table `classifications`
# (`origin` varchar(10), `consensus` varchar(2));});
# db_execute();


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

