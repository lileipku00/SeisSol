#!/usr/bin/env python
##
# @file
# This file is part of SeisSol.
#
# @author Carsten Uphoff (c.uphoff AT tum.de, http://www5.in.tum.de/wiki/index.php/Carsten_Uphoff,_M.Sc.)
#
# @section LICENSE
# Copyright (c) 2017, SeisSol Group
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# @section DESCRIPTION
#

from gemmgen import DB, Tools, Arch, Kernel
import numpy as np

def addMatrices(db, matricesDir, PlasticityMethod, order):
  numberOfBasisFunctions = Tools.numberOfBasisFunctions(order)
  clones = dict()

  # Load matrices
  db.update(Tools.parseMatrixFile('{}/plasticity_{}_matrices_{}.xml'.format(matricesDir, PlasticityMethod, order), clones))

  # force Aligned in order to be compatible with regular DOFs.
  db.insert(DB.MatrixInfo('stressDOFS', numberOfBasisFunctions, 6, forceAligned=True))

  matrixOrder = { 'v': 0, 'vInv': 1 }
  globalMatrixIdRules = [
    (r'^(v|vInv)$', lambda x: matrixOrder[x[0]])
  ]
  DB.determineGlobalMatrixIds(globalMatrixIdRules, db, 'plasticity')

def addKernels(db, kernels):
  evaluateAtNodes = db['v'] * db['stressDOFS']
  db.insert(evaluateAtNodes.flat('interpolationDOFS'))
  kernels.append(Kernel.Prototype('evaluateAtNodes', evaluateAtNodes, beta=0))

  convertToModal = db['vInv'] * db['interpolationDOFS']
  kernels.append(Kernel.Prototype('convertToModal', convertToModal, beta=0))
