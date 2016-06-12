from __future__ import print_function

from math import ceil # For rounding
from datetime import datetime
import re

def expandPortPin(partNumber, pin):
    "Takes a partNumber and pin and returns list of strings with port functions"

    series = partNumber[:6]
    if not series == "SAMD21":
        raise Exception("getNumPins() called on an unknown series")

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

    pinouts = { "SAMD21E" :
                    None, # TODO: Finish
                "SAMD21G" :
                    None, # TODO: Finish
                "SAMD21J" :
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
                    }
              }
    return pinouts[partNumber[:7]]

def knownSamParts():
    "Generator yields all Atmel SAM parts we can generate symbols for"
    families = ["D"]

    serieses = { "D" : ["D21"] }

    pinCounts = { "D21" : ["E", "G", "J"] }

    flashSizes = { "D21" : ["15", "16", "17", "18"] }

    variants = { "D21" : ["A", "B"] }

    packages = { "D21" : ["A", "M", "U", "C"] }

    grades = { "D21" : ["U", "F"] }

    carriers = { "D21" : ["", "T"] }

    # TODO: Several combinations of variant/package/flash size/etc aren't
    #       listed in the datasheet.  Is it easier to just list the ones
    #       that do exist?
    for family in families:
        for series in serieses[family]:
            for pinCount in pinCounts[series]:
                for flashSize in flashSizes[series]:
                    for variant in variants[series]:
                        for package in packages[series]:
                            if pinCount == "J": # J pin count is "64 pin"
                                if package == "U": # U package is WLCSP
                                    continue
                            else:
                                if package == "C": # C package is UFBGA
                                    continue
                            for grade in grades[series]:
                                for carrier in carriers[series]:
                                    yield "SAM" + series + pinCount + flashSize + variant + "-" + package + grade + carrier

def getPackage(partNumber):
    "Returns package as a string, for partNumber"

    series = partNumber[:6]
    if not series == "SAMD21":
        raise Exception("getNumPins() called on an unknown series")

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

def outputLibSymbol(partNumber, aliases=None):
    "Generates the .lib description for partNumber"

    # From Kicad Library Conventions
    # https://github.com/KiCad/kicad-library/wiki/Kicad-Library-Convention
    pinLength = 100 
    pinTextSize = 40
    fieldTextSize = 50
    grid = 100

    # Comment header
    out =  "#\n"
    out += "# " + partNumber + "\n"
    out += "# Automatically generated " + str(datetime.now()) + "\n"
    out += "#\n"

    leftPins, rightPins = arrangePins(partNumber)

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
    out += "DEF " + partNumber + " U 0 40  Y Y 1 F N\n"

    # Required fields
    fieldTextY = top + fieldTextSize + grid
    packageStr = getPackage(partNumber) 

    #TODO: Unsure what the trailing Ns are for
    out += 'F0 "U" %d %d 50 H V L CNN\n' % \
           (-width / 2, fieldTextY)
    out += 'F1 "' + partNumber + '" %d %d 50 H V C CNN\n' % \
           (0, fieldTextY)
    out += 'F2 "' + packageStr + '" %d %d 50 H V R CIN\n' % \
           (width / 2, fieldTextY)
    out += 'F3 "" 0 0 50 H V C CNN\n'

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

        if p is None:   # Gap between groups of pins
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

    return out

def arrangePins(partNumber):
    "Make lists of (pin number, description) tuples for L and R of symbol"
    pins = getPinout(partNumber)

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
        expanded = "/".join(expandPortPin(partNumber, pin[1]) + [pin[1]])
        rightExpanded.append( (pin[0], expanded) )

    return leftSorted, rightExpanded

if __name__ == "__main__":
    print(outputLibSymbol("SAMD21J18A-MF"))
#    for partNumber in knownSamParts():
 #       print(partNumber)
