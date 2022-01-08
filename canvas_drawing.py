from PIL import Image as PIL_img, ImageTk, ImageDraw, ImageOps
from tkinter import *
from tkinter.filedialog import askopenfilename  
from cv_processing import CutImage  
import cv2 as cv
import time
import os
import numpy as np

class ExampleApp(Frame):
    BLACK = [0,0,0]         # sure BG
    WHITE = [255,255,255]
    DRAW_BG = {'color' : BLACK, 'val' : 0}
    DRAW_FG = {'color' : WHITE, 'val' : 1}
    thickness = 3
    #DRAW_PR_BG = {'color' : RED, 'val' : 2}
    #DRAW_PR_FG = {'color' : GREEN, 'val' : 3}
    
    def __init__(self,master):
        Frame.__init__(self,master=None)
        master.geometry("{0}x{1}".format(master.winfo_screenwidth(),
                                            master.winfo_screenheight()))
        # CREATING CANVAS
        self.x = self.y = 0
        self.canvas_width = master.winfo_screenwidth() - (master.winfo_screenwidth()*0.2)
        self.canvas_height = master.winfo_screenheight() - 353
        self.canvas = Canvas(self, width = self.canvas_width, 
                                    height = self.canvas_height, 
                                    cursor="plus",
                                    highlightthickness = 0)
        # -------------------------------------
        
        # SETTING SCROLLBARS
        self.vbar=Scrollbar(self,orient=VERTICAL)
        self.hbar=Scrollbar(self,orient=HORIZONTAL)
        self.vbar.config(command=self.canvas.yview)
        self.hbar.config(command=self.canvas.xview)

        self.canvas.config(yscrollcommand=self.vbar.set)
        self.canvas.config(xscrollcommand=self.hbar.set)
        self.canvas.config(xscrollincrement = 5, yscrollincrement = 5)

        self.canvas.grid(row=0,column=0,sticky=N+E+S+W)

        self.vbar.grid(row=0,column=1,sticky=N+S)
        self.hbar.grid(row=1,column=0,sticky=E+W)
        self.dot_icon = PhotoImage(file = "dot.png")
        self.plus_icon = PhotoImage(file = "plus.png")
        self.on = PhotoImage(file = "on.png")
        self.off = PhotoImage(file = "off.png")
        # -------------------------------------

        # SETING MODE FOR draw_mode
        self.draw_mode=StringVar()
        self.draw_mode.set("No_mode")

        self.fg_bg_mode = StringVar()
        self.fg_bg_mode.set("FG_mode")

        self.cut_mode = 1
        # -------------------------------------
        
        # CREATING AND SETTING RADIOBUTTONS/BUTTONS
        self.hint = Label(text = "Завантажте зображення та оберіть один із доступних інструментів.")
        self.hint.grid(row = 0, column = 0)
        
        self.cut_hint = Label(text = "")
        self.cut_hint.grid(row = 1, column = 0)
        
        self.lb = Label(text = "Спрощений режим")
        self.lb.grid(row = 0, column = 1)

        self.on_off_mode_value = IntVar()
        self.on_off_mode_value.set(1)
        print ("MODE in drawing " , self.on_off_mode_value.get(),self.cut_mode)
        self.on_off_button = Button(image = self.on, command = self.on_off_mode)
        self.on_off_button.grid(row = 0, column = 2)
        self.rect_button = Radiobutton(text = "Прямокутник", 
                                       image = self.plus_icon, 
                                       command = self.draw,
                                       variable=self.draw_mode,
                                       value="Rectangle_mode",
                                       indicatoron=0,
                                       )
        self.rect_button.grid(row = 1, column = 1, pady = 3)

        self.oval_button = Radiobutton(text = "Спрей", 
                                        image = self.dot_icon, 
                                        command = self.draw,
                                        variable=self.draw_mode,
                                        value="Dot_mode",
                                        indicatoron=0,
                                        state = DISABLED)
        self.oval_button.grid(row = 2, column = 1, pady = 3)

        self.fg_mode_button = Radiobutton(text = "Передній план",
                                            width = 10,
                                            height = 2,
                                            command = self.draw,
                                            variable=self.fg_bg_mode,
                                            value = "FG_mode",
                                            indicatoron = 1)
        self.fg_mode_button.grid(row = 1, column = 2)

        self.bg_mode_button = Radiobutton(text = "Задній план",
                                            width = 10,
                                            height = 2,
                                            command = self.draw,
                                            variable=self.fg_bg_mode,
                                            value = "BG_mode",
                                            indicatoron = 1)
        self.bg_mode_button.grid(row = 2, column = 2)

        self.file_button = Button(text = "Завантажити фото", 
                                    height = 2,
                                    command = self.upload_file)

        self.file_button.grid(row = 3, column = 1, pady = 3)
        
        self.cut_button = Button(text = "Обрізати",
                                    width = 10,
                                    height = 2,
                                    state = DISABLED,
                                    command = self.cutting)
        self.cut_button.grid(row = 4, column = 1, pady = 3)

        self.clean_button = Button(text = "Очистити",
                                        width = 10,
                                        height = 2,
                                        command = self.clean)
        self.clean_button.grid(row = 5, column = 1, pady = 3)

        self.save_button = Button(text = "Зберегти",
                                        width = 10,
                                        height = 2,
                                        command = self.save)
        self.cancel_button = Button(text = "Відмінити",
                                        width = 10,
                                        height = 2,
                                        command = self.cancel)

        # -------------------------------------
        
        # CREATING VARIABLES FOR DRAW OBJ
        self.rect = None
        self.oval = None
        self.rect_FG = None
        # -------------------------------------

        # CREATING VARIABLES FOR START X/Y AND END X/Y
        self.start_x = None
        self.start_y = None

        self.end_x = None
        self.end_y = None
        # -------------------------------------
        self.fg_color = "white"
        self.bg_color = "black"
        #self.rectangle_dict = {}
        #self.oval_dict = {}
    
    # DEF FOR CHOOSING MODE AND DRAWING RECTANGLE OR OVAL
    def draw(self):
        self.unbinding()
        if self.fg_bg_mode.get() == "BG_mode":
            self.rect_button["text"] = "Квадрат"
            self.oval_button["text"] = "Спрей"     

        elif self.fg_bg_mode.get() == "FG_mode":
            self.rect_button["text"] = "Прямокутник"
            self.oval_button["text"] = "Спрей"

            # binds for rectangle mode
        if self.draw_mode.get() == "Rectangle_mode":
            self.canvas["cursor"] = "plus"
            self.oval_button["bg"] = "lightgrey"
            self.hint["text"] = "Обрано режим малювання прямокутником."
            self.canvas.bind("<ButtonPress-1>", self.on_button_press)
            self.canvas.bind("<B1-Motion>", self.on_move_press)
            self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
            # binds for dot/oval mode
        elif self.draw_mode.get()  == "Dot_mode":
            self.rect_button["bg"] = "lightgrey"
            self.canvas["cursor"] = "dot"
            self.hint["text"] = "Обрано режим малювання спреєм."
            self.canvas.bind("<B1-Motion>", self.oval_drawing)       
    # -------------------------------------

    # DISABLE BINDS
    def unbinding(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
    # -------------------------------------

    # UPLOADING IMAGE ON CANVAS AND PIL
    def upload_file(self):
        # open the image
        self.f_types = [("All types", ".*")]
        self.filename = askopenfilename(filetypes=self.f_types)
        self.im = PIL_img.open(self.filename)
        self.mask = cv.imread(self.filename)
        self.mask = np.zeros(self.mask.shape[:2], dtype = np.uint8)
        self.mask_img = ImageOps.grayscale(self.im.copy())
        

        self.rcorX,self.rcorY=self.im.size

        self.canvas.config(scrollregion=(0,0,self.rcorX,self.rcorY))
        self.tk_im = ImageTk.PhotoImage(self.im)
        
        # OBJ for drawing mask in paralel to canvas
        self.mask_draw  = ImageDraw.Draw(self.mask_img)
        # upload image on canvas
        self.canvas.create_image(0, 0,anchor="nw",image=self.tk_im)
        self.cut_button["state"] = ACTIVE
        self.hint["text"] = "Зображення придатне до редагування, оберіть інструмент."

        # -------------------------------------


   
    # DEF FOR START DRAWING RECTANGLE
    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = int(self.canvas.canvasx(event.x))
        self.start_y = int(self.canvas.canvasy(event.y))
        if self.fg_bg_mode.get() == "FG_mode":
            print("Start x = {}, y = {}".format(self.start_x, self.start_y))
            self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline=self.fg_color)
        else:
            self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline=self.bg_color)
        
    # -------------------------------------

    # DEF FOR MOVING MOUSE 
    def on_move_press(self, event):
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)


        # scrolling the canvas place when mouse is moving
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if event.x > 0.95*w:
            self.canvas.xview_scroll(1, 'units') 
        elif event.x < 0.05*w:
            self.canvas.xview_scroll(-1, 'units')
        if event.y > 0.95*h:
            self.canvas.yview_scroll(1, 'units') 
        elif event.y < 0.05*h:
            self.canvas.yview_scroll(-1, 'units')

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)    
    # -------------------------------------

    # DEF FOR DRAWING RECTANGLE IN PIL WHEN MOUSE IS RELEASED
    def on_button_release(self, event):
        self.end_x = int(self.canvas.canvasx(event.x))
        self.end_y = int(self.canvas.canvasy(event.y))

        # cv.rectangle(img, start, end, color, thickness)
        if self.fg_bg_mode.get() == "FG_mode":
            cv.rectangle(self.mask, (self.start_x, self.start_y),
                                    (self.end_x, self.end_y),
                                    self.DRAW_FG['val'],
                                    1)

            """self.mask_draw.rectangle([(self.start_x, self.start_y),
                                        (self.end_x, self.end_y)],
                                        outline = self.fg_color,
                                        fill = self.fg_color)"""
            self.rect_FG = (int(self.start_x), int(self.start_y), 
                            int(self.end_x), int(self.end_y))
            print("End x = {}, y = {}".format(self.end_x, self.end_y))
        elif self.fg_bg_mode.get() == "BG_mode": 
            cv.rectangle(self.mask, (self.start_x, self.start_y),
                                    (self.end_x, self.end_y),
                                    self.DRAW_BG['val'],
                                    -1)
            """self.mask_draw.rectangle([(self.start_x, self.start_y),
                                    (self.end_x, self.end_y)],
                                    outline = self.bg_color,
                                    fill = self.bg_color)"""

        print("End x = {}, y = {}".format(self.end_x, self.end_y))
        self.cut_hint["text"] = 'Можливо, ви вже готові утворити нове зображення, натисніть "Обрізати" або продовжуйте редагування.'
    # -------------------------------------

    # DEF FOR DRAWING OVAL ON CANVAS AND PIL
    def oval_drawing(self, event):
        self.curX = int(self.canvas.canvasx(event.x))
        self.curY = int(self.canvas.canvasy(event.y))

        if self.fg_bg_mode.get() == "FG_mode":
            self.oval = self.canvas.create_oval(self.curX, self.curY, self.curX+3, self.curY+3, fill=self.fg_color, 
                                            outline = self.fg_color)
            cv.circle(self.mask, (self.curX, self.curY), self.thickness, self.DRAW_FG['val'], -1)
            """self.mask_draw.ellipse([(self.curX, self.curY), 
                                (self.curX+3, self.curY+3)],
                                outline =self.fg_color,
                                fill=self.fg_color,
                                )"""

        else:
            self.oval = self.canvas.create_oval(self.curX, self.curY, self.curX+3, self.curY+3, fill=self.bg_color, 
                                            outline = self.bg_color)
            cv.circle(self.mask, (self.curX, self.curY), self.thickness, self.DRAW_BG['val'], -1)
            """self.mask_draw.ellipse([(self.curX, self.curY), 
                                (self.curX+3, self.curY+3)],
                                outline =self.bg_color,
                                fill=self.bg_color,
                                )"""

        self.cut_hint["text"] = 'Можливо, ви вже готові утворити нове зображення, натисніть "Обрізати" або продовжуйте редагування.'
        # ellipse drawing in PIL        
    # -------------------------------------
    
    # DEF FOR CUTTING 
    def cutting(self):
        #CutImage.img = cv2.imread(self.filename)
        #self.mask.show()
        if self.rect_FG:
            cut_proccess = CutImage(self.im, self.mask, mode=self.cut_mode, rect=self.rect_FG)
            cut_proccess.cut()
            cut_proccess.savefile() 
            self.res = PIL_img.open('grabcut_output.png')
            self.result_img = ImageTk.PhotoImage(self.res)
            self.canvas.create_image(0, 0,anchor="nw",image=self.result_img)
            self.save_button.grid(row = 4, column = 2, pady = 3)
            self.cancel_button.grid(row = 5, column = 2, pady = 3)
    # -------------------------------------
    def on_off_mode(self):
        onoff = self.on_off_mode_value.get()
        if onoff:
            self.on_off_mode_value.set(0)
            onoff = self.on_off_mode_value.get()
        else: 
            self.on_off_mode_value.set(1)
            onoff = self.on_off_mode_value.get()
        if onoff == 1:
            self.cut_mode = 1
            print ("MODE in drawing " , onoff, self.cut_mode)
            self.on_off_button.configure(image = self.on)
            self.oval_button["state"] = DISABLED 
        elif onoff == 0:
            self.cut_mode = 0
            print ("MODE in drawing " , onoff, self.cut_mode)
            self.on_off_button.configure(image = self.off)
            self.oval_button["state"] = ACTIVE


    def clean(self):
        self.canvas.delete("all")
        self.mask = cv.imread(self.filename)
        self.mask = np.zeros(self.mask.shape[:2], dtype = np.uint8)
        #self.mask_draw = None
        #self.mask_img = None
         
        #self.mask_img = ImageOps.grayscale(self.im.copy())
        #self.mask_draw  = ImageDraw.Draw(self.mask_img)
        self.canvas.create_image(0, 0,anchor="nw",image=self.tk_im)
    
    def cancel(self):
        os.remove('grabcut_output.png')
        self.save_button.grid_forget()
        self.cancel_button.grid_forget()

        self.mask = cv.imread(self.filename)
        self.mask = np.zeros(self.mask.shape[:2], dtype = np.uint8)
        #self.mask_draw = None
        #self.mask_img = None
         
        #self.mask_img = ImageOps.grayscale(self.im.copy())
        #self.mask_draw  = ImageDraw.Draw(self.mask_img)

        self.canvas.create_image(0, 0,anchor="nw",image=self.tk_im)
    
    def save(self):
        os.rename('grabcut_output.png', 'result.png')
        self.hint["text"] = 'Ваш файл збережено під назвою "result.png"'

if __name__ == "__main__":       
    root=Tk()
    root.state('zoomed')
    app = ExampleApp(root)
    app.grid()
    root.mainloop()