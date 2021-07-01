#
# def search_layer(self, layername):
#     couche = None
#     for ch in QgsProject.instance().mapLayers().values():
#         if ch.name() == layername:
#             couche = ch
#             break
#     return couche
#
# def create_layer(self):
#     ch = self.search_layer('projet')
#     if ch == None:
#         ch=QgsVectorLayer("Point?crs=EPSG:3857&field=Nom:string(25)", "projet", "memory")
#     return ch


# def projects_list(self):
#     # Lister les projets existants
#     project_layer = self.search_layer('projet')
#     if project_layer==None:
#         project_layer=self.create_layer()
#     index = project_layer.fields().indexFromName('Nom')
#     projects = project_layer.uniqueValues(index)
#     list_projects = []
#     for i in range(len(projects)):
#         a = str(projects[i])
#         list_projects.append(a)
#     self.dlg.combo_choose.clear()
#     self.dlg.combo_choose.addItems(list_projects)

# def select_project(self):
#     self.dlg.project_name.setText(self.dlg.combo_choose.currentText())
#     project_layer = self.search_layer('projet')
#     project_index = self.dlg.combo_choose.currentIndex()
#     features = processing.features(project_layer)
#     for feature in features:
#         if feature.id()==project_index+1:
#             geom = feature.geometry()
#             x = geom.asPoint().x()
#             y = geom.asPoint().y()
#             self.dlg.x_projet.setText(str(x))
#             self.dlg.y_projet.setText(str(y))

# def create_project(self):
#     x = self.dlg.x_projet.text()
#     x = float(x)
#     y = self.dlg.y_projet.text()
#     y = float(y)
#     name = self.dlg.project_name.text()
#
#     ch = self.search_layer('projet')
#     if ch ==None:
#         ch = self.create_layer()
#     pr = ch.dataProvider()
#     ch.startEditing()
#     fet = QgsFeature()
#     fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x,y)))
#     fet.setAttributes([name])
#     pr.addFeatures([fet])
#     ch.commitChanges()
#     ch.updateExtents()
#     QgsProject.instance().addMapLayer(ch)
#
#     # layers = [tree_layer.layer() for tree_layer in QgsProject.instance().layerTreeRoot().findLayers()]
#     # layer_list = []
#     # for layer in layers:
#     #     layer_list.append(layer.name())
#     # self.dlg.combo_choose.addItems(layer_list)
#     layers = [tree_layer.layer() for tree_layer in QgsProject.instance().layerTreeRoot().findLayers()]
#     layer_list = []
#     for layer in layers:
#         layer_list.append(layer.name())
#     self.dlg.combo_choose.addItems(layer_list)
#
# def buffer(self):
#     x = self.dlg.x_projet.text()
#     # x = float(x)
#     y = self.dlg.y_projet.text()
#     # y = float(y)
#     # radius = self.dlg.buffer_radius.text()
#     radius = "1000"
#     radius= float(radius)
#
#     ch = self.search_layer('projet')
#     buffer_layer = self.search_layer('buffer')
#     if buffer_layer ==None:
#         buffer_layer = QgsVectorLayer('Polygon?crs=EPSG:3857', 'buffer' , "memory")
#
#     if int(buffer_layer.featureCount()) != 0:
#         feats = buffer_layer.getFeatures()
#         buffer_layer.startEditing()
#         for fid in feats:
#             buffer_layer.deleteFeature(fid.id())
#         buffer_layer.commitChanges()
#         buffer_layer.updateExtents()
#         QgsProject.instance().addMapLayer(buffer_layer)
#
#         pr = buffer_layer.dataProvider()
#         buffer_layer.startEditing()
#         for feature in ch.getFeatures():
#             geom = feature.geometry()
#             if geom.asPoint().x() == x and geom.asPoint().y() == y:
#                 fet = QgsFeature()
#                 fet.setGeometry(geom.buffer(radius, 20))
#                 pr.addFeatures([fet])
#         buffer_layer.commitChanges()
#         buffer_layer.updateExtents()
#
#         symbols = buffer_layer.renderer().symbols()
#         symbols = symbols[0]
#         symbols.setColor(QColor.fromRgb(221, 86, 86))
#         couche_buff.setOpacity(40)
#         QgsProject.instance().addMapLayer(buffer_layer)
#
#         self.zoomTo("buffer")

# def zoomTo(self,name):
#     buffer_layer = self.search_layer(name)
#     feats = buffer_layer.getFeatures()
#     for fid in feats:
#         buffer_layer.select(fid.id())
#         self.iface.mapCanvas().zoomToSelected()
#         break


# def intersection(self):
#
#  # for ch in QgsProject.instance().mapLayers().values():
#  #     ch.removeSelection()
#
#  buffer_layer = self.search_layer('Zones')
#  if buffer_layer==None:
#      buffer_layer =QgsVectorLayer("Polygon?crs=EPSG:3857&field=Projets:string(25)&field=Status:string(25)&field=Surface:string(25)&field=Surfaces d'intersection:string(25)", 'Zones' , "memory")
#
#  #delete existing data
#  if int(buffer_layer.featureCount())!=0:
#       feats=buffer_layer.getFeatures()
#       buffer_layer.startEditing()
#       for fid in feats:
#           buffer_layer.deleteFeature(fid.id())
#  buffer_layer.updateExtents()
#  QgsProject.instance().addMapLayer(buffer_layer)
#
# #layers intersection
#  selectionsid=[]
#  selectionstatus=[]
#  selectionsurface=[]
#  selectionintersurface=[]
#  pr = buffer_layer.dataProvider()
#  buffer_layer.startEditing()
#  for ch in QgsProject.instance().mapLayers().values():
#      buffer_layer = self.search_layer('buffer')
#      if ch.name()!="projet" and ch.name()!="buffer" and ch.name()!="Zones":
#          featsbuffer=buffer_layer.getFeatures()
#          for fidbuff in featsbuffer:
#                  feats=ch.getFeatures()
#                  for fid in feats:
#                       if fidbuff.geometry().intersects(fid.geometry()):
#                           fet = QgsFeature()
#                           selectionsid.append(fid.id())
#                           selectionstatus.append(ch.name())
#                           surface=ch.fieldNameIndex("Shape_Area")
#                           selectionsurface.append(fid.attributes()[surface])
#                           selectionintersurface.append(fidbuff.geometry().intersection(fid.geometry()).area())
#                           fet.setAttributes([fid.id(),ch.name(),fid.attributes()[surface],fidbuff.geometry().intersection(fid.geometry()).area()])
#                           fet.setGeometry(fidbuff.geometry().intersection(fid.geometry()))
#                           pr.addFeatures([fet])
#                           ch.setSelectedFeatures(selectionsid)
#                           self.iface.mapCanvas().zoomToSelected(buffer_layer)
#
#  buffer_layer.commitChanges()
#  buffer_layer.updateExtents()
#  QgsProject.instance().addMapLayer(buffer_layer)
#
#  table_zones = self.dlg.map_display
#
#  nb_row = len(selectionsid)
#  nb_col = 4
#  n=nb_row+1
#
#  zones_inter = [0] * n
#  for i in range(n):
#       zones_inter[i] = [0] * nb_col
#
#  zones_inter[0][0]='Projet'
#  zones_inter[0][1]='Statuts'
#  zones_inter[0][2]='Surface'
#  zones_inter[0][3]="Surface d'intersection "
#  for i in range(nb_row):
#           j=i+1
#           zones_inter[j][0]=selectionsid[i]
#           zones_inter[j][1]=selectionstatus[i]
#           zones_inter[j][2]=selectionsurface[i]
#           zones_inter[j][3]=selectionintersurface[i]
#
#
#  table_zones.setRowCount(nb_row)
#  table_zones.setColumnCount(nb_col)
#  for row in range(nb_row):
#      ids = QTableWidgetItem(str(selectionsid[row]))
#      status= QTableWidgetItem(str(selectionstatus[row]))
#      surfaces = QTableWidgetItem(str(selectionsurface[row]))
#      surfacesinter = QTableWidgetItem(str(selectionintersurface[row]))
#
#      table_zones.setItem(row,0,ids)
#      table_zones.setItem(row,1,status)
#      table_zones.setItem(row,2,surfaces)
#      table_zones.setItem(row,3,surfacesinter)
#
#  table_zones.setHorizontalHeaderLabels([u'Projet',u'Status',u'Surface',u"Surface d'intersection"])
#  table_zones.setEditTriggers(table_zones.NoEditTriggers)
#  table_zones.resizeColumnsToContents()
#  return zones_inter

