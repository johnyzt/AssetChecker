import maya.cmds as cmds
from pymel.core import * # for the file handling
import os
import xml.etree.ElementTree as ElementTree
from sets import Set


#class containing all global variables
class global_vars() :
    ITEM_LIST = []
    ITEM_INDEX = 0
    MAIN_WIN = None

    INFO = True
    NEG = True
    POS = False

    NEG_INDEX = 0

    Deformers=False
    Rig_Structure=False
    Geometry=False
    XML=False
    References=False
    Symmetry=False
    Double_Naming=False
    History=False

    topLeftCorner=[0,0]


def RGB01(R,G,B) :
    '''
    Converts 255,255,255 RGB to normalized 1,1,1 one :)
    '''
    r = float(R/255.0)
    g = float(G/255.0)
    b = float(B/255.0)

    return (r,g,b)


def setGlobal(var, val):
    '''
    Sets global variables accordingly with checkboxes - for printing msgs
    '''
    if var == "INFO" :
        global_vars.INFO = val
    if var == "NEG" :
        global_vars.NEG = val
    if var == "POS" :
        global_vars.POS = val

    #printing for debugging
    #print 'info=' + str(global_vars.INFO)
    #print 'neg=' + str(global_vars.NEG)
    #print 'pos=' + str(global_vars.POS)


#some constants - color values for messages:
DARKGREEN = RGB01(0, 100, 0)
DARKRED = RGB01(100, 0, 0)
GRAY = RGB01(100,100,100)
YELLOW = RGB01(100,100,0)
RED = RGB01(255,0,0)



def removeDuplicates(mylist):
    newlist = []
    for i in mylist:
        if i not in newlist:
            newlist.append(i)
    return newlist



def jzConvert(val, v_type) :
    '''
    converts xml variable values to proper types to setAttr - if type is not in the lib the converts to float
    might need looking into later - since there might be more types than listed down here
    '''
    if v_type == "doubleLinear" :
        return float(val)
    elif v_type == "doubleAngle" :
        return float(val)
    elif v_type == "double" :
        return float(val)
    elif v_type == "enum" :
        return int(val)
    elif v_type == "long" :
        return int(val)
    elif v_type == "bool" :
        return int(val)
    elif v_type == "string" :
        return val
    elif v_type == "float3" :
        return str(val).remove('[', ']')
    elif v_type == "float" :
        return float(val)
    elif v_type == "bool" :
        return int(val)
    elif v_type == "byte" :
        return int(val)
    else :
        return float(val)



def jzCompare(val, XMLval, v_type) :
    'compares attributes based on their type:'

    strVal = str(val)
    strXMLVal = str( jzConvert(XMLval, v_type) )

    floats = ["doubleLinear", "double", "doubleAngle", "float"]

    if v_type in floats :
        strXMLVal = strXMLVal.replace(' ','')
        strXMLVal = strXMLVal[0:strXMLVal.index('.')+4]

    if v_type == "bool" :
        if strXMLVal == '1' :
            strXMLVal = 'True'
        elif strXMLVal == '0':
            strXMLVal = 'False'

    #printing for debugging:
    #print('valAtr=' + strVal + ',v_type='+v_type)
    #print('valXML=' + strXMLVal + ',v_type='+v_type + "\n")

    #comparing long floats:
    if v_type in floats :
        big = ''
        little = ''

        if len(strXMLVal) >= len(strVal) :
            big = strXMLVal
            little = strVal
        else :
            big = strVal
            little = strXMLVal

        L = len(str(little))
        one =  str(big)[:L]
        two =  str(little)[:L]

        if one == two:
            return True
        else:
            return False

    #comparing everything else:
    if strXMLVal == strVal :
        return True
    else :
        return False

def jzCompareTypes(type1, type2) :
    '''
    compares two variable types - they are passed as strings
    returns True and False
    '''
    if type1 == type2 :
        return True

    types = []
    types.extend([type1, type2])

    if 'bool' in types and 'boolean' in types :
        return True
    if 'float' in types and 'double' in types :
        return True


def btnFIX(btnName, attr, val) :

    '''
    makes a button for fixing wrong attributes
    '''

    attr_type = cmds.getAttr(attr, type=True)
    converted_value = jzConvert(val, attr_type)

    try :
        cmds.setAttr( attr, converted_value )
    except :
        cmds.warning("Unable to set " + attr + " to " + str(val) + " - it might be locked or hidden")
        cmds.button(btnName, edit=True, bgc=(1,1,0), label="FAIL")
    else:
        cmds.warning("Variable fixed successfully!")
        cmds.button(btnName, edit=True, bgc=(0,1,0), label="FIXED", enable=False)



def printTextLineWithButton(message, attribute, value) :

    #if printing negative messages is off then exit
    if global_vars.NEG == False :
        return

    '''
    outputs a text line into the UI while checking asset:
    '''

    global_vars.ITEM_INDEX +=1
    btnName = "btn_"+str(global_vars.ITEM_INDEX)
    global_vars.ITEM_LIST.append(btnName)
    cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnFIX(btnName, attribute, value))

    printTextLineSec(message)

    global_vars.NEG_INDEX += 1



def printTextLine(message, color=None, textStyle="none", msgType='none', command='none', commandAttr='none') :
    '''
    outputs a text line into the UI while checking asset:
    takes 1 argument (nonoptional) - message is the message that will be printed
    3 optional arguments:
    color - bg color (R,G,B)
    textStyle - plain or bold
    msgType - none, info, neg, pos
    '''

    #make sure we exit when printing of certain type of messages is switched off:
    if msgType == 'info' and global_vars.INFO == False :
        return
    if msgType == 'pos' and global_vars.POS == False :
        return
    if msgType == 'neg' and global_vars.NEG == False :
        return

    if msgType == 'neg':
        global_vars.NEG_INDEX += 1


    fontStyle = 'plainLabelFont'

    if textStyle == "bold" :
        fontStyle = 'boldLabelFont'


    if command == 'none' :
        global_vars.ITEM_INDEX +=1
        itemName = "text_"+str(global_vars.ITEM_INDEX)
        global_vars.ITEM_LIST.append(itemName)

        if color == None :
            cmds.text(itemName, label="", font=fontStyle, width=35)
        else :
            cmds.text(itemName, label="", font=fontStyle, width=35, bgc=color)
    else :
        global_vars.ITEM_INDEX +=1
        btnName = "btn_"+str(global_vars.ITEM_INDEX)
        global_vars.ITEM_LIST.append(btnName)

        if command == 'select' :
            cmds.button(btnName, bgc=(1,0,0), label="select", width=35, height=14, command=lambda x:btnSelect(commandAttr, btnName))
        if command == 'selectNonUnique' :
            cmds.button(btnName, bgc=(1,0,0), label="select", width=35, height=14, command=lambda x:btnSelectNonUnique(commandAttr, btnName))
        if command == 'renameNonUnique' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnRenameNonUnique(obj=commandAttr, btn=btnName))
            cmds.popupMenu()
            cmds.menuItem("rename non unique objects", command=lambda x:btnRenameNonUnique(obj=commandAttr, btn=btnName))
            cmds.menuItem("select non unique objects", command=lambda x:btnSelectNonUnique(commandAttr, btnName))
        if command == 'rename' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnRename(commandAttr, btnName))
            cmds.popupMenu()
            cmds.menuItem("rename object", command=lambda x:btnRename(commandAttr, btnName))
            cmds.menuItem("select object", command=lambda x:btnSelect(commandAttr, btnName))
        if command == 'deleteHistory' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnDelHistory(commandAttr, btnName))
        if command == 'changeColor' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnChangeColor(commandAttr[0], commandAttr[1], btnName))
        if command == 'SetNonKeyable' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnSetNonKeyable(commandAttr, btnName))
        if command == 'createNode' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnCreateNode(commandAttr, btnName))
        if command == 'createGeometry' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnCreateGeometry(commandAttr, btnName))
        if command == 'lockBasicAttrs' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnLockBasicAttrs(commandAttr, btnName))
        if command == 'assignToLayer' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnAssignToLayer(commandAttr[0], commandAttr[1], btnName))
        if command == 'removeFromSet' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnRemoveFromSet(commandAttr[0], commandAttr[1], btnName))

    printTextLineSec(message, fontStyle=fontStyle)


#FUNCTIONS FOR BUTTONS:

def btnSelect(object, btn) :
    '''
    Selects an object
    '''
    cmds.select(object)

    cmds.button(btn, e=1, bgc=(0,1,0) )


def btnSelectNonUnique(object, btn) :
    '''
    selects a bunch of non-uniquely named objects
    '''
    allObjects = cmds.ls()

    cmds.select(cl=1)

    for i in allObjects :
        if object in i and '|' in i:
            cmds.select(i, add=True)

    cmds.warning('Multiple objects selected, save them to a quick selection set and rename one by one')

    cmds.button(btn, e=1, bgc=(0,1,0) )


def btnRenameNonUnique(btn, obj) :
    '''
    Automatically fixes nonUnique naming
    '''

    nonUniqueObjects = []

    allObjects = cmds.ls()
    print allObjects

    cmds.select(cl=1)

    for i in allObjects :
        if obj in i and '|' in i:
            nonUniqueObjects.append(i)

    renamed = []

    #automatically renaming all the nonUnique objects
    for n in nonUniqueObjects :
        c = 0
        newName = obj + str(c)

        while cmds.objExists(newName) :
            c += 1
            newName = obj + str(c)

        x = cmds.rename(n, newName)
        renamed.append(x)

    try :
        cmds.select(renamed)
        cmds.warning('All objects named: '+obj+' were renamed. They are now selected for your review.')
    except :
        cmds.warning('Objects named: '+obj+' were deleted. They are now selected for your review.')

    cmds.button(btn, e=1, label="FIXED", bgc=(0,1,0), enable=False )


def btnRename(object, btn) :
    '''
    Renames an object:
    '''
    result = cmds.promptDialog(
        title='Rename Object:',
        message='Enter new name for: '+object,
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel',
        text=object)

    if result == 'OK' :
        text = cmds.promptDialog(query=True, text=True)
        cmds.rename(object, text)
        cmds.button(btn, e=1, label="FIXED", bgc=(0,1,0), enable=False )


def btnDelHistory(object, btn) :
    '''
    deletes history on selected obj
    '''

    cmds.select(object)
    try :
        mel.eval('doBakeNonDefHistory( 1, {"prePost" });')
    except:
        cmds.warning('Cannot delete Non-Deformer History from: ' + object + ' It might have multiple shapes with history. Remove manually to fix!')
        cmds.button(btn, e=1, label="FAIL", bgc=(1,1,0), enable=False )
        return

    cmds.warning('Non-Deformer History deleted from: ' + object)

    #cmds.delete(object, constructionHistory=True)
    cmds.button(btn, e=1, label="FIXED", bgc=(0,1,0), enable=False )


def btnChangeColor(colorOverride, children, btn) :
    '''
    changes color of children to colorOverride
    '''

    for c in children :
        print('Setting '+c+'.overrideColor to:' + colorOverride)
        try:
            cmds.setAttr(c+'.overrideColor', int(colorOverride) )
        except:
            cmds.warning('Cannot set color for: '+c+', overrideColor attribute must be locked or connected')

    #parent is one of the children now
    #parent = cmds.listRelatives(c, parent=True)[0]
    #cmds.setAttr(parent+'.overrideColor', int(colorOverride) )

    cmds.button(btn, e=1, label="FIXED", bgc=(0,1,0), enable=False )


def btnSetNonKeyable(attrib, btn) :
    '''
    switches attribute to nonKeable
    '''

    mel.eval('setAttr -keyable false -channelBox true '+attrib+';')

    cmds.button(btn, e=1, label="FIXED", bgc=(0,1,0), enable=False )


def btnCreateNode(commandAttr, btn) :
    '''
    creates a node in a World Node
    '''
    GRP = cmds.group(name=commandAttr, empty=True)
    WRLD = cmds.ls('World_*')[0]
    cmds.parent(GRP, WRLD)

    cmds.button(btn, e=1, label="FIXED", bgc=(0,1,0), enable=False )


def btnCreateGeometry(commandAttr, btnName) :
    '''
    Creates LoRes and Proxy by duplicating existing ones
    '''

    HiRes_Geos = cmds.listRelatives("HiRes", children=True)
    LoRes_Geos = cmds.listRelatives("LoRes", children=True)


    if commandAttr == "LoRes" :
        for h in HiRes_Geos :
            l = cmds.duplicate(h, name=h.replace("_Geo", "_LoRes_Geo"))
            cmds.parent(l, "LoRes")

    if commandAttr == "Proxy" :
        for h in LoRes_Geos :
            l = cmds.duplicate(h, name=h.replace("_LoRes_Geo", "_Proxy_Geo"))
            cmds.parent(l, "Proxy")

    cmds.button(btnName, e=1, label="FIXED", bgc=(0,1,0), enable=False )


def btnLockBasicAttrs(commandAttr, btnName) :
    '''
    locks basic attributes in the mesh
    '''

    cmds.setAttr(commandAttr+".tx", lock=True)
    cmds.setAttr(commandAttr+".ty", lock=True)
    cmds.setAttr(commandAttr+".tz", lock=True)
    cmds.setAttr(commandAttr+".rx", lock=True)
    cmds.setAttr(commandAttr+".ry", lock=True)
    cmds.setAttr(commandAttr+".rz", lock=True)
    cmds.setAttr(commandAttr+".sx", lock=True)
    cmds.setAttr(commandAttr+".sy", lock=True)
    cmds.setAttr(commandAttr+".sz", lock=True)

    cmds.warning("All basic attributes on " + commandAttr + " were locked")
    cmds.select(commandAttr)

    cmds.button(btnName, e=1, label="FIXED", bgc=(0,1,0), enable=False )


def btnAssignToLayer(mesh, layer, btnName) :
    '''
    Assigns mesh to the layer:
    '''

    cmds.connectAttr(layer+".drawInfo", mesh+".drawOverride", force=True)
    cmds.warning("Mesh: " + mesh + ", assigned to layer: " + layer)

    cmds.button(btnName, e=1, label="FIXED", bgc=(0,1,0), enable=False )



def btnRemoveFromSet(theMesh, theSet, btnName) :
    '''
    Removes an object from selected set:
    '''
    cmds.warning("Mesh: " + theMesh + ", removed from set: " + theSet)
    cmds.button(btnName, e=1, label="FIXED", bgc=(0,1,0), enable=False )

    #cmds.sets( theMesh, remove=theSet )
    #print "command="+command

    command = 'sets -rm "'+theSet+'" "'+theMesh+'";'
    mel.eval(command)



#END OF FUNCTIONS FOR BUTTONS:




def printTextLineSec(message, fontStyle='plainLabelFont') :
    '''
    prints out text line in the UI while checkin asset - used in both func above
    '''
    global_vars.ITEM_INDEX +=1
    itemName = "text_"+str(global_vars.ITEM_INDEX)
    global_vars.ITEM_LIST.append(itemName)
    cmds.text(itemName, font=fontStyle, label=" "+message+"   ")

    scrollLayoutHeight = global_vars.ITEM_INDEX*18/2 - 3

    if scrollLayoutHeight > 500 :
        scrollLayoutHeight = 500

    if scrollLayoutHeight < 200 :
        scrollLayoutHeight = 200

    scrollLayout("scrollLayoutMain", edit=True, height=scrollLayoutHeight)


def set_channel_value(objects, channels):
    '''
    channels takes the form [channel, value]
    sets each channel on given object to its associated value
    '''
    for object in objects:
        for channel in channels:
            try:
                cmds.setAttr(object+'.'+channel[0], channel[1])
            except:
                print "- Cannot set "+str(object)+"."+str(channel[0]) + " to " + str(channel[1]) + " - it might be locked or connected"



def finalizeScene(*args) :
    '''
    finalizes the scene making it ready for promotion
    '''
    print("\nzeroing out all the Ctrls")

    all_controls = cmds.ls("*_Ctrl")
    all_channels = [['translateX',0],['translateY',0],['translateZ',0],['rotateX',0],['rotateY',0],['rotateZ',0],['scaleX',1],['scaleY',1],['scaleZ',1]]
    set_channel_value(all_controls, all_channels)

    print("\nsetting all the panels")

    #setting the panels:
    thePanel = cmds.getPanel( withFocus=True )
    try:
        cmds.modelEditor(thePanel, edit=True, displayAppearance='boundingBox', grid=False)
    except:
        print 'camera values not set - please give focus to an active modelView'

    #hiding all the cameras
    cameras = cmds.lsThroughFilter( cmds.itemFilter(byType='camera') )
    for c in cameras :
        transform = cmds.listRelatives(c, parent=True)[0]
        cmds.setAttr(transform+'.visibility', False)
        print('# setting ' + transform + '.visibility to False')

    #running DW cleanup script:
    print('\nRunning Dreamworks Cleanup Script')
    import DWcleanUp as DW



def choose_xml(asset_type='char') :
    '''
    allows to choose xml file from the folder in which py file is
    '''

    folder = os.path.dirname(__file__)+"\\\\"
    xmlFileList = mel.eval('$var109 = `getFileList -folder "'+folder+'" -filespec "*.xml"`;')

    if cmds.window("ACChooseXML", exists=True) :
        cmds.deleteUI("ACChooseXML")
        cmds.windowPref("ACChooseXML", removeAll=True)

    win_main = cmds.window("ACChooseXML", title="Choose XML file", iconName='ACChooseXML', sizeable=False )

    cmds.frameLayout(label="Choose XML file from list below:", borderStyle="in")

    cmds.textScrollList("txtScrlXMLList", append=xmlFileList, height=60)

    cmds.button("Load selected file", command=lambda x : loadXML(asset_type) )

    cmds.showWindow( win_main )



def loadXML(asset_type = 'char') :
    '''
    loads selected xml file into the GUI:
    '''

    selected = cmds.textScrollList("txtScrlXMLList", q=1, si=True)

    if selected == None :
        cmds.warning("Select one of the files from the list, exiting")
        cmds.deleteUI("ACChooseXML")
        cmds.windowPref("ACChooseXML", removeAll=True)
        return

    cmds.textField("txtFldXML", e=1, text=selected[0])

    cmds.deleteUI("ACChooseXML")
    cmds.windowPref("ACChooseXML", removeAll=True)


def buildXML(*args) :
    '''
    builds xml file based on selected controls:
    '''

    if cmds.window("ACBuildXml", exists=True) :
        cmds.deleteUI("ACBuildXml")
        cmds.windowPref("ACBuildXml", removeAll=True)

    win_main = cmds.window("ACBuildXml", title="Build XML file", iconName='ACBuildXml', sizeable=False )

    cmds.frameLayout(label="Enter the name of the XML file into the field below:", borderStyle="in")
    cmds.textField("txtFieldXMLFileName", text="fileName.xml", width=100)
    cmds.frameLayout(label="Select display layers you want to include below:", borderStyle="in")

    dispLayers = cmds.ls(type="displayLayer")
    dispLayers.remove("defaultLayer")
    cmds.textScrollList("txtDisplayLayers", allowMultiSelection=1, height=60, append=dispLayers)

    cmds.frameLayout(label="Select asset type below:")
    cmds.radioButtonGrp("radioGrpobjType", label='Asset Type: ', labelArray3=['Prop', 'Char', 'Other'], numberOfRadioButtons=3, columnAlign4=("left", "left", "left", "left"), columnWidth4=(75,75,75,75), select=3)

    cmds.button("Build XML file based on selection", command=buildXMLCommand)

    cmds.showWindow( win_main )


def buildXMLCommand(*args) :
    '''
    builds xml based on data:
    '''
    fileName = cmds.textField("txtFieldXMLFileName", text=True, query=True)

    fileName = fileName.replace(".XML", ".xml")
    fileName = fileName.replace(".Xml", ".xml")

    if ".xml" not in fileName :
        cmds.warning("Please include a full extension: .xml in the filename")
        return

    folder = os.path.dirname(__file__)+"\\\\"
    xmlFileList = mel.eval('$var111 = `getFileList -folder "'+folder+'" -filespec "*.xml"`;')


    #if file already exists - writing over...
    if fileName in xmlFileList :
        result = cmds.confirmDialog( title='File already exists:', message='File already exists do you want to write it over?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        if ( result == "Yes" ) :
            cmds.warning("File will be written over")
        else :
            cmds.warning("File already exists - user cancelled the script, please select another name")
            return

    #retrieving display layers:
    displayLayerList = cmds.textScrollList("txtDisplayLayers", q=1, si=1)

    cmds.warning("Building xml file: " + fileName)

    sel=cmds.ls(sl=1)

    #main variables storing info about layers, controls and nodes
    Layers = []
    Controls = []
    Nodes = []

    #here we are writing data to layers list:
    if displayLayerList != None :
        for l in displayLayerList :
            attribs = []
            attribs.append(["visibility", cmds.getAttr(l+".visibility")])
            attribs.append(["displayType", cmds.getAttr(l+".displayType")])
            attribs.append(["color", cmds.getAttr(l+".color")])
            Layers.append([l, attribs])
    else :
        cmds.warning("No layers were selected to export into XML")

    for i in sel :
        if "Ctrl" in i :
            #for Ctrls we are looking for keyable unlocked attrs
            attrs = cmds.listAttr(i, visible=True, keyable=True, unlocked=True)
            attribs = []

            for a in attrs :
                v_att = i+"."+a
                try :
                    v_val = cmds.getAttr(v_att)
                    v_type = cmds.getAttr(v_att, type=True)
                    attribs.append( [a, v_val, v_type] )
                except :
                    mc.warning("attribute: "+ v_att + " is a compound - cannot export to XML")

            Controls.append([i, attribs])
        else :
            #for nodes we are looking for settable instead of keyable
            attrs = cmds.listAttr(i, visible=True, settable=True, unlocked=True)
            attribs = []

            for a in attrs :
                v_att = i+"."+a
                try :
                    v_val = cmds.getAttr(v_att)
                    v_type = cmds.getAttr(v_att, type=True)
                    attribs.append( [a, v_val, v_type] )
                except :
                    cmds.warning("attribute: "+ v_att + " is a compound - cannot export to XML")

            Nodes.append([i, attribs])

    objectType = cmds.radioButtonGrp("radioGrpobjType", q=1, select=1)

    def enum(arg) :
        if arg == 1: return "prop"
        if arg == 2: return "char"
        if arg == 3: return "both"

    #now write all the data into an xml

    root = ET.Element('data')

    for l in Layers:
        layer = ET.SubElement(root,'layer')
        layer.set('name', l[0])
        layer.set('in', enum(objectType))

        for a in l[1] :
            attr = ET.SubElement(layer,'attribute')
            attr.set('name', str(a[0]) )
            attr.text = str(a[1])

    for c in Controls:
        control = ET.SubElement(root,'control')
        control.set('name', c[0])
        control.set('in', enum(objectType))

        for a in c[1] :
            attr = ET.SubElement(control,'attribute')
            attr.set('name', str(a[0]) )
            attr.set('type', str(a[2]) )
            attr.text = str(a[1]) #unfortunately it has to be converted to string or else XML flips...
                                  #(WE NEED CONVERSION BASED ON TYPE like Convert(a[1],a[2]))
                                  #This needs to be added tomorrow to finalize the script! Mind that if you are reading Melt :D

    #writes nodes into XML
    for n in Nodes:
        node = ET.SubElement(root,'node')
        node.set('name', n[0])
        node.set('in', enum(objectType))

        for a in n[1] :
            attr = ET.SubElement(node,'attribute')
            attr.set('name', str(a[0]) )
            attr.set('type', str(a[2]) )
            attr.text = str(a[1]) #unfortunately it has to be converted to string or else XML flips...
                                  #(WE NEED CONVERSION BASED ON TYPE like Convert(a[1],a[2]))
                                  #This needs to be added tomorrow to finalize the script! Mind that if you are reading Melt :D

    tree = ET.ElementTree(root)
    tree.write(folder+"/"+fileName)

    cmds.warning("xml file: " + fileName + " was succesfully created!")


def createAssetCheckWindow() :
    '''
    That function creates asset checking window
    '''

    #building asset checking window
    if cmds.window("AssetCheckWin", exists=True) :
        #store window position - for the sake of refreshing:
        global_vars.topLeftCorner = window("AssetCheckWin", q=1, topLeftCorner=True)

        cmds.deleteUI("AssetCheckWin")
        cmds.windowPref("AssetCheckWin", removeAll=True)

    win_main = cmds.window("AssetCheckWin", title="Asset Check Result", iconName='AssetCheckWin', sizeable=True )

    cmds.frameLayout(label="Asset Check Result", borderStyle="in", collapsable=True)
    cmds.button("REFRESH", height=20, command=commandRefresh, bgc=(0.8, 0.8, 0.5))
    cmds.scrollLayout("scrollLayoutMain", width=500, height=20, bgc=(0.2, 0.3, 0.4))
    cmds.rowColumnLayout("rowColumnLayoutMain", numberOfColumns=2, columnAlign=(2,"left"))

    #clears UI from all the previous checks - cleans it up so u can check again and again
    for each in global_vars.ITEM_LIST :
        try :
            deleteUI(each)
        except:
            pass
            #cmds.warning("Cannot delete: " + each)
    global_vars.ITEM_LIST = []
    global_vars.ITEM_INDEX = 0
    pass

    #welcome message:
    printTextLine("")
    printTextLine("... Checking current scene ...", color=GRAY, textStyle="bold")

    return win_main


def checkColorOverrides(control, colorOverride) :
    '''
    this is checking the color overrides for certain controls
    part of xml checking
    '''
    children = cmds.listRelatives(control, children=1, shapes=True)

    #we are appending control to children in order to check both transform and the shapes
    children.append(control)

    colorCorrect = True

    for c in children :
        if colorOverride != str(cmds.getAttr(c+".overrideColor")) :
            colorCorrect = False
            break

    if str(cmds.getAttr(control+".overrideColor")) != colorOverride :
        colorCorrect = False

    if colorCorrect == True :
        printTextLine("--- good: Control: \"" + control + "\" has correct color assigned to it", color=DARKGREEN, msgType="pos" )
    else :
        printTextLine("--- xxxx: Control: \"" + control + "\" has a wrong color assigned to it", color=DARKRED, msgType="neg", command='changeColor', commandAttr=(colorOverride,children) )


def checkSceneAgainstXML(xmlFileName) :
    '''
    checks the scene against an XML file:
    '''

    #determine the directory to read xml from:
    _pwd_base = os.path.dirname(__file__)
    _pwd_tree_path = _pwd_base + '/' + xmlFileName

    #loading xml
    tree = ElementTree.parse(_pwd_tree_path)
    root = tree.getroot()

    #variable storing all attributes
    all_attribs = []


    #this saves the total number of problem messages:
    NEGindex = global_vars.NEG_INDEX

    printTextLine('', msgType='info')
    printTextLine("Checking the scene against xml file: "+ xmlFileName, msgType='info', color=GRAY, textStyle="bold")

    #that part deals with display layers
    printTextLine('', msgType='info')
    printTextLine("* Checking display layers:", msgType='info', color=GRAY, textStyle="bold")

    layers_NEG = 0
    for layer in root.findall('layer') :
        layer_name = layer.get('name')

        layer_essential = layer.get('essential')
        if layer_essential == 'None' :
            layer_essential = 'True'

        if not cmds.objExists(layer_name) :
            if layer_essential == 'True' :
                printTextLine("- XXXX: Layer \"" + layer_name + "\" does not exist!", color=DARKRED, msgType="neg" )
            else :
                printTextLine("- info: Optional Layer \"" + layer_name + "\" not found", color=YELLOW, msgType="neg" )
            layers_NEG += 1
        else :
            printTextLine("- Layer: \"" + layer_name + "\" found", color=DARKGREEN, msgType="pos" )
            for attrib in layer.findall('attribute') :
                attrib_name = attrib.get('name')
                attrib_type = attrib.get('type')

                #is attribute essential?
                attrib_essential = str(attrib.get('essential'))
                if attrib_essential == 'None' :
                    attrib_essential = 'True'

                #does attribute have to be set to nonKeyable
                attrib_nonKeyable = str(attrib.get('nonKeyable'))

                if attrib_nonKeyable == 'None' :
                    attrib_nonKeyable = 'False'

                all_attribs.append([layer_name+'.'+attrib_name, attrib.text, attrib_type, attrib_essential, attrib_nonKeyable])
    if layers_NEG == 0 :
        printTextLine('- info: display layers checked', color=YELLOW, msgType='info')

    #that part deals with controls
    printTextLine("", msgType='info')
    printTextLine("* Checking controls:", msgType='info', color=GRAY, textStyle="bold")

    ctrls_NEG = 0
    for control in root.findall('control'):

        #getting name of the control
        ctrl_name = control.get('name')

        #checking if control is essential:
        ctrl_essential = str( control.get('essential') )
        if ctrl_essential == 'None' :
            ctrl_essential = 'True'

        #checking if control has color override attr:
        ctrl_overrideColor = str( control.get('overrideColor') )

        #checks if control exists if its essential it will output red msg, otherwise yellow info
        if cmds.objExists(ctrl_name) == False :
            if ctrl_essential == 'True' :
                printTextLine("- Control: \"" + ctrl_name + "\", does not exist!", color=DARKRED, msgType='neg')
            else :
                printTextLine("- Optional Control: \"" + ctrl_name + "\", does not exist", color=YELLOW, msgType='neg')
            ctrls_NEG += 1
        #if control exists - we are now checking and reading its attributes:
        else :
            for attrib in control.findall('attribute'):
                attrib_name = attrib.get('name')  #attributes name
                attrib_type = attrib.get('type')  #attributes type - we will store it to check if its right

                #attributes importance
                attrib_essential = str(attrib.get('essential'))

                if attrib_essential == 'None' :
                    attrib_essential = 'True'

                #does attribute have to be set to nonKeyable
                attrib_nonKeyable = str(attrib.get('nonKeyable'))

                if attrib_nonKeyable == 'None' :
                    attrib_nonKeyable = 'False'

                all_attribs.append([ctrl_name+'.'+attrib_name, attrib.text, attrib_type, attrib_essential, attrib_nonKeyable])

            #here we deal with colorOverride:
            if ctrl_overrideColor != 'None' :
                checkColorOverrides(ctrl_name, ctrl_overrideColor)

    #if no messages outputted then print out confirmation:
    if ctrls_NEG == 0 :
        printTextLine('- info: controls checked', color=YELLOW, msgType='info')

    #that part deals with other nodes
    printTextLine("", msgType='info')
    printTextLine("* Checking other nodes:", msgType='info', color=GRAY, textStyle='bold')

    nodes_NEG = 0
    for node in root.findall('node'):
        #getting node name:
        node_name = node.get('name')

        #checking if node is essential, assigning True if no info:
        node_essential = node.get('essential')
        if node_essential == 'None' :
            node_essential = 'True'

        #checks if node exists if its essential it will output red msg, otherwise yellow info
        if cmds.objExists(node_name) == False :
            if node_essential == 'True' :
                printTextLine("- Node: \"" + node_name + "\", does not exist!", color=DARKRED, msgType='neg')
            else :
                printTextLine("- Optional Node: \"" + ctrl_name + "\", does not exist", color=YELLOW, msgType='neg')
            nodes_NEG += 1
        #if node exists then read all the attributes and info:
        else :
            for attrib in node.findall('attribute'):
                attrib_name = attrib.get('name')
                attrib_type = attrib.get('type')

                #is attribute essential?
                attrib_essential = str(attrib.get('essential'))
                if attrib_essential == 'None' :
                    attrib_essential = 'True'

                #does attribute have to be set to nonKeyable
                attrib_nonKeyable = str(attrib.get('nonKeyable'))

                if attrib_nonKeyable == 'None' :
                    attrib_nonKeyable = 'False'

                all_attribs.append([node_name+'.'+attrib_name, attrib.text, attrib_type, attrib_essential, attrib_nonKeyable])
    if nodes_NEG == 0 :
        printTextLine('- info: nodes checked', color=YELLOW, msgType='info')

    #that part checks the attributes
    printTextLine("", msgType='info')
    printTextLine("* Checking attributes:", msgType='info', textStyle='bold', color=GRAY)

    attr_NEG = 0
    for attribute in all_attribs:
        try:
            #if attribute exists compare the value to whats in XML:
            checkVal = cmds.getAttr(attribute[0])
            if jzCompare( checkVal, attribute[1], cmds.getAttr(attribute[0], type=1) ):
                printTextLine('- good: ' + attribute[0] + ' equals ' + attribute[1], color=DARKGREEN, msgType='pos' )
            else:
                printTextLineWithButton('- XXXX: ' + attribute[0] + ' equals: ' + str(checkVal) + ' | Proper value is: ' + attribute[1], attribute[0], attribute[1])
                attr_NEG += 1
        except:
            #if attribute does not exist:
            if attribute[3] == 'True' :
                printTextLine("- XXXX: attribute: " + attribute[0] + " does not exist!", color=DARKRED, msgType='neg' )
            else :
                printTextLine("- info: optional attribute: " + attribute[0] + " not found", color=YELLOW, msgType='neg' )
                attr_NEG += 1
        else:
            #comparing attributes types if they exist:
            typeXML = str(attribute[2])
            typeReal = str(cmds.getAttr(attribute[0], type=True))
            #if XML actually contains info about the type then compare:
            if typeXML != 'None':
                if jzCompareTypes(typeXML, typeReal):
                    printTextLine("- good: Attribute type match for: " + attribute[0], color=DARKGREEN, msgType='pos' )
                else :
                    printTextLine("- XXXX: Attr type mismatch: " + typeReal + ', should be: ' + typeXML + ', for: ' + attribute[0], color=DARKRED, msgType='neg' )
            #checking if attributes are nonKeyable if thats what XML says:
            nonKeyable = str(attribute[4])

            if nonKeyable == 'True' :
                if cmds.getAttr(attribute[0], keyable=True) == False :
                    printTextLine("- good: Attribute set to nonKeyable: " + attribute[0], color=DARKGREEN, msgType='pos' )
                else :
                    printTextLine("- XXXX: Attribute needs to be set to nonKeyable: " + attribute[0], color=DARKRED, msgType='neg', command='SetNonKeyable', commandAttr=attribute[0])



    if attr_NEG == 0 :
        printTextLine('- info: attributes checked', color=YELLOW, msgType='info')


    if NEGindex == global_vars.NEG_INDEX :
        printTextLine('', msgType='info')
        printTextLine('- info: XML check completed', color=YELLOW, msgType='info')




def checkDeformers(asset_name, asset_type) :
    '''
    Function checks if deformers are named properly
    '''

    #this saves current number of outputted problem messages:
    NEGindex = global_vars.NEG_INDEX

    printTextLine('', msgType='info')
    printTextLine("Checking All Deformers:", textStyle='bold', msgType='info', color=GRAY)

    checkBendDeformersNaming(asset_name)
    checkSquashDeformersNaming(asset_name)
    checkLatticeNaming(asset_name, asset_type)
    checkClusterNaming()
    checkFolliclesNaming()
    checkJointsNaming(asset_name, asset_type)

    if NEGindex == global_vars.NEG_INDEX :
        printTextLine('', msgType='info')
        printTextLine('- info: deformers checked', color=YELLOW, msgType='info')


def checkJointsNaming(asset_name, asset_type) :
    '''
    checking joints naming
    '''
    printTextLine('', msgType='info')
    printTextLine("* Checking Joints Naming:", textStyle='bold', msgType='info', color=GRAY)

    #this saves current number of outputted problem messages:
    NEGindex = global_vars.NEG_INDEX

    allJoints = cmds.lsThroughFilter( cmds.itemFilter(byType='joint') )
    if allJoints == None :
        allJoints = []
        printTextLine("- no joints found in the file", msgType='info', color=YELLOW)

    for j in allJoints :
        if j[-4:] != '_Jnt' :
            printTextLine("- XXXX: Improper joint name (doesn't end with: _Jnt): "+j, msgType='neg', color=DARKRED, command='rename', commandAttr=j)
        else :
            printTextLine("- good: Proper joint name: "+j, msgType='pos', color=DARKGREEN)

    if asset_type == 'char' :
        charJnt_List = ['Body_Stretch_Def_01_Jnt', 'Body_Stretch_Def_02_Jnt', 'Body_Stretch_Def_03_Jnt', 'Body_Stretch_Def_04_Jnt',
            'Body_Def_Base_Jnt', 'Body_Def_01_Jnt', 'Body_Def_02_Jnt', 'Body_Def_03_Jnt', 'Body_Def_04_Jnt']

        for j in charJnt_List :
            if cmds.objExists :
                printTextLine("- good: Found character joint: "+j, msgType='pos', color=DARKGREEN)
            else :
                printTextLine("- XXXX: Character joint not found: "+j, msgType='neg', color=DARKRED)

        if cmds.objExists('Body_Stretch_Def_01_Jnt') :
            parentGrp = cmds.listRelatives('Body_Stretch_Def_01_Jnt', parent=True)[0]
            if parentGrp != 'Body_Stretch_Jnt_Grp' :
                printTextLine("- XXXX: Stretch joints group named wrong: "+parentGrp+", should be: Body_Stretch_Jnt_Grp", msgType='neg', color=DARKRED, command='rename', commandAttr=parentGrp)
            else :
                printTextLine("- good: Found properly named stretch joints grp: " + parentGrp, msgType='pos', color=DARKGREEN)

        if cmds.objExists('Body_Def_Base_Jnt') :
            parentGrp = cmds.listRelatives('Body_Def_Base_Jnt', parent=True)[0]
            if parentGrp != 'Body_Def_Jnt_Grp' :
                printTextLine("- XXXX: Body joints group named wrong: "+parentGrp+", should be: Body_Def_Jnt_Grp", msgType='neg', color=DARKRED)
            else :
                printTextLine("- good: Found properly named body joints grp: " + parentGrp, msgType='pos', color=DARKGREEN)

    #if total output of negative messages hasn't changed then print joint checked msg:
    if allJoints != [] and NEGindex == global_vars.NEG_INDEX :
        printTextLine('- info: joints checked', color=YELLOW, msgType='info')


def checkBendDeformersNaming(asset_name) :
    '''
    checking bend deformers
    '''

    #this saves current number of outputted problem messages:
    NEGindex = global_vars.NEG_INDEX

    printTextLine('', msgType='info')
    printTextLine("* Checking Bend Deformers Naming:", textStyle='bold', msgType='info', color=GRAY)
    bendDeformers = cmds.lsThroughFilter( cmds.itemFilter(byType='deformBend') )

    if bendDeformers == None :
        bendDeformers = []
        printTextLine("- no bend deformers found in the file", msgType='info', color=YELLOW)

    for d in bendDeformers :

        #we are getting the transform for the bend deformer - it should be named: _Def_Bend_Handle
        transform = cmds.listRelatives(d, parent=True)[0]

        #this is the name of the main transform for bend deformers
        properTransform = asset_name + '_Def_Bend_Handle'

        if cmds.objExists(properTransform) and transform == properTransform:
            printTextLine('- good: transform node = ' + transform, color=DARKGREEN, msgType='pos')
        else :
            if '_Def_Bend_Handle' in transform :
                printTextLine('- info: deformer: ' + transform + ' is not main bend. Main would be named: ' + properTransform, color=YELLOW, msgType='neg')
                printTextLine('- good: transform node = ' + transform, color=DARKGREEN, msgType='pos')
            else :
                printTextLine('- xxxx: transform name incorrect for = ' + transform + ', does it end with _Def_Bend_Handle?', color=DARKRED, msgType='neg', command='rename', commandAttr=transform)

        #bend deformer handle - should be same as transform but without a handle
        handle = transform.replace('_Handle','')

        if cmds.objExists(handle):
            printTextLine('- good: bend deformer handle name matches transform name = ' + handle, color=DARKGREEN, msgType='pos')
        else :
            printTextLine("- xxxx: bend deformer name doesn't match transform. (It should be: " + handle+')', color=DARKRED, msgType='neg')

        #checking if bend deformers are all placed in proper groups:
        parentGrp = transform + '_Grp'

        actualParentGrp = cmds.listRelatives(transform, parent=True)
        if actualParentGrp != None :
            actualParentGrp = actualParentGrp[0]

        if cmds.objExists(parentGrp):
            printTextLine('- good: bend deformer is in a properly named group = ' + parentGrp, color=DARKGREEN, msgType='pos')
        else :
            printTextLine("- xxxx: bend deformer parent group improper (Should be named=" + transform+'_Grp)', color=DARKRED, msgType='neg', command='rename', commandAttr=actualParentGrp)

    if bendDeformers != [] and NEGindex == global_vars.NEG_INDEX :
        printTextLine('- info: bend deformers checked', color=YELLOW, msgType='info')


def checkSquashDeformersNaming(asset_name) :
    '''
    this checks the naming for squash deformers
    '''
    #this saves current number of outputted problem messages:
    NEGindex = global_vars.NEG_INDEX

    printTextLine('', msgType='info')
    printTextLine("* Checking Squash Deformers Naming:", textStyle='bold', color=GRAY, msgType='info')
    squashDeformers = cmds.lsThroughFilter( cmds.itemFilter(byType='deformSquash') )

    if squashDeformers == None :
        squashDeformers = []
        printTextLine("- no squash deformers found in the file", msgType='info', color=YELLOW)

    for s in squashDeformers :

        #we are getting the transform for the squash deformer - it should be named: _Def_Squash_Handle
        transform = cmds.listRelatives(s, parent=True)[0]

        #this is the name of the main transform for squash deformers
        properTransform = asset_name+'_Def_Squash_Handle'

        if cmds.objExists(properTransform) and transform == properTransform:
            printTextLine('- good: transform node = ' + transform, color=DARKGREEN, msgType='pos')
        else :
            if '_Def_Squash_Handle' in transform :
                printTextLine('- info: deformer: ' + transform + ' is not main squash. Main would be named: ' + properTransform, color=YELLOW, msgType='neg')
                printTextLine('- good: transform node = ' + transform, color=DARKGREEN, msgType='pos')
            else :
                printTextLine('- xxxx: transform name incorrect for = ' + transform +', does it end with _Def_Squash_Handle?', color=DARKRED, msgType='neg', command='rename', commandAttr=transform)

        #squash deformer handle - should be same as transform but without a handle
        handle = transform.replace('_Handle','')

        if cmds.objExists(handle):
            printTextLine('- good: squash deformer handle name matches transform name = ' + handle , color=DARKGREEN, msgType='pos')
        else :
            printTextLine("- xxxx: squash deformer name doesn't match transform. (It should be: " + handle+')', color=DARKRED, msgType='neg')

        #checking if bend deformers are all placed in proper groups:
        parentGrp = transform + '_Grp'

        if cmds.objExists(parentGrp):
            printTextLine('- good: squash deformer is in a properly named group = ' + parentGrp, color=DARKGREEN, msgType='pos')
        else :
            printTextLine("- xxxx: squash deformer parent group improper (Should be named=" + transform+'_Grp)', color=DARKRED, msgType='neg')

    if squashDeformers != [] and NEGindex == global_vars.NEG_INDEX :
        printTextLine('- info: squash deformers checked', color=YELLOW, msgType='info')



def getLatticeInfo(latticeShape) :
    '''
    Gets info about a lattice
    takes:
    latticeShape node
    returns:
    * lattice transform
    * lattice base
    * lattice INP / deformer itself
    * returns lattice parent group
    '''
    conns = cmds.listConnections(latticeShape)

    latticeINP = ''
    for i in conns :
        if cmds.nodeType(i) == 'ffd' :
            latticeINP = i
            break

    lTransform = cmds.listRelatives(latticeShape, parent=1)[0]

    parentGrp = cmds.listRelatives(lTransform, parent=1)[0]

    children = cmds.listRelatives(parentGrp, children=True)

    latBase = ''
    for c in children:
        if c != lTransform :
            childList = cmds.listRelatives(c, allDescendents=True)
            for child in childList :
                if cmds.nodeType(child) == 'baseLattice' :
                    latBase = cmds.listRelatives(child, parent=True)[0]
                    break
            if latBase != '' :
                break

    result = "INP="+latticeINP+', Transform='+lTransform+', ParentGrp='+parentGrp +', latBase='+latBase

    return [lTransform, latBase, latticeINP, parentGrp]



def checkLatticeNaming(asset_name, asset_type) :
    '''
    check lattice naming:
    '''

    #this saves current number of outputted problem messages:
    NEGindex = global_vars.NEG_INDEX


    printTextLine('', msgType='info')
    printTextLine("* Checking Lattice Deformers Naming:", textStyle='bold', color=GRAY, msgType='info')

    lDeformers = cmds.lsThroughFilter( cmds.itemFilter(byType='lattice') )
    latticeDeformers = []
    #we are skipping orig nodes for lattices and lattices for the eyes because these are done in DW
    if lDeformers != None :
        for l in lDeformers :
            if not 'Orig' in l and not '_Eye_' in l :
                latticeDeformers.append(l)

    if latticeDeformers == None :
        latticeDeformers = []
        printTextLine("- no lattice deformers found in the file", msgType='info', color=YELLOW)

    for l in latticeDeformers :
        #get all the info about lattice defomer:
        latticeInfo = getLatticeInfo(l)

        transform = latticeInfo[0]

        #determine proper name for lattice transform
        properTransform = 'Body_Def_Lat'
        if asset_type != 'char' :
            properTransform  = asset_name+'_Def_Lat'

        #comparing lattice transform name to proper name
        if transform == properTransform:
            printTextLine('- good: transform node = ' + transform, color=DARKGREEN, msgType='pos')
        else :
            if 'Def_Lat' in transform :
                printTextLine('- info: deformer: ' + transform + ' is not main lattice. It would be named: ' + properTransform, color=YELLOW, msgType='neg')
                printTextLine('- good: transform node: ' + transform, color=DARKGREEN, msgType='pos')
            else :
                printTextLine('- XXXX: transform name incorrect for = ' + transform +', it should be named: *_Def_Lat', color=DARKRED, msgType='neg', command='rename', commandAttr=transform)

        #lattice deformer base:
        base = latticeInfo[1]
        properBase = transform + '_Base'

        if base == properBase:
            printTextLine('- good: lattice base matches transform name = ' + base, color=DARKGREEN, msgType='pos')
        else :
            printTextLine("- XXXX: wrong name for lattice base ("+base+"). Should be: " + properBase, color=DARKRED, msgType='neg', command='rename', commandAttr=base)

        #checking lattice deformer INPUT:
        INP = latticeInfo[2]

        if transform[-8:] == '_Def_Lat' :
            properINP = transform.replace('_Def_Lat','_Def_FFD')
        else :
            properINP = transform + '_Def_FFD'

        if INP == properINP:
            printTextLine('- good: lattice input matches transform name: ' + INP, color=DARKGREEN, msgType='pos')
        else :
            printTextLine("- XXXX: wrong name for lattice input ("+INP+"). It should be: " + properINP, color=DARKRED, msgType='neg', command='rename', commandAttr=INP)

        #checking if lattice deformers are all placed in proper groups:
        properGrp = transform + '_Grp'
        latGrp = latticeInfo[3]

        if latGrp == properGrp:
            printTextLine('- good: lattice is in a properly named group = ' + latGrp, color=DARKGREEN, msgType='pos')
        else :
            printTextLine("- XXXX: lattice not in a properly named group: " + latGrp +", it should be: " + properGrp, color=DARKRED, msgType='neg', command='rename', commandAttr=latGrp)

    if latticeDeformers != [] and NEGindex == global_vars.NEG_INDEX :
        printTextLine('- info: lattices checked', color=YELLOW, msgType='info')



def getClusterInfo(clusterObj) :
    '''
    gets info about the cluster based on its input:

    takes:
    * a cluster deformer/its input node
    returns:
    * cluster transform
    * cluster shape
    * cluster INP
    * cluster parent grp
    '''

    connInfo = cmds.connectionInfo((clusterObj+'.matrix'),sourceFromDestination=1)

    clu_transform = ""

    try :
        clu_transform = connInfo[:connInfo.index('.')]
    except :
        #in case there is a problem with a cluster try get it using clusterXforms
        cmds.warning('There is a problem with a cluster:' + clusterObj + ', it matrix attribute is not connected to anything')
        connInfo = cmds.connectionInfo((clusterObj+'.clusterXforms'),sourceFromDestination=1)
        clu_transform = cmds.listRelatives(connInfo[:connInfo.index('.')], parent=True)[0]

    clu_shape = cmds.listRelatives(clu_transform, children=True)[0]

    cluParentGrp = ""

    ClusterParents = cmds.listRelatives(clu_transform, parent=True)

    if ClusterParents == None :
        cluParentGrp == "No Parent Group"
    else :
        cluParentGrp = ClusterParents[0]

    if cluParentGrp.replace(" ", "") == "" :
        cluParentGrp = "No Parent Group"

    if "_revLoc" in cluParentGrp :
        cluParentGrp = cmds.listRelatives(cluParentGrp, parent=1)[0]

    return [clu_transform, clu_shape, clusterObj, cluParentGrp]


def checkClusterNaming() :
    '''
    checks for proper cluster naming:
    '''

    #this saves current number of outputted problem messages:
    NEGindex = global_vars.NEG_INDEX

    printTextLine("", msgType='info')
    printTextLine("* Checking Clusters Naming:", color=GRAY, textStyle='bold', msgType='info')

    clusters = cmds.lsThroughFilter( cmds.itemFilter(byType='cluster') )

    clusterParentGrps = []

    if clusters != None :
        for c in clusters :
            if "Eye_" in c or "EyeLid_Soft" in c:
                continue

            cluInfo = getClusterInfo(c)

            clusterHandle = cluInfo[0]

            if not c[-11:] == "_CluCluster":
                printTextLine('--- XXXX: cluster name improper (does not end with _CluCluster): ' + c, color=DARKGREEN, msgType='neg', command='rename', commandAttr=c )
            else :
                printTextLine('--- good: proper cluster name: ' + c, color=DARKGREEN, msgType='pos' )
            if clusterHandle[-4:] == "_Clu" :
                printTextLine('--- good: proper cluster handle name: ' + clusterHandle, color=DARKGREEN, msgType='pos')
            else :
                printTextLine('--- XXXX: cluster handle name wrong: ' + clusterHandle, color=DARKRED, msgType='neg', command='rename', commandAttr='clusterHandle' )

            clParent = cluInfo[3]

            if clParent not in clusterParentGrps :
                if clParent[-8:] != "_Clu_Grp" and "CLCluster" not in clParent and 'EyeLid_Soft' not in clParent and 'Eye_' not in clParent:
                    printTextLine('- XXXX: Cls Grp Incorrect for: ' + clusterHandle + ' (It should end with "_Clu_Grp") = ' + clParent, color=DARKRED, msgType='neg', command='rename', commandAttr=clParent)
                else :
                    printTextLine('- good: Proper Cluster Group: ' + clParent, color=DARKGREEN, msgType='pos' )

                clusterParentGrps.append(clParent)

        #now output final message if clusters were checked and no problems were found
        if NEGindex == global_vars.NEG_INDEX :
            printTextLine('- info: clusters checked', color=YELLOW, msgType='info')

    else :
        printTextLine("- no cluster deformers found in the file", msgType='info', color=YELLOW)



def checkFolliclesNaming() :
    '''
    checks naming of the follicles
    '''

    printTextLine('', msgType='info')
    printTextLine("* Checking Follicles Naming:", textStyle='bold', msgType='info', color=GRAY)
    follicles = cmds.lsThroughFilter( cmds.itemFilter(byType='follicle') )

    #this saves current number of outputted problem messages:
    NEGindex = global_vars.NEG_INDEX


    if follicles == None :
        follicles = []
        printTextLine("- no follicles found in the file", msgType='info', color=YELLOW)


    for f in follicles :
        #printTextLine("- follicle found: " + f, msgType='info')
        transform = cmds.listRelatives(f, parent=True)[0]

        if transform[-9:len(transform)] == "_Follicle" :
            printTextLine('- good: follicle named correctly = ' + transform, color=DARKGREEN, msgType='pos')
        else :
            printTextLine('- xxxx: wrongly named follicle (should end with _Follicle) = ' + transform, color=DARKRED, msgType='neg', command='rename', commandAttr=transform)

        follParent = cmds.listRelatives(transform, parent=True)[0]
        if follParent == 'Follicle_Grp' :
            printTextLine('--- good: follicle parent group correct = ' + transform + ', ' + follParent, color=DARKGREEN, msgType='pos')
        else :
            printTextLine('--- xxxx: follicle parent group incorrect (Should be Follicle_Grp) = ' + transform + ', ' + follParent, color=DARKRED, msgType='neg')

    if objExists('Follicle_Grp') :
        follDefGrp = cmds.listRelatives('Follicle_Grp', parent=True)[0]
        if follDefGrp == "Follicle_Def_Grp" :
            printTextLine('- good: follicle deformer group correct = ' + follDefGrp, color=DARKGREEN, msgType='pos')
        else :
            printTextLine('- xxxx: follicle deformer group incorrect (Should be Follicle_Def_Grp) = ' + follDefGrp + ', ' + follParent, color=DARKRED, msgType='neg')

        follicleSubGroups = []
        try :
            follicleSubGroups = cmds.listRelatives('Follicle_Def_Grp', children=True)
        except :
            printTextLine('--- xxxx: group Follicle_Def_Grp not found in the rig, please create one', color=DARKRED, msgType='neg')

        if 'Follicle_Surface_Grp' in follicleSubGroups :
            printTextLine('- good: correct follicle surface group found = ' + follDefGrp, color=DARKGREEN, msgType='pos')

            follicleSurfaces = cmds.listRelatives('Follicle_Surface_Grp', children=True)

            for fs in follicleSurfaces :
                if fs[-17:len(fs)] == '_Follicle_Surface' :
                    printTextLine('--- good: follicle surface group named correctly = ' + fs, color=DARKGREEN, msgType='pos')
                else :
                    printTextLine('--- xxxx: follicle surface group named incorrectly (should end with _Follicle_Surface) = ' + fs, color=DARKRED, msgType='neg', command="rename", commandAttr=fs)
        else :
            printTextLine('- xxxx: cannot find follicle surface group (should be named: Follicle_Surface_Grp)', color=DARKRED, msgType='neg')

    #output final message - if no negative messages were outputted:
    if follicles != [] and NEGindex == global_vars.NEG_INDEX :
        printTextLine('- info: follicles checked', color=YELLOW, msgType='info')



def checkGeometryNaming(objName, objType='prop') :

    '''
    Checks geometry naming in the rig
    '''
    printTextLine('', msgType='info')
    printTextLine('Checking Geometry naming convention in the rig!', msgType='info', color=GRAY, textStyle='bold')

    #this saves current number of outputted problem messages:
    NEGindex = global_vars.NEG_INDEX

    worldNode = "World_" + objName
    relatives = cmds.listRelatives(worldNode, children=True)

    if "Geometry" in relatives :
        printTextLine('- good: Geometry group found inside the rig', color=DARKGREEN, msgType='pos')
    else :
        printTextLine('- XXXX: Geometry group doesn\'t exist inside the rig', color=RED, msgType='none')
        printTextLine('- XXXX: Please FIX, Stopping geometry check! ', color=RED, msgType='none' )
        return

    if objType != 'set' :
        geoSubGrps = cmds.listRelatives("Geometry", children=True)

        geoGrps = ["HiRes", "LoRes", "Proxy"]

        for g in geoGrps:
            if g in geoSubGrps :

                #characters should only have Proxy and HiRes
                if objType == 'char' and g == "LoRes" :
                    printTextLine('--- XXXX: '+g+' group should not exist in geometry node for a character', color=DARKRED, msgType='neg' )
                    continue

                printTextLine('--- good: '+g+' group found inside Geometry node', color=DARKGREEN, msgType='pos' )
                testAllGeoIn(g)
            else :
                if g == "LoRes" and objType != 'char' :
                    printTextLine('--- XXXX: '+g+' group not found in Geometry node', color=DARKRED, msgType='neg' )


    #check geometry assignment to display layers and selection sets... (for props)
    try :
        HIRES = cmds.listRelatives("HiRes", children=True, shapes=False)
        LORES = cmds.ls("*LoRes_Geo")
        PROXY = cmds.ls("*Proxy_Geo")
    except :
        cmds.warning("Multiple objects are named HiRes, LoRes and Proxy, cannot continue geometry check")
        return

    if PROXY == None :
        PROXY = []
    if LORES == None :
        LORES = []

    #add shapes to the list for LORES and PROXY:
    LORESshps = []
    for l in LORES :
        shps = cmds.listRelatives(l, shapes=True)
        if shps != None :
            for s in shps :
                LORESshps.append(s)

    for l in LORESshps :
        if not "Orig" in l :
            LORES.append(l)

    PROXYshps = []
    for p in PROXY :
        shps = cmds.listRelatives(p, shapes=True)
        for s in shps :
            if not "Orig" in s :
                PROXYshps.append(s)

    for p in PROXYshps :
        PROXY.append(p)



    if objType == "prop" :
        for p in HIRES :
            if "Geo_Grp" in p :
                continue

            DispLayer = cmds.listConnections(p+".drawOverride")
            if DispLayer == None:
                DispLayer = []

            if not "Smooth" in DispLayer :
                printTextLine('--- XXXX: HiRes geo: '+p+' not assigned to "Smooth" display layer', color=DARKRED, msgType='neg', command='assignToLayer', commandAttr=[p,"Smooth"] )

        for p in LORES :
            DispLayer = cmds.listConnections(p+".drawOverride")
            if DispLayer == None:
                DispLayer = []

            if not "NoSmooth" in DispLayer :
                printTextLine('--- XXXX: LoRes geo: '+p+' not assigned to "NoSmooth" display layer', color=DARKRED, msgType='neg', command='assignToLayer', commandAttr=[p,"NoSmooth"] )

        for p in PROXY :
            DispLayer = cmds.listConnections(p+".drawOverride")
            if DispLayer == None:
                DispLayer = []

            if not "NoSmooth" in DispLayer :
                printTextLine('--- XXXX: Proxy geo: '+p+' not assigned to "NoSmooth" display layer', color=DARKRED, msgType='neg',command='assignToLayer', commandAttr=[p,"NoSmooth"] )


        #looking for n-gons on LORES
        mel.eval('polyCleanupArgList 3 { "1","2","1","0","1","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0" };')

        nGons = cmds.ls(sl=1, flatten=1)

        if nGons == [] :
            sys.stdout.write('Checked for nGons in the rig, found None...')

        allnGons = []
        for n in nGons:
            geo = n[0:n.index('.')]
            if geo in LORES :
                allnGons.append(n)
                #printTextLine('--- XXXX: nGon found in LoRes_Geo: ' + n, color=DARKRED, msgType='neg', command='select', commandAttr=n )
        if allnGons != [] :
            printTextLine('--- XXXX: nGons found in LoRes_Geo', color=DARKRED, msgType='neg', command='select', commandAttr=allnGons )
        cmds.select(cl=1)

    #check assignment to certain selection sets:
    objs = cmds.lsThroughFilter( cmds.itemFilter(byType='objectSet') )
    objectSets = []
    for o in objs :
        if "_Set" in o :
            objectSets.append(o)

    if cmds.objExists("vrayDisplacement") :
        objectSets.append("vrayDisplacement")
    else :
        printTextLine('XXXX: vrayDisplacement set not found in the rig. Check if its named correctly!', color=DARKRED, msgType='neg')

    for l in LORES :
        for o in objectSets :
            try :
                if cmds.sets(l, isMember=o) :
                    printTextLine('--- XXXX: LoRes object: '+l+' is a member of set: '+o, color=DARKRED, msgType='neg', command="removeFromSet", commandAttr=[l,o])
            except:
                cmds.warning("there is a problem with object: " + l + ", the name is not unique, skipping (can't check set membership)")

    for p in PROXY :
        for o in objectSets :
            try:
                if cmds.sets(p, isMember=o) :
                    printTextLine('--- XXXX: Proxy object: '+p+' is a member of set: '+o, color=DARKRED, msgType='neg', command="removeFromSet", commandAttr=[p,o])
            except:
                cmds.warning("there is a problem with object: " + p + ", the name is not unique, skipping (can't check set membership)")

    if len(PROXY) > 2 :
        if objType == 'prop' :
            printTextLine('--- XXXX: There is more then one proxy mesh in Proxy group - consider combining them', color=DARKRED, msgType='neg')

    #output final message:
    if NEGindex == global_vars.NEG_INDEX :
        printTextLine('- info: geometry checked', color=YELLOW, msgType='info')



def testAllGeoIn(geoGrp) :
    '''
    tests geometry pieces in the group
    '''

    #get all meshes in the group:
    allMeshes = cmds.listRelatives(geoGrp, allDescendents=True, type="mesh")

    #get all mesh transforms - remove duplicates:
    allMeshTransforms = []

    if allMeshes != None :
        for m in allMeshes :
            try :
                geoTransform = cmds.listRelatives(m, parent=True)[0]
            except :
                printTextLine('----- XXXX: multiple shapes are named same, run naming check to fix fast: ' + m, color=DARKRED, msgType='neg' )
                continue

            meshHistory = cmds.listHistory(m)
            for mh in meshHistory :
                if 'poly' in mh and 'Shape' not in mh and 'polySmooth' not in mh:
                    printTextLine('----- XXXX: mesh: '+m+ ', has undeleted history, i.e:'+mh, color=DARKRED, msgType='neg', command='deleteHistory', commandAttr=m )
                    break


            if not geoTransform in allMeshTransforms :
                allMeshTransforms.append(geoTransform)
    else :
        printTextLine('----- XXXX: No geometry found in: ' + geoGrp, color=DARKRED, msgType='neg', command="createGeometry", commandAttr=geoGrp )

    #check if geo is locked or not:

    if allMeshes != None :
        for m in allMeshes :
            unlocked = 0
            try :
                t = cmds.listRelatives(m, parent=True)[0]
            except :
                cmds.warning("There is an issue with mesh: " + m + ", multiple geo objects are named like this, skipping")
                continue

            if type(t) != "string" :
                cmds.warning("There is an issue with mesh: " + m + ", cannot determine its parent: " + str(t))
                continue

            unlocked += cmds.getAttr(t+".tx", lock=True)
            unlocked += cmds.getAttr(t+".ty", lock=True)
            unlocked += cmds.getAttr(t+".tz", lock=True)
            unlocked += cmds.getAttr(t+".rx", lock=True)
            unlocked += cmds.getAttr(t+".ry", lock=True)
            unlocked += cmds.getAttr(t+".rz", lock=True)
            unlocked += cmds.getAttr(t+".sx", lock=True)
            unlocked += cmds.getAttr(t+".sy", lock=True)
            unlocked += cmds.getAttr(t+".sz", lock=True)

            if unlocked < 9 :
                printTextLine('----- XXXX: Some basic attributes on mesh: '+t+ ', are not locked', color=DARKRED, msgType='neg', command='lockBasicAttrs', commandAttr=t )
            else :
                printTextLine('----- good: All basic attributes on mesh: '+t+ ', are locked', color=DARKGREEN, msgType='pos')

    #check the naming:

    for t in allMeshTransforms :
        if geoGrp == "HiRes" :
            if t[-4:len(t)] == '_Geo' :
                printTextLine('----- good: geometry name ends with _Geo: '+ t, color=DARKGREEN, msgType='pos' )
            else :
                printTextLine('----- XXXX: Bad geometry name. No _Geo suffix: '+ t, color=DARKRED, msgType='neg', command='rename', commandAttr=t )

        elif geoGrp == "LoRes" :
            if t[-10:len(t)] == '_LoRes_Geo' :
                printTextLine('----- good: geometry name ends with _LoRes_Geo : '+ t, color=DARKGREEN, msgType='pos' )
            else :
                printTextLine('----- XXXX: Bad geometry name. No _LoRes_Geo suffix: '+ t, color=DARKRED, msgType='neg', command='rename', commandAttr=t )

        elif geoGrp == "Proxy" :
            if t[-10:len(t)] == '_Proxy_Geo' :
                printTextLine('----- good: geometry name ends with _Proxy_Geo : '+ t, color=DARKGREEN, msgType='pos' )
            else :
                printTextLine('----- XXXX: Bad geometry name. No _Proxy_Geo suffix: '+ t, color=DARKRED, msgType='neg', command='rename', commandAttr=t )



def checkLeftAndRight() :
    '''
    Checks symmetry between left and right in characters
    '''

    #new way of discovering symmetry - working on it
    printTextLine('', msgType='info')
    printTextLine('Checking Symmetry Between Left and Right in the rig!', msgType='info', textStyle='bold', color=GRAY)

    #this saves current number of outputted problem messages:
    NEGindex = global_vars.NEG_INDEX

    L_List = cmds.ls('L_*')
    R_List = cmds.ls('R_*')

    reduced_L_list = []
    for i in L_List :
        reduced_L_list.append( i[2:] )

    reduced_R_list = []
    for i in R_List :
        reduced_R_list.append( i[2:] )

    setReduced_L_list = Set(reduced_L_list)
    setReduced_R_list = Set(reduced_R_list)

    L_no_match = setReduced_L_list.difference(setReduced_R_list)
    R_no_match = setReduced_R_list.difference(setReduced_L_list)


    def test(obj):
        '''
        tests an object in order to exlude certain nodeTypes and names
        '''
        stringsToSkip = ['ShapeOrig', 'Shape', '|']
        nodeTypesToSkip = ['parentConstraint', 'scaleConstraint', 'closestPointOnSurface', 'animCurveUU', 'decomposeMatrix', 'plusMinusAverage']

        result = True

        for s in stringsToSkip :
            if s in obj :
                return False

        for n in nodeTypesToSkip :
            if n == cmds.nodeType(obj) :
                return False

        return True


    for l in L_no_match :
        if test('L_'+l) :
            printTextLine('- XXXX: Cannot find symmetry for: L_' + l, color=DARKRED, msgType='neg', command='select', commandAttr='L_'+l )

    for r in R_no_match :
        if test('R_'+r) :
            printTextLine('- XXXX: Cannot find symmetry for: R_' + r, color=DARKRED, msgType='neg', command='select', commandAttr='R_'+r )


    #output final message:
    if NEGindex == global_vars.NEG_INDEX :
        printTextLine('- info: symmetry checked', color=YELLOW, msgType='info')



def checkDoubleNaming() :
    '''
    checks for multiple objects which are named the same
    '''
    printTextLine('', msgType='info')
    printTextLine('Checking For Non Unique Naming in the rig!', msgType='info', textStyle='bold', color=GRAY)

    #this saves current number of outputted problem messages:
    NEGindex = global_vars.NEG_INDEX

    allObjects = cmds.ls()
    nonUnique = []
    for i in allObjects :
        if '|' in i :
            j = i.split('|')[1]
            if not j in nonUnique :
                nonUnique.append(j)
                printTextLine('- XXXX: Non unique name found: ' + j, color=DARKRED, msgType='neg', command='renameNonUnique', commandAttr=j )

    #output final message:
    if NEGindex == global_vars.NEG_INDEX :
        printTextLine('- info: non unique naming checked', color=YELLOW, msgType='info')
    pass



def checkHistory() :
    '''
    checks for undeleted history on controls
    '''

    printTextLine('', msgType='info')
    printTextLine('Checking For Undeleted History On Control Objects!', msgType='info', textStyle='bold', color=GRAY)

    #this saves current number of outputted problem messages:
    NEGindex = global_vars.NEG_INDEX

    allCtrls = cmds.ls('*_Ctrl')

    shapeLst = ['nurbsCurve', 'nurbsSurface', 'transform', 'displayLayer', 'parentConstraint', 'scaleConstraint', 'joint']


    for ctrl in allCtrls :
        hist = ''
        history = cmds.listHistory(ctrl)

        for h in history :
            if not cmds.nodeType(h) in shapeLst and h != ctrl:
                hist = h
                break

        if hist != '' :
            printTextLine('- XXXX: Undeleted history found on: ' + ctrl + ',i.e: ' + hist, color=DARKRED, msgType='neg', command='deleteHistory', commandAttr=ctrl)
        else :
            printTextLine('- good: No history found on: ' + ctrl, color=DARKGREEN, msgType='pos')


    #output final message:
    if NEGindex == global_vars.NEG_INDEX :
        printTextLine('- info: history on controls checked', color=YELLOW, msgType='info')

    pass



def checkRigStructure(asset_type='prop') :
    '''
    Checks rig structure
    '''

    NEGindex = global_vars.NEG_INDEX

    printTextLine('', msgType='info')
    printTextLine('Checking Rig Structure!', color=GRAY, textStyle='bold', msgType='info')
    rigGrps = ["Controllers", "Geometry", "Texture", "Hair", "Rigging", "Lighting", "FX", "info"]

    for r in rigGrps:
        if r == 'info' and asset_type != 'char' :
            continue
        if cmds.objExists(r) :
            printTextLine('- good: '+r+' group found in the rig', color=DARKGREEN, msgType='pos' )
        else :
            printTextLine('- XXXX: '+r+' node not found in the rig', color=DARKRED, msgType='neg', command='createNode', commandAttr=r )
    pass

    #check if control groups are locked:
    allCtrls = cmds.ls('*_Ctrl')

    skipControls = ["Transform_Ctrl", "COG_Ctrl"]
    for c in allCtrls :
        if c in skipControls :
            continue

        try :
            g = cmds.listRelatives(c, parent=True)[0]
        except :
            cmds.warning("There is a problem with control: " + c + ", cannot determine its parent, skipping!")
            continue

        if "Ctrl_Grp" not in g :
            continue

        unlocked = 0

        try :
            unlocked += cmds.getAttr(g+".tx", lock=True)
            unlocked += cmds.getAttr(g+".ty", lock=True)
            unlocked += cmds.getAttr(g+".tz", lock=True)
            unlocked += cmds.getAttr(g+".rx", lock=True)
            unlocked += cmds.getAttr(g+".ry", lock=True)
            unlocked += cmds.getAttr(g+".rz", lock=True)
            unlocked += cmds.getAttr(g+".sx", lock=True)
            unlocked += cmds.getAttr(g+".sy", lock=True)
            unlocked += cmds.getAttr(g+".sz", lock=True)
        except :
            cmds.warning("Cannot determine whether: " + g + " is locked or not")
            unlocked = 9

        if unlocked < 9 :
            printTextLine('----- XXXX: Some basic attributes on control group: '+g+ ', are not locked', color=DARKRED, msgType='neg', command='lockBasicAttrs', commandAttr=g )
        else :
            printTextLine('----- good: All basic attributes on control group: '+g+ ', are locked', color=DARKGREEN, msgType='pos')

    #check if Controls_Layer exists for props (also check if there is a lighting rig since they are coDependent:
    if asset_type == 'prop' :
        Controls_Layer = cmds.objExists('Controls_Layer')
        LightRig = False
        if Controls_Layer :
            if cmds.objExists('Lighting') :
                if cmds.listRelatives('Lighting', children=True) != None :
                    LightRig = True
            else :
                printTextLine('----- XXXX: Lighting group not found in the rig under world node!', color=DARKRED )

        if Controls_Layer and not LightRig :
            printTextLine('----- XXXX: Controls_Layer exists in the rig, yet no lighting rig was found. It should be deleted.', color=DARKRED,  msgType='neg' )
        elif not Controls_Layer and LightRig :
            printTextLine('----- XXXX: Controls_Layer not found in the rig, yet a lighting rig was found. It should be created.', color=DARKRED,  msgType='neg' )
        elif Controls_Layer and LightRig :
            printTextLine('----- good: Controls_Layer exists in the rig, and relevant lighting rig was found.', color=DARKGREEN, msgType='pos' )
        elif not Controls_Layer and not LightRig :
            printTextLine('----- good: No Controls_Layer exists in the rig, nor is there a lighting rig.', color=DARKGREEN, msgType='pos' )


    if NEGindex == global_vars.NEG_INDEX :
        printTextLine('- info: rig structure checked', color=YELLOW, msgType='info' )


def checkForReferences(asset_type) :
    '''
    Checks for references in the file
    returns False if there is no references,
    returns True if there are references...
    '''

    printTextLine('', msgType='info')
    printTextLine('Checking File For References!', textStyle="bold", color=GRAY, msgType='info')

    #now here is the procedure getting the list of all references in the file:
    allReferences=[]

    references = cmds.ls(type='reference')

    # For each reference found in scene, load it with the path leading up to it replaced
    for ref in references:
        refFilePath = ''
        try :
            refFilePath = cmds.referenceQuery(ref, f=True)
        except :
            pass
            #cmds.warning('Reference was deleted for: ' + ref)
        else :
            allReferences.append(refFilePath)
            refFilename = os.path.basename( refFilePath )
            print 'Reference ' + ref + ' found at: ' + cmds.referenceQuery(ref, f=True)

    #thats for debugging:
    #print "list of references: "
    #for i in allReferences :
    #    print i

    if allReferences == [] :
        printTextLine('- good: no references found', color=DARKGREEN, msgType='pos' )
        printTextLine('- info: references checked', color=YELLOW, msgType='info' )
        return False
    else :
        if asset_type != "set" :
            printTextLine('- XXXX: references found in the file:', color=DARKRED, msgType='neg' )

            for each in allReferences :
                printTextLine('--- XXXX: improper reference: ' + each, color=DARKRED, msgType='neg')

            return False
        else :
            printTextLine('- info: There are references in the set file:', color=GRAY, msgType='neg' )

            for each in allReferences :
                printTextLine('--- info: Make sure this is a proper reference: ' + each, color=GRAY, msgType='neg')

            return False
        '''
        printTextLine('- XXXX: references found in the file, please remove them in order to continue:', color=DARKRED, msgType='neg' )

        for each in allReferences :
            printTextLine('--- XXXX: improper reference: ' + each, color=DARKRED, msgType='neg' )

        return True
        '''



def finalizeCheck( win_main ) :
    '''
    finalizes checking of the asset
    by closing the window editing mode
    and displaying it
    '''
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.showWindow( win_main )

    #set the position as the last positon of the window saved in global variables:
    cmds.window(win_main, e=1, topLeftCorner=global_vars.topLeftCorner)


def getAssetType() :
    '''
    determines asset type based on a filename - can be prop/char/set
    '''

    filePath = cmds.file(q=True, sn=True, expandName=1)
    print ('scene file='+filePath)

    if "Props" in filePath :
        return('prop')
    elif "Characters" in filePath :
        return('char')
    elif "Sets" in filePath:
        return('set')
    else :
        return('none')


def determineAssetType() :
    '''
    determines and prints the asset type prop/char/set
    '''

    assetNO=cmds.radioButtonGrp('AssetTypeRadioGRP', q=1, select=1)

    if assetNO == 1 :
        printTextLine("", msgType='info')
        printTextLine("Current scene is a Character", msgType='info', color=YELLOW)
        return('char')
    elif assetNO == 2 :
        printTextLine("", msgType='info')
        printTextLine("Current scene is a Prop", msgType='info', color=YELLOW)
        return('prop')
    else :
        printTextLine("", msgType='info')
        printTextLine("Current scene is a Set!", msgType='info', color=YELLOW)
        return('set')



def checkWorldNode() :
    '''
    looks for a world node in the asset, if it doesnt exist
    returns false otherwise true
    '''
    worldNode = None

    worldNodeLst = cmds.ls("*World_*", type='transform')

    if worldNodeLst != None and worldNodeLst != []:
        worldNode = worldNodeLst[0]

    if worldNode == None :
        return False

    return True



def determineAssetName(asset_type='none') :
    '''
    Determines asset name
    '''

    worldNode = cmds.ls("World_*", type='transform')[0]
    print "worldNode="+worldNode

    assetName = worldNode.replace("World_", '')

    printTextLine("")
    if asset_type == 'prop' :
        printTextLine("Prop Name is: " + assetName, color=YELLOW, msgType='info')
    elif asset_type == 'char' :
        printTextLine("Character Name is: " + assetName, color=YELLOW, msgType='info')
    else :
        printTextLine("Asset Name is: " + assetName, color=YELLOW, msgType='info')

    return assetName




def commandRefresh(*args) :
    '''
    That command gets executed when pressing the refresh button
    It rebuilds the window - using last saved attributes
    '''

    CheckAsset(Deformers=global_vars.Deformers, Rig_Structure=global_vars.Rig_Structure, Geometry=global_vars.Geometry, XML=global_vars.XML, References=global_vars.References, Symmetry=global_vars.Symmetry, Double_Naming=global_vars.Double_Naming, History=global_vars.History)



def CheckAsset(Deformers=False, Rig_Structure=False, Geometry=False, XML=False, References=False, Symmetry=False, Double_Naming=False, History=False) :
    '''
    That function checks an asset based on arguments we provide:
    '''

    #store last used arguments in a global variable/class
    global_vars.Deformers = Deformers
    global_vars.Rig_Structure = Rig_Structure
    global_vars.Geometry = Geometry
    global_vars.XML = XML
    global_vars.References = References
    global_vars.Symmetry = Symmetry
    global_vars.Double_Naming = Double_Naming
    global_vars.History = History
    #this is important for the sake of refresh button

    #create asset check window:
    win_main = createAssetCheckWindow()

    #determine if its a character or a prop:
    asset_type = determineAssetType()

    #grab the world node if cannot find one then exit:
    if not checkWorldNode() :
        printTextLine("", msgType='none')
        printTextLine("Can't find properly named World Node, stopping the check!", color=RED, msgType='none')
        finalizeCheck( win_main )
        return

    #print and determine asset name
    asset_name = determineAssetName(asset_type)

    #checking for references - if there are any stopping the check...
    if References == True :
        if checkForReferences(asset_type) :
            finalizeCheck( win_main )
            return

    #checking the rig structure
    if Rig_Structure == True :
        checkRigStructure(asset_type)

    #checking if deformers are named right
    if Deformers == True :
        checkDeformers(asset_name, asset_type)

    #checking geometry groups and meshes
    if Geometry == True :
        checkGeometryNaming(asset_name, asset_type)

    #checking
    if XML == True:
        checkSceneAgainstXML( cmds.textField("txtFldXML", query=1, text=1) )

    #checking symmetry:
    if Symmetry == True and asset_type=='char':
        checkLeftAndRight()

    #checking for double naming:
    if Double_Naming == True:
        checkDoubleNaming()

    #checking for undeleted history on controls:
    if History == True:
        checkHistory()

    #finalizing the check - wrapping up the result window
    finalizeCheck( win_main )


def CheckProp(*args) :
    '''
    Checks the prop
    '''
    CheckAsset(Deformers=True, Rig_Structure=True, Geometry=True, PropXML=True, CharXML=False, References=True, Symmetry=False)



def CheckChar(*args) :
    '''
    Checks the character
    '''
    CheckAsset(Deformers=True, Rig_Structure=True, Geometry=True, PropXML=False, CharXML=True, References=True, Symmetry=True)



def CheckAllSelected(*args) :
    '''
    Checks all the selected options (reads settings from checkboxes:)
    '''

    v_Deformers = cmds.checkBox("chBx_deformers", q=1, value=True)
    v_Rig_Structure = cmds.checkBox("chBx_structure", q=1, value=True)
    v_Geometry = cmds.checkBox("chBx_geometry", q=1, value=True)
    v_XML = cmds.checkBox("chBx_XML", q=1, value=True)
    v_References = cmds.checkBox("chBx_references", q=1, value=True)
    v_Symmetry = cmds.checkBox("chBx_symmetry", q=1, value=True)
    v_DNaming = cmds.checkBox("chBx_Dnaming", q=1, value=True)
    v_History = cmds.checkBox("chBx_History", q=1, value=True)

    #checks asset based on variables above:
    CheckAsset(Deformers=v_Deformers, Rig_Structure=v_Rig_Structure, Geometry=v_Geometry,
            XML=v_XML, References=v_References, Symmetry=v_Symmetry, Double_Naming=v_DNaming,
            History=v_History)



def CheckAllCheckboxes(val) :
    '''
    sets all checkboxes on and off based on the checkall
    '''

    cmds.checkBox("chBx_deformers", e=1, value=val)
    cmds.checkBox("chBx_structure", e=1, value=val)
    cmds.checkBox("chBx_geometry", e=1, value=val)
    cmds.checkBox("chBx_XML", e=1, value=val)
    cmds.checkBox("chBx_references", e=1, value=val)
    cmds.checkBox("chBx_symmetry", e=1, value=val)
    cmds.checkBox("chBx_Dnaming", e=1, value=val)
    cmds.checkBox("chBx_History", e=1, value=val)



def assetTypeSwitched(*args) :
    assetType = cmds.radioButtonGrp("AssetTypeRadioGRP", q=1, select=1)
    #cmds.warning("asset type was switched to" + str(assetType))

    if assetType==1:
        cmds.checkBox("chBx_symmetry", e=1, enable=1)
        cmds.button("checkNowSYM", e=1, enable=1)
        cmds.textField("txtFldXML", e=1, text='character.xml')
    if assetType==2:
        cmds.checkBox("chBx_symmetry", e=1, enable=0)
        cmds.button("checkNowSYM", e=1, enable=0)
        cmds.textField("txtFldXML", e=1, text='prop.xml')
    if assetType==3:
        cmds.checkBox("chBx_symmetry", e=1, enable=0)
        cmds.button("checkNowSYM", e=1, enable=0)
        cmds.textField("txtFldXML", e=1, text='set.xml')




def showUI() :
    '''
    displays basic UI for the tool
    '''

    if cmds.window("ACChooseXML", exists=True) :
        cmds.deleteUI("ACChooseXML")
        cmds.windowPref("ACChooseXML", removeAll=True)

    if cmds.window("AssetCheckerWin", exists=True) :
        cmds.deleteUI("AssetCheckerWin")
        cmds.windowPref("AssetCheckerWin", removeAll=True)

    if cmds.window("AssetCheckWin", exists=True) :
        cmds.deleteUI("AssetCheckWin")
        cmds.windowPref("AssetCheckWin", removeAll=True)

    if cmds.window("ACBuildXml", exists=True) :
        cmds.deleteUI("ACBuildXml")
        cmds.windowPref("ACBuildXml", removeAll=True)

    win_main = cmds.window("AssetCheckerWin", title="Asset Checker Window", iconName='AssetCheckerWin', sizeable=False )

    cmds.frameLayout(label="Asset Checker Window", borderStyle="in")
    cmds.rowColumnLayout(numberOfColumns=4)

    cmds.checkBox("chBx_deformers", label="Deformers", v=1)
    cmds.text(label=" ")
    cmds.text(label=" ")
    cmds.button("check now", command=lambda x: CheckAsset(Deformers=1, Rig_Structure=0, Geometry=0, XML=0, References=0, Symmetry=0))

    cmds.checkBox("chBx_structure", label="Rig Structure", v=1)
    cmds.text(label=" ")
    cmds.text(label=" ")
    cmds.button("check now", command=lambda x: CheckAsset(Deformers=0, Rig_Structure=1, Geometry=0, XML=0, References=0, Symmetry=0))

    cmds.checkBox("chBx_geometry", label="Geometry", v=1)
    cmds.text(label=" ")
    cmds.text(label=" ")
    cmds.button("check now", command=lambda x: CheckAsset(Deformers=0, Rig_Structure=0, Geometry=1, XML=0, References=0, Symmetry=0))

    cmds.checkBox("chBx_XML", label="Attributes", v=1)
    cmds.button(label="...", command=lambda x : choose_xml(asset_type="char") )
    cmds.textField("txtFldXML", width=175, text='character.xml', enable=False)
    cmds.button("check now", command=lambda x: CheckAsset(Deformers=0, Rig_Structure=0, Geometry=0, XML=1, References=0, Symmetry=0))

    cmds.checkBox("chBx_references", label="References", v=1)
    cmds.text(label=" ")
    cmds.text(label=" ")
    cmds.button("check now", command=lambda x: CheckAsset(Deformers=0, Rig_Structure=0, Geometry=0, XML=0, References=1, Symmetry=0))

    cmds.checkBox("chBx_symmetry", label="Symmetry", v=1)
    cmds.text(label=" ")
    cmds.text(label=" ")
    cmds.button("checkNowSYM", label="check now", command=lambda x: CheckAsset(Deformers=0, Rig_Structure=0, Geometry=0, XML=0, References=0, Symmetry=1))

    cmds.checkBox("chBx_Dnaming", label="Names Issues", v=1)
    cmds.text(label=" ")
    cmds.text(label=" ")
    cmds.button("checkNowDnaming", label="check now", command=lambda x: CheckAsset(Deformers=0, Rig_Structure=0, Geometry=0, XML=0, References=0, Symmetry=0, Double_Naming=1))

    cmds.checkBox("chBx_History", label="History", v=1)
    cmds.text(label=" ")
    cmds.text(label=" ")
    cmds.button("checkNowHistory", label="check now", command=lambda x: CheckAsset(Deformers=0, Rig_Structure=0, Geometry=0, XML=0, References=0, Symmetry=0, Double_Naming=0, History=1))


    cmds.separator()
    cmds.separator()
    cmds.separator()
    cmds.separator()

    cmds.checkBox("Check All", onCommand=lambda x: CheckAllCheckboxes(True), offCommand=lambda x: CheckAllCheckboxes(False), v=1)
    cmds.text(label=" ")
    cmds.text(label=" ")
    cmds.button("check now", command=lambda x: CheckAsset(Deformers=1, Rig_Structure=1, Geometry=1, XML=1, References=1, Symmetry=1, Double_Naming=1, History=1) )

    cmds.separator()
    cmds.separator()
    cmds.separator()
    cmds.separator()

    cmds.setParent("..")
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=4)

    cmds.checkBox("List Only Problems", width=110, value=True, onCommand=lambda a : setGlobal('POS', False), offCommand = lambda d : setGlobal('POS', True) )
    cmds.text(label=" ")
    cmds.text(label="                              Asset Type:    ")
    cmds.radioButtonGrp("AssetTypeRadioGRP", labelArray3=['Character', 'Prop', 'Set'], numberOfRadioButtons=3, vertical=True, changeCommand=assetTypeSwitched)

    cmds.setParent("..")
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=2)

    cmds.separator()
    cmds.separator()

    cmds.button("Run Checks", width=172, command=CheckAllSelected, bgc=RGB01(0,162,22))
    cmds.button(label="Finalize Scene", width=172, command=finalizeScene, bgc=RGB01(162,0,22))
    cmds.setParent("..")

    #adjusting ui to proper window settings:
    assetType = getAssetType()
    if assetType == 'char' :
        cmds.radioButtonGrp("AssetTypeRadioGRP", e=1, select=1)
    elif assetType == 'prop' :
        cmds.radioButtonGrp("AssetTypeRadioGRP", e=1, select=2)
    elif assetType == 'set' :
        cmds.radioButtonGrp("AssetTypeRadioGRP", e=1, select=3)
    else:
        cmds.warning("Cannot determine asset type!")

        def DialogGetUserChoice(*args):
            var = cmds.radioButtonGrp("AssetTypeRadioGRPDialog", query=1, select=1)
            result = '3:set'
            if var == 1 :
                result='1:char'
            elif var == 2 :
                result='2:prop'

            cmds.layoutDialog(dismiss=result)


        def radioPrompt() :
            # Get the dialog's formLayout.
            form = cmds.setParent(q=True)
            # layoutDialog's are not resizable, so hard code a size here,
            # to make sure all UI elements are visible.
            cmds.formLayout(form, e=True, width=300)
            t = cmds.text(l='Cannot auto-detect asset type. Please choose it manually:')
            spacer = cmds.text(l='')
            rgrp = cmds.radioButtonGrp("AssetTypeRadioGRPDialog", labelArray3=['Character', 'Prop', 'Set'], numberOfRadioButtons=3, vertical=True, select=1)
            btnOK = cmds.button('DialogOK', label='OK', command=DialogGetUserChoice)
            cmds.formLayout(form, edit=True,
                attachForm=[(t, 'top', 10), (t, 'left', 10), (rgrp, 'top', 30), (rgrp, 'left', 5), (btnOK, 'top', 90), (btnOK, 'left', 110), (spacer, 'top', 110)] )

        assetType = cmds.layoutDialog(ui=radioPrompt)
        print "# User Selected: " + assetType
        if assetType == 'dismiss' :
            assetType = '1'

        cmds.radioButtonGrp("AssetTypeRadioGRP", e=1, select=int(assetType[0:1]))

    assetTypeSwitched()

    cmds.showWindow( win_main )
    global_vars.MAIN_WIN = win_main

showUI()
