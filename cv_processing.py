from PIL import Image, ImageTk, ImageDraw, ImageOps
import cv2 as cv
import numpy as np


class CutImage():
	#img = cv.imread("images")
	bgdmodel = np.zeros((1,65),np.float64)
	fgdmodel = np.zeros((1,65),np.float64)
	def __init__(self, img, mask, mode=0, rect=(0,0,1,1), ):
		'''mode=0 - mask mode
		   mode=1 - rectangle mode
		'''
		img.save('temp_img.jpg')
		self.rect = rect
		#self.img = np.array(img)
		#cv.imwrite('temp_img.jpg', self.img)
		self.img = cv.imread("temp_img.jpg")
		self.newmask = np.array(mask)
		print("Shape img", self.img.shape)
		print("Shape newmask", self.newmask.shape)
		cv.imwrite('mask.png', self.newmask)
		cv.imwrite('img_cv_proc.png', self.img)
		#self.mask_file_path = mask_file_path
		#default empty mask
		self.mask = np.zeros(self.img.shape[:2], dtype = np.uint8)
		print("Shape zeromask", self.mask.shape)
		self.init_mode(mode)
		self.output = np.zeros(self.img.shape, np.uint8)
		print("RECT to CUT  - ", self.rect)
		mask, b,f = cv.grabCut(self.img, 
			       			self.mask, 
			       			self.rect, 
			       			self.bgdmodel, 
			       			self.fgdmodel, 
			       			1, 
			       			cv.GC_INIT_WITH_RECT)
		self.cut()
		self.savefile() 

	def cut(self):
		print(self.mode)
		img2 = Image.fromarray(self.img)
		mask, b,f = cv.grabCut(self.img, 
			       			self.mask, 
			       			None, 
			       			self.bgdmodel, 
			       			self.fgdmodel, 
			       			1, 
			       			self.mode)
		#mul_mask = np.where((self.mask==1) + (self.mask==3), 255, 0).astype('uint8')
		#self.output = cv.bitwise_and(self.img2, self.img2, mask=mul_mask)
		#mask = np.where((mask==2)|(mask==0),0,1).astype('uint8')
		#self.output = self.img*mask[:,:,np.newaxis]
		mask2 = np.where((mask==1) + (mask==3), 255, 0).astype('uint8')
		self.output = cv.bitwise_and(self.img, self.img, mask=mask2)

	def init_mode(self, mode):
		if mode == 0:
			self.mode = cv.GC_INIT_WITH_MASK
			#newmask = cv.imread(self.mask_file_path,0)
			# wherever it is marked white (sure foreground), change mask=1
			self.mask[self.newmask == 255] = cv.GC_FGD
			# wherever it is marked black (sure background), change mask=0
			self.mask[self.newmask == 0] = cv.GC_BGD
		elif mode == 1:
			self.mode = cv.GC_INIT_WITH_RECT
		else: 
			print("Wrong Mode spacified!")
			self.mode = None

	def savefile(self):
		self.output = cv.cvtColor(self.output, cv.COLOR_RGB2BGR)
		cv.imwrite('grabcut_output.png', self.output)
		
