"""
Basic functional utilities.
"""

def readLines(fileName):
    """
    Return list of lines from the file.
    """
    try:
        f = open(fileName, 'r')
        lines = [line for line in f]
        f.close()
        newlines = []
        for line in lines:
            if (len(line.strip()) != 0):
                newlines.append(line)
        return newlines
    except:
        print 'File read error!'


def writeString(fileName, string):
    """
    Write string to the file.
    """
    try:
        f = open(fileName, 'w')
        f.write(string)
        f.close()
    except:
        print 'File write error!'

