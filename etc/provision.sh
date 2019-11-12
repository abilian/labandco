#!/usr/bin/env bash

#
# Provisionning script for Debian. Must be run as root.
#

set -eo pipefail

# Install needed system packages
apt-get update
apt-get install -y python3-dev python-pip python-virtualenv \
  libpq-dev libffi-dev libldap2-dev libsasl2-dev libxml2-dev libxslt1-dev \
  libjpeg-dev git-core libcairo2-dev libpango1.0-dev \
  libssl-dev libbzip2-dev libsqlite3-dev \
  nodejs default-jdk-headless certbot python3-certbot-nginx \
  poppler-utils redis-server supervisor postgresql nginx node-less

ln -sf /usr/bin/nodejs /usr/local/bin/node

pip install invoke==0.12.2
