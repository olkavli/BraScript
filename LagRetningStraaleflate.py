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


def addrec(cur,geom,name):
    inRow=cur.newRow()
    inRow.setValue('SHAPE',geom)
    inRow.setValue('Id',name)
    cur.insertRow(inRow) 
    return

def pRD(pGeo,retn,avst,z,spRef):
    p = pGeo.pointFromAngleAndDistance (retn, avst, 'PLANAR')
    return (p2Dto3D(p, z,spRef))
    
    

def p2Dto3D(p,z,spRef):
    pnt=p.firstPoint
    pnt.Z=z
    return(arcpy.PointGeometry(pnt,spRef,True,False))


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
        
        stpFC=r'D:\prosjekt\Avinor\Testdata\ENZV.gdb\startpunkt'
        startPointLayer = arcpy.MakeFeatureLayer_management(stpFC)
        tOSF=r'D:\prosjekt\Avinor\Testdata\ENZV.gdb\BraShape2'
        #testPkt=r'D:\prosjekt\Avinor\Testdata\ENZV.gdb\startpunkt'
        testLine=r'D:\prosjekt\Avinor\Testdata\ENZV.gdb\BraLine'
        testPkt=r'D:\prosjekt\Avinor\Testdata\ENZV.gdb\BraPoint'
        
        theta = 20
        a = 300
        b=500
        h=70
        r=a+6000
        D=500
        H=20
        L=1500
      
        
        
        arcpy.env.overwriteOutput=1
        
        # finne høyde og retning
        
              
        with arcpy.da.SearchCursor(startPointLayer,['BRNGTRUE','SHAPE@']) as rows:
            row =  rows.next()
            retn=row[0] 
            pA=row[1]
        pntA = pA.firstPoint
        Z0=pntA.Z
        
        Zh=Z0+h
        ZH=Z0+H
        
        
        
        spRef = pA.spatialReference
    
        arcpy.DeleteFeatures_management(tOSF)
        arcpy.DeleteFeatures_management(testLine)
        arcpy.DeleteFeatures_management(testPkt)
    
    
        insCur = arcpy.InsertCursor(tOSF,spRef)
        insCurL = arcpy.InsertCursor(testLine,spRef)
        insCurP= arcpy.InsertCursor(testPkt,spRef)
        
        
        
        # Sidefelter
        
        # Først Punktene
        p0=pRD(pA, retn, -b , Z0,spRef)
        addrec(insCurP,pA,'pA')
        addrec(insCurP,p0,'p0')
        
        # venstre side
        pl1=pRD(p0, retn+90, D,Z0,spRef)
        addrec(insCurP,pl1,'pl1')
        pl2=pRD(p0,retn+90,L,ZH,spRef)
        addrec(insCurP,pl2,'pl2')
        pl4=pRD(pl1, retn, b+a, Z0,spRef)
        addrec(insCurP,pl4,'pl4')
        
        #Finne kryss mellom 2 linjer
        # Sektor venstre
        
        ps1= pRD(pl4, retn+theta, r, Zh,spRef)
        lineArr = arcpy.Array([pl4.firstPoint,ps1.firstPoint])       
        l1 = arcpy.Polyline(lineArr,spRef,True,False)
        addrec(insCurL,l1,'ll1')
        
        pl3x = pRD(pl2, retn, r, ZH,spRef)
        lineArr = arcpy.Array([pl2.firstPoint,pl3x.firstPoint]) 
        l2=arcpy.Polyline(lineArr,spRef,True,False)
        addrec(insCurL,l2,'ll2')
        
        pl3xx=l1.intersect(l2,1)
        
        pl3=p2Dto3D(pl3xx,ZH,spRef)
        
        # høyre side
        ph1=pRD(p0, retn-90, D,Z0,spRef)
        addrec(insCurP,ph1,'ph1')
        ph2=pRD(p0,retn-90,L,ZH,spRef)
        addrec(insCurP,ph2,'ph2')
        ph4=pRD(ph1, retn, b+a, Z0,spRef)
        addrec(insCurP,ph4,'ph4')
    
        #Finne kryss mellom 2 linjer
        # Sektor venstre
    
        ps1= pRD(ph4, retn-theta, r, Zh,spRef)
        lineArr = arcpy.Array([ph4.firstPoint,ps1.firstPoint])       
        l1 = arcpy.Polyline(lineArr,spRef,True,False)
        addrec(insCurL,l1,'lh1')
    
        ph3x = pRD(ph2, retn, r, ZH,spRef)
        lineArr = arcpy.Array([ph2.firstPoint,ph3x.firstPoint]) 
        l2=arcpy.Polyline(lineArr,spRef,True,False)
        addrec(insCurL,l2,'lh2')
    
        ph3xx=l1.intersect(l2,1)
        ph3=p2Dto3D(ph3xx,ZH,spRef)
        
        
        
            
      
        
        
        polyarr = arcpy.Array()
        polyarr.add(pl1.firstPoint)
        polyarr.add(pl2.firstPoint)
        polyarr.add(pl3.firstPoint)
        polyarr.add(pl4.firstPoint)
        polyarr.add(pl1.firstPoint)
    
        polySurf=arcpy.Polygon(polyarr,spRef,True,False)
    
        inRow=insCur.newRow()
        inRow.setValue('SHAPE',polySurf)
        inRow.setValue('Id',str(int(retn))+'l')
        insCur.insertRow(inRow)                             
            
        polyarr = arcpy.Array()
        polyarr.add(ph1.firstPoint)
        polyarr.add(ph2.firstPoint)
        polyarr.add(ph3.firstPoint)
        polyarr.add(ph4.firstPoint)
        polyarr.add(ph1.firstPoint)
        
        polySurf=arcpy.Polygon(polyarr,spRef,True,False)
    
        inRow=insCur.newRow()
        inRow.setValue('SHAPE',polySurf)
        inRow.setValue('Id',str(int(retn))+'h')
        insCur.insertRow(inRow)                                        
        ## get start and end coordinates
        
        retnStart = retn - theta
        retnSlutt = retn + theta
        
        ra =retnStart
        deltaRetn=1
        
        ## Nytt deltapolygon
        polyarr = arcpy.Array()
    
        while ra < retnSlutt:
            ## Nytt deltapolygon
           
    
            pa0 = pA.pointFromAngleAndDistance (ra, r, 'PLANAR')
            pa = p2Dto3D(pa0,h,spRef)                
            polyarr.add(pa.firstPoint)
            
            addrec(insCurP, pa, 'pa'+str(int(ra)))
            
            ra=ra+deltaRetn
        polyarr.add(pl3.firstPoint)
        polyarr.add(pl4.firstPoint)
        polyarr.add(ph4.firstPoint)
        polyarr.add(ph3.firstPoint)
        
        polySurf=arcpy.Polygon(polyarr,spRef,True,False)
        
        addrec(insCur, polySurf, "vifte")

        del inRow
       # del inRowP
                
        del insCur
        del insCurL
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
        
        
        
    
    
    #Ends the script        
    
    print "Ferdig!"

if __name__ == '__main__':
    main()











    