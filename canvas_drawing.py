from PIL import Image as PIL_img, ImageTk, ImageDraw, ImageOps
from tkinter import *
from tkinter.filedialog import askopenfilename  
from cv_processing import CutImage  



class ExampleApp(Frame):
    def __init__(self,master):
        Frame.__init__(self,master=None)
        master.geometry("{0}x{1}".format(master.winfo_screenwidth(),
            master.winfo_screenheight()))

        self.x = self.y = 0
        self.canvas_width = master.winfo_screenwidth() - (master.winfo_screenwidth()*0.2)
        self.canvas_height = master.winfo_screenheight()
        self.canvas = Canvas(self, width = self.canvas_width, height = self.canvas_height, cursor="cross")

        self.vbar=Scrollbar(self,orient=VERTICAL)
        self.hbar=Scrollbar(self,orient=HORIZONTAL)
        self.vbar.config(command=self.canvas.yview)
        self.hbar.config(command=self.canvas.xview)

        self.canvas.config(yscrollcommand=self.vbar.set)
        self.canvas.config(xscrollcommand=self.hbar.set)
        self.canvas.config(xscrollincrement = 5, yscrollincrement = 5)

        self.canvas.grid(row=0,column=0, sticky = N+S+W+E)

        self.vbar.grid(row=0,column=1,sticky=N+S)
        self.hbar.grid(row=1,column=0,sticky=E+W)

        self.draw_mode=StringVar()
        self.draw_mode.set("No_mode")
        

        self.rect_button = Radiobutton(text = "Rectangle", 
                                       width = 10, 
                                       height = 2, 
                                       command = self.draw,
                                       variable=self.draw_mode,
                                       value="Rectangle_mode",
                                       indicatoron=0)
        self.rect_button.grid(row = 0, column = 2)

        self.oval_button = Radiobutton(text = "Oval", 
                                        width = 10, 
                                        height = 2, 
                                        command = self.draw,
                                        variable=self.draw_mode,
                                        value="Dot_mode",
                                        indicatoron=0)
        self.oval_button.grid(row = 1, column = 2)

        self.file_button = Button(text = "Upload file", 
                                    width = 10, 
                                    height = 2,
                                    command = self.upload_file)

        self.file_button.grid(row = 2, column = 2)
        

        self.rect = None
        self.oval = None
        
        self.start_x = None
        self.start_y = None

        self.end_x = None
        self.end_y = None
        
        self.rectangle_dict = {}
        self.oval_dict = {}
        
    
    
    def draw(self):
        self.unbinding()
        if self.draw_mode.get() == "Rectangle_mode":
            self.oval_button["bg"] = "lightgrey"
            self.canvas.bind("<ButtonPress-1>", self.on_button_press)
            self.canvas.bind("<B1-Motion>", self.on_move_press)
            self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        elif self.draw_mode.get()  == "Dot_mode":
            self.rect_button["bg"] = "lightgrey" 
            self.canvas.bind("<B1-Motion>", self.oval_drawing)  
        
    def unbinding(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

    def upload_file(self):
        self.f_types = [("All types", ".*")]
        self.filename = askopenfilename(filetypes=self.f_types)
        self.im = PIL_img.open(self.filename)
        
        self.mask_img = ImageOps.grayscale(self.im.copy())
        

        self.rcorX,self.rcorY=self.im.size

        self.canvas.config(scrollregion=(0,0,self.rcorX,self.rcorY))
        self.tk_im = ImageTk.PhotoImage(self.im)
        # OBJ for drawing mask in paralel to canvas
        self.mask_draw  = ImageDraw.Draw(self.mask_img)

        self.canvas.create_image(self.canvas_width/2, self.canvas_height/2,anchor="center",image=self.tk_im)


   

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        print("Start x = {}, y = {}".format(self.start_x, self.start_y))

        # create rectangle if not yet exist
        #if not self.rect:
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='red')


    def on_move_press(self, event):
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        #print("Process x = {}, y = {}".format(curX, curY))

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

    def on_button_release(self, event):
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)
        print("End x = {}, y = {}".format(self.end_x, self.end_y))
        self.curX = self.start_x
        self.curY = self.start_y
        # RECTANGLE DRAW IN PIL OBJ
        self.mask_draw.rectangle([(self.start_x, self.start_y),
                                  (self.end_x, self.end_y)],
                                  outline = "black",
                                  fill="black")
        """if self.rect:
            while self.curY < self.end_y and self.curX < self.end_x:

                self.rectangle_dict.setdefault(self.curX, []).append((self.curY))
                self.curY = self.curY+1
                self.curX = self.curX +1
                
            print(self.rectangle_dict.keys())
            print(self.rectangle_dict.values())"""

     

    def oval_drawing(self, event):
        self.curX = self.canvas.canvasx(event.x)
        self.curY = self.canvas.canvasy(event.y)
        self.oval = self.canvas.create_oval(self.curX, self.curY, self.curX+3, self.curY+3, fill='black', width = 2, dash=(10, 10))
        self.mask_draw.ellipse([(self.curX, self.curY), 
                                (self.curX+3, self.curY+3)],
                                outline = "black",
                                fill='black',
                                )


        """if self.oval:
            self.oval_dict.setdefault(self.curX, []).append((self.curY, self.curY+1))

        print(self.oval_dict.keys())
        print(self.oval_dict.values())"""    

if __name__ == "__main__":       
    root=Tk()
    root.state('zoomed')
    app = ExampleApp(root)
    app.grid()
    root.mainloop()
