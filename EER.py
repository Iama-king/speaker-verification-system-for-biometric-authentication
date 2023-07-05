import verification as v
import identification as id
import numpy as np
import os
import matplotlib.pyplot as plt
tardir="D:/audio/rsp/test"
l=os.listdir(tardir)
dic=[]
dic1=[]
dic2=[]
ter=l[19]
for k in l:
    for i in l:
        dic2=[]
        for j in (os.listdir(tardir+"/"+i)):
            s,ts=v.main(k,i,j)
            dic2.append(list(s)[0])
            # if(k==ts):
            #     dic2[i][1]+=1
        if(i==ter):
            dic1=dic1+dic2
            continue
        dic=dic+dic2
        dic2=[]
    break
print(dic)
far = []
threshold = []
for i in range(100):
        num = 0
        for x in dic:
            if((x*100)>i):
                num+=1
        #print(i,num)
        far.append(num)
        threshold.append(i)
far = np.array(far)
print('FAR: ',far)
print('-----------------------------------------------------------')
frr = []
for i in range(100):
        num = 0

        for x in dic1:
                if x*100<i:
                        num+=1
        #print(i,num)
        frr.append(num)


frr = np.array(frr)
print('FRR: ',frr)
print('-----------------------------------------------------------')
for i in range(100):
        a = frr[i]
        b = far[i]
        if(a==b):
            EER= a
            print('EER = ',i)

plt.plot(threshold,frr,'--b',label='FRR')
plt.plot(threshold,far,'--r',label='FAR')
#plt.plot(15,EER,'ro')
plt.xlabel('threshold')
plt.title('FAR,FRR and EER')
plt.legend()
plt.axis([0, 100, 0, 100])
plt.show()

# username="Gowtham"
# tuser="Gowtham"
# #if(en==1):
#     #perform enrollment
# #perform verification
# print("yes")