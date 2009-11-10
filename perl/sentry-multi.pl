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

my $start_timestamp = time;
my $ua = LWP::UserAgent->new;
$ua->timeout(4);
$ua->agent("Mozilla Mirror Monitor/1.0");

my $netres = Net::DNS::Resolver->new();
$netres->tcp_timeout(5);

my $DEBUG = 1;
my %products = ();
my %oss = ();

# Some db credentials (defaults)
$host = '';
$user = '';
$pass = '';
$db = '';

# load the config
do "sentry.cfg";

my $dbh = DBI->connect( "DBI:mysql:$db:$host",$user,$pass) or die "Connecting : $dbi::errstr\n";
my $checknow = "";
if (defined($ARGV[0]) and $ARGV[0] eq 'checknow') {
    $location_sql = qq{SELECT * FROM mirror_locations INNER JOIN mirror_products
    ON mirror_locations.product_id = mirror_products.product_id WHERE
    product_active='1' AND product_checknow=1};
} else {
    $location_sql = qq{SELECT * FROM mirror_locations INNER JOIN mirror_products ON mirror_locations.product_id = mirror_products.product_id WHERE product_active='1'};
}
$mirror_sql = qq{SELECT * FROM mirror_mirrors WHERE mirror_active='1' ORDER BY mirror_name};

my $location_sth = $dbh->prepare($location_sql);
my $mirror_sth = $dbh->prepare($mirror_sql);

# let's build the location information
$location_sth->execute();
my @locations = ();

while (my $location = $location_sth->fetchrow_hashref() ) {
	push(@locations, $location);
}

$mirror_sth->execute();

while (my $mirror = $mirror_sth->fetchrow_hashref() ) {
    system ("/usr/bin/perl -I/data/sentry /data/sentry/sentry.pl checknow " . $mirror->{mirror_id} . " &");
    sleep 1; # wait a second between each spawn so we don't hose the system by spawning 150 at once
}
