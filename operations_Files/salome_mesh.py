#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.11.0 with dump python functionality
###

import sys
import salome

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
import os
import killSalome


geompy = geomBuilder.New()


#-------------------Modify--------------------------

#target box size
xlen = 1.9090909090909092
ylen = 0.1090909090909091
zlen = 0.01909090909090909

#air box scaliing factors
smallBox_factor = 3 #>0
bigBox_factor = 11   #>smallBox_factor


#mesh param

main_Meash_min = 0.0001
main_mesh_max = 1.0
object_Mesh_max = 0.005


#----------------------------------------------------

# rotate ellipse if needed
if ylen > xlen:
    xlen, ylen = ylen, xlen
    rotate = True
else:
    rotate = False


O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
Ellipse_1 = geompy.MakeEllipse(None, None, xlen/2, ylen/2)  #radius x, radius y
Face_1 = geompy.MakeFaceWires([Ellipse_1], 1)
Extrusion_1 = geompy.MakePrismVecH(Face_1, OZ, zlen)
smallBox = geompy.MakeBoxDXDYDZ(xlen * smallBox_factor, ylen * smallBox_factor, zlen * smallBox_factor)
bigBox = geompy.MakeBoxDXDYDZ(xlen * bigBox_factor, ylen * bigBox_factor, zlen * bigBox_factor)
geompy.TranslateDXDYDZ(Extrusion_1, 0, 0, -zlen/2)    
geompy.TranslateDXDYDZ(smallBox, -xlen * smallBox_factor/2, -ylen * smallBox_factor/2, -zlen * smallBox_factor/2)
geompy.TranslateDXDYDZ(bigBox, -xlen * bigBox_factor/2, -ylen * bigBox_factor/2, -zlen * bigBox_factor/2)
if rotate:
    geompy.Rotate(Extrusion_1, OZ, math.pi/2)
    geompy.Rotate(smallBox, OZ, math.pi/2)
    geompy.Rotate(bigBox, OZ, math.pi/2)
Cut_1 = geompy.MakeCutList(bigBox, [smallBox], True)
Cut_2 = geompy.MakeCutList(smallBox, [Extrusion_1], True)
[geomObj_1, geomObj_2, geomObj_3, geomObj_4, geomObj_5, geomObj_6, geomObj_7, geomObj_8, geomObj_9] = geompy.GetGlueFaces( [Extrusion_1, Cut_1, Cut_2], 1e-07)
Glue_1 = geompy.MakeGlueFacesByList([Extrusion_1, Cut_1, Cut_2], 1e-07, [], True, False)
geomObj_10 = geompy.GetInPlace(Glue_1, Extrusion_1, True)
[geomObj_11] = geompy.SubShapeAll(geomObj_10, geompy.ShapeType["SOLID"])
[geomObj_12] = geompy.SubShapeAll(geomObj_10, geompy.ShapeType["SOLID"])
a1 = geompy.CreateGroup(Glue_1, geompy.ShapeType["SOLID"])
geompy.UnionIDs(a1, [2])
geomObj_13 = geompy.GetInPlace(Glue_1, Cut_1, True)
[geomObj_14] = geompy.SubShapeAll(geomObj_13, geompy.ShapeType["SOLID"])
[geomObj_15] = geompy.SubShapeAll(geomObj_13, geompy.ShapeType["SOLID"])
a2 = geompy.CreateGroup(Glue_1, geompy.ShapeType["SOLID"])
geompy.UnionIDs(a2, [15])
geomObj_16 = geompy.GetInPlace(Glue_1, Cut_1, True)
[geomObj_17] = geompy.SubShapeAll(geomObj_16, geompy.ShapeType["SOLID"])
geomObj_18 = geompy.GetInPlace(Glue_1, Cut_2, True)
[geomObj_19] = geompy.SubShapeAll(geomObj_18, geompy.ShapeType["SOLID"])
[geomObj_20] = geompy.SubShapeAll(geomObj_18, geompy.ShapeType["SOLID"])
a3 = geompy.CreateGroup(Glue_1, geompy.ShapeType["SOLID"])
geompy.UnionIDs(a3, [82])
[geomObj_10, a1, geomObj_13, a2, geomObj_16, geomObj_18, a3] = geompy.GetExistingSubObjects(Glue_1, False)


geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( Ellipse_1, 'Ellipse_1' )
geompy.addToStudy( Face_1, 'Face_1' )
geompy.addToStudy( Extrusion_1, 'Extrusion_1' )
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
NETGEN_3D_Parameters_1.SetMaxSize( 1 )
NETGEN_3D_Parameters_1.SetMinSize( 1e-05 )
NETGEN_3D_Parameters_1.SetSecondOrder( 0 )
NETGEN_3D_Parameters_1.SetOptimize( 1 )
NETGEN_3D_Parameters_1.SetFineness( 2 )
NETGEN_3D_Parameters_1.SetChordalError( -1 )
NETGEN_3D_Parameters_1.SetChordalErrorEnabled( 0 )
NETGEN_3D_Parameters_1.SetUseSurfaceCurvature( 1 )
NETGEN_3D_Parameters_1.SetFuseEdges( 1 )
NETGEN_3D_Parameters_1.SetQuadAllowed( 0 )
NETGEN_3D_Parameters_1.UnsetLocalSizeOnEntry("Glue_1")
NETGEN_3D_Parameters_1.SetLocalSizeOnShape(Extrusion_1, 0.005)
NETGEN_3D_Parameters_1.SetCheckChartBoundary( 48 )
NETGEN_3D_Parameters_1.UnsetLocalSizeOnEntry("Glue_1")
a1_1 = Mesh_1.GroupOnGeom(a1,'1',SMESH.VOLUME)
a2_1 = Mesh_1.GroupOnGeom(a2,'2',SMESH.VOLUME)
a3_1 = Mesh_1.GroupOnGeom(a3,'3',SMESH.VOLUME)
isDone = Mesh_1.Compute()
[ a1_1, a2_1, a3_1 ] = Mesh_1.GetGroups()
try:
  Mesh_1.ExportUNV( r'/home/fillies/Documents/UWK_Projects/TMR_shape_optimizer/operations_Files/mesh.unv', 0 )
  pass
except:
  print('ExportUNV() failed. Invalid file name?')

## Set names of Mesh objects
smesh.SetName(NETGEN_1D_2D_3D.GetAlgorithm(), 'NETGEN 1D-2D-3D')
smesh.SetName(NETGEN_3D_Parameters_1, 'NETGEN 3D Parameters_1')
smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')
smesh.SetName(a3_1, '3')
smesh.SetName(a2_1, '2')
smesh.SetName(a1_1, '1')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()



