import maya.cmds as mc 
import pymel.core as pm 
from functools import partial
import pickle
import csv 

G_YUESettings = "" 
G_SettingsPath = ""
G_ComponentDataPath = ""


def Button_BuildSpaceRig(actor, *args):  
	CheckForSpaceRig()   
	actor.DuplicateSpaceRig()

def Button_ParentBakeCube(actor, *args):
	CheckForSpaceRig()
	actor.ParentBakeCube()     

def Button_ParentCharacter(actor, *args):  
	CheckForSpaceRig()       
	actor.ParentActorSpace()

def Button_BakeRoot(actor, *args):
	actor.BakeRoot()

def Button_DeleteRootKeys(actor, *args):
	actor.DeleteRootKeys()

def Options_Change(actor, optionMenu, *args):
	actor.uiSelectOption = mc.optionMenu(optionMenu, query=True, value=True)
	actor.Select()

def Button_Select(actor, *args):
	actor.Select()


# # make and display UI #    

def MakeAndShowUI():

	global G_YUESettings

	winName = "YUE" 
	if mc.window(winName, exists=True): 
		mc.deleteUI(winName)

	mc.window(winName, title=winName, width = 270, te=200) 
	mainCL =	mc.columnLayout() 
	mc.button(label = 'Rebuild Settings', command =	partial(BuildSettings) )
	mc.text(label= "for anim setup: Parent Bakecube -> Parent Character -> Bake Root ")
	mc.text(label= "for export setup: select Anchor Space -> set To Origin to 1 -> select Export grp")	
	mc.text(label= "----------------------------------------")
	for actor in G_YUESettings.actors:

		mc.text(label = actor.GetName()) 
		if actor.isBoat:
			BuildBoatUI(actor) 
		else:
			BuildCharUI(actor)

		mc.setParent(mainCL)

	mc.showWindow() #

def BuildCharUI(actor):     
	row = mc.rowLayout(numberOfColumns=5)
	#mc.button(label = 'Copy SpaceRig', align = 'bottom', command = partial(Button_BuildSpaceRig, actor) )     
	

	columnA = mc.columnLayout()


	mc.button(label = 'Parent Bakecube', command = partial(Button_ParentBakeCube, actor) ) 
	mc.setParent(row)

	mc.button(label = 'Parent Character', command =	partial(Button_ParentCharacter, actor) )


	bakeColumn = mc.columnLayout()
	mc.button(label = 'Bake Root', command =	partial(Button_BakeRoot, actor) )
	mc.button(label = 'Delete Baked Keys', command =	partial(Button_DeleteRootKeys, actor) )
	mc.setParent(row)

	mc.button(label = 'Select:', command =	partial(Button_Select, actor) )
	opt = mc.optionMenu( )
	mc.optionMenu(opt, e=True, changeCommand = partial(Options_Change, actor, opt))
	mc.menuItem(opt, label = "Export Grp")
	mc.menuItem(opt, label = "Root")
	mc.menuItem(opt, label = "Anchor Space")
	mc.menuItem(opt, label = "Boat Attach")



def BuildBoatUI(actor):     
	row = mc.rowLayout(numberOfColumns=4)
	#mc.button(label = 'Copy SpaceRig', align = 'top', command = partial(Button_BuildSpaceRig, actor) )     
	columnA = mc.columnLayout()
	
	
	mc.button(label = 'Parent Bakecubes', command =	partial(Button_ParentBakeCube, actor ) ) 
	mc.setParent(row)
	mc.button(label = 'Parent Boat', command = partial(Button_ParentCharacter, actor) )


def Setup():

	BuildPaths() 
	LoadSettingsFromFile()

	MakeAndShowUI()

def BuildPaths():

	global G_SettingsPath
	global G_ComponentDataPath

	# This is set in workspace.mel file and stores project path
	workspacePath = maya.mel.eval("$temp=$ws")    
	G_SettingsPath = workspacePath + "scripts/YUEData"
	G_ComponentDataPath = workspacePath + "scripts/YUEComponents.csv"


def LoadSettingsFromFile():

	global G_SettingsPath 
	global G_YUESettings

	pickle_in = open(G_SettingsPath, "rb") 
	G_YUESettings =	pickle.load(pickle_in)


def BuildSettings(self):

	global G_YUESettings
	global G_SettingsPath

	G_YUESettings = YUE_Settings()

	Yuki = YUE_Char("Yuki") 
	RocketTurtle = YUE_Char("RocketTurtle") 
	Goldpaws =	YUE_Char("Goldpaws") 
	TigerLady = YUE_Char("TigerLady") 
	TallShark_A =	YUE_Char("TallShark_A") 
	ShortShark_A = YUE_Char("ShortShark_A") 
	TallShark_B =	YUE_Char("TallShark_B") 
	ShortShark_B = YUE_Char("ShortShark_B") 
	YukiBoat =	YUE_Boat("YukiBoat") 
	EvilBoat_A = YUE_Boat("EvilBoat_A") 
	EvilBoat_B = YUE_Boat("EvilBoat_B") 
	EvilBoat_T = YUE_Boat("EvilBoat_T")


	G_YUESettings.actors = [Yuki,  RocketTurtle,  Goldpaws, TigerLady,
	TallShark_A, ShortShark_A, TallShark_B, ShortShark_B, YukiBoat, EvilBoat_A, EvilBoat_B, EvilBoat_T]

	i = 0
	for actor in G_YUESettings.actors:
		i+=1
		actor.csvLine = i

	actorInfo = CSVComponentInfo()

	for actor in G_YUESettings.actors:
		print "building settings for " + actor.name + ", line ID: " + str(actor.csvLine)
		actor.bakeCube = actorInfo.GetBakeCube(actor)
		actor.namespace = actorInfo.GetNamespace(actor)
		if(actor.isBoat):
			actor.hullBakeCube = actorInfo.GetHullCube(actor)
		else: # is character
			actor.root = actorInfo.GetRoot(actor)
			actor.parentEnumID = actorInfo.GetEnumID(actor)
		actor.anchor = actorInfo.GetAnchor(actor)	



	print "saving actors to " + G_SettingsPath
	pickle_out = open(G_SettingsPath,"wb") 
	pickle.dump(G_YUESettings,	pickle_out) 
	pickle_out.close()

def CheckForSpaceRig():

	transforms = pm.ls("::*SpaceRig")
	if(len(transforms) == 0):
		mc.error("no Space Rig found")


def ConnectBoatSpace():


	for i in range(5, 9):
	    print i
	    for boat in range (4):
	        boatName = ""
	        
	        if(boat==0):
	            boatName = "YukiBoat"
	        if(boat==1):
	            boatName = "EvilBoat_A"
	        if(boat==2):
	            boatName = "EvilBoat_B"
	        if(boat==3):
	            boatName = "EvilBoat_T"
	            
	        print boatName

	        attrA = "Out_" +  boatName + ".worldMatrix[0]"
	        attrB = "blendMatrix_BoatSpaces" + str(i) + ".target[" + str(boat) + "].targetMatrix"
	        print attrA
	        print attrB
	        connectAttr(attrA, attrB)


class YUE_Settings():

	actors = []

	def __init__(self):  
		pass


class YUE_Actor():

	csvLine = -1

	namespace = ""
	bakeCube = "" 
	anchor = "" 

	isBoat = False


	# Space Rig components
	_space_In = ""

	 # Constructor     
	def __init__(self, name):
		self.name = name

	def GetName(self):          
		return self.name

	def GetTemplate(self):
		return "";

	def GetSpaceRigComponents(self): 
		self._space_In = pm.ls("::*In_" + self.name)[0] 
		#print "In: " + self._space_In

	def DuplicateSpaceRig(self): 
		template = self.GetTemplate() 
		print ("Duplicating " + template + " for " + self.name) 
		Dup = pm.duplicate(template, upstreamNodes=True, name=self.name)[0]

		self.FixSpaceRigNaming(Dup)

	def FixSpaceRigNaming(self, spaceRig): print ("main")

	def ParentBakeCube(self): 
		self.GetSpaceRigComponents() 
		print "parenting bake cube" 
		print self.bakeCube 

		if(self.bakeCube != ""):
			cubeTr = self.GetBakeCubeTr(self.bakeCube)

			pm.parentConstraint(cubeTr, self._space_In, maintainOffset=False)
			pm.select(self._space_In)

	def GetBakeCubeTr(self, cubeName): 
		cubeSearch = pm.ls("::*"+cubeName) 
		if(len(cubeSearch) == 0):
			mc.error("no transforms could be found when searching for " + cubeName)
		for	result in cubeSearch: 
			if "UCX" not in result.name(): 
				return result


	def FindTransform(self, trName, inNamespace=False): 
		if(trName == ""):
			mc.error("looking for empty transform name")
		searchStr = ""

		if(inNamespace):
			searchStr = "::*" + self.namespace + ":" + trName
		else:
			searchStr = "::*" + trName

		transforms = pm.ls(searchStr)
		if(len(transforms) == 0):
			mc.error("no transforms could be found when searching for " + searchStr)
		elif(len(transforms) > 1):
			mc.error("more than 1 match when searching for " + searchStr)
		else:
			return transforms[0]


class YUE_Char(YUE_Actor):


	isBoat = False
	uiSelectOption = 0

	# component info from CSV sheet
	root = ""
	parentEnumID = -1	# Represents the boats, declared in csv

	# space rig components, fetched from scene
	_space_Out_Root = "" 
	_space_Out_Anchor = ""
	_space_Parent = ""

	def GetTemplate(self): 
		return pm.ls("::*Template_Character*")[0]

	def FixSpaceRigNaming(self, spaceRig): 
		for item in spaceRig.getChildren():
			item.rename(item.name().replace('Char', self.GetName()))

	def GetSpaceRigComponents(self): 
		YUE_Actor.GetSpaceRigComponents(self)
		self._space_Parent = self.FindTransform("In_BoatSpace_" + self.name)
		self._space_Out_Root = self.FindTransform("Out_Root_" + self.name)
		self._space_Out_Anchor = self.FindTransform("Out_Anchor_" + self.name)

		#print "Out_Anchor: " + _space_Out_Anchor print "Out_Root: " +
		#_space_Out_Root

	def ParentActorSpace(self): 
		self.GetSpaceRigComponents() 

		anchorTr = self.FindTransform(self.anchor, inNamespace=True)  
		rootCtrl = self.FindTransform(self.root, inNamespace=True)

		# setting parent space to whichever boat they're on by default
		print self._space_Parent
		print self.parentEnumID
		pm.setAttr( (self._space_Parent + '.ParentSpace'), int(self.parentEnumID))

		pm.parentConstraint(self._space_Out_Anchor,	anchorTr, maintainOffset=False)
		pm.parentConstraint(self._space_Out_Root, rootCtrl,	maintainOffset=False)

	def BakeRoot(self):
		rootCtrl = self.FindTransform(self.root, inNamespace=True)		
		print rootCtrl

		timeRange = str(int(mc.playbackOptions(q=True, minTime=True)))
		timeRange += ":"
		timeRange += str(int(mc.playbackOptions(q=True, maxTime=True)))
		print timeRange
		pm.bakeResults(rootCtrl, t=timeRange)
		pm.select(rootCtrl)
		#bakeResults -simulation true -t "0:153" -sampleBy 1 -oversamplingRate 1 -disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake true -removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {"hammerheadShark_rig:ROOT_CTL"};

	def DeleteRootKeys(self):		
		rootCtrl = self.FindTransform(self.root, inNamespace=True)
		for curve in pm.listConnections(rootCtrl, source=True, destination=False):
			print curve
			pm.delete(curve)
			#print curve

	def Select(self):

		component = str(self.uiSelectOption)		
		print component

		if(component == "0"):
			pm.select(self.FindTransform(trName ="EXPORT", inNamespace=True ))
		elif(component == "Export Grp"):
			pm.select(self.FindTransform(trName ="EXPORT", inNamespace=True ))
		elif(component == "Root"):
			pm.select(self.FindTransform(self.root, inNamespace=True))
		elif(component == "Anchor Space"):
			self.GetSpaceRigComponents()
			pm.select(self._space_Out_Anchor)
		elif(component == "Boat Attach"):
			self.GetSpaceRigComponents()
			pm.select(self._space_Parent)
		else:
			print "select menu option not found"

	def ToOrigin(self, revert=False):

		i = not revert
		print i
		mc.setAttr(self._space_Out_Anchor + '.ToOrigin', 1)

class YUE_Boat(YUE_Actor):

	isBoat = True

	hullBakeCube = ""

	# Space Rig components     
	_space_In_Hull = ""     
	_space_Out = ""

	def GetTemplate(self): 
		return pm.ls("::*Template_Boat*")[0]

	def FixSpaceRigNaming(self, spaceRig): 
		for item in spaceRig.getChildren():	
			item.rename(item.name().replace('Boat', self.GetName()))

	def GetSpaceRigComponents(self): 		
		YUE_Actor.GetSpaceRigComponents(self)
		self._space_In_Hull = self.FindTransform("In_Hull_" + self.name) 
		self._space_Out = self.FindTransform("Out_" + self.name) 

		print "In: " + self._space_In
		print "In_Hull: " + self._space_In_Hull 
		print "Out: " + self._space_Out

	def ParentBakeCube(self): 
		self.GetSpaceRigComponents() 
		print "parenting boat bake cube" 

		if(self.bakeCube != ""):
			cubeTr = self.GetBakeCubeTr(self.bakeCube)

			pm.parentConstraint(cubeTr, self._space_In, maintainOffset=False)
			pm.select(self._space_In)


	def ParentActorSpace(self): 
		self.GetSpaceRigComponents() 
		print self.anchor

		anchorTr = self.FindTransform(self.anchor, inNamespace=True)
		pm.parentConstraint(self._space_Out, anchorTr, maintainOffset=False)


class CSVComponentInfo():

	_csvReader = None
	_csvList = None

	def __init__(self):  
		self.MakeCSVReader()

	def MakeCSVReader(self):
		global G_ComponentDataPath
		print G_ComponentDataPath

		print "read CSV"
		with open(G_ComponentDataPath, 'rb') as csvfile:
			self._csvReader = csv.reader(csvfile, delimiter=',')
			self._csvList = list(self._csvReader)

	def GetColumnData(self, actor, columnNo):

		lineNo = actor.csvLine
		rows = list(self._csvList)
		return rows[lineNo][columnNo]

	def GetNamespace(self, actor):

		return self.GetColumnData(actor, columnNo=1)

	def GetBakeCube(self, actor):

		return self.GetColumnData(actor, columnNo=2)

	def GetHullCube(self, actor):

		return self.GetColumnData(actor, columnNo=3)

	def GetAnchor(self, actor):

		return self.GetColumnData(actor, columnNo=4)

	def GetRoot(self, actor):

		return self.GetColumnData(actor, columnNo=5)

	def GetEnumID(self, actor):

		return self.GetColumnData(actor, columnNo=6)




Setup()


