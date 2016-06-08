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

def getPinout(partNumber):
    """Returns a dict of pin to description mappings.

    Keys are strings, because some packages use pin numbers, and others use
    coordinates.  Descriptions are terse, and are meant to be expanded via
    FUNCTION_TBD.
    """
#TODO: Fill in FUNCTION_TBD above

    pinouts = { "SAMD21E" :
                    {
                        "1" : "something",
                    },
                "SAMD21G" :
                    None,
                "SAMD21J" :
                    None,
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
