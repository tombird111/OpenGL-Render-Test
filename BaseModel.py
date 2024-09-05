#Imports all openGL functions
from OpenGL.GL import *
#Import helper functions
from matutils import *
#Import modules for loading models and applying shaders/textures
from material import Material
from mesh import Mesh
from shaders import *
from texture import Texture

class BaseModel:
    '''
    Base class for all models, implementing the basic draw function for triangular meshes.
    Inherit from this to create new models.
    '''
    def __init__(self, scene, M=poseMatrix(), mesh=Mesh(), color=[1., 1., 1.], primitive=GL_TRIANGLES, visible=True):
        '''
        Initialises the model data
        scene refers to the scene the model is in
        M refers to the position of the model within the scene
        mesh refers to the mesh of the model
        color refers to the colour of the model (prior to texturing/shading)
        primitive refers to the way the model is drawn, whether it is from triangles or squares
        visible refers to whether the model will initially be visible
        '''
        print('+ Initializing {}'.format(self.__class__.__name__))
        #Store the initialised information
        self.visible = visible
        self.scene = scene
        self.primitive = primitive
        self.color = color
        #Store the shader program for rendering this model
        self.shader = None
        #Store the mesh data
        self.mesh = mesh
        self.name = self.mesh.name
        #Create dictionaries to store visual buffer objects and attributes
        self.vbos = {}
        self.attributes = {}
        #Store the position of the model in the scene
        self.M = M
        #Use a vertex array to pack all buffers for GPU rendering
        self.vao = glGenVertexArrays(1)
        #If shared vertex representation is used, a buffer will be used to store the current location within the array
        self.index_buffer = None

    def initialise_vbo(self, name, data):
        if data is None:
            print('(W) Warning in {}.bind_attribute(): Data array for attribute {} is None!'.format(
                self.__class__.__name__, name))
            return

        #Bind the location of the attribute in the GLSL program to the next index
        self.attributes[name] = len(self.vbos)
        #Create a buffer object to store the attribute
        self.vbos[name] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbos[name])
        glEnableVertexAttribArray(self.attributes[name])
        #Associate the bound buffer to the corresponding input location in the shader
        glVertexAttribPointer(index=self.attributes[name], size=data.shape[1], type=GL_FLOAT, normalized=False,
                              stride=0, pointer=None)
        #Put the vertex array data into the buffer
        glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)

    def bind_shader(self, shader):
        '''
        If a new shader is bound, we need to re-link it to ensure attributes are correctly linked.  
        '''
        #If there is no shader, or the name of the shader is invalid
        if self.shader is None or self.shader.name is not shader:
            if isinstance(shader, str): #Check if there is a shader available for that name
                self.shader = PhongShader(shader) #If there is, create a new shader of that type using the shader information
            else:
                self.shader = shader #Use the new shader
            #Bind all attributes and compile the shader
            self.shader.compile(self.attributes)

    def bind(self):
        '''
        This method stores the vertex data in a Vertex Buffer Object (VBO) that can be uploaded
        to the GPU at render time.
        '''
        #Bind the VAO to retrieve all buffers and rendering context
        glBindVertexArray(self.vao)
        if self.mesh.vertices is None:
            print('(W) Warning in {}.bind(): No vertex array!'.format(self.__class__.__name__))
        # initialise vertex position VBO and link to shader program attribute
        self.initialise_vbo('position', self.mesh.vertices)
        self.initialise_vbo('normal', self.mesh.normals)
        self.initialise_vbo('color', self.mesh.colors)
        self.initialise_vbo('texCoord', self.mesh.textureCoords)
        self.initialise_vbo('tangent', self.mesh.tangents)
        self.initialise_vbo('binormal', self.mesh.binormals)
        #If indices are provided, put them in a buffer too
        if self.mesh.faces is not None:
            self.index_buffer = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.mesh.faces, GL_STATIC_DRAW)
        #Finally we unbind the VAO and VBO when we're done to avoid side effects
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, Mp=poseMatrix()):
        '''
        Draws the model using OpenGL functions.
        Mp refers to the model matrix of the parent object, for composite objects.
        '''
        if self.visible:
            if self.mesh.vertices is None:
                print('(W) Warning in {}.draw(): No vertex array!'.format(self.__class__.__name__))
            #Bind the Vertex Array Object so that all buffers are bound correctly and following operations affect them
            glBindVertexArray(self.vao)
            #Setup the shader program and provide it the model and its position relative to where it is being drawn
            #For rendering this model
            self.shader.bind(
                model=self,
                M=np.matmul(Mp, self.M)
            )
            #Bind all textures
            for unit, tex in enumerate(self.mesh.textures):
                glActiveTexture(GL_TEXTURE0 + unit)
                tex.bind()
            #Check whether the data is stored as vertex array or index array
            if self.mesh.faces is not None:
                #Draw the data in the buffer using the index array
                glDrawElements(self.primitive, self.mesh.faces.flatten().shape[0], GL_UNSIGNED_INT, None )
            else:
                #Draw the data in the buffer using the vertex array ordering only.
                glDrawArrays(self.primitive, 0, self.mesh.vertices.shape[0])
            #Unbind the shader to avoid side effects
            glBindVertexArray(0)

    def vbo__del__(self):
        '''
        Release all VBO objects when finished.
        '''
        for vbo in self.vbos.items():
            glDeleteBuffers(1, vbo)
        glDeleteVertexArrays(1,self.vao.tolist())


class DrawModelFromMesh(BaseModel):
    '''
    Base class for all models, inherit from this to create new models
    '''

    def __init__(self, scene, M, mesh, name=None, shader=None, visible=True):
        '''
        Initialises the model data
        '''
        #Create a model using the inputted information
        BaseModel.__init__(self, scene=scene, M=M, mesh=mesh, visible=visible)
        #Name the model if one is provided
        if name is not None:
            self.name = name
        #Check the type of primitives used for drawing
        if self.mesh.faces.shape[1] == 3:
            self.primitive = GL_TRIANGLES
        elif self.mesh.faces.shape[1] == 4:
            self.primitive = GL_QUADS
        else:
            print('(E) Error in DrawModelFromObjFile.__init__(): index array must have 3 (triangles) or 4 (quads) columns, found {}!'.format(self.indices.shape[1]))
        self.bind()
        if shader is not None:
            self.bind_shader(shader)
