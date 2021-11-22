from PIL import Image as PIL_img, ImageTk, ImageDraw, ImageOps
from tkinter import *
from tkinter.filedialog import askopenfilename  
from cv_processing import CutImage  
import cv2


class ExampleApp(Frame):
    def __init__(self,master):
        Frame.__init__(self,master=None)
        master.geometry("{0}x{1}".format(master.winfo_screenwidth(),
                                            master.winfo_screenheight()))
        # CREATING CANVAS
        self.x = self.y = 0
        self.canvas_width = master.winfo_screenwidth() - (master.winfo_screenwidth()*0.2)
        self.canvas_height = master.winfo_screenheight()
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
        # -------------------------------------

        # SETING MODE FOR draw_mode
        self.draw_mode=StringVar()
        self.draw_mode.set("No_mode")

        self.fg_bg_mode = StringVar()
        self.fg_bg_mode.set("FG_mode")
        # -------------------------------------
        
        # CREATING AND SETTING RADIOBUTTONS/BUTTONS
        self.rect_button = Radiobutton(text = "FG rectangle", 
                                       width = 10, 
                                       height = 2, 
                                       command = self.draw,
                                       variable=self.draw_mode,
                                       value="Rectangle_mode",
                                       indicatoron=0,)
        self.rect_button.grid(row = 0, column = 2)

        self.oval_button = Radiobutton(text = "FG oval", 
                                        width = 10, 
                                        height = 2, 
                                        command = self.draw,
                                        variable=self.draw_mode,
                                        value="Dot_mode",
                                        indicatoron=0)
        self.oval_button.grid(row = 1, column = 2)

        self.fg_mode_button = Radiobutton(text = "Foreground",
                                            width = 10,
                                            height = 2,
                                            command = self.draw,
                                            variable=self.fg_bg_mode,
                                            value = "FG_mode",
                                            indicatoron = 1)
        self.fg_mode_button.grid(row = 0, column = 3)

        self.bg_mode_button = Radiobutton(text = "Background",
                                            width = 10,
                                            height = 2,
                                            command = self.draw,
                                            variable=self.fg_bg_mode,
                                            value = "BG_mode",
                                            indicatoron = 1)
        self.bg_mode_button.grid(row = 1, column = 3)

        self.file_button = Button(text = "Upload file", 
                                    width = 10, 
                                    height = 2,
                                    command = self.upload_file)

        self.file_button.grid(row = 2, column = 2)
        
        self.cut_button = Button(text = "Cut",
                                    width = 10,
                                    height = 2,
                                    state = DISABLED,
                                    command = self.cutting)
        self.cut_button.grid(row = 3, column = 2)
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
        self.color = None

        #self.rectangle_dict = {}
        #self.oval_dict = {}
    
    # DEF FOR CHOOSING MODE AND DRAWING RECTANGLE OR OVAL
    def draw(self):
        self.unbinding()
        if self.fg_bg_mode.get() == "BG_mode":
            self.rect_button["text"] = "BG rectangle"
            self.oval_button["text"] = "BG oval"    
            
        elif self.fg_bg_mode.get() == "FG_mode":
            self.rect_button["text"] = "FG rectangle"
            self.oval_button["text"] = "FG oval"

            # binds for rectangle mode
        if self.draw_mode.get() == "Rectangle_mode":
            self.canvas["cursor"] = "plus"
            self.oval_button["bg"] = "lightgrey"
            self.canvas.bind("<ButtonPress-1>", self.on_button_press)
            self.canvas.bind("<B1-Motion>", self.on_move_press)
            self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
            # binds for dot/oval mode
        elif self.draw_mode.get()  == "Dot_mode":
            self.rect_button["bg"] = "lightgrey"
            self.canvas["cursor"] = "dot"
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
        
        self.mask_img = ImageOps.grayscale(self.im.copy())
        

        self.rcorX,self.rcorY=self.im.size

        self.canvas.config(scrollregion=(0,0,self.rcorX,self.rcorY))
        self.tk_im = ImageTk.PhotoImage(self.im)
        
        # OBJ for drawing mask in paralel to canvas
        self.mask_draw  = ImageDraw.Draw(self.mask_img)
        # upload image on canvas
        self.canvas.create_image(0, 0,anchor="nw",image=self.tk_im)
        self.cut_button["state"] = ACTIVE
        # -------------------------------------


   
    # DEF FOR START DRAWING RECTANGLE
    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.color = "black"
        if self.fg_bg_mode.get() == "FG_mode":
            print("Start x = {}, y = {}".format(self.start_x, self.start_y))
            self.color = "white"
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline=self.color)
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
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)
        self.color = "black"
        if self.fg_bg_mode.get() == "FG_mode":
            self.mask_draw.rectangle([(self.start_x, self.start_y),
                                        (self.end_x, self.end_y)],
                                        outline = "white",
                                        fill="white")
            self.rect_FG = (int(self.start_x), int(self.start_y), 
                            int(self.end_x), int(self.end_y))
            print("End x = {}, y = {}".format(self.end_x, self.end_y))
            self.color = "white"
        else:
            self.color = "black" 
        self.mask_draw.rectangle([(self.start_x, self.start_y),
                                    (self.end_x, self.end_y)],
                                    outline = self.color,
                                    fill = self.color)
        print("End x = {}, y = {}".format(self.end_x, self.end_y))
    # -------------------------------------

    # DEF FOR DRAWING OVAL ON CANVAS AND PIL
    def oval_drawing(self, event):
        self.curX = self.canvas.canvasx(event.x)
        self.curY = self.canvas.canvasy(event.y)
        self.color = "black"
        if self.fg_bg_mode.get() == "FG_mode":
            self.color = "white"

        else:
            self.color = "black"
        self.oval = self.canvas.create_oval(self.curX, self.curY, self.curX+3, self.curY+3, fill=self.color, 
                                            outline = self.color)
        # ellipse drawing in PIL        
        self.mask_draw.ellipse([(self.curX, self.curY), 
                                (self.curX+3, self.curY+3)],
                                outline =self.color,
                                fill=self.color,
                                )
    # -------------------------------------
    
    # DEF FOR CUTTING 
    def cutting(self):
        #CutImage.img = cv2.imread(self.filename)
        self.mask_img.show()
        if self.rect_FG:
            cut_proccess = CutImage(self.im, self.mask_img, mode=0, rect=self.rect_FG)

    # -------------------------------------

if __name__ == "__main__":       
    root=Tk()
    root.state('zoomed')
    app = ExampleApp(root)
    app.grid()
    root.mainloop()