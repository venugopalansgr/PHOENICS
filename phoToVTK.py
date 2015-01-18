## Purpose: Python code to create VTK file from PHOENICS phi file
## Usage: Run the code from command line
## Usage: python phoToVTK.py <q1FileName>
## Notes: Tested with Python 2.7
## Notes: No warranty on results. Use at your own risk/discretion
## Notes: Code is free. Appreciate feedback/acknowledging when using it
## Reference: http://www.cham.co.uk/phoenics/d_polis/d_enc/phif.htm
## Created by: Venugopalan Raghavan

import math as math
import os as os
import sys as sys

cwd = os.getcwd().replace("\\","/")

## Get the file names

fileNames = sys.argv
sFN = len(fileNames)

q1File = fileNames[sFN-1]

## Read in the q1 file

iF = cwd + "/" + q1File
iFR = open(iF,"r")
currline = iFR.readline()

yes1 = "DOM" in currline
yes2 = "SIZE" in currline

while currline!='':
	currline = iFR.readline()
	yes1 = "DOM" in currline
	yes2 = "SIZE" in currline
	if yes1 and yes2:
		break

extents = currline.split()
xExtent = float(extents[3].strip(","))
yExtent = float(extents[4].strip(","))
zExtent = float(extents[5])

iFR.close()

## Read in the phi file

phiFile = q1File.split(".q1")[0] + ".phi"

iFR = open(phiFile,"r")
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

## Write out intermediate files that contain data of all variables

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

## Writing out the VK file

oF = q1File.split(".q1")[0] + ".vtk"
oFW = open(oF,"w")

print "\nWriting VTK file"

xI = str(xstart).replace(", "," ")
yI = str(ystart).replace(", "," ")
zI = str(zstart).replace(", "," ")

oFW.write("# vtk DataFile Version 2.0\n")
oFW.write("Output\n")
oFW.write("ASCII\n")
oFW.write("DATASET RECTILINEAR GRID\n")
oFW.write("DIMENSIONS"+str(nx)+" "+str(ny)+" "+str(nz)+"\n")
oFW.write("X_COORINDATES "+str(nx)+" float\n")
oFW.write(xI[1:len(xI)-1])
oFW.write("\nY_COORINDATES "+str(ny)+" float\n")
oFW.write(yI[1:len(yI)-1])
oFW.write("Z_COORINDATES "+str(nz)+" float\n")
oFW.write(zI[1:len(zI)-1])

oFW.write("\nCELL_DATA "+str((nx-1)*(ny-1)*(nz-1))+"\n")

for tt in xrange(0,len(namesToUse)):
	iF = cwd + "/" + namesToUse[tt]
	iFR = open(iF,"r")
	oFW.write("SCALARS "+str(namesToUse[tt])+" float 1\n")
	oFW.write("LOOKUP_TABLE default\n")
	for ii in xrange(0,nz-1):
		A1 = iFR.readline().strip()
		P1A = A1.strip(" ").split()
		for jj in xrange(0,ny-1):
			for kk in xrange(0,nx-1):
				index = jj+kk*(ny-1)
				oFW.write(str(P1A[index])+"\n")
	iFR.close()

oFW.write("VECTORS vecU float \n")

iF = cwd + "/U1"
iF1 = cwd + "/V1"
iF2 = cwd + "/W1"

iFR = open(iF,"r")
iFR1 = open(iF1,"r")
iFR2 = open(iF2,"r")

dF = cwd + "/dummy"
dFW = open(dF,"w")

for ii in xrange(0,nz-1):
	A1 = iFR.readline().strip()
	A2 = iFR1.readline().strip()
	A3 = iFR2.readline().strip()
	if A1 == "":
		break
	U1A = A1.strip(" ").split()
	V1A = A2.strip(" ").split()
	W1A = A3.strip(" ").split()
	for jj in xrange(0,ny-1):
		for kk in xrange(0,nx-1):
			index = jj+kk*(ny-1)
			ux = U1A[index]
			uy = V1A[index]
			uz = W1A[index]
			oFW.write(str(ux)+" "+str(uy)+" "+str(uz)+"\n")

dFW.close()

iFR.close()
iFR1.close()
iFR2.close()

iFR = open(iF,"r")
iFR1 = open(iF1,"r")
iFR2 = open(iF2,"r")

oFW.write("SCALARS magU float 1\n")
oFW.write("LOOKUP_TABLE default\n")

for ii in xrange(0,nz-1):
	A1 = iFR.readline().strip()
	A2 = iFR1.readline().strip()
	A3 = iFR2.readline().strip()
	U1A = A1.strip(" ").split()
	V1A = A2.strip(" ").split()
	W1A = A3.strip(" ").split()
	for jj in xrange(0,ny-1):
		for kk in xrange(0,nx-1):
			index = jj+kk*(ny-1)
			ux = float(U1A[index])
			uy = float(V1A[index])
			uz = float(W1A[index])
			magU = math.sqrt(ux**2 + uy**2 + uz**2)
			oFW.write(str(magU)+"\n")

iFR.close()
iFR1.close()
iFR2.close()

oFW.close()
