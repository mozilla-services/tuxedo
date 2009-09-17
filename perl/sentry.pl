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

use vars qw( $dbi::errstr );
my $start_timestamp = time;
my $ua = LWP::UserAgent->new;
$ua->timeout(5);
$ua->agent("Mozilla Mirror Monitor/1.0");

my $netres = Net::DNS::Resolver->new();
$netres->tcp_timeout(10);

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

my %content_type = (
    dmg => 'application/x-apple-diskimage',
    xpi => 'application/x-xpinstall',
    jar => 'application/x-java-archive',
    mar => 'application/octet-stream',
    msi => 'application/octet-stream',
);

# IP address regex
my $ipregex = qr{^([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])$};

my $output = "";

sub log_this {
  $output .= $_[0];
  print $_[0] if $DEBUG;
}

my $dbh = DBI->connect( "DBI:mysql:$db:$host",$user,$pass) or die "Connecting : $dbi::errstr\n";
if (defined($ARGV[0]) and $ARGV[0] eq 'checknow') {
    $location_sql = qq{SELECT * FROM mirror_locations INNER JOIN mirror_products
    ON mirror_locations.product_id = mirror_products.product_id WHERE
    product_active='1' AND product_checknow=1};
    if (defined($ARGV[1])) {
        if ($ARGV[1] =~ /^\d+$/) {
            $mirror_sql = qq{SELECT * FROM mirror_mirrors WHERE mirror_active='1' AND mirror_id=$ARGV[1]};
        } else {
            $mirror_sql = qq{SELECT * FROM mirror_mirrors WHERE mirror_active='1' AND (mirror_baseurl LIKE } . $dbh->quote('%'.$ARGV[1].'%') . qq{ OR mirror_name LIKE } . $dbh->quote('%'.$ARGV[1].'%') . ")";
        }
    } else {
        $mirror_sql = qq{SELECT * FROM mirror_mirrors WHERE mirror_active='1' ORDER BY mirror_name};
    }
} else {
    $location_sql = qq{SELECT * FROM mirror_locations INNER JOIN mirror_products ON mirror_locations.product_id = mirror_products.product_id WHERE product_active='1'};
    $mirror_sql = qq{SELECT * FROM mirror_mirrors WHERE mirror_active='1' ORDER BY mirror_name};
}
$update_sql = qq{REPLACE mirror_location_mirror_map SET location_id=?,mirror_id=?,location_active=?};
$failed_mirror_sql = qq{UPDATE mirror_location_mirror_map SET location_active='0' WHERE mirror_id=?};
$log_sql = qq{INSERT INTO sentry_log (log_date, mirror_id, mirror_active, mirror_rating, reason) VALUES (FROM_UNIXTIME(?), ?, ?, ?, ?)};
$getlog_sql = qq{SELECT mirror_rating, mirror_active FROM sentry_log WHERE mirror_id = ? ORDER BY log_date DESC LIMIT 4};
$updatelog_sql = qq{UPDATE sentry_log SET reason=? WHERE log_date=FROM_UNIXTIME(?) AND mirror_id=?};
$updaterating_sql = qq{UPDATE mirror_mirrors SET mirror_rating = ? WHERE mirror_id = ?};

my $location_sth = $dbh->prepare($location_sql);
my $mirror_sth = $dbh->prepare($mirror_sql);
my $update_sth = $dbh->prepare($update_sql);
my $failed_mirror_sth = $dbh->prepare($failed_mirror_sql);
my $log_sth = $dbh->prepare($log_sql);
my $getlog_sth = $dbh->prepare($getlog_sql);
my $updatelog_sth = $dbh->prepare($updatelog_sql);
my $updaterating_sth = $dbh->prepare($updaterating_sql);

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
        log_this "DNS resolution for $mirror->{mirror_name} FAILED!  Moving on to next mirror.\n";
        $failed_mirror_sth->execute($mirror->{mirror_id});
        $log_sth->execute($start_timestamp, $mirror->{mirror_id}, '0', $mirror->{mirror_rating}, "DNS failed");

        # send email to infra
#        open(SENDMAIL, "|/usr/sbin/sendmail -t") or die "Cannot open /usr/sbin/sendmail: $!";
#        print SENDMAIL "Subject: [bouncer] (" . $mirror->{mirror_id} . ") " . $mirror->{mirror_name} . " (weight: " . $mirror->{mirror_rating} . ") has failed DNS resolution\n";
#        print SENDMAIL "To: $email\n";
#        print SENDMAIL "Content-type: text/plain\n\n";
#        print SENDMAIL "$mirror->{mirror_name} failed DNS resolution.  All files for this mirror will be disabled until the next check.";
#        close(SENDMAIL);

        next;
    }

    # test the root of the domain, and mark the mirror as invalid on failure to find anything at root
    # we do not allow simple_request because the root of a mirror could return a redirect
	my $mirrorReq = HTTP::Request->new(HEAD => $mirror->{mirror_baseurl});
    my $mirrorRes = $ua->request($mirrorReq);

    # if the mirror is bad, we should skip to the next mirror and avoid iterating over locations
    if ( $mirrorRes->{_rc}>=500 ) {
        if ( $mirrorRes->{_rc} == 500 ) {
            log_this "$mirror->{mirror_baseurl} sent no response after " . $ua->timeout() . " seconds!  Checking recent history...\n";
            $failed_mirror_sth->execute($mirror->{mirror_id});
            $log_sth->execute($start_timestamp, $mirror->{mirror_id}, '0', $mirror->{mirror_rating}, "No response");
            $getlog_sth->execute($mirror->{mirror_id});
            my ($prevweight, $prevactive) = ($mirror->{mirror_rating}, 1);
            my $dropit = 1;
            while (my ($weight, $active) = $getlog_sth->fetchrow_array) {
                log_this "**** weight $weight active $active for $mirror->{mirror_baseurl}\n";
                if (($prevweight != $weight) || ($prevactive == $active)) {
                    $dropit = 0;
                }
                $prevweight = $weight;
                $prevactive = $active;
            }
            my $newweight;
            if ($dropit) {
                log_this "**** $mirror->{mirror_baseurl} Weight Drop Pattern matched, weight will be dropped 10%\n";
                $newweight = $mirror->{mirror_rating} - int($mirror->{mirror_rating} * 0.10);
                log_this "**** $mirror->{mirror_baseurl} Weight change $mirror->{mirror_rating} -> $newweight\n";
                $updaterating_sth->execute($newweight, $mirror->{mirror_id});
            } else {
                log_this "Pattern OK, leaving weight unchanged.\n";
            }
        }
        else {
            log_this "$mirror->{mirror_baseurl} returned error " . $mirrorRes->{_rc} . ".\n";
            $failed_mirror_sth->execute($mirror->{mirror_id});
            $log_sth->execute($start_timestamp, $mirror->{mirror_id}, '0', $mirror->{mirror_rating}, "Bad response");
        }

        $updatelog_sth->execute($output, $start_timestamp, $mirror->{mirror_id});
        # send email to infra
 #       open(SENDMAIL, "|/usr/sbin/sendmail -t") or die "Cannot open /usr/sbin/sendmail: $!";
 #       print SENDMAIL "Subject: [bouncer] (" . $mirror->{mirror_id} . ") " . $mirror->{mirror_name} . " (weight: " . $mirror->{mirror_rating} . ") is not responding";
 #       print SENDMAIL " - weight dropped to $newweight" if $dropit;
 #       print SENDMAIL "\n";
 #       print SENDMAIL "To: $email\n";
 #       print SENDMAIL "Content-type: text/plain\n\n";
 #       print SENDMAIL "$mirror->{mirror_name} sent no response for its URI: $mirror->{mirror_baseurl}.  All files for this mirror will be disabled until the next check.";
 #       close(SENDMAIL);

        next;
    }

	foreach my $location (@locations) {

		my $filepath = $location->{location_path};
                if (($filepath =~ m!/firefox/!) && ($filepath !~ m!/namoroka/!)) {
			$filepath =~ s@/en-US/@/zh-TW/@;
		}
		if ($filepath =~ m!/thunderbird/!) {
			$filepath =~ s@/en-US/@/zh-CN/@;
		}
		log_this "Checking $filepath... ";
		my $req = HTTP::Request->new(HEAD => $mirror->{mirror_baseurl} . $filepath);
		my $res = $ua->simple_request($req);

		if (( $res->{_rc} == 200 ) && ( $res->{_headers}->{'content-type'} !~ /text\/html/ )) {
			log_this "okay.\n";
			$update_sth->execute($location->{location_id}, $mirror->{mirror_id}, '1');
		}
		else {
			log_this "FAILED. rc=" . $res->{_rc} . "\n";
			$update_sth->execute($location->{location_id}, $mirror->{mirror_id}, '0');
		}

		# content-type == text/plain hack here for Mac dmg's
		if ($res->{_rc} == 200) {
                    foreach my $exten (keys %content_type) {
			if ( $location->{location_path} =~ m/.*\.$exten$/ && $res->{_headers}->{'content-type'} !~ /\Q$content_type{$exten}\E/ ) {
				log_this " -> FAILED due to content-type mis-match, expected '$content_type{$exten}', got '$res->{_headers}->{'content-type'}'\n";
	                    $update_sth->execute($location->{location_id}, $mirror->{mirror_id}, '0');
			}
                    }
		}
	}
        $log_sth->execute($start_timestamp, $mirror->{mirror_id}, '1', $mirror->{mirror_rating}, $output);
}
