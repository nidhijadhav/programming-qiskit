## import the necessary tools for our work
%matplotlib inline
from IPython.display import clear_output
from  qiskit import *
from qiskit.visualization import plot_histogram
import numpy as np
import matplotlib.pyplot as plotter
from qiskit.tools.monitor import job_monitor
import seaborn as sns, operator
sns.set_style("dark")
pi = np.pi

## Code for inverse Quantum Fourier Transform adapted from Qiskit Textbook at qiskit.org/textbook
def qft_dagger(circ_, n_qubits):
    """n-qubit QFTdagger the first n qubits in circ"""
    for qubit in range(int(n_qubits/2)):
        circ_.swap(qubit, n_qubits-qubit-1)
    for j in range(0,n_qubits):
        for m in range(j):
            circ_.cu1(-np.pi/float(2**(j-m)), m, j)
        circ_.h(j)

## Code for initial state of Quantum Phase Estimation adapted from Qiskit Textbook at qiskit.org/textbook
def qpe_pre(circ_, n_qubits):
    circ_.h(range(n_qubits))
    circ_.x(n_qubits)

    for x in reversed(range(n_qubits)):
        for _ in range(2**(n_qubits-1-x)):
            circ_.cu1(1, n_qubits-1-x, n_qubits)
            
## Run a Qiskit job on either hardware or simulators
def run_job(circ_, backend_, shots_=1000, optimization_level_=0):
    job = execute(circ_, backend=backend_, shots=shots_, optimization_level=optimization_level_)
    job_monitor(job)
    return job.result().get_counts(circ_)
#load account    
IBMQ.load_account()
simulator_cloud = IBMQ.get_provider(hub='ibm-q',group='open',project='main').get_backend('ibmq_qasm_simulator')
simulator = Aer.get_backend('qasm_simulator')
device = IBMQ.get_provider(hub='ibm-q',group='open',project='main').get_backend('ibmq_16_melbourne')

## Function to estimate pi
def get_pi_estimate(n_qubits):

    # create the circuit
    circ = QuantumCircuit(n_qubits + 1, n_qubits)
    # create the input state
    qpe_pre(circ, n_qubits)
    # apply a barrier
    circ.barrier()
    # apply the inverse fourier transform
    qft_dagger(circ, n_qubits)
    # apply  a barrier
    circ.barrier()
    # measure all but the last qubits
    circ.measure(range(n_qubits), range(n_qubits))
    
    if n_qubits < 10:
        circ.draw(output='mpl').savefig(str(n_qubits)+'_qubit_circuit.png')

    # run the job and get the results
    counts = run_job(circ, backend_=simulator, shots_=10000, optimization_level_=0)
    # print(counts) 

    # get the count that occurred most frequently
    max_counts_result = max(counts, key=counts.get)
    max_counts_result = int(max_counts_result, 2)
    
    # solve for pi from the measured counts
    theta = max_counts_result/2**n_qubits
    return (1./(2*theta))

# estimate pi using different numbers of qubits
nqs = list(range(2,12+1))
pi_estimates = []
for nq in nqs:
    thisnq_pi_estimate = get_pi_estimate(nq)
    pi_estimates.append(thisnq_pi_estimate)
    print(f"{nq} qubits, pi ≈ {thisnq_pi_estimate}")
    
# plot the results
plotter.plot(nqs, [pi]*len(nqs), '--r')
plotter.plot(nqs, pi_estimates, '.-', markersize=12)
plotter.xlim([1.5, 12.5])
plotter.ylim([1.5, 4.5])
plotter.legend(['$\pi$', 'estimate of $\pi$'])
plotter.xlabel('Number of qubits', fontdict={'size':20})
plotter.ylabel('$\pi$ and estimate of $\pi$', fontdict={'size':20})
plotter.tick_params(axis='x', labelsize=12)
plotter.tick_params(axis='y', labelsize=12)
plotter.show()
