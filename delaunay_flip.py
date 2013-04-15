import convex_hull
import simpleTriangulation
import delaunay_check
from PIL import Image,ImageDraw
import random
import math
import time



class Delaunay(object):
    ''' finds non-delaunay triangles '''
    triangles = []
    
    def __init__(self, draw, st, cloud, conv_h, im):
        cir = delaunay_check.circleThroughThreePoints()
        bc = delaunay_check.BarycentricCoordinates()

        self.triangles = st.triangles

        self.searchForNonDelaunay(cloud, cir, draw, im)

        for i in range(len(self.triangles)):
            draw.polygon(self.triangles[i], fill=None, outline='black')



    def searchForNonDelaunay(self, cloud, cir, draw, im):
        center_c = ()
        i=0
        while i<len(cloud):
            ''' take one point and find its triangles'''
            my_point = cloud[i]
            my_triangles = self.findMyTriangles(my_point, self.triangles)
        
            j=0
            while j<len(my_triangles):
                ''' find center of the circumcircle '''
                center = cir.center(my_triangles[j][0],my_triangles[j][1],my_triangles[j][2])
                if center!=None:
                    ''' find radius of the circumcircle '''
                    rad_sqr = cir.radius(center, my_triangles[j][0])
                    
                    k=0
                    while k < len(cloud):
                        ''' check if cloud[k] is inside any triangle '''
                        xi = cloud[k][0]
                        yi = cloud[k][1]
                           
                        if ((xi-center[0])**2+(yi-center[1])**2) < rad_sqr:
                            ''' cloud[k] is inside the circle => triangle[j] is not Delaunay '''
                            
                            ''' find biggest side to flip '''
                            big_side = self.findBigSide(my_triangles[j][0],my_triangles[j][1],my_triangles[j][2])
                            ''' find neighbor '''
                            n = self.neighborTriangle(my_triangles[j], big_side)
                            if n!=None:
                                neighbor = n[0]
                                opposite_point = n[1]
                            
                                self.flip(my_triangles[j], neighbor, my_point, opposite_point, big_side)                            
                            k = len(cloud)
                        k=k+1
                else:
                    print 'no center'
                    
                j=j+1
            i=i+1
                    
                    
    def findBigSide(self, p1,p2,p3):
        s1 = self.euclDist(p1,p2)
        s2 = self.euclDist(p2,p3)
        s3 = self.euclDist(p3,p1)
        bs = max(s1,s2,s3)
        if bs==s1:
            return (p1,p2)
        elif bs==s2:
            return (p2,p3)
        else:
            return (p3,p1)


    def euclDist(self, p1, p2):
        ''' calculate euclidean distance WITHOUT the root '''
        dist = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
        return dist


    def findMyTriangles(self, point, triangles):
        my_triangles = []
            
        for i in range(len(triangles)):
            for j in range(0,3):
                if triangles[i][j]==point:
                    my_triangles.append(triangles[i])
        
        return my_triangles
    

    def neighborTriangle(self, my_triangle, big_side):
        ''' returns neighbor triangle and opposite point '''
        neighbor = None
        bs = set(big_side)
        mytri = set(my_triangle)
        
        i=0
        while i < len(self.triangles):
            tri = set(self.triangles[i])
            if self.triangles[i]!=my_triangle and bs.issubset(tri):
                opposite_point = (tri.difference(bs)).pop()
                my_point = (mytri.difference(bs)).pop()
                if self.isThereIntersection(big_side, (my_point,opposite_point)):
                    #print 'there is intersection'                        
                    neighbor = self.triangles[i]
                i = len(self.triangles)
            i=i+1        

        if neighbor!=None:
            return (neighbor, opposite_point)
        else:
            return None


    def isThereIntersection(self, segA, segB):
        flag = False
        x1 = float(segA[0][0])
        y1 = float(segA[0][1])

        x2 = float(segA[1][0])
        y2 = float(segA[1][1])

        x3 = float(segB[0][0])
        y3 = float(segB[0][1])
                
        x4 = float(segB[1][0])
        y4 = float(segB[1][1])
                   
        if (segA==segB or (segB[1]==segA[0] and segB[0]==segA[1])):
            ''' segments have 2 common points so there is already this segment'''
        elif (segB[0]==segA[0] or segB[1]==segA[1] or segB[1]==segA[0] or segB[0]==segA[1]):
            ''' segments have one common point so there is no intersection! '''
        else:
            if ((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))!=0 and (x4-x3)!=0 and (x2-x1)!=0 :
                ''' calculate the point intersection of two lines '''
                pi_x = ((x1*y2-y1*x2)*(x3-x4)-((x1-x2)*(x3*y4-y3*x4)))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
                pi_y = ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
                        
                #L1 == y1+((y2-y1)/(x2-x1))*(pi_x-x1)  # = pi_y
                #L2 = y3+((y4-y3)/(x4-x3))*(pi_x-x3)  # = pi_y
                print pi_x,pi_y,
                print ((x1,y1),(x2,y2)), ((x3,y3),(x4,y4))
                if min(x1,x2)<pi_x<max(x1,x2) and min(x3,x4)<pi_x<max(x3,x4) and min(y1,y2)<pi_y<max(y1,y2) and min(y3,y4)<pi_y<min(y3,y4):
                    print ''' intersection! '''
                    flag = True
                else:
                    print ''' NO intersection!'''
                    flag =False
            else:
                print 'wtf'
        return flag
    

    def flip(self, my_triangle, neighbor, my_point, opposite_point, common_side):        
        self.triangles.remove(my_triangle)
        self.triangles.remove(neighbor)
        babis1 = [my_point, common_side[0], opposite_point]
        babis2 = [my_point, common_side[1], opposite_point]
        self.triangles.append([my_point, common_side[0], opposite_point])
        self.triangles.append([my_point, common_side[1], opposite_point])
        

    def deleteSameTriangles(self):
        i = 0
        while i<len(self.triangles):
            j = 0
            flag = 0
            while j<len(self.triangles):
                tr1 = set(self.triangles[i])
                tr2 = set(self.triangles[j])
                f = tr1.intersection(tr2)
                if len(f)==3:                  
                    flag = flag+1
                j = j+1
            if flag>1:
                self.triangles.remove(self.triangles[i])
            
            i = i+1


if __name__=='__main__':
    im = Image.new("RGBA", (1000,800), (255,255,255,255))
    draw = ImageDraw.Draw(im)

    points = int(raw_input("How many points?"))
    
    c = convex_hull.Cloud(draw, points)
    cv = convex_hull.ConvHull(draw, c.cloud)
    st = simpleTriangulation.simpleTriangulation(draw, c, cv)
    im.save('before.png')

##    dt = delaunay_check.DelaunayCheck(draw, st.triangles, c.cloud, cv.polygon)
    d = Delaunay(draw, st, c.cloud, cv.polygon, im)
    im.save("new.png")

    
