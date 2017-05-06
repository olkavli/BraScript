# ---------------------------------------------------------------------------
# Create AOCA Hinderflate oppdelt for seleksjon av Hinder
# Input : Utflygingslinje + båndbredde
# April 2015
#  Olav Kavli
# ---------------------------------------------------------------------------

    # Import system modules
import sys, string, os, arcpy,traceback,math
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

import math

def circle_poly(x,y,r): 
    for i in range(100):
        ang = i/100 * math.pi * 2
        yield (x + r * math.cos(ang), y + r * math.sin(ang) )
    
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
        
        stpFC=r'D:\prosjekt\Avinor\Testdata\ENZV.gdb\RunwayEnd'
        startPointLayer = arcpy.MakeFeatureLayer_management(stpFC)
        tOSF=r'D:\prosjekt\Avinor\Testdata\ENZV.gdb\BraShape'
        testPkt=r'D:\prosjekt\Avinor\Testdata\ENZV.gdb\startpunkt'
        alfa = 5
        radalfa = math.radians(alfa)
        Zmin = 0
        Zmax = 0
        r = 200
        R=1000
        
        
        

        arcpy.env.overwriteOutput=1
        
        # finne høyde og retning
        
        
          
                
        with arcpy.da.SearchCursor(startPointLayer,['BRNGTRUE','SHAPE@']) as rows:
            row =  rows.next()
            retning=row[0] 
            toPathGeom=row[1]
        pnt = toPathGeom.firstPoint
        z0=pnt.Z
        
        Zmin = r*math.tan(radalfa) + z0
        Zmax = R*math.tan(radalfa) + z0
        
        

        arcpy.AddMessage("Retning for {0}. XYZ = {1},{2},{3}".format(retning,pnt.X,pnt.Y,pnt.Z))
            
        spRef = toPathGeom.spatialReference
            
        arcpy.DeleteFeatures_management(tOSF)
        arcpy.DeleteFeatures_management(testPkt)
            
        insCur = arcpy.InsertCursor(tOSF,spRef)
        insCurP= arcpy.InsertCursor(testPkt,spRef)
            
           
        # get start and end coordinates
        
        retnStart = retning - 180
        retnSlutt = retning + 180
        
        retn =retnStart
        deltaRetn=1
        
        # Nytt deltapolygon
        polyarr = arcpy.Array()
    
        while retn < retnSlutt:
            # Nytt deltapolygon
            polyarr = arcpy.Array()
    
            p0 = toPathGeom.pointFromAngleAndDistance (retn, r, 'PLANAR')
            pG0 = p2Dto3D(p0,Zmin)                
            polyarr.add(pG0.firstPoint)
            
            p = toPathGeom.pointFromAngleAndDistance (retn+deltaRetn, r, 'PLANAR')
            pG = p2Dto3D(p,Zmin)                
            polyarr.add(pG.firstPoint)
            
            p = toPathGeom.pointFromAngleAndDistance (retn+deltaRetn, R, 'PLANAR')
            pG = p2Dto3D(p,Zmax)                
            polyarr.add(pG.firstPoint)
            
            p = toPathGeom.pointFromAngleAndDistance (retn, R, 'PLANAR')
            pG = p2Dto3D(p,Zmax)                
            polyarr.add(pG.firstPoint)
            
            polyarr.add(pG0.firstPoint)
            
            polySurf=arcpy.Polygon(polyarr,spRef,True,False)
        
            inRow=insCur.newRow()
            inRow.setValue('SHAPE',polySurf)
            inRow.setValue('Id',str(int(retn)))
            insCur.insertRow(inRow)  
            
            
            # cylinder
            
            polyarr = arcpy.Array()
        
            p0 = toPathGeom.pointFromAngleAndDistance (retn, r, 'PLANAR')
            pG0 = p2Dto3D(p0,Zmin)                
            polyarr.add(pG0.firstPoint)
        
            p = toPathGeom.pointFromAngleAndDistance (retn+deltaRetn, r, 'PLANAR')
            pG = p2Dto3D(p,Zmin)                
            polyarr.add(pG.firstPoint)
        
            p = toPathGeom.pointFromAngleAndDistance (retn+deltaRetn, r-0.01, 'PLANAR')
            pG = p2Dto3D(p,z0)                
            polyarr.add(pG.firstPoint)
        
            p = toPathGeom.pointFromAngleAndDistance (retn, r-0.01, 'PLANAR')
            pG = p2Dto3D(p,z0)                
            polyarr.add(pG.firstPoint)
        
            polyarr.add(pG0.firstPoint)
        
            polySurf=arcpy.Polygon(polyarr,spRef,True,False)
        
            inRow=insCur.newRow()
            inRow.setValue('SHAPE',polySurf)
            inRow.setValue('Id',str(int(retn))+'c')
            insCur.insertRow(inRow)                        
            
            
            retn=retn+deltaRetn
    

        del inRow
       # del inRowP
                
        del insCur
      #  del insCurP
            
        
            
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
        
        
        
    
    
    #Ends the script        
    
    print "Ferdig!"

if __name__ == '__main__':
    main()











    