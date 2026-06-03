#PY  <- Needed to identify #
#--automatically built--

adm = Avidemux()
if not adm.loadVideo("/tmp/test.mkv"):
    raise("Cannot load /tmp/test.mkv")
adm.clearSegments()
adm.addSegment(0, 79937000, 741141000)
adm.addSegment(0, 973096000, 568218000)
adm.addSegment(0, 1733256000, 507674000)
adm.addSegment(0, 2457913000, 332732000)
adm.addSegment(0, 3038960000, 448014000)
adm.markerA = 0
adm.markerB = 2597779000
adm.setHDRConfig(1, 1, 1, 1, 0)
adm.videoCodec("Copy")
adm.audioClearTracks()
adm.setSourceTrackLanguage(0,"eng")
adm.setSourceTrackLanguage(1,"spa")
if adm.audioTotalTracksCount() <= 0:
    raise("Cannot add audio track 0, total tracks: " + str(adm.audioTotalTracksCount()))
adm.audioAddTrack(0)
adm.audioCodec(0, "copy")
adm.audioSetDrc2(0, 0, 1, 0.001, 0.2, 1, 2, -12)
adm.audioSetEq(0, 0, 0, 0, 0, 880, 5000)
adm.audioSetChannelGains(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
adm.audioSetChannelDelays(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
adm.audioSetChannelRemap(0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8)
adm.audioSetShift(0, 0, 0)
if adm.audioTotalTracksCount() <= 1:
    raise("Cannot add audio track 1, total tracks: " + str(adm.audioTotalTracksCount()))
adm.audioAddTrack(1)
adm.audioCodec(1, "copy")
adm.audioSetDrc2(1, 0, 1, 0.001, 0.2, 1, 2, -12)
adm.audioSetEq(1, 0, 0, 0, 0, 880, 5000)
adm.audioSetChannelGains(1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
adm.audioSetChannelDelays(1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
adm.audioSetChannelRemap(1, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8)
adm.audioSetShift(1, 0, 0)
adm.setContainer("MKV", "forceAspectRatio=False", "displayWidth=1280", "displayAspectRatio=2", "addColourInfo=False", "colMatrixCoeff=2", "colRange=0", "colTransfer=2", "colPrimaries=2")
