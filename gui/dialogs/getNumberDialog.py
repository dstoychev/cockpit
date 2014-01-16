import gui.guiUtils

import wx


## This class allows for prompting the user for a number, similar to
# wx.GetNumberFromUser except that we allow for floating point values as well.
class GetNumberDialog(wx.Dialog):
    def __init__(self, parent, title, prompt, default):
        wx.Dialog.__init__(self, parent, -1, title)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.value = gui.guiUtils.addLabeledInput(
                parent = self, sizer = mainSizer,
                label = prompt,
                defaultValue = str(default),
                size = (70, -1), minSize = (150, -1), 
                shouldRightAlignInput = True, border = 3, 
                controlType = wx.TextCtrl)

        buttonsBox = wx.BoxSizer(wx.HORIZONTAL)

        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        cancelButton.SetToolTipString("Close this window")
        buttonsBox.Add(cancelButton, 0, wx.ALL, 5)
        
        startButton = wx.Button(self, wx.ID_OK, "Okay")
        buttonsBox.Add(startButton, 0, wx.ALL, 5)
        
        mainSizer.Add(buttonsBox, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 3)

        self.SetSizer(mainSizer)
        self.SetAutoLayout(True)
        mainSizer.Fit(self)


    def getValue(self):
        return self.value.GetValue()

        
def getNumberFromUser(parent, title, prompt, default):
    dialog = GetNumberDialog(parent, title, prompt, default)
    dialog.ShowModal()
    return dialog.getValue()
    
