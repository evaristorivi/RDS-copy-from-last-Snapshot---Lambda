
#createRDS_FROM_SNAPSHOT-Lambda
#Evaristo R. Rivieccio Vega

"""
Specifier: Lambda that creates copies of each RDS that has the tag "Backup". The copies are generated with the last snpashot created.
"""

import boto3

client = boto3.client('rds')

def handler(event, context):
    #AUTO CONFIG
    instances = client.describe_db_instances()
    BackupsInstances=[]   

    for instance in instances["DBInstances"]:
        tags = client.list_tags_for_resource(ResourceName=instance["DBInstanceArn"])
        for tag in tags["TagList"]:
            if tag['Key'] == 'Backup':
                BackupsInstances.append(instance["DBInstanceIdentifier"])

        if instance["DBInstanceIdentifier"] in BackupsInstances:
            #The RDS we want the latest Snpashot.
            RDS_FROM_SNAPSHOT=instance["DBInstanceIdentifier"]
            #Name of the new RDS to be generated.
            NEW_RDS_DB_INSTANCE_INDENTIFIER=instance["DBInstanceIdentifier"] + "-copy"
            #Size of RDS
            DB_CLUSTER_INSTANCE_CLASS=instance["DBInstanceClass"]
            #Other configurations:
            PORT=instance["Endpoint"]["Port"]
            DB_SUBNET_GROUP_NAME=instance["DBSubnetGroup"]["DBSubnetGroupName"]
            VPC_SECURITY_GROUP_IDS=[]
            for groupsids in instance["VpcSecurityGroups"]:
                VPC_SECURITY_GROUP_IDS.append(groupsids["VpcSecurityGroupId"])
            DB_PARAMETER_GROUP_NAME=instance["DBParameterGroups"][0]["DBParameterGroupName"]
            ENABLE_IAM_DATABASE_AUTHENTICATION=instance["IAMDatabaseAuthenticationEnabled"]
            AUTO_MINOR_VERSION_UPGRADE=instance["AutoMinorVersionUpgrade"]
            PUBLICLY_ACCESSIBLE=instance["PubliclyAccessible"]

            #Get the latest snpashot

            #Gets the snapshots
            SNAPSHOT_SELECTION=client.describe_db_snapshots(DBInstanceIdentifier=RDS_FROM_SNAPSHOT)

            #Get the latest snapchot
            LAST_SNAPCHOT=SNAPSHOT_SELECTION["DBSnapshots"][-1]["DBSnapshotIdentifier"]
            print ("The latest snapshot is " + LAST_SNAPCHOT)

            #Restore RDS from Snapchot
            print ("Restoring RDS " + NEW_RDS_DB_INSTANCE_INDENTIFIER + " from the snapshot " + LAST_SNAPCHOT)


            restaure_instance_RDS = client.restore_db_instance_from_db_snapshot(
                DBInstanceIdentifier=NEW_RDS_DB_INSTANCE_INDENTIFIER,
                DBSnapshotIdentifier=LAST_SNAPCHOT,
                DBInstanceClass=DB_CLUSTER_INSTANCE_CLASS,
                Port=PORT,
                DBSubnetGroupName=DB_SUBNET_GROUP_NAME,
                PubliclyAccessible=PUBLICLY_ACCESSIBLE,
                AutoMinorVersionUpgrade=AUTO_MINOR_VERSION_UPGRADE,
                VpcSecurityGroupIds=VPC_SECURITY_GROUP_IDS,
                EnableIAMDatabaseAuthentication=ENABLE_IAM_DATABASE_AUTHENTICATION,
                DBParameterGroupName=DB_PARAMETER_GROUP_NAME
            )

            print (str(restaure_instance_RDS) + "\n")