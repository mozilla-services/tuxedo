#!/usr/bin/perl -wT

use DBI;
use Date::Format;
use Date::Parse;

my $host = "";
my $dbname = "";
my $dbuser = "";
my $dbpass = "";
my $dsn = "dbi:mysql:host=$host;database=$dbname";
my $dbh = DBI->connect($dsn, $dbuser, $dbpass, {});

# [ product name, product regexp, throttle warn level, throttle critical level ]
my @productlist = (
  ["Firefox 3.5.3", "^Firefox-3\\.5\\.3", 45000, 35000],
  ["Firefox 3.0.14", "^Firefox-3\\.0\\.14", 45000, 35000],
);

my $uptakequery = "SELECT MIN(t.available) from (SELECT 
    SUM( m.rating ) as available,
    (
        SELECT SUM( rating )
        FROM mirror_mirrors
        WHERE active = '1' 
    ) as total,
    (   100 * SUM( m.rating )/
        (
            SELECT SUM( rating )
            FROM mirror_mirrors
            WHERE active = '1' 
        )
    ) as percentage,
    p.name as product_name,
    o.name as os_name
    FROM mirror_mirrors m
    JOIN mirror_location_mirror_map lmm ON lmm.mirror_id = m.id
    JOIN mirror_locations l ON l.id = lmm.location_id
    JOIN mirror_products p ON p.id = l.product_id
    JOIN mirror_os o ON o.id = l.os_id
    WHERE lmm.active = '1' AND m.active = '1'
    AND p.name REGEXP ?
    AND o.name = 'win'
    GROUP BY lmm.location_id) as t";
my $uptakeqh = $dbh->prepare($uptakequery);

my $query = "SELECT FROM_UNIXTIME((UNIX_TIMESTAMP(log_date) - (UNIX_TIMESTAMP(log_date) % 300))) AS log_run,
       check_time,
       mirror_baseurl,
       mirror_name,
       sentry_log.mirror_id,
       sentry_log.mirror_active,
       sentry_log.mirror_rating,
       LEFT(reason,20)
FROM sentry_log
     INNER JOIN mirror_mirrors ON sentry_log.mirror_id = mirror_mirrors.id
WHERE log_date > NOW() - INTERVAL 2 HOUR
ORDER BY log_date DESC";

my $qh = $dbh->prepare("SELECT baseurl, rating FROM mirror_mirrors");
$qh->execute();
my %weight = ();
while (my ($url, $weight) = $qh->fetchrow_array()) {
  $weight{$url} = $weight;
}

my $sth = $dbh->prepare($query);
$sth->execute();

my %byhost = ();
my %seentime = ();
my %totalweight = ();
my %activeweight = ();
while (my ($log_run, $check_time, $baseurl, $mname, $id, $active, $rating, $reason) = $sth->fetchrow_array()) {
  my $record = {
    log_run => $log_run,
    check_time => $check_time,
    baseurl => $baseurl,
    mirror_id => $id,
    mirror_name => $mname,
    active => $active,
    rating => $rating,
    reason => $reason,
  };
  $byhost{$baseurl} ||= {};
  $byhost{$baseurl}->{$log_run} = $record;
  $seentime{$log_run} = 1;
  $totalweight{$log_run} ||= 0;
  $totalweight{$log_run} += $rating;
  $activeweight{$log_run} ||= 0;
  if ($active) {
    $activeweight{$log_run} += $rating;
  }
}

print <<EOF;
Content-type: text/html; charset=utf-8
Refresh: 150;

<html>
<head>
<title>Sentry log overview</title>
<style type="text/css"><!--
table { border: solid black 1px; padding: 0px; }
td { border: solid black 1px; font-family: sans-serif; font-size: xx-small; white-space: nowrap; }
td.active { background-color: #9f9; }
td.inactive { background-color: #f99; }
td.dnsfail { background-color: #99f; }
tr:hover td { border: solid yellow 1px; }
td.good { background-color: #9f9; }
td.ok { background-color: yellow; }
td.poor { background-color: #f99; }
tr.divider { height: 4px; }
tr.divider td { background-color: black; height: 4px; font-size: 1px; }
// --></style>
</head>
<body>
<h3>Sentry check stats for the last 2 hours</h3>
<p>Newest checks are on the left.  Note that the most-recent column is often incomplete if checks are still running.  The number inside the colored square is that server's weight at the time of the check.</p>
<p>
<span style="background-color: #faa">Response timeout or connection failure</span>
<span style="background-color: #aaf">DNS lookup failure</span>
<span style="background-color: #afa">Active and responsive</span>
</p>
<table>
EOF

print "<tr><td>Check time (UTC) :</td>";
$::ENV{PATH} = "/usr/bin:/bin"; # for `` from taint mode
my $timezone = `/bin/date +\%Z`;
chomp $timezone;
#my $timezone = 'PDT';
foreach my $timestamp (reverse sort keys %seentime) {
  print "<td>" . time2str("%H:%M",str2time($timestamp." $timezone"),"UTC") . "</td>";
}

print "<tr><td>Total aggregate weight:</td>";
foreach my $timestamp (reverse sort keys %seentime) {
  print "<td>" . $totalweight{$timestamp} . "</td>";
}
print "</tr>\n<tr><td>Active and available aggregate weight:</td>";
foreach my $timestamp (reverse sort keys %seentime) {
  my $class = "good";
  if ($activeweight{$timestamp} < $productlist[0][2]) { $class = "ok" };
  if ($activeweight{$timestamp} < $productlist[0][3]) { $class = "poor" };
  print qq{<td class="$class" title="$class">} . $activeweight{$timestamp} . "</td>";
}
for my $productitem (@productlist) {
  my ($product, $productregexp, $throttlewarn, $throttlecrit) = @$productitem;
  $uptakeqh->execute($productregexp);
  my ($uptake) = $uptakeqh->fetchrow_array();
  print "</tr>\n<tr><td>$product Uptake ($throttlewarn to stay unthrottled)</td>";
  {
    my $class = "good";
    if ($uptake < $throttlewarn) { $class = "ok" };
    if ($uptake < $throttlecrit) { $class = "poor" };
    print qq{<td class="$class" title="$class">} . $uptake . "</td>";
  }
  my $colcount = scalar(keys %seentime);
  $colcount--;
  print "<td>&nbsp;</td>" x $colcount;
  print "</tr>\n";
}
print qq{</tr>\n<tr class="divider"><td>&nbsp;</td>};
print "<td>&nbsp;</td>" x scalar(keys %seentime);
print "</tr>\n";

foreach my $url (reverse sort { $weight{$a} <=> $weight{$b} } keys %byhost) {
  my @times = keys %{$byhost{$url}};
  print qq{<tr id="mirror_} . $byhost{$url}->{$times[0]}->{mirror_id} . qq{"><td title="} . $byhost{$url}->{$times[0]}->{mirror_name} . " [" . $byhost{$url}->{$times[0]}->{mirror_id} . qq{]">$url</td>};
  foreach my $timestamp (reverse sort keys %seentime) {
    #print qq(<!-- ) . Data::Dumper::Dumper($byhost{$url}) . qq( -->);
    if (exists $byhost{$url}->{$timestamp}) {
      my $class = ($byhost{$url}->{$timestamp}->{"active"} == 1) ? "active" : "inactive";
      my $reason = $byhost{$url}->{$timestamp}->{"reason"} || "Active and responsive";
      my $rating = $byhost{$url}->{$timestamp}->{"rating"};
      if ($byhost{$url}->{$timestamp}->{reason} =~ /DNS/i) { $class = "dnsfail" }
      if ($class eq 'active') {
        $reason = "Click for full report";
      }
      $rating = qq{<a href="logentry.cgi?id=} . $byhost{$url}->{$times[0]}->{mirror_id} . qq{&amp;time=} . $byhost{$url}->{$timestamp}->{check_time} . qq{">$rating</a>};
      print qq{<td class="$class" title="$reason">$rating</td>};
    } else {
      print qq{<td class="nocheck" title="No check recorded">&nbsp;</td>};
    }
  }
  print "</tr>\n";
}

print <<EOF;
</table>
</body>
</html>
EOF
