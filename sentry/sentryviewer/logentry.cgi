#!/usr/bin/perl -wT

use DBI;
use Date::Format;
use Date::Parse;
use CGI;

my $cgi = new CGI;

my $host = "";
my $dbname = "";
my $dbuser = "";
my $dbpass = "";
my $dsn = "dbi:mysql:host=$host;database=$dbname";
my $dbh = DBI->connect($dsn, $dbuser, $dbpass, {});

if (!$cgi->param("id")) {
  print $cgi->redirect("/sentry/");
  exit;
}
if (!$cgi->param("time")) {
  print $cgi->redirect("/sentry/");
  exit;
}

my $id = $cgi->param("id");
my $timestamp = $cgi->param("time");

$::ENV{PATH} = "/usr/bin:/bin"; # for `` from taint mode
my $timezone = `/bin/date +\%Z`;
chomp $timezone;
my $mqh = $dbh->prepare("SELECT mirror_name, mirror_baseurl FROM mirror_mirrors WHERE mirror_id=?");
$mqh->execute($id);
my ($mirror_name, $baseurl) = $mqh->fetchrow_array();
my $qh = $dbh->prepare("SELECT reason FROM sentry_log WHERE mirror_id=? AND check_time=?");
$qh->execute($id, $timestamp);
my ($output) = $qh->fetchrow_array();
if (!$output) {
  print <<EOF;
Content-type: text/plain; charset=utf-8

No log entry found for mirror_id=$id at check_time='$timestamp';
EOF
  exit;
}

$timestamp = time2str("%Y-%m-%d %H:%M:%S",str2time($timestamp." $timezone"),"UTC");
print <<EOF;
Content-type: text/plain; charset=utf-8

Log entry for $mirror_name [$id] ($baseurl) at $timestamp UTC

Note: a FAILED/404 result on a file which is not included in the mozilla-current
      module is okay if you are only rsyncing mozilla-current.

$output
EOF

