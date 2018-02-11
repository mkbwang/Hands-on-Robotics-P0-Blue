# This code contains manual and autonomous control for the Green Team robot
# Manual control is default
# In manual mode, the arrow keys control the motion of the robot
# Left and Right keys control the x-direction and up and down keys control the y-direction
# To enter autonomous mode, press “a”

from sensorPlanTCP import SensorPlanTCP
from P1Simulator import Simulator
from joy import JoyApp, progress, Plan
from joy.decl import *
from waypointShared import WAYPOINT_HOST, APRIL_DATA_PORT
from socket import (
  socket, AF_INET,SOCK_DGRAM, IPPROTO_UDP, error as SocketError,
  )
import ckbot.logical as l
import syncmx

class Autonomous ( Plan ):
  def __init__(self, app, robot):
    Plan.__init__(self, app)
    self.robot = robot

  def onStart( self ):
    self.gantry = syncmx.ServoWrapperMX(self, self.robot.at.gantry)
    self.rightWheel = syncmx.ServoWrapperMX(self, self.robot.at.rightWheel)
    self.leftWheel = syncmx.ServoWrapperMX(self, self.robot.at.rightWheel)

    self.gantry._set_motor()
    self.rightWheel._set_motor()
    self.leftWheel._set_motor()

    self.startingRot = self.convToDegrees(self.gantry.get_ang())
    self.rotCount = 0
    self.scanning = True
    self.scanDirection = 1 # 1 for right, -1 for left
    self.halfRot = False
    self.plusMinus = 10
    self.lookForThreshold = False

    self.startingBodyRot = self.convToDegrees(self.rightWheel.get_ang())
    self.moveDirection = 1 # 1 for up, -1 for down
    self.bodyRotCount = 0
    self.totalBodyRotCount = 0

  def keep360(self, num):
    if num > 360:
      num -= 360
    if num < 0:
      num += 360
    return num

  def convToDegrees(self, num):
    if num >= 0:
      return num * 360
    elif num < 0:
      return num * 360 + 360

  def countBodyRotations(self):
    currentAng = self.convToDegrees(self.rightWheel.get_ang())
    print(currentAng)  

    if not self.lookForThreshold and not (self.startingBodyRot - (self.plusMinus) <= currentAng < self.startingBodyRot + (self.plusMinus)):
      self.lookForThreshold = True

    if self.lookForThreshold and self.startingBodyRot - (self.plusMinus) <= currentAng < self.startingBodyRot + (self.plusMinus):
      self.lookForThreshold = False
      return 1
    return 0

  def countRotations(self):
    currentAng = self.convToDegrees(self.gantry.get_ang())
    print(self.startingRot - (self.plusMinus), currentAng, self.startingRot + (self.plusMinus))

    if not self.lookForThreshold and not (self.startingRot - (self.plusMinus) <= currentAng < self.startingRot + (self.plusMinus)):
      self.lookForThreshold = True

    if self.lookForThreshold and self.startingRot - (self.plusMinus) <= currentAng < self.startingRot + (self.plusMinus):
      self.lookForThreshold = False
      return 1
    return 0

  def gantryScan(self):
    self.robot.at.gantry.set_torque(self.scanDirection*.2)
    self.rotCount += self.countRotations()
    print(self.rotCount)
    if (self.rotCount == 6 and self.scanDirection == 1) or (self.rotCount == 6 and self.scanDirection == -1):
      self.scanning = False
      self.rotCount = 0
      self.scanDirection *= -1
      self.startingRot = self.gantry.get_ang()

  def move(self):
    self.robot.at.rightWheel.set_torque(-.1*self.moveDirection)
    self.robot.at.leftWheel.set_torque(.1*self.moveDirection)
    self.bodyRotCount += self.countBodyRotations()
    self.totalBodyRotCount += self.bodyRotCount
    if self.bodyRotCount == 1:
      self.bodyRotCount = 0
      self.robot.at.rightWheel.set_torque(0)
      self.robot.at.leftWheel.set_torque(0)
      self.scanning = True
    #check if we should go the other way next time
    if self.totalBodyRotCount == 5:
      self.moveDirection *= -1
      self.totalBodyRotCount = 0

  def onEvent( self, evt ):
    while (True):
      if self.scanning:
        self.gantryScan()
      else:
        self.robot.at.gantry.set_torque(0)
        #self.scanning = True
        self.move()

    if evt.type == KEYDOWN and evt.key == K_SPACE:
      self.robot.at.gantry.set_torque(0)

    return True

class RobotSimulatorApp( JoyApp ):
  """Concrete class RobotSimulatorApp <<singleton>>
     A JoyApp which runs the Simulator robot model in simulation, and
     emits regular simulated tagStreamer message to the desired waypoint host.
     
     Used in conjection with waypointServer.py to provide a complete simulation
     environment for Project 1
  """    
  def __init__(self,wphAddr=WAYPOINT_HOST,*arg,**kw):
    JoyApp.__init__( self,
      confPath="$/cfg/JoyApp.yml",
      robot = dict(
        count=3,
        names={0x21 : 'gantry', 0x52 : 'rightWheel', 0x4D : 'leftWheel',},
        required=[0x21,0x52,0x4D],
        fillMissing=True),
      *arg, **kw
      ) 
    self.srvAddr = (wphAddr, APRIL_DATA_PORT)
    
  def onStart( self ):
    # Set up socket for emitting fake tag messages
    s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    s.bind(("",0))
    self.sock = s
    # Set up the sensor receiver plan
    self.sensor = SensorPlanTCP(self,server=self.srvAddr[0])
    self.sensor.start()
    self.robSim = Simulator(fn=None)
    self.timeForStatus = self.onceEvery(1)
    self.timeForLaser = self.onceEvery(1/15.0)
    self.timeForFrame = self.onceEvery(1/20.0)
    progress("Using %s:%d as the waypoint host" % self.srvAddr)
    self.T0 = self.now

    self.auto = Autonomous(self, self.robot)
    
  def showSensors( self ):
    ts,f,b = self.sensor.lastSensor
    if ts:
      progress( "Sensor: %4d f %d b %d" % (ts-self.T0,f,b)  )
    else:
      progress( "Sensor: << no reading >>" )
    ts,w = self.sensor.lastWaypoints
    if ts:
      progress( "Waypoints: %4d " % (ts-self.T0) + str(w))
    else:
      progress( "Waypoints: << no reading >>" )
  
  def emitTagMessage( self ):
    """Generate and emit and update simulated tagStreamer message"""
    self.robSim.refreshState()
    # Get the simulated tag message
    msg = self.robSim.getTagMsg()
    # Send message to waypointServer "as if" we were tagStreamer
    self.sock.sendto(msg, self.srvAddr)
    
  def onEvent( self, evt ):
    # periodically, show the sensor reading we got from the waypointServer
    if self.timeForStatus(): 
      self.showSensors()
      progress( self.robSim.logLaserValue(self.now) )
      # generate simulated laser readings
    elif self.timeForLaser():
      self.robSim.logLaserValue(self.now)
    # update the robot and simulate the tagStreamer
    # if self.timeForFrame(): 
    #   self.emitTagMessage()

    if evt.type == KEYUP:
      if evt.key == K_UP:
        self.robot.at.rightWheel.set_torque(0)
        self.robot.at.leftWheel.set_torque(0)
        return progress("(say) End Move forward")
      elif evt.key == K_DOWN:
        self.robot.at.rightWheel.set_torque(0)
        self.robot.at.leftWheel.set_torque(0)
        return progress("(say) End Move back")
      elif evt.key == K_LEFT:
        self.robot.at.gantry.set_torque(0)
        return progress("(say) End Move Left")
      elif evt.key == K_RIGHT:
        self.robot.at.gantry.set_torque(0)
        return progress("(say) End Move Right")

    if evt.type == KEYDOWN:
      if evt.key == K_UP:
        self.robot.at.rightWheel.set_torque(-.1)
        self.robot.at.leftWheel.set_torque(.1)
        # self.robSim.move(0.5)
        return progress("(say) Move forward")
      elif evt.key == K_DOWN:
        self.robot.at.rightWheel.set_torque(.1)
        self.robot.at.leftWheel.set_torque(-.1)
        return progress("(say) Move back")
      elif evt.key == K_LEFT:
        self.robot.at.gantry.set_torque(-.2)
        return progress("(say) Move Left")
      elif evt.key == K_RIGHT:
        self.robot.at.gantry.set_torque(.2)
        return progress("(say) Move Right")
      elif evt.key == K_a:
        self.auto.start()

      elif evt.key == K_SPACE:
        self.robSim.autoMoving = True
        return progress("(say) Auto")
    # Use superclass to show any other events
      else:
        return JoyApp.onEvent(self,evt)
    return # ignoring non-KEYDOWN events

if __name__=="__main__":
  print """
  Running the robot simulator

  Listens on local port 0xBAA (2986) for incoming waypointServer
  information, and also transmits simulated tagStreamer messages to
  the waypointServer. 
  """
  import sys
  if len(sys.argv)>1:
      app=RobotSimulatorApp(wphAddr=sys.argv[1], cfg={'windowSize' : [160,120]})
  else:
      app=RobotSimulatorApp(wphAddr=WAYPOINT_HOST, cfg={'windowSize' : [160,120]})
  app.run()

