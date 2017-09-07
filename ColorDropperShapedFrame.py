#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Copyright (c) 2017 Edward Greig
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.

"""
Color dropper that follows the mouse pointer.

OnClick functionality will have to be implemented by the user.

License: MIT

"""

import wx

if 'phoenix' in wx.version():
    wx.RegionFromBitmap = wx.Region
    wx.EmptyBitmap = wx.Bitmap

def GetComplementaryColor(hexStr):
    """Returns complementary RGB color

    Example Usage:

        >>> GetComplementaryColor('#FFFFFF')
        '#000000'

    """
    if hexStr[0] == '#':
        hexStr = hexStr[1:]
    rgb = (hexStr[0:2], hexStr[2:4], hexStr[4:6])
    compColor = '#'
    for a in rgb:
        compColor += '%02x' % (255 - int(a, 16))
    ## print('complementaryColor = ', compColor)
    if hexStr.isupper():
        return compColor.upper()  # Retain case.
    return compColor


class ColorDotShapedFrame(wx.Frame):
    def __init__(self, parent=None,
                 frameColor='#000000', maskColor='#FFFFFF', dotColor='#FFFFFF', id=wx.ID_ANY, title='',
                 pos=wx.DefaultPosition, size=(96, 96),
                 style=wx.FRAME_SHAPED | wx.NO_BORDER | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP,
                 name='frame'):
        wx.Frame.__init__(self, parent, id, title, pos, size, style, name)

        # self.SetDoubleBuffered(True)

        self.frameColor = frameColor
        self.maskColor = maskColor
        self.dotColor = dotColor
        self.font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)

        # Create the bitmap and set the frame shape.
        self.MakeColorDropperBitmap()
        wx.CallAfter(self.SetWindowShape)

        # Set up the timer which will move the text and paint the screen.
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, source=self.timer)
        self.timer.Start(10)

        # Make sure we are using our custom paint handler.
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)


    def MakeColorDropperBitmap(self):
        dc = wx.MemoryDC(wx.EmptyBitmap(*self.GetClientSize()))
        dc_SetBrush = dc.SetBrush
        # dc_SetPen = dc.SetPen
        maskColor = self.maskColor
        dc_SetBrush(wx.Brush(maskColor))
        dc.Clear()
        # dc.DrawRectangle(x=0, y=0, width=self.Size[0], height=self.Size[1])

        w, h = self.GetClientSize()
        frameColor = self.frameColor
        dc_SetBrush(wx.Brush(frameColor))
        # compFrameColor = GetComplementaryColor(frameColor)
        # dc.SetPen(wx.Pen(compFrameColor))
        dc.SetPen(wx.Pen(frameColor))
        minWH = min(w, h)
        maxWH = max(w, h)
        minWH2 = min(w, h)//2
        maxWH2 = max(w, h)//2
        dc.DrawCircle(x=w//2, y=h//2, radius=minWH2)
        if w > h:
            dc.DrawRectangle(x=maxWH2-minWH2, y=minWH2, width=minWH2, height=minWH2)
        elif w < h:
            dc.DrawRectangle(x=0, y=maxWH2, width=minWH2, height=minWH2+1)
        else:
            dc.DrawRectangle(x=0, y=maxWH2, width=minWH2, height=minWH2)

        bmp = dc.GetAsBitmap((0, 0, w, h))
        bmp.SetMaskColour(maskColor)
        mask = wx.Mask(bmp, maskColor)
        bmp.SetMask(mask)
        self.bmp = bmp

        # wx.CallAfter(self.SetWindowShape)

    def DrawColorDot(self, dc):
        dc_SetBrush = dc.SetBrush
        dc_SetPen = dc.SetPen
        w, h = self.GetClientSize()
        # minWH = min(w, h)
        # maxWH = max(w, h)
        minWH2 = min(w, h)//2
        # maxWH2 = max(w, h)//2

        # Draw the color dot
        dotcolor = self.dotColor
        framecolor = self.frameColor
        compDotColor = GetComplementaryColor(dotcolor)
        compFrameColor = GetComplementaryColor(framecolor)

        dc_SetBrush(wx.Brush(compFrameColor))
        dc_SetPen(wx.Pen(compFrameColor))
        dc.DrawCircle(x=w//2+1, y=h//2+1, radius=minWH2//4*3)

        # dc_SetBrush(wx.Brush('#000000'))
        # dc_SetPen(wx.Pen('#000000'))
        # dc.DrawCircle(x=w//2+1, y=h//2+1, radius=minWH2//4*3)

        dc_SetBrush(wx.Brush(dotcolor))
        dc_SetPen(wx.Pen(dotcolor))
        # dc.SetPen(wx.Pen(framecolor))
        dc.DrawCircle(x=w//2, y=h//2, radius=minWH2//4*3)
        # Draw the color string on the colordot
        fnt = self.font
        fnt.SetPixelSize((minWH2//6, minWH2//4))
        dc.SetFont(fnt)
        tw, th, td, te = dc.GetFullTextExtent(dotcolor, fnt)
        dc.SetTextForeground(framecolor)
        dc.DrawText(dotcolor, x=w//2-tw//2, y=h//2-th//2)
        dc.SetTextForeground(compDotColor)
        dc.DrawText(dotcolor, x=w//2-tw//2-1, y=h//2-th//2-1)

    def SetWindowShape(self):
        # Use the bitmap's mask to determine the region.
        r = wx.RegionFromBitmap(self.bmp)
        self.SetShape(r)

    def OnEraseBackground(self, event):
        pass  # Reduce flicker with BufferedPaintDC.

    def OnPaint(self, event):
        # Draw the bitmap on the screen.
        ## dc = wx.PaintDC(self)
        # dc = wx.BufferedPaintDC(self)
        dc = wx.GCDC(wx.BufferedPaintDC(self))
        gc_obj = dc.GetGraphicsContext()
        gc_obj.SetAntialiasMode(1)
        dc.DrawBitmap(self.bmp, 0, 0, useMask=True)
        self.DrawColorDot(dc)

    def OnTimer(self, event):
        x, y = wx.GetMousePosition()
        self.SetPosition((x + 4, y - self.Size[1] - 4))
        sdc = wx.ScreenDC()
        color = sdc.GetPixel(x, y)
        # print(color)
        hexcolor = color.GetAsString(wx.C2S_HTML_SYNTAX)
        # print(hexcolor)
        self.dotColor = hexcolor
        self.Refresh()
        del sdc

    def __del__(self):
        self.timer.Stop()
        del self.timer

if __name__ == "__main__":
    app = wx.App()
    frame = ColorDotShapedFrame()
    frame.Centre()
    frame.Show(True)
    # frame.SetTransparent(200)
    app.MainLoop()

