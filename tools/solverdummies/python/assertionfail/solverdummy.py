from __future__ import division

import os
import sys
import argparse
import numpy as np
 
from mpi4py import MPI
import PySolverInterface
from PySolverInterface import *

parser = argparse.ArgumentParser()
parser.add_argument("configurationFileName", help="Name of the xml config file.", type=str)
parser.add_argument("participantName", help="Name of the solver.", type=str)
parser.add_argument("meshName", help="Name of the mesh.", type=str)

try:
    args = parser.parse_args()
except SystemExit:
    print("")
    print("Usage: python ./solverdummy precice-config participant-name mesh-name")    
    quit()

configFileName = args.configurationFileName
participantName = args.participantName
meshName = args.meshName

N = 1

solverProcessIndex = 0
solverProcessSize = 1

interface = PySolverInterface(participantName, solverProcessIndex, solverProcessSize)
interface.configure(configFileName)
    
meshID = interface.getMeshID(meshName)

dimensions = interface.getDimensions()
vertex = np.zeros(dimensions)
dataIndices = np.zeros(N)

interface.setMeshVertices(meshID, N, vertex, dataIndices)

data_id_one = interface.getDataID("Forces", meshID)
data_id_two = interface.getDataID("Velocities", meshID)

print("IDS: " + str(data_id_one) + "," + str(data_id_two))

t = 0

print("%s: init preCICE..." % participantName)

dt = interface.initialize()

N_val = 5

if participantName == "SolverOne":
    print("initializing %s" % participantName)
    data_one = np.array([-0.1]) * np.ones(N_val)
    data_two = np.array([0.1]) * np.ones(N_val)
    print("pre write")
    print(data_one)
    if interface.isActionRequired(PyActionWriteInitialData()):
        interface.writeBlockVectorData(data_id_two, N, dataIndices, data_one)
        interface.fulfilledAction(PyActionWriteInitialData())
    print("post write")
    interface.initializeData()

    if interface.isReadDataAvailable():
        interface.readBlockVectorData(data_id_one, N, dataIndices, data_two)

elif participantName == "SolverTwo":
    print("initializing %s" % participantName)
    data_one = np.array([-0.1]) * np.ones(N_val)
    data_two = np.array([0.1]) * np.ones(N_val)
    print("pre write")
    print(data_two)
    if interface.isActionRequired(PyActionWriteInitialData()):
        interface.writeBlockVectorData(data_id_two, N, dataIndices, data_two)
        interface.fulfilledAction(PyActionWriteInitialData())
    print("post write")
    interface.initializeData()

    if interface.isReadDataAvailable():
        interface.readBlockVectorData(data_id_one, N, dataIndices, data_one)
else:
    raise Exception("unknown solver %s" % participantName)


print("%s: init preCICE done..." % participantName)

while interface.isCouplingOngoing():

    print("### pre compute:")
    print(data_one)
    print(data_two)
    print("###")
   
    if interface.isActionRequired(PyActionWriteIterationCheckpoint()):
        print("DUMMY: Writing iteration checkpoint")
        interface.fulfilledAction(PyActionWriteIterationCheckpoint())

    if participantName == "SolverOne":
        data_one = np.copy(data_two)

        print("### pre communicate:")
        print(data_one)
        print(data_two)
        print("###")

        interface.writeBlockVectorData(data_id_one, N, dataIndices, data_one)
        dt = interface.advance(dt)
        interface.readBlockVectorData(data_id_two, N, dataIndices, data_two)

    elif participantName == "SolverTwo":
        data_two = np.copy(data_one**2)

        print("### pre communicate:")
        print(data_one)
        print(data_two)
        print("###")

        interface.writeBlockVectorData(data_id_two, N, dataIndices, data_two)
        dt = interface.advance(dt)
        interface.readBlockVectorData(data_id_one, N, dataIndices, data_one)
    else:
        raise Exception("unknown solver %s" % participantName)

    print("### post communicate:")
    print(data_one)
    print(data_two)
    print("###")
    
    if interface.isActionRequired(PyActionReadIterationCheckpoint()):
        print("DUMMY: Reading iteration checkpoint")
        interface.fulfilledAction(PyActionReadIterationCheckpoint())
    else:
        print("DUMMY: Advancing in time")

print("###")
print(data_one)
print(data_two)
print("###")

interface.finalize()
print("DUMMY: Closing python solver dummy...")

