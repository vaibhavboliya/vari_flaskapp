import cv2
import sys
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import colors
import matplotlib.pyplot as plt



cols1 = ['red','yellow','limegreen', 'green' ,'darkgreen']
cols6 = ['darkgreen', 'lawngreen', 'green', 'darkred']
cols2 =  ['gray', 'gray', 'red', 'yellow', 'green']
cols3 = ['gray', 'blue', 'green', 'yellow', 'red']
cols4 = ['black', 'gray', 'blue', 'green', 'yellow', 'red']
cols5 = ['red', 'green' ]

def create_colormap(args):
    return LinearSegmentedColormap.from_list(name='custom1', colors=args)
def plantStatus(data):
    
    data[data == 0] = np.nan
    mean = np.nanmean(data[:, 1:])
    if(mean<0.01):
        return "No vegetation found"
    elif(mean<0.17):
        return "vegetation has less nutrients or some desease"
    elif(mean<0.26):
        return " vegetation has moderate health"
    elif(mean<0.37):
        return " vegetation has good health"
    else:
        return "vegetation is very healthy"
    
def bandSplit(img):
    b,g,r= cv2.split(img)
    return b,g,r
    
def calculateVARI(b,g,r):
    np.seterr(divide='ignore', invalid='ignore')
    vari =  (g.astype(float) - r.astype(float)) / (g + r - b)
    return vari
def valueClip(index):
    clipval = np.clip(index,a_min = 0, a_max =0.4)
    return clipval

    
    
def vari(indeximg):   
    img = cv2.imread(indeximg)
    b,g,r = bandSplit(img)
    varivalue = calculateVARI(b,g,r)
    clipval = valueClip(varivalue)
    status =  np.copy(clipval)
    title = plantStatus(status)
    colr =plt.imshow(clipval,cmap=create_colormap(cols1))
    plt.axis('off')
    cbar = plt.colorbar(colr)
    plt.title(title)
    cbar.set_ticks([0.01, 0.16, 0.25, 0.33, 0.4])
    cbar.set_ticklabels(["No Vegetation", "less nutrition", "moderate", "high",'very high'])
    imgfile = indeximg.split("/")[-1]
    imgname = imgfile.split(".")[0]
    print(imgname)

    results_dir = './static/variresult/'
    plt.savefig(results_dir +'vari_'+imgname+'.jpg')
    plt.close()


# vari('./upload/farm.jpg')
 
#endvi = np.clip(index,a_min = 0, a_max =1)
#endvi = np.round_(endvi, decimals = 1) 
#print(vari)
#endvi = endvi*256*1000
#plt.imsave("endvi_cmap.png", endvi,cmap=create_colormap(cols1))




#vari = np.clip(vari,a_min = 0, a_max =1)

#vari = vari*256





#orig_map=plt.cm.get_cmap('RdYlGn') 
#plt.imsave("vari_cmap.png", vari,cmap=orig_map)
#plt.imsave("vari_cmap1.png", vari,cmap=create_colormap(cols1))
#plt.imsave("test.png", vari,cmap=create_colormap(cols1))


#data = vari

#array2 = np.argwhere(vari)
#mean = np.nanmean(array2)
#print(mean)

