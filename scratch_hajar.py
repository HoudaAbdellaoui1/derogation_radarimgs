
    def ZoneTampon(self):

        global layer_list
        global layers

        canvas = self.iface.mapCanvas()
        mapRenderer = canvas.mapSettings()
        crs = mapRenderer.destinationCrs()
        self.iface.activeLayer()
        # progress = self.dlg.progressBar
        # progress.setMaximum(100)
        # tam = self.dlg.buffer_radius.text()
        tam = '10000'
        distance = self.dlg.combo_choose.currentIndex()
        layer_buff = QgsVectorLayer("Polygon?crs=EPSG:3857" + str(crs.toWkt()), "Zone de rayonnement", "memory")
        pr = layer_buff.dataProvider()
        for elem in self.FindLayerByName('point de interet').getFeatures():
            geom = elem.geometry()
            buffer = geom.buffer(float(tam),10)
            poly = buffer.asPolygon()
            seg = QgsFeature()
            seg.setGeometry(QgsGeometry.fromPolygonXY(poly))
            pr.addFeatures([seg])
            layer_buff.updateExtents()
            layer_buff.setOpacity(0.4)
            # zooms to layer
        self.iface.actionZoomToLayer().trigger()
            # Ajout de la couche
            # count = layer_buff.selectedFeatureCount()
            # i = 0
            # for feature in layer_buff.selectedFeatures():
            #     i = i + 1
            #     percent = (i / float(count)) * 100
            #     progress.setValue(percent)
            #     time.sleep(1)
        QgsProject.instance().addMapLayers([layer_buff])
        layer_buff.isValid()

        layers = [tree_layer.layer() for tree_layer in QgsProject.instance().layerTreeRoot().findLayers()]
        # layers = self.iface.legendInterface().layers()
        layer_list = []
        self.dlg.combo_choose.clear()
        for layer in layers:
            layer_list.append(layer.name())
        self.dlg.combo_choose.addItems(layer_list)

    def table_attri(self):

        table = self.dlg.map_display
        canvas = self.iface.mapCanvas()
        areas = []
        line_layer = self.FindLayerByName('Zone de rayonnement')
        QgsMessageLog.logMessage(str(line_layer))
        area_layer = self.FindLayerByName(self.dlg.combo_choose.currentText())
        QgsMessageLog.logMessage(str(area_layer))

        prov = area_layer.dataProvider()
        fields = prov.fields()
        table.setColumnCount(7)
        table.setRowCount(1)
        i = 0
        for field in fields:
            if field.name() == "OBJECTID" or field.name() == "REGIME_FON" or field.name() == "REFERENCE_" or field.name() == "CERCLE" or field.name() == "COMMUNE" or field.name() == "STATUT_FON" or field.name() == "SUPERFICIE":
                self.dlg.map_display.setHorizontalHeaderItem(i, QTableWidgetItem(field.name()))
                i = i + 1

        varcheck = 0
        for line_feature in line_layer.getFeatures():
            i = 0
            for area_feature in area_layer.getFeatures():
                QgsMessageLog.logMessage(str(area_feature.geometry().intersects(line_feature.geometry())))
                if (area_feature.geometry().intersects(line_feature.geometry()) == True):
                    varcheck = 1
                    areas.append(area_feature.id())
                    area_feature.geometry().area()
                    table.insertRow(i + 1)
                    j = 0
                    k = 0
                    for field in fields:
                        if field.name() == "OBJECTID" or field.name() == "REGIME_FON" or field.name() == "REFERENCE_" or field.name() == "CERCLE" or field.name() == "COMMUNE" or field.name() == "STATUT_FON" or field.name() == "SUPERFICIE":
                            s = ''
                            s = str(area_feature.attributes()[j])
                            QMessageBox.information(None, "DEBUG:", str(s))
                            table.setItem(i, k, QTableWidgetItem(s))
                            k = k + 1
                        j = j + 1

                    i = i + 1
            table.removeRow(i)

            # if not varcheck:
            #     self.iface.messageBar().pushMessage("Problème : ","Désolés, pas d'intersection entre le couche choisie et alentour de point d'interet.Merci")

        # legend = self.iface.legendInterface()
        layers = [tree_layer.layer() for tree_layer in QgsProject.instance().layerTreeRoot().findLayers()]

        for layer in canvas.layers():
            if layer.type() == layer.VectorLayer:
                layer.removeSelection()
                QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
        canvas.refresh()
        QgsProject.instance().layerTreeRoot().findLayer(area_layer.id()).setItemVisibilityChecked(True)
        QgsProject.instance().layerTreeRoot().findLayer(line_layer.id()).setItemVisibilityChecked(True)
        # legend.setLayerVisible(area_layer, True)
        # legend.setLayerVisible(line_layer, True)
        # project=self.FindLayerByName('Couche_Projet')
        # legend.setLayerVisible(project, True)
        area_layer.select(areas)
        cLayer = self.iface.mapCanvas().currentLayer()
        indexes = table.selectionModel().selectedRows()
        cLayer.removeSelection()
        for index in sorted(indexes):
            print('Row %d is selected' % index.row())
            cLayer.select(index.row())
            canvas.zoomToSelected()
        table.itemSelectionChanged.connect(self.afficher_zoom)

    def afficher_inter(self, row_data, row_number):

        self.dlg.map_display.insertRow(row_number)
        column = 0
        for column_number, data in enumerate(row_data.attributes()):
            if column_number in [0, 3, 7, 10]:
                self.dlg.map_display.setItem(row_number, column, QTableWidgetItem(str(data)))
                column += 1

    def ajouter_table(self):

        canvas = self.iface.mapCanvas()
        w = self.FindLayerByName(self.dlg.combo_choose.currentText())
        v = self.FindLayerByName('Zone de rayonnement')

        self.dlg.map_display.setRowCount(0)
        field_names = [field.name() for num, field in enumerate(w.pendingFields()) if num in [0, 3, 7, 10]]
        self.dlg.map_display.setHorizontalHeaderLabels(field_names)

        row_number = 0
        for a in w.getFeatures():
            for b in v.getFeatures():
                if a.geometry().intersects(b.geometry()):
                    geom = a.geometry().intersection(b.geometry())
                    self.afficher_inter(geom, row_number)
                    row_number += 1

    def afficher_zoom(self):

        table = self.dlg.map_display

        canvas = self.iface.mapCanvas()
        cLayer = self.iface.mapCanvas().currentLayer()
        indexes = table.selectionModel().selectedRows()
        cLayer.removeSelection()
        for index in sorted(indexes):
            print('Row %d is selected' % index.row())
            cLayer.select(index.row())
            canvas.zoomToSelected()

    def intersection(self):
        v = self.FindLayerByName('Zone de rayonnement')
        poly = self.FindLayerByName(str(str(self.dlg.combo_choose.currentText())))
        for a in v.getFeatures():
            for b in poly.getFeatures():
                if a.geometry().intersects(b.geometry()):
                    poly.select(b.id())

    # def FindLayerByName(self,NameLayer):
    #     layer = None
    #     for lyr in QgsProject.instance().mapLayers().values():
    #        if lyr.name() == NameLayer:
    #            layer = lyr
    #            break
    #     return layer
