import FWCore.ParameterSet.Config as cms

looper = cms.Looper("EcalTimingCalibProducer",
                    maxLoop = cms.uint32(2),
                    isSplash = cms.bool(True if options.isSplash == 1 else  False),
                    makeEventPlots = cms.bool(evtPlots),
                    recHitEBCollection = cms.InputTag("ecalRecHit","EcalRecHitsEB"),
                    recHitEECollection = cms.InputTag("ecalRecHit","EcalRecHitsEE"),
                    recHitFlags = cms.vint32([0]), # only recHits with these flags are accepted for calibration
                    #recHitMinimumN = cms.uint32(10),
                    recHitMinimumN = cms.uint32(2),
                    minRecHitEnergy = cms.double(1),
                    minRecHitEnergyStep = cms.double(0.5),
                    minEntries = cms.uint32(1),
                    globalOffset = cms.double(options.offset),
                    produceNewCalib = cms.bool(True),
                    outputDumpFile = process.TFileService.fileName,
                    noiseRMSThreshold = cms.double(0.5),
                    noiseTimeThreshold = cms.double(2.0)
                    )