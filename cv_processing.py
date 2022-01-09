from PIL import Image, ImageTk, ImageDraw, ImageOps
import cv2 as cv
import numpy as np

class CutImage():
	def __init__(self, img, mask, mode=0, rect=(50,52,55,57), ):
		'''mode=0 - mask mode
		   mode=1 - rectangle mode
		'''
		self.bgdmodel = np.zeros((1,65),np.float64)
		self.fgdmodel = np.zeros((1,65),np.float64)
		img.save('temp_img.jpg')
		self.rect = rect
		self.mask = mask
		print("RECT! ", self.rect)
		print("MODE! ", mode)
		#self.img = np.array(img)
		#cv.imwrite('temp_img.jpg', self.img)
		self.img = cv.imread("temp_img.jpg")
		#self.newmask = np.array(mask)
		print("Shape img", self.img.shape)
		#print("Shape newmask", self.newmask.shape)
		cv.imwrite('mask.png', self.mask)
		cv.imwrite('img_cv_proc.png', self.img)
		
		#default empty mask
		#self.mask = np.zeros(self.img.shape[:2], dtype = np.uint8)
		print("Shape zeromask", self.mask.shape)
		self.init_mode(mode)
		self.output = np.zeros(self.img.shape, np.uint8)
		print("RECT to CUT  - ", self.rect)
		self.mask, self.bgdmodel,self.fgdmodel = cv.grabCut(self.img,self.mask,self.rect, self.bgdmodel,self.fgdmodel,1,cv.GC_INIT_WITH_RECT)
		

	def cut(self):
		print(self.mode)
		if (self.mode == 1): self.rect = None
		
		mask, self.bgdmodel,self.fgdmodel = cv.grabCut(self.img, 
			       			self.mask, 
			       			self.rect, 
			       			self.bgdmodel, 
			       			self.fgdmodel, 
			       			1,
			       			self.mode)
		
		mask2 = np.where((mask==1) + (mask==3), 255, 0).astype('uint8')
		self.output = cv.bitwise_and(self.img, self.img, mask=mask2)
		return True

	def init_mode(self, mode):
		if mode == 0:
			self.mode = cv.GC_INIT_WITH_MASK
			# wherever it is marked white (sure foreground), change mask=1
			#self.mask[self.newmask == 255] = cv.GC_FGD
			# wherever it is marked black (sure background), change mask=0
			#self.mask[self.newmask == 0] = cv.GC_BGD
			#self.rect = None
		elif mode == 1:
			self.mode = cv.GC_INIT_WITH_RECT
		else: 
			print("Wrong Mode spacified!")
			self.mode = None

	def savefile(self):
		cv.imwrite('grabcut_output.png', self.output)
		print("DONE")
		
