import tkinter as tk

# dimensioni
cell_h = 40
cell_w = 80
start_hour = 8
end_hour = 17

giorni = ["LUN", "MAR", "MER", "GIO", "VEN", "SAB"]

root = tk.Tk()
root.title("Orario Settimanale")

canvas = tk.Canvas(root, width=600, height=450)
canvas.pack()

# titolo
canvas.create_text(300,20,text="ORARIO SETTIMANALE",font=("Arial",16,"bold"))

top_offset = 40
left_offset = 60

# intestazioni giorni
for i,g in enumerate(giorni):
    x1 = left_offset + i*cell_w
    x2 = x1 + cell_w
    canvas.create_rectangle(x1,top_offset,x2,top_offset+30,fill="#9fd3a6")
    canvas.create_text((x1+x2)/2,top_offset+15,text=g)

# orari
for h in range(start_hour,end_hour+1):

    y = top_offset+30+(h-start_hour)*cell_h
    canvas.create_text(30,y+cell_h/2,text=f"{h:02d}:00")

    for d in range(len(giorni)):
        x1 = left_offset + d*cell_w
        x2 = x1 + cell_w
        y2 = y + cell_h

        canvas.create_rectangle(x1,y,x2,y2)

# funzione per aggiungere evento
def aggiungi_evento(giorno,start,end,testo):

    x1 = left_offset + giorno*cell_w + 5
    x2 = x1 + cell_w - 10

    y1 = top_offset+30 + (start-start_hour)*cell_h
    y2 = top_offset+30 + (end-start_hour)*cell_h

    canvas.create_rectangle(x1,y1,x2,y2,fill="#6bc16b")
    canvas.create_text((x1+x2)/2,(y1+y2)/2,text=testo,font=("Arial",10))

# esempio come nell'immagine
aggiungi_evento(0,8,10.5,"8:00-10:30")

root.mainloop()