# boto3-aws-natgateway

This script allows for you to grab all the NAT gateway public ips from all regions while using a different IAM role and exports them into a csv. 

This can be adapted to pull more data from across your account as well. If you don't need to assume another role in your account, remove the STS block and boto will use your current AWS config. 
