import maya.cmds as mc 
import pymel.core as pm 
from functools import partial
import pickle
import csv 
from PIL import Image 

G_TB_SceneContents = ""
G_PeopleVarName = ""


def Options_Change(actor, optionMenu, *args):
	actor.uiSelectOption = mc.optionMenu(optionMenu, query=True, value=True)
	actor.Select()

def Button_DupChain(skelM, *args):
	skelM.DuplicateChainInitial()

def Button_UpdateChain(skelM, *args):
	skelM.UpdateSingleChain()

def Button_MakeSizedPlane(*args):

	folder = pm.windows.promptForFolder()

	fl = pm.getFileList(folder=folder, filespec='*.png')

	for png in fl:

		path = folder + "/" + png
		img = Image.open(path) 
  
		# get width and height 
		width = img.width 
		height = img.height 

		name = png.replace(".png", "")

		planeSizer = TB_PlaneSizer(width,height)
		planeSizer.BuildSizedPlane(name, texture=path)

def Button_SetCtrlColors(color, *args):

	SetControlsColor(color)

def Button_MakeExpSet(zcam, *args):

	MakeExportSet(zcam)

def Button_AddPeopleVariant(*args):

	global G_PeopleVarName

	AddPeopleRigVariant(G_PeopleVarName)

def TextField_SetVarName(textf, *args):

	global G_PeopleVarName
	G_PeopleVarName = textf


# # make and display UI #    

def MakeAndShowUI():

	global G_TB_SceneContents
	global G_PeopleVarName

	winName = "TB_Tools" 
	if pm.window(winName, exists=True): 
		pm.deleteUI(winName)

	tbWindow = pm.window(winName, title=winName, width = 270, te=200) 
	#print (tbWindow)
	mainCL =	pm.columnLayout() 
	pm.button(label = 'Snap', command = partial(SnapSelected) )
	pm.button(label = 'Zero', command = partial(ZeroSelected) )
	pm.button(label = 'define skin root', command = partial(DefineDrivenSkel) )

	if(G_TB_SceneContents.skeletonMaintainer != None):

		skelM = G_TB_SceneContents.skeletonMaintainer
		pm.text(label= skelM.skinRoot)	
		pm.text(label= len(skelM.skinJoints))	
		pm.button(label = 'duplicate to driver chain', command = partial(Button_DupChain,skelM) )
		pm.button(label = 'update driver chain', command = partial(Button_UpdateChain,skelM) )	

	pm.button(label = 'Select Skin Joints', command = partial(GetSkinJoints) )

	pm.button(label = 'Build Sized Planes', command = partial(Button_MakeSizedPlane) )
	pm.button(label = 'Joints at Pivots', command = partial(MakeJointsAtPivots) )
	pm.button(label = 'Rig Folders', command = partial(SetUpRigFolders) )

	pm.text("Color Controls")
	mc.rowLayout(numberOfColumns=4)	
	pm.button(label = 'Yellow', command = (partial(Button_SetCtrlColors, "YELLOW")))
	pm.button(label = 'Light Blue', command = (partial(Button_SetCtrlColors, "LIGHT BLUE")))
	pm.button(label = 'Red', command = (partial(Button_SetCtrlColors, "BRIGHT RED")))
	pm.button(label = 'Blue', command = (partial(Button_SetCtrlColors, "BLUE")))
	mc.setParent(mainCL)

	pm.text("D&D Extras")
	mc.rowLayout(numberOfColumns=2)	
	pm.button(label = 'Make Export Set', command = partial(Button_MakeExpSet, False) )
	pm.button(label = 'Make Export Set ZCam', command = partial(Button_MakeExpSet, True) )
	mc.setParent(mainCL)
	pm.button(label = 'Check Export Geo', command = partial(CheckExportGeo) )
	pm.button(label = 'D&D Res', command = partial(SetDnDRes) )
	pm.button(label = 'connect spline nodes', command = partial(SetUpIKSplineTranslate) )
	pm.button(label = 'All Constraints', command = partial(FullConstraints) )
	textf = pm.textField(changeCommand = TextField_SetVarName)
	textf.setPlaceholderText("Variant")
	pm.button(label = 'Add People Variant', command = partial(Button_AddPeopleVariant) )


	pm.showWindow() #



def Setup():

	global G_TB_SceneContents

	G_TB_SceneContents = TB_SceneContents()

	MakeAndShowUI()


def DefineDrivenSkel(self):

	global G_TB_SceneContents

	skinRoot = Selection()
	if(skinRoot.nodeType() != "joint"):
		mc.error("Not a joint")

	newSkel = TB_SkeletonMaintainer(skinRoot)
	print(newSkel.skinRoot)
	newSkel.CollectSkinJoints()


	G_TB_SceneContents.skeletonMaintainer = newSkel

	print (G_TB_SceneContents.skeletonMaintainer)

	MakeAndShowUI()

def SetControlsColor(color):
	colorList = {"BLACK" : 1, "GREY" : 3, "DARK RED" : 4, "DARK BLUE" : 5, "BLUE" : 6, "DARK GREEN" : 7, "DARK PURPLE" : 8, "HOT PINK" : 9, "BROWN" : 10, "DARK BROWN" : 11, "BRIGHT RED" : 13, "NEON GREEN" : 14, "NAVY BLUE" : 15, "WHITE" : 16, "YELLOW" : 17, "LIGHT BLUE" : 18, "TURQUOISE" : 19, "LIGHT BROWN" : 21, "PURPLE" : 30}

	sel = Selection(onlyOne=False)
	print(color)
	print(colorList[color])

	for s in sel:
		shape = s.getShape()
		if(pm.nodeType(shape) == "nurbsCurve"):
			shape.overrideEnabled.set(True)
			shape.overrideColor.set(colorList[color])


def SetUpRigFolders(self):

	rigGrp = pm.group(n="Name_Rig", em=True)
	geoGrp = pm.group(n="geo", em=True, p = rigGrp)
	jntGrp = pm.group(n="jnt", p = rigGrp, em=True)
	ctrlGrp = pm.group(n="ctrl", p = rigGrp, em=True)

	pm.select(geoGrp, r=True)
	geoLayer = pm.createDisplayLayer(n='Geo')
	pm.select(jntGrp, r=True)
	geoLayer = pm.createDisplayLayer(n='Joints')
	pm.select(ctrlGrp, r=True)
	geoLayer = pm.createDisplayLayer(n='Controls')



def FindSkinJointsDumb():

	grp = ""

	toCheck = ["SkinJoints","SkinJoints_grp", "SkinJnts", "SkinJnts_grp", "Skin_Joints", "Skin_Joints_grp"]

	for poss in toCheck:
		if(pm.objExists(poss)):
			grp = poss

	return grp



def CheckExportGeo(self):

	allGeo = pm.ls(type="mesh")
	exportGeo = []

	allGood = True

	for geo in allGeo:
		isExportGeo = False
		parent = pm.listRelatives(geo.getTransform(), p=True)
		if(parent == []):
			continue
		isExportGeo = ("EXPORT" in parent[0].listSets())


		if(isExportGeo):
			connections = geo.connections()
			#print(geo.getTransform() + " is export geo")
			for c in connections:
				if (pm.nodeType(c) != "shadingEngine" and pm.nodeType(c) != "nodeGraphEditorInfo" and pm.nodeType(c) != "skinCluster"):
					pm.warning (geo + " has " + c)
					allGood = False

	if(allGood):
		pm.warning("all good!")



def FullConstraints(self):

	sel = Selection(onlyOne = False)

	if(len(sel) != 2):
		pm.error("more than 2 selected")
		return

	driver = sel[0]
	driven = sel[1]
	
	pm.pointConstraint(driver, driven, mo=False)
	pm.orientConstraint(driver, driven, mo=False)
	pm.scaleConstraint(driver, driven, mo=False)






def SnapSelected(self):

	selection = Selection(onlyOne=False)

	if(len(selection) > 1):
		target = selection[-1]
		snapped = selection[:-1]

		targetPos = target.getRotatePivot(ws=True)
		targetRot = target.getRotation(ws=True)

		print(targetPos)
		print(targetRot)


		for snapobj in snapped:
			pm.makeIdentity(snapobj, apply=True, t=True, r=True)
			diff = targetPos - snapobj.getRotatePivot(ws=True)
			print(snapobj.getRotatePivot(ws=True))
			snapobj.setTranslation(diff, ws=True, preserve=False)
			snapobj.setRotation(targetRot, ws=True, preserve=False)

	elif (len(selection)==1):
		print(selection[0].getRotatePivot(ws=True))


def ZeroSelected(self):

	selection = Selection(onlyOne=False)

	for item in selection:
		pm.xform(item, os=True, t=[0,0,0], ro=[0,0,0])


def Selection(onlyOne = True):

	selection = pm.ls(sl=True)
	amt = len(selection)

	if(amt == 0):
		mc.error("nothing selected")
	elif (amt > 1 and onlyOne):
		mc.error("multiple selected")

	if(onlyOne):
		return selection[0]
	else:
		return selection

def FindTransform(trName, inNamespace=False): 
		if(trName == ""):
			mc.error("looking for empty transform name")
		searchStr = ""

		if(inNamespace):
			searchStr = "::*" + self.namespace + ":" + trName
		else:
			searchStr = "::*" + trName

		transforms = pm.ls(searchStr)
		if(len(transforms) == 0):
			return None
		elif(len(transforms) > 1):
			mc.error("more than 1 match when searching for " + searchStr)
		else:
			return transforms[0]

def GetSkinJoints(self):

	print(pm.nodeType(Selection()))
	geoTrans = Selection()
	geoShape = geoTrans.getShape()

	skinJnts = []

	if(geoShape != None):
		skin = geoShape.connections(type="skinCluster")[0]

		if(skin != None):
			skinJnts = skin.connections(type="joint")

	pm.select(skinJnts, r=True)

def MakeJointsAtPivots(self):

	selection = Selection(onlyOne=False)

	grp = pm.group(n="Prelim_Joints", em=True)

	for item in selection:
		if(item.nodeType() == 'transform'):
			newJoint = pm.joint(grp, p=item.getRotatePivot(), name=item+"_JNT")
			newJoint.setAngleX(item.rotateX.get())
			newJoint.setAngleY(item.rotateY.get())
			newJoint.setAngleZ(item.rotateZ.get())


"""
Just Draw&Discover specific stuff
"""

def AddPeopleRigVariant(varName):

	varCtrl = pm.ls("People_Settings_Ctrl")[0]
	varAttr = pm.Attribute(varCtrl+'.Variant')
	geoGrp = pm.group(empty=True, name=(varName+'_geo'), parent='geo')
	ctrlGrp = pm.group(empty=True, name=(varName+'_ctrls'), parent='ctrls')
	varEnums = varAttr.getEnums()
	newList = []

	for enum in varEnums:
		#print (enum)
		newList.append(enum)

	newList.append(varName)
	varCtrl.Variant.setEnums(newList)

	print(varAttr.getEnums()[varName])

	cond = pm.createNode("condition", n=("condition_var_"+varName))
	# condition: is variant enum equal second term
	varAttr >> cond.firstTerm
	cond.secondTerm.set(varAttr.getEnums()[varName])
	# by default it's 1 if it doesn't match and that bugs me, so we switch it
	cond.colorIfTrueR.set(1)
	cond.colorIfFalseR.set(0)
	# if yes, show controls and geo
	cond.outColorR >> geoGrp.visibility
	cond.outColorR >> ctrlGrp.visibility


def SetUpIKSplineTranslate(self):

	sel = Selection(onlyOne=False)
	ctrl = sel[0]
	firstJoint = sel[1]
	restJoints = sel[2:]

	print (ctrl)
	print(restJoints)


	ofsScaleWater = pm.createNode('plusMinusAverage')
	ofsScaleWater.input1D[0].set(0.001)
	ctrl.ScaleWater >> ofsScaleWater.input1D[1]


	#ctrl.ScaleWater >> firstJoint.scaleX
	ofsScaleWater.output1D >> firstJoint.scaleX

	for joint in restJoints:
		initialTransl = pm.createNode('plusMinusAverage')
		initialTransl.input1D[0].set(joint.translateX.get())

		ofsScaleWater = pm.createNode('plusMinusAverage')
		ofsScaleWater.input1D[0].set(0.001)
		ctrl.ScaleWater >> ofsScaleWater.input1D[1]

		mult = pm.createNode('multiplyDivide')
		ofsScaleWater.output1D >> mult.input1.input1X
		initialTransl.output1D >> mult.input2.input2X
		mult.outputX >> joint.translateX
		ofsScaleWater.output1D >> joint.scaleX

		"""
		mult = pm.createNode('multiplyDivide')
		ctrl.ScaleWater >> mult.input1.input1X
		initialTransl.output1D >> mult.input2.input2X
		mult.outputX >> joint.translateX
		ctrl.ScaleWater >> joint.scaleX
		"""


def MakeExportSet(zCam):

	
	geoGrp = pm.ls("geo")
	skinJointGrp = FindSkinJointsDumb()

	if(skinJointGrp == ""):
		pm.error("didn't find joints")
		return

	print (skinJointGrp)

	# delete old
	setExists = pm.objExists("EXPORT")
	if(setExists):
		exportSet = pm.ls("EXPORT")
		pm.delete(exportSet)

	print("make new set")
	# make new
	newExportSet = pm.sets(n="EXPORT") 
	cam = ""
	if(zCam):
		cam = MakeDnDCamera_Z()
	else:		
		cam = MakeDnDCamera()


	pm.sets(newExportSet, include=[cam, skinJointGrp, geoGrp], e=True)
	print(newExportSet.members())
	#newExportSet.union( skinJointGrp )

def SetDnDRes(self):

	
	res = pm.SCENE.defaultResolution
	res.width.set(1440)
	res.height.set(1080)

def MakeDnDCamera():

	# ugh
	ddCam = pm.camera(n="ExportCam")[1]
	ddCam.displayResolution.set(True)
	ddCam.getTransform().translateX.set(800)
	ddCam.getTransform().translateY.set(50)
	ddCam.getTransform().rotateY.set(90)


	res = pm.SCENE.defaultResolution
	res.width.set(1440)
	res.height.set(1080)
	ddCam.overscan.set(1.5)

	return ddCam.getTransform()

def MakeDnDCamera_Z():

	# ugh
	ddCam = pm.camera(n="ExportCam")[1]
	ddCam.displayResolution.set(True)
	ddCam.getTransform().translateZ.set(800)
	ddCam.getTransform().translateY.set(50)
	ddCam.getTransform().rotateY.set(0)


	res = pm.SCENE.defaultResolution
	res.width.set(1440)
	res.height.set(1080)
	ddCam.overscan.set(1.5)

	return ddCam.getTransform()

class TB_PlaneSizer():

	sizeX = 0.0
	sizeY = 0.0

	# Constructor     
	def __init__(self, x, y):
		self.sizeX = x
		self.sizeY = y

	def BuildSizedPlane(self, name, texture):

		plane = pm.polyPlane(n=name, w=int(self.sizeX), h=int(self.sizeY), sh=2, sw=2)
		lamb = pm.shadingNode('lambert', asShader=True, n=("M_" + name))
		tex = pm.shadingNode('file', asTexture=True, n=("T_" + name))
		pm.connectAttr(tex + '.outColor', lamb + '.color')
		pm.connectAttr(tex + '.outTransparency', lamb + '.transparency')
		pm.setAttr(tex + '.fileTextureName', texture, type="string")

		pm.select(plane)

		pm.hyperShade(assign=lamb)




class TB_SceneContents():

	skeletonMaintainer = None

class TB_SkeletonMaintainer():

	# Constructor     
	def __init__(self, skinRoot):
		self.skinRoot = skinRoot

	skinRoot = ""
	driverRoot = ""

	driverJoints = []
	skinJoints = []

	def DuplicateChainInitial(self):

		self.DuplicateJoints(self.skinJoints)

	def UpdateSingleChain(self):

		print ("update")

		self.CollectSkinJoints()
		driverGrp = FindTransform("DriverJoints_grp")

		for skinJnt in self.skinJoints:
			driverJnt = self.GetDriverJnt(skinJnt)
			if(driverJnt == None):
				print("new joint to add")
				print(driverJnt)
				#self.GenerateAndConnectSHJoint(drJoint)
				newDriverJnt = pm.duplicate(skinJnt, po=True, name=self.GenerateSHName(skinJnt))
				pm.parent(newDriverJnt, driverGrp)
				pm.pointConstraint(newDriverJnt, skinJnt, mo=False)
				pm.orientConstraint(newDriverJnt, skinJnt, mo=False)
				pm.scaleConstraint(newDriverJnt, skinJnt, mo=True)
			else:
				print ("updating")
				print(driverJnt)
				print (skinJnt.segmentScaleCompensate.get())
				driverJnt.segmentScaleCompensate.set(skinJnt.segmentScaleCompensate.get())



	def CollectSkinJoints(self):

		self.skinJoints = self.CollectJoints(self.skinRoot)

		print("collected joints")
		print (self.skinJoints)

	def CollectJoints(self, skelRoot):

		desc = skelRoot.listRelatives(ad=True)
		foundJoints = [skelRoot]

		for entry in desc:
			if(pm.nodeType(entry) == "joint"):
				foundJoints.append(entry)

		return foundJoints

	def DuplicateJoints(self, joints):

		dup = FindTransform("DriverJoints_grp")
		if(dup != None):
			mc.error("Duplicate chain exists already")
			#pm.delete(dup)

		jntGrp = pm.group(name = "DriverJoints_grp", em=True, w=True)

		dupJnts = []

		for joint in joints:
			dupJnt = pm.duplicate(joint, po=True, name=self.GenerateSHName(joint))
			pm.parent(dupJnt, jntGrp)
			dupJnts.append(dupJnt)

		self.driverJoints = dupJnts

		i = 0
		for dupJnt in dupJnts:

			skinJnt = joints[i]

			jntParent = self._GetJointParentRecursive(skinJnt)

			if(jntParent != None):
				pm.parent(dupJnt, (self.GenerateSHName(jntParent[0])))


			pm.pointConstraint(dupJnt, skinJnt, mo=False)
			pm.orientConstraint(dupJnt, skinJnt, mo=False)
			pm.scaleConstraint(dupJnt, skinJnt, mo=True)


			i+=1

	def GetDriverJnt(self, driverJnt):


		name = self.GenerateSHName(driverJnt)
		return FindTransform(name)

	def GenerateSHName(self, dName):

		return (dName.replace("_driver", "") + "_SH")

	def _GetJointParentRecursive(self, joint):


		parent = pm.listRelatives(joint, p=True)
		if(len(parent) == 0):
			print("found None")
			return None
		if(pm.nodeType(parent) == "joint"):
			return parent

		return self._GetJointParentRecursive(parent[0])

"""
	def GenerateAndConnectSHJoint(self, driverJnt):

		jntGrp = pm.group(name = "SkinJoints_grp", em=True, w=True)

		dupJnt = pm.duplicate(driverJnt, po=True, name=self.GenerateSHName(driverJnt))
		pm.parent(dupJnt, jntGrp)
		self.SHJoints.append(dupJnt)

		jntParent = self._GetJointParentRecursive(driverJnt)

		if(jntParent != None):
			pm.parent(dupJnt, (self.GenerateSHName(jntParent[0])))

			pm.parentConstraint(driverJnt, dupJnt, mo=True)
			pm.scaleConstraint(driverJnt, dupJnt, mo=True)

"""

	





