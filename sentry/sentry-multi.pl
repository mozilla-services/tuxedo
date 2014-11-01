#!/usr/bin/perl

use strict;

# Given a bunch of IP's figure out how fast you can look up their
#   regions and then determine how good we are at this.
use DBI;
use POSIX ":sys_wait_h";

my $start_timestamp = time;

my $DEBUG = 1;

# Some db credentials (defaults)
our $host = '';
our $user = '';
our $pass = '';
our $db   = '';

# default number of children to fork at a time
our $num_children = 16;

# load the config
do "sentry.cfg";

my $dbh = DBI->connect( "DBI:mysql:$db:$host", $user, $pass )
  or die "Connecting : $dbi::errstr\n";
my $mirror_sql =
  qq{SELECT * FROM mirror_mirrors WHERE active='1' ORDER BY rating DESC};
my $mirror_sth = $dbh->prepare($mirror_sql);
$mirror_sth->execute();

# find sentry directory
$0 =~ /^(.+[\\\/])[^\\\/]+[\\\/]*$/;
my $cgidir = $1 || "./";

my $forked_children = 0;    # forked children count
while ( my $mirror = $mirror_sth->fetchrow_hashref() ) {
    my $pid = fork();
    if ( $pid > 0 ) {       # parent
    }
    elsif ( $pid == 0 ) {    # child
        if ( $ARGV[0] eq 'checkall' ) {
            @ARGV = ( 'checkall', $mirror->{id} );
        }
        else {
            @ARGV = ( 'checknow', $mirror->{id} );
        }
        do "sentry.pl";
        exit 0;
    }
    else {
        die "couldn't fork: $!\n";
    }

    # if max. number was reached, wait before forking more children
    if ( ++$forked_children >= $num_children ) {
        waitpid( -1, WNOHANG );
    }
}
