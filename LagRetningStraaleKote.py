# ---------------------------------------------------------------------------
# Create AOCA Hinderflate oppdelt for seleksjon av Hinder
# Input : Utflygingslinje + b�ndbredde
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

def addrecH(cur,geom,name,h):
    inRow=cur.newRow()
    inRow.setValue('SHAPE',geom)
    inRow.setValue('Id',name)
    inRow.setValue('HOH',h)
    cur.insertRow(inRow) 
    return    

def pRD(pGeo,retn,avst,z,spRef):
    p = pGeo.pointFromAngleAndDistance (retn, avst, 'PLANAR')
    return (p2Dto3D(p, z,spRef))
    
    

def p2Dto3D(p,z,spRef):
    pnt=p.firstPoint
    pnt.Z=z
    return(arcpy.PointGeometry(pnt,spRef,True,False))

def circle_polyline(pntcenter,z,r,retnStart,retnSlutt,spRef):
       
    retn =retnStart
    deltaRetn=1
    linearr = arcpy.Array()
    p0 = pntcenter.pointFromAngleAndDistance (retn, r, 'PLANAR')
    pG0 = p2Dto3D(p0,z,spRef)                
    linearr.add(pG0.firstPoint)
    
    while retn < retnSlutt:
        # Nytt linjearray
        retn=retn+deltaRetn

        
        
        p = pntcenter.pointFromAngleAndDistance (retn, r, 'PLANAR')
        pG = p2Dto3D(p,z,spRef)                
        linearr.add(pG.firstPoint)
        
        
        
    lineGeom=arcpy.Polyline(linearr,spRef,True,False)
    return lineGeom

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
        
        stpFC=r'C:\prosjekt\Avinor\BRA\BRA_verktoy\BRA_data.gdb\Referansepkt_navigasjon'
        stpTab=r'C:\prosjekt\Avinor\BRA\Testdata\ENML.gdb\RetnStrTab'
        tOSF=r'C:\prosjekt\Avinor\BRA\Testdata\ENML.gdb\BraKoter'
        
       
        testLine=r'C:\prosjekt\Avinor\BRA\Testdata\ENML.gdb\BraLine'
        testPkt=r'C:\prosjekt\Avinor\BRA\Testdata\ENML.gdb\BraPoint'
        
       
      
        # UTVALG
        ICAO = 'ENML'
        PUNKTNR ='LOC 07'
        
        arcpy.env.overwriteOutput=1
        
        # finne h�yde og retning
        whereCl = "LUFTHAVN Like '{0}%' AND PUNKTNR = '{1}'".format(ICAO,PUNKTNR)
        # Fra RPR      
        with arcpy.da.SearchCursor(stpFC,['PUNKTNR','HOYDE_HOVED','SHAPE@'],whereCl) as rows:
            row =  rows.next()
            RPR_PUNKTNR=row[0] 
            HOH=row[1]
            pA = row[2]
        # Fra RetnStrTab
        whereCl = "ICAO = '{0}' AND RPR_PUNKTNR = '{1}'".format(ICAO,RPR_PUNKTNR)
              
        with arcpy.da.SearchCursor(stpTab,['A','B','H0','R','D','H1','L','THETA','BEARING'],whereCl) as rows:
            row =  rows.next()
            a=row[0] 
            b=row[1]
            h = row[2]
            R = row[3]+a
            D=row[4]
            H=row[5]
            L=row[6]
            theta = row[7]
            retn = row[8]

        pntA = pA.firstPoint
        Z0=HOH
        
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
        
        # F�rst Punktene
        p0=pRD(pA, retn, -b , Z0,spRef)
        addrecH(insCurP,pA,'pA',Z0)
        addrecH(insCurP,p0,'p0',Z0)
        
        # venstre side
        pl1=pRD(p0, retn+90, D,Z0,spRef)
        addrecH(insCurP,pl1,'pl1',Z0)
        pl2=pRD(p0,retn+90,L,ZH,spRef)
        addrecH(insCurP,pl2,'pl2',ZH)
        pl4=pRD(pl1, retn, b+a, Z0,spRef)
        addrecH(insCurP,pl4,'pl4',Z0)
        
        #Finne kryss mellom 2 linjer

        # Lager linje paa maxradius
        linjeMax = circle_polyline(pA,Zh,R,retn-theta,retn+theta,spRef)
        addrec(insCurL,linjeMax,'maxL')

        # Sektor venstre
        
        ps1x= pRD(pl4, retn+theta, R, Zh,spRef)
        lineArr = arcpy.Array([pl4.firstPoint,ps1x.firstPoint])       
        ll1 = arcpy.Polyline(lineArr,spRef,True,False)
        addrec(insCurL,ll1,'ll1')

        #Xing Venstre maxR

        ps1xx = linjeMax.intersect(ll1,1)
        ps1 = p2Dto3D(ps1xx,Zh,spRef)
        addrecH(insCurP,ps1,'ps1',Zh)
        
        pl3x = pRD(pl2, retn, R, ZH,spRef)
        lineArr = arcpy.Array([pl2.firstPoint,pl3x.firstPoint]) 
        ll2=arcpy.Polyline(lineArr,spRef,True,False)
        addrec(insCurL,ll2,'ll2')
        
        pl3xx=ll1.intersect(ll2,1)
        
        pl3=p2Dto3D(pl3xx,ZH,spRef)
        addrecH(insCurP,pl3,'pl3',ZH)
        
        # høyre side
        ph1=pRD(p0, retn-90, D,Z0,spRef)
        addrecH(insCurP,ph1,'ph1',Z0)
        ph2=pRD(p0,retn-90,L,ZH,spRef)
        addrecH(insCurP,ph2,'ph2',ZH)
        ph4=pRD(ph1, retn, b+a, Z0,spRef)
        addrecH(insCurP,ph4,'ph4',Z0)
    
        #Finne kryss mellom 2 linjer
        # Sektor høyre
    
        ps1= pRD(ph4, retn-theta, R, Zh,spRef)
        lineArr = arcpy.Array([ph4.firstPoint,ps1.firstPoint])       
        lh1 = arcpy.Polyline(lineArr,spRef,True,False)
        addrec(insCurL,lh1,'lh1')
    
        ph3x = pRD(ph2, retn, R, ZH,spRef)
        lineArr = arcpy.Array([ph2.firstPoint,ph3x.firstPoint]) 
        lh2=arcpy.Polyline(lineArr,spRef,True,False)
        addrec(insCurL,lh2,'lh2')
    
        ph3xx=lh1.intersect(lh2,1)
        ph3=p2Dto3D(ph3xx,ZH,spRef)
        addrecH(insCurP,ph3,'ph3',ZH)
        
        # Sektor høyre
        
        ps1x= pRD(ph4, retn-theta, R, Zh,spRef)
        lineArr = arcpy.Array([ph4.firstPoint,ps1x.firstPoint])       
        lh1 = arcpy.Polyline(lineArr,spRef,True,False)
        addrec(insCurL,lh1,'lh1')

        #Xing Venstre maxR

        ps2xx = linjeMax.intersect(lh1,1)
        ps2 = p2Dto3D(ps2xx,Zh,spRef)
        addrecH(insCurP,ps2,'ps2',Zh)
            
      
        
        
        # polyarr = arcpy.Array()
        # polyarr.add(pl1.firstPoint)
        # polyarr.add(pl2.firstPoint)
        # polyarr.add(pl3.firstPoint)
        # polyarr.add(pl4.firstPoint)
        # polyarr.add(pl1.firstPoint)
    
        # polySurf=arcpy.Polygon(polyarr,spRef,True,False)
    
        # inRow=insCur.newRow()
        # inRow.setValue('SHAPE',polySurf)
        # inRow.setValue('Id',str(int(retn))+'l')
        # insCur.insertRow(inRow)                             
            
        # polyarr = arcpy.Array()
        # polyarr.add(ph1.firstPoint)
        # polyarr.add(ph2.firstPoint)
        # polyarr.add(ph3.firstPoint)
        # polyarr.add(ph4.firstPoint)
        # polyarr.add(ph1.firstPoint)
        
        # polySurf=arcpy.Polygon(polyarr,spRef,True,False)
    
        # inRow=insCur.newRow()
        # inRow.setValue('SHAPE',polySurf)
        # inRow.setValue('Id',str(int(retn))+'h')
        # insCur.insertRow(inRow)                                        
        # ## get start and end coordinates
        
        # retnStart = retn - theta
        # retnSlutt = retn + theta
        
        # ra =retnStart
        # deltaRetn=1
        
        # ## Nytt deltapolygon
        # polyarr = arcpy.Array()
    
        # while ra < retnSlutt:
        #     ## Nytt deltapolygon
           
    
        #     pa0 = pA.pointFromAngleAndDistance (ra, r, 'PLANAR')
        #     pa = p2Dto3D(pa0,h,spRef)                
        #     polyarr.add(pa.firstPoint)
            
        #     addrec(insCurP, pa, 'pa'+str(int(ra)))
            
        #     ra=ra+deltaRetn
        # polyarr.add(pl3.firstPoint)
        # polyarr.add(pl4.firstPoint)
        # polyarr.add(ph4.firstPoint)
        # polyarr.add(ph3.firstPoint)
        
        # polySurf=arcpy.Polygon(polyarr,spRef,True,False)
        
        # addrec(insCur, polySurf, "vifte")

        #del inRow
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











    