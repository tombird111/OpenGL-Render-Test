#Import modules for loading models and applying shaders/textures
from BaseModel import BaseModel,DrawModelFromMesh
from mesh import *
from cubeMap import CubeMap
from shaders import *
#Import modules for framebuffer usage
from framebuffer import Framebuffer
from OpenGL.GL.framebufferobjects import *

class EnvironmentShader(BaseShaderProgram):
    def __init__(self, name='environment', map=None):
        #Create a shader program with uniforms "sampler cube" and a collection of matrix uniforms
        BaseShaderProgram.__init__(self, name=name)
        self.add_uniform('sampler_cube')
        self.add_uniform('VM')
        self.add_uniform('VMiT')
        self.add_uniform('VT')
        self.map = map

    def bind(self, model, M):
        glUseProgram(self.program) #Use the shader program
        if self.map is not None: #Map the current texture of the cube map into the 'sampler_cube' uniform
            unit = len(model.mesh.textures)
            glActiveTexture(GL_TEXTURE0)
            self.map.bind()
            self.uniforms['sampler_cube'].bind(0)
        P = model.scene.P  #Get the projection matrix from the scene
        V = model.scene.camera.V  #Get the view matrix from the camera
        #Bind the PVM uniforms
        self.uniforms['PVM'].bind(np.matmul(P, np.matmul(V, M)))
        self.uniforms['VM'].bind(np.matmul(V, M))
        self.uniforms['VMiT'].bind(np.linalg.inv(np.matmul(V, M))[:3, :3].transpose())
        self.uniforms['VT'].bind(V.transpose()[:3, :3])


class EnvironmentMappingTexture(CubeMap):
    def __init__(self, width=200, height=200):
        #Create a cube map
        CubeMap.__init__(self)
        #Note that the environment mapping is not done, and store the width and height
        self.done = False
        self.width = width
        self.height = height
        #Create frame buffers for each face of the cube
        self.fbos = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: Framebuffer()
        }
        #Map the possible views into the framebuffers for each face of the cube
        t = 0.0
        self.views = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: np.matmul(translationMatrix([0, 0, t]), rotationMatrixY(-np.pi/2.0)),
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: np.matmul(translationMatrix([0, 0, t]), rotationMatrixY(+np.pi/2.0)),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: np.matmul(translationMatrix([0, 0, t]), rotationMatrixX(+np.pi/2.0)),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: np.matmul(translationMatrix([0, 0, t]), rotationMatrixX(-np.pi/2.0)),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: np.matmul(translationMatrix([0, 0, t]), rotationMatrixY(-np.pi)),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: translationMatrix([0, 0, t]),
        }
        #Bind the cube
        self.bind()
        #Prepare a framebuffer object for 2D images of each face of the cube
        for (face, fbo) in self.fbos.items():
            glTexImage2D(face, 0, self.format, width, height, 0, self.format, self.type, None)
            fbo.prepare(self, face)
        self.unbind()

    def update(self, scene):
        if self.done:
            return
        #Bind the information
        self.bind()
        #Get the projection of the scene
        Pscene = scene.P
        scene.P = frustumMatrix(-1.0, +1.0, -1.0, +1.0, 1.0, 20.0)
        glViewport(0, 0, self.width, self.height)
        #Draw the reflections and update the camera for each face of the cube
        for (face, fbo) in self.fbos.items():
            fbo.bind()
            scene.camera.V = self.views[face]
            scene.draw_reflections()
            scene.camera.update()
            fbo.unbind()
        #Reset the viewport
        glViewport(0, 0, scene.window_size[0], scene.window_size[1])
        scene.P = Pscene
        self.unbind()
