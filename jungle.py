#Import pygame to run the program
import pygame

#Import the scene class
from scene import Scene
#Import model related classes and functions
from blender import load_obj_file
from BaseModel import DrawModelFromMesh
from sphereModel import Sphere
#Import the environment mapping classes and functions
from environmentMapping import *
from cubeMap import FlattenCubeMap
from shaders import *
#Import the shadow mapping, light sources and skybox modules
from ShadowMapping import *
from lightSource import LightSource
from skyBox import *

class JungleScene(Scene):
    def __init__(self):
        #Initialise the scene using the scene class
        Scene.__init__(self)
        #Create a lightsource for the scene
        self.light = LightSource(self, position=[3., 4., -3.])
        #Use the phong shader within the scene
        self.shaders='phong'
        #Create and show the shadow map
        self.shadows = ShadowMap(light=self.light)
        self.show_shadow_map = ShowTexture(self, self.shadows)
        #Load a series of files and models to be used within the scene
        meshes = load_obj_file('models/palmtree.obj')
        self.add_models_list(
            [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([-3,-1,0]),scaleMatrix([2.,2.,2.])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='palmtree') for mesh in meshes]
        )
        island = load_obj_file('models/island.obj')
        self.island = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([-3,-1,0]),scaleMatrix([0.25,0.25,0.25])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='island') for mesh in island]
        tree = load_obj_file('models/tree.obj')
        self.tree = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([1,-1,0]),scaleMatrix([0.1,0.1,0.1])), mesh=mesh, shader=self.shaders, name='box') for mesh in tree]
        #Draw a skybox for the horizon
        self.skybox = SkyBox(scene=self)
        #Create a light visible at the position the light is coming from within the scene
        self.show_light = DrawModelFromMesh(scene=self, M=poseMatrix(position=self.light.position, scale=0.2), mesh=Sphere(material=Material(Ka=[10,10,10])), shader=FlatShader())
        #After that, draw a texture from the environment for environment mapping
        self.environment = EnvironmentMappingTexture(width=400, height=400)
        #Create a monkey use the environment shader to begin with, which draws from the environment mapping texture
        monkey = load_obj_file('models/Suzanne.obj')
        self.monkey = DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,-1,0]), scaleMatrix([0.25,0.25,0.25])), mesh=monkey[0], shader=EnvironmentShader(map=self.environment))
        #Create a flattened cube map of the environment
        self.flattened_cube = FlattenCubeMap(scene=self, cube=self.environment)

    def draw_shadow_map(self):
        '''Draws a shadow map'''
        #First the buffer is cleared
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #Then these two models are drawn for the purpose of the shadow map
        for model in self.island:
            model.draw()
        for model in self.tree:
            model.draw()

    def draw_reflections(self):
        #Draw the dedicated skybox
        self.skybox.draw()
        #Draw all models
        for model in self.models:
            model.draw()
        # also all models from the island
        for model in self.island:
            model.draw()
        # and for the tree
        for model in self.tree:
            model.draw()


    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''
        #First, the scene and buffer are cleared
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #When using a framebuffer, we do not update the camera to allow for arbitrary viewpoint.
        if not framebuffer:
            self.camera.update()

        #First, the skybox and shadows are drawn and rendered
        self.skybox.draw()
        self.shadows.render(self)

        # when rendering the framebuffer we ignore the reflective object
        if not framebuffer:
            #Update the appearance of the environment
            self.environment.update(self)
            self.monkey.draw()
            #Draw the flattened cube used to simulate the environment for a reflective surface
            self.flattened_cube.draw()
            #Draw the shadow map after the reflections
            self.show_shadow_map.draw()

        #The models are then drawn
        for model in self.models:
            model.draw()
        for model in self.island:
            model.draw()
        for model in self.tree:
            model.draw()
        #With the light drawn after
        self.show_light.draw()

        #Once this is done, the displayed frame is flipped
        #Essentially, this means the frame we are drawing on is displayed, and the previously displayed frame is now used for drawing again
        #This prevents viewing of the drawing process
        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Process additional keyboard events for this demo.
        '''
        Scene.keyboard(self, event)
        #Handles events based on the keyboard
        #C and S allow viewing of the shadow map and cube map respectively
        if event.key == pygame.K_c:
            if self.flattened_cube.visible:
                self.flattened_cube.visible = False
            else:
                print('--> showing cube map')
                self.flattened_cube.visible = True
        if event.key == pygame.K_s:
            if self.show_shadow_map.visible:
                self.show_shadow_map.visible = False
            else:
                print('--> showing shadow map')
                self.show_shadow_map.visible = True

        if event.key == pygame.K_1: #If 1 is pressed, translate the  monkey upwards
            self.monkey.M=np.matmul(translationMatrix([0,1,0]), self.monkey.M)

        if event.key == pygame.K_2: #If 2 is pressed, rotate the monkey around the X axis
            self.monkey.M=np.matmul(rotationMatrixX(1), self.monkey.M)


if __name__ == '__main__':
    #Initialises the scene object
    scene = JungleScene()
    #Begin running the scene
    scene.run()
