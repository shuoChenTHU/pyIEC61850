# -*- coding: utf-8 -*-
"""
Created on Sun Aug 22 22:44:01 2021

@author: chen, Morris
"""
import sys
import os

#sys.path.append(r"X:\GitLab_THU_SGFG\dockervirtualcls\libiec61850")
#sys.path.append(r"C:\ProgramData\Anaconda3\Lib\site-packages\libiec61850\python37")


sys.path.append("/work/")
listFile = os.listdir("/work/")
print("check files in working directory")
print(listFile)
os.environ["PATH"] = "/work/;" + os.environ["PATH"]

import iec61850 as iec
import time
import random
from datetime import datetime, timedelta, timezone
import calendar
#import numpy
#import csv
#import json
#import threading
#import logging


class gvar():
    # global counter
    gcount = 0
    # simulation time settings
    pf_time_obj = ""
    pf_timeset_start = ""
    pf_timeset_end = ""
    pf_list_timescale = ""
    pf_timeset_steps = 1.0
    pf_sim_set_flag = False
    # server settings and stats
    tcpPort = 61850
    hostname = "127.0.0.1"
    uptime_sec = 0
    uptime_min = 0
    uptime_h = 0
    start_time = 0
    current_time = 0
    intrvl_start = 0
    intrvl_duratn = 0.0
    intrvl_table = []
    int_avg_duratn = 0.0
    # Data Model
    iedServer = []
    iedModel = []
    iec_model_dict = {}
    iec_model_dict_callback = {}
    LD_iedModel = []
    app = []
    proj = []
    container_pvsys = []
    container_pvsys_callback = []
    container_load = []
    container_load_callback = []
    container_all_objects = []
#    container_loads = {}
    current_pfObjId = ''
    pvsys_list = []
    pvsys_PFOID_nr_dict = {}
    pvsys_PFOID_pfObj = {}
    pvsys_PFOID_list = []
    load_list = []
    load_PFOID_nr_dict = {}
    load_PFOID_pfObj = {}
    load_PFOID_list = []
    
    dictUpdateVal = []
    # csv vars
    csv_filename = ""
    
    IedModelName = "demoVirtualCLS"
    DeviceName = "demoProsumerXY"
    demoProsumerXY_mmxu1_f_current_val = 50
    demoProsumerXY_mmxu1_totw_current_val = 5000
    demoProsumerXY_mmxu1_totvar_current_val = 200
    demoProsumerXY_mmxu1_outwset_current_val = 1.0


def create_IED_model_device(DeviceName):    
    # Logical Device
    gvar.LD_iedModel = iec.LogicalDevice_create(DeviceName, gvar.iedModel)
    # LLN0
    LN_LLN0     = iec.LogicalNode_create("LLN0", gvar.LD_iedModel)
    # LLN0 - DOs / CDCs
    DO_LLN0_Beh     = iec.CDC_ENS_create("Beh", iec.toModelNode(LN_LLN0), 0)
    DA_LLN0_Beh_stVal = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_Beh), "stVal")
    DO_LLN0_Loc     = iec.CDC_ENS_create("Loc", iec.toModelNode(LN_LLN0), 0)
    DO_LLN0_Mod     = iec.CDC_ENC_create("Mod", iec.toModelNode(LN_LLN0), 0, 1)
    DA_LLN0_Mod_stVal = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_Mod), "stVal")
    DO_LLN0_NamPlt = iec.CDC_DPL_create("NamPlt", iec.toModelNode(LN_LLN0), 0)
    # LPHD1
    LN_LPHD1 = iec.LogicalNode_create("LPHD1", gvar.LD_iedModel)
    # LPHD1 - DOs / CDCs
    DO_LPHD1_PhyHealth = iec.CDC_ENS_create("PhyHealth", iec.toModelNode(LN_LPHD1), 0)
    DO_LPHD1_PhyNam = iec.CDC_DPL_create("PhyNam", iec.toModelNode(LN_LPHD1), 0)
    DO_LPHD1_Proxy = iec.CDC_SPS_create("Proxy", iec.toModelNode(LN_LPHD1), 0)


def get_UTC_timestamp_uint64():
    # Get current time and convert to uint64_t
    # Consider correct offset
    offset_summer_time = 7200000
    current_time = datetime.now()
    current_time_uint64_t = calendar.timegm(current_time.utctimetuple())*1000
    return current_time_uint64_t - offset_summer_time

def get_simulation_timestamp_uint64(simulationTime):
    offset_summer_time = 0
    current_time = datetime.strptime(simulationTime, '%Y-%m-%d %H:%M:%S.%f')
    current_time_uint64_t = calendar.timegm(current_time.utctimetuple())*1000
    return current_time_uint64_t - offset_summer_time


def create_IED_model_essential():
    setattr(gvar, "iedModel", 0)
    #setattr(gvar, 'ied_model_dict', {})
        
    IedModelName = gvar.IedModelName
    IedModelName = IedModelName + "_"
        
    gvar.iedModel = iec.IedModel_create(IedModelName)
    
    print("Auto generating IED model: %s" %(IedModelName))
    return


# Create IED server
def create_IED_server():
    gvar.iedServer = iec.IedServer_create(gvar.iedModel)
    print("IED server created")

def start_IED_server():
    iec.IedServer_start(gvar.iedServer, gvar.tcpPort)
    print("IED server started")
    return 
    
    
def create_demo_IED_model():
    '''
    Create LN (pvsys or load) from JSON tag
    '''
    # Def
    dictUpdateVal = dict()
#    dictUpdateVal["PF_obj"] = device
#    dictUpdateVal["PF_obj_name"] = device.loc_name
    
    PF_attr = []
    Iec_DA = []
    Iec_DO_name = []
    Iec_DA_mag = []
    Iec_DA_t = []
        
    # create_LN
    DeviceName = gvar.DeviceName
    #print('LN Name:', DeviceName)
#    linkPFIEC["Iec_obj_name"] = DeviceName
        
    
    SysTypPref = 'PV'
    LNDevInstance = '1'
    #print('Current LN Dev Instance:', LNDevInstance)
    
    LNType = "MMXU"
    LNInstance = int(LNDevInstance)-1
    LNName = SysTypPref + str(LNDevInstance) + "_" + LNType + str(LNInstance)
    LNgvarStr = DeviceName + "_LN_" + LNName	
    		
    LNgvar = setattr(gvar, LNgvarStr, 0)
    LNgvar = iec.LogicalNode_create(LNName, gvar.LD_iedModel)
    	
    # create_DS 
    DSgvarStr = DeviceName + "_DS_" + LNName	
    DSgvar = setattr(gvar, DSgvarStr, 0)
    DSgvar = iec.DataSet_create(DSgvarStr, LNgvar)	
    
    RCB_gvarStr = DeviceName + "_RP_" + LNName
    RCB_gvarStrID = RCB_gvarStr + "_01"
    RCB_gvar = setattr(gvar, RCB_gvarStr, 0)
    RCB_gvar =  iec.ReportControlBlock_create(RCB_gvarStr, LNgvar, RCB_gvarStrID, False, DSgvarStr , 1, 8, 0, 0, 10000)
    
    gvar.DSgvar = DSgvar
    gvar.DSgvarStr = DSgvarStr
    gvar.RCB_gvar = RCB_gvar
    gvar.RCB_gvarStr = RCB_gvarStr
    
    # Create Variables
    ### Create Ubb
    Value = "f"	  
    ValueType = "mag_f"
    ValueDataType = "mag.f"
    DA_t = 't'
    DOgvar = DeviceName + "_DO_"  + LNName + "_" + Value
    DAgvar = DeviceName + "_DA_"  + LNName + "_" + Value	+ "_" + ValueType
    DAgvar_t = DeviceName + "_DA_"  + LNName + "_" + Value	+ "_" + DA_t
    Iec_DO_name.append(DOgvar)
    
    
    localgvarDO = setattr(gvar, DOgvar, 0)
    localgvarDO = iec.CDC_MV_create(Value, iec.toModelNode(LNgvar), 0, False)
    localgvarDA = setattr(gvar, DAgvar, 0)
    localgvarDA = iec.ModelNode_getChild(iec.toModelNode(localgvarDO), ValueDataType)
    localgvarDA_t = iec.ModelNode_getChild(iec.toModelNode(localgvarDO), DA_t)
    
    PF_attr.append("m:u")
    Iec_DA.append(localgvarDA)
    Iec_DA_mag.append(0)
    Iec_DA_t.append(localgvarDA_t)
    setattr(gvar, "f_index", PF_attr.index("m:u"))
    
    #Add DataSet Entry
    DSentryMMS = LNName + "$MX$" + Value
    DSgvarEntryStr = DeviceName + "_DS_" + LNName + "_" + Value
    localgvarDSentry = setattr(gvar, DSgvarEntryStr, 0)
    localgvarDSentry = iec.DataSetEntry_create(DSgvar, DSentryMMS, 1, None)
    
    ### Create DO TotW
    Value = "TotW"	
    ValueType = "mag_f"
    ValueDataType = "mag.f"
    DOgvar = DeviceName + "_DO_"	+ LNName + "_" + Value
    DAgvar = DeviceName + "_DA_"  + LNName + "_" + Value	+ "_" + ValueType
    Iec_DO_name.append(DOgvar)
    	
    localgvarDO = setattr(gvar, DOgvar, 0)
    localgvarDO = iec.CDC_MV_create(Value, iec.toModelNode(LNgvar), 0, False)
    localgvarDA = setattr(gvar, DAgvar, 0)
    localgvarDA = iec.ModelNode_getChild(iec.toModelNode(localgvarDO), ValueDataType)
    localgvarDA_t = iec.ModelNode_getChild(iec.toModelNode(localgvarDO), DA_t)
    
    PF_attr.append("m:P:bus1")
    Iec_DA.append(localgvarDA)
    Iec_DA_mag.append(0)
    Iec_DA_t.append(localgvarDA_t)
    setattr(gvar, "p_tot_index", PF_attr.index("m:P:bus1"))
    
    #Add DataSet Entry
    DSentryMMS = LNName + "$MX$" + Value
    DSgvarEntryStr = DeviceName + "_DS_" + LNName + "_" + Value
    localgvarDSentry = setattr(gvar, DSgvarEntryStr, 0)
    localgvarDSentry = iec.DataSetEntry_create(DSgvar, DSentryMMS, 1, None)
    
    ### Create TotVar
    Value = "TotVar"	
    ValueType = "mag_f"
    ValueDataType = "mag.f"
    DOgvar = DeviceName + "_DO_"	+ LNName + "_" + Value
    DAgvar = DeviceName +"_DA_"  + LNName + "_" + Value	+ "_" + ValueType
    Iec_DO_name.append(DOgvar)
    	
    localgvarDO = setattr(gvar, DOgvar, 0)
    localgvarDO = iec.CDC_MV_create(Value, iec.toModelNode(LNgvar), 0, False)
    localgvarDA = setattr(gvar, DAgvar, 0)
    localgvarDA = iec.ModelNode_getChild(iec.toModelNode(localgvarDO), ValueDataType)
    localgvarDA_t = iec.ModelNode_getChild(iec.toModelNode(localgvarDO), DA_t)
    
    
    PF_attr.append("m:Q:bus1")
    Iec_DA.append(localgvarDA)
    Iec_DA_mag.append(0)
    Iec_DA_t.append(localgvarDA_t)
    setattr(gvar, "q_tot_index", PF_attr.index("m:Q:bus1"))
    
    #Add DataSet Entry
    DSentryMMS = LNName + "$MX$" + Value
    DSgvarEntryStr = DeviceName + "_DS_" + LNName + "_" + Value
    localgvarDSentry = setattr(gvar, DSgvarEntryStr, 0)
    localgvarDSentry = iec.DataSetEntry_create(DSgvar, DSentryMMS, 1, None)
    
    ######### DO for control ################################
    Value = "OutWSet"	
    ValueType = "setMag_f"
    ValueDataType = "setMag.f"
    DOgvar = DeviceName + "_DO_"	+ LNName + "_" + Value
    DAgvar = DeviceName + "_DA_"  + LNName + "_" + Value	+ "_" + ValueType
    Iec_DO_name.append(DOgvar)
    	
    localgvarDO = setattr(gvar, DOgvar, 0)
    localgvarDO = iec.CDC_ASG_create(Value, iec.toModelNode(LNgvar), iec.CDC_OPTION_UNIT, False)
    localgvarDA = setattr(gvar, DAgvar, 0)
    localgvarDA = iec.ModelNode_getChild(iec.toModelNode(localgvarDO), ValueDataType)
    
    PF_attr.append("Pmax_uc")
    Iec_DA.append(localgvarDA)
    Iec_DA_mag.append(0)
    setattr(gvar, "p_pv_max_index", PF_attr.index("Pmax_uc"))
    
    #Add DataSet Entry
    DSentryMMS = LNName + "$SP$" + Value
    DSgvarEntryStr = DeviceName + "_DS_" + LNName + "_" + Value
    localgvarDSentry = setattr(gvar, DSgvarEntryStr, 0)
    localgvarDSentry = iec.DataSetEntry_create(DSgvar, DSentryMMS, 1, None)


    # write initial IED data model
    dictUpdateVal["PF_attr"] = PF_attr  
    dictUpdateVal["Iec_DA"] = Iec_DA
    dictUpdateVal["Iec_DO_name"] = Iec_DO_name
    dictUpdateVal["Iec_DA_mag"] = Iec_DA_mag
    dictUpdateVal["Iec_DA_t"] = Iec_DA_t
        
    #print(linkPFIEC)
    print("LD created: {}".format(DeviceName))
    return (dictUpdateVal)

def set_init_vals():
    gvar.demoProsumerXY_mmxu1_f_mag_f = 50
    gvar.demoProsumerXY_mmxu1_totvar_mag_f = 200
    gvar.demoProsumerXY_mmxu1_totw_mag_f = 5000
    return

def set_rndm_vals():
    gvar.demoProsumerXY_mmxu1_f_mag_f  += random.randint(-100,100)/1000
    gvar.demoProsumerXY_mmxu1_totvar_mag_f += random.randint(-100,100)/1000
    gvar.demoProsumerXY_mmxu1_totw_mag_f += random.randint(-3000,3000)/10000
    return

def set_SP_init():
    gvar.demoProsumerXY_mmxu1_outwset_setmag_f = 1.0

    
def update_SP_init():
    dictUpdateVal = gvar.container_pvsys[0] # container has only one element with index = 0
    Iec_DA = dictUpdateVal['Iec_DA']
    Iec_DA_mag = dictUpdateVal['Iec_DA_mag']
    gvar.demoProsumerXY_mmxu1_outwset_setmag_f = 1.0
    iec.IedServer_updateFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA[gvar.p_pv_max_index]), 1.0)
    Iec_DA_mag[gvar.p_pv_max_index] = 1.000

    
def update_IED_attr(srvTimeSource = 'simulation'):
    dictUpdateVal = gvar.container_pvsys[0] # container has only one element with index = 0
    Iec_DA = dictUpdateVal['Iec_DA']
    Iec_DA_mag = dictUpdateVal['Iec_DA_mag']
    Iec_DA_t = dictUpdateVal['Iec_DA_t']
    iec.IedServer_updateFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA[gvar.f_index]), gvar.demoProsumerXY_mmxu1_f_mag_f)
    iec.IedServer_updateFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA[gvar.q_tot_index]), gvar.demoProsumerXY_mmxu1_totvar_mag_f)      
    iec.IedServer_updateFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA[gvar.p_tot_index]), gvar.demoProsumerXY_mmxu1_totw_mag_f)        
    # update all timestamps
#    simulationTime = datetime.fromtimestamp(gvar.pf_list_timescale[gvar.gcount]).strftime('%Y-%m-%d %H:%M:%S.%f')
    if srvTimeSource == 'absolute':
        iec.IedServer_updateUTCTimeAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA_t[gvar.q_tot_index]), get_UTC_timestamp_uint64())
        iec.IedServer_updateUTCTimeAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA_t[gvar.f_index]), get_UTC_timestamp_uint64())
        iec.IedServer_updateUTCTimeAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA_t[gvar.p_tot_index]), get_UTC_timestamp_uint64())
    
    gvar.demoProsumerXY_mmxu1_f_current_val = iec.IedServer_getFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA[gvar.f_index]))
    gvar.demoProsumerXY_mmxu1_totw_current_val = iec.IedServer_getFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA[gvar.p_tot_index]))
    gvar.demoProsumerXY_mmxu1_totvar_current_val = iec.IedServer_getFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA[gvar.q_tot_index]))
    gvar.demoProsumerXY_mmxu1_outwset_current_val = iec.IedServer_getFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA[gvar.p_pv_max_index]))
    
    return

def get_SP_control():
    dict_pvsys = gvar.container_pvsys[0]
    Iec_DA = dict_pvsys['Iec_DA']
    Iec_DA_mag = dict_pvsys['Iec_DA_mag']
    outwset_server = Iec_DA_mag[gvar.p_pv_max_index]
    outwset_client = iec.IedServer_getFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA[gvar.p_pv_max_index])) 
    print('SP value in the IED server: {}'.format(outwset_server))
    print('SP value from client: {}'.format(outwset_client))
    if outwset_server != outwset_client:
        print('************************************')
        print('***  control command received ******')
        print('************************************')
        print("OutWSet changed: {} -> {}".format(Iec_DA_mag[gvar.p_pv_max_index], iec.IedServer_getFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA[gvar.p_pv_max_index]))))
        Iec_DA_mag[gvar.p_pv_max_index] = outwset_client
        gvar.container_pvsys[0]['Iec_DA_mag'][gvar.p_pv_max_index] = outwset_client
        gvar.demoProsumerXY_mmxu1_outwset_setmag_f = outwset_client
    else:
        pass
    iec.IedServer_updateFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA[gvar.p_pv_max_index]), gvar.demoProsumerXY_mmxu1_outwset_setmag_f)
    gvar.demoProsumerXY_mmxu1_outwset_current_val = iec.IedServer_getFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(Iec_DA[gvar.p_pv_max_index]))
    return

def server_routine():
    listNameLN = ['MMXU']
    create_IED_model_essential()
    create_IED_model_device(gvar.DeviceName)
    for NameLN in listNameLN:                  
        dictUpdateVal = create_demo_IED_model()
        gvar.container_all_objects.append(dictUpdateVal)
        gvar.container_pvsys.append(dictUpdateVal)
    
    create_IED_server()
    start_IED_server()
    set_init_vals()
    set_SP_init()
    update_SP_init()
    
    print('#################################')
    print("Server running")
    
    print('init measurements:')
    print('TotW: {} W; TotVAR: {} VAr; f: {} Hz'.format(gvar.demoProsumerXY_mmxu1_totw_mag_f, gvar.demoProsumerXY_mmxu1_totvar_mag_f, gvar.demoProsumerXY_mmxu1_f_mag_f))
       
    print('init measurements IEC 61850:')
    print('TotW: {} W; TotVAR: {} VAr; f: {} Hz'.format(gvar.demoProsumerXY_mmxu1_totw_current_val, gvar.demoProsumerXY_mmxu1_totvar_current_val, gvar.demoProsumerXY_mmxu1_f_current_val))

    print('init setpoint value:')
    print('OutWSet: {}'.format(gvar.demoProsumerXY_mmxu1_outwset_current_val))
    print('#################################')

    print('Verif DO in the IED data model')     
    print(gvar.container_pvsys)
    
    print('#################################')
    print('verify LD in the IED model')
    print('IED LD count: {}'.format(iec.IedModel_getLogicalDeviceCount(gvar.iedModel)))
    
    print('#################################')
    print('Verif Data Sets in the IED data model') 
    obj_dataset = iec.IedModel_lookupDataSet(gvar.iedModel, '{}_{}/PV1_MMXU0${}'.format(gvar.IedModelName, gvar.DeviceName, gvar.DSgvarStr))    
    if obj_dataset != None:
        print('Found data set with name: {}'.format(obj_dataset.name))
    else:
        print('No data set available')
    print('Data set size: {}'.format(iec.DataSet_getSize(obj_dataset)))
    
#    obj_firstEntry = iec.DataSet_getFirstEntry(obj_dataset)
#    obj_firstEntry_value = obj_firstEntry.value
#    obj_firstEntry_mms = iec.MmsValue_getElement(obj_firstEntry_value,1)
#    obj_nextEntry = iec.DataSetEntry_getNext(obj_firstEntry)
#    obj_nextEntry_value = obj_nextEntry.value
#    obj_nextEntry_mms = iec.MmsValue_getElement(obj_nextEntry_value,1)
    
#    print('#################################') 
#    print('Verif ReportControlBLocks in the IED data model')   
#    print(gvar.RCB_gvar)

    time.sleep(10) 
    i= 0
    while i<60*24*365:
       gvar.intrvl_start = time.time()
       print('#################################')
       print("Server running")
       # get_MMS_vals()
       
       print('update measurement values')
       set_rndm_vals()
       update_IED_attr("absolute")
       #uptime()
       #self.stat_uptime.set("{:0>2}:{:0>2}:{:05.2f}".format(int(gvar.uptime_h),int(gvar.uptime_min),gvar.uptime_sec))
       # if self.var_intrvl.get() == 1:
       #    intrvl_measurement(self)
       print('current measurements:')
       print('TotW: {} W; TotVAR: {} VAr; f: {} Hz'.format(gvar.demoProsumerXY_mmxu1_totw_mag_f, gvar.demoProsumerXY_mmxu1_totvar_mag_f, gvar.demoProsumerXY_mmxu1_f_mag_f))
       
       print('current measurements IEC 61850:')
       print('TotW: {} W; TotVAR: {} VAr; f: {} Hz'.format(gvar.demoProsumerXY_mmxu1_totw_current_val, gvar.demoProsumerXY_mmxu1_totvar_current_val, gvar.demoProsumerXY_mmxu1_f_current_val))

       print('current setpoint value:')
       print('OotWSet: {}'.format(gvar.demoProsumerXY_mmxu1_outwset_current_val))
       print('#################################')
             
       get_SP_control()
       
       time.sleep(10) 
       i+=1


server_routine()