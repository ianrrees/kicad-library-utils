from __future__ import print_function

def ufbgaPinGenerator(rows, cols):
    for row, col in zip(range(rows), range(cols)):
        yield "%s%d" % (chr(ord("A" + row)), 1 + col)

def wlcspPinGenerator(numPins):
    if numPins == 45:
        rows = 7
        colsLong = 7 # number of pins in a long row, short rows have one less
        startLong = False # is row A a long row?
    else:
        raise Exception("Don't know how to make %d pin WLCSP" % numPins)

    for row in range(rows):
        isLong = (row % 2 == 0) == startLong

        # Bools upgrade to integers 0 and 1
        cols = range(2 - isLong, colsLong * 2, 2)
        for col in cols:
            yield "%s%d" % (chr(ord('A') + row), col)

def pinIterator(partNumber):
    series = partNumber[:6]

    if not series == "SAMD21":
        raise Exception("getNumPins() called on an unknown series")

    pinCode = partNumber[6]
    packageCode = partNumber[11]

    if series == "SAMD21":
        if packageCode in ["A", "M"]: # TQFP or QFN
           return {
                  "E" : ("%d" % (p + 1) for p in range(32)),
                  "G" : ("%d" % (p + 1) for p in range(48)),
                  "J" : ("%d" % (p + 1) for p in range(64)),
                  } [pinCode]
        elif packageCode in ["U"]: # WLCSP
            return {
                  "E" : wlcspPinGenerator(35),
                  "G" : wlcspPinGenerator(45),
                   } [pinCode]
        elif packageCode in ["C"]: # UFBGA
            return {
                  "J" : ufbgaPinGenerator(8, 8),
                   } [pinCode]

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
    """Returns a dict of pin to description mappings.

    Keys are strings, because some packages use pin numbers, and others use
    coordinates.  Descriptions are terse, and are meant to be expanded via
    FUNCTION_TBD.
    """
#TODO: Fill in FUNCTION_TBD above

    pinouts = { "SAMD21E" :
                    None,
                "SAMD21G" :
                    None,
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
                        "52" : "RESET", #TODO: Active low mark?
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


if __name__ == "__main__":
    for partNumber in knownSamParts():
        print(partNumber)
