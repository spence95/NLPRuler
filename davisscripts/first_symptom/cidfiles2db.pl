#! /usr/bin/perl -w

# Loads detailedcuis.txt index files into a database


use DBI;
use Getopt::Long;
my ($help, $db);
my $cl_opts = GetOptions("help"=>\$help, "db=s"=>\$db, "dir=s",\$dir);

if ($help || !-e $dir || !$db) {
	show_help();
	exit;
}



my $dbh = DBI->connect ("DBI:mysql:$db", "root", "vger123", { RaiseError => 1 });

my $sth = db_execute($dbh,"SHOW TABLES");
while (my $r=$sth->fetchrow_arrayref()) {
	if ($r->[0]=~/^(concepts(?:_data)?)$/) {
		push @tables, $1;
		$count++;
	}
}
if ($count==0) {
	create_tables();
} elsif ($count==1) {
	print "Table " . $tables[0] . " exists in database '$db' but not the other required db.  Either both 'concepts' and 'concepts_data' tables are required (or neither).  If neither is present, the system will create them.";
	exit;
}





print "Loading files from directory: $dir\nInto database: $db\n";

@files = get_filenames($dir);

for my $f (@files) {
    print "Loading $f...";
    $f =~ /\/?([^\/]+)_qt/;
    $notenum=$1;
    print "$notenum, $f\n";
    open IN, $f;
    my $a = <IN>;
    $a=~/: *(\d+)/;
    my $totalcuis = $1;
    $a = <IN>;
    $a=~/: *(\d+)/;
    my $uniquecuis = $1;
    my ($cui,$cuipn,$styp,$sentnum,$wordnum,$score,$attr, $orig_phrase_text,$section_string);
    my %cui_count;
    my %cui_data;
    while ($a = <IN>) {
        $a =~ s/[\n\r]+$//;
        ($cui,$cuipn,$styp,$sentnum,$wordnum,$score,$attr, $orig_phrase_text,$section_string) = split /\|/,$a;
        next if !$cui;
        
        $cuipn = $dbh->quote($cuipn);
        $styp = $dbh->quote($styp);
        $attr = $dbh->quote($attr);
        $orig_phrase_text = $dbh->quote($orig_phrase_text);
        $section_string = $dbh->quote($section_string);
        @sections = split /<->/,$section_string;
        $cui_count{$cui}++;
        $cui_data{$cui} = "$cui,$cuipn,$styp";
        
        db_execute($dbh, "INSERT INTO concepts_data (notenum,cui,sentnum,wordnum,score,attr,orig_text,section_string)
                   VALUES ($notenum,$cui,$sentnum,$wordnum,$score,$attr,$orig_phrase_text,$section_string)");
        #$cui|$cuiPN|$tty_labels|$sentnum|$wordnum|$score|$attr|$phrase_text|$section
        print '';
    }
    while (my ($cui,$coun) = each %cui_count) {
        db_execute($dbh,"INSERT INTO concepts (cui,cui_pn,sty,count,notecount)
                   VALUES ($cui_data{$cui},$cui_count{$cui},1)
                   ON DUPLICATE KEY UPDATE count=count+$cui_count{$cui}, notecount=notecount+1");    
    }
    print "done.\n";
}






sub show_help {
    print qq{Help
    -db=database to load into (on vger1 - must already exist and have tables created)
    -dir=directory for concept files
    
    example:
    ./cidfiles2db.pl -db=PheWAS -dir=/home/km/DATA/tagged/concept
    };
}


sub get_filenames {
  my $dir = shift;
  my @txtfiles;
  if($dir =~ /\w/) {
    print "Getting files for data directory: $dir\n";
    opendir THISDIR, $dir or die "can't open directory: $dir";
    chdir $dir;
    @txtfiles=grep /\.detailedcuis.txt$/i, readdir THISDIR;
    closedir THISDIR;
    
    @txtfiles = map {$dir .'/'. $_} @txtfiles;
    
    if (($#txtfiles==0)&&($txtfiles[0] eq '')) {
      die "Unable to open files defined by directory \"$dir\" and filenames *.txt.";
    }
  } 
  @txtfiles = sort {rand > .5} @txtfiles;
  return (@txtfiles);
}


sub create_tables {
	
	db_execute($dbh, qq{CREATE TABLE `concepts` (
  `id` int(11) unsigned NOT NULL auto_increment,
  `cui` int(11) unsigned NOT NULL,
  `cui_pn` varchar(256) NOT NULL,
  `sty` varchar(256) NOT NULL,
  `count` int(11) default NULL,
  `notecount` int(11) default NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `cui` (`cui`),
  KEY `cui_pn` (`cui_pn`),
  KEY `sty` (`sty`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;});

	db_execute($dbh, qq{CREATE TABLE `concepts_data` (
  `id` int(11) NOT NULL auto_increment,
  `notenum` int(11) unsigned NOT NULL,
  `cui` int(11) unsigned NOT NULL,
  `sentnum` int(6) unsigned NOT NULL,
  `wordnum` int(5) unsigned NOT NULL,
  `score` float NOT NULL,
  `attr` varchar(256) NOT NULL,
  `orig_text` varchar(256) NOT NULL,
  `section_string` varchar(1000) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `cui` (`cui`),
  KEY `notenum` (`notenum`),
  KEY `orig_text` (`orig_text`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;});

}


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
