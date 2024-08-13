import maya.cmds as mc 
import pymel.core as pm 
import maya.mel as mel
from functools import partial
import pickle
import csv 

G_MALLSettings = "" 

G_WorkspacePath = ""
G_SettingsPath = ""
G_ComponentDataPath = ""

# Button Wrappers

def Button_ImportCharRig(actor, *args):
	actor.CreateRigReference()

def Button_BuildSpaceRigForActor(actor, *args):  
	CheckForSpaceRig()   
	actor.BuildSpaceRig()

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

def Button_PropExportSelect(grp, *args):
	pm.select(grp)

# # make and display UI #

def MakeAndShowUI():

	global G_MALLSettings

	winName = "MALL" 
	if mc.window(winName, exists=True): 
		mc.deleteUI(winName)

	mc.window(winName, title=winName, width = 500, te=300) 
	mainCL = mc.scrollLayout(
	horizontalScrollBarThickness=16,
	verticalScrollBarThickness=16)
	#mainCL =	mc.columnLayout() 

	mc.rowLayout(numberOfColumns=4)
	mc.button(label = 'Import SpaceRig', command =	partial(ImportSpaceRig) )
	mc.button(label = 'Rebuild Settings', command =	partial(BuildSettings) )
	mc.button(label = 'Rebuild SpaceRig', command =	RebuildSpaceRig )
	mc.button(label = 'Filter Actors', command =	FilterActorsInScene )
	#mc.button(label = 'Cam Border', command =	TurnOnCameraBorder )
	mc.setParent(mainCL)

	mc.rowLayout(numberOfColumns=1)
	mc.button(label = 'PROPS', command =	partial(DoPropUI) )
	mc.setParent(mainCL)

	for actor in G_MALLSettings.actors:

		mc.text(label = actor.GetName()) 
		mc.button(label = "Import Rig", command =	partial(Button_ImportCharRig, actor))

		BuildCharUI(actor)

		mc.setParent(mainCL)

	mc.showWindow() #

def DoPropUI(*args):

	winName = "PROPS" 
	if mc.window(winName, exists=True): 
		mc.deleteUI(winName)

	mc.window(winName, title=winName, width = 500, te=300) 
	mainCL = mc.scrollLayout(
	horizontalScrollBarThickness=16,
	verticalScrollBarThickness=16)


	mc.text("Grill was split into 2 components, both need to be exported") 

	mc.button(label = 'Grill A EXPORT', command =	partial(Button_PropExportSelect, 'AtillaGrillProps_rig:EXPORT_A') )
	mc.button(label = 'Grill B EXPORT', command =	partial(Button_PropExportSelect, 'AtillaGrillProps_rig:EXPORT_B') )
	mc.button(label = 'Gen EXPORT', command =	partial(Button_PropExportSelect, 'FoodCourtProps_rig:EXPORT') )


	mc.showWindow() #


def ShowUIWithActorsFiltered(filteredActorList):

	global G_MALLSettings

	winName = "MALL" 
	if mc.window(winName, exists=True): 
		mc.deleteUI(winName)

	mc.window(winName, title=winName, width = 500, te=300) 
	mainCL = mc.scrollLayout(
	horizontalScrollBarThickness=16,
	verticalScrollBarThickness=16)
	#mainCL =	mc.columnLayout() 

	mc.rowLayout(numberOfColumns=4)
	mc.button(label = 'Import SpaceRig', command =	partial(ImportSpaceRig) )
	mc.button(label = 'Rebuild Settings', command =	partial(BuildSettings) )
	mc.button(label = 'Rebuild SpaceRig', command =	RebuildSpaceRig )
	mc.button(label = 'Filter Actors', command =	FilterActorsInScene )
	#mc.button(label = 'Cam Border', command =	TurnOnCameraBorder )
	mc.setParent(mainCL)

	
	mc.rowLayout(numberOfColumns=1)
	mc.button(label = 'PROPS', command =	partial(DoPropUI) )
	mc.setParent(mainCL)

	for actor in filteredActorList:

		mc.text(label = actor.GetName()) 
		mc.button(label = "Import Rig", command =	partial(Button_ImportCharRig, actor))

		BuildCharUI(actor)

		mc.setParent(mainCL)

	mc.showWindow() #



def BuildCharUI(actor):     
	row = mc.rowLayout(numberOfColumns=7)
	#mc.button(label = 'Copy SpaceRig', align = 'bottom', command = partial(Button_BuildSpaceRigForActor, actor) ) 
	

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
	mc.menuItem(opt, label = "Parent Attach")


def RunMALL():

	BuildPaths() 
	LoadSettingsFromFile()
	#BuildSettings()

	MakeAndShowUI()

def BuildPaths():

	global G_WorkspacePath
	global G_SettingsPath
	global G_ComponentDataPath

	# This is set in workspace.mel file and stores project path
	G_WorkspacePath = mel.eval("$temp=$ws")   
	G_SettingsPath = G_WorkspacePath + "scripts/MALLData"
	G_ComponentDataPath = G_WorkspacePath + "scripts/MALLComponents.csv"


def LoadSettingsFromFile():

	global G_SettingsPath 
	global G_MALLSettings

	pickle_in = open(G_SettingsPath, "rb") 
	G_MALLSettings =	pickle.load(pickle_in)


def BuildSettings(self):

	print "rebuilding settings"

	global G_MALLSettings
	global G_SettingsPath

	G_MALLSettings = MALL_Settings()
	csvSheetData = CSVSheetData()

	actorNames = csvSheetData.GetActorNamesInCSV()

	del G_MALLSettings.actors[:]


	Minnie = MALL_Char("Minnie") 
	Incidental6 = MALL_Char("Incidental6") 

	# HARDCODED ORDER, CORRESPONDS TO .CSV LINE IN COMPONENTS DOCUMENT (or should)
	#G_MALLSettings.actors = [Minnie, Incidental6]
	#G_MALLSettings.actors.append(Minnie)
	#G_MALLSettings.actors.append(Incidental6)

	tempList = []
	# trying to build actor classes automatically, reading rows from csv sheet as actor list
	for actorName in actorNames:

		newActor = MALL_Char(actorName)
		#newActor = MALL_Char("TEST")
		tempList.append(newActor)

	# if I append actors to the G_MALLSettings list straight away it doesn't pickle, I don't know why but this is a workaround
	G_MALLSettings.actors = tempList

	# assigning csv row index
	i = 0
	for actor in G_MALLSettings.actors:
		i+=1
		actor.csvLine = i



	# writing actor data from csv to actor class
	for actor in G_MALLSettings.actors:
		print "building settings for " + actor.name + ", line ID: " + str(actor.csvLine)

		actor.filepath = csvSheetData.GetFilePath(actor)
		actor.bakeCube = csvSheetData.GetBakeCube(actor)
		actor.namespace = csvSheetData.GetNamespace(actor)

		actor.root = csvSheetData.GetRoot(actor)		
		actor.anchor = csvSheetData.GetAnchor(actor)	

		#G_MALLSettings.actorsByName.update({actor.name : actor})


	print len(G_MALLSettings.actors)	
	#print len(G_MALLSettings.actorsByName)

	print "saving actors to " + G_SettingsPath
	pickle_out = open(G_SettingsPath,"wb") 
	pickle.dump(G_MALLSettings,	pickle_out)
	# protocol=pickle.HIGHEST_PROTOCOL 
	pickle_out.close()

def ImportSpaceRig(*args):
	global G_WorkspacePath

	transforms = pm.ls("::*SpaceRig")
	if(len(transforms) != 0):
		mc.error("Already exists")
	else:
		pm.createReference("$RIGS/SpaceRig.ma")		
		#pm.createReference(G_WorkspacePath + "RIGS/SpaceRig.ma")

def CheckForSpaceRig():

	transforms = pm.ls("::*SpaceRig*")
	if(len(transforms) == 0):
		mc.error("no Space Rig found")

def RebuildSpaceRig(self):

	global G_MALLSettings

	for actor in G_MALLSettings.actors:
		print actor.name
		actor.BuildSpaceRig()


def FilterActorsInScene(self):

	global G_MALLSettings

	cubeSearch = pm.ls("::*"+"_BAKE")
	actorNames = []
	filteredActors = []


	for result in cubeSearch: 
		print result
		r2 = result.replace('_BAKE', '')		
		r3 = r2.split(":")[-1]
		#print r3
		actorNames.append(r3)

	for name in actorNames:
		actor = G_MALLSettings.GetActorByname(name)
		if(actor == None):
			print "no actor found for " + name
		filteredActors.append(actor)

	ShowUIWithActorsFiltered(filteredActors)




class MALL_Settings():

	actors = []

	def GetActorByname(self, name):
		for actor in self.actors:
			if(actor.GetName() == name):
				return actor

		return None


	def __init__(self):  
		pass

class MALL_Actor():

	csvLine = -1
	filepath = ""

	namespace = ""
	bakeCube = "" 
	anchor = "" 

	# Space Rig components
	_space_In = ""

	 # Constructor     
	def __init__(self, name):
		self.name = name

	def GetName(self):          
		return self.name

	# override
	def GetTemplate(self):
		return "";

	def GetSpaceRigComponents(self): 
		self._space_In = pm.ls("::*In_" + self.name)[0] 
		#print "In: " + self._space_In

	def BuildSpaceRig(self):

		newRig = self._DuplicateSpaceRigTemplate()
		# gotta fix names first because we refer to components by names uu
		self._FixSpaceRigNaming(newRig)
		self._BuildParentSpaceHooks(newRig)


	def _DuplicateSpaceRigTemplate(self): 
		template = self.GetTemplate() 
		print ("Duplicating " + template + " for " + self.name) 
		return pm.duplicate(template, upstreamNodes=True, name=self.name)[0]

	# override
	def _FixSpaceRigNaming(self, spaceRig): print ("main")

	# override
	def _BuildParentSpaceHooks(self, spaceRig): print ("main")

	def CreateRigReference(self):
		global G_WorkspacePath

		#rigPath = G_WorkspacePath + self.filepath
		rigPath = "$" + self.filepath

		if(self.filepath != ""):
			pm.createReference(rigPath, namespace = self.namespace)
		else:
			mc.error("No rig path on file")

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

class MALL_Char(MALL_Actor):


	isBoat = False
	uiSelectOption = 0

	# component info from CSV sheet
	root = ""

	# space rig components, fetched from scene
	_space_Out_Root = "" 
	_space_Out_Anchor = ""
	_space_Parent = ""
	_space_BlendNode = ""

	def GetTemplate(self): 
		return pm.ls("::*Template_Character*")[0]

	def _BuildParentSpaceHooks(self, spaceRig):

		self.GetSpaceRigComponents()
		#decomp = pm.listConnections(self._space_Parent, source=True, destination=False, t="decomposeMatrix")[0]
		#boatSpaceBlend = pm.listConnections(decomp, source=True, destination=False, t="blendMatrix")[0]

		print self._space_In
		# hard coded parent spaces to switch between
		spaces = [pm.ls(self._space_Out_Root)[0]] 

		#pm.ls("WORLD")[0]]

		i = 0
		for space in spaces:
			#print space
			attrA = space + ".worldMatrix[0]"
			attrB = self._space_BlendNode + ".target[" + str(i) + "]" + ".targetMatrix"
			#print attrA
			#print attrB
			pm.connectAttr(attrA, attrB)
			i+=1

	def _FixSpaceRigNaming(self, spaceRig): 
		for item in spaceRig.getChildren():
			item.rename(item.name().replace('Char', self.GetName()))

	def GetSpaceRigComponents(self): 
		MALL_Actor.GetSpaceRigComponents(self)
		self._space_Parent = self.FindTransform("In_ParentSpace_" + self.name)
		self._space_Out_Root = self.FindTransform("Out_Root_" + self.name)
		self._space_Out_Anchor = self.FindTransform("Out_Anchor_" + self.name)


		decomp = pm.listConnections(self._space_Parent, source=True, destination=False, t="decomposeMatrix")[0]
		self._space_BlendNode = pm.listConnections(decomp, source=True, destination=False, t="blendMatrix")[0]
		#print "Out_Anchor: " + _space_Out_Anchor print "Out_Root: " +
		#_space_Out_Root

	def ParentActorSpace(self): 
		self.GetSpaceRigComponents() 

		anchorTr = self.FindTransform(self.anchor, inNamespace=True)  
		rootCtrl = self.FindTransform(self.root, inNamespace=True)

		# setting parent space to whichever boat they're on by default
		print self._space_Parent
		pm.setAttr( (self._space_Parent + '.ParentSpace'), 0)

		pm.parentConstraint(self._space_Out_Anchor,	anchorTr, maintainOffset=False)
		pm.parentConstraint(self._space_Out_Root, rootCtrl,	maintainOffset=False)

	


	def BakeRoot(self):

		self.GetSpaceRigComponents()

		spaceEnum = pm.getAttr(self._space_Parent + '.ParentSpace')
		isWorldSpace = (spaceEnum == 0)

		if(isWorldSpace):
			confirm = pm.confirmDialog(message = "This will bake the character in world space. Is that what you mean to do?", button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
			if confirm == 'Yes':
				self._SetWorldSpaceToFirstFrame()
				self._BakeKeys()

			else:
				mc.warning("Bake canceled")

		else:
			self._BakeKeys()
		#bakeResults -simulation true -t "0:153" -sampleBy 1 -oversamplingRate 1 -disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake true -removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {"hammerheadShark_rig:ROOT_CTL"};

	def _SetWorldSpaceToFirstFrame(self, *args):

		self.GetSpaceRigComponents()
		pm.currentTime(0, edit=True)
		spaceInMatrix = pm.getAttr(self._space_Out_Root + '.worldMatrix')
		pm.disconnectAttr(self._space_BlendNode + '.target[0].targetMatrix')
		pm.setAttr(self._space_BlendNode + '.target[0].targetMatrix', spaceInMatrix)

	def _BakeKeys(self):

		rootCtrl = self.FindTransform(self.root, inNamespace=True)
		timeRange = str(int(mc.playbackOptions(q=True, minTime=True)))
		timeRange += ":"
		timeRange += str(int(mc.playbackOptions(q=True, maxTime=True)))
		print timeRange
		pm.bakeResults(rootCtrl, t=timeRange)
		pm.select(rootCtrl)

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
		elif(component == "Parent Attach"):
			self.GetSpaceRigComponents()
			pm.select(self._space_Parent)
		else:
			print "select menu option not found"

	def ToOrigin(self, revert=False):

		i = not revert
		print i
		mc.setAttr(self._space_Out_Anchor + '.ToOrigin', 1)


class CSVSheetData():

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

	def GetActorNamesInCSV(self):
		rows = list(self._csvList)
		actors = []
		for row in rows:
			actors.append(row[0])
		#gotta skip first
		del actors[0]

		print "actor names in .csv:"
		for actor in actors:
			print actor

		return actors



	def GetActorName(self, actor):

		return self.GetColumnData(actor, columnNo=0)

	def GetNamespace(self, actor):

		return self.GetColumnData(actor, columnNo=1)

	def GetBakeCube(self, actor):

		return self.GetColumnData(actor, columnNo=2)

	def GetAnchor(self, actor):

		return self.GetColumnData(actor, columnNo=3)

	def GetRoot(self, actor):

		return self.GetColumnData(actor, columnNo=4)

	def GetFilePath(self, actor):

		return self.GetColumnData(actor, columnNo=5)

RunMALL()



