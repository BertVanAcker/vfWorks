from __future__ import print_function
from vfworks.utils.auxiliary import *
import odrive
from odrive.enums import *
import time
import math
from pycaret.anomaly import *
import serial



class RWSystem_BLDC_D5065():

    def __init__(self,name,VERBOSE=True,INITIALIZED=False,CALIBRATED=False,monitorPeriod=0.5,DEPLOYED=True,SERIAL=False):
        self.name = name
        self.VERBOSE = VERBOSE
        self.vel_request = 0
        self.maximumVelocity = 30       #turns/s

        # ------------Monitoring-------------------
        self.monitorActive = False
        self.timeStamps = []
        self.powerMeasurements=[]
        self.rpmMeasurements = []
        self.busVoltageMeasurements = []
        self.runtimeMeasurements = {"power": 0.0, "rpm": 0.0, "busVoltage": 0.0, "velocityCommand": 0.0, "temperature": 0.0}
        # current measurements
        self.timestamp = 0.0
        self.power = 0.0
        self.rpm = 0.0
        self.busVoltage = 0.0
        self.velocityCommand = 0.0
        self.max_anomaly_score = 0.0
        self.value = 1
        self.runtimeSpecifications = []
        if DEPLOYED:
            #----------Odrive initialization-----------------
            if not INITIALIZED:
                self.mydrive = self.initBLDC()
            else:
                self.mydrive = odrive.find_any()

            #----------System monitoring-----------------
            self.monitorPeriod = monitorPeriod
            self.t_monitor = perpetualTimer(self.monitorPeriod,self.monitor)

            # ----------Odrive calibration-----------------
            if not CALIBRATED:
                self.calibrateBLDC()

        if SERIAL:
            #---------serial connections for forwarding data to serial ------------
            self.serialPort = serial.Serial('COM6', 115200)

        #-------anomaly detection components---------------
        self.model = None
        self.models = [] # list of models for redundancy
        self.ANOMALYDETECTORLOADED = False




    def initBLDC(self):
        # Find a connected ODrive (this will block until you connect one)
        print("finding an odriveExperiment...")
        my_drive = odrive.find_any()

        #drive settings for BLDC D5065 270KV
        odrv = my_drive
        odrv.config.dc_bus_overvoltage_trip_level = 25
        odrv.config.dc_bus_undervoltage_trip_level = 10.5
        odrv.config.dc_max_positive_current = math.inf
        odrv.config.dc_max_negative_current = -math.inf
        odrv.config.brake_resistor0.enable = True
        odrv.config.brake_resistor0.resistance = 2
        odrv.axis0.config.motor.motor_type = MotorType.HIGH_CURRENT
        odrv.axis0.config.motor.pole_pairs = 7
        odrv.axis0.config.motor.torque_constant = 0.030629629629629628
        odrv.axis0.config.motor.current_soft_max = 65
        odrv.axis0.config.motor.current_hard_max = 85
        odrv.axis0.config.motor.calibration_current = 10
        odrv.axis0.config.motor.resistance_calib_max_voltage = 2
        odrv.axis0.config.calibration_lockin.current = 10
        odrv.axis0.motor.motor_thermistor.config.enabled = True
        odrv.axis0.motor.motor_thermistor.config.r_ref = 10000
        odrv.axis0.motor.motor_thermistor.config.beta = 3435
        odrv.axis0.motor.motor_thermistor.config.temp_limit_lower = 110
        odrv.axis0.motor.motor_thermistor.config.temp_limit_upper = 130
        odrv.axis0.controller.config.control_mode = ControlMode.VELOCITY_CONTROL
        odrv.axis0.controller.config.input_mode = InputMode.PASSTHROUGH
        odrv.axis0.controller.config.vel_limit = 30
        odrv.axis0.controller.config.vel_limit_tolerance = 2
        odrv.axis0.config.torque_soft_min = -math.inf
        odrv.axis0.config.torque_soft_max = math.inf
        odrv.can.config.protocol = Protocol.NONE
        odrv.axis0.config.enable_watchdog = False
        odrv.inc_encoder0.config.enabled = True
        odrv.axis0.config.load_encoder = EncoderId.INC_ENCODER0
        odrv.axis0.config.commutation_encoder = EncoderId.INC_ENCODER0
        odrv.inc_encoder0.config.cpr = 20480
        odrv.axis0.commutation_mapper.config.use_index_gpio = True
        odrv.axis0.pos_vel_mapper.config.use_index_gpio = True
        odrv.config.gpio10_mode = GpioMode.DIGITAL
        odrv.axis0.pos_vel_mapper.config.index_gpio = 10
        odrv.axis0.pos_vel_mapper.config.index_offset = 0
        odrv.axis0.pos_vel_mapper.config.index_offset_valid = True
        odrv.axis0.commutation_mapper.config.index_gpio = 10
        odrv.config.enable_uart_a = False
        odrv.axis0.motor.motor_thermistor.config = False

        return my_drive

    def calibrateBLDC(self):
        # Calibrate motor and wait for it to finish
        if self.VERBOSE:print("starting calibration...")
        self.mydrive.axis0.requested_state = AxisState.FULL_CALIBRATION_SEQUENCE           #AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        while self.mydrive.axis0.current_state != AxisState.IDLE:                    #AXIS_STATE_IDLE:
            time.sleep(0.1)
        time.sleep(15)


    def setVelocity(self,percentage):
        if self.VERBOSE:print("Change velocity to "+ percentage.__str__()+"%")
        self.vel_request = float(percentage/100)*self.maximumVelocity
        self.mydrive.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
        self.mydrive.axis0.controller.config.input_mode = InputMode.VEL_RAMP
        self.mydrive.axis0.controller.input_vel = self.vel_request


    def start(self):
        # enable closed-loop control + ramped velocity
        self.mydrive.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
        self.mydrive.axis0.controller.config.input_mode = InputMode.VEL_RAMP
        # start monitoring
        self.monitorActive = True
        if not self.t_monitor.isAlive():
            self.t_monitor.start()
    def stop(self):
        self.mydrive.axis0.requested_state = AxisState.IDLE
        #stop monitoring
        self.monitorActive = False


    #---------------------------EXPERIMENTS--------------------------
    def experiment_constant_velocity(self,experimentTime=10,percentage=100):

        # Flush measurements
        self.flushMeasurements()
        # Start monitoring and activate close-loop speed control
        self.start()
        #set constant velocity
        self.vel_request = float(percentage / 100) * self.maximumVelocity
        self.mydrive.axis0.controller.input_vel = self.vel_request
        self.runtimeMeasurements["velocityCommand"] = percentage
        #sleep experiment time
        time.sleep(experimentTime)
        #disable closed-loop control to finish experiment
        self.stop()
        # format the measurements and return
        measurements = [self.timeStamps,self.powerMeasurements,self.rpmMeasurements,self.busVoltageMeasurements]
        return measurements

    def experiment_velocity_sweep(self,experimentTime=10, percentage=100):
        self.flushMeasurements()
        self.start()

        for i in range(percentage+1):
            self.vel_request = float(i / 100) * self.maximumVelocity
            self.mydrive.axis0.controller.input_vel = self.vel_request
            self.runtimeMeasurements["velocityCommand"] = i

            time.sleep(experimentTime/percentage)
        self.stop()
        measurements = [self.timeStamps,self.powerMeasurements,self.rpmMeasurements,self.busVoltageMeasurements]
        return measurements

    def experiment_square_wave_velocity(self,experimentTime=10,percentage=100, period=1):
        # Flush measurements
        self.flushMeasurements()
        # Start monitoring and activate close-loop speed control
        self.start()
        # set constant velocity
        curr_time = 0
        self.vel_request = 0
        while curr_time < experimentTime:
            if self.vel_request == 0:
                self.vel_request = float(percentage / 100) * self.maximumVelocity
                self.runtimeMeasurements["velocityCommand"] = percentage
            else:
                self.vel_request = 0
                self.runtimeMeasurements["velocityCommand"] = self.vel_request
            self.mydrive.axis0.controller.input_vel = self.vel_request
            time.sleep(period)
            curr_time += period
        # disable closed-loop control to finish experiment
        self.stop()
        # format the measurements and return
        measurements = [self.timeStamps, self.powerMeasurements, self.rpmMeasurements, self.busVoltageMeasurements]
        return measurements



    #---------------------------MONITORING--------------------------
    def monitor(self):
        if self.monitorActive:
            # timestamps
            self.timestamp = self.timestamp + self.monitorPeriod

            #measurements
            self.power = self.mydrive.axis0.motor.alpha_beta_controller.power
            self.rpm = self.mydrive.encoder_estimator0.vel_estimate*60
            self.busVoltage = self.mydrive.vbus_voltage

            #local storage
            self.timeStamps.append(self.timestamp)
            self.powerMeasurements.append(self.power)
            self.rpmMeasurements.append(self.rpm)
            self.busVoltageMeasurements.append(self.busVoltage)

            #-------- PERFORM ANOMALY DETECTION-------------
            if self.ANOMALYDETECTORLOADED:
                self.anomalyDetection(self)     #TODO:METHOD OVERLOADING NEEDED!!

    def flushMeasurements(self):
        """Flush measurement to start new experiment"""
        self.timestamp = 0.0
        self.timeStamps = []
        self.powerMeasurements = []
        self.rpmMeasurements = []
        self.busVoltageMeasurements = []
        self.runtimeMeasurements = {"power": 0.0, "rpm": 0.0, "busVoltage": 0.0, "velocityCommand": 0.0,
                                    "temperature": 0.0}
    # ----------------------MONITORS-------------------------
    def runtimeMonitor(self):
        for spec in self.runtimeSpecifications:
            if spec.feature in self.runtimeMeasurements:
                if not spec.value.validate_point(self.runtimeMeasurements[spec.feature]):
                    print("WARNING: " + spec.feature + " is out of range")

    def addRuntimeSpecification(self,spec):
        self.runtimeSpecifications.append(spec)

    # ----------------------ANOMALY DETECTION----------------------
    def anomalyDetection(self):
        print("Warning: anomaly detection function not implemented")

    def loadAnomalyDetectionModel(self, model,type="pycaret"):
        if type == "pycaret":
            self.model = load_model(model)
            self.ANOMALYDETECTORLOADED = True
        elif type == "torch":
            self.model = model
            self.models.append(model)
            self.ANOMALYDETECTORLOADED = True
        else:
            self.model = None
            self.ANOMALYDETECTORLOADED = False




