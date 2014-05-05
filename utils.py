def readLines(fileName):
    try:
        f = open(fileName, 'r')
        lines = [line for line in f]
        f.close()
        return lines
    except:
        print 'File Error!'
