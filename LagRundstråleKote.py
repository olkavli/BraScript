# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create AOCA Hinderflate oppdelt for seleksjon av Hinder
# Input : Utflygingslinje + b�ndbredde
# April 2015
#  Olav Kavli
# ---------------------------------------------------------------------------

# Import system modules
import sys
import string
import os
import arcpy
import traceback
import math
import arcpy.da as da


# Global variables

spRef=None

punkt=[]

def p2Dto3D(p,z):
    pnt=p.firstPoint
    pnt.Z=z
    return(arcpy.PointGeometry(pnt,spRef,True,False))

def ppl(end,p1,p2,distance):
    res=p1.angleAndDistanceTo (p2)
    if end == 'END':
        p=p2.pointFromAngleAndDistance( res[0]-90.0, distance)
        pL=p2Dto3D(p, p2)
        p=p2.pointFromAngleAndDistance (res[0]+90.0, distance)
        pR=p2Dto3D(p, p2)

    else:
       
        p=p1.pointFromAngleAndDistance( res[0]-90.0, distance)
        pL=p2Dto3D(p, p1)
        p=p1.pointFromAngleAndDistance (res[0]+90.0, distance)
        pR=p2Dto3D(p, p1)       
    return (pL,pR)
    
    

def mellompunktG(geom,dL):
    
    pntGeom = geom.positionAlongLine(dL)
    #pkt=pntGeom.firstPoint
    
    
    width = width0 + extfactor*dL
    if width > widthm:
        width=widthm
            
    return(pntGeom,width)


def circle_poly(x,y,r): 
    for i in range(100):
        ang = i/100 * math.pi * 2
        yield (x + r * math.cos(ang), y + r * math.sin(ang) )

def circle_polyline(pntcenter,z,r):
    retning = 0
    retnStart = retning - 180
    retnSlutt = retning + 180
        
    retn =retnStart
    deltaRetn=1
    linearr = arcpy.Array()
    p0 = pntcenter.pointFromAngleAndDistance (retn, r, 'PLANAR')
    pG0 = p2Dto3D(p0,z)                
    linearr.add(pG0.firstPoint)
    
    while retn < retnSlutt:
        # Nytt linjearray
        retn=retn+deltaRetn

        
        
        p = pntcenter.pointFromAngleAndDistance (retn, r, 'PLANAR')
        pG = p2Dto3D(p,z)                
        linearr.add(pG.firstPoint)
        
        
        
    lineGeom=arcpy.Polyline(linearr,spRef,True,False)
    return lineGeom

def main():
    # Local variables...
    try:    
        
        maxbredde=False
        maxDist = 10000
        deltaDist=100 
             #startPointLayer = arcpy.GetParameter(0)
        #Zmin = arcpy.GetParameter(1)
        #Zmax = arcpy.GetParameter(2)
        #Rmin = arcpy.GetParameter(3)
        #Rmax = arcpy.GetParameter(4)
        
        stpFC=r'C:\prosjekt\Avinor\BRA\BRA_verktoy\BRA_data.gdb\Referansepkt_navigasjon'
        startPointLayer = arcpy.MakeFeatureLayer_management(stpFC)
        tOSF=r'C:\prosjekt\Avinor\BRA\Testdata\ENML.gdb\BraKoter'
        testPkt=r'C:\prosjekt\Avinor\BRA\Testdata\ENML.gdb\startpunkt'
        alfa = 5
        radalfa = math.radians(alfa)
        Zmin = 0
        Zmax = 0
        r = 200
        R=1000
        ekvidistanse = 10
        
        

        arcpy.env.overwriteOutput=1
        
        # finne høyde og retning
        
        whereClause = "LUFTHAVN_ID = {0} AND PUNKTNR = '{1}'".format(23,'NDB')
          
        retning = 0        
        with arcpy.da.SearchCursor(startPointLayer,['SHAPE@','HOYDE_HOVED'],whereClause) as rows:
            row =  rows.next()
             
            toPathGeom=row[0]
        pnt = toPathGeom.firstPoint
        z0=row[1]
        
        Zmin = r*math.tan(radalfa) + z0
        Zmax = R*math.tan(radalfa) + z0


        # Aktuelle koter
        lstKote = []
        forsteKote = long((Zmin+ekvidistanse)/ekvidistanse) * ekvidistanse
        
        kote = forsteKote
        while kote < Zmax:
            lstKote.append(kote)
            kote = kote + ekvidistanse

        arcpy.AddMessage("Retning for {0}. XYZ = {1},{2},{3}".format(retning,pnt.X,pnt.Y,pnt.Z))
            
        spRef = toPathGeom.spatialReference
            
        arcpy.DeleteFeatures_management(tOSF)
        arcpy.DeleteFeatures_management(testPkt)
            
        insCur = arcpy.InsertCursor(tOSF,spRef)
        insCurP= arcpy.InsertCursor(testPkt,spRef)
            
        # Lag første kote   Zmin

        pLine = circle_polyline(toPathGeom,Zmin,r)

        inRow=insCur.newRow()
        inRow.setValue('SHAPE',pLine)
        inRow.setValue('HOH',str(round(Zmin, 2)))
        inRow.setValue('Type','Grense')
        insCur.insertRow(inRow)  
        for z in lstKote:
            rk = (z-z0)/math.tan(radalfa)
            pLine = circle_polyline(toPathGeom,z,rk)

            inRow=insCur.newRow()
            inRow.setValue('SHAPE',pLine)
            inRow.setValue('HOH',str(round(z, 2)))
            inRow.setValue('Type','Kote')
            insCur.insertRow(inRow)  


        pLine = circle_polyline(toPathGeom,Zmax,R)

        inRow=insCur.newRow()
        inRow.setValue('SHAPE',pLine)
        inRow.setValue('HOH',str(round(Zmax, 2)))
        inRow.setValue('Type','Grense')
        insCur.insertRow(inRow)  

        br = 0
        del insCur
        del insCurP

    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
    
        # Concatenate information together concerning the error into a message string
        #
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
    
        # Return python error messages for use in script tool or Python Window
        #
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)
    
        # Print Python error messages for use in Python / Python Window
        #
        print pymsg + "\n"
        print msgs
        
        

    print 'Ferdig!'


if __name__ == '__main__':
    main()
