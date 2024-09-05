#Import useful functions
from matutils import *


class Camera:
    '''
    Base class for handling the camera.
    '''

    def __init__(self):
        self.V = np.identity(4)
        self.phi = 0.               #Azimuth angle
        self.psi = 0.               #Zenith angle
        self.distance = 5.         #Distance of the camera to the centre point
        self.center = [0., 0., 0.]  #Position of the centre
        self.update()               #Calculate the view matrix

    def update(self):
        '''
        Function to update the camera view matrix from parameters.
        '''
        #Calculate the translation matrix for the view center (the point we look at)
        T0 = translationMatrix(self.center)
        #Calculate the rotation matrix from the angles phi (azimuth) and psi (zenith) angles.
        R = np.matmul(rotationMatrixX(self.psi), rotationMatrixY(self.phi))
        #Calculate translation for the camera distance to the center point
        T = translationMatrix([0., 0., -self.distance])
        #Combine the three matrices for the final transformation
        self.V = np.matmul(np.matmul(T, R), T0)