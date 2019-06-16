import os
import csv

class Report():
	def updateReport(self, file_name, entry):
		path = os.getcwd() + file_name
		with open(path, 'a', newline='') as fileWriter:
			writer = csv.writer(fileWriter)
			writer.writerow(entry)
		fileWriter.close()
