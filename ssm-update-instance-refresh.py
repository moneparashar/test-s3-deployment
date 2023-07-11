import os
import json
import boto3
import logging
from botocore.exceptions import ClientError

# Initializing variables
log_level = os.environ.get('LOG_LEVEL').lower()

# Logger setup
logLevel = {"critical": 50,"error": 40,"warning": 30,"info": 20,"debug": 10,"notset": 0}
logger = logging.getLogger()
logger.setLevel(logLevel[log_level])

# AWS Client
ssm_client = boto3.client('ssm')
sns_client = boto3.client('sns')

SNS = os.environ['SNS_TOPIC_ARN']

API_FOLDER = "api-artifacts"
WORKER_FOLDER = "worker-artifacts"

API_SSM_KEY = "DOTNET_ZIP_API"
WORKER_SSM_KEY = "DOTNET_ZIP_WORKER"

def publish_message(object_key):
    try:
        mail = "Hi,\n\n" + "New Binary uploaded in Folder : " + object_key + "\n\n" + "Please refresh the ELB Instances"
        
        response = sns_client.publish(TopicArn=SNS, Message=mail)
        message_id = response['MessageId']
        
        logger.info( "Published message ! Message ID {} to topic {}".format(message_id, SNS))
        
        return True
    except Exception as e:
        logger.error("Got ERROR while sending release email!")
        raise e
    
def update_ssm(object_loc, zip_name) :
    if API_FOLDER in object_loc :
        try :
            logger.info("Got API event")
            response = ssm_client.put_parameter(
                Name = API_SSM_KEY,
                Value = zip_name,
                Overwrite=True
            )
            logger.info("{} update with value {}".format(API_SSM_KEY, zip_name))
            logger.debug("Response from SSM Put {}".format(json.dumps(response)))
            return True
        except ClientError as e:
            logger.error("Caught Exception "+ str(e))
            raise e
    elif WORKER_FOLDER in object_loc :
        try :
            logger.info("Got Wroker event")
            response = ssm_client.put_parameter(
                Name = WORKER_SSM_KEY,
                Value = zip_name,
                Overwrite=True
            )
            logger.info("{} update with value {}".format(WORKER_SSM_KEY, zip_name))
            logger.debug("Response from SSM Put {}".format(json.dumps(response)))
            return True
        except ClientError as e:
            logger.error("Caught Exception "+ str(e))
            raise e
    else :
        logger.info("Unknow folder event")

        return False

def instance_refresh(event):
    
    # Specify the names of the Auto Scaling groups
    auto_scaling_group1_name = 'Api-1-Scaling-Group'
    auto_scaling_group2_name = 'Api-2-Scaling-Group'
    
    # Create an AutoScaling client
    autoscaling_client = boto3.client('autoscaling')
    
    # Start instance refresh for the first Auto Scaling group
    response1 = autoscaling_client.start_instance_refresh(
        AutoScalingGroupName=auto_scaling_group1_name,
        Strategy='Rolling',
        Preferences={
            'MinHealthyPercentage': 100,
            'InstanceWarmup': 300,
            'SkipMatching': False
        }
    )
    
    # Start instance refresh for the second Auto Scaling group
    response2 = autoscaling_client.start_instance_refresh(
        AutoScalingGroupName=auto_scaling_group2_name,
        Strategy='Rolling',
        Preferences={
            'MinHealthyPercentage': 100,
            'InstanceWarmup': 300,
            'SkipMatching': False
        }
    )
    
    logger.info("Instance refresh started for Auto Scaling group 1")
    logger.info("Instance refresh started for Auto Scaling group 2")
    

def lambda_handler(event, context):
    logger.info("S3 event : {}".format(json.dumps(event)))
    
    isSsmUpdated=False
    for record in event['Records'] :
        object_key = record['s3']['object']['key']
        logger.info("S3 object key : {}".format(object_key))

        build_name = object_key.split("/")[-1]
        logger.info("Build file name : {}".format(build_name))

        status = update_ssm(object_key, build_name)

        publish_message(object_key)

        if status :
            logger.info("SSM is updated")
            isSsmUpdated=True
        else :
            logger.info("SSM not updated")
    if isSsmUpdated:
        instance_refresh(event)