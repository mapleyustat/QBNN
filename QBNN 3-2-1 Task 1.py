#author: Yidong Liao         yidong.liao@uq.net.au

import cmath
import math

from projectq.ops import Ph,ControlledGate,NOT,CNOT,H, Z, All, R, Swap, Measure, X, get_inverse, QFT, Tensor, BasicGate
from projectq.meta import Loop, Compute, Uncompute, Control

from projectq.cengines import (MainEngine,
                               AutoReplacer,
                               LocalOptimizer,
                               TagRemover,
                               DecompositionRuleSet)
from hiq.projectq.cengines import GreedyScheduler, HiQMainEngine
from hiq.projectq.backends import SimulatorMPI
import projectq.setups.decompositions
from mpi4py import MPI

theta = math.pi/8    #the incremental in phase accumulation

def qbn(eng): 
    
  #operations in the 1st layer
    CNOT | (layer1_weight_reg[0],layer1_input_reg[0])
    CNOT | (layer1_weight_reg[1],layer1_input_reg[1])  
    CNOT | (layer1_weight_reg[2],layer1_input_reg[2])
    CNOT | (layer1_weight_reg[3],layer1_input_reg[3])
    CNOT | (layer1_weight_reg[4],layer1_input_reg[4])
    CNOT | (layer1_weight_reg[5],layer1_input_reg[5])
       
    ControlledGate(NOT,3) | (layer1_input_reg[0],layer1_input_reg[1],layer1_input_reg[2],output_reg[0])  
    X|layer1_input_reg[0]
    ControlledGate(NOT,3) | (layer1_input_reg[0],layer1_input_reg[1],layer1_input_reg[2],output_reg[0])  
    X|layer1_input_reg[0]
    X|layer1_input_reg[1]
    ControlledGate(NOT,3) | (layer1_input_reg[0],layer1_input_reg[1],layer1_input_reg[2],output_reg[0])  
    X|layer1_input_reg[1]
    X|layer1_input_reg[2]
    ControlledGate(NOT,3) | (layer1_input_reg[0],layer1_input_reg[1],layer1_input_reg[2],output_reg[0])  
    X|layer1_input_reg[2]
    
    ControlledGate(NOT,3) | (layer1_input_reg[3],layer1_input_reg[4],layer1_input_reg[5],output_reg[1]) 
    X|layer1_input_reg[3]
    ControlledGate(NOT,3) | (layer1_input_reg[3],layer1_input_reg[4],layer1_input_reg[5],output_reg[1])  
    X|layer1_input_reg[3]
    X|layer1_input_reg[4]
    ControlledGate(NOT,3) | (layer1_input_reg[3],layer1_input_reg[4],layer1_input_reg[5],output_reg[1])  
    X|layer1_input_reg[4]
    X|layer1_input_reg[5]
    ControlledGate(NOT,3) | (layer1_input_reg[3],layer1_input_reg[4],layer1_input_reg[5],output_reg[1])  
    X|layer1_input_reg[5]
    
   #operations in the 2nd Layer
    CNOT | (layer2_weight_reg[0],output_reg[0])
    CNOT | (layer2_weight_reg[1],output_reg[1]) 

    ControlledGate(NOT,2) | (output_reg[0],output_reg[1],output_reg[2]) 

#The Oracle that compares output of the network and the desired ouput with respect to corresponding inputs, 
# adds a incremental phase if they are identical.
def oracle(eng):
    
    ControlledGate(Ph(theta), 2) | (output_reg[2],des_output,ancilla2)
    X|output_reg[2]
    X|des_output
    ControlledGate(Ph(theta), 2) | (output_reg[2],des_output,ancilla2)
    X|output_reg[2]
    X|des_output    
      
#The marking process--for one input: Computation with QBNN, Oracle adding phase followed by Uncomputation of QBNN
def qnn(eng):

    with Compute(eng):
        qbn(eng)

    oracle(eng)
     
    Uncompute(eng) 
    
#The marking process--accumulation for many inputs in the training set:
# We chagne the inputs for each QBNN run by applying X gates on the input register, adopting Task 2 for this instance.
def run_qnn(eng):

    qnn(eng)

    X|layer1_input_reg[0]
    X|layer1_input_reg[3]
    qnn(eng)
    X|layer1_input_reg[0]
    X|layer1_input_reg[3]

    X|layer1_input_reg[1]
    X|layer1_input_reg[4]
    qnn(eng)
    X|layer1_input_reg[1]
    X|layer1_input_reg[4]

    X|layer1_input_reg[2]
    X|layer1_input_reg[5]
    qnn(eng)
    X|layer1_input_reg[2]
    X|layer1_input_reg[5]

    X|layer1_input_reg[0]
    X|layer1_input_reg[3]
    X|layer1_input_reg[1]
    X|layer1_input_reg[4]
    X|des_output
    qnn(eng)
    X|layer1_input_reg[0]
    X|layer1_input_reg[3]
    X|layer1_input_reg[1]
    X|layer1_input_reg[4]
    X|des_output

    X|layer1_input_reg[0]
    X|layer1_input_reg[3]
    X|layer1_input_reg[2]
    X|layer1_input_reg[5]
    X|des_output
    qnn(eng)
    X|layer1_input_reg[0]
    X|layer1_input_reg[3]
    X|layer1_input_reg[2]
    X|layer1_input_reg[5]
    X|des_output

    X|layer1_input_reg[2]
    X|layer1_input_reg[5]
    X|layer1_input_reg[1]
    X|layer1_input_reg[4]
    X|des_output
    qnn(eng)
    X|layer1_input_reg[2]
    X|layer1_input_reg[5]
    X|layer1_input_reg[1]
    X|layer1_input_reg[4]
    X|des_output

    X|layer1_input_reg[0]
    X|layer1_input_reg[3]
    X|layer1_input_reg[1]
    X|layer1_input_reg[4]
    X|layer1_input_reg[2]
    X|layer1_input_reg[5]
    X|des_output
    qnn(eng)
    X|layer1_input_reg[0]
    X|layer1_input_reg[3]
    X|layer1_input_reg[1]
    X|layer1_input_reg[4]
    X|layer1_input_reg[2]
    X|layer1_input_reg[5]
    X|des_output

    

def quanutm_phase_estimation(eng):

    All(H) | phase_reg
    
    with Control(eng, phase_reg[0]):
            run_qnn(eng)                

    with Control(eng, phase_reg[1]):
        with Loop(eng,2):
            run_qnn(eng)

    with Control(eng, phase_reg[2]):
        with Loop(eng,4):
            run_qnn(eng)
            
    Swap | (phase_reg[0], phase_reg[2])
  
    get_inverse(QFT) | phase_reg

    
#Binarize the marking--According to the evaluated phase(goodness) of each weight from PE, add a minus sign on those ones that match
#the critia of optimal weights--For this instance, weights with goodness of 100% accuracy (a weight is good for all the 
#input-desired ouput pairs) are marked with a minus sign in front of them.
def add_minus_sign(eng):
 
    with Compute(eng):
          quanutm_phase_estimation(eng)
    
    X|phase_reg[1]
    X|phase_reg[0]
    ControlledGate(NOT, 3)|(phase_reg[0],phase_reg[1],phase_reg[2],ancilla_qubit)
    X|phase_reg[1]
    X|phase_reg[0]
    
    Uncompute(eng)
    
#Standard Grover's Diffusion to amplified the marked weights
def diffusion(eng):

    with Compute(eng):
            All(H) | layer1_weight_reg
            All(H) | layer2_weight_reg
            All(X) | layer1_weight_reg
            All(X) | layer2_weight_reg

    ControlledGate(Z, 7) | (layer1_weight_reg[0],layer1_weight_reg[1],layer1_weight_reg[2],layer1_weight_reg[3],layer1_weight_reg[4],layer1_weight_reg[5],layer2_weight_reg[0],layer2_weight_reg[1])

    Uncompute(eng)
    
#The whole training cycle: binarized marking + diffusion   
def run_qbnn(eng):    
    
    add_minus_sign(eng)
    
    diffusion(eng)
     

if __name__ == "__main__":

    backend = SimulatorMPI(gate_fusion=True, num_local_qubits=23)

    cache_depth = 10
    rule_set = DecompositionRuleSet(modules=[projectq.setups.decompositions])
    engines = [TagRemover()
               , LocalOptimizer(cache_depth)
               , AutoReplacer(rule_set)
               , TagRemover()
               , LocalOptimizer(cache_depth)
               , GreedyScheduler()
               ]

    eng = HiQMainEngine(backend, engines)

    if MPI.COMM_WORLD.Get_rank() == 0:

    #allocate all the qubits
       layer1_weight_reg = eng.allocate_qureg(6)   
       layer1_input_reg = eng.allocate_qureg(6)

       layer2_weight_reg = eng.allocate_qureg(2)


       output_reg = eng.allocate_qureg(3)
       des_output = eng.allocate_qubit()
       ancilla_qubit = eng.allocate_qubit()
       ancilla2 = eng.allocate_qubit()
       phase_reg = eng.allocate_qureg(3)
        
    #initialize the ancilla and weight qubits
       X | ancilla_qubit
       H | ancilla_qubit

       All(H) | layer1_weight_reg
       All(H) | layer2_weight_reg

    #run the training cycle, one should adjust the number of loops and run the whole program again to get results for different iterations 
       with Loop(eng,2):
             run_qbnn(eng)
    
       H | ancilla_qubit
       X | ancilla_qubit

       All(Measure) | layer1_weight_reg
       All(Measure) | layer2_weight_reg
    
       eng.flush()
    
       print("===========================================================================")
       print("This is the QBNN demo")
       print("The measured weight string is")
print(int(layer1_weight_reg[0]),int(layer1_weight_reg[1]),int(layer1_weight_reg[2]),int(layer1_weight_reg[3]),int(layer1_weight_reg[4]),int(layer1_weight_reg[5]),int(layer2_weight_reg[0]),int(layer2_weight_reg[1]))
   











