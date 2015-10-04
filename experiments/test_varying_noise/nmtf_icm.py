"""
Test the performance of ICM for recovering a toy dataset, where 
we vary the level of noise.
We repeat this 10 times per fraction and average that.

We use the correct number of latent factors and flatter priors than used to generate the data.

I, J, K, L = 100, 80, 5, 5

The noise levels indicate the percentage of noise, compared to the amount of 
variance in the dataset - i.e. the inverse of the Signal to Noise ratio:
    SNR = std_signal^2 / std_noise^2
    noise = 1 / SNR
We test it for 1%, 2%, 5%, 10%, 20%, 50% noise.
"""

project_location = "/home/tab43/Documents/Projects/libraries/"
import sys
sys.path.append(project_location)

from BNMTF.code.nmtf_icm import nmtf_icm
from BNMTF.experiments.generate_toy.bnmtf.generate_bnmtf import add_noise, try_generate_M
from ml_helpers.code.mask import calc_inverse_M

import numpy, matplotlib.pyplot as plt

##########

fraction_unknown = 0.1
noise_ratios = [ 0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5 ] # 1/SNR

input_folder = project_location+"BNMTF/experiments/generate_toy/bnmtf/"

repeats = 10
iterations = 2000
I,J,K,L = 100, 80, 5, 5

alpha, beta = 1., 1.
lambdaF = numpy.ones((I,K))/10.
lambdaS = numpy.ones((K,L))/10.
lambdaG = numpy.ones((J,L))/10.
priors = { 'alpha':alpha, 'beta':beta, 'lambdaF':lambdaF, 'lambdaS':lambdaS, 'lambdaG':lambdaG }

init_S = 'random'
init_FG = 'kmeans'

minimum_TN = 0.1

metrics = ['MSE', 'R^2', 'Rp']


# Load in data
R_true = numpy.loadtxt(input_folder+"R_true.txt")


# For each noise ratio, generate mask matrices for each attempt
M_attempts = 100
all_Ms = [ 
    [try_generate_M(I,J,fraction_unknown,M_attempts) for r in range(0,repeats)]
    for noise in noise_ratios
]
all_Ms_test = [ [calc_inverse_M(M) for M in Ms] for Ms in all_Ms ]

# Make sure each M has no empty rows or columns
def check_empty_rows_columns(M,fraction):
    sums_columns = M.sum(axis=0)
    sums_rows = M.sum(axis=1)
    for i,c in enumerate(sums_rows):
        assert c != 0, "Fully unobserved row in M, row %s. Fraction %s." % (i,fraction)
    for j,c in enumerate(sums_columns):
        assert c != 0, "Fully unobserved column in M, column %s. Fraction %s." % (j,fraction)
        
for Ms in all_Ms:
    for M in Ms:
        check_empty_rows_columns(M,fraction_unknown)


# For each noise ratio, add that level of noise to the true R
all_R = []
variance_signal = R_true.var()
for noise in noise_ratios:
    tau = 1. / (variance_signal * noise)
    print "Noise: %s%%. Variance in dataset is %s. Adding noise with variance %s." % (100.*noise,variance_signal,1./tau)
    
    R = add_noise(R_true,tau)
    all_R.append(R)
    
    
# We now run the VB algorithm on each of the M's for each noise ratio    
all_performances = {metric:[] for metric in metrics} 
average_performances = {metric:[] for metric in metrics} # averaged over repeats
for (noise,R,Ms,Ms_test) in zip(noise_ratios,all_R,all_Ms,all_Ms_test):
    print "Trying noise ratio %s." % noise
    
    # Run the algorithm <repeats> times and store all the performances
    for metric in metrics:
        all_performances[metric].append([])
    for (repeat,M,M_test) in zip(range(0,repeats),Ms,Ms_test):
        print "Repeat %s of noise ratio %s." % (repeat+1, noise)
    
        BNMF = nmtf_icm(R,M,K,L,priors)
        BNMF.initialise(init_S,init_FG)
        BNMF.run(iterations,minimum_TN=minimum_TN)
    
        # Measure the performances
        performances = BNMF.predict(M_test)
        for metric in metrics:
            # Add this metric's performance to the list of <repeat> performances for this noise ratio
            all_performances[metric][-1].append(performances[metric])
            
    # Compute the average across attempts
    for metric in metrics:
        average_performances[metric].append(sum(all_performances[metric][-1])/repeats)
    

    
print "repeats=%s \nnoise_ratios = %s \nall_performances = %s \naverage_performances = %s" % \
    (repeats,noise_ratios,all_performances,average_performances)


'''
repeats=10 
noise_ratios = [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5] 
all_performances = {'R^2': [[0.999845460169911, 0.9999022715641026, 0.9999475793910907, 0.9999184056996892, 0.9999163435891139, 0.9999226601855131, 0.9999293481527641, 0.9999078687766354, 0.9999266335711907, 0.9998742200988066], [0.9880548419622303, 0.9902091931664591, 0.988040390128037, 0.9864939759655382, 0.9884615641737413, 0.9884075874943741, 0.9880847457298473, 0.9886760234821876, 0.9872214903902712, 0.9861923988337536], [0.9788792317619726, 0.976812822095893, 0.9780548300808166, 0.9747747793108394, 0.9780599005033862, 0.978885021708471, 0.9751112815654013, 0.976133826804325, 0.9786000269274711, 0.9762145251591746], [0.9454962684662657, 0.9398461290282167, 0.9438485978143312, 0.9472517907350142, 0.9395063368584395, 0.9394851841003802, 0.9496732102879967, 0.9400631038462538, 0.9533739873520835, 0.9493356711930867], [0.8780064836374761, 0.8981891187317712, 0.8819164944466622, 0.8964247836532026, 0.8766786576750065, 0.9119840988839636, 0.8960192237816988, 0.904296846961825, 0.8880862833703997, 0.8982556416925839], [0.7903466131514447, 0.7902867958732855, 0.7673546509159677, 0.7775485852662493, 0.8012036701692535, 0.7774315276275359, 0.8078119595610362, 0.7801522885032528, 0.7783181100201378, 0.7536185632693208], [0.6009785632095666, 0.6166178275701555, 0.6151859210593813, 0.5814602232402175, 0.6199320569290512, 0.5773062739453014, 0.5638790054180441, 0.6095723893425564, 0.5475397983190898, 0.5793205693974062]], 'MSE': [[0.097727968869588705, 0.064123927212889509, 0.033834792811192116, 0.045687031638371949, 0.048790257037139996, 0.034801584288425912, 0.047136893329671505, 0.05328451065540421, 0.040488997746199518, 0.066715966573012958], [6.7989136007380839, 6.4348676779072722, 6.5791685499763037, 6.5318557512594841, 6.4602064492046649, 6.4649498861786379, 6.3209774986716134, 6.9654393362451774, 6.8216651655651672, 6.7375071004621825], [13.445682639148361, 13.280786887214246, 13.776235857272606, 13.724674443676145, 12.985198479387718, 13.662920333412931, 13.897825615273716, 12.457627383187123, 14.048740694623227, 13.238416317231186], [31.221434410435275, 35.159089535960888, 34.369315834665983, 34.707639648649071, 35.37572222665775, 37.039670691380493, 33.687037063324098, 36.248600973548143, 32.508738437717199, 34.408228793413322], [70.146138744969818, 64.271213902668947, 68.091633546689565, 69.130953244573135, 72.048799607897266, 66.315836266705389, 72.569009379021907, 59.777919193837903, 70.32443151325171, 68.699111836170786], [139.95014730648265, 143.30300209580554, 135.04976740821996, 130.4543071260394, 144.19597533772742, 135.54065723293289, 130.83436299722345, 132.19449949915625, 141.00042202602509, 129.21136044153943], [323.87740331806231, 334.72926534953956, 338.08281024643003, 342.56652812222734, 355.61609904693091, 326.24512787756453, 333.45483749808847, 339.19801895407801, 342.82584575723354, 362.15245484989674]], 'Rp': [[0.9999231506198385, 0.99995149559902463, 0.99997439787438824, 0.99995975873913956, 0.99995836060925281, 0.99996158482337261, 0.99996553139979216, 0.99995416312461249, 0.99996455277755647, 0.99993796128692092], [0.99402710139966421, 0.99509303483634926, 0.99403151582801619, 0.99324288691426221, 0.99422867733038989, 0.99421568007806627, 0.99403555258532661, 0.99434645926606446, 0.99359233771422306, 0.99309119719640926], [0.98939883724825328, 0.98836370764881909, 0.98896671694262595, 0.98732952474755176, 0.98898883780580826, 0.98940439073125497, 0.98756973749821653, 0.98799931144796282, 0.98926809486819112, 0.98805197920925347], [0.97236688256324511, 0.96954936431819838, 0.97158484046108939, 0.97327516479879195, 0.96930520113442731, 0.96935304782189391, 0.97468445780276913, 0.9697806283597924, 0.97640897053242226, 0.97437097486988922], [0.93729493144923981, 0.94782021096091595, 0.9392408349962823, 0.94684983007367185, 0.93668308283978552, 0.95531559773058827, 0.94661424523492355, 0.9512276601189722, 0.94289076179150921, 0.9479070586544901], [0.89092469054961976, 0.88961022398669631, 0.8783531165110614, 0.88380924728893728, 0.89612993284432485, 0.88326707816957717, 0.89914764612761144, 0.88362118971135872, 0.88272015502158707, 0.87117358392447064], [0.78351224766892202, 0.78652453153782809, 0.78595296877452692, 0.76739682165127299, 0.78827962432679621, 0.76789919167479825, 0.75753911465408885, 0.7827784431242546, 0.74708761479598107, 0.76414858411878006]]} 
average_performances = {'R^2': [0.99990907911988169, 0.98798422113264406, 0.97715262459177521, 0.94478802796820671, 0.89298576328345902, 0.78240727643574837, 0.59117926284307687], 'MSE': [0.053259193016189629, 6.6115551016208585, 13.451810865042725, 34.472547761575228, 68.137504723578644, 136.1734501471152, 339.87483910200524], 'Rp': [0.99995509568538987, 0.99399044431487726, 0.98853411381479361, 0.97206795326625195, 0.94518442138503789, 0.88587568641352432, 0.77311191423272485]}
'''


# Plot the MSE, R^2 and Rp
for metric in metrics:
    plt.figure()
    x = noise_ratios
    y = average_performances[metric]
    plt.plot(x,y)
    plt.xlabel("Noise ratios missing")
    plt.ylabel(metric)