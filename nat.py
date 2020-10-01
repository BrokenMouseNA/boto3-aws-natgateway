import boto3
from datetime import datetime
from csv import writer

def get_nateway_ids():

    # Uses STS to assume the role needed. 
    boto_sts=boto3.client('sts')
    sts_response = boto_sts.assume_role(
        # Remove or replace with your Role ARN
        RoleArn='arn:aws:iam::12345:role/foo',
        RoleSessionName='Bar'
    )

    # Save the details from assumed role into vars
    sts_credentials = sts_response["Credentials"]
    session_id = sts_credentials["AccessKeyId"]
    session_key = sts_credentials["SecretAccessKey"]
    session_token = sts_credentials["SessionToken"]

    # List and store all the regions

    # Since AWS sessions are tied to one region, you need to start new sessions in each region.
    # You also have to declare at least one region to start the client in. 
    ec2_client=boto3.client('ec2',aws_access_key_id=session_id,aws_secret_access_key=session_key,aws_session_token=session_token,region_name='us-west-1')
    all_regions=[region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    nat_ips = []
    for region in all_regions:
        max_results = 1000
        next_token = ''
        ec2_client=boto3.client('ec2',aws_access_key_id=session_id,aws_secret_access_key=session_key,aws_session_token=session_token,region_name=region)
        # This variable was initially used to store the session. While not needed now, I kept it in for future use. 
        session=boto3.Session(aws_access_key_id=session_id, aws_secret_access_key=session_key, aws_session_token=session_token, region_name=region)
        while next_token or next_token == '':
            response = ec2_client.describe_nat_gateways(MaxResults=max_results, NextToken=next_token)
            for gateway in response["NatGateways"]:
                for address in gateway["NatGatewayAddresses"]:
                    # We need to make sure the subnet of our public ip is attached due to how we handle filtering
                    nat_ips.append(address["PublicIp"]+'/32')
            next_token = response.get("NextToken", None)

    return nat_ips

# Uploads the data to an s3 bucket if needed
def _s3_upload(filename):
    s3 = boto3.resource('s3')
    bucket = 'foo-bar'
    object_name = 'bar_ips/'
    s3.meta.client.upload_file(Filename=filename,Bucket=bucket,Key=object_name+filename)
    print(f'Uploading {filename} to {bucket}')

# The default output from AWS is kind of a pain to handle.
# This will take the ips without the region name attached and add them into a csv with IPs 
# in seperate rows/lines
def write_list_to_file(filename, data):
    lines_string = '\n'.join(str(x) for x in data)
    with open(filename,'w') as output:
        output.writelines(lines_string)
        print(f'Writing file to {filename}')
        
# Bringing it all together
if __name__ == "__main__":
    date = datetime.now().strftime('%Y%m%d')
    filename = f'natgateway_ips{date}.csv'
    nat_ips = get_nateway_ids()
    print(filename)
    write_list_to_file(filename, nat_ips)
    _s3_upload(filename)