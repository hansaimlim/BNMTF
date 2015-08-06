"""
Recover the toy dataset generated by example/generate_toy/bnmf/generate_bnmf.py
We use the parameters for the true priors.

We can plot the values Uik, Vjk, or tau, to see how the Gibbs sampler converges. 
"""

project_location = "/home/tab43/Documents/Projects/libraries/"
import sys
sys.path.append(project_location)

from BNMTF.code.bnmf_gibbs import bnmf_gibbs
from ml_helpers.code.mask import calc_inverse_M

import numpy, matplotlib.pyplot as plt

##########

input_folder = project_location+"BNMTF/example/generate_toy/bnmf/"

iterations = 1000
init = 'random'
I, J, K = 100, 50, 10 #20,10,3 #

alpha, beta = 10., 1.
lambdaU = numpy.ones((I,K))
lambdaV = numpy.ones((J,K))/2.    
priors = { 'alpha':alpha, 'beta':beta, 'lambdaU':lambdaU, 'lambdaV':lambdaV }

# Load in data
R = numpy.loadtxt(input_folder+"R.txt")
M = numpy.loadtxt(input_folder+"M.txt")
M_test = calc_inverse_M(M)

# Run the Gibbs sampler
BNMF = bnmf_gibbs(R,M,K,priors)
BNMF.initialise(init)
BNMF.run(iterations)

taus = BNMF.all_tau
Us = BNMF.all_U
Vs = BNMF.all_V

# Plot tau against iterations to see that it converges
f, axarr = plt.subplots(3, sharex=True)
x = range(1,len(taus)+1)
axarr[0].set_title('Convergence of values')
axarr[0].plot(x, taus)
axarr[0].set_ylabel("tau")
axarr[1].plot(x, Us[:,0,0])    
axarr[1].set_ylabel("U[0,0]")
axarr[2].plot(x, Vs[:,0,0]) 
axarr[2].set_ylabel("V[0,0]")
axarr[2].set_xlabel("Iterations")

# Approximate the expectations
burn_in = 500
thinning = 5
(exp_U, exp_V, exp_tau) = BNMF.approx_expectation(burn_in,thinning)

# Also measure the performances
performances = BNMF.predict(M_test,burn_in,thinning)
print performances

# Fraction 0.8 -> {'R^2': 0.5993843272108599, 'MSE': 47.053865584088975, 'Rp': 0.80084186224234466}, burnin 500, 1000 iterations
# Fraction 0.8 -> {'R^2': 0.6577436241537928, 'MSE': 37.485750341642493, 'Rp': 0.82229688740868889}, burnin 200, 3000 iterations
# Fraction 0.8 -> {'R^2': 0.5225676074319987, 'MSE': 56.076287452710268, 'Rp': 0.76294345449595236}, burnin 1000, 10000 iterations
# Fraction 0.8 -> {'R^2': 0.6922696618487401, 'MSE': 36.14412253695572, 'Rp': 0.84189442112385626}, burnin 5000, 10000 iterations
