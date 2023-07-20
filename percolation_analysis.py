import os
import tkinter as tk
import tkinter.filedialog
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import imageio
from scipy import stats


plt.rcParams.update({'font.size': 20})
plt.rcParams["font.family"] = "sans-serif"
root = tk.Tk()
root.geometry('300x450')
folderlist = []
table = tk.Entry(root, relief=tk.RIDGE, width=50)
data = pd.DataFrame(
    columns=['Section', 'Subdivision Length', 'Voxel Cluster Size', 'Cluster Size', 'Start', 'End', 'Top', 'Bottom',
             'Dist_top', 'L^(-1/0.88)_top', 'Dist_bot', 'L^(-1/0.88)_bot'])
regressiontable = pd.DataFrame(columns=['Folder','Section','Subdivision Length','d_top','R2_top','d_bot','R2_bot'])

def fileCallback():
    global folderlist
    directory = tkinter.filedialog.askdirectory(parent=root, title='Choose a file',
                                                initialdir='G://MicroCT//Devro_0.5_20_0.5//')
    folderlist.append(str(directory))

def fileWriter(folder, subdirs, section):
    global data
    global edge
    start = 1
    path = folder + '/' + subdirs
    if subdirs.startswith(folderprefix.get()):    
        voxelcluster = int(subdirs[len(folderprefix.get())::])
        clustersize = float(pixelsize.get()) * voxelcluster
        counter = 0
        print('Now analysing '+subdirs + ' ' + section)
        pathlist = os.listdir(path)
        pathlist.sort()
        for subfiles in pathlist:
            if start is 1:
                start = 0
                image = imageio.imread(os.path.join(path, subfiles))
                maxval = np.amax(image)
                blankimage = np.ones(image.shape, dtype = int) * maxval
                edge = range(image.shape[0] - 2*int(border.get()), 0,
                             -image.shape[0]//int(granularity.get()))
                print(edge)
                end = len(pathlist) -1
                #int(start) + image.shape[0] - 1 - 2*int(border.get())
                blankdir = {key:[] for key in edge}
            for value in edge:
                if section == 'Centre':
                    startslice = int(border.get()) + image.shape[0]//2 - value//2
                    endslice = image.shape[0]//2 + value//2- int(border.get())
                else:
                    startslice = int(border.get())
                    endslice = value - int(border.get())
                image = imageio.imread(os.path.join(path, subfiles))
                if np.array_equal(image[startslice:endslice,startslice:endslice],
                                  blankimage[startslice:endslice,startslice:endslice]):
                    blankdir[value].append(counter)
                if counter == end and len(blankdir[value]) > 0:
                    top = blankdir[value][0]
                    bottom = blankdir[value][-1]
                    if top != start:
                        Ltop = (float(pixelsize.get()) * (top - start + 1)) ** -(1 / 0.88)
                    else:
                        Ltop = None
                    if bottom != end:
                        Lbot = (float(pixelsize.get()) * (end - bottom + 1)) ** -(1 / 0.88)
                    else:
                        Lbot = None
                    data = data.append(pd.Series([section,value,subdirs[len(folderprefix.get())::] ,clustersize,start ,end,top,bottom,top - start + 1,Ltop,
                                 end - bottom + 1,Lbot], index=data.columns),ignore_index = True)
            counter += 1
			
def batchAnalysis():
    global folderlist
    global data
    global regressiontable
    global edge
    print('Analysing list of files:',folderlist)
    for folder in folderlist:
        for root, dirs, files in os.walk(folder):
            for subdirs in dirs:
                fileWriter(folder, subdirs, 'Left Corner')
                fileWriter(folder, subdirs, 'Centre')
        data.sort_values(by=['Cluster Size'], inplace=True)      
        data.to_csv(folder[8::].replace("\\","-")+'-'+'percolation-results.csv')
        for sectionname in ['Centre','Left Corner']:
            for subdivision in edge:
                newdata = data[data['Section'].isin([sectionname]) & data['Subdivision Length'].isin([subdivision])]
                newdata = newdata.dropna(subset = ['L^(-1/0.88)_top'])
                y1 = newdata['Cluster Size'].astype('float64')
                X1 = newdata['L^(-1/0.88)_top'].astype('float64')
                try:
                    regtopint = None
                    regtopr = None
                    slope, regtopint, regtopr, p_value, std_err = stats.linregress(X1, y1)
                    botfig = plt.figure()
                    plt.plot(X1,y1,'o--',)
                    plt.xlabel('L$^\\frac{-1}{0.88}$ /'+chr(956)+'m')
                    plt.ylabel('d / '+chr(956)+'m')
                    botfig.tight_layout()
                    plt.savefig(folder[8::].replace("\\","-")+'-'+str(sectionname)+'-'+str(subdivision)+'-top-percolation.png')
                    plt.close()
                except:
                    pass
                newdata = data[data['Section'].isin([sectionname]) & data['Subdivision Length'].isin([subdivision])]
                newdata = newdata.dropna(subset = ['L^(-1/0.88)_bot'])
                X2 = newdata['L^(-1/0.88)_bot'].astype('float64')
                y2 = newdata['Cluster Size'].astype('float64')
                try:
                    regbotint = None
                    regbotr = None
                    slope, regbotint, regbotr, p_value, std_err = stats.linregress(X2, y2)
                    botfig = plt.figure()
                    plt.plot(X2,y2,'o--',)
                    plt.xlabel('L$^\\frac{-1}{0.88}$ /'+chr(956)+'m')
                    plt.ylabel('d / '+chr(956)+'m')
                    botfig.tight_layout()
                    plt.savefig(folder[8::].replace("\\","-")+'-'+str(sectionname)+'-'+str(subdivision)+'-bot-percolation.png')
                    plt.close()
                except:
                    pass
                
                regressiontable = regressiontable.append(pd.Series([folder,sectionname,subdivision,regtopint,regtopr,regbotint,regbotr],index=regressiontable.columns),ignore_index = True)
        plt.close()
        print('Analysis of folder: \" '+ folder +'\" complete')
        data = pd.DataFrame(columns=['Section', 'Subdivision Length', 'Voxel Cluster Size', 'Cluster Size', 'Start', 'End', 'Top', 'Bottom','Dist_top', 'L^(-1/0.88)_top', 'Dist_bot', 'L^(-1/0.88)_bot'])
        regressiontable.to_csv('regressiontable.csv', mode='a', header=False)
        regressiontable = pd.DataFrame(columns=['Folder','Section','Subdivision Length','d_top','R2_top','d_bot','R2_bot'])
    print('All files analysed')


def addFolderList():
    global folderlist
    addon = tkinter.filedialog.askopenfilename(parent=root, title='Choose a file')
    addonlist = [line.rstrip('\n') for line in open(addon)]
    folderlist = folderlist + addonlist
    


def delDir():
    global folderlist
    del folderlist[int(indexentry.get())]


def fetchDir():
    global folderlist
    global table
    if table:
        table.destroy()
    table = tk.Entry(root, relief=tk.RIDGE, width=50)
    for i in range(len(folderlist)):
        table.grid(row=1, column=i, sticky=tk.NSEW)
        table.insert(tk.END, '%s' % (folderlist[i]))
        table.pack()


a = tk.Button(root, text='Select files to analyse', command=fileCallback)
a.pack()

b = tk.Button(root, text='Run percolation analysis', command=batchAnalysis)
b.pack()

c = tk.Button(root, text='Pixel size (um): ', relief=tk.FLAT)
c.pack()

pixelsize = tk.Entry(root)
pixelsize.insert(tk.END, '3')
pixelsize.pack()

d = tk.Button(root, text='Border size (pixels): ', relief=tk.FLAT)
d.pack()

border = tk.Entry(root)
border.insert(tk.END, '0')
border.pack()

e = tk.Button(root, text='Enter granularity factor of percolation analysis', relief=tk.FLAT)
e.pack()

granularity = tk.Entry(root)
granularity.insert(tk.END, '20')
granularity.pack()

g = tk.Button(root, text='Enter folder prefix before voxel size', relief=tk.FLAT)
g.pack()

folderprefix = tk.Entry(root)
folderprefix.insert(tk.END, 'ROI-')
folderprefix.pack()

h = tk.Button(root, text='Load file with list of directories', command=addFolderList)
h.pack()

i = tk.Button(root, text='Fetch directories', command=fetchDir)
i.pack()

j = tk.Button(root, text='Delete directory', command=delDir)
j.pack()

indexentry = tk.Entry(root)
indexentry.insert(tk.END, 'Index begins from 0')
indexentry.pack()
root.wm_title("Percolation Analysis Tool")

root.mainloop()