def clear(self):
    # vider les champs
    self.dlg.X.setText('')
    self.dlg.Y.setText('')
    self.dlg.buffer_radius.setText('')
    self.dlg.couches.clear()

    for index in range(self.dlg.layers_name.count()):
        item = self.dlg.layers_name.item(index)
        self.dlg.layer_name.takeItem(self.dlg.layers_name.row(item))
    self.dlg.result.setColumnCount(3)
    self.dlg.result.setRowCount(1)
    self.dlg.result.setHorizontalHeaderItem(0, QTableWidgetItem("ID"))
    self.dlg.result.setHorizontalHeaderItem(1, QTableWidgetItem("Statut"))
    self.dlg.result.setHorizontalHeaderItem(2, QTableWidgetItem("Surface"))
    self.dlg.stackedWidget.setCurrentIndex(0)


def new_project(self):
    self.dlg.combo_choose.addItem('Nouveau projet')
    self.dlg.combo_choose.setCurrentIndex(self.dlg.combo_choose.count() - 1)


def loadLayers(self):
    layers = [tree_layer.layer() for tree_layer in QgsProject.instance().layerTreeRoot().findLayers()]
    layers_list = []
    for layer in layers:
        layers_list.append(layer.name())
    self.dlg.couches.addItems(layers_list)
    self.dlg.combo_choose.addItems(layers_list)


def addLayer(self):
    Found = False
    if (self.dlg.layers_name.count() != 0):
        for index in range(self.dlg.layers_name.count()):
            if (self.dlg.layers_name.item(index).text() == self.dlg.couches.currentText()):
                Found = True
    if Found == False:
        self.dlg.layers_name.addItem(str(self.dlg.couches.currentText()))


def removeLayer(self):
    item = self.dlg.layers_name.currentItem()
    if item != None:
        self.dlg.layers_name.takeItem(self.dlg.layers_name.row(item))


def FindLayerByName(self, NameLayer):
    layer = None
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == NameLayer:
            layer = lyr
            break
    return layer


def analyser(self):
    self.Validate()

    self.dlg.stackedWidget.setCurrentIndex(self.dlg.stackedWidget.currentIndex() + 1)


def clearLayer(self, layer):
    provider = layer.dataProvider()
    layer.startEditing()
    feat = layer.getFeatures()
    if layer.featureCount() > 0:
        provider.deleteFeatures([i.id() for i in feat])
    layer.triggerRepaint()


def is_number(self, s, x):
    try:
        float(s)
        return True
    except ValueError:
        x.setText('Error')
        return False


def Validate(self):
    x = float(self.dlg.X.text())
    y = float(self.dlg.Y.text())

    self.is_number(x, self.dlg.X)
    self.is_number(y, self.dlg.Y)

    #   Create PROJECT center
    center = QgsVectorLayer("Point", "Centre du projet", "memory")
    provider = center.dataProvider()

    ft = QgsFeature()
    ft.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
    ft.setAttributes([0, "Position"])
    provider.addFeatures([ft])
    center.commitChanges()
    center.updateExtents()

    # Search for buffer layer
    canvas = self.iface.mapCanvas()
    mapRenderer = canvas.mapSettings()
    crs = mapRenderer.destinationCrs()
    buffer_layer = self.FindLayerByName('Buffer')

    #       if it exists, we clear / delete the existing one and create a new one
    #     If it doesn't exist, we generate a new one
    if buffer_layer != None:
        self.clearLayer(buffer_layer)
    else:
        buffer_layer = QgsVectorLayer('Polygon?crs=EPSG:3875' + str(crs.toWkt()), 'Buffer', "memory")
        QgsProject.instance().addMapLayer(buffer_layer)
        symbols = buffer_layer.renderer().symbols()
        symbol = symbols[0]
        symbol.setColor(QColor.fromRgb(221, 86, 86))
        buffer_layer.setOpacity(0.4)
        self.loadLayer(buffer_layer, 0)
        # renderer = buffer_layer.renderer()
        # ranger = renderer.ranges()[1]
        # symbol = ranger.symbol()
        # new_symbol = symbol.clone()
        # new_symbol.setColor(QColor.fromRgb(221,86,86))
        # renderer.updateRangeSymbol(1,new_symbol)
        buffer_layer.setOpacity(0.4)
    radius = self.dlg.buffer_radius.text()
    self.is_number(radius, self.dlg.buffer_radius)
    radius = float(radius)
    prd = buffer_layer.dataProvider()

    for e in center.getFeatures():
        attributs = e.attributes()
        geom = e.geometry()
        buffer = geom.buffer(radius, 20)
        seg = QgsFeature()
        seg.setGeometry(buffer)
        # seg.setAttributes([attributs[0],attributs[1],radius])
        # provider.addFeatures([seg])
        buffer_layer.commitChanges()
        buffer_layer.updateExtents()
    QgsProject.instance().addMapLayer(buffer_layer)
    areas = []

    #     table headers
    self.dlg.result.setColumnCount(4)
    self.dlg.result.setRowCount(1)
    self.dlg.result.setHorizontalHeaderItem(0, QTableWidgetItem("ID"))
    self.dlg.result.setHorizontalHeaderItem(1, QTableWidgetItem("Reference"))
    self.dlg.result.setHorizontalHeaderItem(2, QTableWidgetItem("State"))
    self.dlg.result.setHorizontalHeaderItem(3, QTableWidgetItem("Surface"))

    memory_layer = self.FindLayerByName(str(self.dlg.combo_choose.currentText()))
    if (str(self.dlg.combo_choose.currentText()) == 'Nouveau Projet'):
        memory_layer = QgsVectorLayer('Polygon?crs=EPSG:3875', 'Nouveau Projet', 'memory')
        prov = memory_layer.dataProvider()
        prov.addAttributes([QgsField("id", QVariant.Int)])
        prov.addAttributes([QgsField("Reference", QVariant.Int)])
        prov.addAttributes([QgsField("State", QVariant.String)])
        prov.addAttributes([QgsField("Surface", QVariant.Double)])
        memory_layer.updateFields()
    i = 0

    # Fill TableWidget By Current Project Attribute Table(Existing Project)
    for area_feature in memory_layer.getFeatures():
        self.dlg.result.insertRow(i + 1)
        self.dlg.result.setItem(i, 0, QTableWidgetItem(str(area_feature['ID'])))
        self.dlg.result.setItem(i, 1, QTableWidgetItem(str(area_feature['Reference'])))
        self.dlg.result.setItem(i, 2, QTableWidgetItem(str(area_feature['State'])))
        self.dlg.result.setItem(i, 3, QTableWidgetItem(str(area_feature['Surface'])))
        i = i + 1
    self.dlg.result.removeRow(i)

    # Fill TableWidget and Project Attribute Table
    for index in range(self.dlg.layers_name.count()):
        area_layer = self.FindLayerByName(self.dlg.layers_name.item(index).text())
        if (area_layer.name() != "Buffer" and area_layer.name() != str(self.dlg.combo_choose.currentText())):
            for line_feature in buffer_layer.getFeatures():
                for area_feature in area_layer.getFeatures():
                    if (area_feature.geometry().intersects(line_feature.geometry()) == True):
                        areas.append(area_feature.id())
                        self.dlg.result.insertRow(i)
                        self.dlg.result.setItem(i, 0, QTableWidgetItem(str(i)))
                        self.dlg.result.setItem(i, 1, QTableWidgetItem(str(area_feature['REFERENCE_'])))
                        self.dlg.result.setItem(i, 2, QTableWidgetItem(str(area_layer.name())))
                        self.dlg.result.setItem(i, 3, QTableWidgetItem(str(area_feature.geometry().area())))
                        geom = area_feature.geometry().intersection(line_feature.geometry())
                        feat = QgsFeature()
                        feat.setAttributes([i, str(area_feature['REFERENCE_']), area_layer.name(), float(geom.area())])

                        feat.setGeometry(geom)
                        prov.addFeatures([feat])
                        i = i + 1
                memory_layer.updateFields()
        QgsProject.instance().addMapLayer(memory_layer)
        self.loadLayer(memory_layer, 1)
        field = memory_layer.fields().indexFromName('State')
        unique_values = memory_layer.uniqueValues(field)
        column = 'State'

        categories = []
        for unique_value in unique_values:
            # initialize the default symbol for this geometry type
            symbol = QgsSymbolV2.defaultSymbol(memory_layer.geometryType())
            # configure a symbol layer
            layer_style = {}
            layer_style['color'] = '%d, %d, %d' % (
            random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
            layer_style['outline'] = '#000000'
            symbol_layer = QgsSimpleFillSymbolLayerV2.create(layer_style)
            # replace default symbol layer with the configured one
            if symbol_layer is not None:
                symbol.changeSymbolLayer(0, symbol_layer)
                # create renderer object
                category = QgsRendererCategoryV2(unique_value, symbol, str(unique_value))
                # entry for the list of category items
                categories.append(category)
        renderer = QgsCategorizedSymbolRenderer(column, categories)
        memory_layer.setRendererV2(renderer)

        memory_layer.triggerRepaint()
        # Zoom to Buffer
        ex = bufferLayer.extent()
        self.iface.mapCanvas().setExtent(ex)
        self.dlg.result.removeRow(i)


def loadLayer(self, layer, order):
    root = QgsProject.instance().layerTreeRoot()
    mylayer = root.findLayer(layer.id())
    myClone = mylayer.clone()
    parent = mylayer.parent()
    parent.insertChildNode(order, myClone)
    parent.removeChildNode(mylayer)


def savefile(self):
    layer = self.FindLayerByName(self.dlg.combo_choose.currentText())
    layerex = self.FindLayerByName('Buffer')
    ex = layerex.extent()
    self.iface.mapCanvas().setExtent(ex)
    mapRenderer = self.iface.mapCanvas().mapSettings()
    c = QgsComposition(mapRenderer)
    c.setPlotStyle(QgsComposition.Print)
    c.setPrintResolution(600)
    w, h = c.paperWidth(), c.paperHeight()
    composerMap = QgsComposerMap(c, 0, 0, w, h)
    c.addItem(composerMap)

    c2 = QgsComposition(mapRenderer)
    c2.setPlotStyle(QgsComposition.Print)
    x, y = 100, 0

    # Add Title
    title = QgsComposerLabel(c)
    title.setText("Carte de derogation : Region de Khmisset")
    title.setFont(QFont("Cambria", 20, QFont.Bold))
    title.setItemPosition(80, 4)
    title.adjustSizeToText()
    c.addItem(title)

    # Add Legende
    legend = QgsComposerLegend(c)
    legend.model().setLayerSet(mapRenderer.layerSet())
    legend.setItemPosition(10, 0)
    legend.setFrameEnabled(True)
    legend.setScale(.8)
    c.addItem(legend)

    # Add North Arrow
    arrow = QgsComposerPicture(c)
    # arrow.setPictureFile("C:\Program Files (x86)\QGIS Wien\apps\qgis-ltr\svg\arrows\NorthArrow_06.png")
    arrow.setSceneRect(QRectF(0, 0, 50, 50))
    arrow.setItemPosition(210, 15)
    arrow.updateItem()
    c.addItem(arrow)
    composerLabel = QgsComposerLabel(c)
    composerLabel.setText("N")
    composerLabel.setFont(QFont("Roboto", 30, QFont.Bold))
    composerLabel.setItemPosition(230, 15)
    composerLabel.adjustSizeToText()
    c.addItem(composerLabel)

    # Add Echelle
    item = QgsComposerScaleBar(c)
    item.setStyle('Single Box')
    item.setComposerMap(composerMap)
    item.applyDefaultSize()
    item.setAlignment(QgsComposerScaleBar.Left)
    item.setNumSegmentsLeft(0)
    item.setNumSegments(3)
    item.setItemPosition(200, 190)
    c.addItem(item)

    # Add Table
    table = QgsComposerAttributeTable(c2)
    table.setItemPosition(x, y)
    table.setVectorLayer(layer)
    table.setMaximumNumberOfFeatures(self.dlg.result.rowCount())
    values = []
    for row in range(self.dlg.result.rowCount()):
        item = self.dlg.result.item(row, 0)
        ids = int(item.text())
        values.append(ids)
    values = tuple(values)
    table.setFeatureFilter("ID IN " + str(values))
    table.setFilterFeatures(True)
    field_names = ['ID', 'Reference', 'State', 'Surface']
    col_name = []
    for name in field_names:
        col = QgsComposerTableColumn()
        col.setAttribute(name)
        col.setHeading(name)
        col_name.append(col)
    table.setColumns(col_name)
    c2.addItem(table)
    # Select Output Folder
    tablefile = QFileDialog.getSaveFileName(self.dlg, "Select output Table file ", "", '*.pdf')
    mapfile = QFileDialog.getSaveFileName(self.dlg, "Select output Map file ", "", '*.pdf')
    # Save to Pdf
    self.printpdf(c, mapfile, w, h)
    self.printpdf(c2, tablefile, w, float(self.dlg.result.rowCount() * 10))


def printpdf(self, c, filename, w, h):
    printer = QPrinter()
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(filename)
    printer.setPaperSize(QSizeF(w, h), QPrinter.Millimeter)

    printer.setFullPage(True)
    printer.setColorMode(QPrinter.Color)
    printer.setResolution(c.printResolution())
    pdfPainter = QPainter(printer)
    paperRectMM = printer.pageRect(QPrinter.Millimeter)
    paperRectPixel = printer.pageRect(QPrinter.DevicePixel)
    c.render(pdfPainter, paperRectPixel, paperRectMM)
    pdfPainter.end()


def Extent(self):
    canvas = self.iface.mapCanvas()
    cLayer = self.FindLayerByName(str(self.dlg.combo_choose.currentText()))
    self.iface.setActiveLayer(cLayer)
    expression = 'ID =' + str(self.dlg.result.currentItem().text())
    print(expression)
    expr = QgsExpression(expression)
    it = cLayer.getFeatures(QgsFeatureRequest(expr))
    ids = [i.id() for i in it]
    cLayer.setSelectedFeatures(ids)
    self.iface.mapCanvas().zoomToSelected()

    # self.loadLayers()
    # self.dlg.save_btn.clicked.connect(self.savefile)
    # self.dlg.analyser.clicked.connect(self.analyser)
    # self.dlg.Add.clicked.connect(self.addLayer)
    # self.dlg.Delete.clicked.connect(self.removeLayer)
    # self.dlg.result.itemDoubleClicked.connect(self.Extent)
    # self.dlg.pushButton.clicked.connect(self.new_project)

    class extra_Tools(QgsMapTool):

        def __init__(self, canvas, parent=None):
            QgsMapTool.__init__(self, canvas)
            self.canvas = canvas
            self.parent = parent

        def canvasPressEvent(self, event):
            pass

        def canvasMoveEvent(self, event):
            x = event.pos().x()
            y = event.pos().y()

            point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

        def canvasReleaseEvent(self, event):
            # Get the click
            x = event.pos().x()
            y = event.pos().y()

            point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

            self.parent.dlg.X.setText(str(point[0]))
            self.parent.dlg.Y.setText(str(point[1]))

        def activate(self):
            pass

        def deactivate(self):
            pass

        def isZoomTool(self):
            return False

        def isTransient(self):
            return False

        def isEditTool(self):
            return True
