from __future__ import print_function

from math import ceil # For rounding
from datetime import datetime
import re

class SamModel(object):
    """Represents a particular Atmel SAM part number
    
    Provides methods to generate an Eeschema symbol for the part.
    """
    def __init__(self, partNumber):
        series = partNumber[:6]
        if not series == "SAMD21":
            raise Exception("Don't know about series " + series)

        self.partNumber = partNumber

    def __str__(self):
        return self.partNumber

    def __repr__(self):
        return "SamModel(\"" + self.partNumber + "\")"

    def _arrangePins(self):
        "Make lists of (pin number, description) tuples for L and R of symbol"

        pins = getPinout(self.partNumber)
    
        # Build lists of (pin number, pin name) tuples for pins that go
        # on the left or right of the symbol.
        leftSide = []
        rightSide = []
    
        # Right side is IO, left is everything else (mainly power)
        isPort = re.compile(r"P[A-Z][0-9]{2}")
        for number in pins:
            if isPort.match(pins[number]):
                rightSide.append( (number, pins[number]) )
            else:
                leftSide.append( (number, pins[number]) )
    
        # Sort left pins roughly by function; misc, power, ground
        # TODO: Maybe another group for analog power pins?
        leftNotPower = []
        leftPower = []
        leftGround = []
        for item in leftSide:
            if "VDD" in item[1]:
                leftPower.append(item)
            elif "GND" in item[1]:
                leftGround.append(item)
            else:
                leftNotPower.append(item)
    
        leftSorted = sorted(leftNotPower, key = lambda x: x[1])
        leftSorted += [None]    # Put a gap between groups
        leftSorted += sorted(leftPower, key = lambda x: x[1])
        leftSorted += [None]
        leftSorted += sorted(leftGround, key = lambda x: x[1])
    
        # Sort pins by port name (eg PA02, PA03...) rather than pin number
        rightSide = sorted(rightSide, key = lambda x: x[1])
        rightExpanded = []
        for pin in rightSide:
            # Eeschema can't handle spaces in pin names, so join with slashes.
            expanded = "/".join(expandPortPin(self.partNumber, pin[1]) + [pin[1]])
            rightExpanded.append( (pin[0], expanded) )

        return leftSorted, rightExpanded

    def canAlias(self, other):
        "Returns True iff self and other have same schematic symbols."

        ourPn, otherPn = self.partNumber, other.partNumber

        #               Flash Size           Temp Grade   Carrier
        mask = ourPn[:7] + ".." + ourPn[9:12] + "."     +   "T?"

        if re.search(mask, otherPn):
            return True
        else:
            return False

    def outputLibSymbol(self, aliases):
        "Generates the .lib description as bytearray, refers to list aliases"
    
        # From Kicad Library Conventions
        # https://github.com/KiCad/kicad-library/wiki/Kicad-Library-Convention
        pinLength = 100 
        pinTextSize = 40
        fieldTextSize = 50
        grid = 100
    
        # Comment header
        out =  "#\n"
        out += "# " + self.partNumber + "\n"
        out += "# Automatically generated " + str(datetime.now()) + "\n"
        out += "#\n"
    
        leftPins, rightPins = self._arrangePins()
    
        # Find the longest text between left and right
        maxLenLeft, maxLenRight = 0, 0
        for p in leftPins:
            if p is not None:
                maxLenLeft = max(maxLenLeft, len(p[1]))
        for p in rightPins:
            maxLenRight = max(maxLenRight, len(p[1]))
    
        requiredWidth = (maxLenLeft + maxLenRight) * pinTextSize + 2 * pinLength
    
        # Figure out width and height to put all the pins on grid intersections
        width = 2 * grid * ceil(requiredWidth / (2 * grid))
    
        numPinsTall = max(len(leftPins), len(rightPins))
        height = 2 * grid * ceil(grid * numPinsTall / (2 * grid))
    
        top = grid * ceil(height / (2 * grid) )
    
        # Start the definition
        # TODO: Unsure what the F and N are for - copied from existing library
        out += "DEF " + self.partNumber + " U 0 40  Y Y 1 F N\n"
    
        # Required fields
        fieldTextY = top + fieldTextSize + grid
        packageStr = getPackage(self.partNumber) 
    
        #TODO: Unsure what the trailing Ns are for
        out += 'F0 "U" %d %d 50 H V L CNN\n' % \
               (-width / 2, fieldTextY)
        out += 'F1 "' + self.partNumber + '" %d %d 50 H V C CNN\n' % \
               (0, fieldTextY)
        out += 'F2 "' + packageStr + '" %d %d 50 H V R CIN\n' % \
               (width / 2, fieldTextY)
        out += 'F3 "" 0 0 50 H V C CNN\n'
    
        if len(aliases) > 0:
            out += "ALIAS " + " ".join([al.partNumber for al in aliases]) + "\n"
    
        # Start drawing with the bounding box around the chip
        boxBottom = top - grid * max(len(leftPins), len(rightPins))
        out += "DRAW\n"
        out += "S %d %d %d %d 0 1 10 f\n" % ( -width / 2 + pinLength, top + grid,
                                              width / 2 - pinLength, boxBottom )
    
        # ...and the pins!
        row = 0
        for p in leftPins:
            xPos = -width / 2
            yPos = top - row * grid
    
            if p is None:     # Gap between groups of pins
                row += 1
                continue
            elif "VDD" in p[1] or "GND" in p[1]:
                pinType = "W" # Power in
            elif "RESET" in p[1]:
                pinType = "I" # Input
            else:
                pinType = "B" # Bidirectional
    
            params= (p[1], p[0], xPos, yPos, pinLength, pinTextSize, pinTextSize, pinType)
            out += "X %s %s %d %d %d R %d %d 1 1 %s\n" % params
            row += 1
    
        row = 0
        for p in rightPins:
            xPos = width / 2
            yPos = top - row * grid
    
            params = (p[1], p[0], xPos, yPos, pinLength, pinTextSize, pinTextSize)
            out += "X %s %s %d %d %d L %d %d 1 1 B\n" % params
            row += 1
        out += "ENDDRAW\n"
    
        out += "ENDDEF\n"
    
        return out.encode("UTF-8")
    
    def getDatasheetUrlString(self):
        "Returns URL to download datasheet"
        return "http://www.atmel.com/images/atmel-42181-sam-d21_datasheet.pdf"

    def getOverviewString(self):
        "Returns a high level description for the .dcm file"
        return "ARM 32bit Microcontroller 48MHz CortexM0+"

    def getPackagingString(self):
        "Returns 'Tape and Reel' or 'Tray' depending on packaging of partNumber"
        if self.partNumber[-1] == "T":
            return "Tape and Reel"
        else:
            return "Tray"

    def getArmFamilyString(self):
        "Returns ARM family name for specified part eg 'CortexM0+'"
        return "CortexM0+"

    def getSpeedString(self):
        "Returns max CPU speed for specified part eg '48MHz'"
        return "48MHz"

    def outputDcm(self):
        "Returns section of an Eeschema .dcm file as UTF-8 encoded bytearray"

        partNumber = self.partNumber #TODO: Get rid of this

        out = "#\n"
        out += "$CMP " + partNumber + "\n"
    
        brief = [
                getPackage(partNumber),
                getFlashString(partNumber) + " Flash",
                getRamString(partNumber) + " RAM",
                self.getSpeedString(),
                self.getArmFamilyString(),
                self.getPackagingString(),
                ]
        out += "D " + ", ".join(brief) + "\n"
        out += "K " + self.getOverviewString() + "\n"
        out += "F " + self.getDatasheetUrlString() + "\n"
        out += "$ENDCMP\n"

        return out.encode("UTF-8")

def expandPortPin(partNumber, pin):
    "Takes a partNumber and pin and returns list of strings with port functions"

    series = partNumber[:6]
    if not series == "SAMD21":
        raise Exception("expandPortPin() called on an unknown series")

    functionDict = {
            "PA00" : ["EXTINT0", "SERCOM1_PAD0", "TCC2_WO0"],
            "PA01" : ["EXTINT1", "SERCOM1_PAD1", "TCC2_WO1"],
            "PA02" : ["EXTINT2", "AIN0", "Y0", "VOUT"],
            "PA03" : ["EXTINT3", "ADC_DAC_VREFA", "AIN1", "Y1"],
            "PA04" : ["EXTINT4", "ADC_VREFB", "AIN4", "AIN0", "Y2", "SERCOM0_PAD0", "TCC0_WO0"],
            "PA05" : ["EXTINT5", "AIN5", "AIN1", "Y3", "SERCOM0_PAD1", "TCC0_WO1"],
            "PA06" : ["EXTINT6", "AIN6", "AIN2", "Y4", "SERCOM0_PAD2", "TCC1_WO0"],
            "PA07" : ["EXTINT7", "AIN7", "AIN3", "Y5", "SERCOM0_PAD3", "TCC1_WO1", "I2S_SD0"],
            "PA08" : ["NMI", "AIN16", "X0", "SERCOM0_PAD0", "SERCOM2_PAD0", "TCC0_WO0", "TCC1_WO2", "I2S_SD1"],
            "PA09" : ["EXTINT9", "AIN17", "X1", "SERCOM0_PAD1", "SERCOM2_PAD1", "TCC0_WO1", "TCC1_WO3", "I2S_MCK0"],
            "PA10" : ["EXTIN10", "AIN18", "X2", "SERCOM0_PAD2", "SERCOM2_PAD2", "TCC1_WO0", "TCC0_WO2", "I2S_SCK0", "GCLK_IO4"],
            "PA11" : ["EXTINT11", "AIN19", "X3", "SERCOM0_PAD3", "SERCOM2_PAD3", "TCC1_WO1", "TCC0_WO3", "I2S_FS0", "GCLK_IO5"],
            "PA12" : ["EXTINT12", "SERCOM2_PAD0", "SERCOM4_PAD0", "TCC2_WO0", "TCC0_WO6", "AC_CMP0"],
            "PA13" : ["EXTINT13", "SERCOM2_PAD1", "SERCOM4_PAD1", "TCC2_WO1", "TCC0_WO7", "AC_CMP1"],
            "PA14" : ["EXTINT14", "SERCOM2_PAD2", "SERCOM4_PAD2", "TC3_WO0", "TCC0_WO4", "GCLK_IO0"],
            "PA15" : ["EXTINT15", "SERCOM2_PAD3", "SERCOM4_PAD3", "TC3_WO1", "TCC0_WO5", "GCLK_IO1"],
            "PA16" : ["EXTINT0", "X4", "SERCOM1_PAD0", "SERCOM3_PAD0", "TCC2_WO0", "TCC0_WO6", "GCLK_IO2"],
            "PA17" : ["EXTINT1", "X5", "SERCOM1_PAD1", "SERCOM3_PAD1", "TCC2_WO1", "TCC0_WO7", "GCLK_IO3"],
            "PA18" : ["EXTINT2", "X6", "SERCOM1_PAD2", "SERCOM3_PAD2", "TC3_WO0", "TCC0_WO2", "AC_CMP0"],
            "PA19" : ["EXTINT3", "X7", "SERCOM1_PAD3", "SERCOM3_PAD3", "TC3_WO1", "TCC0_WO3", "I2S_SD0", "AC_CMP1"],
            "PA20" : ["EXTINT4", "X8", "SERCOM5_PAD2", "SERCOM3_PAD2", "TC7_WO0", "TCC0_WO6", "I2S_SCK0", "GCLK_IO4"],
            "PA21" : ["EXTINT5", "X9", "SERCOM5_PAD3", "SERCOM3_PAD3", "TC7_WO1", "TCC0_WO7", "I2S_FS0", "GCLK_IO5"],
            "PA22" : ["EXTINT6", "X10", "SERCOM3_PAD0", "SERCOM5_PAD0", "TC4_WO0", "TCC0_WO4", "GCLK_IO6"],
            "PA23" : ["EXTINT7", "X11", "SERCOM3_PAD1", "SERCOM5_PAD1", "TC4_WO1", "TCC0_WO5", "USB_SOF", "GCLK_IO7"],
            "PA24" : ["EXTINT12", "SERCOM3_PAD2", "SERCOM5_PAD2", "TC5_WO0", "TCC1_WO2", "USB_DM"],
            "PA25" : ["EXTINT13", "SERCOM3_PAD3", "SERCOM5_PAD3", "TC5_WO1", "TCC1_WO3", "USB_DP"],
            "PA27" : ["EXTINT15", "GCLK_IO0"],
            "PA28" : ["EXTINT8", "GCLK_IO0"],
            "PA30" : ["EXTINT10", "SERCOM1_PAD2", "TCC1_WO0", "SWCLK", "GCLK_IO0"],
            "PA31" : ["EXTINT11", "SERCOM1_PAD3", "TCC1_WO1", "SWDIO"],
            "PB00" : ["EXTINT0", "AIN8", "Y6", "SERCOM5_PAD2", "TC7_WO0"],
            "PB01" : ["EXTINT1", "AIN9", "Y7", "SERCOM5_PAD3", "TC7_WO1"],
            "PB02" : ["EXTINT2", "AIN10", "Y8", "SERCOM5_PAD0", "TC6_WO0"],
            "PB03" : ["EXTINT3", "AIN11", "Y9", "SERCOM5_PAD1", "TC6_WO1"],
            "PB04" : ["EXTINT4", "AIN12", "Y10"],
            "PB05" : ["EXTINT5", "AIN13", "Y11"],
            "PB06" : ["EXTINT6", "AIN14", "Y12"],
            "PB07" : ["EXTINT7", "AIN15", "Y13"],
            "PB08" : ["EXTINT8", "AIN2", "Y14", "SERCOM4_PAD0", "TC4_WO0"],
            "PB09" : ["EXTINT9", "AIN3", "Y15", "SERCOM4_PAD1", "TC4_WO1"],
            "PB10" : ["EXTINT10", "SERCOM4_PAD2", "TC5_WO0", "TCC0_WO4", "I2S_MCK1", "GLCK_IO4"],
            "PB11" : ["EXTINT11", "SERCOM4_PAD3", "TC5_WO1", "TCC0_WO5", "TCC0_WO5", "I2S_SCK1", "GCLK_IO5"],
            "PB12" : ["EXTINT12", "X12", "SERCOM4_PAD0", "TC4_WO0", "TCC0_WO6", "I2S_FS1", "GCLK_IO6"],
            "PB13" : ["EXTINT13", "X13", "SERCOM4_PAD1", "TC4_WO1", "TCC0_WO7", "GCLK_IO7"],
            "PB14" : ["EXTINT14", "X14", "SERCOM4_PAD2", "TC5_WO0", "GCLK_IO0"],
            "PB15" : ["EXTINT15", "X15", "SERCOM4_PAD3", "TC5_WO1", "GCLK_IO1"],
            "PB16" : ["EXTINT0", "SERCOM5_PAD0", "TC6_WO0", "TCC0_WO4", "I2S_SD1", "GCLK_IO2"],
            "PB17" : ["EXTINT1", "SERCOM5_PAD1", "TC6_WO1", "TCC0_WO5", "I2S_MCK0", "GCLK_IO3"],
            "PB22" : ["EXTINT6", "SERCOM5_PAD2", "TC7_WO0", "GCLK_IO0"],
            "PB23" : ["EXTINT7", "SERCOM5_PAD3", "TC7_WO1", "GCLK_IO1"],
            "PB30" : ["EXTINT14", "SERCOM5_PAD0", "TCC0_WO0", "TCC1_WO2"],
            "PB31" : ["EXTINT15", "SERCOM5_PAD1", "TCC0_WO1", "TCC1_WO3"],
            }

    return functionDict[pin]

def getPinout(partNumber):
    """Returns a dict of pin to brief description mappings.

    Keys are strings, because some packages use pin numbers, and others use
    coordinates.  Descriptions are terse, and are meant to be expanded via
    expandPortPin().
    """

    series = partNumber[:6]
    if not series == "SAMD21":
        raise Exception("getPinout() called on an unknown series")

    package = getPackage(partNumber)
    briefPackage = package[-2:] + '-'

    if "TQFP" in package or "QFN" in package:
        briefPackage += "quad"
    else:
        briefPackage += "grid"
    
    pinouts = { "32-quad" :
                  {
                      "1" : "PA00",
                      "2" : "PA01",
                      "3" : "PA02",
                      "4" : "PA03",
                      "5" : "PA04",
                      "6" : "PA05",
                      "7" : "PA06",
                      "8" : "PA07",
                      "9" : "VDDANA",
                      "10" : "GND",
                      "11" : "PA08",
                      "12" : "PA09",
                      "13" : "PA10",
                      "14" : "PA11",
                      "15" : "PA14",
                      "16" : "PA15",
                      "17" : "PA16",
                      "18" : "PA17",
                      "19" : "PA18",
                      "20" : "PA19",
                      "21" : "PA22",
                      "22" : "PA23",
                      "23" : "PA24",
                      "24" : "PA25",
                      "25" : "PA27",
                      "26" : "~RESET~",
                      "27" : "PA28",
                      "28" : "GND",
                      "29" : "VDDCORE",
                      "30" : "VDDIN",
                      "31" : "PA30",
                      "32" : "PA31",
                  },
                "32-grid" :
                  {
                      "A1" : "PA00",
                      "A2" : "PA01",
                      "A3" : "GNDANA",
                      "A4" : "VDDANA",
                      "A5" : "PA06",
                      "A6" : "VDDIO",
                      "B1" : "PA30",
                      "B2" : "PA31",
                      "B3" : "PA02",
                      "B4" : "PA04",
                      "B5" : "PA07",
                      # B6 is a key
                      "C1" : "VDDCORE",
                      "C2" : "VDDIN",
                      "C3" : "PA03",
                      "C4" : "PA05",
                      "C5" : "PA08",
                      "C6" : "PA10",
                      "D1" : "GND",
                      "D2" : "PA28",
                      "D3" : "GND",
                      "D4" : "PA11",
                      "D5" : "PA09",
                      "D6" : "GND",
                      "E1" : "~RESET~",
                      "E2" : "PA27",
                      "E3" : "PA22",
                      "E4" : "PA17",
                      "E5" : "PA16",
                      "E6" : "PA14",
                      "F1" : "PA25",
                      "F2" : "PA24",
                      "F3" : "PA23",
                      "F4" : "PA19",
                      "F5" : "PA18",
                      "F6" : "PA15",
                  },
                "48-quad" :
                  {
                      "1" : "PA00",
                      "2" : "PA01",
                      "3" : "PA02",
                      "4" : "PA03",
                      "5" : "GNDANA",
                      "6" : "VDDANA",
                      "7" : "PB08",
                      "8" : "PB09",
                      "9" : "PA04",
                      "10" : "PA05",
                      "11" : "PA06",
                      "12" : "PA07",
                      "13" : "PA08",
                      "14" : "PA09",
                      "15" : "PA10",
                      "16" : "PA11",
                      "17" : "VDDIO",
                      "18" : "GND",
                      "19" : "PB10",
                      "20" : "PB11",
                      "21" : "PA12",
                      "22" : "PA13",
                      "23" : "PA14",
                      "24" : "PA15",
                      "25" : "PA16",
                      "26" : "PA17",
                      "27" : "PA18",
                      "28" : "PA19",
                      "29" : "PA20",
                      "30" : "PA21",
                      "31" : "PA22",
                      "32" : "PA23",
                      "33" : "PA24",
                      "34" : "PA25",
                      "35" : "GND",
                      "36" : "VDDIO",
                      "37" : "PB22",
                      "38" : "PB23",
                      "39" : "PA27",
                      "40" : "~RESET~",
                      "41" : "PA28",
                      "42" : "GND",
                      "43" : "VDDCORE",
                      "44" : "VDDIN",
                      "45" : "PA30",
                      "46" : "PA31",
                      "47" : "PB02",
                      "48" : "PB03",
                  },
                "48-grid" : # WLCSP45 package
                  {
                      "A2"  : "PA27",
                      "A4"  : "PA28",
                      "A6"  : "GND",
                      "A8"  : "VDDCORE",
                      "A10" : "VDDIN",
                      "A12" : "PB02",
                      "B1"  : "PA25",
                      "B3"  : "VDDIO",
                      "B5"  : "~RESET~",
                      "B7"  : "PA30",
                      "B9"  : "PA31",
                      "B11" : "PB03",
                      "B13" : "PA01",
                      "C2"  : "PA24",
                      "C4"  : "GND",
                      "C6"  : "PA22",
                      "C8"  : "PA03",
                      "C10" : "PA02",
                      "C12" : "PA00",
                      "D1"  : "PA21",
                      "D3"  : "PA23",
                      "D5"  : "PA16",
                      "D7"  : "PA12",
                      "D9"  : "PB08",
                      "D11" : "PB04",
                      "D13" : "GNDANA",
                      "E2"  : "PA20",
                      "E4"  : "PA19",
                      "E6"  : "PA09",
                      "E8"  : "PA06",
                      "E10" : "PB09",
                      "E12" : "VDDANA",
                      "F1"  : "PA18",
                      "F3"  : "PA17",
                      "F5"  : "PA13",
                      "F7"  : "PA11",
                      "F9"  : "PA08",
                      "F11" : "PA05",
                      "F13" : "PA04",
                      "G2"  : "PA15",
                      "G4"  : "PA14",
                      "G6"  : "GND",
                      "G8"  : "VDDIO",
                      "G10" : "PA10",
                      "G12" : "PA07",
                  },
                "64-quad" :
                  {
                      "1" : "PA00",
                      "2" : "PA01",
                      "3" : "PA02",
                      "4" : "PA03",
                      "5" : "PB04",
                      "6" : "PB05",
                      "7" : "GNDANA",
                      "8" : "VDDANA",
                      "9" : "PB06",
                      "10" : "PB07",
                      "11" : "PB08",
                      "12" : "PB09",
                      "13" : "PA04",
                      "14" : "PA05",
                      "15" : "PA06",
                      "16" : "PA07",
                      "17" : "PA08",
                      "18" : "PA09",
                      "19" : "PA10",
                      "20" : "PA11",
                      "21" : "VDDIO",
                      "22" : "GND",
                      "23" : "PB10",
                      "24" : "PB11",
                      "25" : "PB12",
                      "26" : "PB13",
                      "27" : "PB14",
                      "28" : "PB15",
                      "29" : "PA12",
                      "30" : "PA13",
                      "31" : "PA14",
                      "32" : "PA15",
                      "33" : "GND",
                      "34" : "VDDIO",
                      "35" : "PA16",
                      "36" : "PA17",
                      "37" : "PA18",
                      "38" : "PA19",
                      "39" : "PB16",
                      "40" : "PB17",
                      "41" : "PA20",
                      "42" : "PA21",
                      "43" : "PA22",
                      "44" : "PA23",
                      "45" : "PA24",
                      "46" : "PA25",
                      "47" : "GND",
                      "48" : "VDDIO",
                      "49" : "PB22",
                      "50" : "PB23",
                      "51" : "PA27",
                      "52" : "~RESET~",
                      "53" : "PA28",
                      "54" : "GND",
                      "55" : "VDDCORE",
                      "56" : "VDDIN",
                      "57" : "PA30",
                      "58" : "PA31",
                      "59" : "PB30",
                      "60" : "PB31",
                      "61" : "PB00",
                      "62" : "PB01",
                      "63" : "PB02",
                      "64" : "PB03",
                    },
                "64-grid" :
                    {
                      "A1" : "PB02",
                      "A2" : "PB01",
                      "A3" : "VDDIN",
                      "A4" : "VDDCORE",
                      "A5" : "GND",
                      "A6" : "PA28",
                      "A7" : "PB23",
                      "A8" : "PB22",
                      "B1" : "PA00",
                      "B2" : "PB00",
                      "B3" : "PB31",
                      "B4" : "PA31",
                      "B5" : "PA30",
                      "B6" : "~RESET~",
                      "B7" : "PA27",
                      "B8" : "VDDIO",
                      "C1" : "PA01",
                      "C2" : "PB03",
                      "C3" : "PA02",
                      "C4" : "PB30",
                      "C5" : "PA21",
                      "C6" : "PA22",
                      "C7" : "PA23",
                      "C8" : "GND",
                      "D1" : "GNDANA",
                      "D2" : "PB04",
                      "D3" : "PA03",
                      "D4" : "PB05",
                      "D5" : "PB17",
                      "D6" : "PA20",
                      "D7" : "PB16",
                      "D8" : "PA25",
                      "E1" : "VDDANA",
                      "E2" : "PB08",
                      "E3" : "PB07",
                      "E4" : "PB06",
                      "E5" : "PB11",
                      "E6" : "PB15",
                      "E7" : "PA19",
                      "E8" : "PA24",
                      "F1" : "PA04",
                      "F2" : "PA05",
                      "F3" : "PA10",
                      "F4" : "PB09",
                      "F5" : "PB12",
                      "F6" : "PA12",
                      "F7" : "PA18",
                      "F8" : "PA17",
                      "G1" : "PA07",
                      "G2" : "PA06",
                      "G3" : "PA11",
                      "G4" : "PB10",
                      "G5" : "PB13",
                      "G6" : "PA13",
                      "G7" : "PA17",
                      "G8" : "VDDIO",
                      "H1" : "PA08",
                      "H2" : "PA09",
                      "H3" : "VDDIO",
                      "H4" : "GND",
                      "H5" : "PB14",
                      "H6" : "PA14",
                      "H7" : "PA15",
                      "H8" : "GND",
                    },
              }
    return pinouts[briefPackage]

def knownSamParts():
    "Returns a list of all Atmel SAM parts we can generate symbols for"

    # This is just copy-paste-regex'ed from the datasheet - tried the
    # algorithmic way, but exceptions started looking tedious.
    partNumbers = [
            "SAMD21E15A-AU", "SAMD21E15A-AUT", 
            "SAMD21E15A-AF", "SAMD21E15A-AFT", 
            "SAMD21E15A-MU", "SAMD21E15A-MUT", 
            "SAMD21E15A-MF", "SAMD21E15A-MFT", 
            "SAMD21E16A-AU", "SAMD21E16A-AUT", 
            "SAMD21E16A-AF", "SAMD21E16A-AFT", 
            "SAMD21E16A-MU", "SAMD21E16A-MUT", 
            "SAMD21E16A-MF", "SAMD21E16A-MFT", 
            "SAMD21E17A-AU", "SAMD21E17A-AUT", 
            "SAMD21E17A-AF", "SAMD21E17A-AFT", 
            "SAMD21E17A-MU", "SAMD21E17A-MUT", 
            "SAMD21E17A-MF", "SAMD21E17A-MFT", 
            "SAMD21E18A-AU", "SAMD21E18A-AUT", 
            "SAMD21E18A-AF", "SAMD21E18A-AFT", 
            "SAMD21E18A-MU", "SAMD21E18A-MUT", 
            "SAMD21E18A-MF", "SAMD21E18A-MFT", 
            "SAMD21E15B-AU", "SAMD21E15B-AUT", 
            "SAMD21E15B-AF", "SAMD21E15B-AFT", 
            "SAMD21E15B-MU", "SAMD21E15B-MUT", 
            "SAMD21E15B-MF", "SAMD21E15B-MFT", 
            "SAMD21E16B-AU", "SAMD21E16B-AUT", 
            "SAMD21E16B-AF", "SAMD21E16B-AFT", 
            "SAMD21E16B-MU", "SAMD21E16B-MUT", 
            "SAMD21E16B-MF", "SAMD21E16B-MFT", 
                             "SAMD21E16B-UUT", 
            "SAMD21G15A-AU", "SAMD21G15A-AUT", 
            "SAMD21G15A-AF", "SAMD21G15A-AFT", 
            "SAMD21G15A-MU", "SAMD21G15A-MUT", 
            "SAMD21G15A-MF", "SAMD21G15A-MFT", 
            "SAMD21G16A-AU", "SAMD21G16A-AUT", 
            "SAMD21G16A-AF", "SAMD21G16A-AFT", 
            "SAMD21G16A-MU", "SAMD21G16A-MUT", 
            "SAMD21G16A-MF", "SAMD21G16A-MFT", 
            "SAMD21G17A-AU", "SAMD21G17A-AUT", 
            "SAMD21G17A-AF", "SAMD21G17A-AFT", 
            "SAMD21G17A-MU", "SAMD21G17A-MUT", 
            "SAMD21G17A-MF", "SAMD21G17A-MFT", 
                             "SAMD21G17A-UUT", 
            "SAMD21G18A-AU", "SAMD21G18A-AUT", 
            "SAMD21G18A-AF", "SAMD21G18A-AFT", 
            "SAMD21G18A-MU", "SAMD21G18A-MUT", 
            "SAMD21G18A-MF", "SAMD21G18A-MFT", 
                             "SAMD21G18A-UUT", 
            "SAMD21G15B-AU", "SAMD21G15B-AUT", 
            "SAMD21G15B-AF", "SAMD21G15B-AFT", 
            "SAMD21G15B-MU", "SAMD21G15B-MUT", 
            "SAMD21G15B-MF", "SAMD21G15B-MFT", 
            "SAMD21G16B-AU", "SAMD21G16B-AUT", 
            "SAMD21G16B-AF", "SAMD21G16B-AFT", 
            "SAMD21G16B-MU", "SAMD21G16B-MUT", 
            "SAMD21G16B-MF", "SAMD21G16B-MFT", 
            "SAMD21J15A-AU", "SAMD21J15A-AUT", 
            "SAMD21J15A-AF", "SAMD21J15A-AFT", 
            "SAMD21J15A-MU", "SAMD21J15A-MUT", 
            "SAMD21J15A-MF", "SAMD21J15A-MFT", 
            "SAMD21J16A-AU", "SAMD21J16A-AUT", 
            "SAMD21J16A-AF", "SAMD21J16A-AFT", 
            "SAMD21J16A-MU", "SAMD21J16A-MUT", 
            "SAMD21J16A-MF", "SAMD21J16A-MFT", 
            "SAMD21J16A-CU", "SAMD21J16A-CUT", 
            "SAMD21J17A-AU", "SAMD21J17A-AUT", 
            "SAMD21J17A-AF", "SAMD21J17A-AFT", 
            "SAMD21J17A-MU", "SAMD21J17A-MUT", 
            "SAMD21J17A-MF", "SAMD21J17A-MFT", 
            "SAMD21J17A-CU", "SAMD21J17A-CUT", 
            "SAMD21J18A-AU", "SAMD21J18A-AUT", 
            "SAMD21J18A-AF", "SAMD21J18A-AFT", 
            "SAMD21J18A-MU", "SAMD21J18A-MUT", 
            "SAMD21J18A-MF", "SAMD21J18A-MFT", 
            "SAMD21J18A-CU", "SAMD21J18A-CUT", 
            "SAMD21J15B-AU", "SAMD21J15B-AUT", 
            "SAMD21J15B-AF", "SAMD21J15B-AFT", 
            "SAMD21J15B-MU", "SAMD21J15B-MUT", 
            "SAMD21J15B-MF", "SAMD21J15B-MFT", 
            "SAMD21J16B-AU", "SAMD21J16B-AUT", 
            "SAMD21J16B-AF", "SAMD21J16B-AFT", 
            "SAMD21J16B-MU", "SAMD21J16B-MUT", 
            "SAMD21J16B-MF", "SAMD21J16B-MFT", 
            "SAMD21J16B-CU", "SAMD21J16B-CUT",             
            ]

    return [SamModel(pn) for pn in partNumbers]

def getPackage(partNumber):
    "Returns package as a string, for partNumber"

    series = partNumber[:6]
    if not series == "SAMD21":
        raise Exception("getPackage() called on an unknown series")

    pinCode, packageCode = partNumber[6], partNumber[11]

    numPinsStr = {
                   "E" : "32",
                   "G" : "48",
                   "J" : "64",
                 } [pinCode]
    
    packageName = {
                    "A" : "TQFP",
                    "M" : "QFN",
                    "U" : "WLCSP",
                    "C" : "UFBGA",
                  } [packageCode]

    return packageName + numPinsStr

def getFlashString(partNumber):
    "Returns Flash storage size as a string in specified part eg '256KB'"
    series = partNumber[:6]
    if not series == "SAMD21":
        raise Exception("getFlashString() called on an unknown series")

    memCode = partNumber[7:9]
    return {
            "18" : "256KB",
            "17" : "128KB",
            "16" : "64KB",
            "15" : "32KB",
            } [memCode]

def getRamString(partNumber):
    "Returns amount of SRAM available in specified part eg '32KB'"
    series = partNumber[:6]
    if not series == "SAMD21":
        raise Exception("getRamString() called on an unknown series")

    memCode = partNumber[7:9]
    return {
            "18" : "32KB",
            "17" : "16KB",
            "16" : "8KB",
            "15" : "4KB",
            } [memCode]

def assembleAliases(allParts):
    "Constructs a list of lists, where members of each sublist are aliasable"
    outList = []

    for newPart in allParts:
        aliased = False
        for possibleAlias in outList:
            if possibleAlias[0].canAlias(newPart):
                possibleAlias.append(newPart)
                aliased = True
                break

        if not aliased:
            outList.append([newPart])

    return outList

if __name__ == "__main__":
    
    baseName = "test"

    parts = assembleAliases(knownSamParts())

    with open(baseName + ".lib", "wb") as outFile:
        for aliases in parts:
            outFile.write( aliases[0].outputLibSymbol(aliases[1:]) )

    with open(baseName + ".dcm", "wb") as outFile:
        for aliases in parts:
            for part in aliases:
                outFile.write( part.outputDcm() )
