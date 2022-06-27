
#createRDS_FROM_SNAPSHOT-Lambda
#Evaristo R. Rivieccio Vega 

"""
Specifier: Lambda that creates copies of each RDS that has the tag "Backup". The copies are generated with the last snpashot created.
"""

import boto3
from botocore.exceptions import ClientError
client = boto3.client('rds')

def lambda_handler(event, context):
    body="There is nothing to do"
    bodyerror=""
    #AUTO CONFIG
    instances = client.describe_db_instances()
    BackupsInstances=[]   
    SnapshotsList=[]
    BackupErrors=[]
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
            #Automatic would be with instance["DBInstanceClass"] but we want to force it to be always "db.t3.small".
            DB_CLUSTER_INSTANCE_CLASS="db.t3.small"
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
            DATELIST=[]
            for LAST_SNAPCHOT in SNAPSHOT_SELECTION["DBSnapshots"]:
                DATELIST.append(LAST_SNAPCHOT["SnapshotCreateTime"])
            DATELIST.sort() 
            for LAST_SNAPCHOT in SNAPSHOT_SELECTION["DBSnapshots"]:
                if LAST_SNAPCHOT["SnapshotCreateTime"] == DATELIST[-1]:
                    LAST_SNAPCHOT_NAME=LAST_SNAPCHOT["DBSnapshotIdentifier"]
                    SnapshotsList.append(LAST_SNAPCHOT_NAME)

            #Restore RDS from Snapchot
            print ("Restoring RDS " + NEW_RDS_DB_INSTANCE_INDENTIFIER + " from the snapshot " + LAST_SNAPCHOT_NAME)

            try:
                restaure_instance_RDS = client.restore_db_instance_from_db_snapshot(
                    DBInstanceIdentifier=NEW_RDS_DB_INSTANCE_INDENTIFIER,
                    DBSnapshotIdentifier=LAST_SNAPCHOT_NAME,
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
                body="Restoring RDS " + str(BackupsInstances) + " from the snapshot " + str(SnapshotsList)
                STATUSCODE=200
            except ClientError as e:
                if e.response ['Error']['Code'] == 'DBInstanceAlreadyExists':
                    print ("The RDS " + NEW_RDS_DB_INSTANCE_INDENTIFIER + " already exists. It will not be restored." )
                    BackupErrors.append(NEW_RDS_DB_INSTANCE_INDENTIFIER)
                    bodyerror="The RDS " + str(BackupErrors) + " already exists. It will not be restored." 
                    STATUSCODE=1
                    pass

                
    return {
        'statusCode': STATUSCODE,
        'body': body,
        'bodyerror': bodyerror
    }   
