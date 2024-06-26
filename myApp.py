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
        self.ui.categoryList.itemSelectionChanged.connect(self.categoryChanged)
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
            sql_str = "SELECT b.name, b.address, b.city, b.stars, b.reviewcount, b.reviewrating, COALESCE(SUM(c.count), 0) " + \
            "FROM business AS b JOIN checkins c ON b.business_id = c.business_id " + \
            "WHERE b.state = '" + state + "' " + \
            "GROUP BY b.business_id, b.name, b.address, b.city, b.stars, b.reviewcount, b.reviewrating;"
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
            sql_str = "SELECT b.name, b.address, b.city, b.stars, b.reviewcount, b.reviewrating, COALESCE(SUM(c.count), 0) " + \
            "FROM business AS b JOIN checkins c ON b.business_id = c.business_id " + \
            "WHERE b.state = '" + state + "' AND b.city = '" + city + "' " + \
            "GROUP BY b.business_id, b.name, b.address, b.city, b.stars, b.reviewcount, b.reviewrating;"
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
            sql_str = "SELECT b.name, b.address, b.city, b.stars, b.reviewcount, b.reviewrating, COALESCE(SUM(c.count), 0) " + \
            "FROM business AS b JOIN checkins c ON b.business_id = c.business_id " + \
            "WHERE b.state = '" + state + "' AND b.city = '" + city + "' AND b.zipcode = '" + zipcode + "' " + \
            "GROUP BY b.business_id, b.name, b.address, b.city, b.stars, b.reviewcount, b.reviewrating;"
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

            # update zip code statistics
            self.updateZipCodeStatistics()

            # update popular and successful business tables
            self.updatePopularTable()
            self.updateSuccessfulTable()

    def updateZipCodeStatistics(self):
        # update business count text box
        self.ui.zipCodeBusinessCount.clear()
        zipcode = self.ui.zipCodeList.selectedItems()[0].text()
        sql_str = "SELECT COUNT(*) FROM business WHERE zipcode = '" + zipcode + "';"
        results = self.executeQuery(sql_str)
        print(results)
        self.ui.zipCodeBusinessCount.addItem(str(results[0][0]))

        # update population text box
        self.ui.zipCodePopulationCount.clear()
        zipcode = self.ui.zipCodeList.selectedItems()[0].text()
        sql_str = "SELECT population FROM zipcodedata WHERE zipcode = '" + zipcode + "';"
        results = self.executeQuery(sql_str)
        print(results)
        self.ui.zipCodePopulationCount.addItem(str(results[0][0]))

        # update avg income text box
        self.ui.zipCodeAverageIncome.clear()
        zipcode = self.ui.zipCodeList.selectedItems()[0].text()
        sql_str = "SELECT meanIncome FROM zipcodedata WHERE zipcode = '" + zipcode + "';"
        results = self.executeQuery(sql_str)
        print(results)
        self.ui.zipCodeAverageIncome.addItem(str(results[0][0]))

        # update top categories table
        sql_str = "SELECT c.category_name, COUNT(*) AS category_count " + \
        "FROM categories c JOIN business b ON c.business_id = b.business_id " + \
        "WHERE b.zipcode = '" + zipcode + "' GROUP BY c.category_name ORDER BY category_count DESC;"
        try:
            results = self.executeQuery(sql_str)
            if len(results) == 0:
                self.ui.zipCodeTopCategories.setColumnCount(1)
                self.ui.zipCodeTopCategories.setRowCount(1)
                self.ui.zipCodeTopCategories.setItem(0, 0, QTableWidgetItem("No categories found!"))
                return
            style = "::section {""background-color: #f3f3f3; }"
            self.ui.zipCodeTopCategories.horizontalHeader().setStyleSheet(style)
            self.ui.zipCodeTopCategories.setColumnCount(len(results[0])) # amount of elements in tuple
            self.ui.zipCodeTopCategories.setRowCount(len(results))
            self.ui.zipCodeTopCategories.setHorizontalHeaderLabels(['Category', '#'])
            #self.ui.zipCodeTopCategories.horizontalHeader().setMinimumHeight(20)
            self.ui.zipCodeTopCategories.setColumnWidth(0, 250)
            self.ui.zipCodeTopCategories.setColumnWidth(1, 20)
            currentRowCount = 0
            for row in results:
                for colCount in range (0, len(results[0])):
                    print(row[colCount])
                    self.ui.zipCodeTopCategories.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                currentRowCount += 1
        except Exception as e:
            print("Query failed:", str(e))
        
    def updatePopularTable(self):
        # get businesses where avg checkin count is higher than avg in the zipcode
        zipcode = self.ui.zipCodeList.selectedItems()[0].text()
        sql_str = "SELECT b.name FROM business b JOIN checkins c ON b.business_id = c.business_id " + \
        "WHERE b.zipcode = '" + zipcode + "' GROUP BY b.business_id, b.name " + \
        "HAVING AVG(c.count) > (SELECT AVG(c.count) FROM business b JOIN checkins c ON b.business_id = c.business_id WHERE b.zipcode = '" + zipcode + "');"
        try:
            results = self.executeQuery(sql_str)

            # update popular table
            if len(results) == 0:
                self.ui.popularTable.setColumnCount(1)
                self.ui.popularTable.setRowCount(1)
                self.ui.popularTable.setItem(0, 0, QTableWidgetItem("No popular businesses found!"))
                return
            style = "::section {""background-color: #f3f3f3; }"
            self.ui.popularTable.horizontalHeader().setStyleSheet(style)
            self.ui.popularTable.setColumnCount(len(results[0])) # amount of elements in tuple
            self.ui.popularTable.setRowCount(len(results))
            self.ui.popularTable.setHorizontalHeaderLabels(['Business Name'])
            currentRowCount = 0
            for row in results:
                for colCount in range (0, len(results[0])):
                    if isinstance(row[colCount], float):
                        self.ui.popularTable.setItem(currentRowCount, colCount, QTableWidgetItem(str(round(row[colCount], 2))))
                    else:
                        self.ui.popularTable.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                currentRowCount += 1
        except Exception as e:
            print("popular Query failed:", str(e))
        
    def updateSuccessfulTable(self):
        # get businesses with >=4.0 stars
        zipcode = self.ui.zipCodeList.selectedItems()[0].text()
        sql_str = "SELECT b.name, b.stars FROM business b WHERE b.zipcode = '" + zipcode + "' AND b.stars >= 4.0;"
        try:
            results = self.executeQuery(sql_str)

            # update successful table
            if len(results) == 0:
                self.ui.successfulTable.setColumnCount(1)
                self.ui.successfulTable.setRowCount(1)
                self.ui.successfulTable.setItem(0, 0, QTableWidgetItem("No successful businesses found!"))
                return
            style = "::section {""background-color: #f3f3f3; }"
            self.ui.successfulTable.horizontalHeader().setStyleSheet(style)
            self.ui.successfulTable.setColumnCount(len(results[0])) # amount of elements in tuple
            self.ui.successfulTable.setRowCount(len(results))
            self.ui.successfulTable.setHorizontalHeaderLabels(['Business Name', 'Stars'])
            self.ui.successfulTable.setColumnWidth(0, 400) # business name
            self.ui.successfulTable.setColumnWidth(1, 100) # stars
            currentRowCount = 0
            for row in results:
                for colCount in range (0, len(results[0])):
                    if isinstance(row[colCount], float):
                        self.ui.successfulTable.setItem(currentRowCount, colCount, QTableWidgetItem(str(round(row[colCount], 2))))
                    else:
                        self.ui.successfulTable.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                currentRowCount += 1
        except Exception as e:
            print("Query failed: ", str(e))

    def categoryChanged(self):
        if (self.ui.stateList.currentIndex() >= 0) and (len(self.ui.categoryList.selectedItems()) > 0):
            state = self.ui.stateList.currentText()
            city = self.ui.cityList.selectedItems()[0].text()
            zipcode = self.ui.zipCodeList.selectedItems()[0].text()
            category = self.ui.categoryList.selectedItems()[0].text()
            # sql_str = "SELECT name, city, state FROM business " + \
            # "JOIN categories ON business.business_id = categories.business_id " + \
            # "WHERE state = '" + state + "' AND city = '" + city + "' AND zipcode = '" + zipcode + "' AND category_name = '" + category + "' ORDER BY name;"

            sql_str = "SELECT b.name, b.address, b.city, b.stars, b.reviewcount, b.reviewrating, COALESCE(SUM(c.count), 0) " + \
            "FROM business AS b JOIN checkins c ON b.business_id = c.business_id " + \
            "LEFT JOIN categories c2 ON b.business_id = c2.business_id " + \
            "WHERE b.state = '" + state + "' AND b.city = '" + city + "' AND b.zipcode = '" + zipcode + "' AND c2.category_name = '" + category + "' " + \
            "GROUP BY b.business_id, b.name, b.address, b.city, b.stars, b.reviewcount, b.reviewrating, c2.category_name;"
            try:
                print(sql_str)
                results = self.executeQuery(sql_str)
                self.updateBusinessTable(results)
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
        if len(results) == 0:
            self.ui.businessTable.setColumnCount(1)
            self.ui.businessTable.setRowCount(1)
            self.ui.businessTable.setItem(0, 0, QTableWidgetItem("No businesses found!"))
            return
        style = "::section {""background-color: #f3f3f3; }"
        self.ui.businessTable.horizontalHeader().setStyleSheet(style)
        self.ui.businessTable.horizontalHeader().setMinimumHeight(40)
        self.ui.businessTable.setColumnCount(len(results[0])) # amount of elements in tuple
        self.ui.businessTable.setRowCount(len(results))
        self.ui.businessTable.setHorizontalHeaderLabels(['Business Name', 'Address', 'City', 'Stars', '# Reviews', 'Review Rating', 'Checkins'])
        self.ui.businessTable.resizeColumnsToContents()
        self.ui.businessTable.setColumnWidth(0, 300) # business name
        self.ui.businessTable.setColumnWidth(1, 200) # address
        self.ui.businessTable.setColumnWidth(2, 100) # city
        self.ui.businessTable.setColumnWidth(3, 50) # stars
        self.ui.businessTable.setColumnWidth(4, 100) # reviewcount
        self.ui.businessTable.setColumnWidth(5, 150) # reviewrating 
        self.ui.businessTable.setColumnWidth(6, 50) # checkins
        currentRowCount = 0
        for row in results:
            for colCount in range (0, len(results[0])):
                if isinstance(row[colCount], float):
                    self.ui.businessTable.setItem(currentRowCount, colCount, QTableWidgetItem(str(round(row[colCount], 2))))
                else:
                    self.ui.businessTable.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
            currentRowCount += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myApp()
    window.show()
    sys.exit(app.exec_())
