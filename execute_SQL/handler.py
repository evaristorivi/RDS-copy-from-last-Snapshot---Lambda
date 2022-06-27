
#truncate.SQL.Lambda
#Evaristo R. Rivieccio Vega  

"""
Connect to DB to run truncation SQL.
---
Add to the Secret Manager the credentials of the DB under the name of the rdscopy
For SQL, in Parametor Store add a /lambda/nombrerdscopy record. This record will be the default one if no other documents are specified in the Secrets Manager
within the optional_documents value.
"""

import boto3
import pymysql
import pymssql
import json

#import base64
#from botocore.exceptions import ClientError


rds = boto3.client('rds')
instances = rds.describe_db_instances()
ssm = boto3.client('ssm')


def get_secret(SecretId):
    secretsmanager = boto3.client('secretsmanager')

    response = secretsmanager.get_secret_value(
        SecretId=SecretId
    )

    database_secrets = json.loads(response['SecretString'])

    #print(database_secrets['password'])
    return database_secrets

def execute_SQL(cursor,SQLDATA):
    for statement in SQLDATA.split(';'):
        if len(statement) > 0:
            try:
                cursor.execute(statement + ';')
                #Trace SQL
                #print ("Execute: " + statement + ';')
            except pymysql.OperationalError as e:
                if e == 'Query was empty':
                    pass


def lambda_handler(event, context):
    BackupsInstancesMysql=[]
    BackupsInstancesSQLserver=[]   

    for instance in instances["DBInstances"]:
        tags = rds.list_tags_for_resource(ResourceName=instance["DBInstanceArn"])
        for tag in tags["TagList"]:
            if tag['Key'] == 'Backup':
                if "copy" in instance["DBInstanceIdentifier"]:
                    if instance["Engine"]=="mysql":
                        BackupsInstancesMysql.append(instance["DBInstanceIdentifier"])
                    if "sqlserver" in instance["Engine"]:
                        BackupsInstancesSQLserver.append(instance["DBInstanceIdentifier"])

                    

    #AUTO CONFIG MYSQL
    for AUTO_CONFIGURE_MYSQL in BackupsInstancesMysql:
        SECRET_NAME=AUTO_CONFIGURE_MYSQL
        print ("Credentials have been obtained from " + SECRET_NAME)
        PARAMETER_STORE_NAME=['/lambda/' + AUTO_CONFIGURE_MYSQL]
        credential=get_secret(SECRET_NAME)

        if "optional_documents" in credential:
            for SPLIT_DOCS in credential["optional_documents"].split(","):
                PARAMETER_STORE_NAME.append(SPLIT_DOCS)

        print ("SQL has been obtained from the Parameter Store " + str(PARAMETER_STORE_NAME) + "\n")
        print ("Establishing a connection with: " + AUTO_CONFIGURE_MYSQL + "... \n")

        for DOCUMENTS in PARAMETER_STORE_NAME:
            parameter = ssm.get_parameter(Name=DOCUMENTS, WithDecryption=True)
            SQLDATA=(parameter['Parameter']['Value'])

            #Configuration Values
            endpoint=credential["endpoint"]
            username=credential["username"]
            password=credential["password"]

            #Conecction
            connection=pymysql.connect(host=endpoint,
                                    user=username,
                                    passwd=password
                                    )
            

            cursor=connection.cursor()
            execute_SQL(cursor,SQLDATA)
            rows=cursor.fetchall()

            print ("SQL executed from " + DOCUMENTS)
            print ("\n")

            for row in rows:
                print("{0} {1} {2}".format(row[0], row[1], row[2]))
                print ("\n")


    #AUTO CONFIG MSSQL
    for AUTO_CONFIGURE_SQL in BackupsInstancesSQLserver:
        SECRET_NAME=AUTO_CONFIGURE_SQL
        print ("Credentials have been obtained from " + SECRET_NAME)
        PARAMETER_STORE_NAME=['/lambda/' + AUTO_CONFIGURE_SQL]
        credential=get_secret(SECRET_NAME)

        if "optional_documents" in credential:
            for SPLIT_DOCS in credential["optional_documents"].split(","):
                PARAMETER_STORE_NAME.append(SPLIT_DOCS)
 
        print ("SQL has been obtained from the Parameter Store " + str(PARAMETER_STORE_NAME) + "\n")
        print ("Establishing a connection with: " + AUTO_CONFIGURE_SQL + "... \n")

        for DOCUMENTS in PARAMETER_STORE_NAME:
            parameter = ssm.get_parameter(Name=DOCUMENTS, WithDecryption=True)
            SQLDATA=(parameter['Parameter']['Value'])

            #Configuration Values
            endpoint=credential["endpoint"]
            username=credential["username"]
            password=credential["password"]

            #Conecction
            connection=pymssql.connect(host=endpoint,
                                    user=username,
                                    password=password
                                    )

            cursor=connection.cursor()
            execute_SQL(cursor,SQLDATA)
            rows=cursor.fetchall()
            
            print ("SQL executed from " + DOCUMENTS)
            print ("\n")

            for row in rows:
                print("{0} {1} {2}".format(row[0], row[1], row[2]))
                print ("\n")

    return {
        'statusCode': 200,
        'body': "SQL executed"
    }
