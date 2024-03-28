#
# PySNMP MIB module SNMPv2-MIB (http://snmplabs.com/pysmi)
# ASN.1 source file:///usr/share/snmp/mibs/SNMPv2-MIB.txt
# Produced by pysmi-0.3.2 at Thu Nov  8 17:36:57 2018
# On host nms_new_01.svtech.com.vn platform Linux version 3.10.0-862.3.3.el7.x86_64 by user root
# Using Python version 2.7.5 (default, Apr 11 2018, 07:36:10) 
#
Integer, ObjectIdentifier, OctetString = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
NamedValues, = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
ConstraintsUnion, SingleValueConstraint, ConstraintsIntersection, ValueSizeConstraint, ValueRangeConstraint = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsUnion", "SingleValueConstraint", "ConstraintsIntersection", "ValueSizeConstraint", "ValueRangeConstraint")
NotificationGroup, ModuleCompliance, ObjectGroup = mibBuilder.importSymbols("SNMPv2-CONF", "NotificationGroup", "ModuleCompliance", "ObjectGroup")
Integer32, MibScalar, MibTable, MibTableRow, MibTableColumn, NotificationType, MibIdentifier, mib_2, IpAddress, TimeTicks, Counter64, Unsigned32, ModuleIdentity, Gauge32, snmpModules, iso, ObjectIdentity, Bits, Counter32 = mibBuilder.importSymbols("SNMPv2-SMI", "Integer32", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "NotificationType", "MibIdentifier", "mib-2", "IpAddress", "TimeTicks", "Counter64", "Unsigned32", "ModuleIdentity", "Gauge32", "snmpModules", "iso", "ObjectIdentity", "Bits", "Counter32")
DisplayString, TimeStamp, TextualConvention, TestAndIncr = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString", "TimeStamp", "TextualConvention", "TestAndIncr")
snmpMIB = ModuleIdentity((1, 3, 6, 1, 6, 3, 1))
snmpMIB.setRevisions(('2002-10-16 00:00', '1995-11-09 00:00', '1993-04-01 00:00',))
if mibBuilder.loadTexts: snmpMIB.setLastUpdated('200210160000Z')
if mibBuilder.loadTexts: snmpMIB.setOrganization('IETF SNMPv3 Working Group')
snmpMIBObjects = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 1))
system = MibIdentifier((1, 3, 6, 1, 2, 1, 1))
sysDescr = MibScalar((1, 3, 6, 1, 2, 1, 1, 1), DisplayString().subtype(subtypeSpec=ValueSizeConstraint(0, 255))).setMaxAccess("readonly")
if mibBuilder.loadTexts: sysDescr.setStatus('current')
sysObjectID = MibScalar((1, 3, 6, 1, 2, 1, 1, 2), ObjectIdentifier()).setMaxAccess("readonly")
if mibBuilder.loadTexts: sysObjectID.setStatus('current')
sysUpTime = MibScalar((1, 3, 6, 1, 2, 1, 1, 3), TimeTicks()).setMaxAccess("readonly")
if mibBuilder.loadTexts: sysUpTime.setStatus('current')
sysContact = MibScalar((1, 3, 6, 1, 2, 1, 1, 4), DisplayString().subtype(subtypeSpec=ValueSizeConstraint(0, 255))).setMaxAccess("readwrite")
if mibBuilder.loadTexts: sysContact.setStatus('current')
sysName = MibScalar((1, 3, 6, 1, 2, 1, 1, 5), DisplayString().subtype(subtypeSpec=ValueSizeConstraint(0, 255))).setMaxAccess("readwrite")
if mibBuilder.loadTexts: sysName.setStatus('current')
sysLocation = MibScalar((1, 3, 6, 1, 2, 1, 1, 6), DisplayString().subtype(subtypeSpec=ValueSizeConstraint(0, 255))).setMaxAccess("readwrite")
if mibBuilder.loadTexts: sysLocation.setStatus('current')
sysServices = MibScalar((1, 3, 6, 1, 2, 1, 1, 7), Integer32().subtype(subtypeSpec=ValueRangeConstraint(0, 127))).setMaxAccess("readonly")
if mibBuilder.loadTexts: sysServices.setStatus('current')
sysORLastChange = MibScalar((1, 3, 6, 1, 2, 1, 1, 8), TimeStamp()).setMaxAccess("readonly")
if mibBuilder.loadTexts: sysORLastChange.setStatus('current')
sysORTable = MibTable((1, 3, 6, 1, 2, 1, 1, 9), )
if mibBuilder.loadTexts: sysORTable.setStatus('current')
sysOREntry = MibTableRow((1, 3, 6, 1, 2, 1, 1, 9, 1), ).setIndexNames((0, "SNMPv2-MIB", "sysORIndex"))
if mibBuilder.loadTexts: sysOREntry.setStatus('current')
sysORIndex = MibTableColumn((1, 3, 6, 1, 2, 1, 1, 9, 1, 1), Integer32().subtype(subtypeSpec=ValueRangeConstraint(1, 2147483647)))
if mibBuilder.loadTexts: sysORIndex.setStatus('current')
sysORID = MibTableColumn((1, 3, 6, 1, 2, 1, 1, 9, 1, 2), ObjectIdentifier()).setMaxAccess("readonly")
if mibBuilder.loadTexts: sysORID.setStatus('current')
sysORDescr = MibTableColumn((1, 3, 6, 1, 2, 1, 1, 9, 1, 3), DisplayString()).setMaxAccess("readonly")
if mibBuilder.loadTexts: sysORDescr.setStatus('current')
sysORUpTime = MibTableColumn((1, 3, 6, 1, 2, 1, 1, 9, 1, 4), TimeStamp()).setMaxAccess("readonly")
if mibBuilder.loadTexts: sysORUpTime.setStatus('current')
snmp = MibIdentifier((1, 3, 6, 1, 2, 1, 11))
snmpInPkts = MibScalar((1, 3, 6, 1, 2, 1, 11, 1), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInPkts.setStatus('current')
snmpInBadVersions = MibScalar((1, 3, 6, 1, 2, 1, 11, 3), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInBadVersions.setStatus('current')
snmpInBadCommunityNames = MibScalar((1, 3, 6, 1, 2, 1, 11, 4), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInBadCommunityNames.setStatus('current')
snmpInBadCommunityUses = MibScalar((1, 3, 6, 1, 2, 1, 11, 5), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInBadCommunityUses.setStatus('current')
snmpInASNParseErrs = MibScalar((1, 3, 6, 1, 2, 1, 11, 6), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInASNParseErrs.setStatus('current')
snmpEnableAuthenTraps = MibScalar((1, 3, 6, 1, 2, 1, 11, 30), Integer32().subtype(subtypeSpec=SingleValueConstraint(1, 2)).clone(namedValues=NamedValues(("enabled", 1), ("disabled", 2)))).setMaxAccess("readwrite")
if mibBuilder.loadTexts: snmpEnableAuthenTraps.setStatus('current')
snmpSilentDrops = MibScalar((1, 3, 6, 1, 2, 1, 11, 31), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpSilentDrops.setStatus('current')
snmpProxyDrops = MibScalar((1, 3, 6, 1, 2, 1, 11, 32), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpProxyDrops.setStatus('current')
snmpTrap = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 1, 4))
snmpTrapOID = MibScalar((1, 3, 6, 1, 6, 3, 1, 1, 4, 1), ObjectIdentifier()).setMaxAccess("accessiblefornotify")
if mibBuilder.loadTexts: snmpTrapOID.setStatus('current')
snmpTrapEnterprise = MibScalar((1, 3, 6, 1, 6, 3, 1, 1, 4, 3), ObjectIdentifier()).setMaxAccess("accessiblefornotify")
if mibBuilder.loadTexts: snmpTrapEnterprise.setStatus('current')
snmpTraps = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 1, 5))
coldStart = NotificationType((1, 3, 6, 1, 6, 3, 1, 1, 5, 1))
if mibBuilder.loadTexts: coldStart.setStatus('current')
warmStart = NotificationType((1, 3, 6, 1, 6, 3, 1, 1, 5, 2))
if mibBuilder.loadTexts: warmStart.setStatus('current')
authenticationFailure = NotificationType((1, 3, 6, 1, 6, 3, 1, 1, 5, 5))
if mibBuilder.loadTexts: authenticationFailure.setStatus('current')
snmpSet = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 1, 6))
snmpSetSerialNo = MibScalar((1, 3, 6, 1, 6, 3, 1, 1, 6, 1), TestAndIncr()).setMaxAccess("readwrite")
if mibBuilder.loadTexts: snmpSetSerialNo.setStatus('current')
snmpMIBConformance = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 2))
snmpMIBCompliances = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 2, 1))
snmpMIBGroups = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 2, 2))
snmpBasicCompliance = ModuleCompliance((1, 3, 6, 1, 6, 3, 1, 2, 1, 2)).setObjects(("SNMPv2-MIB", "snmpGroup"), ("SNMPv2-MIB", "snmpSetGroup"), ("SNMPv2-MIB", "systemGroup"), ("SNMPv2-MIB", "snmpBasicNotificationsGroup"), ("SNMPv2-MIB", "snmpCommunityGroup"))

if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    snmpBasicCompliance = snmpBasicCompliance.setStatus('deprecated')
snmpBasicComplianceRev2 = ModuleCompliance((1, 3, 6, 1, 6, 3, 1, 2, 1, 3)).setObjects(("SNMPv2-MIB", "snmpGroup"), ("SNMPv2-MIB", "snmpSetGroup"), ("SNMPv2-MIB", "systemGroup"), ("SNMPv2-MIB", "snmpBasicNotificationsGroup"), ("SNMPv2-MIB", "snmpCommunityGroup"), ("SNMPv2-MIB", "snmpWarmStartNotificationGroup"))

if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    snmpBasicComplianceRev2 = snmpBasicComplianceRev2.setStatus('current')
snmpGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 8)).setObjects(("SNMPv2-MIB", "snmpInPkts"), ("SNMPv2-MIB", "snmpInBadVersions"), ("SNMPv2-MIB", "snmpInASNParseErrs"), ("SNMPv2-MIB", "snmpSilentDrops"), ("SNMPv2-MIB", "snmpProxyDrops"), ("SNMPv2-MIB", "snmpEnableAuthenTraps"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    snmpGroup = snmpGroup.setStatus('current')
snmpCommunityGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 9)).setObjects(("SNMPv2-MIB", "snmpInBadCommunityNames"), ("SNMPv2-MIB", "snmpInBadCommunityUses"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    snmpCommunityGroup = snmpCommunityGroup.setStatus('current')
snmpSetGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 5)).setObjects(("SNMPv2-MIB", "snmpSetSerialNo"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    snmpSetGroup = snmpSetGroup.setStatus('current')
systemGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 6)).setObjects(("SNMPv2-MIB", "sysDescr"), ("SNMPv2-MIB", "sysObjectID"), ("SNMPv2-MIB", "sysUpTime"), ("SNMPv2-MIB", "sysContact"), ("SNMPv2-MIB", "sysName"), ("SNMPv2-MIB", "sysLocation"), ("SNMPv2-MIB", "sysServices"), ("SNMPv2-MIB", "sysORLastChange"), ("SNMPv2-MIB", "sysORID"), ("SNMPv2-MIB", "sysORUpTime"), ("SNMPv2-MIB", "sysORDescr"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    systemGroup = systemGroup.setStatus('current')
snmpBasicNotificationsGroup = NotificationGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 7)).setObjects(("SNMPv2-MIB", "coldStart"), ("SNMPv2-MIB", "authenticationFailure"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    snmpBasicNotificationsGroup = snmpBasicNotificationsGroup.setStatus('current')
snmpWarmStartNotificationGroup = NotificationGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 11)).setObjects(("SNMPv2-MIB", "warmStart"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    snmpWarmStartNotificationGroup = snmpWarmStartNotificationGroup.setStatus('current')
snmpNotificationGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 12)).setObjects(("SNMPv2-MIB", "snmpTrapOID"), ("SNMPv2-MIB", "snmpTrapEnterprise"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    snmpNotificationGroup = snmpNotificationGroup.setStatus('current')
snmpOutPkts = MibScalar((1, 3, 6, 1, 2, 1, 11, 2), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpOutPkts.setStatus('obsolete')
snmpInTooBigs = MibScalar((1, 3, 6, 1, 2, 1, 11, 8), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInTooBigs.setStatus('obsolete')
snmpInNoSuchNames = MibScalar((1, 3, 6, 1, 2, 1, 11, 9), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInNoSuchNames.setStatus('obsolete')
snmpInBadValues = MibScalar((1, 3, 6, 1, 2, 1, 11, 10), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInBadValues.setStatus('obsolete')
snmpInReadOnlys = MibScalar((1, 3, 6, 1, 2, 1, 11, 11), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInReadOnlys.setStatus('obsolete')
snmpInGenErrs = MibScalar((1, 3, 6, 1, 2, 1, 11, 12), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInGenErrs.setStatus('obsolete')
snmpInTotalReqVars = MibScalar((1, 3, 6, 1, 2, 1, 11, 13), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInTotalReqVars.setStatus('obsolete')
snmpInTotalSetVars = MibScalar((1, 3, 6, 1, 2, 1, 11, 14), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInTotalSetVars.setStatus('obsolete')
snmpInGetRequests = MibScalar((1, 3, 6, 1, 2, 1, 11, 15), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInGetRequests.setStatus('obsolete')
snmpInGetNexts = MibScalar((1, 3, 6, 1, 2, 1, 11, 16), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInGetNexts.setStatus('obsolete')
snmpInSetRequests = MibScalar((1, 3, 6, 1, 2, 1, 11, 17), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInSetRequests.setStatus('obsolete')
snmpInGetResponses = MibScalar((1, 3, 6, 1, 2, 1, 11, 18), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInGetResponses.setStatus('obsolete')
snmpInTraps = MibScalar((1, 3, 6, 1, 2, 1, 11, 19), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpInTraps.setStatus('obsolete')
snmpOutTooBigs = MibScalar((1, 3, 6, 1, 2, 1, 11, 20), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpOutTooBigs.setStatus('obsolete')
snmpOutNoSuchNames = MibScalar((1, 3, 6, 1, 2, 1, 11, 21), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpOutNoSuchNames.setStatus('obsolete')
snmpOutBadValues = MibScalar((1, 3, 6, 1, 2, 1, 11, 22), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpOutBadValues.setStatus('obsolete')
snmpOutGenErrs = MibScalar((1, 3, 6, 1, 2, 1, 11, 24), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpOutGenErrs.setStatus('obsolete')
snmpOutGetRequests = MibScalar((1, 3, 6, 1, 2, 1, 11, 25), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpOutGetRequests.setStatus('obsolete')
snmpOutGetNexts = MibScalar((1, 3, 6, 1, 2, 1, 11, 26), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpOutGetNexts.setStatus('obsolete')
snmpOutSetRequests = MibScalar((1, 3, 6, 1, 2, 1, 11, 27), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpOutSetRequests.setStatus('obsolete')
snmpOutGetResponses = MibScalar((1, 3, 6, 1, 2, 1, 11, 28), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpOutGetResponses.setStatus('obsolete')
snmpOutTraps = MibScalar((1, 3, 6, 1, 2, 1, 11, 29), Counter32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: snmpOutTraps.setStatus('obsolete')
snmpObsoleteGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 10)).setObjects(("SNMPv2-MIB", "snmpOutPkts"), ("SNMPv2-MIB", "snmpInTooBigs"), ("SNMPv2-MIB", "snmpInNoSuchNames"), ("SNMPv2-MIB", "snmpInBadValues"), ("SNMPv2-MIB", "snmpInReadOnlys"), ("SNMPv2-MIB", "snmpInGenErrs"), ("SNMPv2-MIB", "snmpInTotalReqVars"), ("SNMPv2-MIB", "snmpInTotalSetVars"), ("SNMPv2-MIB", "snmpInGetRequests"), ("SNMPv2-MIB", "snmpInGetNexts"), ("SNMPv2-MIB", "snmpInSetRequests"), ("SNMPv2-MIB", "snmpInGetResponses"), ("SNMPv2-MIB", "snmpInTraps"), ("SNMPv2-MIB", "snmpOutTooBigs"), ("SNMPv2-MIB", "snmpOutNoSuchNames"), ("SNMPv2-MIB", "snmpOutBadValues"), ("SNMPv2-MIB", "snmpOutGenErrs"), ("SNMPv2-MIB", "snmpOutGetRequests"), ("SNMPv2-MIB", "snmpOutGetNexts"), ("SNMPv2-MIB", "snmpOutSetRequests"), ("SNMPv2-MIB", "snmpOutGetResponses"), ("SNMPv2-MIB", "snmpOutTraps"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    snmpObsoleteGroup = snmpObsoleteGroup.setStatus('obsolete')
mibBuilder.exportSymbols("SNMPv2-MIB", snmpMIBGroups=snmpMIBGroups, snmpSetGroup=snmpSetGroup, snmpInTraps=snmpInTraps, sysOREntry=sysOREntry, snmpOutPkts=snmpOutPkts, snmpInTotalSetVars=snmpInTotalSetVars, snmpInGetNexts=snmpInGetNexts, sysLocation=sysLocation, snmpBasicNotificationsGroup=snmpBasicNotificationsGroup, snmpOutTooBigs=snmpOutTooBigs, systemGroup=systemGroup, snmpMIB=snmpMIB, snmpInSetRequests=snmpInSetRequests, snmpInBadVersions=snmpInBadVersions, snmpTrapEnterprise=snmpTrapEnterprise, sysName=sysName, snmpTrapOID=snmpTrapOID, snmpOutNoSuchNames=snmpOutNoSuchNames, snmpInReadOnlys=snmpInReadOnlys, snmpOutGetResponses=snmpOutGetResponses, snmpWarmStartNotificationGroup=snmpWarmStartNotificationGroup, warmStart=warmStart, sysUpTime=sysUpTime, snmpCommunityGroup=snmpCommunityGroup, snmpInTotalReqVars=snmpInTotalReqVars, sysORLastChange=sysORLastChange, snmpOutGetNexts=snmpOutGetNexts, snmpOutGetRequests=snmpOutGetRequests, snmpInBadCommunityUses=snmpInBadCommunityUses, snmpMIBCompliances=snmpMIBCompliances, snmpTrap=snmpTrap, PYSNMP_MODULE_ID=snmpMIB, coldStart=coldStart, authenticationFailure=authenticationFailure, snmpInGenErrs=snmpInGenErrs, snmpInGetRequests=snmpInGetRequests, snmpOutTraps=snmpOutTraps, snmpOutGenErrs=snmpOutGenErrs, snmpProxyDrops=snmpProxyDrops, snmpSet=snmpSet, snmpMIBObjects=snmpMIBObjects, sysContact=sysContact, snmpOutBadValues=snmpOutBadValues, sysServices=sysServices, snmpTraps=snmpTraps, sysObjectID=sysObjectID, snmpOutSetRequests=snmpOutSetRequests, snmpInNoSuchNames=snmpInNoSuchNames, snmpObsoleteGroup=snmpObsoleteGroup, sysDescr=sysDescr, snmpMIBConformance=snmpMIBConformance, snmpInPkts=snmpInPkts, snmpGroup=snmpGroup, snmpBasicCompliance=snmpBasicCompliance, snmpInBadCommunityNames=snmpInBadCommunityNames, system=system, sysORUpTime=sysORUpTime, snmpBasicComplianceRev2=snmpBasicComplianceRev2, sysORTable=sysORTable, snmpInBadValues=snmpInBadValues, sysORDescr=sysORDescr, sysORIndex=sysORIndex, snmpSetSerialNo=snmpSetSerialNo, sysORID=sysORID, snmpInGetResponses=snmpInGetResponses, snmp=snmp, snmpInTooBigs=snmpInTooBigs, snmpInASNParseErrs=snmpInASNParseErrs, snmpEnableAuthenTraps=snmpEnableAuthenTraps, snmpNotificationGroup=snmpNotificationGroup, snmpSilentDrops=snmpSilentDrops)
