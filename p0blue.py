from joy import *

#@title: Blue Team Project Zero Code
#@authors: Mukai Wang, Ali Yassine, Anne Gu, Royce Chung
#@date: 1/29/2018
#@course: EECS 464 - Hands On Robotics
#
#Derived from shave and haircut demo
#Redesigned to working with 2018 Project 0 Blue Team Leaping robot
#Key terminology
#plan: method of performing function i.e. turning left, right, or moving foward
#leftPlan: method to turn left
#rightPlan: method to turn right
#leapPlan: method to leap foward
#onStart(): Overided method from JoyApp class that starts the code by loading the plans
#onEvent(): Overided method from JoyApp class that reads keyboard commands to run plans


class ProjectZeroApp( JoyApp ):
  # Load left, right, and leap motion patterns from their CSV files
    LEFT = loadCSV("left.csv")
    RIGHT = loadCSV("right.csv")
    LEAP = loadCSV("leap.csv")

  #Constructor for ProjectZeroApp. Initializes JoyApp instance	
    def __init__(self,rightSpec,leftSpec,leapSpec,*arg,**kw):
        JoyApp.__init__(self, *arg,**kw)
        self.rightSpec = rightSpec
        self.leftSpec = leftSpec
        self.leapSpec = leapSpec

  #Overide for onStart() function in JoyApp
  #Reads motion patterns and sorts plans into their appropriate plans
    def onStart(self):
  
  #Sorting done here  
        self.leapplan = SheetPlan(self, self.LEAP, x=self.leapSpec, y=self.rightSpec, z=self.leftSpec)
        self.leftplan = SheetPlan(self, self.LEFT, x=self.leapSpec, y=self.rightSpec, z=self.leftSpec)
        self.rightplan = SheetPlan(self, self.RIGHT, x=self.leapSpec, y=self.rightSpec, z=self.leftSpec)

  #Shows progress messages when a motion is called
  #Useful for debugging
        self.leapplan.onStart = lambda : progress("Leap: starting") 
        self.leapplan.onStop = lambda : progress("Leap: done")
        self.leftplan.onStart = lambda : progress("Left: starting")
        self.leftplan.onStop = lambda : progress("Left: done")
        self.rightplan.onStart = lambda : progress("Right: starting")
        self.rightplan.onStop = lambda : progress("Right: done") 
 
  #Overide for onEvent() function in JoyApp
  #Reads input from keyboard and runs plans based off what key was pressed
  #Can terminated program in case of emergency
    def onEvent(self,evt):
        if evt.type != KEYDOWN:
            return
  # Assertion: must be a KEYDOWN event 
    
  #If 'W' key is pressed down, run the leap plan
        elif evt.key == K_w:
            if ( not self.leapplan.isRunning() 
                and not self.leftplan.isRunning()
                and not self.rightplan.isRunning()
                ):
                self.leapplan.start()

  #If 'A' key is pressed down, run the left plan
        elif evt.key == K_a:
            if ( not self.leapplan.isRunning() 
                and not self.leftplan.isRunning()
                and not self.rightplan.isRunning()
                ):
                self.leftplan.start()

  #If 'D' key is pressed down, run the right plan
        elif evt.key == K_d:
            if ( not self.leapplan.isRunning() 
                and not self.leftplan.isRunning()
                and not self.rightplan.isRunning()
                ):
                self.rightplan.start()
  #If the escape key is pressed down, end the program
  #Overides all other commands, useful emergency switch
        elif evt.key == K_ESCAPE:
            self.stop()

  #If no keys are being pressed, keep the program running,
  #but stop all running plans
        else:
            if self.leapplan.isRunning():
                self.leapplan.stop()
            elif self.leftplan.isRunning():
                self.leftplan.stop()
            elif self.rightplan.isRunning():
                self.rightplan.stop()
            else:
                return

if __name__=="__main__":
    robot = None
    scr = None
    args = list(sys.argv[1:])
    while args:
        arg = args.pop(0)
        if arg=='--mod-count' or arg=='-c':
            N = int(args.pop(0))
            robot = dict(count=N)
        elif arg=='--assign-servo' or arg=='-s':
            rightSpec = args.pop(0)
            leftSpec = args.pop(0)
            leapSpec = args.pop(0)
            if leapSpec[:1]==">": scr = {}
        elif arg=='--help' or arg=='-h':
            sys.stdout.write("""
                Usage: %s [options]
                This is used for team blue in P0
                When running, the app uses the keyboard. The keys are:
                'a' -- turn left
                's' -- turn right
                'w' -- leap forward
                no key pressed -- stop the current motion, if any
                'escape' -- exit program
                Options:      
                    --mod-count <number> | -c <number>
                    Search for specified number of modules at startup
                    --assign-servo <spec> | -s <spec>
                    Specify which servo performs which functions.
		    In order of right, left, and leap servo on robot
                    Typical <spec> values would be:
                    'Nx0C/@set_pos Nx65/@set_pos Nx02/@set_pos' 
                    Where Nx0C is the right module, Nx65 is the left module, 
                    and  Nx02 is the leap Module
                    NOTE: to use robot modules you MUST also specify a -c option
                    """ % sys.argv[0])
            sys.exit(1)
    # ENDS cmdline parsing loop
  
    app = ProjectZeroApp(rightSpec,leftSpec,leapSpec,robot=robot,scr=scr)
    app.run()
