import wx

import depot
import deviceHandler

import gui.guiUtils
import gui.toggleButton


## This handler is for stage positioner devices.
class PositionerHandler(deviceHandler.DeviceHandler):
    ## callbacks should fill in the following functions:
    # - moveAbsolute(axis, position): Move the axis to the
    #   given position, in microns.
    # - moveRelative(axis, delta): Move the axis by the specified
    #   delta, in microns.
    # - getPosition(axis): Get the position for the specified axis.
    # - setSafety(axis, value, isMax): Set the min or max soft safety limit.
    # Additionally, if the device is to be used in experiments, it must have:
    # - getMovementTime(axis, start, end): Get the amount of time it takes to 
    #   move from start to end and then stabilize.
    # - cleanupAfterExperiment(axis, isCleanupFinal): return the axis to to the
    #   state it was in prior to the experiment.
    # \param axis A numerical indicator of the axis (0 = X, 1 = Y, 2 = Z).
    # \param stepSizes List of step size increments for when the user wants
    #        to move using the keypad.
    # \param stepIndex Default index into stepSizes.
    # \param hardLimits A (minPosition, maxPosition) tuple indicating
    #        the device's hard motion limits.
    # \param softLimits Default soft motion limits for the device. Defaults
    #        to the hard limits.
    def __init__(self, name, groupName, isEligibleForExperiments, callbacks, 
            axis, stepSizes, stepIndex, hardLimits, softLimits = None):
        deviceHandler.DeviceHandler.__init__(self, name, groupName,
                isEligibleForExperiments, callbacks, 
                depot.STAGE_POSITIONER)
        self.axis = axis
        self.stepSizes = stepSizes
        self.stepIndex = stepIndex
        self.hardLimits = hardLimits
        if softLimits is None:
            softLimits = hardLimits
        # Cast to a list since we may need to modify these later.
        self.softLimits = list(softLimits)


    ## Handle being told to move to a specific position.
    def moveAbsolute(self, pos):
        if self.softLimits[0] <= pos <= self.softLimits[1]:
            self.callbacks['moveAbsolute'](self.axis, pos)
        else:
            raise RuntimeError("Tried to move %s " % (self.name) +
                    "outside soft motion limits (target %.2f, limits [%.2f, %.2f])" %
                    (pos, self.softLimits[0], self.softLimits[1]))


    ## Handle being told to move by a specific delta.
    def moveRelative(self, delta):
        target = self.callbacks['getPosition'](self.axis) + delta
        if self.softLimits[0] <= target <= self.softLimits[1]:
            self.callbacks['moveRelative'](self.axis, delta)
        else:
            raise RuntimeError("Tried to move %s " % (self.name) +
                    "outside soft motion limits (target %.2f, limits [%.2f, %.2f])" %
                    (target, self.softLimits[0], self.softLimits[1]))


    ## Handle being told to move by a step.
    # \param stepDirection Either -1 or +1, depending on direction of motion.
    def moveStep(self, stepDirection):
        self.moveRelative(stepDirection * self.stepSizes[self.stepIndex])


    ## Change the current step size by the provided delta (that is, change 
    # our index into self.stepSizes by the given delta). If we try to go off
    # the end of the list, then just stay at the current index.
    def changeStepSize(self, delta):
        newIndex = self.stepIndex + delta
        self.stepIndex = min(len(self.stepSizes) - 1, max(0, newIndex))


    ## Return the current step size.
    def getStepSize(self):
        return self.stepSizes[self.stepIndex]


    ## Retrieve the current position.
    def getPosition(self):
        return self.callbacks['getPosition'](self.axis)


    ## Simple getter.
    def getHardLimits(self):
        return self.hardLimits


    ## Simple getter.
    def getSoftLimits(self):
        return self.softLimits


    ## Set a soft limit, either min or max.
    def setSoftLimit(self, value, isMax):
        if isMax and value > self.hardLimits[1]:
            raise RuntimeError("Attempted to set soft motion limit of %s, exceeding our hard motion limit of %s" % (value, self.hardLimits[1]))
        elif not isMax and value < self.hardLimits[0]:
            raise RuntimeError("Attempted to set soft motion limit of %s, lower than our hard motion limit of %s" % (value, self.hardLimits[0]))
        self.callbacks['setSafety'](self.axis, value, isMax)
        self.softLimits[int(isMax)] = value

    
    ## Return the amount of time it'd take us to move the specified distance,
    # and the amount of time needed to stabilize after reaching that point.
    # Only called if this device is experiment-eligible.
    def getMovementTime(self, start, end):
        if self.isEligibleForExperiments:
            if (start < self.softLimits[0] or start > self.softLimits[1] or 
                    end < self.softLimits[0] or end > self.softLimits[1]):
                raise RuntimeError("Experiment tries to move [%s] from %.2f to %.2f, outside motion limits (%.2f, %.2f)" % (self.name, start, end, self.softLimits[0], self.softLimits[1]))
            return self.callbacks['getMovementTime'](self.axis, start, end)
        raise RuntimeError("Called getMovementTime on non-experiment-eligible positioner [%s]" % self.name)


    ## Do any necessary cleanup now that the experiment is over.
    def cleanupAfterExperiment(self, isCleanupFinal = True):
        if self.isEligibleForExperiments:
            return self.callbacks['cleanupAfterExperiment'](self.axis, isCleanupFinal)
