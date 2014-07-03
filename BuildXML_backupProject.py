#building xml file


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
