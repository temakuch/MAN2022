from PIL import Image as pil_img, ImageTk
from tkinter import *
    



class ExampleApp(Frame):
    def __init__(self,master):
        Frame.__init__(self,master=None)
        master.geometry("{0}x{1}".format(master.winfo_screenwidth(),
            master.winfo_screenheight()))

        self.x = self.y = 0
        self.canvas = Canvas(self,  cursor="cross")

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
        


        #self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        #self.canvas.bind("<B1-Motion>", self.on_move_press)
        #self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
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

        self.rect = None
        self.oval = None
        
        self.start_x = None
        self.start_y = None

        self.end_x = None
        self.end_y = None

        self.im = pil_img.open("a.jpg")
        self.rcorX,self.rcorY=self.im.size

        self.canvas.config(scrollregion=(0,0,self.rcorX,self.rcorY))
        self.tk_im = ImageTk.PhotoImage(self.im)
        self.canvas.create_image(0, 0,anchor="nw",image=self.tk_im)   
    
    def draw(self):
        print(self.draw_mode.get())
        self.unbinding()
        if self.draw_mode.get() == "Rectangle_mode":
            self.rect_button["bg"] = "green"
            self.canvas.bind("<ButtonPress-1>", self.on_button_press)
            self.canvas.bind("<B1-Motion>", self.on_move_press)
            self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        elif self.draw_mode.get()  == "Dot_mode":
            self.oval_button["bg"] = "green" 
            self.canvas.bind("<B1-Motion>", self.oval_drawing)  
        
    def unbinding(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

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
        #pass    

    def oval_drawing(self, event):
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        self.oval = self.canvas.create_oval(curX, curY, curX+3, curY+3, fill='black', width = 2, dash=(10, 10))


if __name__ == "__main__":       
    root=Tk()
    root.state('zoomed')
    app = ExampleApp(root)
    app.grid()
    root.mainloop()
