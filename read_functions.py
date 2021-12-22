import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import os
import pandas as pd
import json

'''
stock = 'AAPL'
data = 'EARNINGS'
key = ["fiscalDateEnding", "reportedEPS"]
'''

cwd=os.getcwd()
def librarian(stock, datatype, keys=None, period=2):
    # period = 2 quarterly, period = 1 annual

    os.chdir(os.path.join(cwd,"Data//" + stock))
    filename = stock + '_' + datatype + '.csv'
    if datatype=='TIME_SERIES_DAILY':
        read = get_key_from_csv(filename)
    else:
        read = get_key_from_json(filename, period)
    if keys != None:
        read = read[keys]
    return read


def get_key_from_csv(filename):
    filedata = pd.read_csv(filename)
    filedata['timestamp'] = filedata['timestamp'].map(date.fromisoformat)
    return filedata

def get_key_from_json(filename, period):
    file=open(filename,'r').read()
    filedata = json.loads(file)
    filedata = pd.DataFrame.from_dict(filedata[list(filedata.keys())[period]])
    return filedata




'''
a = librarian(stock,data)
print(a)
plt.plot(a[0],a[1])
plt.show()
'''
