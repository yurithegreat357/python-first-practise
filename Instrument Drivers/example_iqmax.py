
import logging
from ...iqmax import IQmeasure as iqmeasure
from ...iqmax import IQsequence as iqsequence

log = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s', level=logging.INFO)


class example_IQMAX_test(object):
    instrument_address="192.168.106.19"
    def __init__(self,instrument_address):
        self.instrument_address=instrument_address

    def initial(self):
        self.iq_measure = iqmeasure.Driver(resource=self.instrument_address)
        self.iq_sequence = iqsequence.Driver()
        return 0

    def IQMAX_test(self):
        log.info("Step 1: Initialize the Driver")
        # iq_measure = iqmeasure.Driver(resource=self.instrument_address)
        # iq_sequence = iqsequence.Driver()


        log.info("Step 2: Get version")
        version = self.iq_measure.get_version(buff_size=256)
        log.info(version)

        log.info("Step 3:Mpa initialize")
        self.iq_sequence.LP_MpsInit()

        log.info("Step 4:MPA version")
        Mpsversion = self.iq_sequence.LP_MpsGetVersion(buff_size=2048)
        log.info(Mpsversion)

        log.info("Step 5:Get serial number")
        serial = self.iq_sequence.LP_MptaGetSerialNumber(buffer_size=256)
        log.info(serial)

        # Play 3 segments
        log.info("Step 6: LP_SetVsa")
        self.iq_measure.LP_SetVsa(freq=2412e6, rfamp_db=-44.597 ,port=2, extAttenDb=0,triggerLevelDb=-15)

        log.info("Step 7: Set Vsg")
        self.iq_measure.LP_SetVsg()

        log.info("Step 8:Set VSG modulation")
        condition = self.iq_measure.LP_SetVsgModulation_SetPlayCondition(modFileName='C:\Development\projects\WNBU\Antigua_WIN7'
                                                                             '\Antigua_PM3\Instruments\LitePoint_LV\\6OFDM_BPSK_1000B.mod')
        log.info("Step 9:MPA RXA testing")
        self.iq_sequence.LP_MpsRxPer_MIMO()

        log.info("Step 10:MPA get results")
        power_level, packet, ack_received, per, array_size=self.iq_sequence.LP_MptaGetRxPerResults(step_index=0)
        log.info("Power level:{0}\npacket send:{1}\nAckreceived:{2}\nPer:{3}\narray size:{4}\n".format(power_level, packet,
                                                                                                       ack_received, per, array_size))
        log.info("Step 11:Get scalar measurement")
        result = self.iq_measure.LP_GetScalarMeasurement(measurement='demodulation')
        log.info("The result is {}".format(result))

        log.info("Step 12:Get string measurement")
        result1= self.iq_measure.LP_GetStringMeasurment()
        log.info("The result is {}".format(result1))

        log.info("Step 13:Get scalar measurement")
        result = self.iq_measure.LP_GetScalarMeasurement(measurement='P_av_no_gap_all_dBm')
        log.info("The result is {}".format(result))
        #mimo13
        log.info("Step 14: Set Vsg")
        self.iq_measure.LP_SetVsg(rfFreqHz=2.437e+9, port=3, rfGainDb=-50)

        log.info("Step 15: capture MPTA")
        self.iq_sequence.LP_MptaDirectCapture()

        log.info("Step 16: measure AGC")
        agc_value=self.iq_measure.query_agc()
        log.info('The AGC value is {}'.format(agc_value))

        log.info("Step 17:Set VSA Bluetooth")
        self.iq_measure.LP_SetVsaBluetooth(rfFreqHz=2412e6, rfAmplDb=18, port=2,
                                              triggerLevelDb=-25, triggerPreTime=10e-6)

        log.info("Step 18:Set trigger timeout")
        self.iq_measure.LP_SetVsaTriggerTimeout(trigger_time=0)

        log.info('Get ready to close the connection')
        #iq_measure.close()
        return 0

    def IQMAX_close_instrument(self):

        log.info('close_instrument')
        self.iq_measure.close()
        return 0

def step1():
    global example
    example = example_IQMAX_test("192.168.106.19")
    example.initial()
    return 0

def step2():
    global example
    example.IQMAX_test()
    return 0

def step3():
    global example
    example.IQMAX_close_instrument()
    return 0


if __name__=="__main__":
    step1()
    step2()
    step3()






