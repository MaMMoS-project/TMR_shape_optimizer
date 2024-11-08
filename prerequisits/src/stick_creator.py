#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.11.0 with dump python functionality
###

import sys
import salome
import numpy as np
salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, r'/ceph/home/fillies/tmr_sensors/automatization')

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS


geompy = geomBuilder.New()

#-------------------Modify--------------------------

#target box size
xlen = 1
ylen = 0.1
zlen = 0.01

#air box scaliing factors
smallBox_factor = 3 #>0
bigBox_factor = 11   #>smallBox_factor


#mesh param

main_Meash_min = 0.00001
main_mesh_max = 1
object_Mesh_max = 0.005


#----------------------------------------------------

arrow_len = np.sqrt(2* ylen**2)/2


O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
Box_1 = geompy.MakeBoxDXDYDZ(xlen, ylen, zlen)
Box_2 = geompy.MakeBoxDXDYDZ(arrow_len, arrow_len, zlen)
Box_3 = geompy.MakeBoxDXDYDZ(arrow_len, arrow_len, zlen)
geompy.Rotate(Box_2, OZ, 45*math.pi/180.0)
geompy.Rotate(Box_3, OZ, 45*math.pi/180.0)
geompy.TranslateDXDYDZ(Box_3, xlen, 0, 0)
Fuse_1 = geompy.MakeFuseList([Box_1, Box_2, Box_3], True, True)
geompy.TranslateDXDYDZ(Fuse_1, -xlen/2 , -ylen/2, -zlen/2)
smallBox = geompy.MakeBoxDXDYDZ(xlen * smallBox_factor, ylen * smallBox_factor, zlen * smallBox_factor)
bigBox = geompy.MakeBoxDXDYDZ(xlen * bigBox_factor, ylen * bigBox_factor, zlen * bigBox_factor)
geompy.TranslateDXDYDZ(smallBox, -xlen * smallBox_factor/2, -ylen * smallBox_factor/2, -zlen * smallBox_factor/2)
geompy.TranslateDXDYDZ(bigBox, -xlen * bigBox_factor/2, -ylen * bigBox_factor/2, -zlen * bigBox_factor/2)
[geomObj_1] = geompy.SubShapeAll(Fuse_1, geompy.ShapeType["SOLID"])
[geomObj_2] = geompy.SubShapeAll(Fuse_1, geompy.ShapeType["SOLID"])
Cut_1 = geompy.MakeCutList(bigBox, [smallBox], True)
[geomObj_3] = geompy.SubShapeAll(Cut_1, geompy.ShapeType["SOLID"])
[geomObj_4] = geompy.SubShapeAll(Cut_1, geompy.ShapeType["SOLID"])
Cut_2 = geompy.MakeCutList(smallBox, [Fuse_1], True)
[geomObj_1, geomObj_2, geomObj_3, geomObj_4, geomObj_5, geomObj_6, geomObj_7, geomObj_8, geomObj_9, geomObj_10, geomObj_11, geomObj_12, geomObj_13, geomObj_14] = geompy.GetGlueFaces( [Fuse_1, Cut_1, Cut_2], 1e-07)
[geomObj_21] = geompy.SubShapeAll(Cut_2, geompy.ShapeType["SOLID"])
[geomObj_22] = geompy.SubShapeAll(Cut_2, geompy.ShapeType["SOLID"])
Glue_1 = geompy.MakeGlueFacesByList([Fuse_1, Cut_1, Cut_2], 1e-07, [], True, False)
a1 = geompy.CreateGroup(Glue_1, geompy.ShapeType["SOLID"])
geompy.UnionIDs(a1, [2])
a2 = geompy.CreateGroup(Glue_1, geompy.ShapeType["SOLID"])
geompy.UnionIDs(a2, [64])
a3 = geompy.CreateGroup(Glue_1, geompy.ShapeType["SOLID"])
geompy.UnionIDs(a3, [131])
[a1, a2, a3] = geompy.GetExistingSubObjects(Glue_1, False)


geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( Box_1, 'Box_1' )
geompy.addToStudy( Box_2, 'Box_2' )
geompy.addToStudy( Box_3, 'Box_3' )

geompy.addToStudy( Fuse_1, 'Fuse_1' )
geompy.addToStudy( smallBox, 'smallBox' )
geompy.addToStudy( bigBox, 'bigBox' )

geompy.addToStudy( Cut_1, 'Cut_1' )
geompy.addToStudy( Cut_2, 'Cut_2' )

geompy.addToStudy( Glue_1, 'Glue_1' )
geompy.addToStudyInFather( Glue_1, a1, '1' )
geompy.addToStudyInFather( Glue_1, a2, '2' )
geompy.addToStudyInFather( Glue_1, a3, '3' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)

Mesh_1 = smesh.Mesh(Glue_1,'Mesh_1')
NETGEN_1D_2D_3D = Mesh_1.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)
NETGEN_3D_Parameters_1 = NETGEN_1D_2D_3D.Parameters()
NETGEN_3D_Parameters_1.SetMaxSize( main_mesh_max )
NETGEN_3D_Parameters_1.SetMinSize( main_Meash_min )
NETGEN_3D_Parameters_1.SetSecondOrder( 0 )
NETGEN_3D_Parameters_1.SetOptimize( 1 )
NETGEN_3D_Parameters_1.SetFineness( 2 )
NETGEN_3D_Parameters_1.SetChordalError( -1 )
NETGEN_3D_Parameters_1.SetChordalErrorEnabled( 0 )
NETGEN_3D_Parameters_1.SetUseSurfaceCurvature( 1 )
NETGEN_3D_Parameters_1.SetFuseEdges( 1 )
NETGEN_3D_Parameters_1.SetQuadAllowed( 0 )
a1_1 = Mesh_1.GroupOnGeom(a1,'1',SMESH.VOLUME)
a2_1 = Mesh_1.GroupOnGeom(a2,'2',SMESH.VOLUME)
a3_1 = Mesh_1.GroupOnGeom(a3,'3',SMESH.VOLUME)
a1_2 = Mesh_1.GroupOnGeom(a1,'1',SMESH.VOLUME)
a2_2 = Mesh_1.GroupOnGeom(a2,'2',SMESH.VOLUME)
a3_2 = Mesh_1.GroupOnGeom(a3,'3',SMESH.VOLUME)
NETGEN_3D_Parameters_1.SetLocalSizeOnShape(Fuse_1,object_Mesh_max)
NETGEN_3D_Parameters_1.SetCheckChartBoundary( 48 )
isDone = Mesh_1.Compute()
[ a1_1, a2_1, a3_1, a1_2, a2_2, a3_2 ] = Mesh_1.GetGroups()
tets = a1_1.Size()  #Finde tets
try:
  # Specify the file path and name
  output_file_path = "tets_output.txt"

  # Open the file in write mode and save the tets value
  with open(output_file_path, "w") as file:
    file.write(f"Tets Size: {tets}\n")
except:
  print('ExportUNV() failed. Invalid file name?')
try:

  
  Mesh_1.ExportUNV( r'/ceph/home/fillies/tmr_sensor_sensors/automatization/operations_Files/mesh.unv', 0 )
  pass
except:
  print('ExportUNV() failed. Invalid file name?')



## Set names of Mesh objects
smesh.SetName(NETGEN_1D_2D_3D.GetAlgorithm(), 'NETGEN 1D-2D-3D')
smesh.SetName(NETGEN_3D_Parameters_1, 'NETGEN 3D Parameters_1')
smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')
smesh.SetName(a3_2, '3')
smesh.SetName(a2_2, '2')
smesh.SetName(a1_2, '1')
smesh.SetName(a3_1, '3')
smesh.SetName(a2_1, '2')
smesh.SetName(a1_1, '1')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
