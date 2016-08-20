#!/usr/bin/perl

# Given a bunch of IP's figure out how fast you can look up their
#   regions and then determine how good we are at this.

use locale;
use POSIX;
use DBI;
use Data::Dumper;
use LWP;
use LWP::UserAgent::Determined;
use Net::DNS;
use URI;
use Time::HiRes qw(gettimeofday tv_interval);

BEGIN { $ENV{PERL_LWP_SSL_VERIFY_HOSTNAME} = 0 }

use vars qw( $dbi::errstr );
my $start_timestamp = time;
my %ua_options = ('keep_alive' => 5);
my $ua = LWP::UserAgent::Determined->new(%ua_options);
$ua->timeout(10);
$ua->agent("Mozilla Mirror Monitor/1.0 (@ARGV)");

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
$email = '';

# content types that we need to check
%content_type = ();

# load the config
do "sentry.cfg";

# IP address regex
my $ipregex = qr{^([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])$};

my $output = "";

sub log_this {
  $output .= $_[0];
  print $_[0] if $DEBUG;
}

my $dbh = DBI->connect( "DBI:mysql:$db:$host",$user,$pass) or die "Connecting : $dbi::errstr\n";
if (defined($ARGV[0]) and ($ARGV[0] eq 'checknow' or $ARGV[0] eq 'checkall')) {
    $location_sql = qq{SELECT mirror_locations.* FROM mirror_locations INNER JOIN mirror_products
        ON mirror_locations.product_id = mirror_products.id WHERE
        mirror_products.active='1'};
    if ($ARGV[0] eq 'checknow') {
        $location_sql .= qq{AND mirror_products.checknow=1};
    }

    if (defined($ARGV[1])) {
        if ($ARGV[1] =~ /^\d+$/) {
            $mirror_sql = qq{SELECT * FROM mirror_mirrors WHERE active='1' AND id=$ARGV[1]};
        } else {
            $mirror_sql = qq{SELECT * FROM mirror_mirrors WHERE active='1' AND (baseurl LIKE } . $dbh->quote('%'.$ARGV[1].'%') . qq{ OR name LIKE } . $dbh->quote('%'.$ARGV[1].'%') . ")";
        }
    } else {
        $mirror_sql = qq{SELECT * FROM mirror_mirrors WHERE active='1' ORDER BY name};
    }
} else {
    $location_sql = qq{SELECT mirror_locations.* FROM mirror_locations INNER JOIN mirror_products ON mirror_locations.product_id = mirror_products.id WHERE mirror_products.active='1'};
    $mirror_sql = qq{SELECT * FROM mirror_mirrors WHERE active='1' ORDER BY name};
}
$update_sql = qq{INSERT INTO mirror_location_mirror_map (location_id, mirror_id, active, healthy) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE active=VALUES(active), healthy=VALUES(healthy)};
$failed_mirror_sql = qq{UPDATE mirror_location_mirror_map SET healthy='0' WHERE mirror_id=?};
$log_sql = qq{INSERT INTO sentry_log (log_date, mirror_id, mirror_active, mirror_rating, reason) VALUES (FROM_UNIXTIME(?), ?, ?, ?, ?)};
$getlog_sql = qq{SELECT mirror_rating, mirror_active FROM sentry_log WHERE mirror_id = ? ORDER BY log_date DESC LIMIT 4};
$updatelog_sql = qq{UPDATE sentry_log SET reason=? WHERE log_date=FROM_UNIXTIME(?) AND mirror_id=?};
$updaterating_sql = qq{UPDATE mirror_mirrors SET rating = ? WHERE id = ?};
$logratingchange_sql = qq{INSERT INTO django_admin_log (action_time, user_id, content_type_id, object_id, object_repr, action_flag, change_message) VALUES (NOW(), 32, 16, ?, ?, 2, ?)};

my $location_sth = $dbh->prepare($location_sql);
my $mirror_sth = $dbh->prepare($mirror_sql);
my $update_sth = $dbh->prepare($update_sql);
my $failed_mirror_sth = $dbh->prepare($failed_mirror_sql);
my $log_sth = $dbh->prepare($log_sql);
my $getlog_sth = $dbh->prepare($getlog_sql);
my $updatelog_sth = $dbh->prepare($updatelog_sql);
my $updaterating_sth = $dbh->prepare($updaterating_sql);
my $logratingchange_sth = $dbh->prepare($logratingchange_sql);

# populate a product and os hash if we're debugging stuff
# this way we don't have to make too many selects against the DB
if ( $DEBUG ) {
    my $product_sql = qq{SELECT * FROM mirror_products};
    my $oss_sql = qq{SELECT * FROM mirror_os};

    my $product_sth = $dbh->prepare($product_sql);
    $product_sth->execute();

    while ( my $product = $product_sth->fetchrow_hashref() ) {
        $products{$product->{id}} = $product->{name};
    }

    $oss_sth = $dbh->prepare($oss_sql);
    $oss_sth->execute();

    while ( my $os = $oss_sth->fetchrow_hashref() ) {
        $oss{$os->{id}} = $os->{name};
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
    my $domain = URI->new($mirror->{baseurl})->authority;
    log_this "Checking mirror $domain ...\n";

    # test the domain, and mark the mirror as invalid on failure to resolve
    # if the mirror is bad, we should skip to the next mirror and avoid iterating over locations
    #
    # we also only want to check the domain if the host is NOT a straight IP address
    # since for some reason Net::DNS::query still tries to resolve IP addresses (dumb).
    #
    # Unhealthy, not fatal.
    if ($domain !~ m($ipregex) && !$netres->query($domain)) {
        log_this "DNS resolution for $mirror->{mirror_name} FAILED!  Moving on to next mirror.\n";
        $failed_mirror_sth->execute($mirror->{id});
        $log_sth->execute($start_timestamp, $mirror->{id}, '0', $mirror->{rating}, "DNS failed");

        # send email to infra
#        open(SENDMAIL, "|/usr/sbin/sendmail -t") or die "Cannot open /usr/sbin/sendmail: $!";
#        print SENDMAIL "Subject: [bouncer] (" . $mirror->{id} . ") " . $mirror->{name} . " (weight: " . $mirror->{rating} . ") has failed DNS resolution\n";
#        print SENDMAIL "To: $email\n";
#        print SENDMAIL "Content-type: text/plain\n\n";
#        print SENDMAIL "$mirror->{name} failed DNS resolution.  All files for this mirror will be disabled until the next check.";
#        close(SENDMAIL);

        next;
    }
    else {
        my $answerpacket = $netres->query($domain);
        my @answer = $answerpacket->answer;
        foreach my $line (@answer) {
            if ('A' eq $line->type) {
                #Record IPs we find
                $mirror->{ip} ||= [];
                push @{$mirror->{ip}}, $line->address;
            }
            log_this $line->string . "\n";
        }
    }

    if (exists $mirror->{ip}) {
        my $ip = $mirror->{ip}[0];
        log_this"Using first seen IP: $ip for requests\n";

        my $uri = URI->new($mirror->{baseurl});
        $uri->authority($ip);
        $mirror->{baseurl} = $uri;
        $mirror->{host} = $domain;

        log_this "Making base URL $mirror->{baseurl}\n";
    }

    # test the root of the domain, and mark the mirror as invalid on failure to find anything at root
    # we do not allow simple_request because the root of a mirror could return a redirect
    my $mirrorReq = HTTP::Request->new(HEAD => $mirror->{baseurl});

    # Explicitely set the Host: header if needed (
    if ($mirror->{host}) {
        $mirrorReq->header("Host" => $mirror->{host} );
    }

    my $mirrorRes = $ua->request($mirrorReq);

    # if the mirror is bad, we should skip to the next mirror and avoid iterating over locations
    #
    # Unhealthy, not fatal.
    if ( $mirrorRes->{_rc}>=500 ) {
        if ( $mirrorRes->{_rc} == 500 ) {
            log_this "$mirror->{baseurl} sent no response after " . $ua->timeout() . " seconds!  Checking recent history...\n";
            $failed_mirror_sth->execute($mirror->{id});
            $log_sth->execute($start_timestamp, $mirror->{id}, '0', $mirror->{rating}, "No response");
            $getlog_sth->execute($mirror->{id});
            my ($prevweight, $prevactive) = ($mirror->{rating}, 1);
            my $dropit = 1;
            while (my ($weight, $active) = $getlog_sth->fetchrow_array) {
                log_this "**** weight $weight active $active for $mirror->{baseurl}\n";
                if (($prevweight != $weight) || ($prevactive == $active)) {
                    $dropit = 0;
                }
                $prevweight = $weight;
                $prevactive = $active;
            }
            my $newweight;
            if ($dropit) {
                log_this "**** $mirror->{baseurl} Weight Drop Pattern matched, weight will be dropped 10%\n";
                $newweight = $mirror->{rating} - int($mirror->{rating} * 0.10);
                log_this "**** $mirror->{baseurl} Weight change $mirror->{rating} -> $newweight\n";
                $updaterating_sth->execute($newweight, $mirror->{id});
                $logratingchange_sth->execute($mirror->{id}, $mirror->{name}, "Changed rating to $newweight.");
            } else {
                log_this "Pattern OK, leaving weight unchanged.\n";
            }
        }
        else {
            log_this "$mirror->{baseurl} returned error " . $mirrorRes->{_rc} . ".\n";
            $failed_mirror_sth->execute($mirror->{id});
            $log_sth->execute($start_timestamp, $mirror->{id}, '0', $mirror->{rating}, "Bad response");
        }

        $updatelog_sth->execute($output, $start_timestamp, $mirror->{id});
        # send email to infra
 #       open(SENDMAIL, "|/usr/sbin/sendmail -t") or die "Cannot open /usr/sbin/sendmail: $!";
 #       print SENDMAIL "Subject: [bouncer] (" . $mirror->{id} . ") " . $mirror->{name} . " (weight: " . $mirror->{rating} . ") is not responding";
 #       print SENDMAIL " - weight dropped to $newweight" if $dropit;
 #       print SENDMAIL "\n";
 #       print SENDMAIL "To: $email\n";
 #       print SENDMAIL "Content-type: text/plain\n\n";
 #       print SENDMAIL "$mirror->{name} sent no response for its URI: $mirror->{baseurl}.  All files for this mirror will be disabled until the next check.";
 #       close(SENDMAIL);

        next;
    }

    foreach my $location (@locations) {

        if (($ARGV[0] eq 'checknow') && ((time - $start_timestamp) > 360)) {
            log_this "*** $mirror->{baseurl} took longer than 6 minutes to execute file checks ... assuming host is overloaded and pulling it out.\n";
            $failed_mirror_sth->execute($mirror->{id});
            $log_sth->execute($start_timestamp, $mirror->{id}, '0', $mirror->{rating}, $output);
            exit;
        }
        my $filepath = $location->{path};
        if (($filepath =~ m!/firefox/!)
            && ($filepath !~ m!/namoroka/!)
            && ($filepath !~ m!/devpreview/!)
            && ($filepath !~ m!3\.6b1!)
            && ($filepath !~ m!wince\-arm!)
            && ($filepath !~ m!EUballot!i)
        ) {
            $filepath =~ s@:lang@zh-TW@;
        }
        elsif ($filepath =~ m!/thunderbird/!) {
            if ($filepath =~ m!3\.1a1!) {
                $filepath =~ s@:lang@tr@;
            }
            else {
                $filepath =~ s@:lang@zh-TW@;
            }
        }
        elsif ($filepath =~ m!/seamonkey/!) {
            if (($filepath =~ m!2\.0\.5!) || ($filepath =~ m!2\.0\.6!)) {
                $filepath =~ s@:lang@zh-CN@;
            }
            else {
                $filepath =~ s@:lang@tr@;
            }
        }
        elsif ($filepath =~ m!-euballot/!i) {
            $filepath =~ s@:lang@sv-SE@;
        } else {
            $filepath =~ s@:lang@en-US@g;
        }

        my $req = HTTP::Request->new(HEAD => $mirror->{baseurl} . $filepath);

        # Explicitely set the Host: header if needed (
        if ($mirror->{host}) {
            $req->header("Host" => $mirror->{host} );
        }

        log_this "[" . strftime("%F %T %z", localtime) . "] " . $req->method . " " . $req->uri . " ... ";

        # allow 1 redirect
        $ua->max_redirect(1);

        my $start = [gettimeofday];
        my $res = $ua->request($req);
        my $elapsed = tv_interval($start);

        my $took = " TOOK=$elapsed";

        my $cache = ":miss:";
        if (my $xcache = $res->header('X-Cache')) {
          $cache = lc $xcache;
        }
        $cache = " CACHE=$cache";

        if (( $res->{_rc} == 200 ) && ( $res->{_headers}->{'content-type'} !~ /text\/html/ )) {
            log_this "okay.$cache$took\n";
            $update_sth->execute($location->{id}, $mirror->{id}, '1', '1');
        }
        elsif (( $res->{_rc} == 404 ) || ( $res->{_rc} == 403 )) {
            log_this "FAILED. rc=" . $res->{_rc} . "$cache$took\n";
            $update_sth->execute($location->{id}, $mirror->{id}, '0', '0');
        }
        else {
            log_this "FAILED. rc=" . $res->{_rc} . "$cache$took\n";
            $update_sth->execute($location->{id}, $mirror->{id}, '1', '0');
        }

        # content-type == text/plain hack here for Mac dmg's
    }
    log_this "Finished. Elapsed time: " . (time - $start_timestamp) . ".\n";
    $log_sth->execute($start_timestamp, $mirror->{id}, '1', $mirror->{rating}, $output);
}
