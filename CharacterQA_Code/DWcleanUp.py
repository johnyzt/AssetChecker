import maya.cmds as cmds
import maya.mel as mel


def clean_scene():
   msg = []
   #msg.append(clear_refs())
   msg.append(clear_groupID())
   msg.append(clear_panels())
   for m in msg:
       print m
   return

def clear_refs():
   referencedNodes = cmds.ls(type = 'reference')
   num = 0
   for node in referencedNodes:
       cmds.lockNode(node,lock = False)
       cmds.delete(node)
       num += 1
       print 'deleted %s'%node
   msg = '%i references deleted.' % num
   return msg

def clear_groupID():
   groupIDs = cmds.ls(type = 'groupId')
   num = 0
   for node in groupIDs:
       connections = cmds.listConnections(node)
       if not connections:
           cmds.delete(node)
           num += 1
           print 'deleted %s'%node
   msg = '%i groupIDs deleted.' % num
   return msg

def clear_panels():
   '''Description: Removes all panels and resets to default panels.
      Input: None
      Return: None'''
   default_panels = {'modelPanel1': 'Top View',
                     'modelPanel2': 'Side View',
                     'modelPanel3': 'Front View',
                     'modelPanel4': 'Persp View',
                     'outlinerPanel1': 'Outliner', 
                     'graphEditor1': 'Graph Editor',
                     'dopeSheetPanel1': 'Dope Sheet',
                     'clipEditorPanel1': 'Trax Editor',
                     'sequenceEditorPanel1': 'Camera Sequencer',
                     'hyperGraphPanel1': 'Hypergraph Hierarchy',
                     'hyperShadePanel1': 'Hypershade',
                     'visorPanel1': 'Visor',
                     'nodeEditorPanel1': 'Node Editor',
                     'createNodePanel1': 'Create Node',
                     'polyTexturePlacementPanel1': 'UV Texture Editor',
                     'renderView': 'Render View',
                     'blendShapePanel1': 'Blend Shape',
                     'dynRelEdPanel1': 'Dynamic Relationships Editor',
                     'relationshipPanel1': 'Relationship Editor',
                     'referenceEditorPanel1': 'Reference Editor',
                     'componentEditorPanel1': 'Component Editor',
                     'dynPaintScriptedPanel': 'Paint Effects',
                     'scriptEditorPanel1': 'Script Editor'}
   default_layouts = set(['hyperGraphInfo', 'hyperGraphLayout'])

   p_names = set(default_panels.keys())
   panels = set(cmds.getPanel(allPanels=True))
   panels = list(panels.difference(p_names))
   p_num = 0
   for panel in panels:
       cmds.deleteUI(panel, panel=True)
       p_num += 1
   
   layouts = set(cmds.ls(type=['hyperView', 'hyperLayout', 'hyperGraphInfo']))
   layouts = list(layouts.difference(default_layouts))
   l_num = 0
   for layout in layouts:
       try:
           cmds.delete(layout)
       except:
           pass
       finally:
           l_num += 1
       
   msg = '%i panels / %i layouts deleted' % (p_num, l_num)
   
   #Rebuild model panels if missing
   model_panels = ['modelPanel1','modelPanel2','modelPanel3','modelPanel4']
   gMainPane = mel.eval('global string $gMainPane; $temp = $gMainPane;')
   for m_panel in model_panels:
       if not cmds.modelPanel(m_panel, exists=True):
           cmds.modelPanel(m_panel, parent=gMainPane)
   
   for name, label in default_panels.items():
       try:
           cmds.panel(name, e=True, label=label)
       except:
           pass

   mel.eval('lookThroughModelPanel top modelPanel1')
   mel.eval('lookThroughModelPanel side modelPanel2')
   mel.eval('lookThroughModelPanel front modelPanel3')
   mel.eval('lookThroughModelPanel persp modelPanel4')
   mel.eval('setNamedPanelLayout "Single Perspective View"')
   return msg
   
   
clean_scene()
#clear_refs()
clear_groupID()
clear_panels()  