import pandas as pd
import itertools

 
source = 'C:\Desktop\\'
solventpercolation = pd.read_csv(source + 'regressiontable.csv') 
myparameters = []
pixelsize = 3 # Change this to the pixel size used

def myround(x, base):
    return base * round(x/base)
	
def longest_repetition(iterable, **kwargs):
    """
    Return the item with the most consecutive repetitions in `iterable`.
    If there are multiple such items, return the first one.
    If `iterable` is empty, return `None`.
    """
    try:
        return max((sum(1 for _ in group), -i, item)
                   for i, (item, group) in enumerate(itertools.groupby(iterable)))[2]
    except ValueError:
        return kwargs
 
solventpercolationTop = solventpercolation[(solventpercolation['Percolation Top']> 0)]
solventpercolationBot = solventpercolation[(solventpercolation['Percolation Bottom'] > 0)]
solventpercolationTop.loc[:,'Percolation Top'] = myround(solventpercolationTop['Percolation Top'],pixelsize)
idx = solventpercolationTop.groupby(myparameters+['Section','Folder'])['Percolation Top'].transform(longest_repetition) == solventpercolationTop['Percolation Top'] #Everything to the left of folder must be the name of the column, where you are looking at different parameters.

solventpercolationTop = solventpercolationTop[idx]
solventpercolationTop = solventpercolationTop.rename(columns={'Percolation Top':'Percolation'})
solventpercolationBot.loc[:,'Percolation Bottom'] = myround(solventpercolationBot['Percolation Bottom'],pixelsize)
idx = solventpercolationBot.groupby(myparameters+['Section','Folder'])['Percolation Bottom'].transform(longest_repetition) == solventpercolationBot['Percolation Bottom'] #Everything to the left of folder must be the name of the column, where you are looking at different parameters.

solventpercolationBot = solventpercolationBot[idx]
solventpercolationBot = solventpercolationBot.rename(columns={'Percolation Bottom':'Percolation'})
solventpercolation = pd.concat([solventpercolationTop,solventpercolationBot])
solventpercolation = solventpercolation.drop_duplicates()
solventmeans = solventpercolation.groupby(myparameters+['Folder']).mean().reset_index()
solventmeans = solventmeans[myparameters+['Folder','Percolation']] #Everything to the left of folder must be the name of the column, where you are looking at different parameters.
solventmeans.to_csv(source + 'percolation-final-processed-results.csv')