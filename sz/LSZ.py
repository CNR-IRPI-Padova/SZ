# -*- coding: utf-8 -*-
"""
/***************************************************************************
 model
                                 A QGIS plugin
 Landslide Susceptibility Zoning
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-06-22
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Giacomo Titti CNR-IRPI
        email                : giacomotitti@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .LSZ_dialog import modelDialog
import os.path

##############################
import numpy as np
from osgeo import gdal
import sys
import math
import csv
#sys.path.append('/home/irpi/.qgis2/python/plugins/WoE')
from .classe import WoE
from qgis.core import QgsMessageLog
import scipy.misc as im
import sys
##############################


class model:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'model_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        #Create the dialog (after translation) and keep reference
        #self.dlg = modelDialog()#WOEdialg
        # if self.first_start == True:
        #    self.first_start = False
        #    self.dlg = modelDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&SZ')
        self.toolbar = self.iface.addToolBar(u'SZ')
        self.toolbar.setObjectName(u'SZ')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None#none

    #####################################################

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('model', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/sz/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Susceptibiliy Zoning'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&SZ'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
    #import input cause
    # def select_input_file(self):
    #     filename, _ = QFileDialog.getOpenFileName(self.dlg, 'Select input raster cause 1','', '*.tif')
    #     self.dlg.lineEdit.setText(filename)
    #
    # def select_input2_file(self):
    #     filename, _ = QFileDialog.getOpenFileName(self.dlg, "Select input raster cause 2","", '*.tif')
    #     self.dlg.lineEdit_2.setText(filename)
    #
    # def select_input3_file(self):
    #     filename, _ = QFileDialog.getOpenFileName(self.dlg, "Select input raster cause 3","", '*.tif')
    #     self.dlg.lineEdit_3.setText(filename)
    #
    # def select_input4_file(self):
    #     filename, _ = QFileDialog.getOpenFileName(self.dlg, "Select input raster cause 4","", '*.tif')
    #     self.dlg.lineEdit_4.setText(filename)
    # #import input cause txt
    def select_txt_file(self):
        filename, _ = QFileDialog.getOpenFileName(self.dlg, "Select input classes cause 1","", '*.txt')
        self.dlg.lineEdit_6.setText(filename)

    def select_txt2_file(self):
        filename, _ = QFileDialog.getOpenFileName(self.dlg, "Select input classes cause 2","", '*.txt')
        self.dlg.lineEdit_7.setText(filename)

    def select_txt3_file(self):
        filename, _ = QFileDialog.getOpenFileName(self.dlg, "Select input classes cause 3","", '*.txt')
        self.dlg.lineEdit_8.setText(filename)

    def select_txt4_file(self):
        filename, _ = QFileDialog.getOpenFileName(self.dlg, "Select input classes cause 4","", '*.txt')
        self.dlg.lineEdit_9.setText(filename)
    # ####inventory,dem,fold
    # def select_input10_file(self):
    #     filename, _ = QFileDialog.getOpenFileName(self.dlg, "Select input inventory","", '*.shp')
    #     self.dlg.lineEdit_10.setText(filename)
    #
    # def select_input11_file(self):
    #     filename, _ = QFileDialog.getOpenFileName(self.dlg, "Select input DEM","", '*.tif')
    #     self.dlg.lineEdit_11.setText(filename)

    def select_input16_file(self):
        filename= QFileDialog.getExistingDirectory(self.dlg, "Work folder","")
        self.dlg.lineEdit_16.setText(filename)

    # def select_input12_file(self):
    #     filename, _ = QFileDialog.getOpenFileName(self.dlg, "Select polygon","", '*.shp')
    #     self.dlg.lineEdit_12.setText(filename)

    # def select_ext(self):
    #     filename, _ = QFileDialog.getOpenFileName(self.dlg, "Select polygon","", '*.shp')
    #     self.dlg.mExtentGroupBox.setText(filename)

    #####ymax,xmin,ymin,xmax
#    def select_ymax(self):
#        filename = QFileDialog.getOpenFileName(self.dlg, "Select input inventory","", '*.tif')
#        self.dlg.doubleSpinBox.setText(filename)

#    def select_xmin(self):
#        filename = QFileDialog.getOpenFileName(self.dlg, "Select input DEM","", '*.tif')
#        self.dlg.doubleSpinBox2.setText(filename)

#    def select_ymin(self):
#        filename = QFileDialog.getExistingDirectory(self.dlg, "Work folder","")
#        self.dlg.doubleSpinBox4.setText(filename)

#    def select_xmax(self):
#        filename = QFileDialog.getExistingDirectory(self.dlg, "Work folder","")
#        self.dlg.doubleSpinBox3.setText(filename)

    #output file save
    def select_output_file(self):
        filename, _ = QFileDialog.getSaveFileName(self.dlg, "Select output raster ","", '*.tif')
        self.dlg.lineEdit_5.setText(filename)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = modelDialog()
            ########################################
            #input button
            # self.dlg.lineEdit.clear()
            # self.dlg.pushButton.clicked.connect(self.select_input_file)
            # self.dlg.lineEdit_2.clear()
            # self.dlg.pushButton_2.clicked.connect(self.select_input2_file)
            # self.dlg.lineEdit_3.clear()
            # self.dlg.pushButton_3.clicked.connect(self.select_input3_file)
            # self.dlg.lineEdit_4.clear()
            # self.dlg.pushButton_4.clicked.connect(self.select_input4_file)
            # #input txt classes
            self.dlg.lineEdit_6.clear()
            self.dlg.pushButton_6.clicked.connect(self.select_txt_file)
            self.dlg.lineEdit_7.clear()
            self.dlg.pushButton_7.clicked.connect(self.select_txt2_file)
            self.dlg.lineEdit_8.clear()
            self.dlg.pushButton_8.clicked.connect(self.select_txt3_file)
            self.dlg.lineEdit_9.clear()
            self.dlg.pushButton_9.clicked.connect(self.select_txt4_file)
            # #inventory,dem,fold
            # self.dlg.lineEdit_10.clear()
            # self.dlg.pushButton_10.clicked.connect(self.select_input10_file)
            # self.dlg.lineEdit_11.clear()
            # self.dlg.pushButton_11.clicked.connect(self.select_input11_file)
            self.dlg.lineEdit_16.clear()
            self.dlg.pushButton_12.clicked.connect(self.select_input16_file)
            #output button
            self.dlg.lineEdit_5.clear()
            self.dlg.pushButton_5.clicked.connect(self.select_output_file)
            #boundary shp
            #self.dlg.lineEdit_12.clear()
            #self.dlg.pushButton_13.clicked.connect(self.select_input12_file)
            #

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # import class classe###################
            self.test = WoE()
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # if len(self.dlg.lineEdit.text())==0:
            #     QgsMessageLog.logMessage('ERROR: Cause 1 cannot be empty', tag="WoE")
            #     raise ValueError  # Cause 1 cannot be empty, see 'WoE' Log Messages Panel
            if len(self.dlg.lineEdit_6.text())==0:
                QgsMessageLog.logMessage('ERROR: Classes 1 classes cannot be empty', tag="WoE")
                raise ValueError  # Cause 1 classes cannot be empty, see 'WoE' Log Messages Panel
            else:
                self.test.Wcause1=self.dlg.mMapLayerComboBox_4
                QgsMessageLog.logMessage(self.test.Wcause1, tag="WoE")
                self.test.classes1=self.dlg.lineEdit_6.text()
                QgsMessageLog.logMessage(self.test.classes1, tag="WoE")
            if self.dlg.checkBox_6==False:
                self.test.Wcause2=None
                self.test.classes2=None
            elif len(self.dlg.lineEdit_7.text())==0:
                QgsMessageLog.logMessage('ERROR: Classes 2 cannot be empty', tag="WoE")
                raise ValueError  # inventory cannot be empty, see 'WoE' Log Messages Panel
            else:
                self.test.Wcause2=self.dlg.mMapLayerComboBox_6
                self.test.classes2=self.dlg.lineEdit_7.text()
            if self.dlg.checkBox_8==False:
                self.test.Wcause3=None
                self.test.classes3=None
            elif len(self.dlg.lineEdit_8.text())==0:
                QgsMessageLog.logMessage('ERROR: Classes 3 cannot be empty', tag="WoE")
                raise ValueError  # inventory cannot be empty, see 'WoE' Log Messages Panel
            else:
                self.test.Wcause3=self.dlg.mMapLayerComboBox_8
                self.test.classes3=self.dlg.lineEdit_8.text()
            if self.dlg.checkBox_10==False:
                self.test.Wcause4=None
                self.test.classes4=None
            elif len(self.dlg.lineEdit_9.text())==0:
                QgsMessageLog.logMessage('ERROR: Classes 4 cannot be empty', tag="WoE")
                raise ValueError  # inventory cannot be empty, see 'WoE' Log Messages Panel
            else:
                self.test.Wcause4=self.dlg.mMapLayerComboBox_10
                self.test.classes4=self.dlg.lineEdit_9.text()
            if len(self.dlg.lineEdit_10.text())==0:
                QgsMessageLog.logMessage('ERROR: inventory cannot be empty', tag="WoE")
                raise ValueError  # inventory cannot be empty, see 'WoE' Log Messages Panel
            else:
                self.test.inventory=self.dlg.mMapLayerComboBox_3
            # if len(self.dlg.lineEdit_11.text())==0:
            #     QgsMessageLog.logMessage('ERROR: dem cannot be empty', tag="WoE")
            #     raise ValueError  # dem cannot be empty, see 'WoE' Log Messages Panel
            # else:
            self.test.Wdem=self.dlg.mMapLayerComboBox_3
            if len(self.dlg.lineEdit_5.text())==0:
                QgsMessageLog.logMessage('ERROR: LSIout cannot be empty', tag="WoE")
                raise ValueError  # LSIout cannot be empty, see 'WoE' Log Messages Panel
            else:
                self.test.LSIout=self.dlg.lineEdit_5.text()
            if self.dlg.checkBox_2==False:
                self.test.fold='/tmp'
            else:
                self.test.fold=self.dlg.lineEdit_16.text()
            if self.dlg.checkBox.isChecked() == False:
                self.test.poly=self.dlg.mMapLayerComboBox
                self.test.polynum=0
            else:
                self.test.polynum=1
                #self.test.poly=self.dlg.lineEdit_12.text()
            #xmin,ymin,xmax,ymax
            # self.test.xmax=round(self.dlg.doubleSpinBox_3.value(),2)
            # self.test.ymax=round(self.dlg.doubleSpinBox.value(),2)
            # self.test.xmin=round(self.dlg.doubleSpinBox_2.value(),2)
            # self.test.ymin=round(self.dlg.doubleSpinBox_4.value(),2)
            #xmin,ymin,xmax,ymax
            self.test.xmax=round(self.dlg.comboExtentChoiche.currentExtent().xMaximum(),2)
            self.test.ymax=round(self.dlg.comboExtentChoiche.currentExtent().yMaximum(),2)
            self.test.xmin=round(self.dlg.comboExtentChoiche.currentExtent().xMinimum(),2)
            self.test.ymin=round(self.dlg.comboExtentChoiche.currentExtent().yMinimum(),2)
            self.test.epsg=self.dlg.crsChoice.crs().authid()


            self.test.w=abs(round(self.dlg.doubleSpinBox_5.value(),4))
            self.test.h=abs(round(self.dlg.doubleSpinBox_6.value(),4))

            self.test.iter()
            self.test.sumWf()
            self.test.saveLSI()
