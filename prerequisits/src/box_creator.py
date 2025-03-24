#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.11.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
import killSalome
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

O_1 = geompy.MakeVertex(0, 0, 0)
OX_1 = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY_1 = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ_1 = geompy.MakeVectorDXDYDZ(0, 0, 1)


targetBox = geompy.MakeBoxDXDYDZ(xlen, ylen, zlen)
Box_1 = geompy.MakeBoxDXDYDZ(xlen * smallBox_factor, ylen * smallBox_factor, zlen * smallBox_factor)
Box_2 = geompy.MakeBoxDXDYDZ(xlen * bigBox_factor, ylen * bigBox_factor, zlen * bigBox_factor)
geompy.TranslateDXDYDZ(targetBox, -xlen/2, -ylen/2, -zlen/2)
geompy.TranslateDXDYDZ(Box_1, -xlen * smallBox_factor/2, -ylen * smallBox_factor/2, -zlen * smallBox_factor/2)
geompy.TranslateDXDYDZ(Box_2, -xlen * bigBox_factor/2, -ylen * bigBox_factor/2, -zlen * bigBox_factor/2)
box1Cut = geompy.MakeCutList(Box_1, [targetBox], True)
box2Cut = geompy.MakeCutList(Box_2, [Box_1], True)


[geomObj_31, geomObj_32, geomObj_33, geomObj_34, geomObj_35, geomObj_36, geomObj_37, geomObj_38, geomObj_39, geomObj_40, geomObj_41, geomObj_42] = geompy.GetGlueFaces( [targetBox, box1Cut, box2Cut], 1e-07)
Glue_1 = geompy.MakeGlueFacesByList([targetBox, box1Cut, box2Cut], 1e-07, [], True, False)
geomObj_43 = geompy.GetInPlace(Glue_1, targetBox, True)
[geomObj_44] = geompy.SubShapeAll(geomObj_43, geompy.ShapeType["SOLID"])
[geomObj_45] = geompy.SubShapeAll(geomObj_43, geompy.ShapeType["SOLID"])
a1 = geompy.CreateGroup(Glue_1, geompy.ShapeType["SOLID"])
geompy.UnionIDs(a1, [2])
geomObj_46 = geompy.GetInPlace(Glue_1, box1Cut, True)
[geomObj_47] = geompy.SubShapeAll(geomObj_46, geompy.ShapeType["SOLID"])
[geomObj_48] = geompy.SubShapeAll(geomObj_46, geompy.ShapeType["SOLID"])
a2 = geompy.CreateGroup(Glue_1, geompy.ShapeType["SOLID"])
geompy.UnionIDs(a2, [36])
geomObj_49 = geompy.GetInPlace(Glue_1, box2Cut, True)
[geomObj_50] = geompy.SubShapeAll(geomObj_49, geompy.ShapeType["SOLID"])
[geomObj_51] = geompy.SubShapeAll(geomObj_49, geompy.ShapeType["SOLID"])
a3 = geompy.CreateGroup(Glue_1, geompy.ShapeType["SOLID"])
geompy.UnionIDs(a3, [71])
[geomObj_43, a1, geomObj_46, a2, geomObj_49, a3] = geompy.GetExistingSubObjects(Glue_1, False)
[geomObj_43, a1, geomObj_46, a2, geomObj_49, a3] = geompy.GetExistingSubObjects(Glue_1, False)

geompy.addToStudy( O_1, 'O' )
geompy.addToStudy( OX_1, 'OX' )
geompy.addToStudy( OY_1, 'OY' )
geompy.addToStudy( OZ_1, 'OZ' )
geompy.addToStudy( targetBox, 'targetBox' )
geompy.addToStudy( Box_1, 'Box_1' )
geompy.addToStudy( Box_2, 'Box_2' )
geompy.addToStudy( box1Cut, 'box1Cut' )
geompy.addToStudy( box2Cut, 'box2Cut' )

geompy.addToStudy( Glue_1, 'Glue_1' )
geompy.addToStudyInFather( Glue_1, a1, '1' )
geompy.addToStudyInFather( Glue_1, a2, '2' )
geompy.addToStudyInFather( Glue_1, a3, '3' )
"""
###
### SMESH component
###
"""
import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)

Mesh_2 = smesh.Mesh(Glue_1,'Mesh_2')
NETGEN_1D_2D_3D = Mesh_2.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)
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
a1_1 = Mesh_2.GroupOnGeom(a1,'1',SMESH.VOLUME)
a2_1 = Mesh_2.GroupOnGeom(a2,'2',SMESH.VOLUME)
a3_1 = Mesh_2.GroupOnGeom(a3,'3',SMESH.VOLUME)
a1_2 = Mesh_2.GroupOnGeom(a1,'1',SMESH.VOLUME)
a2_2 = Mesh_2.GroupOnGeom(a2,'2',SMESH.VOLUME)
a3_2 = Mesh_2.GroupOnGeom(a3,'3',SMESH.VOLUME)
isDone = Mesh_2.Compute()
[ a1_1, a2_1, a3_1, a1_2, a2_2, a3_2 ] = Mesh_2.GetGroups()
NETGEN_3D_Parameters_1.SetLocalSizeOnShape(targetBox, object_Mesh_max)
NETGEN_3D_Parameters_1.SetCheckChartBoundary( 48 )
isDone = Mesh_2.Compute()
[ a1_1, a2_1, a3_1, a1_2, a2_2, a3_2 ] = Mesh_2.GetGroups()
try:

  
  Mesh_2.ExportUNV( r'/ceph/home/fillies/tmr_sensor_sensors/automatization/operations_Files/mesh.unv', 0 )
  pass
except:
  print('ExportUNV() failed. Invalid file name?')


## Set names of Mesh objects
smesh.SetName(NETGEN_1D_2D_3D.GetAlgorithm(), 'NETGEN 1D-2D-3D')
smesh.SetName(NETGEN_3D_Parameters_1, 'NETGEN 3D Parameters_1')
smesh.SetName(Mesh_2.GetMesh(), 'Mesh_2')
smesh.SetName(a3_2, '3')
smesh.SetName(a2_2, '2')
smesh.SetName(a1_2, '1')
smesh.SetName(a3_1, '3')
smesh.SetName(a2_1, '2')
smesh.SetName(a1_1, '1')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()


killSalome.killAllPorts() 

  
 
