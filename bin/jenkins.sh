#!/bin/bash
set -e

# PHP tests
export FILEPATH="`pwd`/bouncer/php/"
pushd bouncer/php/cfg
cp config-dist.php config.php
sed -i .bak "s%/var/www/download%$FILEPATH%" config.php
popd
pushd bouncer/tests
# FIXME replace w/ phpunit
for f in *.php
do
    php -q $f
done
popd
