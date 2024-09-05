#Import numpy for matrix functionality
import numpy as np
#Import textures and materials
from texture import Texture
from material import Material

class Mesh:
    '''
    Simple class to hold a mesh data. For now we will only focus on vertices, faces (indices of vertices for each face)
    and normals.
    '''
    def __init__(self, vertices=None, faces=None, normals=None, textureCoords=None, material=Material()):
        '''
        Initialises a mesh object.
        :param vertices: A numpy array containing all vertices
        :param faces: [optional] An int array containing the vertex indices for all faces.
        :param normals: [optional] An array of normal vectors, calculated from the faces if not provided.
        :param material: [optional] An object containing the material information for this object
        '''
        #Store all information relevant to the mesh
        self.name = 'Unknown'
        self.vertices = vertices
        self.faces = faces
        self.material = material
        self.colors = None
        self.textureCoords = textureCoords
        self.textures = []
        self.tangents = None
        self.binormals = None
        #Create a mesh from the set of inputted vertices
        if vertices is not None:
            print('Creating mesh')
            print('- {} vertices'.format(self.vertices.shape[0]))
            if faces is not None:
                print('- {} faces'.format(self.faces.shape[0]))
        #Calculate the normals in code of they are not provided
        if normals is None:
            if faces is None:
                print('(W) Warning: the current code only calculates normals using the face vector of indices, which was not provided here.')
            else:
                self.calculate_normals()
        else:
            self.normals = normals
        #If a texture is supplied, apply it
        if material.texture is not None:
            self.textures.append(Texture(material.texture))


    def calculate_normals(self):
        ''' Method to calculate normals from the mesh faces '''
        #Create an array of empty matrices for the normals
        self.normals = np.zeros((self.vertices.shape[0], 3), dtype='f')
        #If there are texture co-ordinates, create an array of empty matrices for the binormals and tangents as well
        if self.textureCoords is not None:
            self.tangents = np.zeros((self.vertices.shape[0], 3), dtype='f')
            self.binormals = np.zeros((self.vertices.shape[0], 3), dtype='f')
        for f in range(self.faces.shape[0]):
            #Calculate the face normal using the cross product of the triangle's sides
            a = self.vertices[self.faces[f, 1]] - self.vertices[self.faces[f, 0]]
            b = self.vertices[self.faces[f, 2]] - self.vertices[self.faces[f, 0]]
            face_normal = np.cross(a, b)
            #Calculate the tangents and binormals by using the previously calculated normals 
            if self.textureCoords is not None:
                txa = self.textureCoords[self.faces[f, 1], :] - self.textureCoords[self.faces[f, 0], :]
                txb = self.textureCoords[self.faces[f, 2], :] - self.textureCoords[self.faces[f, 2], :]
                face_tangent = txb[0]*a - txa[0]*b
                face_binormal = -txb[1]*a + txa[1]*b
            #Blend the normal on all 3 vertices
            for j in range(3):
                self.normals[self.faces[f, j], :] += face_normal
                if self.textureCoords is not None:
                    self.tangents[self.faces[f, j], :] += face_tangent
                    self.binormals[self.faces[f, j], :] += face_binormal
        #Finally, the vectors are normalised
        self.normals /= np.linalg.norm(self.normals, axis=1, keepdims=True)
        if self.textureCoords is not None:
            self.tangents /= np.linalg.norm(self.tangents, axis=1, keepdims=True)
            self.binormals /= np.linalg.norm(self.binormals, axis=1, keepdims=True)


class CubeMesh(Mesh):
    def __init__(self, texture=None, inside=False):
        #Create an array for a cubes vertices
        vertices = np.array([

            [-1.0, -1.0, -1.0],  # 0
            [+1.0, -1.0, -1.0],  # 1

            [-1.0, +1.0, -1.0],  # 2
            [+1.0, +1.0, -1.0],  # 3

            [-1.0, -1.0, +1.0],  # 4
            [-1.0, +1.0, +1.0],  # 5

            [+1.0, -1.0, +1.0],  # 6
            [+1.0, +1.0, +1.0]  # 7

        ], dtype='f')
        #Create an array for a cubes faces
        faces = np.array([

            # back
            [1, 0, 2],
            [1, 2, 3],

            # right
            [2, 0, 4],
            [2, 4, 5],

            # left
            [1, 3, 7],
            [1, 7, 6],

            # front
            [5, 4, 6],
            [5, 6, 7],

            # bottom
            [0, 1, 4],
            [4, 1, 6],

            # top
            [2, 5, 3],
            [5, 7, 3],

        ], dtype=np.uint32)
        #If you are expected to be inside the box, rotate the faces so they are facing inwards
        if inside:
            faces = faces[:, np.argsort([0, 2, 1])]
        #Create a mesh with the faces and vertices
        textureCoords = None
        Mesh.__init__(self, vertices=vertices, faces=faces, textureCoords=textureCoords)
        #Apply the textures if they are supplied
        if texture is not None:
            self.textures = [
                texture
            ]