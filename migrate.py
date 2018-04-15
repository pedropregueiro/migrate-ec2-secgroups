#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import logging
import argparse
import sys

import boto.ec2
import boto.exception

logging.basicConfig(format='%(asctime)s %(pathname)s:%(lineno)s [%(levelname)s] %(message)s', level=logging.INFO)


def migrate_groups(origin, dest, groups, aws_key, aws_secret):
	from_conn = boto.ec2.connect_to_region(origin, aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)
	to_conn = boto.ec2.connect_to_region(dest, aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)

	# test connections
	try:
		from_conn.describe_account_attributes()
		to_conn.describe_account_attributes()
	except Exception as e:
		logging.error('please make sure that you set your EC2 credentials and that they are correct')
		sys.exit(0)


	from_groups = from_conn.get_all_security_groups()
	to_groups = [ group.name for group in to_conn.get_all_security_groups() ]
	for from_group in from_groups:
		if from_group.name not in groups:
			continue

		if from_group.name in groups:
			logging.warn("security group with name '%s' already exists on region '%s'" % (from_group.name, dest))
			continue

		try:
			from_group.copy_to_region(boto.ec2.get_region(dest))
		except Exception as e:
			logging.error("error trying to migrate group '%s' from '%s' to '%s'" % (from_group.name, origin, dest))
			continue
		logging.info("migrated group '%s' from '%s' to '%s' successfully!" % (from_group.name, origin, dest))


if __name__ == '__main__':

	AWS_KEY = ''
	AWS_SECRET = ''

	parser = argparse.ArgumentParser(description='example: migrate.py us-west-2 eu-west-1 default prod-security ...')
	parser.add_argument('origin', help='EC2 region to export FROM')
	parser.add_argument('dest', help='EC2 region to import TO')
	parser.add_argument('groups', nargs='+', help='EC2 security groups\' names')
	parser.add_argument('--key', nargs='?', help='AWS_KEY')
	parser.add_argument('--secret', nargs='?', help='AWS_SECRET')
	args = parser.parse_args()

	from_region = args.origin
	to_region = args.dest
	groups = args.groups

	# 1st check - command line arguments
	if args.key and args.secret:
		AWS_KEY = args.key
		AWS_SECRET = args.secret

	# 2nd check - aws_credentials.cfg
	if not AWS_KEY or not AWS_SECRET:
		props_dict = {}
		for line in open('aws_credentials.cfg', 'r').readlines():
			line = line.strip()
			prop, value = line.split('=')
			props_dict[prop] = value

		if 'AWS_KEY' in props_dict and 'AWS_SECRET' in props_dict:
			AWS_KEY = props_dict['AWS_KEY']
			AWS_SECRET = props_dict['AWS_SECRET']

	# 3rd check - environment variables
	if not AWS_KEY or not AWS_SECRET:
		if 'AWS_KEY' in os.environ and 'AWS_SECRET' in os.environ:
			AWS_KEY = os.environ['AWS_KEY']
			AWS_SECRET = os.environ['AWS_SECRET']

	migrate_groups(origin=from_region, dest=to_region, groups=groups, aws_key=AWS_KEY, aws_secret=AWS_SECRET)
