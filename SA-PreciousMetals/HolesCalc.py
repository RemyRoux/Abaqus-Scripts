# -*- coding: utf-8 -*-
"""
Created on Wed May 11 09:49:33 2016

@author: Jack
"""

N_circles = 10;
R_react = 590*10**-3;
A=[0];
R=[0];
N=[4];
R_inlet = 50*10**-3;
A_inlet= pi*(R_inlet)**2;

holeTot = 0;
for i in range(1,N_circles+1):
    R.append(i*R_react/N_circles)
    A.append(pi*(i*R_react/N_circles)**2-pi*((i-1)*R_react/N_circles)**2)
    print str(i)+'Circle Radius: ' + str(R[i]) +'\n';
    print 'Area: ' + str(A[i])+'\n';


for i in range(1,(N_circles)):
    N.append((A[i+1]*N[i-1])/A[i])
    holeTot = holeTot+N[i];
    print str(i) + 'N circles: ' + str(N[i]);
    print 'sum: ' + str(holeTot);

A_hole=A_inlet/holeTot;

R_hole = (A_hole/pi)**0.5;
print str(R_hole);