#!/usr/bin/perl

# Given a bunch of IP's figure out how fast you can look up their
#   regions and then determine how good we are at this.

use locale;
use DBI;
use Data::Dumper;
use LWP;
use LWP::UserAgent;
use Net::DNS;
use URI;
use URI::Escape;
use Digest::MD5 qw(md5_hex);

# Some config options
my $configfile = 'sentry.cfg';
eval('require "$configfile"');
die "*** Failed to eval() file $configfile:\n$@\n" if ($@);

my $ua = LWP::UserAgent->new;
$ua->timeout(4);
$ua->agent("Mozilla Mirror Monitor/1.1");

my $netres = Net::DNS::Resolver->new();
$netres->tcp_timeout(5);

my %products = (); my %oss = (); my %langs = ();

srand; # seed the random no. generator for random file chunks to be checked

# IP address regex
my $ipregex = qr{^([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])$};

my $dbh = DBI->connect( "DBI:mysql:$db:$host",$user,$pass) or die "Connecting : $dbi::errstr\n";
if (defined($ARGV[0]) and $ARGV[0] eq 'checknow') {
    $location_sql = qq{SELECT * FROM mirror_locations INNER JOIN mirror_products
    ON mirror_locations.product_id = mirror_products.product_id WHERE
    product_active='1' AND product_checknow=1};
} else {
    $location_sql = qq{SELECT * FROM mirror_locations INNER JOIN mirror_products ON mirror_locations.product_id = mirror_products.product_id WHERE product_active='1'};
}
$mirror_sql = qq{SELECT * FROM mirror_mirrors WHERE mirror_active='1' ORDER BY mirror_name};
$update_sql = qq{REPLACE mirror_location_mirror_map SET location_id=?,mirror_id=?,location_active=?};
$failed_mirror_sql = qq{UPDATE mirror_location_mirror_map SET location_active='0' WHERE mirror_id=?};

my $location_sth = $dbh->prepare($location_sql);
my $mirror_sth = $dbh->prepare($mirror_sql);
my $update_sth = $dbh->prepare($update_sql);
my $failed_mirror_sth = $dbh->prepare($failed_mirror_sql);

# populate a product and os hash if we're debugging stuff
# this way we don't have to make too many selects against the DB
if ( $DEBUG ) {
	my $product_sql = qq{SELECT * FROM mirror_products};
	my $oss_sql = qq{SELECT * FROM mirror_os};
	my $lang_sql = qq{SELECT * FROM mirror_langs};

	my $product_sth = $dbh->prepare($product_sql);
	$product_sth->execute();

	while ( my $product = $product_sth->fetchrow_hashref() ) {
		$products{$product->{product_id}} = $product->{product_name};
	}

	$oss_sth = $dbh->prepare($oss_sql);
        $oss_sth->execute();

        while ( my $os = $oss_sth->fetchrow_hashref() ) {
                $oss{$os->{os_id}} = $os->{os_name};
        }

    $lang_sth = $dbh->prepare($lang_sql);
    $lang_sth->execute();
    while ( my $lang = $lang_sth->fetchrow_hashref() ) {
        $langs{$lang->{lang_id}} = $lang->{lang};
    }
}

# let's build the location information
$location_sth->execute();
my @locations = ();

while (my $location = $location_sth->fetchrow_hashref() ) {
	push(@locations, $location);
}

$mirror_sth->execute();

while (my $mirror = $mirror_sth->fetchrow_hashref() ) {
	my $ok = 1;

    # parse domain out of the mirror's base uri
    my $domain = URI->new($mirror->{mirror_baseurl})->authority;

    # test the domain, and mark the mirror as invalid on failure to resolve
    # if the mirror is bad, we should skip to the next mirror and avoid iterating over locations
    #
    # we also only want to check the domain if the host is NOT a straight IP address
    # since for some reason Net::DNS::query still tries to resolve IP addresses (dumb).
    if ($domain !~ m($ipregex) && !$netres->query($domain)) {
        print "DNS resolution for $mirror->{mirror_name} FAILED!  Moving on to next mirror.\n" if $DEBUG;
        $failed_mirror_sth->execute($mirror->{mirror_id});

        # send email to infra
        open(SENDMAIL, "|/usr/sbin/sendmail -t") or die "Cannot open /usr/sbin/sendmail: $!";
        print SENDMAIL "Subject: [bouncer] " . $mirror->{mirror_name} . " (weight: " . $mirror->{mirror_rating} . ") has failed DNS resolution\n";
        print SENDMAIL "To: $email\n";
        print SENDMAIL "Content-type: text/plain\n\n";
        print SENDMAIL "$mirror->{mirror_name} failed DNS resolution.  All files for this mirror will be disabled until the next check.";
        close(SENDMAIL);

        next;
    }

    # test the root of the domain, and mark the mirror as invalid on failure to find anything at root
    # we do not allow simple_request because the root of a mirror could return a redirect
	my $mirrorReq = HTTP::Request->new(HEAD => $mirror->{mirror_baseurl});
    my $mirrorRes = $ua->request($mirrorReq);

    # if the mirror is bad, we should skip to the next mirror and avoid iterating over locations
    if ( $mirrorRes->code >= 500 ) {
        print "$mirror->{mirror_name} sent no response!  Moving on to next mirror.\n" if $DEBUG;
        $failed_mirror_sth->execute($mirror->{mirror_id});

        # send email to infra
        open(SENDMAIL, "|/usr/sbin/sendmail -t") or die "Cannot open /usr/sbin/sendmail: $!";
        print SENDMAIL "Subject: [bouncer] " . $mirror->{mirror_name} . " (weight: " . $mirror->{mirror_rating} . ") is not responding\n";
        print SENDMAIL "To: $email\n";
        print SENDMAIL "Content-type: text/plain\n\n";
        print SENDMAIL "$mirror->{mirror_name} sent no response for its URI: $mirror->{mirror_baseurl}.  All files for this mirror will be disabled until the next check.";
        close(SENDMAIL);

        next;
    } elsif ( $hashcheck && $mirrorRes->header('Accept-Ranges') != 'bytes' ) {
        # hash checking enabled but mirror not capable of it
        print "$mirror->{mirror_name} is not capable of byte range requests!  Moving on to next mirror.\n" if $DEBUG;
        $failed_mirror_sth->execute($mirror->{mirror_id});

        # send email to infra
        open(SENDMAIL, "|/usr/sbin/sendmail -t") or die "Cannot open /usr/sbin/sendmail: $!";
        print SENDMAIL "Subject: [bouncer] " . $mirror->{mirror_name} . " (weight: " . $mirror->{mirror_rating} . ") does not support byte range requests\n";
        print SENDMAIL "To: $email\n";
        print SENDMAIL "Content-type: text/plain\n\n";
        print SENDMAIL "$mirror->{mirror_name} does not support byte range requests: $mirror->{mirror_baseurl}.  File integrity can not be checked.  All files for this mirror will be disabled until the next check.";
        close(SENDMAIL);

        next;

    }

	foreach my $location (@locations) {
        my $loc_ok = '0';

        my $location_uri = $mirror->{mirror_baseurl} . $location->{location_path};
        my $res = HTTP::Response->new();

        if ($hashcheck) {
            # hash check files

            # grab local file copy
            my $localfile = $localdir . uri_unescape($location->{location_path});
            if (!open (FILE, "< $localfile")) {
                print "Couldn't open local file $localfile: $!\n";
                next;
            }
            binmode(FILE);
            my $filesize = -s $localfile;

            # get random chunk from file and MD5-hash it
            my $chunkstart = int(rand($filesize - $chunksize + 1));
            #print "Checking chunk starting with byte $chunkstart...\n";
            seek(FILE, $chunkstart, 0);
            read(FILE, $chunk, $chunksize);
            close(FILE);
            my $localhash = md5_hex($chunk);
            #print "local: $localhash (".length($chunk).")\n";

            # get the same chunk from remote file
            my $rangeheader = HTTP::Headers->new('Range' => "bytes=$chunkstart-".($chunkstart+$chunksize-1));
            my $req = HTTP::Request->new('GET', $location_uri, $rangeheader);
            my $res = $ua->request($req);
            my $remotehash = md5_hex($res->content);
            #print "remote: $remotehash (".$res->content_length.")\n";
            
            if ( $localhash == $remotehash ) {
                print "Hash check on $mirror->{mirror_name} for $products{$location->{product_id}} on $oss{$location->{os_id}} ($langs{$location->{lang_id}}) is okay.\n" if $DEBUG;
                $loc_ok = '1';
            } else {
                print "Hash check on $mirror->{mirror_name} for $products{$location->{product_id}} on $oss{$location->{os_id}} ($langs{$location->{lang_id}}) FAILED.\n" if $DEBUG;
                $loc_ok = '0';
            }

        } else {
            # just check the HTTP response code
            my $req = HTTP::Request->new(HEAD => $location_uri);
            my $res = $ua->simple_request($req);

            if ( $res->code == 200 ) {
                print "$mirror->{mirror_name} for $products{$location->{product_id}} on $oss{$location->{os_id}} ($langs{$location->{lang_id}}) is okay.\n" if $DEBUG;
                $loc_ok = '1';
            } else {
                print "$mirror->{mirror_name} for $products{$location->{product_id}} on $oss{$location->{os_id}} ($langs{$location->{lang_id}}) FAILED.\n" if $DEBUG;
                $loc_ok = '0';
            }
        }

		# content-type == text/plain hack here for Mac dmg's
		if ( ($res->code >= 200) && ($res->code < 300) && ($location->{os_id} == 4) ) {
			print "Testing: $products{$location->{product_id}} on $oss{$location->{os_id}} content-type: " 
                . $res->{_headers}->{'content-type'} . "\n" if $DEBUG;
			if ( $location->{location_path} =~ m/.*\.dmg$/ && $res->{_headers}->{'content-type'} !~ /application\/x-apple-diskimage/ ) {
				print "$mirror->{mirror_name} for $products{$location->{product_id}} on $oss{$location->{os_id}} ($langs{$location->{lang_id}}) FAILED due to content-type mis-match.\n" if $DEBUG;
                $loc_ok = '0';
			}
		}
		
        # mark location as ok or not
        $update_sth->execute($location->{location_id}, $mirror->{mirror_id}, $loc_ok);
	}
}
