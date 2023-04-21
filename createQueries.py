import json
import csv
from uuid import *

f=open("config/config.json")
config=json.load(f)
f.close()

users=[]
with open(config['folder']['input']+"/"+config['file']['input'], 'r') as file:
    users.extend(csv.reader(file))

userQueries=[]
screeningQueries=[]
deviceConfigsQueries=[]
evaluationCriteriaQueries=[]

userTemplate="insert into Users(Timestamp, Modified, Username, CognitoGuid, HasLoggedIn, RequestedDataDeletion, RequestedDataDeletionReason, DisabledDataSharing, RequestedDataDeletionReasonText) "
for user in users:
    userTemplate1=userTemplate+"values(SYSDATETIME(), SYSDATETIME(),'"+user[0]+"','"+user[1]+"', 1, Null, Null, Null, Null);\n"
    userQueries.append(userTemplate1)


screeningTemplate="insert into screenings(timestamp,guid,clinicid,uploadedts,userid) "
startUserID=config['start']['userId']
startScreeningGuid=config['start']['screeningGuid']
for i in range(len(users)):
    screeningTemplate1=screeningTemplate+"values(SYSDATETIME(),'"+str(startScreeningGuid)+"',1,SYSDATETIME(),"+str(startUserID)+");\n"
    screeningQueries.append(screeningTemplate1)
    startScreeningGuid=str(UUID(int=UUID(startScreeningGuid).int+1)).upper()
    startUserID+=1


deviceConfigsTemplate="insert into DeviceConfigs(timestamp,Modified,guid,StimDeviceId,ScreeningId,FirmwareVersion,AppVersion,AppDeviceId) "
evaluationCriteriaTemplate="insert into EvaluationCriteria(timestamp,Modified,guid,DeviceConfigurationId,ScreeningId,Foot,StimulationCurrentAmplitude,SkinParesthesiaPulseWidth,FootParesthesiaPulseWidth,ComfortLevelPulseWidth,EmgDetectionPointPulseWidth,TargetTherapyLevelPulseWidth,ComfortLevelEMGStrength,EmgDetectionPointEMGStrength,TargetEMGStrength,UploadedTS,TherapyLength,TherapySchedule,EmgStrengthMax,CurrentTick,TempPainThreshold,DailyTherapyTime,LastCompletedTime,IsValid) "
startScreeningID=config['start']['screeningId']
startDeviceConfigGuid=config['start']['deviceConfigGuid']
startDeviceConfigurationID=config['start']['deviceConfigurationID']
for i in range(len(users)):
    deviceConfigsTemplate1=deviceConfigsTemplate+"values(SYSDATETIME(),SYSDATETIME(),'"+startDeviceConfigGuid+"','1',"+str(startScreeningID)+",'1.7.4','1.0.102',null);\n"
    evaluationCriteriaTemplate1=evaluationCriteriaTemplate+"values(SYSDATETIME(),SYSDATETIME(),'"+startDeviceConfigurationID+"',null,"+str(startScreeningID)+",0,0,0,0,0,0,0,0,0,0,SYSDATETIME(),0,0,0,0,0,0,0,1);\n"
    deviceConfigsQueries.append(deviceConfigsTemplate1)
    evaluationCriteriaQueries.append(evaluationCriteriaTemplate1)
    startDeviceConfigGuid=str(UUID(int=UUID(startDeviceConfigGuid).int+1)).upper()
    startDeviceConfigurationID=str(UUID(int=UUID(startDeviceConfigurationID).int+1)).upper()
    startScreeningID+=1

f=open(config['folder']['output']+"/"+config['file']['output'],"w")
f.writelines(userQueries)
f.writelines(["----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n","\n"])
f.writelines(screeningQueries)
f.writelines(["----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n","\n"])
f.writelines(deviceConfigsQueries)
f.writelines(["----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n","\n"])
f.writelines(evaluationCriteriaQueries)
f.close()