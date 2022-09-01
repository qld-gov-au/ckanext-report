#!/usr/bin/env sh
##
# Initialise CKAN data for testing.
#
set -e

. ${APP_DIR}/bin/activate
CLICK_ARGS="--yes" ckan_cli db clean
ckan_cli db init
ckan_cli db upgrade

# Initialise report tables
PASTER_PLUGIN=ckanext-report ckan_cli report initdb
PASTER_PLUGIN=ckanext-report ckan_cli report generate tagless-datasets

# Create some base test data
. $APP_DIR/bin/create-test-data.sh
