# ==================== Libraries ==============================
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy import stats

# Define function and index
def NSE(obs,sim): 
	ind = np.where(np.isnan(obs) == False)[0]
	M = np.mean(obs[ind])
	A = np.sum((sim[ind]-obs[ind])**2)
	B = np.sum((obs[ind]-M)**2)
	NSE = 1.-A/B
	#print(A,B,M)
	#NSE = 1.-np.sum((sim-obs)**2)/np.sum((obs-np.mean(obs))**2)
	return NSE

def RMSE(obs,sim):
	ind = np.where(np.isnan(obs) == False)[0]
	#ind = obs.notna()
	return np.sqrt(np.mean((sim[ind]-obs[ind])**2))
	
def PBIAS(obs,sim):
	ind = np.where(np.isnan(obs) == False)[0]
	#ind = obs.notna()
	return 100*(np.sum(obs[ind])-np.sum(sim[ind]))/np.sum(obs[ind])
	
def CumEr(obs,sim): # CumEr
	ind = np.where(np.isnan(obs) == False)[0]
	#ind = obs.notna()
	return np.sum(sim[ind]-obs[ind])/np.sum(obs[ind])
	
def RSR(obs,sim):
	ind = np.where(np.isnan(obs) == False)[0]
	#ind = obs.notna()
	return np.sqrt(np.sum((sim[ind]-obs[ind])**2)/np.sum((np.mean(obs[ind])-obs[ind])**2))

def RT2(obs,sim):
	ind = np.where(np.isnan(obs) == False)[0]
	#ind = obs.notna()
	n = len(ind)
	a = (n*np.sum(sim[ind]*obs[ind])-np.sum(sim[ind])*np.sum(sim[ind]))**2
	b1 = (n*np.sum(sim[ind]**2)-np.sum(sim[ind])**2)
	b2 = (n*np.sum(obs[ind]**2)-np.sum(obs[ind])**2)
	return a/(b1*b2)

def filterSM(K,sm,dt,T):
	SWI = []
	SWI.append(sm[0])
	i = 1
	SWI_0 = SWI[i-1]
	for i in range(1,len(sm)):
	
		K = K/(K+np.exp(-dt/T))
		
		if np.isnan(sm[i]) == True:
		
			SWI.append(np.nan)
			
			if i < len(sm)-1:
				#print(i)
				SWI_0 = sm[i+1]
				
		else:
		
			SWI.append(SWI_0+K*(sm[i]-SWI_0))
			
			SWI_0 = SWI[i]
		#i += 1
	#print(K)
	return(SWI)

def pearsonr(obs,sim):

	ind = np.where(np.isnan(obs) == False)[0]
	
	return stats.pearsonr(obs[ind], sim[ind])
	
def KGE(obs, sim):
	print(len(obs), len(sim))
	ind = np.where(np.isnan(obs) == False)[0]

	S_RT2 = RT2(obs[ind],sim[ind])
	
	S_mean = np.mean(sim[ind])
	
	O_mean = np.mean(obs[ind])
	
	S_std = np.std(sim[ind])
	
	O_std = np.std(obs[ind])
	
	A = (S_mean/O_mean-1)**2
	
	B = (S_std/O_std-1)**2
	
	C = (S_RT2**0.5-1)**2
	
	return (1-np.power(A+B+C,0.5))
	
def manning(n,b,y,S,m):#
		
	P = b + 2*y*(np.sqrt(1+m))
		
	T = b+2*y*m
	
	A = 0.5*y*(b+T)
	
	R = A/P
	
	V = (1/n) * np.power(R,2/3)*np.power(S,0.5)
	
	Q = A*V
	
	return Q

def confidence_interval_TS(multi_array, weight, p):
	"""confidence interval for model time series
	parameters
	multi_array:array with all model simulation for only one station
	weight:		can be Nash or other between 0-1
	p:			probability
	output
	q1, q2, q3:	min, mean, max
	"""
	q1=[]	
	q2=[]	
	q3=[]
	
	n, m = np.shape(multi_array)
	iflume=0

	for i in range(m):
		# Select soil moisture at time t_i from every valid simulation
		# Sort data from lower to highest
		ind = np.argsort(multi_array[:,i])
		y = np.array(multi_array[:,i])[ind]
		#y=np.insert((np.array(modelNash)[:,i])[ind],0,0.)
		# Assign the probability and Accumulate probability
		x = np.add.accumulate(weight[ind])
		x = (x-np.min(x))/(np.max(x)-np.min(x))
		#x=np.insert(np.add.accumulate((np.array(weight))[ind]),0,0.)
		# Normalize probability
		#x=x/x[-1]
		# define interpolation of uncertainty band
		f = interp1d(x, y, kind='linear')
		# Find 90 % interval confidence
		q1.append(f(1.-p))
		q2.append(f(0.5))
		q3.append(f(p))
	
	return q1, q2, q3
	
def wquantile(x, weight, p):
	"""confidence interval for model time series
	parameters
	multi_array:array with all model simulation for only one station
	weight:		can be Nash or other between 0-1
	p:			probability
	output
	q1, q2, q3:	min, mean, max
	"""
    # Select soil moisture at time t_i from every valid simulation
	# Sort data from lower to highest
	ind = np.argsort(x)
	y = np.array(x)[ind]
	
	# Assign the probability and Accumulate probability
	pdf = np.add.accumulate(weight[ind])
	pdf = (pdf-np.min(pdf))/(np.max(pdf)-np.min(pdf))
	
	# define interpolation of uncertainty band
	f = interp1d(pdf, y, kind='linear')
	
	# Find 90 % interval confidence
	#q1 = np.interp(1-p, y, pdf)
	#q2 = np.interp(0.5, y, pdf)
	#q3 = np.interp(p, y, pdf)
	
	q1 = (f(1.-p))
	q2 = (f(0.5))
	q3 = (f(p))
	
	return q1, q2, q3