import maya.cmds as cmds
from pymel.core import * # for the file handling
import os
import xml.etree.ElementTree as ElementTree
from sets import Set


#class defining what is allowed and what is not allowed for an asset type...
class AssetType() :
    name = ''
    referencesAllowed = False
    rigStructureXMLTree = None
    rigStructureXMLRoot = None

    def __init__ (self, assetName) :
        self.name = assetName
        asset_structure_xml_path = os.path.dirname(__file__) + '/AssetData/' + assetName + '/' + "rig_structure.xml"

        print 'AssetXMLStructureFile='+asset_structure_xml_path

        #if xml file does not exists then use default basic one:
        if not os.path.exists(asset_structure_xml_path) :
            cmds.warning('AssetChecker-->Cannot find rig_structure.xml for asset type: ' + assetName + ', using default file...')
            asset_structure_xml_path = os.path.dirname(__file__) + '/AssetData/Default/rig_structure.xml'

        #read xml from that file:
        try:
            self.rigStructureXMLTree = ElementTree.parse(asset_structure_xml_path)
        except:
            cmds.error('AssetChecker-->rig_structure.xml for asset type: ' + assetName + ', is invalid... stopping the checker.')

        #now getting the root:
        self.rigStructureXMLRoot = self.rigStructureXMLTree.getroot()


#class defining AssetChecker rules - it will all be eventually loaded from XML or textFile (ACRules stands for Asset Checker Rules):
class ACRules() :

    def __init__ (self) :
        #defines main node substring...
        self.mainNode_Substr = 'World_'

        #here declare the list of asset types as a list []
        self.AssetTypes=[]

        #list containing asset types...

        #definition of PROP asset type:
        prop = AssetType('prop')
        prop.referencesAllowed = False

        #definition of CHARACTER asset type:
        char = AssetType('char')
        char.referencesAllowed = False

        #definition of SET asset type:
        aset = AssetType('set')
        aset.referencesAllowed = True

        self.AssetTypes.append(prop)
        self.AssetTypes.append(char)
        self.AssetTypes.append(aset)


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


#declare global variable containing all the rules for AssetChecker - ACR - asset checker rules...
ACR = ACRules()


def setGlobal(var, val):
    '''
    Sets global variables accordingly with checkboxes - for printing msgs
    '''

    #messages which this tool outputs will be divided in 3 categories:
    # "info", "neg" and "pos" - neutral, negative, positive

    if var == "INFO" :
        global_vars.INFO = val
    if var == "NEG" :
        global_vars.NEG = val
    if var == "POS" :
        global_vars.POS = val



def RGB01(R,G,B) :
    '''
    Converts 255,255,255 RGB to normalized 1,1,1 one :)
    '''
    r = float(R/255.0)
    g = float(G/255.0)
    b = float(B/255.0)

    return (r,g,b)


#some constants/ global variables - color values for messages:
DARKGREEN = RGB01(0, 100, 0)
DARKRED = RGB01(100, 0, 0)
GRAY = RGB01(100,100,100)
YELLOW = RGB01(100,100,0)
RED = RGB01(255,0,0)



def removeDuplicates(mylist):
    '''
    removes duplicates from a list
    '''
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
    '''
    compares attributes based on their type:
    '''

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
    makes a default button for fixing wrong attributes
    '''

    #flush the output:
    sys.stdout.write('')

    attr_type = cmds.getAttr(attr, type=True)
    converted_value = jzConvert(val, attr_type)

    try :
        cmds.setAttr( attr, converted_value )
    except :
        cmds.warning("\nAssetChecker-->Unable to set " + attr + " to " + str(val) + " - it might be locked or hidden\n")
        cmds.button(btnName, edit=True, bgc=(1,1,0), label="FAIL")
    else:
        sys.stdout.write("\nAssetChecker-->Attribute: "+attr+" successfully set to: "+val+"\n")
        cmds.button(btnName, edit=True, bgc=(0,1,0), label="FIXED", enable=False)



def printTextLineWithButton(message, attribute, value) :
    '''
    outputs a text line into the UI while checking asset
    also puts a default button next to the text
    '''

    #if printing negative messages is off then exit
    if global_vars.NEG == False :
        return

    global_vars.ITEM_INDEX +=1
    btnName = "btn_"+str(global_vars.ITEM_INDEX)
    global_vars.ITEM_LIST.append(btnName)
    cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnFIX(btnName, attribute, value))

    printTextLineSec(message)

    global_vars.NEG_INDEX += 1



def printTextLine(message, color=None, textStyle="none", msgType='none', command='none', commandAttr='none') :
    '''
    outputs a text line into the UI while checking asset, if command != 'none' it creates a button for fixing:
    takes 1 argument (nonoptional) - message is the message that will be printed
    5 optional arguments:
    color - bg color (R,G,B)
    textStyle - plain or bold
    msgType - none, info, neg, pos
    command - button command for fixing the problem
    commandAttr - if button command needs an attribute thats where its passed
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

        #button command - select
        if command == 'select' :
            cmds.button(btnName, bgc=(1,0,0), label="select", width=35, height=14, command=lambda x:btnSelect(commandAttr, btnName))

        #button command - select non uniquely named objects
        if command == 'selectNonUnique' :
            cmds.button(btnName, bgc=(1,0,0), label="select", width=35, height=14, command=lambda x:btnSelectNonUnique(commandAttr, btnName))

        #button command - automatically rename non uniquely named objects, right click - select them
        if command == 'renameNonUnique' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnRenameNonUnique(obj=commandAttr, btn=btnName))
            cmds.popupMenu()
            cmds.menuItem("rename non unique objects", command=lambda x:btnRenameNonUnique(obj=commandAttr, btn=btnName))
            cmds.menuItem("select non unique objects", command=lambda x:btnSelectNonUnique(commandAttr, btnName))

        #button command - rename an object, right click - select it
        if command == 'rename' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnRename(commandAttr, btnName))
            cmds.popupMenu()
            cmds.menuItem("rename object", command=lambda x:btnRename(commandAttr, btnName))
            cmds.menuItem("select object", command=lambda x:btnSelect(commandAttr, btnName))

        #button command - delete history from objects (nonDeformer)
        if command == 'deleteHistory' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnDelHistory(commandAttr, btnName))

        #button command - change objects color override
        if command == 'changeColor' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnChangeColor(commandAttr[0], commandAttr[1], btnName))

        #button command - sets attribute to nonKeyable
        if command == 'SetNonKeyable' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnSetNonKeyable(commandAttr, btnName))

        #button command - creates a node (rig structure)
        if command == 'createNode' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnCreateNode(commandAttr, btnName))

        #button command - create a node and parent it under another node (rig structure)
        if command =='createNodeUnder' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnCreateNodeUnder(commandAttr, btnName))

        #button command - creates geometry (for loRes and proxy version)
        if command == 'createGeometry' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnCreateGeometry(commandAttr, btnName))

        #button command - locks basic attributes on object
        if command == 'lockBasicAttrs' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnLockBasicAttrs(commandAttr, btnName))

        #button command - assigns object to a display layer
        if command == 'assignToLayer' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnAssignToLayer(commandAttr[0], commandAttr[1], btnName))

        #button command - removes object from specified selection set
        if command == 'removeFromSet' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnRemoveFromSet(commandAttr[0], commandAttr[1], btnName))

        #button command - offers selecting ngons or fixing them by tesselation
        if command == 'selectFixByTesselation' :
            cmds.button(btnName, bgc=(1,0,0), label="select", width=35, height=14, command=lambda x:btnSelect(commandAttr, btnName))
            cmds.popupMenu()
            cmds.menuItem('Fix all nGons by tessellation', command=lambda x:btnFixByTessellation(commandAttr, btnName))

        #button command - delete layer
        if command == 'deleteLayer' :
            cmds.button(btnName, bgc=(1,0,0), label="delete", width=35, height=14, command=lambda x:btnDeleteLayer(commandAttr, btnName))

        #button command - combine proxy geo
        if command == 'combineGeo' :
            cmds.button(btnName, bgc=(1,0,0), label="FIX", width=35, height=14, command=lambda x:btnCombineGeo(commandAttr, btnName))


    #now function outputs a message next to button (if button was created)
    printTextLineSec(message, fontStyle=fontStyle)


#DEFINITIONS OF FUNCTIONS FOR BUTTONS:

def btnSelect(obj, btn) :
    '''
    Selects an object
    '''

    #clears output
    sys.stdout.write('')

    if str(type(obj)) != "<type 'list'>" :
        if cmds.objExists(obj) :
            cmds.select(obj)
            cmds.button(btn, e=1, bgc=(0,1,0) )
            sys.stdout.write("AssetChecker --> object: " + str(obj) + " is selected!")
        else  :
            cmds.warning("AssetChecker --> object: " + str(obj) + " no longer exists!")
            cmds.button(btn, e=1, bgc=(1,0,0) )
    else :
        cmds.select(cl=1)
        for i in obj :
            if cmds.objExists(i) :
                cmds.select(i, add=True)
            else  :
                cmds.warning("AssetChecker --> object: " + str(obj) + " no longer exists!")
                cmds.button(btn, e=1, bgc=(1,0,0) )
                return

        sys.stdout.write("AssetChecker --> object: " + str(obj) + " is selected!")

        cmds.button(btn, e=1, bgc=(0,1,0) )


def btnSelectNonUnique(obj, btn) :
    '''
    Selects a bunch of non-uniquely named objects
    '''

    #clears output
    sys.stdout.write('')

    allObjects = cmds.ls()

    cmds.select(cl=1)

    for i in allObjects :
        if obj in i and '|' in i:
            cmds.select(i, add=True)

    sys.stdout.write("AssetChecker --> multiple objects named: " + obj + " selected, save them to a quick selection set and rename one by one")

    cmds.button(btn, e=1, bgc=(0,1,0) )


def btnRenameNonUnique(btn, obj) :
    '''
    Automatically fixes nonUnique naming
    '''

    #clears output
    sys.stdout.write('')

    #gets a list of nonUnique objects - (bases it on appearance of string '|' in the name)
    nonUniqueObjects = []

    allObjects = cmds.ls()
    for i in allObjects :
        if obj in i and '|' in i:
            nonUniqueObjects.append(i)


    #list of objects that were renamed
    renamed = []

    #automatically renaming all the nonUnique objects by adding a number to them
    #(could be improved - numbers should be placed before important suffixes )
    for n in nonUniqueObjects :

        #before renaming checking if the object exists - might have been deleted:
        if not cmds.objExists(n) :
            cmds.warning("AssetChecker --> object: " + n + " was deleted, cannot rename... skipping")
            continue

        c = 0
        newName = obj + str(c)

        #we are determining if the name is available if not we increase the number
        while cmds.objExists(newName) :
            c += 1
            newName = obj + str(c)

        #rename the object if it exists and append to the list of renamed objects
        x = cmds.rename(n, newName)
        renamed.append(x)

    try :
        cmds.select(renamed)
        sys.stdout.write('AssetChecker--> All objects named: '+obj+' were renamed. They are now selected for your review.')
    except :
        cmds.warning('AssetChecker--> Objects named: '+obj+' were deleted... Cannot select')
        cmds.button(btn, edit=True, bgc=(1,1,0), label="FAIL", enable=False)
    else :
        #switch button label to fixed:
        cmds.button(btn, e=1, label="FIXED", bgc=(0,1,0), enable=False )



def btnRename(obj, btn) :
    '''
    Renames an object:
    '''

    #clears output
    sys.stdout.write('')

    #outputs a prompt for renaming - putting in the name that was there before
    result = cmds.promptDialog(
        title='Rename Object:',
        message='Enter new name for: '+obj,
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel',
        text=obj)

    #if user clicked ok - go on with renaming (if object exists):
    if result == 'OK' :
        if cmds.objExists(obj) :
            text = cmds.promptDialog(query=True, text=True)
            cmds.rename(obj, text)
            cmds.button(btn, e=1, label="FIXED", bgc=(0,1,0), enable=False )
        else :
            cmds.warning("AssetChecker--> Object: '+obj+' doesn't exist, cannot rename")
            cmds.button(btn, edit=True, bgc=(1,1,0), label="FAIL", enable=False)

    #output success message
    sys.stdout.write('AssetChecker--> Object: '+obj+' renamed to: ' + text)


def btnDelHistory(obj, btn) :
    '''
    deletes history on selected obj
    '''

    #clears output
    sys.stdout.write('')

    cmds.select(obj)
    try :
        mel.eval('doBakeNonDefHistory( 1, {"prePost" });')
    except:
        cmds.warning('AssetChecker--> Cannot delete Non-Deformer History from: ' + obj + ' It might have multiple shapes with history. Remove manually to fix!')
        cmds.button(btn, e=1, label="FAIL", bgc=(1,1,0), enable=False )
        return

    sys.stdout.write('AssetChecker--> Non-Deformer History deleted from: ' + obj)

    #set the button to FIXED mode
    cmds.button(btn, e=1, label="FIXED", bgc=(0,1,0), enable=False )


def btnChangeColor(colorOverride, children, btn) :
    '''
    changes color of children to colorOverride
    '''

    #clears output
    sys.stdout.write('')

    successList = ""

    for c in children :
        print('Setting '+c+'.overrideColor to:' + colorOverride)
        try:
            cmds.setAttr(c+'.overrideColor', int(colorOverride) )
            successList += c + ", "
        except:
            cmds.warning('AssetChecker--> Cannot set color for: '+c+', overrideColor attribute must be locked or connected')

    sys.stdout.write('AssetChecker--> Color set to: ' + colorOverride + ' for objects: ' + successList)

    #set button to fixed state:
    cmds.button(btn, e=1, label="FIXED", bgc=(0,1,0), enable=False )


def btnSetNonKeyable(attrib, btn) :
    '''
    switches attribute to nonKeable
    '''

    #clears output
    sys.stdout.write('')

    try :
        mel.eval('setAttr -keyable false -channelBox true '+attrib+';')
    except:
        cmds.warning('AssetChecker--> Cannot set attribute to non-keyable: '+attrib+', must be locked')
        cmds.button(btn, edit=True, bgc=(1,1,0), label="FAIL", enable=False)
    else:
        sys.stdout.write('AssetChecker--> Attribute set to non-keyable: '+attrib)
        cmds.button(btn, edit=True, bgc=(0,1,0), label="FIXED", enable=False)
        #... setting your button to FIXED state ...


def btnCreateNode(commandAttr, btn) :
    '''
    creates a node in a World Node
    '''

    #clears output:
    sys.stdout.write('')

    #creating a node and parenting it under the world node (this could be revised)
    GRP = cmds.group(name=commandAttr, empty=True)
    WRLD = cmds.ls('World_*')[0]
    cmds.parent(GRP, WRLD)

    #output success message:
    sys.stdout.write('AssetChecker--> Node '+GRP+' created and parented under: ' + WRLD)

    cmds.button(btn, e=1, label="FIXED", bgc=(0,1,0), enable=False )


def btnCreateNodeUnder(commandAttr, btn) :
    '''
    creates a node and parents it under another specified node
    '''

    #clears output:
    sys.stdout.write('')

    #creating a node and parenting it under another specified node
    GRP = cmds.group(name=commandAttr[0], empty=True)
    cmds.parent(GRP, commandAttr[1])

    #output success message:
    sys.stdout.write('AssetChecker--> Node '+GRP+' created and parented under: ' + commandAttr[1])

    cmds.button(btn, e=1, label="FIXED", bgc=(0,1,0), enable=False )



def btnCreateGeometry(commandAttr, btnName) :
    '''
    Creates LoRes and Proxy by duplicating existing ones
    '''

    #declare inner function for renaming...
    def renameAllChildren(GRPname, renameTo) :
        '''
        this is a recurrence function
        which renames all geos or runs itself again for a
        group'''


        #clears output:
        sys.stdout.write('')

        #get children of the group
        children = cmds.listRelatives(GRPname, children=True, fullPath=True)

        #if specified object has children...
        if children != None :
            for c in children :
                #now strip the long path, but keep it in memory for renaming...
                original_c = c

                if '|' in c :
                    c = c[c.rindex('|')+1:]

                #renaming geometry - if child is a geometry transform object...
                if c[-4:] == "_Geo" :
                    new_c = c
                    if "LoRes_Geo" in c :
                        new_c = c.replace("_LoRes_Geo", "_" + renameTo + "_Geo")
                    else :
                        new_c = c.replace("_Geo", "_" + renameTo + "_Geo")
                    cmds.rename(original_c, new_c)
                else :
                    new_c = c

                    #renaming geometry groups (as long as they are proper)
                    if "LoRes_Geo_Grp" in c :
                        new_c = c.replace('LoRes_Geo_Grp', renameTo+'_Geo_Grp')
                        cmds.rename(original_c, new_c)
                    elif "Geo_Grp" in c :
                        new_c = c.replace('Geo_Grp', renameTo+'_Geo_Grp')
                        cmds.rename(original_c, new_c)

                    #recurrence call of the same function...
                    renameAllChildren(new_c, renameTo)


    #duplicate geometry
    Duplicate = ''
    if commandAttr == "LoRes" :
        Duplicate = cmds.duplicate("HiRes", name="Duplicate")[0]
    elif commandAttr == "Proxy" :
        Duplicate = cmds.duplicate("LoRes", name="Duplicate")[0]

    #execute recurrence function to rename all children in duplicate...
    renameAllChildren(Duplicate, commandAttr)

    #now parent all the contents of the Duplicate Group Under Proper Geometry Group:
    children = cmds.listRelatives(Duplicate, children=True)

    for c in children :
        cmds.parent(c, commandAttr)

    #to finish delete the duplicate group in the end...
    cmds.delete(Duplicate)

    #output success message:
    source = ''
    if commandAttr == "LoRes" :
        source = "HiRes"
    elif commandAttr == "Proxy" :
        source = "LoRes"

    sys.stdout.write('AssetChecker--> '+commandAttr+' geometry was successfully created by duplicating and renaming '+source+' geometry!')

    #set button state to FIXED
    cmds.button(btnName, e=1, label="FIXED", bgc=(0,1,0), enable=False )



def btnLockBasicAttrs(commandAttr, btnName) :
    '''
    locks basic attributes in the mesh or some other thing
    '''

    #clears output:
    sys.stdout.write('')

    try :
        cmds.setAttr(commandAttr+".tx", lock=True)
        cmds.setAttr(commandAttr+".ty", lock=True)
        cmds.setAttr(commandAttr+".tz", lock=True)
        cmds.setAttr(commandAttr+".rx", lock=True)
        cmds.setAttr(commandAttr+".ry", lock=True)
        cmds.setAttr(commandAttr+".rz", lock=True)
        cmds.setAttr(commandAttr+".sx", lock=True)
        cmds.setAttr(commandAttr+".sy", lock=True)
        cmds.setAttr(commandAttr+".sz", lock=True)
    except :
        cmds.warning('AssetChecker--> Cannot lock attributes on '+commandAttr+'. Check if the object still exists!')
        cmds.button(btnName, edit=True, bgc=(1,1,0), label="FAIL", enable=False)
    else :
        #output success message:
        sys.stdout.write('AssetChecker--> All basic attributes on '+commandAttr+' were successfully locked!')
        #set button to fixed state:
        cmds.button(btnName, e=1, label="FIXED", bgc=(0,1,0), enable=False )



def btnAssignToLayer(mesh, layer, btnName) :
    '''
    Assigns mesh to the layer:
    '''

    #clears output:
    sys.stdout.write('')

    #first check if object exists:
    if cmds.objExists(mesh) :
        cmds.connectAttr(layer+".drawInfo", mesh+".drawOverride", force=True)
        sys.stdout.write('AssetChecker--> Mesh: ' + mesh + ', assigned to layer: ' + layer)
        #set button state:
        cmds.button(btnName, e=1, label="FIXED", bgc=(0,1,0), enable=False )
    else :
        cmds.warning("AssetChecker--> Mesh: " + mesh + ", no longer exists, exiting")
        cmds.button(btnName, e=1, label="FAIL", bgc=(1,1,0), enable=False )


def btnRemoveFromSet(theMesh, theSet, btnName) :
    '''
    Removes an object from selected set:
    '''

    #clears output:
    sys.stdout.write('')

    if cmds.objExists(theMesh) :
        command = 'sets -rm "'+theSet+'" "'+theMesh+'";'
        mel.eval(command)

        cmds.button(btnName, e=1, label="FIXED", bgc=(0,1,0), enable=False )
        sys.stdout.write('AssetChecker--> Mesh: ' + theMesh + ', successfully removed from set: ' + theSet)
    else :
        cmds.warning("AssetChecker--> Mesh: " + theMesh + ", no longer exists, exiting")
        cmds.button(btnName, e=1, label="FAIL", bgc=(1,1,0), enable=False )


def btnFixByTessellation(nGons, btnName) :
    '''
    Fixes specified ngons by tessellation
    '''
    #clears output
    sys.stdout.write('')

    cmds.select(nGons)
    mel.eval('polyCleanupArgList 3 { "1","1","1","0","1","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0" };')
    mel.eval('polyCleanupArgList 3 { "0","1","1","0","1","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0" };')

    outputNGons = ''

    for n in nGons : outputNGons += n + " "

    sys.stdout.write("AssetChecker --> Following ngons were fixed by tessellation: " + outputNGons)

    cmds.button(btnName, e=1, bgc=(0,1,0) )



def btnDeleteLayer(layerName, btnName) :
    '''
    Deletes specified display layer
    '''
    #clears output
    sys.stdout.write('')

    cmds.delete(layerName)

    #set the button to FIXED:
    cmds.button(btnName, e=1, label="FIXED", bgc=(0,1,0), enable=False )

    #final output
    sys.stdout.write("AssetChecker --> Following layer was deleted: " + layerName)


def btnCombineGeo(GEOS, btnName) :
    '''
    Combines geos in the specified list
    '''
    #clears output
    sys.stdout.write('')

    #filter GEOS so that we only get the transform nodes - no shapes:
    GEOS = [g for g in GEOS if cmds.nodeType(g) == "transform"]

    cmds.select(GEOS)

    #get the parent where to parent combined geo under:
    theParent = cmds.listRelatives(GEOS[0], parent=True)

    #now combine:
    combined=cmds.polyUnite(GEOS, ch=1, mergeUVSets=1)[0]
    cmds.parent(combined, theParent)

    #delete history:
    cmds.select(combined)
    mel.eval('DeleteHistory;')

    #now prompt dialog to set a name for the object, and rename it...
    result = cmds.promptDialog(
            title='Enter Name:',
            message='Enter new name for combined object',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')

    if result == 'OK' :
        text = cmds.promptDialog(query=True, text=True)
        if text != "" :
            cmds.rename(combined, text)
        else:
            cmds.warning("AssetChecker-->User did not specify correct name, leaving default name!")

    #set the button to FIXED:
    cmds.button(btnName, e=1, label="FIXED", bgc=(0,1,0), enable=False )

    #final output
    sys.stdout.write("AssetChecker --> Following ges were combined: " + str(GEOS) )


################################
#
#END OF FUNCTIONS FOR BUTTONS:
#
################################


def printTextLineSec(message, fontStyle='plainLabelFont') :
    '''
    prints out text line in the UI while checking the asset - used in both func above
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
    this function is used for zeroing channels below:
    '''
    for obj in objects:
        for channel in channels:
            try:
                cmds.setAttr(obj+'.'+channel[0], channel[1])
            except:
                print "- Cannot set "+str(obj)+"."+str(channel[0]) + " to " + str(channel[1]) + " - it might be locked or connected"



def finalizeScene(*args) :
    '''
    finalizes the scene making it ready for promotion
    '''
    print("\nAssetChecker--> Zeroing out all the Ctrls")

    all_controls = cmds.ls("*_Ctrl")
    all_channels = [['translateX',0],['translateY',0],['translateZ',0],['rotateX',0],['rotateY',0],['rotateZ',0],['scaleX',1],['scaleY',1],['scaleZ',1]]
    set_channel_value(all_controls, all_channels)

    print("\nAssetChecker--> Setting all the panels")

    #setting the panels:
    thePanel = cmds.getPanel( withFocus=True )
    try:
        cmds.modelEditor(thePanel, edit=True, displayAppearance='boundingBox', grid=False)
    except:
        cmds.warning('AssetChecker--> Camera values not set - please give focus to an active modelView')

    #hiding all the cameras
    cameras = cmds.lsThroughFilter( cmds.itemFilter(byType='camera') )
    for c in cameras :
        transform = cmds.listRelatives(c, parent=True)[0]
        cmds.setAttr(transform+'.visibility', False)
        print('AssetChecker--> setting ' + transform + '.visibility to False')

    #running DW cleanup script:
    print('\nAssetChecker--> Running Dreamworks Cleanup Script')
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
        if shps != None :
            for s in shps :
                if not "Orig" in s :
                    PROXYshps.append(s)
        else :
            cmds.warning("list of shapes for geo: " + p + " is empty, skipping...")

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

        #go back to Active Change Mode...
        #if cmds.objExists("persp") :
        #    mel.eval('maintainActiveChangeSelectMode "persp";')

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
            printTextLine('--- XXXX: nGons found in LoRes_Geo', color=DARKRED, msgType='neg', command='selectFixByTesselation', commandAttr=allnGons )
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
            printTextLine('--- XXXX: There is more then one proxy mesh in Proxy group - consider combining them', color=DARKRED, msgType='neg', command="combineGeo", commandAttr=PROXY)

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
            t = None
            try :
                t = str(cmds.listRelatives(m, parent=True)[0])
            except :
                cmds.warning("There is an issue with mesh: " + m + ", multiple geo objects are named like this, skipping")
                continue

            if type(t) != str :
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
    Checks rig structure:
    -> checks that transform hierarchy is the same...
    -> checks that control groups are locked (we will list them in XML... the group names to be locked...)
    -> checks if proper layers exist in the rig (listed in xml...)
    -> needs to check for a lightRig / controls layer co-depenency - it could be executing a code from external .py (specified in xml)

    (NEEDS TO BE MOVED OUT AND UPDATED)
    '''

    #save current index of negative outputs...
    NEGindex = global_vars.NEG_INDEX

    printTextLine('', msgType='info')
    printTextLine('Checking Rig Structure!', color=GRAY, textStyle='bold', msgType='info')


    #check the structure using xml file data:
    #StructureXML ACR

    CurrentAssetType = None #variable storing current asset type:

    #look through asset types and get the relevant one (prop for prop, char for char, etc...)
    for at in ACR.AssetTypes :
        if at.name == asset_type :
            CurrentAssetType = at
            break

    #a recurrential function to check the folder structure and make sure it matches the xml file:
    def recurrentialFolderCheck(folderStructureFromXML) :
        #get the parent folder
        parentFolder = folderStructureFromXML.tag

        #if parent folder is 'main_node' then get the world node instead
        if parentFolder == 'main_node' :
            parentFolder = getMainNode()

        #current subfolders = we will compare them to xml (as long as parent folder exists, otherwise stop the function)
        currentSubfolders = None
        if cmds.objExists(parentFolder) :
            currentSubfolders = cmds.listRelatives(parentFolder, children=True)
        else :
            return

        #look through folders in XML file and see if they exists in the maya file... output messages accordingly
        if len(folderStructureFromXML) != 0 :

            for folderXML in folderStructureFromXML :

                folderSTR = folderXML.tag

                if folderSTR in currentSubfolders :
                    printTextLine('- good: '+folderSTR+' found in the rig, under: ' + parentFolder, color=DARKGREEN, msgType='pos' )
                else :
                    printTextLine('- XXXX: '+folderSTR+' not found in the rig under: ' + parentFolder, color=DARKRED, msgType='neg', command='createNodeUnder', commandAttr=[folderSTR, parentFolder])

                recurrentialFolderCheck(folderXML)

    #get folder structure from xml file - using function defined above:
    recurrentialFolderCheck(CurrentAssetType.rigStructureXMLRoot.find('main_node'))

    ###### checking control groups ######
    transformsToLockXML = CurrentAssetType.rigStructureXMLRoot.find('transformsToLock')

    substrings_for_obj = transformsToLockXML.find('substrings_for_obj').text
    substrings_for_parent = transformsToLockXML.find('substrings_for_parent').text
    skip_objs = transformsToLockXML.find('skip_objs').text


    #get all the controls:
    allCtrls = cmds.ls(substrings_for_obj)

    #get all the control names to bypass:
    skipControls = skip_objs.split(',')

    #running the check for control groups - checking if they are locked
    for c in allCtrls :
        if c in skipControls :
            continue
        try :
            g = cmds.listRelatives(c, parent=True)[0]
        except :
            cmds.warning("There is a problem with an object: " + c + ", cannot determine its parent, skipping!")
            continue

        if substrings_for_parent not in g :
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
            printTextLine('----- XXXX: Controls_Layer exists in the rig, yet no lighting rig was found. It should be deleted.', color=DARKRED,  msgType='neg', command='deleteLayer', commandAttr="Controls_Layer")
        elif not Controls_Layer and LightRig :
            printTextLine('----- XXXX: Controls_Layer not found in the rig, yet a lighting rig was found. It should be created.', color=DARKRED,  msgType='neg' )
        elif Controls_Layer and LightRig :
            printTextLine('----- good: Controls_Layer exists in the rig, and relevant lighting rig was found.', color=DARKGREEN, msgType='pos' )
        elif not Controls_Layer and not LightRig :
            printTextLine('----- good: No Controls_Layer exists in the rig, nor is there a lighting rig.', color=DARKGREEN, msgType='pos' )

    #final checking message - info output...
    if NEGindex == global_vars.NEG_INDEX :
        printTextLine('- info: rig structure checked', color=YELLOW, msgType='info' )



def checkForReferences(asset_type) :
    '''
    Checks for references in the file
    returns False if there is no references,
    returns True if there are references...
    (MOVED OUT)
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
        else :
            allReferences.append(refFilePath)
            refFilename = os.path.basename( refFilePath )
            print 'Reference ' + ref + ' found at: ' + cmds.referenceQuery(ref, f=True)

    #if there are no references:
    if allReferences == [] :
        printTextLine('- good: no references found', color=DARKGREEN, msgType='pos' )
        printTextLine('- info: references checked', color=YELLOW, msgType='info' )
        return False

    #in case there are references:
    else :
        #now doing the check for all asset types...
        for a in ACR.AssetTypes :
            #if specific asset bans references then output neg messages and return True
            if a.referencesAllowed == False :
                printTextLine('- XXXX: references found in the file:', color=DARKRED, msgType='neg' )
                for each in allReferences :
                    printTextLine('--- XXXX: improper reference: ' + each, color=DARKRED, msgType='neg')
                return True
            #if specific asset allows refereces then output info messages and return False...
            else :
                printTextLine('- info: There are references in asset file:', color=GRAY, msgType='neg' )
                for each in allReferences :
                    printTextLine('--- info: Make sure this is a proper reference: ' + each, color=GRAY, msgType='neg')

            return False




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



def checkMainNode() :
    '''
    looks for a main node in the asset, if it doesn't exist
    returns FALSE otherwise returns TRUE
    for VGT it is a node with *World_* in it
    (moved OUT)
    '''
    worldNode = None

    #get the top nodes from the outliner...
    worldNodeLst = cmds.ls(assemblies=True)

    #filter the list so that we get only nodes which have mainNode_Substring in it...
    worldNodeLst = [ x for x in worldNodeLst if ACR.mainNode_Substr in x ]

    if worldNodeLst != None and worldNodeLst != []:
        worldNode = worldNodeLst[0]

    if worldNode == None :
        return False

    return True



def getMainNode() :
    '''
    gets the main Node based on ACR
    (MOVED OUT)
    '''

    worldNode = None

    #get the top nodes from the outliner...
    worldNodeLst = cmds.ls(assemblies=True)

    #filter the list so that we get only nodes which have mainNode_Substring in it...
    worldNodeLst = [ x for x in worldNodeLst if ACR.mainNode_Substr in x ]

    if worldNodeLst != None and worldNodeLst != []:
        worldNode = worldNodeLst[0]

    return worldNode



def determineAssetName(asset_type='asset') :
    '''
    Determines asset name (takes mainNode name minus the mainNode_Substr)
    This rule can be changed or moved out of the code...
    (MOVED OUT)
    '''

    worldNode = getMainNode()
    print "AssetChecker--> MainNode = "+worldNode

    assetName = worldNode.replace(ACR.mainNode_Substr, '')

    #output empty text line...
    printTextLine("")

    #print the asset type in the form of info message:

    printTextLine(asset_type.upper()[0] + asset_type[1:] + " name is: " + assetName, color=YELLOW, msgType='info')

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
    if not checkMainNode() :
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
