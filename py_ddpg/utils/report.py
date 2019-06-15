import os
import csv

class Report():
	def updateReport(self, entry):
		path = os.getcwd() + r"\report\report.csv"
		with open(path, 'a', newline='') as fileWriter:
			writer = csv.writer(fileWriter)
			writer.writerow(entry)
		fileWriter.close()
