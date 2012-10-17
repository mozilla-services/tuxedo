#!/usr/bin/perl -wT

use DBI;

my $host = "";
my $dbname = "";
my $dbuser = "";
my $dbpass = "";
my $dsn = "dbi:mysql:host=$host;database=$dbname";
my $dbh = DBI->connect($dsn, $dbuser, $dbpass, {});
$dbh->do("SET NAMES utf8");

# [ product name, product regexp, throttle warn level, throttle critical level ]
my @productlist = (
  ['Firefox 7.0b3', "^Firefox-7\\.0b3(-|\$)", 15000, 18000],
  ['Firefox 6.0.1', "^Firefox-6\\.0\\.1(-|\$)", 45000, 35000],
  ["Firefox 3.6.21", "^Firefox-3\\.6\\.21(-|\$)", 45000, 35000],
  ["Thunderbird 7.0b3", "^Thunderbird-7\\.0b3(-|\$)", 15000, 18000],
  ["Thunderbird 7.0", "^Thunderbird-7\\.0(-|\$)", 15000, 18000],
  ["Thunderbird 3.1.15", "^Thunderbird-3\\.1\\.15(-|\$)", 30000, 18000],
  ["SeaMonkey 2.3.2", "^Seamonkey-2\\.3\\.2(-|\$)", 30000, 18000],
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

my $regionsquery = "SELECT id, name, priority, throttle FROM geoip_regions ORDER BY name";
my $regionsqh = $dbh->prepare($regionsquery);
$regionsqh->execute();
my $regions = $regionsqh->fetchall_hashref('name');

my $uptakebyregionquery = "SELECT MIN(t.available) from (SELECT 
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
    JOIN geoip_mirror_region_map gmrm ON m.id = gmrm.mirror_id
    WHERE lmm.active = '1' AND m.active = '1'
    AND p.name REGEXP ?
    AND o.name = 'win'
    AND gmrm.region_id = ?
    GROUP BY lmm.location_id) as t";
my $uptakebyregionqh = $dbh->prepare($uptakebyregionquery);

my $weightbyregionquery = "SELECT SUM(m.rating)
    FROM mirror_mirrors m
         JOIN geoip_mirror_region_map gmrm ON m.id = gmrm.mirror_id
    WHERE active = '1' AND gmrm.region_id = ?";
my $weightbyregionqh = $dbh->prepare($weightbyregionquery);

foreach my $region (sort keys %$regions) {
    $weightbyregionqh->execute($regions->{$region}->{'id'});
    my ($weightbyregion) = $weightbyregionqh->fetchrow_array();
    $regions->{$region}->{'activeweight'} = $weightbyregion;
}

use Data::Dumper;
print Data::Dumper->Dump([\@productlist], [qw( productlist )]);
print Data::Dumper->Dump([$regions], [qw( regions )]);

my %uptake = ();
for my $productitem (@productlist) {
  my ($product, $productregexp, $throttlewarn, $throttlecrit) = @$productitem;
  $uptakeqh->execute($productregexp);
  $uptake{$product} = {};
  my ($uptake) = $uptakeqh->fetchrow_array();
  {
      $uptake{$product}->{Global} = $uptake;
  }
  foreach my $region (sort keys %$regions) {
    $uptakebyregionqh->execute($productregexp, $regions->{$region}->{'id'});
    my ($uptakebyregion) = $uptakebyregionqh->fetchrow_array();
    $uptake{$product}->{$region} = $uptakebyregion;
  }
}

print Data::Dumper->Dump([\%uptake], [qw( uptake )]);

