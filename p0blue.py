from joy import *

#class ShaveNHaircutPlan( Plan ):
  #"""
  #ShaveNHaircutPlan shows a simple example of sequential composition:
  #its behavior is to run the shave plan followed by the haircut plan.
  #"""
#  def __init__(self,app,shave,haircut,tail,*arg,**kw):
#    Plan.__init__(self,app,*arg,**kw)
#    self.shave = shave
#    self.haircut = haircut
#    self.tail = tail
    
#  def behavior( self ):
#    progress("Both: starting 'Shave' sequence")
#    yield self.shave
#    progress("Both: starting 'Haircut' sequence")
#    yield self.haircut    
 #   progress("Both: starting 'Tail' sequence")
 #   yield self.tail    
 #   progress("Both: done")
    
class ShaveNHaircutApp( JoyApp ):
  # Load both patterns from their CSV files
    LEFT = loadCSV("left.csv")
    RIGHT = loadCSV("right.csv")
    LEAP = loadCSV("leap.csv")

    def __init__(self,shaveSpec,hairSpec,tailSpec,*arg,**kw):
        JoyApp.__init__(self, *arg,**kw)
        self.shaveSpec = shaveSpec
        self.hairSpec = hairSpec
        self.tailSpec = tailSpec

    def onStart(self):
    
        self.leapplan = SheetPlan(self, self.LEAP, x=self.tailSpec, y=self.shaveSpec, z=self.hairSpec)
        self.leftplan = SheetPlan(self, self.LEFT, x=self.tailSpec, y=self.shaveSpec, z=self.hairSpec)
        self.rightplan = SheetPlan(self, self.RIGHT, x=self.tailSpec, y=self.shaveSpec, z=self.hairSpec)

        # give us start and stop messages; in your own code you can omit these 
        self.leapplan.onStart = lambda : progress("Leap: starting") 
        self.leapplan.onStop = lambda : progress("Leap: done")
        self.leftplan.onStart = lambda : progress("Left: starting")
        self.leftplan.onStop = lambda : progress("Left: done")
        self.rightplan.onStart = lambda : progress("Right: starting")
        self.rightplan.onStop = lambda : progress("Right: done") 
        #
        # Set up a ShaveNHaircutPlan using both of the previous plans
        #
        #self.both = ShaveNHaircutPlan(self, self.shaveplan, self.hairplan,self.tailplan)

    def onEvent(self,evt):
        if evt.type != KEYDOWN:
            return
    # assertion: must be a KEYDOWN event 
        elif evt.key == K_b:
            if ( not self.leapplan.isRunning() 
                and not self.leftplan.isRunning()
                and not self.rightplan.isRunning()
                ):
                self.leapplan.start()
        elif evt.key == K_l:
            if ( not self.leapplan.isRunning() 
                and not self.leftplan.isRunning()
                and not self.rightplan.isRunning()
                ):
                self.leftplan.start()
        elif evt.key == K_r:
            if ( not self.leapplan.isRunning() 
                and not self.leftplan.isRunning()
                and not self.rightplan.isRunning()
                ):
                self.rightplan.start()
        elif evt.key == K_z:
            if self.leapplan.isRunning():
                self.leapplan.stop()
            elif self.leftplan.isRunning():
                self.leftplan.stop()
            elif self.rightplan.isRunning():
                self.rightplan.stop()
            else:
                return
        elif evt.key == K_ESCAPE:
            self.stop()

if __name__=="__main__":
    robot = None
    scr = None
    args = list(sys.argv[1:])
    while args:
        arg = args.pop(0)
        if arg=='--mod-count' or arg=='-c':
            N = int(args.pop(0))
            robot = dict(count=N)
        elif arg=='--tail' or arg=='-t':
            shaveSpec = args.pop(0)
            hairSpec = args.pop(0)
            tailSpec = args.pop(0)
            if tailSpec[:1]==">": scr = {}

        elif arg=='--help' or arg=='-h':
            sys.stdout.write("""
                Usage: %s [options]
                This is used for team blue in P0
                When running, the demo uses the keyboard. The keys are:
                'l' -- turn left
                'r' -- turn right
                'b' -- leap forward
                'z' -- stop the current motion, if any
                'escape' -- exit program
                Options:      
                    --mod-count <number> | -c <number>
                    Search for specified number of modules at startup
                    --shave <spec> | -s <spec>
                    --haircut <spec> | -h <spec>
                    Specify the output setter to use for 'shave' (resp. 'haircut')
                    Typical <spec> values would be:
                    'Nx3C/@set_pos' -- send to position of CKBot servo module with ID 0x3C
                    NOTE: to use robot modules you MUST also specify a -c option
                    """ % sys.argv[0])
            sys.exit(1)
    # ENDS cmdline parsing loop
  
    app = ShaveNHaircutApp(shaveSpec,hairSpec,tailSpec,robot=robot,scr=scr)
    app.run()
