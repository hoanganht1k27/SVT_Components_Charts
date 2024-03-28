#
# PySNMP MIB module JUNIPER-DOM-MIB (http://snmplabs.com/pysmi)
# ASN.1 source file:///usr/share/snmp/mibs/mib-jnx-dom.txt
# Produced by pysmi-0.3.2 at Mon Nov  5 17:03:41 2018
# On host Server platform Linux version 3.10.0-862.11.6.el7.x86_64 by user root
# Using Python version 2.7.5 (default, Jul 13 2018, 13:06:57) 
#
Integer, ObjectIdentifier, OctetString = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
NamedValues, = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
ConstraintsUnion, SingleValueConstraint, ConstraintsIntersection, ValueSizeConstraint, ValueRangeConstraint = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsUnion", "SingleValueConstraint", "ConstraintsIntersection", "ValueSizeConstraint", "ValueRangeConstraint")
ifIndex, ifDescr = mibBuilder.importSymbols("IF-MIB", "ifIndex", "ifDescr")
jnxDomMibRoot, jnxDomNotifications, jnxDomLaneNotifications = mibBuilder.importSymbols("JUNIPER-SMI", "jnxDomMibRoot", "jnxDomNotifications", "jnxDomLaneNotifications")
NotificationGroup, ModuleCompliance = mibBuilder.importSymbols("SNMPv2-CONF", "NotificationGroup", "ModuleCompliance")
Integer32, MibScalar, MibTable, MibTableRow, MibTableColumn, NotificationType, MibIdentifier, IpAddress, TimeTicks, Counter64, Unsigned32, ModuleIdentity, Gauge32, iso, ObjectIdentity, Bits, Counter32 = mibBuilder.importSymbols("SNMPv2-SMI", "Integer32", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "NotificationType", "MibIdentifier", "IpAddress", "TimeTicks", "Counter64", "Unsigned32", "ModuleIdentity", "Gauge32", "iso", "ObjectIdentity", "Bits", "Counter32")
DisplayString, TextualConvention, DateAndTime = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString", "TextualConvention", "DateAndTime")
jnxDomMib = ModuleIdentity((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1))
jnxDomMib.setRevisions(('2014-03-20 00:00', '2009-12-23 00:00',))
if mibBuilder.loadTexts: jnxDomMib.setLastUpdated('201403200000Z')
if mibBuilder.loadTexts: jnxDomMib.setOrganization('Juniper Networks, Inc.')
class JnxDomAlarmId(TextualConvention, Bits):
    status = 'current'
    namedValues = NamedValues(("domRxLossSignalAlarm", 0), ("domRxCDRLossLockAlarm", 1), ("domRxNotReadyAlarm", 2), ("domRxLaserPowerHighAlarm", 3), ("domRxLaserPowerLowAlarm", 4), ("domTxLaserBiasCurrentHighAlarm", 5), ("domTxLaserBiasCurrentLowAlarm", 6), ("domTxLaserOutputPowerHighAlarm", 7), ("domTxLaserOutputPowerLowAlarm", 8), ("domTxDataNotReadyAlarm", 9), ("domTxNotReadyAlarm", 10), ("domTxLaserFaultAlarm", 11), ("domTxCDRLossLockAlarm", 12), ("domModuleTemperatureHighAlarm", 13), ("domModuleTemperatureLowAlarm", 14), ("domModuleNotReadyAlarm", 15), ("domModulePowerDownAlarm", 16), ("domLinkDownAlarm", 17), ("domModuleRemovedAlarm", 18), ("domModuleVoltageHighAlarm", 19), ("domModuleVoltageLowAlarm", 20))

class JnxDomWarningId(TextualConvention, Bits):
    status = 'current'
    namedValues = NamedValues(("domRxLaserPowerHighWarning", 0), ("domRxLaserPowerLowWarning", 1), ("domTxLaserBiasCurrentHighWarning", 2), ("domTxLaserBiasCurrentLowWarning", 3), ("domTxLaserOutputPowerHighWarning", 4), ("domTxLaserOutputPowerLowWarning", 5), ("domModuleTemperatureHighWarning", 6), ("domModuleTemperatureLowWarning", 7), ("domModuleVoltageHighWarning", 8), ("domModuleVoltageLowWarning", 9))

class JnxDomLaneAlarmId(TextualConvention, Bits):
    status = 'current'
    namedValues = NamedValues(("domLaneRxLaserPowerHighAlarm", 0), ("domLaneRxLaserPowerLowAlarm", 1), ("domLaneTxLaserBiasCurrentHighAlarm", 2), ("domLaneTxLaserBiasCurrentLowAlarm", 3), ("domLaneTxLaserOutputPowerHighAlarm", 4), ("domLaneTxLaserOutputPowerLowAlarm", 5), ("domLaneLaserTemperatureHighAlarm", 6), ("domLaneLaserTemperatureLowAlarm", 7))

class JnxDomLaneWarningId(TextualConvention, Bits):
    status = 'current'
    namedValues = NamedValues(("domLaneRxLaserPowerHighWarning", 0), ("domLaneRxLaserPowerLowWarning", 1), ("domLaneTxLaserBiasCurrentHighWarning", 2), ("domLaneTxLaserBiasCurrentLowWarning", 3), ("domLaneTxLaserOutputPowerHighWarning", 4), ("domLaneTxLaserOutputPowerLowWarning", 5), ("domLaneLaserTemperatureHighWarning", 6), ("domLaneLaserTemperatureLowWarning", 7))

jnxDomDigitalMonitoring = MibIdentifier((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1))
jnxDomCurrentTable = MibTable((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1), )
if mibBuilder.loadTexts: jnxDomCurrentTable.setStatus('current')
jnxDomCurrentEntry = MibTableRow((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1), ).setIndexNames((0, "IF-MIB", "ifIndex"))
if mibBuilder.loadTexts: jnxDomCurrentEntry.setStatus('current')
jnxDomCurrentAlarms = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 1), JnxDomAlarmId()).setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentAlarms.setStatus('current')
jnxDomCurrentAlarmDate = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 2), DateAndTime()).setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentAlarmDate.setStatus('current')
jnxDomLastAlarms = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 3), JnxDomAlarmId()).setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomLastAlarms.setStatus('current')
jnxDomCurrentWarnings = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 4), JnxDomWarningId()).setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentWarnings.setStatus('current')
jnxDomCurrentRxLaserPower = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 5), Integer32()).setUnits('0.01 dbm').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentRxLaserPower.setStatus('current')
jnxDomCurrentTxLaserBiasCurrent = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 6), Integer32()).setUnits('0.001 mA').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentTxLaserBiasCurrent.setStatus('current')
jnxDomCurrentTxLaserOutputPower = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 7), Integer32()).setUnits('0.01 dbm').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentTxLaserOutputPower.setStatus('current')
jnxDomCurrentModuleTemperature = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 8), Integer32()).setUnits('Celsius (degrees C)').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentModuleTemperature.setStatus('current')
jnxDomCurrentRxLaserPowerHighAlarmThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 9), Integer32()).setUnits('0.01 dbm').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentRxLaserPowerHighAlarmThreshold.setStatus('current')
jnxDomCurrentRxLaserPowerLowAlarmThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 10), Integer32()).setUnits('0.01 dbm').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentRxLaserPowerLowAlarmThreshold.setStatus('current')
jnxDomCurrentRxLaserPowerHighWarningThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 11), Integer32()).setUnits('0.01 dbm').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentRxLaserPowerHighWarningThreshold.setStatus('current')
jnxDomCurrentRxLaserPowerLowWarningThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 12), Integer32()).setUnits('0.01 dbm').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentRxLaserPowerLowWarningThreshold.setStatus('current')
jnxDomCurrentTxLaserBiasCurrentHighAlarmThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 13), Integer32()).setUnits('0.001 mA').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentTxLaserBiasCurrentHighAlarmThreshold.setStatus('current')
jnxDomCurrentTxLaserBiasCurrentLowAlarmThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 14), Integer32()).setUnits('0.001 mA').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentTxLaserBiasCurrentLowAlarmThreshold.setStatus('current')
jnxDomCurrentTxLaserBiasCurrentHighWarningThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 15), Integer32()).setUnits('0.001 mA').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentTxLaserBiasCurrentHighWarningThreshold.setStatus('current')
jnxDomCurrentTxLaserBiasCurrentLowWarningThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 16), Integer32()).setUnits('0.001 mA').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentTxLaserBiasCurrentLowWarningThreshold.setStatus('current')
jnxDomCurrentTxLaserOutputPowerHighAlarmThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 17), Integer32()).setUnits('0.01 dbm').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentTxLaserOutputPowerHighAlarmThreshold.setStatus('current')
jnxDomCurrentTxLaserOutputPowerLowAlarmThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 18), Integer32()).setUnits('0.01 dbm').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentTxLaserOutputPowerLowAlarmThreshold.setStatus('current')
jnxDomCurrentTxLaserOutputPowerHighWarningThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 19), Integer32()).setUnits('0.01 dbm').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentTxLaserOutputPowerHighWarningThreshold.setStatus('current')
jnxDomCurrentTxLaserOutputPowerLowWarningThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 20), Integer32()).setUnits('0.01 dbm').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentTxLaserOutputPowerLowWarningThreshold.setStatus('current')
jnxDomCurrentModuleTemperatureHighAlarmThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 21), Integer32()).setUnits('Celsius (degrees C)').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentModuleTemperatureHighAlarmThreshold.setStatus('current')
jnxDomCurrentModuleTemperatureLowAlarmThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 22), Integer32()).setUnits('Celsius (degrees C)').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentModuleTemperatureLowAlarmThreshold.setStatus('current')
jnxDomCurrentModuleTemperatureHighWarningThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 23), Integer32()).setUnits('Celsius (degrees C)').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentModuleTemperatureHighWarningThreshold.setStatus('current')
jnxDomCurrentModuleTemperatureLowWarningThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 24), Integer32()).setUnits('Celsius (degrees C)').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentModuleTemperatureLowWarningThreshold.setStatus('current')
jnxDomCurrentModuleVoltage = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 25), Integer32()).setUnits('0.001 V').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentModuleVoltage.setStatus('current')
jnxDomCurrentModuleVoltageHighAlarmThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 26), Integer32()).setUnits('0.001 V').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentModuleVoltageHighAlarmThreshold.setStatus('current')
jnxDomCurrentModuleVoltageLowAlarmThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 27), Integer32()).setUnits('0.001 V').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentModuleVoltageLowAlarmThreshold.setStatus('current')
jnxDomCurrentModuleVoltageHighWarningThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 28), Integer32()).setUnits('0.001 V').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentModuleVoltageHighWarningThreshold.setStatus('current')
jnxDomCurrentModuleVoltageLowWarningThreshold = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 29), Integer32()).setUnits('0.001 V').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentModuleVoltageLowWarningThreshold.setStatus('current')
jnxDomCurrentModuleLaneCount = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 1, 1, 1, 30), Integer32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentModuleLaneCount.setStatus('current')
jnxDomDigitalLaneMonitoring = MibIdentifier((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 2))
jnxDomModuleLaneTable = MibTable((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 2, 1), )
if mibBuilder.loadTexts: jnxDomModuleLaneTable.setStatus('current')
jnxDomCurrentLaneEntry = MibTableRow((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 2, 1, 1), ).setIndexNames((0, "IF-MIB", "ifIndex"), (0, "JUNIPER-DOM-MIB", "jnxDomLaneIndex"))
if mibBuilder.loadTexts: jnxDomCurrentLaneEntry.setStatus('current')
jnxDomLaneIndex = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 2, 1, 1, 1), Integer32().subtype(subtypeSpec=ValueRangeConstraint(0, 1000))).setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomLaneIndex.setStatus('current')
jnxDomCurrentLaneAlarms = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 2, 1, 1, 2), JnxDomLaneAlarmId()).setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentLaneAlarms.setStatus('current')
jnxDomCurrentLaneAlarmDate = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 2, 1, 1, 3), DateAndTime()).setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentLaneAlarmDate.setStatus('current')
jnxDomLaneLastAlarms = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 2, 1, 1, 4), JnxDomLaneAlarmId()).setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomLaneLastAlarms.setStatus('current')
jnxDomCurrentLaneWarnings = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 2, 1, 1, 5), JnxDomLaneWarningId()).setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentLaneWarnings.setStatus('current')
jnxDomCurrentLaneRxLaserPower = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 2, 1, 1, 6), Integer32()).setUnits('0.01 dbm').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentLaneRxLaserPower.setStatus('current')
jnxDomCurrentLaneTxLaserBiasCurrent = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 2, 1, 1, 7), Integer32()).setUnits('0.001 mA').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentLaneTxLaserBiasCurrent.setStatus('current')
jnxDomCurrentLaneTxLaserOutputPower = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 2, 1, 1, 8), Integer32()).setUnits('0.01 dbm').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentLaneTxLaserOutputPower.setStatus('current')
jnxDomCurrentLaneLaserTemperature = MibTableColumn((1, 3, 6, 1, 4, 1, 2636, 3, 60, 1, 2, 1, 1, 9), Integer32()).setUnits('Celsius (degrees C)').setMaxAccess("readonly")
if mibBuilder.loadTexts: jnxDomCurrentLaneLaserTemperature.setStatus('current')
jnxDomNotificationPrefix = MibIdentifier((1, 3, 6, 1, 4, 1, 2636, 4, 18, 0))
jnxDomAlarmSet = NotificationType((1, 3, 6, 1, 4, 1, 2636, 4, 18, 0, 1)).setObjects(("IF-MIB", "ifDescr"), ("JUNIPER-DOM-MIB", "jnxDomLastAlarms"), ("JUNIPER-DOM-MIB", "jnxDomCurrentAlarms"), ("JUNIPER-DOM-MIB", "jnxDomCurrentAlarmDate"))
if mibBuilder.loadTexts: jnxDomAlarmSet.setStatus('current')
jnxDomAlarmCleared = NotificationType((1, 3, 6, 1, 4, 1, 2636, 4, 18, 0, 2)).setObjects(("IF-MIB", "ifDescr"), ("JUNIPER-DOM-MIB", "jnxDomLastAlarms"), ("JUNIPER-DOM-MIB", "jnxDomCurrentAlarms"), ("JUNIPER-DOM-MIB", "jnxDomCurrentAlarmDate"))
if mibBuilder.loadTexts: jnxDomAlarmCleared.setStatus('current')
jnxDomLaneNotificationPrefix = MibIdentifier((1, 3, 6, 1, 4, 1, 2636, 4, 25, 0))
jnxDomLaneAlarmSet = NotificationType((1, 3, 6, 1, 4, 1, 2636, 4, 25, 0, 1)).setObjects(("IF-MIB", "ifDescr"), ("JUNIPER-DOM-MIB", "jnxDomLaneIndex"), ("JUNIPER-DOM-MIB", "jnxDomLaneLastAlarms"), ("JUNIPER-DOM-MIB", "jnxDomCurrentLaneAlarms"), ("JUNIPER-DOM-MIB", "jnxDomCurrentLaneAlarmDate"))
if mibBuilder.loadTexts: jnxDomLaneAlarmSet.setStatus('current')
jnxDomLaneAlarmCleared = NotificationType((1, 3, 6, 1, 4, 1, 2636, 4, 25, 0, 2)).setObjects(("IF-MIB", "ifDescr"), ("JUNIPER-DOM-MIB", "jnxDomLaneIndex"), ("JUNIPER-DOM-MIB", "jnxDomLaneLastAlarms"), ("JUNIPER-DOM-MIB", "jnxDomCurrentLaneAlarms"), ("JUNIPER-DOM-MIB", "jnxDomCurrentLaneAlarmDate"))
if mibBuilder.loadTexts: jnxDomLaneAlarmCleared.setStatus('current')
mibBuilder.exportSymbols("JUNIPER-DOM-MIB", jnxDomCurrentTxLaserBiasCurrentLowAlarmThreshold=jnxDomCurrentTxLaserBiasCurrentLowAlarmThreshold, jnxDomCurrentLaneWarnings=jnxDomCurrentLaneWarnings, jnxDomCurrentModuleVoltage=jnxDomCurrentModuleVoltage, JnxDomLaneWarningId=JnxDomLaneWarningId, jnxDomCurrentModuleVoltageLowAlarmThreshold=jnxDomCurrentModuleVoltageLowAlarmThreshold, jnxDomCurrentTxLaserOutputPowerHighWarningThreshold=jnxDomCurrentTxLaserOutputPowerHighWarningThreshold, jnxDomCurrentLaneAlarms=jnxDomCurrentLaneAlarms, jnxDomLaneAlarmCleared=jnxDomLaneAlarmCleared, jnxDomAlarmSet=jnxDomAlarmSet, jnxDomMib=jnxDomMib, jnxDomCurrentRxLaserPowerHighAlarmThreshold=jnxDomCurrentRxLaserPowerHighAlarmThreshold, jnxDomCurrentTable=jnxDomCurrentTable, jnxDomCurrentTxLaserOutputPowerLowAlarmThreshold=jnxDomCurrentTxLaserOutputPowerLowAlarmThreshold, JnxDomAlarmId=JnxDomAlarmId, jnxDomCurrentEntry=jnxDomCurrentEntry, jnxDomCurrentTxLaserBiasCurrentHighAlarmThreshold=jnxDomCurrentTxLaserBiasCurrentHighAlarmThreshold, jnxDomCurrentAlarms=jnxDomCurrentAlarms, jnxDomCurrentLaneTxLaserBiasCurrent=jnxDomCurrentLaneTxLaserBiasCurrent, jnxDomCurrentTxLaserBiasCurrent=jnxDomCurrentTxLaserBiasCurrent, JnxDomLaneAlarmId=JnxDomLaneAlarmId, jnxDomCurrentLaneTxLaserOutputPower=jnxDomCurrentLaneTxLaserOutputPower, jnxDomLastAlarms=jnxDomLastAlarms, jnxDomCurrentRxLaserPowerLowWarningThreshold=jnxDomCurrentRxLaserPowerLowWarningThreshold, jnxDomCurrentLaneEntry=jnxDomCurrentLaneEntry, jnxDomDigitalLaneMonitoring=jnxDomDigitalLaneMonitoring, jnxDomLaneNotificationPrefix=jnxDomLaneNotificationPrefix, jnxDomCurrentTxLaserBiasCurrentLowWarningThreshold=jnxDomCurrentTxLaserBiasCurrentLowWarningThreshold, jnxDomDigitalMonitoring=jnxDomDigitalMonitoring, jnxDomAlarmCleared=jnxDomAlarmCleared, jnxDomCurrentRxLaserPower=jnxDomCurrentRxLaserPower, PYSNMP_MODULE_ID=jnxDomMib, jnxDomCurrentModuleTemperatureLowAlarmThreshold=jnxDomCurrentModuleTemperatureLowAlarmThreshold, jnxDomCurrentModuleTemperatureHighWarningThreshold=jnxDomCurrentModuleTemperatureHighWarningThreshold, jnxDomCurrentWarnings=jnxDomCurrentWarnings, jnxDomCurrentAlarmDate=jnxDomCurrentAlarmDate, jnxDomLaneAlarmSet=jnxDomLaneAlarmSet, jnxDomNotificationPrefix=jnxDomNotificationPrefix, jnxDomCurrentModuleTemperatureHighAlarmThreshold=jnxDomCurrentModuleTemperatureHighAlarmThreshold, jnxDomCurrentTxLaserOutputPowerHighAlarmThreshold=jnxDomCurrentTxLaserOutputPowerHighAlarmThreshold, jnxDomCurrentTxLaserBiasCurrentHighWarningThreshold=jnxDomCurrentTxLaserBiasCurrentHighWarningThreshold, jnxDomCurrentTxLaserOutputPower=jnxDomCurrentTxLaserOutputPower, jnxDomCurrentLaneLaserTemperature=jnxDomCurrentLaneLaserTemperature, jnxDomCurrentRxLaserPowerHighWarningThreshold=jnxDomCurrentRxLaserPowerHighWarningThreshold, jnxDomCurrentLaneRxLaserPower=jnxDomCurrentLaneRxLaserPower, jnxDomCurrentLaneAlarmDate=jnxDomCurrentLaneAlarmDate, jnxDomLaneLastAlarms=jnxDomLaneLastAlarms, jnxDomCurrentModuleTemperature=jnxDomCurrentModuleTemperature, jnxDomCurrentModuleVoltageHighWarningThreshold=jnxDomCurrentModuleVoltageHighWarningThreshold, jnxDomCurrentModuleLaneCount=jnxDomCurrentModuleLaneCount, jnxDomCurrentRxLaserPowerLowAlarmThreshold=jnxDomCurrentRxLaserPowerLowAlarmThreshold, jnxDomModuleLaneTable=jnxDomModuleLaneTable, jnxDomCurrentModuleVoltageLowWarningThreshold=jnxDomCurrentModuleVoltageLowWarningThreshold, jnxDomCurrentModuleVoltageHighAlarmThreshold=jnxDomCurrentModuleVoltageHighAlarmThreshold, JnxDomWarningId=JnxDomWarningId, jnxDomCurrentModuleTemperatureLowWarningThreshold=jnxDomCurrentModuleTemperatureLowWarningThreshold, jnxDomLaneIndex=jnxDomLaneIndex, jnxDomCurrentTxLaserOutputPowerLowWarningThreshold=jnxDomCurrentTxLaserOutputPowerLowWarningThreshold)