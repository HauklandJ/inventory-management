from tkinter import *
from tkinter import ttk
import sqlite3

class Inventory:
	#Create database unless it already exists
	db_name = 'goodybagsdatabas.db'
	conn = sqlite3.connect('goodybagsdatabas.db')
	c = conn.cursor()
	#Add tables to the database if they don't already exist
	c.execute("""CREATE TABLE IF NOT EXISTS varer(
		nullrow text,
		navn text,
		antall integer,
		størrelse text,
		pris integer,
		status text,
		utløpsdato text,
		kommentar text
		)""")
	def __init__(self, wind):
		self.wind = wind
		self.wind.title ('Goodybags Varelager')
		#GUI for adding a new item to the inventory management system
		frame = LabelFrame (self.wind, text = 'Legg til ny vare')
		frame.grid (row = 0, column = 1)

		Label (frame, text = 'Varenavn: ').grid (row = 1, column = 1)
		self.name = Entry (frame)
		self.name.grid (row =1, column =2)

		Label (frame, text = 'Antall: ').grid (row = 2, column = 1)
		self.amount = Entry (frame)
		self.amount.grid (row = 2, column = 2)

		Label (frame, text = 'Størrelse: ').grid (row = 3, column = 1)
		self.size = Entry (frame)
		self.size.grid (row = 3, column = 2)

		Label (frame, text = 'Pris: ').grid (row = 4, column = 1)
		self.price = Entry (frame)
		self.price.grid (row = 4, column = 2)

		Label (frame, text = 'Status: ').grid (row = 5, column = 1)
		self.status = Entry (frame)
		self.status.grid (row = 5, column = 2)

		Label (frame, text = 'Best før: ').grid (row = 6, column = 1)
		self.best = Entry (frame)
		self.best.grid (row = 6, column = 2)

		Label (frame, text = 'kommentar: ').grid (row = 7, column = 1)
		self.comment = Entry (frame)
		self.comment.grid (row = 7, column = 2)
		#Finally adding button to save the new item
		ttk.Button(frame, text = 'Legg til vare', command = self.adding).grid (row = 8, column = 2)
		#All in-app GUI messages
		self.message = Label (text = '', fg = 'red' )
		self.message.grid (row = 8, column = 0)
		#Initialize the Treeview
		self.tree = ttk.Treeview (height = 15, columns = ('amount', 'size','price','status','best','comment'))
		self.tree.grid (row = 9, column = 0, columnspan = 7)
		self.tree.heading ('#0', text = 'Varenavn', anchor = W)
		self.tree.heading ('amount', text = 'Antall', anchor = W)
		self.tree.heading ('size', text = 'Størrelse', anchor = W)
		self.tree.heading ('price', text = 'Pris', anchor = W)
		self.tree.heading ('status', text = 'Status', anchor = W)
		self.tree.heading ('best', text = 'Best før', anchor = W)
		self.tree.heading ('comment', text = 'Kommentar', anchor = W)
		#Add all buttons to the GUI, commands are functions below
		ttk.Button (text = 'Slett rad', command = self.deleting).grid (row = 10, column = 0)
		ttk.Button (text = 'Rediger rad', command = self.editing).grid (row = 10, column = 1)
		ttk.Button (text = 'Søk', command = self.searching).grid (row = 10, column = 2)
		ttk.Button (text = 'Oppdater', command = self.viewing_records).grid (row = 10, column = 3)

		self.viewing_records()
	#Funtion sorting the tree by descending expiration date, now obsolete - done by viewing_records below
	def sortby(tree, col, descending):
		data = [(tree.set(child, col), child) for child in tree.get_children('')]
		data.sort(reverse=descending)
		for i, item in enumerate(data):
			tree.move(item[1], '', i)
		tree.heading(col, command=lambda col=col: sortby(tree, col, int(not descending)))
	#Function building queries to send to the sqlite3 database
	def run_query (self, query, parameters = []):
		with sqlite3.connect (self.db_name) as conn:
			cursor = conn.cursor()
			query_result = cursor.execute (query, parameters)
			conn.commit()
		return query_result
	#Function building queries for the search-implementation as no parameters are used in that instance
	def run_search_query(self,query):
		with sqlite3.connect (self.db_name) as conn:
			cursor = conn.cursor()
			query_result = cursor.execute (query)
			conn.commit()
		return query_result
	#Function to update the GUI with the user-made changes, displaying the treeviews children, all data in the db
	def viewing_records (self):
		records = self.tree.get_children()
		for element in records:
			self.tree.delete (element)
		query = 'SELECT * FROM varer ORDER BY utløpsdato DESC'
		db_rows = self.run_query (query)
		for row in db_rows:
			self.tree.insert ('', 0, text = row[1], values = (row[2], row[3],row[4],row[5],row[6],row[7]))

		self.message['text'] = 'Listen har blitt oppdatert.'

	#Function making sure that the userinput for name, amount, size, price, status and best are non-empty, thus making them required
	def validation (self):
		return len (self.name.get()) != 0 and len(self.amount.get()) != 0 and len(self.size.get())!= 0 and len(self.price.get())!= 0 and len(self.status.get()) != 0 and len(self.best.get())!= 0
	#Functionality for the Legg til ny vare - button
	def adding (self):
		if self.validation():
			query = 'INSERT INTO varer VALUES (NULL,?,?,?,?,?,?,?)'
			parameters = [self.name.get(), self.amount.get(), self.size.get(), self.price.get(), self.status.get(), self.best.get(), self.comment.get()]
			self.run_query (query, parameters)
			self.message ['text'] = 'Vare {} lagt til'.format (self.name.get())
			self.name.delete (0, END)
			self.amount.delete (0, END)
			self.size.delete (0, END)
			self.price.delete (0, END)
			self.status.delete (0, END)
			self.best.delete (0, END)
			self.comment.delete (0, END)
		else:
			self.message['text'] = 'Et eller flere felt er ikke fylt ut.'
		self.viewing_records()
	#Funtionality for the Slett vare - button
	def deleting (self):
		self.message ['text'] = ''
		try:
			self.tree.item (self.tree.selection())['values'][0]
		except IndexError as e:
			self.message['text'] = 'Velg en rad som skal slettes'
			return

		self.message['text'] = ''
		name = self.tree.item (self.tree.selection())['text']
		best = self.tree.item( self.tree.selection())['values'][4]
		
		query = 'DELETE FROM varer WHERE navn = ?  AND utløpsdato = ?'
		self.run_query (query, (name, best))
		self.message['text'] = 'Vare {} slettet'.format(name)
		self.viewing_records ()
	#Funtionality for the Rediger Vare - button
	def editing (self):
		self.message['text'] = ''
		try:
			self.tree.item(self.tree.selection())['values'][0]
		except IndexError as e:
			self.message['text'] = 'Vennligst velg rad for redigering.'
			return

		name = self.tree.item (self.tree.selection())['text']
		old_amount = self.tree.item ( self.tree.selection())['values'][0]
		old_size = self.tree.item( self.tree.selection())['values'][1]
		old_price = self.tree.item( self.tree.selection())['values'][2]
		old_status = self.tree.item( self.tree.selection())['values'][3]
		old_best = self.tree.item( self.tree.selection())['values'][4]
		old_comment = self.tree.item( self.tree.selection())['values'][5]

		self.edit_wind = Toplevel()
		self.edit_wind.title = ('Redigering')

		Label (self.edit_wind, text = 'Tidligere navn:').grid(row = 0, column = 1)
		Entry (self.edit_wind, textvariable = StringVar(self.edit_wind, value = name), state = 'readonly').grid(row = 0, column = 2)
		Label (self.edit_wind, text = 'Nytt navn:').grid (row = 1, column = 1)
		new_name = Entry(self.edit_wind)
		new_name.grid( row = 1, column = 2)

		Label (self.edit_wind, text = 'Tidligere antall:').grid(row = 2, column = 1)
		Entry (self.edit_wind, textvariable = StringVar(self.edit_wind, value = old_amount), state = 'readonly').grid(row = 2, column = 2)
		Label (self.edit_wind, text = 'Nytt antall:').grid (row = 3, column = 1)
		new_amount = Entry(self.edit_wind)
		new_amount.grid( row = 3, column = 2)

		Label (self.edit_wind, text = 'Tidligere størrelse:').grid(row = 4, column = 1)
		Entry (self.edit_wind, textvariable = StringVar(self.edit_wind, value = old_size), state = 'readonly').grid(row = 4, column = 2)
		Label (self.edit_wind, text = 'Ny størrelse:').grid (row = 5, column = 1)
		new_size = Entry(self.edit_wind)
		new_size.grid( row = 5, column = 2)

		Label (self.edit_wind, text = 'Tidligere pris:').grid(row = 6, column = 1)
		Entry (self.edit_wind, textvariable = StringVar(self.edit_wind, value = old_price), state = 'readonly').grid(row = 6, column = 2)
		Label (self.edit_wind, text = 'Ny pris:').grid (row = 7, column = 1)
		new_price = Entry(self.edit_wind)
		new_price.grid( row = 7, column = 2)

		Label (self.edit_wind, text = 'Tidligere status:').grid(row = 8, column = 1)
		Entry (self.edit_wind, textvariable = StringVar(self.edit_wind, value = old_status), state = 'readonly').grid(row = 8, column = 2)
		Label (self.edit_wind, text = 'Ny status:').grid (row = 9, column = 1)
		new_status = Entry(self.edit_wind)
		new_status.grid( row = 9, column = 2)

		Label (self.edit_wind, text = 'Tidligere utløpsdato:').grid(row = 10, column = 1)
		Entry (self.edit_wind, textvariable = StringVar(self.edit_wind, value = old_best), state = 'readonly').grid(row = 10, column = 2)
		Label (self.edit_wind, text = 'Ny utløpsdato:').grid (row = 11, column = 1)
		new_best = Entry(self.edit_wind)
		new_best.grid( row = 11, column = 2)

		Label (self.edit_wind, text = 'Tidligere kommentar:').grid(row = 12, column = 1)
		Entry (self.edit_wind, textvariable = StringVar(self.edit_wind, value = old_best), state = 'readonly').grid(row = 12, column = 2)
		Label (self.edit_wind, text = 'Ny kommentar:').grid (row = 13, column = 1)
		new_comment = Entry(self.edit_wind)
		new_comment.grid( row = 13, column = 2)

		Button (self.edit_wind, text = 'Lagre endringer', 
			command = lambda: self.edit_records(new_name.get(),name,new_amount.get(),
				old_amount,new_size.get(),old_size,new_price.get(),old_price,new_status.get(),old_status,
				new_best.get(),old_best,new_comment.get(),old_comment)).grid (row = 15, column = 2, sticky = W)

		self.edit_wind.mainloop()
	#More functionality for editing an item 
	def edit_records (self, new_name, name, new_amount, amount,new_size,size,new_price,price,new_status,status, new_best, best, new_comment, comment):
		query = 'UPDATE varer SET navn = ?, antall = ?, størrelse = ?, pris = ?, status = ?, utløpsdato = ?, kommentar = ? WHERE navn = ? AND antall = ? AND størrelse = ? AND pris = ? AND status = ? AND utløpsdato = ? AND kommentar = ?'
		if new_name == '':
			new_name = name
		if new_amount== '':
			new_amount = amount
		if new_size == '':
			new_size = size
		if new_price == '':
			new_price = price
		if new_status == '':
			new_status = status
		if new_best == '':
			new_best = best
		if new_comment == '':
			new_comment = comment
		parameters = [new_name, new_amount, new_size, new_price, new_status, new_best, new_comment, name, amount, size, price, status, best, comment]
		
		
		self.run_query(query,parameters)
		self.edit_wind.destroy()
		self.message['text'] = '{} har blitt endret.'.format(name)
		self.viewing_records()
	#search functionality
	def searching(self):
		#open search window
		self.edit_wind = Toplevel()
		self.edit_wind.title = ('Søk')
		Label (self.edit_wind, text = 'Her kan du søke etter varer:').grid (row = 1, column = 1)
		

		search_name = Entry(self.edit_wind)
		search_name.grid( row = 1, column = 2)
		#add buttons to the window
		Button (self.edit_wind, text = 'Utfør søk', command = lambda: self.search_records(search_name.get())).grid (row = 6, column = 2, sticky = W)
		Button (self.edit_wind, text = 'Lukk', command = lambda: self.destroy_and_view()).grid (row = 6, column = 3, sticky = W)
		
	#Lukk - button functionality
	def destroy_and_view(self):
		self.edit_wind.destroy()
		self.viewing_records()
	#Utfør søk - button funtionality
	def search_records(self, name):
		rows = 0
		records = self.tree.get_children()
		for element in records:
			self.tree.delete (element)
		
		query = "SELECT * FROM varer WHERE navn LIKE \'%"+name+"%\'"
		db_rows = self.run_search_query(query)
		for row in db_rows:
			rows +=1
			self.tree.insert ('', 0, text = row[1], values = (row[2], row[3],row[4],row[5],row[6],row[7]))
		self.message['text'] = '{} rader funnet med {} i navnet.'.format(rows, name)
		
		


if __name__ == '__main__':
	wind = Tk()
	application = Inventory (wind)
	wind.mainloop()
