import cv2 as cv
import numpy as np


class CutImage():
	img = cv.imread('a.jpg')
	bgdModel = np.zeros((1,65),np.float64)
	fgdModel = np.zeros((1,65),np.float64)
	def __init__(self, mask_file_path, mode=0, rect=None, ):
		'''mode=0 - mask mode
		   mode=1 - rectangle mode
		'''
		self.mode = mode
		self.mask_file_path = mask_file_path
		#default empty mask
		self.mask = np.zeros(self.img.shape[:2], dtype = np.uint8)
		self.init_mode(mode)
		self.output = np.zeros(self.img.shape, np.uint8)
		self.cut()
		self.savefile() 

	def cut(self):
		mask,bg,fg= cv.grabCut(self.img, 
			       			self.mask, 
			       			self.rect, 
			       			self.bgdmodel, 
			       			self.fgdmodel, 
			       			iterCount=1, 
			       			mode=self.mode)
		#mul_mask = np.where((self.mask==1) + (self.mask==3), 255, 0).astype('uint8')
		#self.output = cv.bitwise_and(self.img2, self.img2, mask=mul_mask)
		mask = np.where((mask==2)|(mask==0),0,1).astype('uint8')
		self.output = self.img*mask[:,:,np.newaxis]

	def init_mode(self, mode):
		if mode == 0:
			self.mode = cv.GC_INIT_WITH_MASK
			newmask = cv.imread(self, self.mask_file_path,0)
			# wherever it is marked white (sure foreground), change mask=1
			self.mask[newmask == 255] = cv.GC_FGD
			# wherever it is marked black (sure background), change mask=0
			self.mask[newmask == 0] = cv.GC_BGD
		elif mode == 1:
			self.mode = cv.GC_INIT_WITH_RECT
		else: 
			print("Wrong Mode spacified!")
			self.mode = None

	def savefile(self):
		cv.imwrite('grabcut_output.png', self.output)
		
