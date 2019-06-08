
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 13:15:41 2019

@author: Phylyd
"""

import sys
import numpy as np
import cmath
import math

from hiq.ops import Ph,ControlledGate,NOT,CNOT,H, Z, All, R, Swap, Measure, X, get_inverse, QFT, Tensor, BasicGate
from hiq.meta import Loop, Compute, Uncompute, Control

from hiq.backends import CircuitDrawer, CommandPrinter, Simulator
from hiq.cengines import (MainEngine,
                               AutoReplacer,
                               LocalOptimizer,
                               TagRemover,
                               DecompositionRuleSet)
import ctypes
ctypes.CDLL("libmpi.so", mode=ctypes.RTLD_GLOBAL)

from huawei.hiq.cengines import GreedyScheduler
import hiq.setups.decompositions

theta = math.pi/8


def qbn(eng): 

    CNOT | (layer1_weight_reg[0],layer1_input_reg[0])
    CNOT | (layer1_weight_reg[1],layer1_input_reg[1])  
    
    ControlledGate(NOT,2) | (layer1_input_reg[0],layer1_input_reg[1],output_reg[0]) 
       
    CNOT | (layer1_weight_reg[2],layer1_input_reg[2])
    CNOT | (layer1_weight_reg[3],layer1_input_reg[3])  
    
    ControlledGate(NOT,2) | (layer1_input_reg[2],layer1_input_reg[3],output_reg[1]) 
    
    CNOT | (layer2_weight_reg[0],output_reg[0])
    CNOT | (layer2_weight_reg[1],output_reg[1]) 

    ControlledGate(NOT,2) | (output_reg[0],output_reg[1],output_reg[2]) 
    
def oracle(eng):
    
    ControlledGate(Ph(theta), 2) | (output_reg[2],des_output,ancilla2)
    X|output_reg[2]
    X|des_output
    ControlledGate(Ph(theta), 2) | (output_reg[2],des_output,ancilla2)
    X|output_reg[2]
    X|des_output    
      
    
def qnn(eng):

    with Compute(eng):
        qbn(eng)

    oracle(eng)
     
    Uncompute(eng) 
    
    
def run_qnn(eng):

    qnn(eng)

    X|layer1_input_reg[0]
    X|layer1_input_reg[2]
    qnn(eng)
    X|layer1_input_reg[0]
    X|layer1_input_reg[2]

    X|layer1_input_reg[1]
    X|layer1_input_reg[3]
    qnn(eng)
    X|layer1_input_reg[1]
    X|layer1_input_reg[3]

    X|layer1_input_reg[0]
    X|layer1_input_reg[2]
    X|layer1_input_reg[1]
    X|layer1_input_reg[3]
    X|des_output
    qnn(eng)
    X|layer1_input_reg[0]
    X|layer1_input_reg[2]
    X|layer1_input_reg[1]
    X|layer1_input_reg[3]
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

def add_minus_sign(eng):

    with Compute(eng):
          quanutm_phase_estimation(eng)
    
    X|phase_reg[1]
    X|phase_reg[0]
    ControlledGate(NOT, 3)|(phase_reg[0],phase_reg[1],phase_reg[2],ancilla_qubit)
    X|phase_reg[1]
    X|phase_reg[0]
    
    Uncompute(eng)
    
def diffusion(eng):

    with Compute(eng):
            All(H) | layer1_weight_reg
            All(H) | layer2_weight_reg
            All(X) | layer1_weight_reg
            All(X) | layer2_weight_reg

    ControlledGate(Z, 5) | (layer1_weight_reg[0],layer1_weight_reg[1],layer1_weight_reg[2],layer1_weight_reg[3],layer2_weight_reg[0],layer2_weight_reg[1])

    Uncompute(eng)
    
def run_qbnn(eng):    
    
    add_minus_sign(eng)
    
    diffusion(eng)
    

if __name__ == "__main__":
    
    eng = MainEngine(backend = Simulator(rnd_seed = 1))

    layer1_weight_reg = eng.allocate_qureg(4)
    layer1_input_reg = eng.allocate_qureg(4)

    layer2_weight_reg = eng.allocate_qureg(2)


    output_reg = eng.allocate_qureg(3)
    des_output = eng.allocate_qubit()
    ancilla_qubit = eng.allocate_qubit()
    ancilla2 = eng.allocate_qubit()
    phase_reg = eng.allocate_qureg(3)
    
    X | ancilla_qubit
    H | ancilla_qubit

    All(H) | layer1_weight_reg
    All(H) | layer2_weight_reg

    with Loop(eng, 2):
        run_qbnn(eng)
    #add_minus_sign(eng)
    
    #run_qbnn(eng)
    
    H | ancilla_qubit
    X | ancilla_qubit

    All(Measure) | layer1_weight_reg
    All(Measure) | layer2_weight_reg


    
    eng.flush()
    print("===========================================================================")
    print("This is the QBNN demo")
    print("The optimal weight string is:")
    print(int(layer1_weight_reg[0]),int(layer1_weight_reg[1]),int(layer1_weight_reg[2]),int(layer1_weight_reg[3]),int(layer2_weight_reg[0]),int(layer2_weight_reg[1]))












