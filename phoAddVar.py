## Purpose: Python code to create additional variables for PHOENICS results
## Usage: Run the code from command line
## Usage: python phoAddVar.py <q1FileName> <AdditionalVariableSpecification>
## Notes: Rule to create additional variable to be put in separate text file
## Notes: Specify operator through word   
## Notes: Eg: K1 = U1 + V1 written as K1 equals U1 add V1
## Notes: Adding "final" (no quotes) after V1 implies K1 to be written to phi
## Notes: Requires "numpy" library to be installed! Tested with Python 2.7
## Notes: No warranty on results. Use at your own risk/discretion
## Notes: Code is free. Appreciate feedback/acknowledging when using it
## Reference: http://www.cham.co.uk/phoenics/d_polis/d_enc/phif.htm
## Created by: Venugopalan Raghavan

import numpy as np
import os as os
import sys as sys

cwd = os.getcwd().replace("\\","/")

## Get the file names

fileNames = sys.argv
lFN = len(fileNames)
AddFile = fileNames[lFN-1]
q1File = fileNames[lFN-2]

## Read in the q1 file

iF = cwd +"/" + q1File
iFR = open(iF,"r")

currline = iFR.readline()

yes1 = "DOM" in currline
yes2 = "SIZE" in currline

while currline!='':
	yes1 = "DOM" in currline 
	yes2 = "SIZE" in currline
	if yes1 and yes2:
		break
	currline = iFR.readline()

iFR.close()

extents = currline.strip().split()
xExtent = float(extents[3].strip(","))
yExtent = float(extents[4].strip(","))
zExtent = float(extents[5].strip(","))

## Read in the phi file

phiFile = q1File.split(".q1")[0]

iF = cwd + "/" + phiFile + ".phi"
iFR = open(iF,"r")

currline = iFR.readline()

nx = ny = nz = nphi = den1 = den2 = epor = npor = hpor = vpor = lenrec = 0
numblk = nmatst = nfmak1 = 0

currline = iFR.readline()
currline = iFR.readline()

values = currline.split()
nx = int(values[0])+1
ny = int(values[1])+1
nz = int(values[2])+1
nphi = int(values[3])
den1 = int(values[4])
den2 = int(values[5])
epor = int(values[6])

print "Grid size = ",(nx-1),"x",(ny-1),"x",(nz-1)

currline = iFR.readline()

values = currline.split()
npor = int(values[0])
hpor = int(values[1])
vpor = int(values[2])
lenrec = int(values[3])
numblk = int(values[4])
nmatst = int(values[5])
nfmak1 = int(values[6])

currline = iFR.readline()

varnames = list()
cnt = 0

print "\nExtracting the fields present"

while cnt < nphi:
	currline = iFR.readline()
	lc = len(currline)
	ii = 1
	while ii < lc:
		var = currline[ii:ii+4]
		if var.strip()!="":
			varnames.append(var.strip())
		ii = ii + 4
		cnt = cnt + 1
			
xstart = list()
ystart = list()
zstart = list()
pcorr = list()
cnt = 0

xstart.append(0)
ystart.append(0)
zstart.append(0)

SX = len(xstart) < nx
SY = len(ystart) < ny
SZ = len(zstart) < nz
SP = len(pcorr) < nz - 1

## Reading in the coordinates of the grid points
print "\nReading in the grid points"

while (SX or SY or SZ or SP):
	currline = iFR.readline()
	lc = len(currline)
	ii = 0
	while ii < lc:
		var = currline[ii:ii+13]
		if var.strip()!="":
			if SX:
				xstart.append(float(var))
				SX = len(xstart) < nx
			elif ~SX and SY:
				ystart.append(float(var))
				SY = len(ystart) < ny
			elif ~SX and ~SY and SZ:
				zstart.append(float(var))
				SZ = len(zstart) < nz
			elif ~SX and ~SY and ~SZ and SP:
				pcorr.append(float(var))
				SP = len(pcorr) < nz - 1
		ii = ii + 13

currline = iFR.readline()
l = len(currline.strip())
ind1 = [n for n in xrange(len(currline.strip())) if currline.strip().find('T',n)==n]
currline = iFR.readline()
ind2 = [n for n in xrange(len(currline.strip())) if currline.strip().find('T',n)==n]	

namesToUse = list()
for ii in xrange(0,len(ind1)):
	namesToUse.append(varnames[ind1[ii]])
for ii in xrange(0,len(ind2)):
	namesToUse.append(varnames[l+ind2[ii]])

print "\nVariables with results are:",namesToUse

for ii in xrange(0,nz-1):
	for jj in xrange(0,len(namesToUse)):
		oF = cwd + "/" + namesToUse[jj]
		if ii == 0:
			oFW = open(oF,"w")
		else:
			oFW = open(oF,"a")
		cnt = 0
		while cnt < ((nx-1)*(ny-1)):
			currline = iFR.readline()
			i = 0
			lc = len(currline)
			while i < lc:
				var = currline[i:i+13]
				if var.strip()!="":
					oFW.write(var+" ")
					cnt = cnt + 1
				i = i + 13
		oFW.write("\n")
		oFW.close()

iFR.close()

## Reading in the additional variables file

print "\nReading in the additional variables file"

iF = cwd + "/" + AddFile
iFR = open(iF,"r")

currline = iFR.readline()

varsAndOps = list()

while currline!='':
	varsAndOps.append(currline.strip())
	currline = iFR.readline()

iFR.close()

newVarList = list()
writeList = list()

for ii in xrange(0,len(varsAndOps)):
	s1 = varsAndOps[ii]
	s2 = s1.split()
	newVar = s2[0]
	newVarList.append(newVar)
	try:
		oldVar = float(s2[2])
	except:
		oldVar = s2[2]

	if "final" in s1:
		writeList.append(newVar)
	
	if type(oldVar) is str:
		iF = cwd + "/" + oldVar
		OV = np.loadtxt(iF,dtype=float)
	else:
		OV = np.array(oldVar)
	
	gg = ("add" or "subtract" or "multiply" or "divide") in s2

	if gg:
		operator = s2[3]
		try:
			operand = float(s2[4])
		except:
			operand = s2[4]

		if type(oldVar) is str:
			iF = cwd + "/" + operand
			OP = np.loadtxt(iF,dtype=float)
		else:
			OP = np.array(operand)

		if operator == "add":
			NV = OV + OP
		elif operator == "subtract":
			NV = OV - OP
		elif operator == "multiply":
			NV = OV * OP
		elif operator == "divide":
			NV = OV / OP
	else:
		NV = OV*np.ones((nx-1)*(ny-1))
	oF = cwd + "/" + newVar
	np.savetxt(oF,NV,fmt='%1.6E')


## Writing the new phi file

print "\nCreating the new phi file"

oF = cwd + "/" + phiFile + "_Added.phi"
oFW = open(oF,"w")

iF = cwd + "/" + phiFile + ".phi"
iFR = open(iF,"r")
currline = iFR.readline()

for ii in xrange(0,12):
	oFW.write(currline)
	currline = iFR.readline()

for ii in xrange(0,len(writeList)):
	qq = currline.strip().rfind("nul")
	currline = currline[:qq] + str(writeList[ii]) + currline[qq+4:]

oFW.write(currline)

currline = iFR.readline()

while currline!='':
	if "T" in currline or "F" in currline:
		break
	else:
		oFW.write(currline)
	currline = iFR.readline()

oFW.write(currline)
currline = iFR.readline()

for ii in xrange(0,len(writeList)):
	qq = currline.strip().rfind("F")
	currline = currline[:qq] + "T" + currline[qq+1:]

oFW.write(currline)

iFR.close()

updatedNameList = list()

for ii in xrange(0,len(namesToUse)-6):
	updatedNameList.append(namesToUse[ii])

for ii in xrange(0,len(writeList)):
	dummy = writeList[len(writeList)-ii-1]
	updatedNameList.append(dummy)

for ii in xrange(len(namesToUse)-6,len(namesToUse)):
	updatedNameList.append(namesToUse[ii])

jj = 0

pos = np.zeros(len(updatedNameList),dtype=int)

while jj < nz-1:
	for ii in xrange(0,len(updatedNameList)):
		iF = cwd + "/" + updatedNameList[ii]
		iFR = open(iF,"r")
		if jj == 0:
			iFR.seek(0,0)
		else:
			iFR.seek(pos[ii])
		currline = iFR.readline()
		pos[ii] = iFR.tell()
		s1 = currline.strip().split()
		cnt = 0
		for kk in xrange(0,len(s1)):
			if len(s1[kk])==13:
				oFW.write(s1[kk])
			else:
				oFW.write(" "+s1[kk])
			cnt = cnt + 13
			if cnt%78==0:
				oFW.write("\n")
		oFW.write("\n")
		iFR.close()
	jj = jj + 1

oFW.close()	
