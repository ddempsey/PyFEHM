"""Functions for FEHM thermodynamic variables calculations."""

"""
Copyright 2013.
Los Alamos National Security, LLC. 
This material was produced under U.S. Government contract DE-AC52-06NA25396 for 
Los Alamos National Laboratory (LANL), which is operated by Los Alamos National 
Security, LLC for the U.S. Department of Energy. The U.S. Government has rights 
to use, reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR LOS 
ALAMOS NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES 
ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is modified to produce 
derivative works, such modified software should be clearly marked, so as not to 
confuse it with the version available from LANL.

Additionally, this library is free software; you can redistribute it and/or modify 
it under the terms of the GNU Lesser General Public License as published by the 
Free Software Foundation; either version 2.1 of the License, or (at your option) 
any later version. Accordingly, this library is distributed in the hope that it 
will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General 
Public License for more details.
"""

import numpy as np
from ftool import*
from scipy import interpolate

from fdflt import*
dflt = fdflt()

YEL=[ 0.25623465e-03, 0.10184405e-02, 0.22554970e-04, 0.34836663e-07, 0.41769866e-02, -0.21244879e-04, 
   0.25493516e-07, 0.89557885e-04, 0.10855046e-06, -0.21720560e-06,]
YEV=[ 0.31290881e+00, -0.10e+01, 0.25748596e-01, 0.38846142e-03, 0.11319298e-01, 0.20966376e-04, 
   0.74228083e-08, 0.19206133e-02, -0.10372453e-03, 0.59104245e-07,]
YDL=[ 0.10000000e+01, 0.17472599e-01, -0.20443098e-04, -0.17442012e-06, 0.49564109e-02, -0.40757664e-04, 
   0.50676664e-07, 0.50330978e-04, 0.33914814e-06, -0.18383009e-06,] 
YDV=[ 0.15089524e-05, 0.10000000e+01, -0.10000000e+01, -0.16676705e-02, 0.40111210e-07, 0.25625316e-10, 
  -0.40479650e-12, 0.43379623e-01, 0.24991800e-02, -0.94755043e-04,]
YVL=[ 0.17409149e-02, 0.18894882e-04, -0.66439332e-07, -0.23122388e-09, -0.31534914e-05, 0.11120716e-07, 
  -0.48576020e-10, 0.28006861e-07, 0.23225035e-09, 0.47180171e-10,] 
YVV=[-0.13920783e-03, 0.98434337e-02, -0.51504232e-03, 0.62554603e-04, 0.27105772e-04, 0.84981906e-05, 
   0.34539757e-07, -0.25524682e-03, 0, 0.12316788e-05,] 
 
ZEL=[ 0.10000000e+01, 0.23513278e-01, 0.48716386e-04, -0.19935046e-08, -0.50770309e-02, 0.57780287e-05, 
   0.90972916e-09, -0.58981537e-04, -0.12990752e-07, 0.45872518e-08,]
ZEV=[ 0.12511319e+00, -0.36061317e+00, 0.58668929e-02, 0.99059715e-04, 0.44331611e-02, 0.50902084e-05, 
  -0.10812602e-08, 0.90918809e-03, -0.26960555e-04, -0.36454880e-06,]
ZDL=[ 0.10009476e-02, 0.16812589e-04, -0.24582622e-07, -0.17014984e-09, 0.48841156e-05, -0.32967985e-07, 
   0.28619380e-10, 0.53249055e-07, 0.30456698e-09, -0.12221899e-09,]
ZDV=[ 0.12636224e+00, -0.30463489e+00, 0.27981880e-02, 0.51132337e-05, 0.59318010e-02, 0.80972509e-05, 
  -0.43798358e-07, 0.53046787e-03, -0.84916607e-05, 0.48444919e-06,]
ZVL=[ 0.10000000e+01, 0.10523153e-01, -0.22658391e-05, -0.31796607e-06, 0.29869141e-01, 0.21844248e-03, 
  -0.87658855e-06, 0.41690362e-03, -0.25147022e-05, 0.22144660e-05,]
ZVV=[ 0.10000000e+01, 0.10000000e+01, -0.10e1 , -0.10e1 , 0.10000000e+01,  0.0000000e+01,
  -0.22934622e-03, 0.10000000e+01, 0 , 0.25834551e-01,]    
  
YSP=[ 0.71725602e-03, 0.22607516e-04, 0.26178556e-05, -0.10516335e-07, 0.63167028e-09,]
YST=[-0.25048121e-05, 0.45249584e-02, 0.33551528e+00, 0.10000000e+01, 0.12254786e+00,]

ZSP=[ 0.10000000e+01, -0.22460012e-02, 0.30234492e-05, -0.32466525e-09, 0.0,]
ZST=[0.20889841e-06, 0.11587544e-03, 0.31934455e-02, 0.45538151e-02, 0.23756593e-03,]  

# co2 solubility globals, from FEHM source (params_eosco2.h)
DENC, TC, RG, PC = [467.6e0, 304.1282e0, 0.1889241e0, 7.3773e0]
A = [8.37304456e0,-3.70454304e0,2.5e0,1.99427042e0,0.62105248e0,0.41195293e0,1.04028922e0,0.08327678e0]
PHIC = [0.0e0,0.0e0,0.0e0,3.15163e0,6.1119e0,6.77708e0,11.32384e0,27.08792e0]
N = [0.38856823203161e0,0.2938547594274e1,-0.55867188534934e1,-0.76753199592477e0,0.31729005580416e0,0.54803315897767e0,
    0.12279411220335e0,0.2165896154322e1,0.15841735109724e1,-0.23132705405503e0,0.58116916431436e-1,-0.55369137205382e0,0.48946615909422e0,
    -0.24275739843501e-1,0.62494790501678e-1,-0.12175860225246e0,-0.37055685270086e0,-0.16775879700426e-1,-0.11960736637987e0,
    -0.45619362508778e-1,0.35612789270346e-1,-0.74427727132052e-2,-0.17395704902432e-2,-0.21810121289527e-1,0.24332166559236e-1,
    -0.37440133423463e-1,0.14338715756878e0,-0.13491969083286e0,-0.2315122505348e-1,0.12363125492901e-1,0.2105832197294e-2,
    -0.33958519026368e-3,0.55993651771592e-2,-0.30335118055646e-3,-0.2136548868832e3,0.26641569149272e5,-0.24027212204557e5,
    -0.28341603423999e3,0.21247284400179e3,-0.66642276540751e0,0.72608632349897e0,0.55068668612842e-1]
C = [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,3,3,3,4,4,4,4,4,4,5,6]
D = [1,1,1,1,2,2,3,1,2,4,5,5,5,6,6,6,1,1,4,4,4,7,8,2,3,3,5,5,6,7,8,10,4,8,2,2,2,3,3]
TI = [0.e0, 0.75e0,1.0e0,2.0e0,0.75e0,2.0e0,0.75e0,1.5e0,1.5e0,2.5e0,0.0e0,1.5e0,2.0e0,0.0e0,1.0e0,2.0e0,3.0e0,6.0e0,3.0e0,6.0e0,
    8.0e0,6.0e0,0.0e0,7.0e0,12.0e0,16.0e0,22.0e0,24.0e0,16.0e0,24.0e0,8.0e0,2.0e0,28.0e0,14.0e0,1.0e0,0.0e0,1.0e0,3.0e0,3.0e0]
ALPHA = [25.,25.,25.,15.,20.]
ALPHA = np.concatenate([np.zeros(34), ALPHA])
BETA = [325.,300.,300.,275.,275.,0.3,0.3,0.3]
BETA = np.concatenate([np.zeros(34), BETA])
GAMMA = [1.16,1.19,1.19,1.25,1.22]
GAMMA = np.concatenate([np.zeros(34), GAMMA])
IPSILON = [1.,1.,1.,1.,1.]
IPSILON = np.concatenate([np.zeros(34), IPSILON])
ACO2 = [3.5,3.5,3.0]
ACO2 = np.concatenate([np.zeros(39), ACO2])
BCO2 = [0.875,0.925,0.875]
BCO2 = np.concatenate([np.zeros(39), BCO2])
CAPA = [0.7,0.7,0.7]
CAPA = np.concatenate([np.zeros(39), CAPA])
CAPB = [0.3,0.3,1.]
CAPB = np.concatenate([np.zeros(39), CAPB])
CAPC = [10.,10.,12.5]
CAPC = np.concatenate([np.zeros(39), CAPC])
CAPD = [275.,275.,275.]
CAPD = np.concatenate([np.zeros(39), CAPD])
CP = [-38.640844, 5.8948420, 59.876516, 26.654627, 10.637097]

co2_interp_path = dflt.co2_interp_path

co2Vars = False
if co2_interp_path != '' and os.path.isfile(co2_interp_path): 
    co2Vars = True
if os.path.isfile('co2_interp_table.txt'):
    co2_interp_path = './co2_interp_table.txt'
    co2Vars = True

if co2Vars:
    with open(co2_interp_path,'r') as f:
        f.readline()
        line = f.readline()
        tn,pn,na = line.split()[:3]
        tn = int(tn); pn = int(pn); na = int(na)
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        # read in temperature data
        keepReading = True
        T = []
        while keepReading:
            line = f.readline()
            if '>' in line: break
            T.append(line.strip().split())
        T = list(flatten(T))
        Tval = np.array([float(t) for t in T])
        Tdict = dict([(t,i) for i,t in enumerate(Tval)])
        # read in pressure data
        P = []
        while keepReading:
            line = f.readline()
            if '>' in line: break
            P.append(line.strip().split())
        P = list(flatten(P))
        Pval = np.array([float(p) for p in P])	
        Pdict = dict([(p,i) for i,p in enumerate(Pval)])
        # read to array data
        while keepReading:
            line = f.readline()
            if '>' in line: break
        # read in array data
        arraynames = ['density','dddt','dddp','enthalpy','dhdt','dhdp','viscosity','dvdt','dvdp']
        arrays = {}
        for arrayname in arraynames:
            array = []
            while keepReading:
                line = f.readline()
                if '>' in line: break
                array.append(line.strip().split())
            array = list(flatten(array))
            array = np.array([float(a) for a in array])	
            arrays.update(dict(((arrayname,array),)))
        while keepReading:
            line = f.readline()
            if 'Number of saturation line vertices' in line: 
                n_sv = int(line.split()[0])
                break
        f.readline()
        # read in saturation line vertices
        co2_sat_P = []
        co2_sat_T = []
        co2_sat_i = []
        for n in range(n_sv):
            vs = f.readline().split()
            co2_sat_i.append(int(vs[3]))
            co2_sat_P.append(float(vs[0]))
            co2_sat_T.append(float(vs[1]))
        while keepReading:
            line = f.readline()
            if '>' in line: break
        f.readline()
        co2l_arrays = {}
        array = []
        for n in range(n_sv):
            array.append([float(v) for v in f.readline().strip().split()])
        array = np.array(array)
        for i,arrayname in enumerate(arraynames):
            co2l_arrays[arrayname] = array[:,i]
        while keepReading:
            line = f.readline()
            if '>' in line: break
        f.readline()
        co2g_arrays = {}
        array = []
        for n in range(n_sv):
            array.append([float(v) for v in f.readline().strip().split()])
        array = np.array(array)
        for i,arrayname in enumerate(arraynames):
            co2g_arrays[arrayname] = array[:,i]

    
def dens(P,T,derivative=''):
    """Return liquid water, vapor water and CO2 density, or derivatives with respect to temperature or pressure, for specified temperature and pressure.
    
    :param P: Pressure (MPa). 
    :type P: fl64
    :param T: Temperature (degC)
    :type T: fl64
    :param derivative: Supply 'T' or 'temperature' for derivatives with respect to temperature, or 'P' or 'pressure' for derivatives with respect to pressure.
    :type T: str
    :returns: Three element tuple containing (liquid, vapor, CO2) density or derivatives if requested.
    
    """
    if hasattr(P, "__len__"): 
        P = np.array(P)
    else:
        P = np.array([P])
    if hasattr(T, "__len__"): 
        T = np.array(T)
    else:
        T = np.array([T])
    # calculate water properties
    if not derivative:
        YL0 = (YDL[0] +
               YDL[1]*P +
               YDL[2]*P**2 +
               YDL[3]*P**3 +
               YDL[4]*T +
               YDL[5]*T**2 +
               YDL[6]*T**3 +
               YDL[7]*P*T +
               YDL[8]*P**2*T +
               YDL[9]*P*T**2)
        ZL0 = (ZDL[0] +
               ZDL[1]*P +
               ZDL[2]*P**2 +
               ZDL[3]*P**3 +
               ZDL[4]*T +
               ZDL[5]*T**2 +
               ZDL[6]*T**3 +
               ZDL[7]*P*T +
               ZDL[8]*P**2*T +
               ZDL[9]*P*T**2)
        YV0 = (YDV[0] +
               YDV[1]*P +
               YDV[2]*P**2 +
               YDV[3]*P**3 +
               YDV[4]*T +
               YDV[5]*T**2 +
               YDV[6]*T**3 +
               YDV[7]*P*T +
               YDV[8]*P**2*T +
               YDV[9]*P*T**2)
        ZV0 = (ZDV[0] +
               ZDV[1]*P +
               ZDV[2]*P**2 +
               ZDV[3]*P**3 +
               ZDV[4]*T +
               ZDV[5]*T**2 +
               ZDV[6]*T**3 +
               ZDV[7]*P*T +
               ZDV[8]*P**2*T +
               ZDV[9]*P*T**2)
        dens_l = YL0/ZL0
        dens_v = YV0/ZV0
    elif derivative in ['P','pressure']:
        # terms
        YL0 = (YDL[0] +
               YDL[1]*P +
               YDL[2]*P**2 +
               YDL[3]*P**3 +
               YDL[4]*T +
               YDL[5]*T**2 +
               YDL[6]*T**3 +
               YDL[7]*P*T +
               YDL[8]*P**2*T +
               YDL[9]*P*T**2)
        ZL0 = (ZDL[0] +
               ZDL[1]*P +
               ZDL[2]*P**2 +
               ZDL[3]*P**3 +
               ZDL[4]*T +
               ZDL[5]*T**2 +
               ZDL[6]*T**3 +
               ZDL[7]*P*T +
               ZDL[8]*P**2*T +
               ZDL[9]*P*T**2)
        YV0 = (YDV[0] +
               YDV[1]*P +
               YDV[2]*P**2 +
               YDV[3]*P**3 +
               YDV[4]*T +
               YDV[5]*T**2 +
               YDV[6]*T**3 +
               YDV[7]*P*T +
               YDV[8]*P**2*T +
               YDV[9]*P*T**2)
        ZV0 = (ZDV[0] +
               ZDV[1]*P +
               ZDV[2]*P**2 +
               ZDV[3]*P**3 +
               ZDV[4]*T +
               ZDV[5]*T**2 +
               ZDV[6]*T**3 +
               ZDV[7]*P*T +
               ZDV[8]*P**2*T +
               ZDV[9]*P*T**2)
        # derivatives
        YL1 = (YDL[1] +
               YDL[2]*P*2 +
               YDL[3]*P**2*3 +
               YDL[7]*T +
               YDL[8]*P*2*T +
               YDL[9]*T**2)
        ZL1 = (ZDL[1] +
               ZDL[2]*P*2 +
               ZDL[3]*P**2*3 +
               ZDL[7]*T +
               ZDL[8]*P*2*T +
               ZDL[9]*T**2)
        YV1 = (YDV[1] +
               YDV[2]*P*2 +
               YDV[3]*P**2*3 +
               YDV[7]*T +
               YDV[8]*P*2*T +
               YDV[9]*T**2)
        ZV1 = (ZDV[1] +
               ZDV[2]*P*2 +
               ZDV[3]*P**2*3 +
               ZDV[7]*T +
               ZDV[8]*P*2*T +
               ZDV[9]*T**2)
        dens_l = (ZL0*YL1-YL0*ZL1)/ZL0**2
        dens_v = (ZV0*YV1-YV0*ZV1)/ZV0**2
    elif derivative in ['T','temperature']:
        # terms
        YL0 = (YDL[0] +
               YDL[1]*P +
               YDL[2]*P**2 +
               YDL[3]*P**3 +
               YDL[4]*T +
               YDL[5]*T**2 +
               YDL[6]*T**3 +
               YDL[7]*P*T +
               YDL[8]*P**2*T +
               YDL[9]*P*T**2)
        ZL0 = (ZDL[0] +
               ZDL[1]*P +
               ZDL[2]*P**2 +
               ZDL[3]*P**3 +
               ZDL[4]*T +
               ZDL[5]*T**2 +
               ZDL[6]*T**3 +
               ZDL[7]*P*T +
               ZDL[8]*P**2*T +
               ZDL[9]*P*T**2)
        YV0 = (YDV[0] +
               YDV[1]*P +
               YDV[2]*P**2 +
               YDV[3]*P**3 +
               YDV[4]*T +
               YDV[5]*T**2 +
               YDV[6]*T**3 +
               YDV[7]*P*T +
               YDV[8]*P**2*T +
               YDV[9]*P*T**2)
        ZV0 = (ZDV[0] +
               ZDV[1]*P +
               ZDV[2]*P**2 +
               ZDV[3]*P**3 +
               ZDV[4]*T +
               ZDV[5]*T**2 +
               ZDV[6]*T**3 +
               ZDV[7]*P*T +
               ZDV[8]*P**2*T +
               ZDV[9]*P*T**2)
        # derivatives
        YL1 = (YDL[4] +
               YDL[5]*T*2 +
               YDL[6]*T**2*3 +
               YDL[7]*P +
               YDL[8]*P**2 +
               YDL[9]*P*T*2)
        ZL1 = (ZDL[4] +
               ZDL[5]*T*2 +
               ZDL[6]*T**2*3 +
               ZDL[7]*P +
               ZDL[8]*P**2 +
               ZDL[9]*P*T*2)
        YV1 = (YDV[4] +
               YDV[5]*T*2 +
               YDV[6]*T**2*3 +
               YDV[7]*P +
               YDV[8]*P**2 +
               YDV[9]*P*T*2)
        ZV1 = (ZDV[4] +
               ZDV[5]*T*2 +
               ZDV[6]*T**2*3 +
               ZDV[7]*P +
               ZDV[8]*P**2 +
               ZDV[9]*P*T*2)
        dens_l = (ZL0*YL1-YL0*ZL1)/ZL0**2
        dens_v = (ZV0*YV1-YV0*ZV1)/ZV0**2
    else: print('not a valid derivative'); return
    
    if not co2Vars: return (dens_l,dens_v,np.array([]))
    
    # calculate co2 properties
    if not derivative: k = 'density'
    elif derivative in ['P','pressure']: k = 'dddp'
    elif derivative in ['T','temperature']: k = 'dddt'
    
    arr_z = arrays[k][0:len(Pval)*len(Tval)].reshape(len(Pval),len(Tval)) 
    fdens = interpolate.interp2d( Tval, Pval, arr_z )
    dens_c = [fdens(t,p)[0] for t,p in zip(T,P)] 

    return (dens_l,dens_v,np.array(dens_c))
def enth(P,T,derivative=''):
    """Return liquid water, vapor water and CO2 enthalpy, or derivatives with respect to temperature or pressure, for specified temperature and pressure.
    
    :param P: Pressure (MPa). 
    :type P: fl64
    :param T: Temperature (degC)
    :type T: fl64
    :param derivative: Supply 'T' or 'temperature' for derivatives with respect to temperature, or 'P' or 'pressure' for derivatives with respect to pressure.
    :type T: str
    :returns: Three element tuple containing (liquid, vapor, CO2) enthalpy or derivatives if requested.
    
    """
    P = np.array(P)
    T = np.array(T)
    if not derivative:
        YL0 = (YEL[0] +
               YEL[1]*P +
               YEL[2]*P**2 +
               YEL[3]*P**3 +
               YEL[4]*T +
               YEL[5]*T**2 +
               YEL[6]*T**3 +
               YEL[7]*P*T +
               YEL[8]*P**2*T +
               YEL[9]*P*T**2)
        ZL0 = (ZEL[0] +
               ZEL[1]*P +
               ZEL[2]*P**2 +
               ZEL[3]*P**3 +
               ZEL[4]*T +
               ZEL[5]*T**2 +
               ZEL[6]*T**3 +
               ZEL[7]*P*T +
               ZEL[8]*P**2*T +
               ZEL[9]*P*T**2)
        YV0 = (YEV[0] +
               YEV[1]*P +
               YEV[2]*P**2 +
               YEV[3]*P**3 +
               YEV[4]*T +
               YEV[5]*T**2 +
               YEV[6]*T**3 +
               YEV[7]*P*T +
               YEV[8]*P**2*T +
               YEV[9]*P*T**2)
        ZV0 = (ZEV[0] +
               ZEV[1]*P +
               ZEV[2]*P**2 +
               ZEV[3]*P**3 +
               ZEV[4]*T +
               ZEV[5]*T**2 +
               ZEV[6]*T**3 +
               ZEV[7]*P*T +
               ZEV[8]*P**2*T +
               ZEV[9]*P*T**2)
        dens_l = YL0/ZL0
        dens_v = YV0/ZV0
    elif derivative in ['P','pressure']:
        # terms
        YL0 = (YEL[0] +
               YEL[1]*P +
               YEL[2]*P**2 +
               YEL[3]*P**3 +
               YEL[4]*T +
               YEL[5]*T**2 +
               YEL[6]*T**3 +
               YEL[7]*P*T +
               YEL[8]*P**2*T +
               YEL[9]*P*T**2)
        ZL0 = (ZEL[0] +
               ZEL[1]*P +
               ZEL[2]*P**2 +
               ZEL[3]*P**3 +
               ZEL[4]*T +
               ZEL[5]*T**2 +
               ZEL[6]*T**3 +
               ZEL[7]*P*T +
               ZEL[8]*P**2*T +
               ZEL[9]*P*T**2)
        YV0 = (YEV[0] +
               YEV[1]*P +
               YEV[2]*P**2 +
               YEV[3]*P**3 +
               YEV[4]*T +
               YEV[5]*T**2 +
               YEV[6]*T**3 +
               YEV[7]*P*T +
               YEV[8]*P**2*T +
               YEV[9]*P*T**2)
        ZV0 = (ZEV[0] +
               ZEV[1]*P +
               ZEV[2]*P**2 +
               ZEV[3]*P**3 +
               ZEV[4]*T +
               ZEV[5]*T**2 +
               ZEV[6]*T**3 +
               ZEV[7]*P*T +
               ZEV[8]*P**2*T +
               ZEV[9]*P*T**2)
        # derivatives
        YL1 = (YEL[1] +
               YEL[2]*P*2 +
               YEL[3]*P**2*3 +
               YEL[7]*T +
               YEL[8]*P*2*T +
               YEL[9]*T**2)
        ZL1 = (ZEL[1] +
               ZEL[2]*P*2 +
               ZEL[3]*P**2*3 +
               ZEL[7]*T +
               ZEL[8]*P*2*T +
               ZEL[9]*T**2)
        YV1 = (YEV[1] +
               YEV[2]*P*2 +
               YEV[3]*P**2*3 +
               YEV[7]*T +
               YEV[8]*P*2*T +
               YEV[9]*T**2)
        ZV1 = (ZEV[1] +
               ZEV[2]*P*2 +
               ZEV[3]*P**2*3 +
               ZEV[7]*T +
               ZEV[8]*P*2*T +
               ZEV[9]*T**2)
        dens_l = (ZL0*YL1-YL0*ZL1)/ZL0**2
        dens_v = (ZV0*YV1-YV0*ZV1)/ZV0**2
    elif derivative in ['T','temperature']:
        # terms
        YL0 = (YEL[0] +
               YEL[1]*P +
               YEL[2]*P**2 +
               YEL[3]*P**3 +
               YEL[4]*T +
               YEL[5]*T**2 +
               YEL[6]*T**3 +
               YEL[7]*P*T +
               YEL[8]*P**2*T +
               YEL[9]*P*T**2)
        ZL0 = (ZEL[0] +
               ZEL[1]*P +
               ZEL[2]*P**2 +
               ZEL[3]*P**3 +
               ZEL[4]*T +
               ZEL[5]*T**2 +
               ZEL[6]*T**3 +
               ZEL[7]*P*T +
               ZEL[8]*P**2*T +
               ZEL[9]*P*T**2)
        YV0 = (YEV[0] +
               YEV[1]*P +
               YEV[2]*P**2 +
               YEV[3]*P**3 +
               YEV[4]*T +
               YEV[5]*T**2 +
               YEV[6]*T**3 +
               YEV[7]*P*T +
               YEV[8]*P**2*T +
               YEV[9]*P*T**2)
        ZV0 = (ZEV[0] +
               ZEV[1]*P +
               ZEV[2]*P**2 +
               ZEV[3]*P**3 +
               ZEV[4]*T +
               ZEV[5]*T**2 +
               ZEV[6]*T**3 +
               ZEV[7]*P*T +
               ZEV[8]*P**2*T +
               ZEV[9]*P*T**2)
        # derivatives
        YL1 = (YEL[4] +
               YEL[5]*T*2 +
               YEL[6]*T**2*3 +
               YEL[7]*P +
               YEL[8]*P**2 +
               YEL[9]*P*T*2)
        ZL1 = (ZEL[4] +
               ZEL[5]*T*2 +
               ZEL[6]*T**2*3 +
               ZEL[7]*P +
               ZEL[8]*P**2 +
               ZEL[9]*P*T*2)
        YV1 = (YEV[4] +
               YEV[5]*T*2 +
               YEV[6]*T**2*3 +
               YEV[7]*P +
               YEV[8]*P**2 +
               YEV[9]*P*T*2)
        ZV1 = (ZEV[4] +
               ZEV[5]*T*2 +
               ZEV[6]*T**2*3 +
               ZEV[7]*P +
               ZEV[8]*P**2 +
               ZEV[9]*P*T*2)
        dens_l = (ZL0*YL1-YL0*ZL1)/ZL0**2
        dens_v = (ZV0*YV1-YV0*ZV1)/ZV0**2
    else: print('not a valid derivative'); return
    
    if not co2Vars: return (dens_l,dens_v,np.array([]))
        
    # calculate co2 properties
    if not derivative: k = 'enthalpy'
    elif derivative in ['P','pressure']: k = 'dhdp'
    elif derivative in ['T','temperature']: k = 'dhdt'
    
    if not P.shape: P = np.array([P])
    if not T.shape: T = np.array([T])
    if P.size == 1 and not T.size == 1: P = P*np.ones((1,len(T)))[0]
    elif T.size == 1 and not P.size == 1: T = T*np.ones((1,len(P)))[0]
    # calculate bounding values of P
    dens_c = []
    for Pi, Ti in zip(P,T):
        if Pi<=Pval[0]: p0 = Pval[0]; p1 = Pval[0]
        elif Pi>=Pval[-1]: p0 = Pval[-1]; p1 = Pval[-1]
        else:
            p0 = Pval[0]
            for p in Pval[1:]:
                if Pi<=p: 
                    p1 = p; break
                else: 
                    p0 = p
        # calculate bounding values of T
        if Ti<=Tval[0]: t0 = Tval[0]; t1 = Tval[0]
        elif Ti>=Tval[-1]: t0 = Tval[-1]; t1 = Tval[-1]
        else:
            t0 = Tval[0]
            for t in Tval[1:]:
                if Ti<=t: 
                    t1 = t; break
                else: 
                    t0 = t
        # calculate four indices
        dt0 = abs(Ti-t0); dt1 = abs(Ti-t1); dp0 = abs(Pi-p0); dp1 = abs(Pi-p1)
        t0 = Tdict[t0]; t1 = Tdict[t1]; p0 = Pdict[p0]; p1 = Pdict[p1]
        i1 = p0*tn+t0
        i2 = p0*tn+t1
        i3 = p1*tn+t0
        i4 = p1*tn+t1
        # locate value in array
        v1 = arrays[k][i1]
        v2 = arrays[k][i2]
        v3 = arrays[k][i3]
        v4 = arrays[k][i4]
        dens_c.append((p0*(t1*v3+t0*v4)/(t1+t0) + p1*(t1*v1+t0*v2)/(t1+t0))/(p0+p1))
    
    return (dens_l,dens_v,np.array(dens_c))
def visc(P,T,derivative=''):
    """Return liquid water, vapor water and CO2 viscosity, or derivatives with respect to temperature or pressure, for specified temperature and pressure.
    
    :param P: Pressure (MPa). 
    :type P: fl64
    :param T: Temperature (degC)
    :type T: fl64
    :param derivative: Supply 'T' or 'temperature' for derivatives with respect to temperature, or 'P' or 'pressure' for derivatives with respect to pressure.
    :type T: str
    :returns: Three element tuple containing (liquid, vapor, CO2) viscosity or derivatives if requested.
    
    """
    P = np.array(P)
    T = np.array(T)
    if not derivative:
        YL0 = (YVL[0] +
               YVL[1]*P +
               YVL[2]*P**2 +
               YVL[3]*P**3 +
               YVL[4]*T +
               YVL[5]*T**2 +
               YVL[6]*T**3 +
               YVL[7]*P*T +
               YVL[8]*P**2*T +
               YVL[9]*P*T**2)
        ZL0 = (ZVL[0] +
               ZVL[1]*P +
               ZVL[2]*P**2 +
               ZVL[3]*P**3 +
               ZVL[4]*T +
               ZVL[5]*T**2 +
               ZVL[6]*T**3 +
               ZVL[7]*P*T +
               ZVL[8]*P**2*T +
               ZVL[9]*P*T**2)
        YV0 = (YVV[0] +
               YVV[1]*P +
               YVV[2]*P**2 +
               YVV[3]*P**3 +
               YVV[4]*T +
               YVV[5]*T**2 +
               YVV[6]*T**3 +
               YVV[7]*P*T +
               YVV[8]*P**2*T +
               YVV[9]*P*T**2)
        ZV0 = (ZVV[0] +
               ZVV[1]*P +
               ZVV[2]*P**2 +
               ZVV[3]*P**3 +
               ZVV[4]*T +
               ZVV[5]*T**2 +
               ZVV[6]*T**3 +
               ZVV[7]*P*T +
               ZVV[8]*P**2*T +
               ZVV[9]*P*T**2)
        dens_l = YL0/ZL0
        dens_v = YV0/ZV0
    elif derivative in ['P','pressure']:
        # terms
        YL0 = (YVL[0] +
               YVL[1]*P +
               YVL[2]*P**2 +
               YVL[3]*P**3 +
               YVL[4]*T +
               YVL[5]*T**2 +
               YVL[6]*T**3 +
               YVL[7]*P*T +
               YVL[8]*P**2*T +
               YVL[9]*P*T**2)
        ZL0 = (ZVL[0] +
               ZVL[1]*P +
               ZVL[2]*P**2 +
               ZVL[3]*P**3 +
               ZVL[4]*T +
               ZVL[5]*T**2 +
               ZVL[6]*T**3 +
               ZVL[7]*P*T +
               ZVL[8]*P**2*T +
               ZVL[9]*P*T**2)
        YV0 = (YVV[0] +
               YVV[1]*P +
               YVV[2]*P**2 +
               YVV[3]*P**3 +
               YVV[4]*T +
               YVV[5]*T**2 +
               YVV[6]*T**3 +
               YVV[7]*P*T +
               YVV[8]*P**2*T +
               YVV[9]*P*T**2)
        ZV0 = (ZVV[0] +
               ZVV[1]*P +
               ZVV[2]*P**2 +
               ZVV[3]*P**3 +
               ZVV[4]*T +
               ZVV[5]*T**2 +
               ZVV[6]*T**3 +
               ZVV[7]*P*T +
               ZVV[8]*P**2*T +
               ZVV[9]*P*T**2)
        # derivatives
        YL1 = (YVL[1] +
               YVL[2]*P*2 +
               YVL[3]*P**2*3 +
               YVL[7]*T +
               YVL[8]*P*2*T +
               YVL[9]*T**2)
        ZL1 = (ZVL[1] +
               ZVL[2]*P*2 +
               ZVL[3]*P**2*3 +
               ZVL[7]*T +
               ZVL[8]*P*2*T +
               ZVL[9]*T**2)
        YV1 = (YVV[1] +
               YVV[2]*P*2 +
               YVV[3]*P**2*3 +
               YVV[7]*T +
               YVV[8]*P*2*T +
               YVV[9]*T**2)
        ZV1 = (ZVV[1] +
               ZVV[2]*P*2 +
               ZVV[3]*P**2*3 +
               ZVV[7]*T +
               ZVV[8]*P*2*T +
               ZVV[9]*T**2)
        dens_l = (ZL0*YL1-YL0*ZL1)/ZL0**2
        dens_v = (ZV0*YV1-YV0*ZV1)/ZV0**2
    elif derivative in ['T','temperature']:
        # terms
        YL0 = (YVL[0] +
               YVL[1]*P +
               YVL[2]*P**2 +
               YVL[3]*P**3 +
               YVL[4]*T +
               YVL[5]*T**2 +
               YVL[6]*T**3 +
               YVL[7]*P*T +
               YVL[8]*P**2*T +
               YVL[9]*P*T**2)
        ZL0 = (ZVL[0] +
               ZVL[1]*P +
               ZVL[2]*P**2 +
               ZVL[3]*P**3 +
               ZVL[4]*T +
               ZVL[5]*T**2 +
               ZVL[6]*T**3 +
               ZVL[7]*P*T +
               ZVL[8]*P**2*T +
               ZVL[9]*P*T**2)
        YV0 = (YVV[0] +
               YVV[1]*P +
               YVV[2]*P**2 +
               YVV[3]*P**3 +
               YVV[4]*T +
               YVV[5]*T**2 +
               YVV[6]*T**3 +
               YVV[7]*P*T +
               YVV[8]*P**2*T +
               YVV[9]*P*T**2)
        ZV0 = (ZVV[0] +
               ZVV[1]*P +
               ZVV[2]*P**2 +
               ZVV[3]*P**3 +
               ZVV[4]*T +
               ZVV[5]*T**2 +
               ZVV[6]*T**3 +
               ZVV[7]*P*T +
               ZVV[8]*P**2*T +
               ZVV[9]*P*T**2)
        # derivatives
        YL1 = (YVL[4] +
               YVL[5]*T*2 +
               YVL[6]*T**2*3 +
               YVL[7]*P +
               YVL[8]*P**2 +
               YVL[9]*P*T*2)
        ZL1 = (ZVL[4] +
               ZVL[5]*T*2 +
               ZVL[6]*T**2*3 +
               ZVL[7]*P +
               ZVL[8]*P**2 +
               ZVL[9]*P*T*2)
        YV1 = (YVV[4] +
               YVV[5]*T*2 +
               YVV[6]*T**2*3 +
               YVV[7]*P +
               YVV[8]*P**2 +
               YVV[9]*P*T*2)
        ZV1 = (ZVV[4] +
               ZVV[5]*T*2 +
               ZVV[6]*T**2*3 +
               ZVV[7]*P +
               ZVV[8]*P**2 +
               ZVV[9]*P*T*2)
        dens_l = (ZL0*YL1-YL0*ZL1)/ZL0**2
        dens_v = (ZV0*YV1-YV0*ZV1)/ZV0**2
    else: print('not a valid derivative'); return
    
    # calculate co2 properties
    if not derivative: k = 'viscosity'
    elif derivative in ['P','pressure']: k = 'dvdp'
    elif derivative in ['T','temperature']: k = 'dvdt'
    
    if not co2Vars: return (dens_l,dens_v,np.array([]))
    
    if not P.shape: P = np.array([P])
    if not T.shape: T = np.array([T])
    if P.size == 1 and not T.size == 1: P = P*np.ones((1,len(T)))[0]
    elif T.size == 1 and not P.size == 1: T = T*np.ones((1,len(P)))[0]
    # calculate bounding values of P
    dens_c = []
    for Pi, Ti in zip(P,T):
        if Pi<=Pval[0]: p0 = Pval[0]; p1 = Pval[0]
        elif Pi>=Pval[-1]: p0 = Pval[-1]; p1 = Pval[-1]
        else:
            p0 = Pval[0]
            for p in Pval[1:]:
                if Pi<=p: 
                    p1 = p; break
                else: 
                    p0 = p
        # calculate bounding values of T
        if Ti<=Tval[0]: t0 = Tval[0]; t1 = Tval[0]
        elif Ti>=Tval[-1]: t0 = Tval[-1]; t1 = Tval[-1]
        else:
            t0 = Tval[0]
            for t in Tval[1:]:
                if Ti<=t: 
                    t1 = t; break
                else: 
                    t0 = t
        # calculate four indices
        dt0 = abs(Ti-t0); dt1 = abs(Ti-t1); dp0 = abs(Pi-p0); dp1 = abs(Pi-p1)
        t0 = Tdict[t0]; t1 = Tdict[t1]; p0 = Pdict[p0]; p1 = Pdict[p1]
        i1 = p0*tn+t0
        i2 = p0*tn+t1
        i3 = p1*tn+t0
        i4 = p1*tn+t1
        # locate value in array
        v1 = arrays[k][i1]
        v2 = arrays[k][i2]
        v3 = arrays[k][i3]
        v4 = arrays[k][i4]
        dens_c.append((p0*(t1*v3+t0*v4)/(t1+t0) + p1*(t1*v1+t0*v2)/(t1+t0))/(p0+p1))
    
    return (dens_l,dens_v,np.array(dens_c)*1e-6)
def sat(T):
    """Return saturation pressure and first derivative for given temperature.
    
    :param T: Temperature (degC)
    :type T: fl64
    :returns: Two element tuple containing (saturation pressure, derivative).
    
    """
    Y0 = (YSP[0]+
          YSP[1]*T+
          YSP[2]*T**2+
          YSP[3]*T**3+
          YSP[4]*T**4)
    Z0 = (ZSP[0]+
          ZSP[1]*T+
          ZSP[2]*T**2+
          ZSP[3]*T**3+
          ZSP[4]*T**4)
    Y1 = (YSP[1]+
          YSP[2]*T*2+
          YSP[3]*T**2*3+
          YSP[4]*T**3*4)
    Z1 = (ZSP[1]+
          ZSP[2]*T*2+
          ZSP[3]*T**2*3+
          ZSP[4]*T**3*4)
    satP = Y0/Z0
    dsatPdT = (Z0*Y1-Y0*Z1)/Z0**2
    return (satP, dsatPdT)
def tsat(P):
    """Return saturation temperature and first derivative for given pressure.
    
    :param P: Pressure (degC)
    :type P: fl64
    :returns: Two element tuple containing (saturation temperature, derivative).
    
    """
    Y0 = (YST[0]+
          YST[1]*P+
          YST[2]*P**2+
          YST[3]*P**3+
          YST[4]*P**4)
    Z0 = (ZST[0]+
          ZST[1]*P+
          ZST[2]*P**2+
          ZST[3]*P**3+
          ZST[4]*P**4)
    Y1 = (YST[1]+
          YST[2]*P*2+
          YST[3]*P**2*3+
          YST[4]*P**3*4)
    Z1 = (ZST[1]+
          ZST[2]*P*2+
          ZST[3]*P**2*3+
          ZST[4]*P**3*4)
    satT = Y0/Z0
    dsatTdP = (Z0*Y1-Y0*Z1)/Z0**2
    return (satT, dsatTdP)
def fluid_column(z,Tgrad,Tsurf,Psurf,iterations = 3):
    '''Calculate thermodynamic properties of a column of fluid.
    
    :param z: Vector of depths at which to return properties. If z does not begin at 0, this will be prepended.
    :type z: ndarray
    :param Tgrad: Temperature gradient in the column (degC / m).
    :type Tgrad: fl64
    :param Tsurf: Surface temperature (degC).
    :type Tsurf: fl64
    :param Psurf: Surface pressure (MPa).
    :type Psurf:
    :param iterations: Number of times to recalculate column pressure based on updated density.
    :type iterations: int
    :returns: Three element tuple containing (liquid, vapor, CO2) properties. Each contains a three column array corresponding to pressure, temperature, density, enthalpy and viscosity of the fluid.
    
    '''
    z = abs(np.array(z))
    
    if z[-1] < z[0]: z = np.flipud(z)
    if z[0] != 0: z = np.array([0,]+list(z))
    
    if isinstance(Tgrad,str): 		# interpret Tgrad as a down well temperature profile
        if not os.path.isfile(Tgrad): print('ERROR: cannot find temperature gradient file \''+Tgrad+'\'.'); return
        
        tempfile = open(Tgrad,'r')
        ln = tempfile.readline()
        tempfile.close()
        commaFlag = False; spaceFlag = False
        if len(ln.split(',')) > 1: commaFlag = True
        elif len(ln.split()) > 1: spaceFlag = True
        if not commaFlag and not spaceFlag: print('ERROR: incorrect formatting for \''+Tgrad+'\'. Expect first column depth (m) and second column temperature (degC), either comma or space separated.'); return
        if commaFlag: tempdat = np.loadtxt(Tgrad,delimiter=',')
        else: tempdat = np.loadtxt(Tgrad)
        zt = tempdat[:,0]; tt = tempdat[:,1]
        
        T = np.interp(z,zt,tt)
        
    else:
        Tgrad = abs(Tgrad)
        T = Tsurf + Tgrad*z
    Pgrad = 800*9.81/1e6
    Phgrad = 1000*9.81/1e6
    if co2Vars:
        Pco2 = Psurf + Pgrad*z
    Ph = Psurf + Phgrad*z
    
    for i in range(iterations):
        if co2Vars:
            rho = dens(Pco2,T)[2]
            Pco2=np.array([(abs(np.trapz(rho[:i+1],z[:i+1]))*9.81/1e6)+Pco2[0] for i in range(len(rho))])
        rho = dens(Ph,T)[0]
        Ph=np.array([(abs(np.trapz(rho[:i+1],z[:i+1]))*9.81/1e6)+Ph[0] for i in range(len(rho))])
    
    if co2Vars:
        rho = dens(Pco2,T)
        H = enth(Pco2,T)
        mu = visc(Pco2,T)
    
    rhoh = dens(Ph,T)
    Hh = enth(Ph,T)
    muh = visc(Ph,T)
    
    if co2Vars:
        return (np.array([Ph,T,rhoh[0],Hh[0],muh[0]]).T,np.array([Ph,T,rhoh[1],Hh[1],muh[1]]).T,np.array([Pco2,T,rho[2],H[2],mu[2]]).T)
    else:
        return (np.array([Ph,T,rhoh[0],Hh[0],muh[0]]).T,np.array([Ph,T,rhoh[1],Hh[1],muh[1]]).T,np.array([]))

def co2_dens_sat_line(derivative=''):
    """Return CO2 density, or derivatives with respect to temperature or pressure, for specified temperature and pressure near the CO2 saturation line.
    
    :param P: Pressure (MPa). 
    :type P: fl64
    :param T: Temperature (degC)
    :type T: fl64
    :param derivative: Supply 'T' or 'temperature' for derivatives with respect to temperature, or 'P' or 'pressure' for derivatives with respect to pressure.
    :type T: str
    :returns: Three element tuple containing (liquid, vapor, CO2) density or derivatives if requested.
    
    """

    if not co2Vars: 
        print("Error: CO2 property table not found")
        return
    
    # calculate co2 properties
    if not derivative: k = 'density'
    elif derivative in ['P','pressure']: k = 'dddp'
    elif derivative in ['T','temperature']: k = 'dddt'
    
    print('P T liquid-'+k+' gas-'+k)
    for p,t,l,g in zip(co2_sat_P, co2_sat_T, co2l_arrays[k], co2g_arrays[k]):
        print(p,t,l,g)

    return list(zip(co2_sat_P, co2_sat_T, co2l_arrays[k], co2g_arrays[k]))

def theta(i,del2,tau2):
    return (1.e0-tau2)+(CAPA[i]*(((del2-1.e0)**2.e0)**(1.e0/(2.e0*BETA[i]))))

def psi(i,del2,tau2):
    psi=-(CAPC[i]*((del2-1.e0)**2.e0))-(CAPD[i]*((tau2-1.e0)**2.e0))
    return np.exp(psi)

def dpsiddel(i,del2,tau2):
    psi1=psi(i,del2,tau2)
    return -2.e0*CAPC[i]*(del2-1.e0)*psi1

def capdel(i,del2,tau2):
    theta1=theta(i,del2,tau2)
    return (theta1*theta1)+(CAPB[i]*(((del2-1.e0)**2.e0)**ACO2[i]))

def ddelbiddel(i,del2,tau2):
    capdel1=capdel(i,del2,tau2)
    ddd=dcapdelddel(i,del2,tau2)
    return BCO2[i]*(capdel1**(BCO2[i]-1.e0))*ddd

def dcapdelddel(i,del2,tau2):
    theta1=theta(i,del2,tau2)
    out=((del2-1.e0)*((CAPA[i]*theta1*(2.e0/BETA[i])*
    ((del2-1.e0)**2.e0)**((1/(2.e0*BETA[i]))-1.e0))+(2.e0*CAPB[i]*ACO2[i]*
    (((del2-1.e0)**2.e0)**(ACO2[i]-1.e0)))))
    return out

def phir(del2, tau2):
    r_helm = 0.0e0

    for i in range(7):
        r_helm = r_helm+(N[i]*(del2**D[i])*(tau2**TI[i]))        

    for i in range(7, 34):
        r_helm = r_helm+(N[i]*(del2**D[i])*(tau2**TI[i])*np.exp(-del2**C[i])) 

    for i in range(34,39):
        r_helm = (r_helm+(N[i]*(del2**D[i])*(tau2**TI[i])*
        np.exp((-ALPHA[i]*((del2-IPSILON[i])**2))-(BETA[i]*
        ((tau2-GAMMA[i])**2)))))

    for i in range(39,42):
        psi1=psi(i,del2,tau2)
        capdel1=capdel(i,del2,tau2)

        r_helm=r_helm+(N[i]*(capdel1**BCO2[i])*del2*psi1)

    return r_helm

def dphirddel(del2,tau2):
    derdr_helm = 0.0e0
    for i in range(7):
        derdr_helm=derdr_helm+(N[i]*D[i]*(del2**(D[i]-1.e0))*(tau2**TI[i]))
    
    for i in range(7,34):
        derdr_helm=(derdr_helm+(N[i]*(del2**(D[i]-1.e0))*(tau2**TI[i])
            *np.exp(-del2**C[i])*(D[i]-(C[i]*(del2**C[i])))))
    
    for i in range(34, 39):
        derdr_helm = (derdr_helm+(N[i]*(del2**D[i])*(tau2**TI[i])*
        np.exp((-ALPHA[i]*((del2-IPSILON[i])**2.0e0))-(BETA[i]*
        ((tau2-GAMMA[i])**2.0e0)))*
        ((D[i]/del2)-(2.0e0*ALPHA[i]*(del2-IPSILON[i])))))
        
    for i in range(39, 42):
        psi1=psi(i,del2,tau2)
        capdel1=capdel(i,del2,tau2)
        dsidd=dpsiddel(i,del2,tau2)
        ddelbdd=ddelbiddel(i,del2,tau2)
        derdr_helm=(derdr_helm+(N[i]*(((capdel1**BCO2[i])*(psi1+
            (del2*dsidd)))+(del2*psi1*ddelbdd))))
    
    return derdr_helm

def co2_fugacity(var2,var3):
    dell = var3/DENC
    tau = TC/var2

    fir = phir(dell,tau)
    fird = dphirddel(dell,tau)
    fg1 = np.exp(fir+(dell*fird)-np.log(1.e0+(dell*fird)))

    return fg1

def mco2(P,T,nc=0.):
    '''
        P = pressure (MPa)
        T = tempearture (degC)
        nc = NaCl content (mol/kg)

        return solubility in kg CO2 / kg H2O
    '''

    # calculate the dissolved CO2 concentration based on Duan (2003) eqn.
    # need to calculate fugacity first based on the density.
    c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15 = np.zeros(15)

    # added fugacity calculation from Duan 2006 paper formulation
    # equation 2.
    P = np.max([P,1.e-3])
    t = T + 273.15  # convert to K
    p = P*10.       # convert to bar
    mol = nc#/58.443e3  # convert to mol/kg

    if ((t>273.e0)and(t<573.e0)):
        if (t<TC):
            a1 = -7.0602087e0
            a2 = 1.9391218e0
            a3 = -1.6463597e0
            a4 = -3.2995634
            nu = 1.e0-(t/TC)
            ps1 = a1*nu+(a2*(nu**1.5e0))+(a3*(nu**2.e0))+(a4*(nu**4.e0))
            ps2 = a1+(1.5e0*a2*(nu**0.5e0))+(2.0e0*a3*nu)+(4.e0*a4*(nu**3.e0))
            ps = ps1*TC/t
            ps = np.exp(ps)*PC
            p1 = ps
        elif ((t>TC)and(t<405.e0)):
            p1 = 75.e0+(t-TC)*1.25e0
        elif (t>405.e0):
            p1 = 200.e0
        
        if( p<p1):
            c1 = 1.e0
            c2 = 4.7586835e-3
            c3 = -3.3569963e-6
            c5 = -1.3179356
            c6 = -3.8389101e-6
            c8 = 2.2815104e-3
        elif (t<340.e0):
            if(p<1000):
                c1 = -7.1734882e-1
                c2 = 1.5985379e-4
                c3 = -4.9286471e-7
                c6 = -2.7855285e-7
                c7 = 1.1877015e-9
                c12 = -96.539512
                c13 = 4.4774938e-1
                c14 = 101.81078e0
                c15 = 5.3783879e-6
            else:
                c1 = -6.5129019e-2
                c2 = -2.1429977e-4
                c3 = -1.144493e-6
                c6 = -1.1558081e-7
                c7 = 1.195237e-9
                c12 = -221.34306e0
                c14 = 71.820393e0
                c15 = 6.6089246e-6
            
        elif (t<435.e0):
            if (p<1000):
                c1 = 5.0383896e0
                c2 = -4.4257744e-3
                c4 = 1.9572733e0
                c6 = 2.4223436e-6
                c8 = -9.3796135e-4
                c9 = -1.502603e0
                c10 = 3.027224e-3
                c11 = -31.377342e0
                c12 = -12.847063e0
                c15 = -1.5056648e-5
            else:
                c1 = -16.063152e0
                c2 = -2.705799e-3
                c4 = 1.4119239e-1
                c6 = 8.1132965e-7
                c8 = -1.1453082e-4
                c9 = 2.3895671e0
                c10 = 5.0527457e-4
                c11 = -17.76346e0
                c12 = 985.92232e0
                c15 = -5.4965256e-7
        else:
            c1 = -1.569349e-1
            c2 = 4.4621407e-4
            c3 = -9.1080591e-7
            c6 = 1.0647399e-7
            c7 = 2.4273357e-10
            c9 = 3.5874255e-1
            c10 = 6.3319710e-5
            c11 = -249.89661e0
            c14 = 888.768e0
            c15 = -6.6348003e-7

    fg = co2_fugacity(t,dens(P,T)[-1][0])
        
    liq_cp = (28.9447706e0 + (-0.0354581768e0*t) + (-4770.67077e0/t)  
        +(1.02782768e-5*t*t) + (33.8126098/(630-t)) + (9.0403714e-3*p)  
        +(-1.14934031e-3*p*np.log(t)) + (-0.307405726*p/t)  
        + (-0.0907301486*p/(630.e0-t))   
        + (9.32713393e-4*p*p/((630.e0-t)**2.e0)))

    # changed the above line not multiplied by 2 before
    lambdaco2_na = (-0.411370585e0 + (6.07632013e-4*t) 
        + (97.5347708e0/t) + (-0.0237622469e0*p/t)  
        + (0.0170656236*p/(630.e0-t)) + (1.41335834e-5*t*np.log(p)))

    tauco2_na_cl = (3.36389723e-4 + (-1.9829898e-5*t)  
        + (2.1222083e-3*p/t) + (-5.24873303e-3*p/(630.e0-t)))

    rhs = liq_cp + (2.e0*lambdaco2_na*mol) + (tauco2_na_cl*mol*mol)

    # tt = (t-647.29)/647.29
    # Ph20 = 220.85*t/647.29*(1.+CP[0]*(-tt)**1.9+CP[1]*t+CP[2]*t**2+CP[3]*t**3+CP[4]*t**4)
    # yco2 = (p-Ph20)/p
    yco2 = 1.
    mco21 = yco2*fg*p*44.e-3
    mco2 = mco21/(mco21*0+np.exp(rhs))

    return mco2

def dens_co2(P,T):
    Mco2=0.044 # kg/mol
    rho=dens(P,T)[0][0]  # kg/m3
    c=mco2(P,T) #kg co2/ kg h2o
    c=c*rho/Mco2 # mol/m3
    Vphi=(37.51-9.585e-2*T+8.74e-4*T**2-5.044e-7*T**3)/(100**3) #apparent molar volume
    rho_co2=rho+Mco2*c-c*rho*Vphi # density
    print(rho,rho_co2,(rho_co2/rho-1.)*100)    

def test_co2_sol():
    P = 5.
    T = 45.
    #print(mco2(0.1,25),mco2(50.,100))
    print(mco2(5.,140), mco2(5.,140)*(1/44)/(1./18))
    dens_co2(5,140)
    #print(mco2(0.1,20))
    # print(mco2(1,25)*18/44*10000,mco2(50.,100)*18/44*10000)
    # print(mco2(1,25)*18/44,mco2(50.,100)*18/44)
    #print(mco2(1.96,140), mco2(5,140)/mco2(1.96,140), mco2(5,45)/mco2(1.96,140), mco2(0.3,45)/mco2(1.96,140))
    
    return
    from matplotlib import pyplot as plt
    f,ax = plt.subplots(1,1)
    P = np.linspace(1,200,101)
    # ax.plot(P, [mco2(Pi,573.15-273.15, 1.09)/44.e-3 for Pi in P], 'k-')
    # ax.plot(P, [mco2(Pi,573.15-273.15, 4.)/44.e-3 for Pi in P], 'b-')
    T = np.linspace(280,520,50)
    for P in [5,10,20,50,100]:
        ax.plot(T, [mco2(P,Ti-273.15,0)/44.e-3 for Ti in T], 'k-')
    plt.show()

def check_enthalpy_formulation():
    P,T = [5, 100.]
    rho = dens(P,T)[-1][0]
    drho_dP = dens(P,T,'P')[-1][0]
    drho_dT = dens(P,T,'T')[-1][0]
    h = enth(P,T)[-1][0]
    dh_dP = enth(P,T,'P')[-1][0]
    dh_dT = enth(P,T,'T')[-1][0]

    print(rho, drho_dP, drho_dT, h, dh_dP, dh_dT)
    print(dh_dP, h*drho_dP, -h/rho*drho_dP, 1./rho-P/rho**2*drho_dP)

def run_tests():
    test_co2_sol()
    # check_enthalpy_formulation()

if __name__ == "__main__":
    run_tests()