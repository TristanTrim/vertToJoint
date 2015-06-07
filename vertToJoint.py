import sys
import stl
from collections import defaultdict
from math import sqrt
import math

rounding_percision=4
drawAllEdges = False

def getJoints(mesh):
    print(mesh.__dict__)
    return(mesh)


  ## the normals from the stl library are untrustworthy. Someone look at whether this is an stl file thing or a python stl lib thing. Let me know.
# This is a simple function to find plane inclination. It uses cross products to find the normal of a plane which is being represented by 3 arbitrary points.
# I want to read more about matrixes, quaternions, and rotation in general. And math in general.
def getNormalNormal(face):
    vect1 = [face[1][i] - face[0][i] for i in range(0,3)]
    vect2 = [face[2][i] - face[0][i] for i in range(0,3)]
    norm = (vect1[1]*vect2[2] - vect1[2]*vect2[1],
            vect1[2]*vect2[0] - vect1[0]*vect2[2],
            vect1[0]*vect2[1] - vect1[1]*vect2[0],)
    return(normalifyVector(norm))

def normalifyVector(norm):
    magnitude = sqrt(norm[0]**2+norm[1]**2+norm[2]**2)
    normnorm = (norm[0]/magnitude,norm[1]/magnitude,norm[2]/magnitude)
    if normnorm[0]<0:
        return(tuple(-normnorm[i] for i in range(0,3)))
    elif normnorm[0]==0 and normnorm[1]<0:
        return(tuple(-normnorm[i] for i in range(0,3)))
    elif normnorm[0]==0 and normnorm[1]==0 and normnorm[2]>0:
        return(tuple(-normnorm[i] for i in range(0,3)))
    else:
        return(normnorm)

#no.
def get_combined_face(facebits):
    combined_vertices=set()
    for vertex in facebits:
        combined_vertices.add(vertex)
        combined_vertices.update(get_combined_face(vertmap.pop(vertex)))
    
    return(vertices.union(get_combined_face(facebits[1])))


if __name__=='__main__':
    fl = open(sys.argv[1])
    print(sys.argv[1])
    try:
        mesh = stl.read_binary_file(fl)
    except stl.binary.FormatError:
        mesh = stl.read_ascii_file(fl)

    # planes in stl files are made up of many triangles. We only want to have joints at the corners, where they are needed.
    # To determine what faces can be combined, faces can be group'd by thier inclination. Not all faces with the same inclination will combine, but a lot will.
    normal2tris=defaultdict(set)
    tri2normal={}
    vert2tris=defaultdict(set)
    vert2normals=defaultdict(set)
    tri2edges=defaultdict(set)

    for tri in mesh.facets:
        #round the things so that we can get floating point coordinate-vertices to land on the same little reality block.
        tri = tuple(tuple(round(ordo,rounding_percision) for ordo in vertex) for vertex in tri.vertices)
        # add this face to the data dicts.
        normal = getNormalNormal(tri)
        normal2tris[normal].add(tri)
        tri2normal[tri] = normal
        for vertNum in [0,1,2]:
            vert2tris[tri[vertNum]].add(tri)
            vert2normals[tri[vertNum]].add(normal)
            for ii in [0,1,2]:
                tri2edges[tri].add(
                    tuple(sorted((tri[ii-1],tri[ii])))
                        )
    joints=[]

    for center_vert,tris in vert2tris.iteritems():
    #for center_vert,tris in (((1,1,1),vert2tris[(1,1,1)]),):
        print("vert {}".format(center_vert))
        useable_tris=[]# usable_tris fills up with tris translated such that center vert = (0,0,0)
        if not drawAllEdges:
            useable_tris = []
            for normal in vert2normals[center_vert]:
                normalTris=list(tri for tri in normal2tris[normal] if center_vert in tri)
                while True:
                    tri = normalTris.pop()
                    if not normalTris:
                        useable_tris+=[tri]
                        break
                    for otherTri in normalTris:
                        these_edges = tri2edges[tri]
                        other_edges = tri2edges[otherTri]
                        shared_edges = these_edges.intersection(other_edges)
                        if shared_edges:
                            normalTris.remove(otherTri)
                            useable_edges = tuple(( edge for edge in
                                these_edges.symmetric_difference(other_edges)
                                if center_vert in edge))
                            new_tri = tuple(set(vert for edge in
                                        useable_edges
                                        for vert in edge))
                            normalTris+=[new_tri]
                            break
                        useable_tris+=[tri]
        else:
            useable_tris = tris
        # translate
        useable_tris = tuple(
                tuple(
                    tuple(
                        vert[ii] - center_vert[ii]
                        for ii in [0,1,2])
                    for vert in tri)
                for tri in useable_tris)

        average_vecter = [0,0,0]
        for tri in useable_tris:
            for vert in tri:
                for ii in [0,1,2]:
                    average_vecter[ii]+=vert[ii]
        #average_vecter = normalifyVector(average_vecter)
        print(average_vecter)

        average_angle_x = ((math.atan2(average_vecter[1],average_vecter[2]))%(2*math.pi))
        #rotate
        x_rotated_tris = tuple((
                    tuple((
                        tuple((
                            vert[0],
                            vert[1]*math.cos(average_angle_x) + vert[2]*-math.sin(average_angle_x),
                            vert[1]*math.sin(average_angle_x) + vert[2]*math.cos(average_angle_x),
                        ))
                    for vert in tri ))
                for tri in useable_tris ))
        average_vecter_y = (average_vecter[0],
                          average_vecter[1]*math.cos(average_angle_x) + average_vecter[2]*-math.sin(average_angle_x),
                          average_vecter[1]*math.sin(average_angle_x) + average_vecter[2]*math.cos(average_angle_x),
                          )
        print(average_vecter_y)
        average_angle_y = (0*math.pi/2)+((math.atan2(average_vecter_y[0],average_vecter_y[2]))%(2*math.pi))
        rotated_tris = tuple((
                    tuple((
                        tuple((
                            round(vert[0]*math.cos(average_angle_y) + vert[2]*-math.sin(average_angle_y),2),
                            round(vert[1],2),
                            round(vert[0]*math.sin(average_angle_y) + vert[2]*math.cos(average_angle_y),2),
                        ))
                        for vert in tri ))
                     for tri in x_rotated_tris ))

        from pprint import pprint
        pprint("un rot tri")
        pprint(average_vecter)
        pprint(useable_tris)
        pprint("x rot tri")
        pprint(average_angle_x)
        pprint(x_rotated_tris)
        pprint("rot tri")
        pprint(average_angle_y)
        pprint(rotated_tris)


