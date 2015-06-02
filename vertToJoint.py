import sys
import stl
from collections import defaultdict
from math import sqrt

rounding_percision=4

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
    magnitude = sqrt(norm[0]**2+norm[1]**2+norm[2]**2)
    normnorm = (norm[0]/magnitude,norm[1]/magnitude,norm[2]/magnitude)
    if normnorm[0]>0:
        return(tuple(-normnorm[i] for i in range(0,3)))
    elif normnorm[0]==0 and normnorm[1]>0:
        return(tuple(-normnorm[i] for i in range(0,3)))
    elif normnorm[0]==0 and normnorm[1]>0:
        return(tuple(-normnorm[i] for i in range(0,3)))
    elif normnorm[0]==0 and normnorm[1]==0 and normnorm[2]>0:
        return(tuple(-normnorm[i] for i in range(0,3)))
    else:
        return(normnorm)

if __name__=='__main__':
    fl = open(sys.argv[1])
    print(sys.argv[1])
    try:
        mesh = stl.read_binary_file(fl)
    except stl.binary.FormatError:
        mesh = stl.read_ascii_file(fl)

    # planes in stl files are made up of many triangles. We only want to have joints at the corners, where they are needed.
    # To determine what faces can be combined, faces can be group'd by thier inclination. Not all faces with the same inclination will combine, but a lot will.
    face_normal_grouping=defaultdict(set)

    for face in mesh.facets:
        face = tuple((tuple((round(ordo,rounding_percision) for ordo in vertex)) for vertex in face.vertices))
        normal = getNormalNormal(face)
        face_normal_grouping[normal].add(face)

    faces = []

    for face_normal in face_normal_grouping:
        from pprint import pprint
        pprint(face_normal)
