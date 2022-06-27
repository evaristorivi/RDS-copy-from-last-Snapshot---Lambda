# README #

![scheme](https://bitbucket.org/bitbucketsm/aws.lambdas/raw/633909690cec50863cee441259bd2b95797ca13f/RDS-backup/scheme.png)


### Descripción ###

Sistema de Backups de RDS sin servidor para no depender de las máquinas de Scripts.
<br />
### Requisitos ###
"restore_rds_from_snapshot":
<br />
-Añadir Tag: "Backup" (Con cualquier valor) a la RDS de la que se quiere crear copias.
<br />
-El rol tiene que tener la política adjunta rds-backup-policie.json
<br />

"delete_rds":
<br />
Sin requisitos.
<br />
"restore_rds_from_snapshot"
<br />
Se requiere taguear las RDS indicadas con el tag "Backup"
<br />
"executeSQL":
<br />
Para la ejecución de código SQL se requiere:
<br />
-Un Parameter Store con el nombre /lambda/nombrerds+copy que contenga el código SQL a ejecutar.
<br />
-Opcionalmente se pueden crear otros documentos SQL: /lambda/nombrerds+copy-parte1, /lambda/nombrerds+copy-parte2, etc.... Estos deberán de ser indicados explícitamente en el campo optional_documents del Secret MAnager. (Explicado a continuación)

-Un secreto en AWS Secrets Manager por cada rds-copy con el mismo nombre de la que sería la rds-copy: nombrerds+copy
<br />
Debe tener los siguientes campos:
<br />
endpoint
<br />
username
<br />
password
<br />
Opcionalmente se puede añadir un campo optional_documents donde se indicarán documentos SQL extras del Parameter Store, separados por ",".
<br />
Si no existen estos documentos extra solo se ejecutará un único documento, el nombrado: /lambda/nombrerds+copy


Cruce de SG:
<br />
-Lambda debe permitir el SG de las RDS en su SG y a su vez las RDS deben permitir el SG de la Lambda en sus SG.
<br />
-La lambda debe de estar en la VPC y subnet correctas.
<br />
-El rol debe tener la política: AWSLambdaVPCAccessExecutionRole
<br />

### Funcionamiento deseado de las Lambdas ###

1. Se ejecuta la Lambda "delete_rds" que elimina la última copia.
(Esta recorre las rds en búsqueda de las que tengan el tag "Backup" y la palabra copy en el nombre y actúa sobre ellas)

2. Se ejecuta la Lambda "restore_rds_from_snapshot" que lanza una nueva rds-copy desde la última snapshot.
(Esta recorre las rds en búsqueda de las que tengan el tag "Backup" y actúa sobre ellas)

3. Se ejecuta la Lambda "executeSQL"
(Esta recorre las rds en búsqueda de las que tengan el tag "Copy" y la palabra copy en el nombre (Doble seguridad),
Por cada RDS que encuentre se parametriza automáticamente la lambda:
<br />
-Credenciales de acceso, desde Secret manager.
<br />
-SQL que va a ejecutar, desde Parameter Store.
<br />
Y ejecuta cada SQL en cada BD.

### Arquitectura y precio ###

"delete_rds" y "restore_rds_from_snapshot":
<br />
Funcionan sobre arm64 (Graviton) así que el precio es:
<br />
Arm      0,0000133334 USD por cada GB-segundo0,20 USD por 1 millón de solicitudes
<br />
128mb    0,0000000017 USD
<br />

"executeSQL" corre sobre x86_64 debido a que no existe para arm64 el módulo pymssql utilizado en la conexión mssql.
<br />
Precio de x86	0,0000166667 USD por cada GB/segundo	0,20 USD por un millón de solicitudes
<br />
128mb	        0,0000000021 USD
<br />



* Evaristo R. Rivieccio Vega - evaristo.rivieccio@colex.grupo-sm.com - Operaciones - Grupo SM