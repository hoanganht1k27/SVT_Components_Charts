# SNMP Manager Configuration and Deployment
## 1. Edit config in .env file `cp env-template .env`
```sh
# Image info
repository="vyvuvivo/snmp-manager"
tag="v1.2.0"
# ENV for send external command to icinga (using in process_check_result.sh)
ICINGA_HOST="10.98.10.181"
ICINGA_PORT="5665"
ICINGA_USER="icingaweb"
ICINGA_PASSWORD="icingaweb"
# ENV for snmptrap output to mysql (using in snmptt.ini)
## Set the environment variable to enable logging events to the database. 1: enable, 0: disable
MYSQL_DBI_ENABLE="0"
## Set db connection info
MYSQL_DBI_HOST="localhost"
MYSQL_DBI_PORT="3306"
MYSQL_DBI_DATABASE="snmptt"
MYSQL_DBI_TABLE="snmptt"
MYSQL_DBI_TABLE_UNKNOWN="snmptt_unknown"
MYSQL_DBI_USERNAME="snmptt"
MYSQL_DBI_PASSWORD="snmptt"
```

If you enable logging events to the database, ensure that the database already exists.
Alternatively, create a new database as shown below:
```sql
-- create database for snmptt
CREATE DATABASE snmptt;
grant all privileges on snmptt.* to 'snmptt'@'%' identified by 'juniper@123';
grant all privileges on snmptt.* to 'snmptt'@'localhost' identified by 'juniper@123';

USE snmptt;
DROP TABLE snmptt;
CREATE TABLE snmptt (
id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
eventname VARCHAR(50),
eventid VARCHAR(50),
trapoid VARCHAR(100),
enterprise VARCHAR(100),
community VARCHAR(20),
hostname VARCHAR(100),
agentip  VARCHAR(16),
category VARCHAR(20),
severity VARCHAR(20),
uptime  VARCHAR(20),
traptime DATETIME,
formatline VARCHAR(255));
```

## 2. Start the SNMP Manager using Docker Compose
Run the following command to launch the SNMP Manager in a Docker container:
```sh
docker compose -p snmp-manager up -d
```

# MIB Conversion for SNMP Trap Monitoring
To monitor SNMP traps from a specific device, follow these steps:

## 1. Download the MIB file for the device. 
For example, to monitor a MikroTik device, use:
```sh
wget http://download2.mikrotik.com/Mikrotik.mib
```

## 2. Convert the MIB file to a trap configuration file using the "snmpttconvertmib" tool
Replace `/path-to-file/Mikrotik.mib` with the actual path to the downloaded MIB file and `/container-mounted-path/snmptt-mikrotik.conf` with the desired path for the generated configuration file:
```sh
snmpttconvertmib --in=/path-to-file/Mikrotik.mib --out=/container-mounted-path/snmptt-mikrotik.conf
```
For example:
```sh
snmpttconvertmib --in=/root/Mikrotik.mib --out=/etc/snmptt/trapconf/snmptt-mikrotik.conf
```


## 3. Add an exec_command (EXEC) to each event that needs to process passive checks
For example:
```
EVENT coldStart .1.3.6.1.6.3.1.1.5.1 "Status Events" Normal
FORMAT Device reinitialized (coldStart)
EXEC /bin/sh /etc/snmptt/external_command/process_check_result $aA mkt_snmptrap '$Fz' '2' >> /var/log/snmptt/snmptt_exec.log 2>&1
SDESC
A coldStart trap signifies that the SNMPv2 entity, acting
in an agent role, is reinitializing itself and that its
configuration may have been altered.
EDESC
```

`EXEC` command with:
- `/etc/snmptt/external_command/process_check_result`: path to external command
- `$aA`: agent IP address
- `mkt_snmptrap`: passive service on icinga2
- `$Fz`: Translated FORMAT line that is output for passive service

## 4. Integrate the Generated Trap Configuration
Add the generated trap configuration file (snmptt-mikrotik.conf) to the snmptt.ini file for processing SNMP traps. For example:
```
[TrapFiles]
# A list of snmptt.conf files (this is NOT the snmptrapd.conf file).  The COMPLETE path 
# and filename.  Ex: '/etc/snmp/snmptt.conf'
snmptt_conf_files = <<END
/etc/snmptt/trapconf/snmptt-mikrotik.conf
END
```

## 5. Apply the configuration
To apply the configuration, you can execute a command inside the container and run the `reload` command or restart the container.
