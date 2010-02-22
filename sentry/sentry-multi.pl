#!/usr/bin/perl

# Given a bunch of IP's figure out how fast you can look up their
#   regions and then determine how good we are at this.

use DBI;

my $start_timestamp = time;

my $DEBUG = 1;

# Some db credentials (defaults)
$host = '';
$user = '';
$pass = '';
$db = '';

# number of children to fork at a time
my $num_children = 16;

# load the config
do "sentry.cfg";

my $dbh = DBI->connect( "DBI:mysql:$db:$host",$user,$pass) or die "Connecting : $dbi::errstr\n";
my $checknow = "";
if (defined($ARGV[0]) and $ARGV[0] eq 'checknow') {
    $location_sql = qq{SELECT * FROM mirror_locations INNER JOIN mirror_products
    ON mirror_locations.product_id = mirror_products.id WHERE
    mirror_products.active='1' AND mirror_products.checknow=1};
} else {
    $location_sql = qq{SELECT * FROM mirror_locations INNER JOIN mirror_products ON mirror_locations.product_id = mirror_products.id WHERE mirror_products.active='1'};
}
$mirror_sql = qq{SELECT * FROM mirror_mirrors WHERE active='1' ORDER BY name};

my $location_sth = $dbh->prepare($location_sql);
my $mirror_sth = $dbh->prepare($mirror_sql);

# let's build the location information
$location_sth->execute();
my @locations = ();

while (my $location = $location_sth->fetchrow_hashref() ) {
    push(@locations, $location);
}

$mirror_sth->execute();

# find sentry directory
$0=~/^(.+[\\\/])[^\\\/]+[\\\/]*$/;
$cgidir= $1 || "./";

my $forked_children = 0; # forked children count
while (my $mirror = $mirror_sth->fetchrow_hashref() ) {
    my $pid = fork();
    if ($pid > 0) { # parent
    } elsif ($pid == 0) { # child
        @ARGV = ('checknow', $mirror->{id});
        do "sentry.pl";
        exit 0;
    } else {
        die "couldn't fork: $!\n";
    }
    sleep 1; # wait a second between each spawn so we don't hose the system by spawning all children at once

    # if max. number was reached, wait before forking more children
    if (++$forked_children >= $num_children) {
        waitpid(-1, WNOHANG);
    }
}
