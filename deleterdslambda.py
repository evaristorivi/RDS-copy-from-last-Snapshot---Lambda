
#deleterds-Lambda
#Evaristo R. Rivieccio Vega - evaristo.rivieccio@colex.grupo-sm.com - Operaciones - Grupo SM

"""
Delete all RDS that have the hastag "Backup" and the word "copy" in their instance identifier.
"""

import boto3


client = boto3.client('rds')

def lambda_handler(event, context):
    #AUTO CONFIG
    instances = client.describe_db_instances()
    BackupsInstances=[]   

    for instance in instances["DBInstances"]:
        tags = client.list_tags_for_resource(ResourceName=instance["DBInstanceArn"])
        for tag in tags["TagList"]:
            if tag['Key'] == 'Backup':
                if "copy" in instance["DBInstanceIdentifier"]:
                    BackupsInstances.append(instance["DBInstanceIdentifier"])

        if instance["DBInstanceIdentifier"] in BackupsInstances:
            #The RDS we want the latest Snpashot.
            RDS_TO_DELETE=instance["DBInstanceIdentifier"]
            SKIP_FINAL_SNAPSHOT=True

            #Delete the last RDS copy

            client.describe_db_instances(DBInstanceIdentifier=RDS_TO_DELETE)
            deleteRDS = client.delete_db_instance(
                DBInstanceIdentifier=RDS_TO_DELETE,
                SkipFinalSnapshot=SKIP_FINAL_SNAPSHOT,
                )
            print ("Removing RDS instance: " + RDS_TO_DELETE)

    return {
        'statusCode': 200,
        'body': "RDSs deleted: " + str(BackupsInstances)
    }
