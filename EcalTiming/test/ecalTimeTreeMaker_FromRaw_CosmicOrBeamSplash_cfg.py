import FWCore.ParameterSet.Config as cms
import os, sys, imp, re
import FWCore.ParameterSet.VarParsing as VarParsing

#sys.path(".")
############################################################
### SETUP OPTIONS
options = VarParsing.VarParsing('standard')
options.register('jsonFile',
                 "",
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "path and name of the json file")
options.register('offset',
                 0.0,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.float,
                 "add this to each crystal time")
options.register('isSplash',
                 0,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "0=false, 1=true"
                 )
### setup any defaults you want
options.output="ecalTiming.root"
options.secondaryOutput="ntuple.root"
options.files= ""
options.maxEvents = -1 # -1 means all events
### get and parse the command line arguments
options.parseArguments()
print options

process = cms.Process("TIMECALIBANALYSIS")

#dataset=/MinimumBias/Commissioning2015-v1/RAW run=243506


process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')

if(options.isSplash==1):
    ## Get Cosmic Reconstruction
    process.load('Configuration/StandardSequences/ReconstructionCosmics_cff')
    process.caloCosmics.remove(process.hbhereco)
    process.caloCosmics.remove(process.hcalLocalRecoSequence)
    process.caloCosmics.remove(process.hfreco)
    process.caloCosmics.remove(process.horeco)
    process.caloCosmics.remove(process.zdcreco)
    process.caloCosmics.remove(process.ecalClusters)
    process.caloCosmicOrSplashRECOSequence = cms.Sequence(process.caloCosmics )#+ process.egammaCosmics)
else:
    process.load('Configuration/StandardSequences/Reconstruction_cff')
    process.recoSequence = cms.Sequence(process.calolocalreco )#+ process.egammaCosmics)

process.load('PhiSym.EcalCalibAlgos.ecalPhiSymLocarecoWeights_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')


## Raw to Digi
process.load('Configuration/StandardSequences/RawToDigi_Data_cff')

## HLT Filter Splash
import HLTrigger.HLTfilters.hltHighLevel_cfi
process.spashesHltFilter = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone(
    throw = cms.bool(False),
    HLTPaths = ['HLT_EG20*', 'HLT_SplashEcalSumET', 'HLT_Calibration','HLT_EcalCalibration','HLT_HcalCalibration','HLT_Random','HLT_Physics','HLT_HcalNZS','HLT_SplashEcalSumET','HLTriggerFinalPath' ]
)


## Do you want to Pre-Scale
process.load("FWCore.Modules.preScaler_cfi")
process.preScaler.prescaleFactor = 1
## GlobalTag Conditions Related
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')

## Process Digi To Raw Step
process.digiStep = cms.Sequence(process.ecalDigis  + process.ecalPreshowerDigis)

## Process Reco






# Dump Some event Content
import FWCore.Modules.printContent_cfi
process.dumpEv = FWCore.Modules.printContent_cfi.printContent.clone()

### Print Out Some Messages
process.MessageLogger = cms.Service("MessageLogger",
    cout = cms.untracked.PSet(
        threshold = cms.untracked.string('WARNING')
    ),
    categories = cms.untracked.vstring('ecalTimeTree'),
    destinations = cms.untracked.vstring('cout')
)
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(1000)

# enable the TrigReport and TimeReport
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
#    SkipEvent = cms.untracked.vstring('ProductNotFound')
)

# dbs search --query "find file where dataset=/ExpressPhysics/BeamCommissioning09-Express-v2/FEVT and run=124020" | grep store | awk '{printf "\"%s\",\n", $1}'
# Input source
process.source = cms.Source("PoolSource",
    secondaryFileNames = cms.untracked.vstring(),
    #  fileNames = cms.untracked.vstring('file:test_DIGI.root')
 	 fileNames = cms.untracked.vstring(options.files),
)

# process.source = cms.Source(
#     "PoolSource",
#     skipEvents = cms.untracked.uint32(0),
#     fileNames = cms.untracked.vstring(
#     #'file:MyCrab/50988619-41DE-E211-9F98-003048FFD770.root'
#     #'root://xrootd.unl.edu//store/data/Run2010B/Cosmics/RAW/v1/000/144/556/C8B5FCA9-F3B5-DF11-B28A-0030487CD16E.root'
#     #'file:Cosmic-Commissioning2014-Cosmics-RAW-v1-AC4963B3-54BE-E311-97F5-02163E00E6E3.root'
#     #'/store/data/Commissioning2015/Cosmics/RAW-RECO/CosmicSP-6Mar2015-v1/10000/248747E6-25CA-E411-B17C-02163E00BD75.root'
#     #'/store/data/Run2010B/Cosmics/RAW/v1/000/144/559/306A4ABD-F3B5-DF11-9CAD-003048F118C6.root'
#     '/store/data/Commissioning2015/Cosmics/RAW/v1/000/232/881/00000/26ADAFFB-3FAB-E411-A313-02163E011DDC.root'
#      ),               
#     # drop native rechits and clusters, to be sure only those locally made will be picked up
#     inputCommands = cms.untracked.vstring('keep *'
#                                           ,'drop EcalRecHitsSorted_*_*_RECO' # drop hfRecoEcalCandidate as remade in this process
#                                           , 'drop recoSuperClusters_*_*_RECO' # drop hfRecoEcalCandidate as remade in this process
#                                           , 'drop recoCaloClusters_*_*_RECO'
#                                           )


# Output definition
process.RECOoutput = cms.OutputModule("PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    outputCommands = process.RECOEventContent.outputCommands,
    fileName = cms.untracked.string('test_RECO.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('RECO')
    )
)


## Histogram files
process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string(options.output),
                                   closeFileFast = cms.untracked.bool(True)
                                   )

## Dumpevent Event Contents
process.dumpEvContent = cms.EDAnalyzer("EventContentAnalyzer")

### NumBer of events
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(options.maxEvents))


process.filter=cms.Sequence()
if(options.isSplash==1):
    process.filter+=process.spashesHltFilter
    process.reco_step = cms.Sequence(process.caloCosmicOrSplashRECOSequence)
else:
    process.reco_step = cms.Sequence(process.reconstruction_step_multiFit)

### Process Full Path
if(options.isSplash==0):
    process.digiStep = cms.Sequence()

process.p = cms.Path( process.filter #+ process.preScaler 
                      + process.digiStep 
                      + process.reco_step
                      )

process.endp = cms.EndPath(process.RECOoutput)

### Schedule ###
process.schedule = cms.Schedule(process.p) # , process.endp) 

process.looper = cms.Looper("EcalTimingCalibProducer",
                            maxLoop = cms.uint32(2),
                            isSplash = cms.bool(True if options.isSplash == 1 else  False),
                            makeEventPlots = cms.bool(True),
                            recHitEBCollection = cms.InputTag("ecalRecHit","EcalRecHitsEB"),
                            recHitEECollection = cms.InputTag("ecalRecHit","EcalRecHitsEE"),
                            recHitFlags = cms.vint32([0]), # only recHits with these flags are accepted for calibration
                            recHitMinimumN = cms.uint32(10),
                            #recHitMinimumN = cms.uint32(2),
                            minRecHitEnergy = cms.double(1),
                            globalOffset = cms.double(options.offset),
                            produceNewCalib = cms.bool(True),
                            outputDumpFile = process.TFileService.fileName,
                            noiseRMSThreshold = cms.double(0.5),
                            noiseTimeThreshold = cms.double(2.0)
                            )

processDumpFile = open('processDump.py', 'w')
print >> processDumpFile, process.dumpPython()
