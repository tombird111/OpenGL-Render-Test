#Pygame is just used to create a window with the operating system on which to draw.
import pygame
#Imports all openGL functions
from OpenGL.GL import *
#Import helper functions
from matutils import *
#Import the shaders, camera and lightsource
from shaders import *
from camera import Camera
from lightSource import LightSource

class Scene:
    '''
    This is the main class for adrawing an OpenGL scene using the PyGame library
    '''
    def __init__(self, width=800, height=600, shaders=None):
        '''
        Initialises the scene
        '''
        #Create the pygame window, and set wireframe to off
        self.window_size = (width, height)
        self.wireframe = False
        pygame.init()
        screen = pygame.display.set_mode(self.window_size, pygame.OPENGL | pygame.DOUBLEBUF, 24)
        #Here we start initialising the window from the OpenGL side
        glViewport(0, 0, self.window_size[0], self.window_size[1])
        #This selects the background color
        glClearColor(0.7, 0.7, 1.0, 1.0)
        #Enable back face culling
        glEnable(GL_CULL_FACE)
        #Enable the vertex array capability
        glEnableClientState(GL_VERTEX_ARRAY)
        # enable depth test for clean output
        glEnable(GL_DEPTH_TEST)
        #Set the default shader program
        self.shaders = 'flat'

        #Create the initial information for the projection
        near = 1.0
        far = 20.0
        left = -1.0
        right = 1.0
        top = -1.0
        bottom = 1.0

        #Cycle through models
        self.show_model = -1

        #Set the projection of the scene to be a frustumMatrix using the initial information
        self.P = frustumMatrix(left, right, top, bottom, near, far)

        #Initialises the camera object and lighting
        self.camera = Camera()
        self.light = LightSource(self, position=[5., 5., 5.])
        #Set the rendering mode for shaders
        self.mode = 1
        #Create a list of models to be drawn in the scene
        self.models = []

    def add_model(self, model):
        '''
        This method just adds a model to the scene.
        :param model: The model object to add to the scene
        '''
        self.models.append(model)

    def add_models_list(self, models_list):
        '''
        This method just adds a list of models to the scene.
        :param model: The list of models to add to the scene
        '''
        for model in models_list:
            self.add_model(model)

    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''
        #First, clear the scene if there is no framebuffer in use, and update the camera
        if not framebuffer:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.camera.update()
        #Loop over all models in the list and draw them
        for model in self.models:
            model.draw()
        #Once this is done, the displayed frame is flipped
        #Essentially, this means the frame we are drawing on is displayed, and the previously displayed frame is now used for drawing again
        #This prevents viewing of the drawing process
        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Method to process keyboard events. Check Pygame documentation for a list of key events
        :param event: the event object that was raised
        '''
        #Stop running the program is q is pressed
        if event.key == pygame.K_q:
            self.running = False

    def pygameEvents(self):
        '''
        Method to handle PyGame events for user interaction.
        '''
        # check whether the window has been closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            #If a key is pressed, perform the respective action
            elif event.type == pygame.KEYDOWN:
                self.keyboard(event)
            elif event.type == pygame.MOUSEBUTTONDOWN: #If a mouse button is pressed
                mods = pygame.key.get_mods()
                if event.button == 4: #Move the light if the scroll wheel is moved whilst holding control, or the camera if control is not held
                    if mods & pygame.KMOD_CTRL: 
                        self.light.position *= 1.1
                        self.light.update()
                    else:
                        self.camera.distance = max(1, self.camera.distance - 1)
                elif event.button == 5:
                    if mods & pygame.KMOD_CTRL:
                        self.light.position *= 0.9
                        self.light.update()
                    else:
                        self.camera.distance += 1
            elif event.type == pygame.MOUSEMOTION: #Move the camera if the left mouse button is clicked whilst moving
                if pygame.mouse.get_pressed()[0]:
                    if self.mouse_mvt is not None:
                        self.mouse_mvt = pygame.mouse.get_rel()
                        self.camera.center[0] -= (float(self.mouse_mvt[0]) / self.window_size[0])
                        self.camera.center[1] -= (float(self.mouse_mvt[1]) / self.window_size[1])
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()
                elif pygame.mouse.get_pressed()[2]: #Rotate the camera if the left mouse button is clicked whilst moving
                    if self.mouse_mvt is not None:
                        self.mouse_mvt = pygame.mouse.get_rel()
                        #TODO: WS2
                        self.camera.phi -= (float(self.mouse_mvt[0]) / self.window_size[0])
                        self.camera.psi -= (float(self.mouse_mvt[1]) / self.window_size[1])
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()
                else:
                    self.mouse_mvt = None

    def run(self):
        '''
        Draws the scene in a loop until exit.
        '''
        self.running = True
        while self.running:
            self.pygameEvents()
            self.draw()