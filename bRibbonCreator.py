import math

import maya.api.OpenMaya as om
import maya.cmds as mc
import maya.mel as mel

from RigLibrary.base import control

from Utils import ParentOffsetMatrixTransfer

## REQUIRES CLEANING OF HIERARCHY
##Creation of Ribbon

UDirection = (0, 0, 0)
VDirection = (0, 0, 0)


class Ribbon():

    # TODO EXPOSED VARIABLES HERE : Length, Width, Name, UPatches, ControlJoints, RibbonType, SurfaceDegree
    def __init__(self,
                 name="defaultRibbon",
                 VWidth=1,
                 ULength=1,
                 U_Patches=1,
                 surfaceDegree=3,
                 controlJointsNumber=0,
                 ribbonType="Normal",
                 translateTo="",
                 rotateTo="",
                 rootSize = 1,
                 ctrlsSize = 1):

        """

        :param name: name of the ribbon in the hierarchy, string
        :param width: width of the ribbon, float
        :param length: length of the ribbon, length
        :param U_Patches: number of U divisions on the ribbon, int
        :param V_Patches: number of V divisions on the ribbon, int
        :param surfaceDegree: the surface degree of the nurb plane, can be in [1,2,3,5,7]
        :param axis: initial direction of the ribbon, can be only [X,Y,Z]
        :param parentTo: the parent of the ribbon, str
        :param translateTo: the object to translate the ribbon to, str
        :param rotateTo: the object to rotate the ribbon to, str
        :param lockChanels: the chanels to lock in the ribbon, char[]
        """

        self.name = name
        self.vWidth = VWidth
        self.uLength = ULength
        self.uPatches = U_Patches
        self.surfaceDegree = surfaceDegree
        self.controlJointsNumber = controlJointsNumber
        self.ribbonType = ribbonType
        self.rootSize = rootSize
        self.ctrlsSize = ctrlsSize

        # Checking if surface degree is a correct number
        if surfaceDegree not in [1, 2, 3, 5, 7]:
            raise ValueError("Please enter a correct number for the surface degree")

        ribbon = mc.nurbsPlane(n=name + "_ribbon", d=surfaceDegree, u=U_Patches, w=VWidth, ch=False,
                               lr=ULength, ax=(0, 1, 0))
        ribbonShape = mc.listRelatives(ribbon, shapes=True)[0]

        equidistantSpacing = 1 / U_Patches

        uCoordinate = 0

        ctrls = []
        follicleJoints = []
        follicles = []

        folliclesGrp = mc.group(n="folliclesGrp", em=1)
        ctrlsGrp = mc.group(n="ctrlsGrp", em=1)

        for i in range(U_Patches + 1):
            follicle_name = "test_follicle"

            follicle = mc.createNode("follicle", n=follicle_name)
            follicle_trans = mc.listRelatives(follicle, p=True, type="transform")[0]

            follicles.append(follicle_trans)

            mc.connectAttr(follicle + ".outRotate", follicle_trans + ".rotate")
            mc.connectAttr(follicle + ".outTranslate", follicle_trans + ".translate")

            mc.connectAttr(ribbonShape + ".local", follicle + ".inputSurface")
            mc.connectAttr(ribbonShape + ".worldMatrix[0]", follicle + ".inputWorldMatrix")

            mc.setAttr(follicle + ".parameterU", uCoordinate)
            mc.setAttr(follicle + ".parameterV", 0.5)

            uCoordinate += equidistantSpacing

            # Making multiple follicles

            # making joints in each follicle

            joint = mc.joint(n=f"ribbonJoint{i + 1}")

            mc.makeIdentity(joint, translate=True, rotate=True, jointOrient=True)

            follicleJoints.append(joint)

            mc.parent(follicle_trans, folliclesGrp)

        # ATTACHING CONTROL JOINTS AND CONTROLS TO THE CONTROL JOINTS DEPENDING ON HOW MANY THE USER WANTS

        numberOfJoints = len(follicleJoints)

        spacingCtrlJoints = int(numberOfJoints / controlJointsNumber)

        ctrlJoints = []
        ctrlJointDistance = 0

        ctrlJointsGrp = mc.group(n="ctrlJointsGrp", em=1)

        while (ctrlJointDistance <= numberOfJoints - 1):
            ctrlJoint = \
            mc.duplicate(follicleJoints[ctrlJointDistance], n=follicleJoints[ctrlJointDistance] + "_ctrlJnt",
                         parentOnly=True)[0]
            mc.setAttr(ctrlJoint + ".radius", 10)
            mc.parent(ctrlJoint, ctrlJointsGrp)

            ParentOffsetMatrixTransfer.parentOffsetTransfer(ctrlJoint)
            ctrlJoints.append(ctrlJoint)

            ctrl = control.Control(prefix=follicleJoints[ctrlJointDistance], scale= self.ctrlsSize,
                                   translateTo=ctrlJoint, rotateTo=ctrlJoint,
                                   shape="circleX", parentTo="", lockChanels=["s"], allowParentOffsetTransfer=True)
            print(self.ctrlsSize)

            ctrls.append(ctrl)

            mc.connectAttr(ctrl.C + ".worldMatrix[0]", ctrlJoint + ".offsetParentMatrix")
            # mc.connectAttr(ctrl.C + ".translate", ctrlJoint + ".translate")
            # mc.connectAttr(ctrl.C + ".rotate", ctrlJoint + ".rotate")

            ctrlJointDistance += spacingCtrlJoints

            mc.parent(ctrl.C, ctrlsGrp)

        # SKINING CONTROL JOINTS AND THE RIBBON PLANE

        # HIDING RIBBON OBJECTS

        for i in range(len(ctrlJoints)):
            mc.hide(ctrlJoints[i])

        for i in range(len(follicleJoints)):
            mc.hide(follicleJoints[i])
            mc.hide(follicles[i])

        # CLEANING HIERARCHY

        mainRibbonGroup = mc.group(name=name + "_RibbonGroup", em=1)
        mc.parent(ribbon, mainRibbonGroup)
        mc.parent(ctrlJointsGrp, mainRibbonGroup)
        mc.parent(ctrlsGrp, mainRibbonGroup)
        mc.parent(folliclesGrp, mainRibbonGroup)

        # ATTACHING OBJECT AND RIBBON PLANE TOGETHER

        # CREATING MAIN CONTROLLER

        ctrl = control.Control(prefix=name + "_rootCtrl", scale= self.rootSize,
                               translateTo=ctrlJoints[0], rotateTo=ctrlJoints[0],
                               shape="circleX", parentTo="", lockChanels=["s"], allowParentOffsetTransfer=True,)
        print(self.rootSize)
        for i in range(len(ctrls)):
            mc.parent(ctrls[i].C, ctrl.C)
        mc.parent(ctrl.C, mainRibbonGroup)

        # CREATING DUPLICATES OF RIBBONS ( SIN-RIBBON etc )

        # CONSTRAINT OF RIBBONS TO MAIN RIBBON'S BIG JOINTS

        # CREATING BLENDSHAPE

        # CREATING SIN LOGIC

        if (ribbonType == "Automated Sine-Based" or ribbonType == "Automated Fully"):

            mc.addAttr(ctrl.C, ln="sine", nn="======", at="enum", enumName="SINE", k=1)

            amplitudeZ = mc.addAttr(ctrl.C, longName="amplitudeZ", attributeType='double', defaultValue=0.0,
                                    keyable=True)
            frequencyZ = mc.addAttr(ctrl.C, longName="frequencyZ", attributeType='double', defaultValue=0.0,
                                    keyable=True)
            phaseOffsetZ = mc.addAttr(ctrl.C, longName="phaseOffsetZ", attributeType='double', defaultValue=0.0,
                                      keyable=True)
            offsetZ = mc.addAttr(ctrl.C, longName="offsetZ", attributeType='double', defaultValue=0.0, keyable=True)


            # SIN LOGIC
            for i in range(len(ctrls)):  # Iterate through the joints
                sineWaveValue = mc.addAttr(ctrls[i].C, longName="sinWaveValue", attributeType='double',
                                           defaultValue=1.0,
                                           keyable=True, hidden=True)

                sinExpression = f"""
    
                                float $frame;
                                $frame = `currentTime -q`;
                                float $sinWaveValueZ = {ctrl.C}.amplitudeZ * sin( ($frame * {ctrl.C}.frequencyZ)  + {i} *  {ctrl.C}.phaseOffsetZ + {ctrl.C}.offsetZ);
                                {ctrls[i].C}.translateZ = $sinWaveValueZ;
                                
                                """
                # mc.setAttr(f"{ctrls[i].C}.translateZ", keyable=True)
                sinNodeExpression = mc.expression(s=sinExpression, o=ctrls[i].C)

        if (ribbonType == "Normal"):

            volumeRibbon = mc.nurbsPlane(n=name + "_volume", d=surfaceDegree, u=U_Patches, w=VWidth, ch=False,
                                         lr=ULength, ax=(0, 1, 0))[0]

            sinRibbon = mc.nurbsPlane(n=name + "_sin", d=surfaceDegree, u=U_Patches, w=VWidth, ch=False,
                                      lr=ULength, ax=(0, 1, 0))[0]
            twistRibbon = mc.nurbsPlane(n=name + "_twist", d=surfaceDegree, u=U_Patches, w=VWidth, ch=False,
                                        lr=ULength, ax=(0, 1, 0))[0]

            rollRibbon = mc.nurbsPlane(n=name + "_roll", d=surfaceDegree, u=U_Patches, w=VWidth, ch=False,
                                       lr=ULength, ax=(0, 1, 0))[0]

            blendShapeRibbons = [sinRibbon, twistRibbon, rollRibbon]

            blendShapeNode = mc.blendShape(rollRibbon, volumeRibbon, sinRibbon, twistRibbon, ribbon)[0]

            ribbonBS_group = mc.group(n= name + "ribbons_BS", em=1)

            # CREATION OF TWIST DEFORMER

            twist_deformer = mc.nonLinear(twistRibbon, type="twist")
            twistHandle = twist_deformer[1]
            mc.setAttr(twistHandle + ".rotateZ", 90)
            mc.parent(twistHandle, ribbonBS_group)
            print(twist_deformer)

            # CREATION OF SIN DEFORMER

            sin_deformer = mc.nonLinear(sinRibbon, type="sine")
            sineHandle = sin_deformer[1]
            mc.setAttr(sineHandle + ".rotateZ", 90)
            mc.parent(sineHandle, ribbonBS_group)
            print(sin_deformer)

            # CREATION OF ROLL DEFORMER

            roll_deformer = mc.nonLinear(rollRibbon, type="bend")
            rollHandle = roll_deformer[1]
            mc.setAttr(rollHandle + ".rotateZ", 90)

            mc.parent(rollHandle, ribbonBS_group)
            print(roll_deformer)

            # HIDING BLENDSHAPE RIBBONS

            volume_deformer = mc.deformer(volumeRibbon, type="sculpt")
            print(volume_deformer)


            mc.parent(ribbonBS_group, ctrl.C)
            # TODO THIS IS TEMPORARY UNTIL IMPLEMENTING VOLUME

            handles = [sineHandle, twistHandle, rollHandle]
            for handle, blendShapeRibbon in zip(handles, blendShapeRibbons):
                mc.parent(handle, blendShapeRibbon)
                mc.hide(blendShapeRibbon)
                mc.hide(handle)

                mc.parent(volumeRibbon, blendShapeRibbon)
                mc.parent(blendShapeRibbon, ribbonBS_group)

            # EXPOSING VARIABLES

            # 1-SINE

            mc.addAttr(ctrl.C, ln="sine", nn="======", at="enum", enumName="SINE", k=1)

            sineBlend = mc.addAttr(ctrl.C, longName="sineBlend", attributeType="double", defaultValue=1.0, keyable=True)

            amplitudeZ = mc.addAttr(ctrl.C, longName="amplitudeZ", attributeType='double', defaultValue=0.0,
                                    keyable=True)
            frequencyZ = mc.addAttr(ctrl.C, longName="frequencyZ", attributeType='double', defaultValue=0.0,
                                    keyable=True)
            phaseOffsetZ = mc.addAttr(ctrl.C, longName="phaseOffsetZ", attributeType='double', defaultValue=0.0,
                                      keyable=True)
            dropoffZ = mc.addAttr(ctrl.C, longName="dropoffZ", attributeType='double', defaultValue=0.0, keyable=True)

            # LINKING SINE VALUES

            # TODO : THIS A TEMPORARY IMPLEMENTATION, THIS IS NOT ENOUGH
            mc.connectAttr(ctrl.C + ".sineBlend", blendShapeNode + "." + sinRibbon)
            mc.connectAttr(ctrl.C + ".amplitudeZ", sineHandle[:5] + ".amplitude")
            mc.connectAttr(ctrl.C + ".frequencyZ", sineHandle[:5] + ".wavelength")
            mc.connectAttr(ctrl.C + ".phaseOffsetZ", sineHandle[:5] + ".offset")
            mc.connectAttr(ctrl.C + ".dropoffZ", sineHandle[:5] + ".dropoff")

            # 2- TWIST

            mc.addAttr(ctrl.C, ln="twist", nn="======", at="enum", enumName="TWIST", k=1)

            sineBlend = mc.addAttr(ctrl.C, longName="twistBlend", attributeType="double", defaultValue=1.0,
                                   keyable=True)

            amplitudeZ = mc.addAttr(ctrl.C, longName="startAngle", attributeType='double', defaultValue=0.0,
                                    keyable=True)
            frequencyZ = mc.addAttr(ctrl.C, longName="endAngle", attributeType='double', defaultValue=0.0,
                                    keyable=True)

            # LINKING SINE VALUES

            mc.connectAttr(ctrl.C + ".twistBlend", blendShapeNode + "." + twistRibbon)
            mc.connectAttr(ctrl.C + ".startAngle", twistHandle[:6] + ".startAngle")
            mc.connectAttr(ctrl.C + ".endAngle", twistHandle[:6] + ".endAngle")

            # 3- BEND

            mc.addAttr(ctrl.C, ln="roll", nn="=========", at="enum", enumName="ROLL", k=1)
            mc.setAttr(rollHandle[:5] + ".highBound", 0)

            rollBlend = mc.addAttr(ctrl.C, longName="rollBlend", attributeType="double", defaultValue=1.0, keyable=True)

            curvature = mc.addAttr(ctrl.C, longName="curvature", attributeType="double", defaultValue=0.0, keyable=True)

            mc.connectAttr(ctrl.C + ".curvature", rollHandle[:5] + ".curvature")
            mc.connectAttr(ctrl.C + ".rollBlend", blendShapeNode + "." + rollRibbon)

            # BEND EXPRESSION AUTOMATIC

            mc.hide(volumeRibbon)

        # SKINNING

        # TODO HERE IS THE SKIN CLUSTER
        ribbonSkinCluster = mc.skinCluster([ctrlJoints[i] for i in range(len(ctrlJoints))], ribbon, tsb=True)[0]

        for i in range(len(ctrlJoints)):
            mc.skinPercent(ribbonSkinCluster, ribbon, transform=ctrlJoints[i])

            if translateTo:
                mc.delete(mc.pointConstraint(translateTo, ctrl.C))

            # ROTATING THE CONTROL

            if rotateTo:
                mc.delete(mc.orientConstraint(rotateTo, ctrl.C))
