#!/usr/bin/perl

#open(INC,">names.txt");

#for each of the first 160 directories:
$n=1;
while($n<161)
{
	open(OUT, ">pvals/compile_pvals".$n."\.txt");
	#for each of the 1000 files in each directory 7-1006
	for($m=7;$m<1007;$m++)
	{
		#print INC "<set".$n."/summary".$n."\.".$m."up\.txt\n";
		open(IN, "<set".$n."/summary".$n."\.".$m."up\.txt");
		$snp=0;
		while(<IN>)
		{
			chomp;
			$line=$_;
			#print OUT $line."\n";
			if ($line =~ /\"(.{1,50}?)\"/)
			{
				print OUT "$1\t";
			#}else{
			#	print OUT "no_snp\t";
			}

			if($line =~ /\bSNP\b/)
			{
				$snp++;
				@cols = split(/\s+/,$line);
				print OUT "$cols[1]\t$cols[2]\t$cols[3]\n";
			#}else{
			#	print OUT "no_pvals\n";
			}
			if($line =~ /e3/ && $snp <1)
			{
				print OUT "NA\tNA\tNA\n";
			}
		}
		close(IN);
	}
	close(OUT);
	$n++;
}

#for directory 161
$n=161;
open(OUT, ">pvals/compile_pvals".$n."\.txt");
	#for each of the 1000 files in each directory 7-1006
	for($m=7;$m<52;$m++)
	{
		#print INC "<set".$n."/summary".$n."\.".$m."up\.txt\n";
		open(IN, "<set".$n."/summary".$n."\.".$m."up\.txt");
		$snp=0;
		while(<IN>)
		{
			chomp;
			$line=$_;
			#print OUT $line."\n";
			if ($line =~ /\"(.{1,50}?)\"/)
			{
				print OUT "$1\t";
			#}else{
			#	print OUT "no_snp\t";
			}

			if($line =~ /\bSNP\b/)
			{
				$snp++;
				@cols = split(/\s+/,$line);
				print OUT "$cols[1]\t$cols[2]\t$cols[3]\n";
			#}else{
			#	print OUT "no_pvals\n";
			}
			if($line =~ /e3/ && $snp <1)
			{
				print OUT "NA\tNA\tNA\n";
			}
		}
		close(IN);
	}
	close(OUT);
	$n++;