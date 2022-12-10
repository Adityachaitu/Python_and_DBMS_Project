import os
import pickle
import tkinter as tk
from tkinter import filedialog
from tkinter import Image,PhotoImage
from pygame import mixer
from PIL import Image,ImageTk

import pymongo
import gridfs

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
mongo_collection = mongo_client["grid_file"]["fs.files"]

list_of_songs = [x["filename"] for x in mongo_collection.find()]



class Player(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master
		self.pack()
		mixer.init()

		self.playlist = list_of_songs

		self.current = 0
		self.paused = True
		self.played = False

		self.create_frames()
		self.track_widgets()
		self.control_widgets()
		self.tracklist_widgets()

	def create_frames(self):
		self.track = tk.LabelFrame(self, text='Song Track', 
					font=("times new roman",15,"bold"),
					bg="grey",fg="white",bd=5,relief=tk.GROOVE)
		self.track.config(width=410,height=300)
		self.track.grid(row=0, column=0, padx=10)

		self.tracklist = tk.LabelFrame(self, text=f'Favorites - {str(len(self.playlist))}',
							font=("times new roman",15,"bold"),
							bg="grey",fg="white",bd=5,relief=tk.GROOVE)
		self.tracklist.config(width=190,height=400)
		self.tracklist.grid(row=0, column=1, rowspan=3, pady=5)

		self.controls = tk.LabelFrame(self,
							font=("times new roman",15,"bold"),
							bg="white",fg="white",bd=2,relief=tk.GROOVE)
		self.controls.config(width=410,height=80)
		self.controls.grid(row=2, column=0, pady=5, padx=10)

	def track_widgets(self):
		self.canvas = tk.Label(self.track, image=img)
		self.canvas.configure(width=400, height=240)
		self.canvas.grid(row=0,column=0)

		self.songtrack = tk.Label(self.track, font=("times new roman",16,"bold"),
						bg="white",fg="dark blue")
		self.songtrack['text'] = 'Musicxy MP3 Player'
		self.songtrack.config(width=30, height=1)
		self.songtrack.grid(row=1,column=0,padx=10)

	def control_widgets(self):
		self.loadSongs = tk.Button(self.controls, bg='green', fg='white', font=10)
		self.loadSongs['text'] = 'Load Songs'
		self.loadSongs['command'] = self.retrieve_songs
		self.loadSongs.grid(row=0, column=0, padx=10)

		self.prev = tk.Button(self.controls, image=prev)
		self.prev['command'] = self.prev_song
		self.prev.grid(row=0, column=1)

		self.pause = tk.Button(self.controls, image=pause)
		self.pause['command'] = self.pause_song
		self.pause.grid(row=0, column=2)

		self.next = tk.Button(self.controls, image=next_)
		self.next['command'] = self.next_song
		self.next.grid(row=0, column=3)

		self.volume = tk.DoubleVar(self)
		self.slider = tk.Scale(self.controls, from_ = 0, to = 10, orient = tk.HORIZONTAL)
		self.slider['variable'] = self.volume
		self.slider.set(8)
		mixer.music.set_volume(0.8)
		self.slider['command'] = self.change_volume
		self.slider.grid(row=0, column=4, padx=5)


	def tracklist_widgets(self):
		self.scrollbar = tk.Scrollbar(self.tracklist, orient=tk.VERTICAL)
		self.scrollbar.grid(row=0,column=1, rowspan=5, sticky='ns')

		self.list = tk.Listbox(self.tracklist, selectmode=tk.SINGLE,
					 yscrollcommand=self.scrollbar.set, selectbackground='sky blue')
		self.enumerate_songs()
		self.list.config(height=22)
		self.list.bind('<Double-1>', self.play_song) 

		self.scrollbar.config(command=self.list.yview)
		self.list.grid(row=0, column=0, rowspan=5)

	def retrieve_songs(self):
		self.songlist = []
		directory = filedialog.askdirectory()
		for root_, dirs, files in os.walk(directory):
				for file in files:
					if os.path.splitext(file)[1] == '.mp3':
						path = (root_ + '/' + file).replace('\\','/')
						self.songlist.append(path)

		with open('songs.pickle', 'wb') as f:
			pickle.dump(self.songlist, f)
		self.playlist = self.songlist
		self.tracklist['text'] = f'PlayList - {str(len(self.playlist))}'
		self.list.delete(0, tk.END)
		self.enumerate_songs()

	def enumerate_songs(self):
		for index, song in enumerate(self.playlist):
			self.list.insert(index, os.path.basename(song))


	def play_song(self, event=None):
		if event is not None:
			self.current = self.list.curselection()[0]
			for i in range(len(self.playlist)):
				self.list.itemconfigure(i, bg="white")

		songname = self.playlist[self.current]

		db = mongo_client.grid_file
		fs = gridfs.GridFS(db)

		mixer.music.unload()

		data = db.fs.files.find_one({'filename' : songname})
		my_id = data['_id']
		outputdata = fs.get(my_id).read()
		download_location = f"E:\\temp"
		output = open(download_location, "wb")
		output.write(outputdata)
		output.close()


		download_music_location = f"E:\\temp"
		mixer.music.load(download_music_location)
		self.songtrack['anchor'] = 'w'
		self.songtrack['text'] = os.path.basename(self.playlist[self.current])

		self.pause['image'] = play
		self.paused = False
		self.played = True
		self.list.activate(self.current) 
		self.list.itemconfigure(self.current, bg='sky blue')

		mixer.music.play()

	def pause_song(self):
		if not self.paused:
			self.paused = True
			mixer.music.pause()
			self.pause['image'] = pause
		else:
			if self.played == False:
				self.play_song()
			self.paused = False
			mixer.music.unpause()
			self.pause['image'] = play

	def prev_song(self):
		if self.current > 0:
			self.current -= 1
		else:
			self.current = 0
		self.list.itemconfigure(self.current + 1, bg='white')
		self.play_song()

	def next_song(self):
		if self.current < len(self.playlist) - 1:
			self.current += 1
		else:
			self.current = 0
		self.list.itemconfigure(self.current - 1, bg='white')
		self.play_song()

	def change_volume(self, event=None):
		self.v = self.volume.get()
		mixer.music.set_volume(self.v / 10)

# ----------------------------- Main -------------------------------------------

root = tk.Tk()
root.geometry('600x400')
root.wm_title('High-Vibe')

img = ImageTk.PhotoImage(file='images/music.gif')
next_ = ImageTk.PhotoImage(file = 'images/next.gif')
prev = ImageTk.PhotoImage(file='images/previous.gif')
play = ImageTk.PhotoImage(file='images/play.gif')
pause = ImageTk.PhotoImage(file='images/pause.gif')

app = Player(master=root)
app.mainloop()