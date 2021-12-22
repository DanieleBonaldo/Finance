from datetime import datetime, timedelta, date
import requests
import numpy as np
import time
import os


# Script per scaricare i data da Alpha Vantage con controllo automatico sul limite di accessi e stato di aggiornamento
# Verificare che funzioni day_access

# Set the directory in which data will be stored and the day limit of your account
local_dir = 'C:\\Users\\bonal\\OneDrive\\Desktop\\Codice\\Finance'
day_limit = 500

os.chdir(local_dir)

def open_file(file, msg):
    if os.path.isfile(file):
        return open(file).readlines()
    else:
        f=open(file,'w')
        f.close()
        print(msg)
        quit()

followed=open_file("followed.txt",'Write the stocks you want to follow in column in the file "followed.txt"')
followed=[i[:-1] for i in followed]


# DataFile e cadenza di aggiornamento in giorni

data_to_collect = open_file('data_to_collect.txt','Write the data you want in column in the file "data_to_collect.txt" \
                                \n The format should be: \n data_pack(as in AlphaVantage Doc) (number of days between updates)')

updates= {}
for i in data_to_collect:
    texts=i.split()
    updates[texts[0]]=timedelta(days=int(texts[1]))

# Inizializzazione

F=open_file('Data_alpha.txt','Write your key for AlphaVantage in the first row in the format "key: *****" \
            in the file Data_alpha \n The program will write automatically the last accesses') # Chiave e ultimi accessi


key=F[0].split()[1]
last=[0,0,0,0,0]
try:
    ls=F[1].split()
except:
    ls=[datetime.datetime(1990,10,10)]*5

for i in range(5):
    last[i]=datetime.strptime(ls[1]+' '+ls[2+i],"%m/%d/%y %H:%M:%S") # Raccolta ultimi accessi

if date.today().day-last[-1].date().day==0:
    day_access = F[2].split()[1]
else:
    day_access = 0

API_URL='https://www.alphavantage.co/query?'

# Funzioni
''' Da usare ogni volta prima di un get: last=check(last)'''
# Controlla che nell'ultimo minuto non siano stati fatti più di 5 accessi, in tal caso aspetta i
# secondi necessari per non far crashare il programma
def check(t, day_access):
    print("Availability check:", end=" ")
    now=datetime.now()
    if day_access>=day_limit:
        print("Daily limit reached")
        quit()
    if (now-t[0]).total_seconds()>61:
        t.pop(0)
        t.append(now)
        print("Ok")
        return t
    else:
        waittime=60-(now-t[0]).total_seconds()+1
        print('Wait {:.2f} seconds..'.format(waittime),end=" ", flush=True)
        t.pop(0)
        t.append(now)
        time.sleep(waittime)
        print("Ok")
        return t

# Corpo
if os.path.isdir('./Data'): # Mossa o creazione nella cartella Data
    os.chdir('./Data')
else:
    os.mkdir('./Data')
    os.chdir('./Data')

for i in followed: # Itero sulle società
    try:
        if os.path.isdir('./'+ i): # Mossa o creazione della cartella
            os.chdir('./'+ i)
        else:
            os.mkdir('./'+ i)
            os.chdir('./'+ i)
        print("\n Getting data for " + i)
        if os.path.isfile('./'+ i + '_check.txt'): # Apertura check file
            filecheck=open(i+'_check.txt').readlines()
        else:
            filecheck=['Day check \n']
        for work in updates: # Itero sui parametri
            try:
                row=[i.find(work) for i in filecheck].index(0)
                lastup=filecheck[row].split()[1]
            except:
                row=len(filecheck)
                filecheck.append(work)
                lastup='01/01/01'
            data = { "function": work,
                "symbol": i,
                "outputsize" : "full",
                "datatype": "csv",
                "apikey": key }
            if datetime.now()-datetime.strptime(lastup,'%m/%d/%y')>updates[work]: # Controllo e update
                print('\tGetting '+ work, end=': ',flush=True)
                last=check(last, day_access)
                day_access += 1
                out=open(i + '_'+work+'.csv','w')
                response = requests.get(API_URL, data)
                out.write(response.text)
                filecheck[row]=work+' ' + datetime.now().strftime('%m/%d/%y') + '\n'
            else:
                print('\t'+work+ ' up to date')
        out_check=open(i + '_check.txt','w')
        out_check.writelines(filecheck)
        os.chdir('../') # Ritorno alla cartella generale
    except Exception as e:
        print(e)
        os.chdir('../')
        continue
os.chdir('../')
# Fine
F1=open('Data_alpha.txt','w') # Aggiornamento file sugli ultimi accessi
F1.write(F[0])
F1.write('last_access: {} '.format(last[0].strftime("%m/%d/%y")))
for i in last:
    F1.write(i.strftime("%H:%M:%S")+' ')
F1.write('\nday_access: ' + str(day_access))
