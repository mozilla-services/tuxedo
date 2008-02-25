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

my $ua = LWP::UserAgent->new;
$ua->timeout(4);
$ua->agent("Mozilla Mirror Monitor/1.0");

my $netres = Net::DNS::Resolver->new();
$netres->tcp_timeout(5);

my $DEBUG = 1;
my %products = ();
my %oss = ();

# Some db credentials
$host = '';
$user = '';
$pass = '';
$db = $user;

# email address to notify of mirror failures
my $email = '';

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
    if ( $mirrorRes->{_rc}>=500 ) {
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
    }

	foreach my $location (@locations) {

		my $req = HTTP::Request->new(HEAD => $mirror->{mirror_baseurl} . $location->{location_path});
		my $res = $ua->simple_request($req);

		if ( $res->{_rc} == 200 ) {
			print "$mirror->{mirror_name} for $products{$location->{product_id}} on $oss{$location->{os_id}} is okay.\n" if $DEBUG;
			$update_sth->execute($location->{location_id}, $mirror->{mirror_id}, '1');
		}
		else {
			print "$mirror->{mirror_name} for $products{$location->{product_id}} on $oss{$location->{os_id}} FAILED.\n" if $DEBUG;
			$update_sth->execute($location->{location_id}, $mirror->{mirror_id}, '0');
		}

		# content-type == text/plain hack here for Mac dmg's
		if ( ($res->{_rc} == 200) && ($location->{os_id} == 4) ) {
			print "Testing: $products{$location->{product_id}} on $oss{$location->{os_id}} content-type: " .
                $res->{_headers}->{'content-type'} . "\n" if $DEBUG;
			if ( $location->{location_path} =~ m/.*\.dmg$/ && $res->{_headers}->{'content-type'} !~ /application\/x-apple-diskimage/ ) {
				print "$mirror->{mirror_name} for $products{$location->{product_id}} on $oss{$location->{os_id}} FAILED due to content-type mis-match.\n" if $DEBUG;
	            $update_sth->execute($location->{location_id}, $mirror->{mirror_id}, '0');
			}
		}
	}
}
