import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QIcon, QPixmap
import psycopg2

qtCreatorFile = "MyUI.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class myApp(QMainWindow):
    def __init__(self):
        super(myApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadStateList()
        self.ui.stateList.currentTextChanged.connect(self.stateChanged)
        self.ui.cityList.itemSelectionChanged.connect(self.cityChanged)
        self.ui.zipCodeList.itemSelectionChanged.connect(self.zipCodeChanged)
        self.ui.bname.textChanged.connect(self.getBusinessNames)
        self.ui.businesses.itemSelectionChanged.connect(self.displayBusinessCity)

    def executeQuery(self, sql_str):
        try:
            # conn = psycopg2.connect("dbname='milestone1db' user='postgres' host='localhost' password='112358'")
            conn = psycopg2.connect(dbname='yelpdb', user='postgres', password='112358', host='localhost', port='5432')
        except Exception as e:
            print('Unable to connect to database:', str(e))
        cur = conn.cursor()
        cur.execute(sql_str)
        conn.commit()
        result = cur.fetchall()
        conn.close()
        return result
    
    def loadStateList(self):
        sql_str = "SELECT distinct state FROM business ORDER BY state;"
        try:
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.stateList.addItem(row[0])
        except Exception as e:
            print('Query failed:', str(e))
        # clear default selection
        self.ui.stateList.setCurrentIndex(-1)
        self.ui.stateList.clearEditText()

    def stateChanged(self):
        self.ui.cityList.clear()
        self.ui.zipCodeList.clear()
        self.ui.categoryList.clear()
        state = self.ui.stateList.currentText()
        if (self.ui.stateList.currentIndex() >= 0):
            sql_str = "SELECT distinct city FROM business WHERE state ='" + state + "' ORDER BY city;"
            try:
                results = self.executeQuery(sql_str)
                for row in results:
                    self.ui.cityList.addItem(row[0]) 
            except Exception as e:
                print("Query failed:", str(e))

            for i in reversed(range(self.ui.businessTable.rowCount())):
                self.ui.businessTable.removeRow(i)
            sql_str = "SELECT name, city, state FROM business WHERE state ='" + state + "' ORDER BY name;"
            try:
                results = self.executeQuery(sql_str)
                self.updateBusinessTable(results)
            except Exception as e:
                print("Query failed:", str(e))

    def cityChanged(self):
        self.ui.zipCodeList.clear()
        self.ui.categoryList.clear()
        if (self.ui.stateList.currentIndex() >= 0) and (len(self.ui.cityList.selectedItems()) > 0):
            city = self.ui.cityList.selectedItems()[0].text()

            # update zipCodeList
            sql_str = "SELECT distinct zipcode FROM business WHERE city ='" + city + "';"
            try:
                results = self.executeQuery(sql_str)
                for row in results:
                    self.ui.zipCodeList.addItem(row[0]) 
            except Exception as e:
                print("Query failed:", str(e))
            
            state = self.ui.stateList.currentText()
            city = self.ui.cityList.selectedItems()[0].text()
            sql_str = "SELECT name, city, state FROM business WHERE state = '" + state + "' AND city='" + city + "' ORDER BY name;"
            try:
                results = self.executeQuery(sql_str)
                self.updateBusinessTable(results)
            except Exception as e:
                print("Query failed:", str(e))

    def zipCodeChanged(self):
        self.ui.categoryList.clear()
        if (self.ui.stateList.currentIndex() >= 0) and (len(self.ui.zipCodeList.selectedItems()) > 0):
            state = self.ui.stateList.currentText()
            city = self.ui.cityList.selectedItems()[0].text()
            zipcode = self.ui.zipCodeList.selectedItems()[0].text()
            sql_str = "SELECT name, city, state FROM business WHERE state = '" + state + "' AND city='" + city + "'" + "AND zipcode='" + zipcode + "' ORDER BY name;"
            try:
                results = self.executeQuery(sql_str)
                self.updateBusinessTable(results)
            except Exception as e:
                print("Query failed:", str(e))

            # update categoryList
            sql_str = "SELECT DISTINCT category_name FROM business JOIN categories ON business.business_id = categories.business_id WHERE zipcode = '" + zipcode + "';"
            try:
                results = self.executeQuery(sql_str)
                for row in results:
                    self.ui.categoryList.addItem(row[0])
            except Exception as e:
                print("Query failed:", str(e))

    def getBusinessNames(self):
        self.ui.businesses.clear()
        business_name = self.ui.bname.text()
        sql_str = "SELECT name FROM business WHERE name LIKE '%" + business_name + "%' ORDER BY name;"
        try:
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.businesses.addItem(row[0])
        except Exception as e:
            print("Query failed:", str(e))

    def displayBusinessCity(self):
        business_name = self.ui.businesses.selectedItems()[0].text()
        sql_str = "SELECT city FROM business WHERE name = '" + business_name + "';"
        try:
            results = self.executeQuery(sql_str)
            self.ui.bcity.setText(results[0][0])
        except Exception as e:
            print("Query failed:", str(e))

    def updateBusinessTable(self, results):
        style = "::section {""background-color: #f3f3f3; }"
        self.ui.businessTable.horizontalHeader().setStyleSheet(style)
        self.ui.businessTable.setColumnCount(len(results[0])) # amount of elements in tuple
        self.ui.businessTable.setRowCount(len(results))
        self.ui.businessTable.setHorizontalHeaderLabels(['Business Name', 'City', 'State'])
        self.ui.businessTable.resizeColumnsToContents()
        self.ui.businessTable.setColumnWidth(0, 300)
        self.ui.businessTable.setColumnWidth(1, 100)
        self.ui.businessTable.setColumnWidth(2, 50)
        currentRowCount = 0
        for row in results:
            for colCount in range (0, len(results[0])):
                self.ui.businessTable.setItem(currentRowCount, colCount, QTableWidgetItem(row[colCount]))
            currentRowCount += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myApp()
    window.show()
    sys.exit(app.exec_())
