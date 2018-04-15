migrate-ec2-secgroups
=====================

Tool to migrate security groups between EC2 regions

## Configuration

Before running this script you need to set your Amazon credentials in one of the following 3 forms:

* pass as parameters to the script: --key and --secret
* copy the `aws_credentials.cfg.template` to `aws_credentials.cfg` and add your credentials there
* set as environment variables (AWS_KEY and AWS_SECRET)

## Running

The basic command to run this script is:

	python migrate.py origin_region destination_region list_of_groups

Here are some examples:

	python migrate.py us-west-2 eu-west-1 security-group
	python migrate.py us-west-2 eu-west-1 security-group1 security-group2 ...
	python migrate.py --key AAA --secret BBBBBB us-west-2 eu-west-1 security-group1 security-group2 ...

