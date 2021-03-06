from abapy import materials
from abapy.misc import load
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import pickle, copy, platform, compmod


# GENERAL SETTINGS
settings = {}
settings['export_fields'] = True
settings['compart'] = True
settings['is_3D']   = False
settings['lx']      = 10.
settings['ly']      = 10. # test direction 
settings['lz']      = 10.
settings['Nx']      = 40
settings['Ny']      = 20
settings['Nz']      = 2
settings['disp']    = 1.2
settings['nFrames'] = 50
settings['workdir'] = "workdir/"
settings['label']   = "cuboidTest"
settings['elType']  = "CPS4"
settings['cpus']    = 1

run_simulation = False # True to run it, False to just use existing results

E           = 1.
sy_mean     = .001
nu          = 0.3
sigma_sat   = .005
n           = 0.05


# ABAQUS PATH SETTINGS
node = platform.node()
if node ==  'lcharleux':      
  settings['abqlauncher']   = "/opt/Abaqus/6.9/Commands/abaqus" 
if node ==  'serv2-ms-symme': 
  settings['abqlauncher']   = "/opt/abaqus/Commands/abaqus"
if node ==  'epua-pd47': 
  settings['abqlauncher']   = "C:/SIMULIA/Abaqus/6.11-2/exec/abq6112.exe" 
if node ==  'epua-pd45': 
  settings['abqlauncher']   = "C:\SIMULIA/Abaqus/Commands/abaqus"
if node ==  'SERV3-MS-SYMME': 
  settings['abqlauncher']   = "C:/Program Files (x86)/SIMULIA/Abaqus/6.11-2/exec/abq6112.exe"


# MATERIALS CREATION
Ne = settings['Nx'] * settings['Ny'] 
if settings['is_3D']: Ne *= settings['Nz']
if settings['compart']:
  E         = E         * np.ones(Ne) # Young's modulus
  nu        = nu        * np.ones(Ne) # Poisson's ratio
  sy_mean   = sy_mean   * np.ones(Ne)
  sigma_sat = sigma_sat * np.ones(Ne)
  n         = n         * np.ones(Ne)
  sy = compmod.distributions.Rayleigh(sy_mean).rvs(Ne)
  labels = ['mat_{0}'.format(i+1) for i in xrange(len(sy_mean))]
  settings['material'] = [materials.Bilinear(labels = labels[i], 
                                 E = E[i], nu = nu[i], Ssat = sigma_sat[i], 
                                 n=n[i], sy = sy[i]) for i in xrange(Ne)]
else:
  labels = 'SAMPLE_MAT'
  settings['material'] = materials.Bilinear(labels = labels, 
                                E = E, nu = nu, sy = sy_mean, Ssat = sigma_sat,
                                n = n)

       
m = compmod.models.CuboidTest(**settings)
if run_simulation:
  m.MakeInp()
  m.Run()
  m.MakePostProc()
  m.RunPostProc()
m.LoadResults()
# Plotting results
if m.outputs['completed']:
  

  # History Outputs
  disp =  np.array(m.outputs['history']['disp'].values()[0].data[0])
  force =  np.array(np.array(m.outputs['history']['force'].values()).sum().data[0])
  volume = np.array(np.array(m.outputs['history']['volume'].values()).sum().data[0])
  length = settings['ly'] + disp
  surface = volume / length
  logstrain = np.log10(1. + disp / settings['ly'])
  linstrain = disp/ settings['ly']
  strain = linstrain
  stress = force / surface 
   
  fig = plt.figure(0)
  plt.clf()
  sp1 = fig.add_subplot(2, 1, 1)
  plt.plot(disp, force, 'ro-')
  plt.xlabel('Displacement, $U$')
  plt.ylabel('Force, $F$')
  plt.grid()
  sp1 = fig.add_subplot(2, 1, 2)
  plt.plot(strain, stress, 'ro-', label = 'simulation curve', linewidth = 2.)
  plt.xlabel('Tensile Strain, $\epsilon$')
  plt.ylabel(' Tensile Stress $\sigma$')
  plt.grid()
  plt.savefig(settings['workdir'] + settings['label'] + 'history.pdf')
  
  
  # Field Outputs
  if settings["export_fields"]:
    m.mesh.dump2vtk(settings['workdir'] + settings['label'] + '.vtk')
  
