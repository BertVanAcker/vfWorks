from D5065experiments import RWSystem_BLDC_D5065


system = RWSystem_BLDC_D5065(name="D5065 system under study",INITIALIZED=True, CALIBRATED=False,monitorPeriod=0.1)

#-----------------------------------------------------------------------------------------------------------------------
#                                   VF reference
#-----------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------
#                                   EXPERIMENT 1
#-----------------------------------------------------------------------------------------------------------------------
experimentTime = 100    #100 sec
cmd = 100               #100% velocity
label = "nominal"       #nominal behavior of the system
system.experiment_constant_velocity(experimentTime=experimentTime,percentage=cmd)
