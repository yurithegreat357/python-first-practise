/*! \mainpage IQsequence Library Documentation
 *
 * The IQsequence Library adds MPS functionalities to IQmeasure
 *
 * \section revision_sec Revision History
 *
 * \subsection revision_1_8_57_1_3 "3 (2010-09-21)\n"
 * Date: Sep 21, 2010
 *   -# Separated IQmeasure and IQsequence.  IQsequence.DLL contains only the MPS functionality.
 *   -# IQapi version: 1.8.57.1
 *
 * \subsection revision_1_8_56_2 1.8.56.3 MPS
 * Date: Apr 13, 2010
 *   -# IQapi version: 1.8.56
 *
 */

#pragma once

#if !defined (__cplusplus)
#define IQSEQUENCE_API extern
#elif !defined (WIN32)
#define IQSEQUENCE_API extern "C"
#elif defined(IQSEQUENCE_EXPORTS)
#define IQSEQUENCE_API extern "C" __declspec(dllexport)
#else
#define IQSEQUENCE_API extern "C" __declspec(dllimport) 
#endif

#include "iqapi.h"

#define MAX_MPTA_PORTS     4
#if !defined(MAXERRORLENGTH)
    #define MAXERRORLENGTH     1000
#endif

#if !defined(MAX_RFPORT_SIZE)
    #define MAX_RFPORT_SIZE			4
#endif

#ifndef ON
#define ON 1
#endif

#ifndef OFF
#define OFF 0
#endif

// If user uses this built-in trigger level, IQ tester will set the trigger
// level to the lowest trigger level per the specification
#ifndef TESTER_BUILT_IN_TRIGGER_LEVEL_DBM
#define TESTER_BUILT_IN_TRIGGER_LEVEL_DBM -175.0
#endif

//IQSEQUENCE_API enum LP_MEASURMENT_TYPE_ENUM
//{
//    TYPE_SCALAR   = 1,                       /*!< The measurement result is of scalar type*/ 
//    TYPE_VECTOR,                             /*!< The measurement result is of vector type*/
//    TYPE_STRING,                             /*!< The measurement result is of string type*/
//    TYPE_INVALID                             /*!< Invalid type*/
//};
//

//IQSEQUENCE_API enum LP_MEASUREMENT_VSG_MODE
//{
//    VSG_NO_MOD_FILE_LOADED = 0,             /*!< No MOD file has been loaded*/
//    VSG_SINGLE_MOD_FILE,                    /*!< Single MOD file has been loaded*/
//    VSG_MULTI_SEGMENT_MOD_FILE,             /*!< Multi-segment MOD file has been loaded*/
//    VSG_INVALID_MODE                        /*!< Invalid VSG mode*/
//};




//IQSEQUENCE_API enum IQMEASURE_ERROR_CODES
//{
//	ERR_OK,
//	ERR_NO_CONNECTION,
//	ERR_NOT_INITIALIZED,
//	ERR_SAVE_WAVE_FAILED,
//	ERR_LOAD_WAVE_FAILED,
//	ERR_SET_TX_FAILED,
//	ERR_SET_WAVE_FAILED,
//	ERR_SET_RX_FAILED,
//	ERR_CAPTURE_FAILED,
//	ERR_NO_CAPTURE_DATA,
//	ERR_VSA_NUM_OUT_OF_RANGE,
//	ERR_ANALYSIS_FAILED,
//	ERR_NO_VALID_ANALYSIS,
//    ERR_MPTA_PORT_EXCEED_RANGE,
//    ERR_MPTA_CANNOT_BE_ENABLED,
//    ERR_MPTA_SWITCH_CAPTURE_FAILED,
//    ERR_NO_MPTA_FOUND,
//    ERR_NO_IQ2010_FOUND,
//	ERR_MPSIF_FAILED_TO_INITIALIZE,
//	ERR_FAILED_TO_CONNECT_MPTA,
//	ERR_VSG_PORT_IS_OFF,
//	ERR_MULTISEGMENT_WAVELOAD_FAILED,
//	ERR_BUILD_SEQUENCE_ERROR,
//	ERR_SEGMENT_OUT_OF_RANGE,
//    ERR_SEGMENT_COUNT_OUT_OF_RANGE,
//    ERR_TOO_MANY_POWER_LEVELS,
//    ERR_TOO_MANY_SEQ_STEPS,
//    ERR_MAXIMUM_POWER_OUT_OF_RANGE,
//    ERR_POWER_RANGE_OUT_OF_RANGE,
//    ERR_NO_MOD_FILE_LOADED,
//    ERR_NO_CONT_FOR_MULTI_SEGMENT,
//    ERR_PL_OFFSET_OUT_OF_RANGE,
//    ERR_MEASUREMENT_NAME_NOT_FOUND,
//    ERR_INVALID_ANALYSIS_TYPE,
//    ERR_NO_ANALYSIS_RESULT_AVAILABLE,
//    ERR_NO_MEASUREMENT_RESULT,
//    ERR_INVALID_RF_PORT,
//    ERR_INVALID_DATA_CAPTURE_RANGE,
//	ERR_VSA_SEQUENCE_STILL_RUNNING,
//	ERR_VSA_SEQUENCE_NOT_INITIATED,
//	ERR_IQAPIEXT_ERROR,
//	ERR_FM,
//	ERR_GPS,
//    ERR_GENERAL_ERR
//};


IQSEQUENCE_API enum IQSEQUENCE_ERROR_CODES
{
    ERR_SEQ_OK = ERR_OK,
    ERR_MULTISEGMENT_WAVELOAD_FAILED,
    ERR_INVALID_RF_PORT,
    ERR_NO_IQ2010_FOUND,
    ERR_NO_MPTA_FOUND,
    ERR_VSA_SEQUENCE_STILL_RUNNING,
    ERR_VSA_SEQUENCE_NOT_INITIATED,
    ERR_IQAPIEXT_ERROR,
	ERR_NO_IQ2010Q_FOUND,
    ERR_INVALID_PACKET_LENGTH,
    ERR_INVALID_VSG_POWER_2011Q,
	ERR_INCOMPATIBLE_TESTER_TYPE
};

/******************/
/* Error handling */
/******************/
//IQSEQUENCE_API char *LP_GetErrorString(int err);
//IQSEQUENCE_API char *LP_GetIQapiHndlLastErrMsg();

//! Get Error from IQsequence. 
/*!
 * \return error msg
 */
IQSEQUENCE_API const char* LP_MpsGetLastErr(void); 


//! Initializes MPS
/*!
 * \return 0 if MPS was initialized OK; non-zero indicates MPS failed to initialize.
 * \param[in] licenseType To check licenses of IQ2011+ and IQ2011Q
 * \remakr This function has to be called right after LP_InitTester()
 */
IQSEQUENCE_API int  LP_MpsInit(int licenseType = 0);

IQSEQUENCE_API int LP_MpsTerm(void);
IQSEQUENCE_API int LP_MpsReportTimerDurations(void);


//! Return IQsequence Version Info
/*!
 * \return 0 if MPS was initialized OK; non-zero indicates MPS failed to initialize.
 * \remakr This function is to replace LP_GetVersion()
 */
IQSEQUENCE_API int LP_MpsGetVersion(char *buffer, int buf_size);


//! Setups and performs switch capture for MIMO.   
/*!
 * \param[in] skipCount The number of frames to be skipped before capture. Needs to be equal to or greater than 1
 * \param[in] samplingTimeSecs The capture duration in second (<=1023us) for the capture on each port 
 * \param[in] portList An array specifying the list of ports (1-4) at which captures will occur sequentially
 * \param[in] portCount Number of ports included in portList
 * \param[out] Total Buffer length The number of points in the full acquisition of all ports
 *
 * \return ERR_OK if no errors; otherwise call LP_GetErrorString() for detailed error message.
 * \remark	This function sets up the Multiport Test Adapter to
 *         -# Setup
 *         -# Switch
 *         -# Capture data with the Vector Signal Analyzer (VSA)
 *			This is used for DUT Transmitter Testing using an MPTA or the IQmimo.
 *			Results can be retrieved using the LP Analyse MIMO and LP Get Scalar Measurement or LP Get Vector Measurement functions.        
 */
IQSEQUENCE_API int LP_MptaSetupSwitchCapture(int	skipCount,
											 double	samplingTimeSecs,
											 int	portList[], 
											 int	portCount,
											 int	ht40Mode=OFF);
//! Performs non-switch capture using MPTA
/*!
 * \param[in] samplingTimeSecs The capture duration in second for the capture on each port. <=1023us
 * \param[in] triggerType Trigger type used for capturing. Valid options are:
 *              - 1: free-run
 *              - 2: external trigger
 *              - 6: signal trigger
 * \param[in] portMask Bit mask determining one or more ports will be used:
 *               - Bit 0 is for DUT Port 1
 *               - Bit 1 is for DUT Port 2
 *               - Bit 2 is for DUT Port 3
 *               - Bit 3 is for DUT Port 4
 *               .
 * \param[in] ht40Mode Specifies if the capture is for HT40 mask (802.11n only)
 *              - 1: HT40 mask
 *              - 2: HT20 mask (Default)
 *
 * \return ERR_OK if no errors; otherwise call LP_GetErrorString() for detailed error message.
 */

IQSEQUENCE_API int LP_MptaDirectCapture(double	samplingTimeSecs,
										int		triggerType,
										int		portMask, 
										int		ht40Mode,
										int		captureCount,
										int		configureMpta,
										double	rfAmplDb,
										double	triggerLevelDb);




//! Selects one of the captures done by LP_MptaDirectCapture for analysis
/*!
 * \param[in] captureIndex The capture index to be selected for analysis
 *
 * \return ERR_OK if no errors; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_MptaSelectCaptureIndex(int captureIndex);





//! Enable or disable the TX sequence during RX sequence (for loopback test)
/*!
 * \param[in] enable 1-Enable TX sequence during RX sequence;0-Disable TX sequence during RX sequence
 *
 *
 * \remark 
 *          -# This function is made for the IQ2010 loopback test only
 *			-# When enabled, LP_MpsRxPer_PB() will also execute a TX sequence which is meant to capture the packets from VSG
 *			-# The TX sequence can be configured by calling LP_MpsTxSequenceBuild() prior
 *
 * \return ERR_OK if the call is successful; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_DBG_EnableVsaSequenceInVsgSequence(int enable=0);

IQSEQUENCE_API int LP_DBG_EnableAdcTriggerTestMode(int enable);

IQSEQUENCE_API int LP_DBG_EnableLoopbackTest();

IQSEQUENCE_API int LP_DBG_GetVsaSequenceStepGainError(double stepGainError[], int arraySize);


//! Keep VSA/VSG in MPS mode or not
/*!
 * \param[in] enable 1-Keep VSA/VSG in MPS mode;0-Do NOT keep VSA/VSG in MPS mode
 *
 *
 * \remark 
 *          -# When VSA/VSG are kept in MPS mode, the very first TX sequence/RX sequence will bring VSA/VSG into MPS mode,
 *             but will not exit the MPS mode, so the following TX sequences/RX sequences will not need to spend time
 *             to bring VSA/VSG in MPS mode
 *			-# Otherwise, every TX sequence/RX sequence will bring VSA/VSG into MPS mode at the beginning and exit MPS
 *             mode at the end
 *
 * \return ERR_OK if the call is successful; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_DBG_KeepVsaVsgInSequenceMode(int enable=0);

//! Prepare tester for HT40 Mask operation in PUSH
/*!
 * \param[in] centerFreqMHz The center frequency (MHz) for DUT HT40 operation
 * \param[in] modSpectrumShiftMHz The shift (MHz) made to the VSG waveform
 * \param[in] ht40Mode Mode for SYNC operation:  0-SYNC performed at center using HT40 data rate
 *                                              -1-SYNC performed at -10MHz shift
 *                                              +1-SYNC performed at +10MHz shift
 * \param[out] actualRFFreqMHz
 * \param[out] actualIFFreqMHz
 * \param[out] actualVsaIFOffsetMHz
 * \param[out] actualVsgIFOffsetMHz
 * \param[out] vsaGainOffsetDb
 *
 * \return IQEXT_ERR_OK if the function call is successful; otherwise call IQEXT_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_PUSH_HT40MaskVsaVsgPreparation(int      centerFreqMHz,
                                                     int      modSpectrumShiftMHz,
                                                     int      ht40Mode,
                                                     int      *actualRFFreqMHz,
                                                     int      *actualIFFreqMHz,
                                                     int      *actualVsaIFOffsetMHz,
                                                     int      *actualVsgIFOffsetMHz,
                                                     double   *vsaGainOffsetDb);

IQSEQUENCE_API int LP_PUSH_ResetVsaVsgIFOffsetMHz(void);

//! Build MPS VSA Sequence
/*!
 * \param[in] powerLeveldBm[] An array each element of which specifies the peak power level (dBm) at the RF ports
 * \param[in] captureLengthUs[] Capture length in us
 * \param[in] preTriggerTimeUs[] Pre-trigger time in us
 * \param[in] skipPktCnt[] Skip count before capture
 * \param[in] captureCnt[] Capture count
 * \param[in] arraySize Number of elements in the array powerLeveldBm[], captureLengthUs[], preTriggerTimeUs[], 
 *            skipPktCnt[], and captureCnt[].
 * \param[in] rfPort RF port. Valid values are 2 (RF1) and 3(RF2).
 * \param[in] triggerLeveldBm Trigger level in dBm.
 *
 * \return ERR_OK if the RX PER is successful; otherwise call LP_GetErrorString() for detailed error message.
 *
 * \remark 
 *         -# All power levels are specified at the 4 DUT ports of the tester
 *         -# In most cases, the stop power level would be lower than the start power level, but it could be
 *            higher than the start power level.  In either way, step would be relative, meaning always positive.
 *         -# If only one power level is interested for RX PER, set step to 0, or make the powerLevelStop be qual 
 *            to powerLevelStart.
 *         -# Every element of portMaskList[] is either RF1 or RF2
 *               - 2 for RF1 (or LEFT)
 *               - 3 for RF2 (or Right)
 *               .
 *         -# Every element of portMaskList[] is either RF1 or RF2
 *
 * \return ERR_OK if the switch capture is successful; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_MpsTxSequenceBuild(double		powerLeveldBm[],
										 int	    captureLengthUs[],  
										 int	    preTriggerTimeUs[],
										 int	    skipPktCnt[],
										 int	    captureCnt[],
										 int	    arraySize,
										 int		rfPort,
										 double		triggerLeveldBm);



//! Initiate MPS VSA Sequence (IQ2010 and IQexpress/IQturbo)
/*!
 * \remark 
 *		This function starts executing the VSA sequence defined by LP_MpsTxSequenceBuild() and returns,
 *		while the tester, IQ2010, or IQexpress/IQturbo, is performing captures in the background
 *
 * \return ERR_OK if the switch capture is successful; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_MpsInitiateCapture(void);



//! Finish MPS VSA Sequence
/*!
 * \remark 
 *		This function transfers the captures from the tester to PC.
 *		It will wait for the VSA sequence to finish if the sequence is still running when issued.
 *
 * \return ERR_OK if the switch capture is successful; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_MpsFinishCapture(void);

IQSEQUENCE_API int LP_MpsCapturePreProcess(double	*real[],
										   double	*imag[],
										   int		length[],
										   double	sampleFreqHz[],
										   int		shiftFreqMHz = 0,
										   double	compensatePower_dB = 0.0);

//! Select a portion of the capture for analysis
/*!
 * \param[in] startPositionUs Start position in the capture (us) for analysis
 * \param[in] lengthUs The length (us) in the capture for analysis
 *
 * \remark This function does not support IQnxn or IQnxn_plus
 *
 * \return ERR_OK if no errors; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_MpsSelectCaptureRange(double startPositionUs, double lengthUs);


//! Load multi-segment wavefile to VSG
/*!
 * \param[in] sigFile A .mod or .sig file that consists of multi-segment waveforms
 * \param[in] markerFile A text file that describes the marker positions 
 *
 * \return ERR_OK if the multi-segment wavefile has been loaded;; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_LoadMultiSegmentWaveFile(const char *sigFile, const char *markerFile);

IQSEQUENCE_API int LP_VsgSingleSegmentPlay(int segmentIndex, int packetCount);
IQSEQUENCE_API int LP_VsgSingleSegmentStop();


//! Run RX PER using MPTA
/*!
 * \param[in] segmentIndex[] An array each element of which specifies a segment index (0 based) of the multi-segment wavefile
 * \param[in] powerLevelStart[] An array each element of which specifies the start of power level (dBm at DUT) for 
 *                              each corresponding segment
 * \param[in] powerLevelStop[] An array each element of which specifies the stop of power level (dBm at DUT ports) for 
 *                             each corresponding segment
 * \param[in] step[] An array each element of which specifies the increment of power level (dB) for 
 *                   each corresponding segment.  Minimum step is 0.5dB.
 * \param[in] packetCount[] An array each element of which specifies the number of packets to be transmitted for
 *                          each corresponding segment.  Maximum number of packets is 32768.
 * \param[in] portMaskList[] An array specifying the list of port masks which are used for RX PER testing. 
 * \param[in] arraySize Number of elements in the array segmentIndex[], powerLevelStart[], powerLevelStop[], 
 *            step[], packetCount[], and portMaskList[].
 *
 * \return ERR_OK if the RX PER is successful; otherwise call LP_GetErrorString() for detailed error message.
 *
 * \remark 
 *         -# All power levels are specified at the 4 DUT ports of the tester
 *         -# In most cases, the stop power level would be lower than the start power level, but it could be
 *            higher than the start power level.  In either way, step would be relative, meaning always positive.
 *         -# If only one power level is interested for RX PER, set step to 0, or make the powerLevelStop be qual 
 *            to powerLevelStart.
 *         -# The maximum accepted power range is 45dB.  If more-than-45dB range is required, please call this
 *            function twice, one on the lower end, and one on the higher range.
 *         -# The highest power level at any DUT port is limited to -14dBm.
 *         -# Every element of portMaskList[] is a bit mask determining one or more ports will be used.
 *               - Bit 0 is for DUT Port 1
 *               - Bit 1 is for DUT Port 2
 *               - Bit 2 is for DUT Port 3
 *               - Bit 3 is for DUT Port 4
 *               .
 *         For example, {1, 2, 3} will perform RX PER in the order of Port 1, Port 2, and Port 1+2.
 *         When the RX PER is performed on Port 1, Port 2, 3, and 4 are set to the "OFF" state (maximum attenuation).
 *         When the RX PER is performed on Port 1+2, Port 3 and 4 are set to the "OFF" state (maximum attenuation).
 *         -# If VSG is required to transmit continuously, please follow the procedures below:
 *            - Call LP_EnableVsgRF(0) to turn off the VSG RF output
 *            - Call LP_SetVsgModulation() to load the .mod file
 *            - Set portMaskList[0] to include the ports from which signal will come
 *            - Set powerLevelStart[0] to the desired power level
 *            - Set packetCount[0] to 0
 *            - Call LP_MptaRxPer() with arraySize=1.  Other parameters will be ignored.
*/
//IQSEQUENCE_API int LP_MpsRxPer(int    segmentIndex[],
//                              double powerLevelStart[], 
//                              double powerLevelStop[], 
//                              double step[],
//                              int    packetCount[],
//                              int    portMaskList[],
//                              int    arraySize
//                              );
//
////! LP_MptaRxPer -- Obsoleted
///*!
// * \remark LP_MptaRxPer() has benn renamed to LP_MpsRxPer()
// */
IQSEQUENCE_API int LP_MptaRxPer(int    segmentIndex[],
								double powerLevelStart[], 
								double powerLevelStop[], 
								double step[],
								int    packetCount[],
								int    portMaskList[],
								int    arraySize
								);



//! Run RX PER using MIMO
/*!
 * \param[in] segmentIndex[] An array each element of which specifies a segment index (0 based) of the multi-segment wavefile
 * \param[in] powerLevelStart[] An array each element of which specifies the start of power level (dBm at DUT) for 
 *                              each corresponding segment
 * \param[in] powerLevelStop[] An array each element of which specifies the stop of power level (dBm at DUT ports) for 
 *                             each corresponding segment
 * \param[in] step[] An array each element of which specifies the increment of power level (dB) for 
 *                   each corresponding segment.  Minimum step is 0.5dB.
 * \param[in] packetCount[] An array each element of which specifies the number of packets to be transmitted for
 *                          each corresponding segment.  Maximum number of packets is 32768.
 * \param[in] portMaskList[] An array specifying the list of port masks which are used for RX PER testing. 
 * \param[in] arraySize Number of elements in the array segmentIndex[], powerLevelStart[], powerLevelStop[], 
 *            step[], packetCount[], and portMaskList[].
 *
 * \return ERR_OK if the RX PER is successful; otherwise call LP_GetErrorString() for detailed error message.
 *
 * \remark 
 *         -# All power levels are specified at the 4 DUT ports of the tester
 *         -# In most cases, the stop power level would be lower than the start power level, but it could be
 *            higher than the start power level.  In either way, step would be relative, meaning always positive.
 *         -# If only one power level is interested for RX PER, set step to 0, or make the powerLevelStop be qual 
 *            to powerLevelStart.
 *         -# The maximum accepted power range is 45dB.  If more-than-45dB range is required, please call this
 *            function twice, one on the lower end, and one on the higher range.
 *         -# The highest power level at any DUT port is limited to -14dBm.
 *         -# Every element of portMaskList[] is a bit mask determining one or more ports will be used.
 *               - Bit 0 is for DUT Port 1
 *               - Bit 1 is for DUT Port 2
 *               - Bit 2 is for DUT Port 3
 *               - Bit 3 is for DUT Port 4
 *               .
 *         For example, {1, 2, 3} will perform RX PER in the order of Port 1, Port 2, and Port 1+2.
 *         When the RX PER is performed on Port 1, Port 2, 3, and 4 are set to the "OFF" state (maximum attenuation).
 *         When the RX PER is performed on Port 1+2, Port 3 and 4 are set to the "OFF" state (maximum attenuation).
 *         -# If VSG is required to transmit continuously, please follow the procedures below:
 *            - Call LP_EnableVsgRF(0) to turn off the VSG RF output
 *            - Call LP_SetVsgModulation() to load the .mod file
 *            - Set portMaskList[0] to include the ports from which signal will come
 *            - Set powerLevelStart[0] to the desired power level
 *            - Set packetCount[0] to 0
 *            - Call LP_MptaRxPer() with arraySize=1.  Other parameters will be ignored.
*/
//IQSEQUENCE_API int LP_MpsRxPer_MIMO(int    segmentIndex[],
//                              double powerLevelStart[], 
//                              double powerLevelStop[], 
//                              double step[],
//                              int    packetCount[],
//                              int    portMaskList[],
//                              int    arraySize
//                              );
//
// */
IQSEQUENCE_API int LP_MpsRxPer_MIMO(int    segmentIndex[],
									double powerLevelStart[], 
									double powerLevelStop[], 
									double step[],
									int    packetCount[],
									int    portMaskList[],
									int    arraySize
									);



//! IQ201X ACK-based RX PER Test
/*!
 * \param[in] segmentIndex[] An array each element of which specifies a segment index (0 based) of the multi-segment wavefile
 * \param[in] powerLevelStart[] An array each element of which specifies the start of power level (dBm at DUT) for 
 *                              each corresponding segment
 * \param[in] powerLevelStop[] An array each element of which specifies the stop of power level (dBm at DUT ports) for 
 *                             each corresponding segment
 * \param[in] step[] An array each element of which specifies the increment of power level (dB) for 
 *                   each corresponding segment.  Minimum step is 0.5dB.
 * \param[in] packetCount[] An array each element of which specifies the number of packets to be transmitted for
 *                          each corresponding segment.  Maximum number of packets is 32768.
 * \param[in] rfPort[] An array specifying the RF ports used for RX PER testing. 
 * \param[in] arraySize Number of elements in the array segmentIndex[], powerLevelStart[], powerLevelStop[], 
 *            step[], packetCount[], and portMaskList[].
 * \param[in] ackTriggerLeveldBm TODO
 * \param[in] perMode Mode for PER test.  0-Fixed ACK mode; 1-Fixed Packet mode. Default to 1-Fixed Packet Mode
 * \param[in] timeSlotMultiplier Coefficient to multiply the base time slot in time slot based comm standards
 * \param[in] transmitPacketCount Total number of packets to be transmitted in BlueTooth BER test
 * \param[in] PacketDelayUs Packet delay for each step. If not specified, the global value is used.
 *
 * \return ERR_OK if the RX PER is successful; otherwise call LP_GetErrorString() for detailed error message.
 *
 * \remark 
 *         -# arraySize is always 1 for IQ2010.  Parameters are declared as arrays for consistence with IQmimo
 *         -# All power levels are specified at the 4 DUT ports of the tester
 *         -# In most cases, the stop power level would be lower than the start power level, but it could be
 *            higher than the start power level.  In either way, step would be relative, meaning always positive.
 *         -# If only one power level is interested for RX PER, set step to 0, or make the powerLevelStop be qual 
 *            to powerLevelStart.
 *         -# Every element of portMaskList[] is either RF1 or RF2
 *               - 2 for RF1 (or LEFT)
 *               - 3 for RF2 (or Right)
 *               .
 *         -# Every element of portMaskList[] is either RF1 or RF2
 */
IQSEQUENCE_API int LP_MpsRxPer_PB(int    segmentIndex[],
								  double powerLevelStart[], 
								  double powerLevelStop[], 
								  double step[],
								  int    packetCount[],
								  int    rfPort[],
								  int    arraySize,
								  double ackTriggerLeveldBm,
								  int    perMode = 1,
								  int	 *timeSlotMultiplier = NULL,
								  int	 *transmitPacketCount = NULL,
								  int	 *packetDelayUs = NULL
                                  );

IQSEQUENCE_API int LP_MpsRxPer_ET(int    segmentIndex[],
								  double powerLevelStart[], 
								  double powerLevelStop[], 
								  double step[],
								  int    packetCount[],
								  int    portMaskList[],
								  int    arraySize,
								  double ackTriggerLeveldBm,
								  double *lowestTriggerLeveldBm=NULL
								  );

// 4UP Functions --------------------------------------------------------------
IQSEQUENCE_API int LP_MpsVTC4UP_Init(const char *A121TesterIP = NULL);

IQSEQUENCE_API int LP_MpsVTC4UP_Term(void);

IQSEQUENCE_API int LP_MpsRxPer_A121PB(int	 dutSelect[MAX_RFPORT_SIZE],
									  int    segmentIndex[],
									  double *powerLevelStart[MAX_RFPORT_SIZE], 
									  double *powerLevelStop[MAX_RFPORT_SIZE], 
									  double *step[MAX_RFPORT_SIZE],
									  double ackPowerLeveldBm[MAX_RFPORT_SIZE],
									  int    packetCount[],
									  int	 packetDelayUs[],
									  int	 ackTimeoutUs[],
									  int    arraySize,
									  int    perMode,
									  int    rfFreqMHz,
									  int    rfPort,
									  int	 vsgTimeoutMs,
									  double triggerOffset_dB = -30.0
									  );

IQSEQUENCE_API int LP_MpsGetRxPerResults_A121PB(int    stepIndex,
												int	   dutIndex,
												double actualPowerLevel[], 
												int    packetSent[], 
												int    ackReceived[],
												double ackRespMax[],
												double ackRespMin[],
												double per[],
												int    *arraySize
												);

IQSEQUENCE_API int LP_MpsTxSeqBuild_A121PB(int	  dutSelect[MAX_RFPORT_SIZE],
										   double *peakTxPower[MAX_RFPORT_SIZE], 
										   int    skipCount[],
										   int	  captureCount[],
										   int	  captureTimeUs[],
										   int	  preTriggerUs[],
										   int    arraySize,
										   int    rfFreqMHz,
										   int    rfPort,
										   char	  *seqName,
										   double triggerOffset_dB = -30.0
										   );

IQSEQUENCE_API int LP_MpsInitCapture_A121PB(char *seqName);

IQSEQUENCE_API int LP_MpsFinishCapture_A121PB(char *seqName);

IQSEQUENCE_API int LP_MpsGetStepGainError_A121PB(int dutIndex,
												 double stepGainError[],
												 int *arraySize);

IQSEQUENCE_API int LP_InquireDutCaptures(int captureStatus[MAX_RFPORT_SIZE]);

IQSEQUENCE_API int LP_SetPortGains(int	  rfFreqMHz,
								   double portGain_dB[MAX_RFPORT_SIZE],
								   double portGainError_dB[MAX_RFPORT_SIZE]);

IQSEQUENCE_API int LP_VsgSingleSegmentPlayA121PB(int	dutSelect[MAX_RFPORT_SIZE],
												 double portPowerLeveldBm[MAX_RFPORT_SIZE],
												 int	rfFreqMHz,
												 int    segmentIndex,
												 int    packetCount,
												 int    rfPort,
												 int	vsgTimeoutMs
												 );

IQSEQUENCE_API int LP_StopSingleSegmentA121PB(void);

IQSEQUENCE_API int LP_VsgWaitTransmitDone(int vsgTimeOutMs);
// 4UP Functions --------------------------------------------------------------

// A221 Functions -------------------------------------------------------------
IQSEQUENCE_API int LP_MpsA221Test(void);
// A221 Functions -------------------------------------------------------------

// PBQ Functions --------------------------------------------------------------
IQSEQUENCE_API int LP_MpsRxPer_PBQ(int		dutSelect[MAX_RFPORT_SIZE],
								   int		segmentIndex[],
								   double	*powerLevelStart[MAX_RFPORT_SIZE], 
								   double	*powerLevelStop[MAX_RFPORT_SIZE], 
								   double	*step[MAX_RFPORT_SIZE],
								   double	ackPowerLeveldBm[MAX_RFPORT_SIZE],
								   int		packetCount[],
								   int		packetDelayUs[],
								   int		ackTimeoutUs[],
								   int		arraySize,
								   int		perMode,
								   int		rfFreqMHz,
								   int		vsgTimeoutMs,
								   double	triggerOffset_dB = -30,
								   int		*timeSlotMultiplier = NULL,
								   int		*transmitPacketCount = NULL,
                                   double   seqVsgRfGain_dB = -200.0);

IQSEQUENCE_API int LP_MpsGetRxPerResults_PBQ(int    stepIndex,
											 int	dutIndex,
											 double actualPowerLevel[], 
											 int    packetSent[], 
											 int    ackReceived[],
											 double ackRespMax[],
											 double ackRespMin[],
											 double per[],
											 int    *arraySize);

IQSEQUENCE_API int LP_MpsGetRxAttenIndex_PBQ(int    stepIndex,
											 int	dutIndex,
											 char   portAttenIndexRx[],
											 int    *arraySize);

IQSEQUENCE_API int LP_MpsTxSeqBuild_PBQ(int		dutSelect[MAX_RFPORT_SIZE],
										double *peakTxPower[MAX_RFPORT_SIZE], 
										int		skipCount[],
										int		captureCount[],
										int		captureTimeUs[],
										int		preTriggerUs[],
										int		arraySize,
										int		rfFreqMHz,
										double	triggerOffset_dB = -175,
										double  triggerOffsetHT40_dB = -175,
										int		triggerType = 0);

IQSEQUENCE_API int LP_VsgSingleSegmentPlay_PBQ(int		dutSelect[MAX_RFPORT_SIZE],
											   double	portPowerLeveldBm[MAX_RFPORT_SIZE],
											   int		rfFreqMHz,
											   int		segmentIndex,
											   int		packetCount,
											   int		timeSlotMultiplier,
											   int		vsgTimeoutMs,
											   double	actualTransmitPowerdBm[MAX_RFPORT_SIZE]);

IQSEQUENCE_API int LP_VsgStopSingleSegmentPlay_PBQ(void);

IQSEQUENCE_API int LP_MpsGetStepGainError_PBQ(int dutIndex,
											  double stepGainError[],
											  int *arraySize);

IQSEQUENCE_API int LP_MpsGetTxAttenIndex_PBQ(int dutIndex,
                                             char portAttenIndexTx[],
											 int *arraySize);

IQSEQUENCE_API int LP_InquireDutCaptures_PBQ(int captureStatus[MAX_RFPORT_SIZE]);

IQSEQUENCE_API int LP_MpsSeqVsgInquire(int freqMHz,
									   int arraySize,
									   double *vsgLevels_dBm = NULL,
									   int *arraySizeReturn = NULL,
									   double *powerAmpOffLevel_dBm = NULL);

// PBQ Functions --------------------------------------------------------------


// VSG VSA Ram Manipulation Functions -----------------------------------------
IQSEQUENCE_API int LP_MpsVsaRamRead(short			*bufferI,
									short			*bufferQ,
									unsigned int	arraySize,
									unsigned int	startAddress = 0,
									const char	*fileNameI = NULL,
									const char	*fileNameQ = NULL);

IQSEQUENCE_API int LP_MpsVsaRamWrite(short		*bufferI,
									 short		*bufferQ,
									 unsigned int	arraySize,
									 unsigned int	startAddress = 0);

IQSEQUENCE_API int LP_MpsVsgRamRead(short			*bufferI,
									short			*bufferQ,
									unsigned int	arraySize,
									unsigned int	startAddress = 0,
									const char	*fileNameI = NULL,
									const char	*fileNameQ = NULL);

IQSEQUENCE_API int LP_MpsVsgRamWrite(short		*bufferI,
									 short		*bufferQ,
									 unsigned int	arraySize,
									 unsigned int	startAddress = 0);

// VSG VSA Ram Manipulation Functions -----------------------------------------

// VSG CW function for MPTA
IQSEQUENCE_API int LP_MpsSetVsgCw(double rfFreqHz, double offsetFrequencyMHz, double rfGainDb, int port);

// VSG Wave Shift Funtions ----------------------------------------------------
IQSEQUENCE_API int LP_MpsBtLeVsgWaveInit(unsigned int	startAddress,
										 unsigned int	length,
										 unsigned int	waveId);

IQSEQUENCE_API int LP_MpsBtLeVsgWaveShift(unsigned int waveId,
										  int		   frequencyShiftMhz);

// VSG Wave Shift Funtions ----------------------------------------------------

//! Retrieve RX PER results from last run of LP_MpsRxPer
/*!
 * \param[in] stepIndex Specifies the step number of total steps included in LP_MptaRxPer.  0 based.
 * \param[out] actualPowerLevel Returns the actual power levels for each enabled port at each power level
 * \param[out] packetSent Returns packets sent at each power level
 * \param[out] ackReceived Returns ACKs received at each power level
 * \param[out] per Returns the PER result at each power level
 * \param[out] arraySize Specifies the array size, meaning number of power levels.
 *
 * \return ERR_OK if the switch capture is successful; otherwise call LP_GetErrorString() for detailed error message.
 *
 * \remark After finishing LP_MptaRxPer(), you call LP_MptaGetRxPerResults() to retrive the PER results.
 *        Each one of the total steps, specified by arraySize in LP_MptaRxPer(), will correspond to
 *        a range of power levels, determined by powerLevelStart, powerLevelStop, and step in LP_MptaRxPer(),
 *        and this value will be returned by arraySize in LP_MptaGetRxPerResults().
 *        The returned arrays have the following sizes:
 *           - actualPowerLevel[arraySize*4]:  For the unused ports, the value is -999.00
 *           - packetSent[arraySize]
 *           - ackReceived[arraySize]
 *           - per[arraySize]
*/
//IQSEQUENCE_API int LP_MpsGetRxPerResults(int    stepIndex,
//                                        double actualPowerLevel[], 
//                                        int    packetSent[], 
//                                        int    ackReceived[],
//                                        double per[],
//                                        int    *arraySize
//                                        );
//
////! LP_MptaGetRxPerResults -- Obsoleted
///*!
// * \remark LP_MptaGetRxPerResults() has benn renamed to LP_MpsGetRxPerResults()
// */
IQSEQUENCE_API int LP_MptaGetRxPerResults(int		stepIndex,
										  double	actualPowerLevel[], 
										  int		packetSent[], 
										  int		ackReceived[],
										  double	per[],
										  int		*arraySize
										  );

IQSEQUENCE_API int LP_MpsGetRxPerResults_PB(int		stepIndex,
											double	actualPowerLevel[], 
											int		acketSent[], 
											int		ackReceived[],
											double	ackRespMax[],
											double	ackRespMin[],
											double	per[],
											int		*arraySize
											);

IQSEQUENCE_API int LP_MpsGetRxPerResults_PUSH(int    stepIndex,
                                              double actualPowerLevel[], 
                                              int    packetSent[], 
                                              int    ackReceived[],
                                              double ackRespMax[],
                                              double ackRespMin[],
                                              double ackWidthMax[],
                                              double ackWidthMin[],
                                              double packetPowerMax[],
                                              double packetPowerMin[],
                                              int    syncGapTimeout[],
                                              int    syncAckTimeout[],   
                                              int    ackCatchupTimeout[],
                                              double per[],
                                              int    *arraySize
                                              );

IQSEQUENCE_API int LP_MpsGetTxStatus_PB(int    stepIndex[],
										double totalStepPower_dBm[], 
										double maxPacketPower_dBm[],
										double minPacketPower_dBm[],
										double maxPacketLength_us[],
										double minPacketLength_us[],
										int	   arraySize
										);

IQSEQUENCE_API int LP_MpsGetRxPerResults_ET(int    stepIndex,
											double actualPowerLevel[], 
											int    packetSent[], 
											int    ackReceived[],
											double ackRespMax[],
											double ackRespMin[],
											double per[],
											int    *arraySize
											);


//IQSEQUENCE_API int LP_MpsResetRxPerResults();
IQSEQUENCE_API int LP_MptaResetRxPerResults();

IQSEQUENCE_API int LP_MpsGetBerCapture(int captureID,
									   double *real[],
									   double *imag[],
									   int length[],
									   double *sampleFreqHz
									   );

IQSEQUENCE_API int LP_MpsGetBerCaptureIDs(int stepIndex,
                                          int captureID[]
                                          );

IQSEQUENCE_API int LP_MpsSaveBerCapture(const char *baseName,
										int captureID,
										double *real[],
										double *imag[],
										int length[],
										double sampleFreqHz
										);

IQSEQUENCE_API int LP_MpsReleaseBerCaptures(int captureID[],
                                            int arraySize
                                            );

//IQSEQUENCE_API int LP_PUSH_A48eepromRead(int byteAddress, 
//                                         char buffer[], 
//                                         int numberOfBytes
//                                         );
//
//IQSEQUENCE_API int LP_PUSH_A48eepromWrite(int byteAddress, 
//                                          char buffer[], 
//                                          int numberOfBytes
//                                          );

IQSEQUENCE_API int LP_PUSH_ConfigRfPort(const char *rfPortName, 
                                        int *rfPortValue,
                                        int freqMHz,
                                        double *insertionLossdB,
                                        char *loopBackRfPortName = NULL,
                                        double *insertionLossLoopBackPortdB = NULL
                                        );

//IQSEQUENCE_API int LP_PUSH_GetA48InsertionLossTable(void);

//! Set Power Level Offset between 4 DUT ports for LP_MptaRxPer()
/*!
 * \param[in] port1 Power level offset (dB) for DUT port 1 
 * \param[in] port2 Power level offset (dB) for DUT port 2 
 * \param[in] port3 Power level offset (dB) for DUT port 3 
 * \param[in] port4 Power level offset (dB) for DUT port 4 
 *
 * \remark Without specifying those offsets, LP_MptaRxPer() will apply same power levels to all 4 DUT ports.  
 *         However, if the individual DUT ports require different power levels, LP_MptaSetDutPortPowerLevelOffset()
 *         can be used to adjust the power level for each port by introducing an offset.
 *         New offset settings will take effective for next call of LP_MptaRxPer().
 *         The allowed offset range is +/-6dB
 *         Note: 
 *            - The offsets will not take effect until the next call of LP_MptaRxPer
 *            - This function has no effect on LP_SetVsgCw()
 * \return ERR_OK if offsets are set; otherwise call LP_GetErrorString() for detailed error message.
 */

//IQSEQUENCE_API int LP_MpsSetDutPortPowerLevelOffset(double port1, double port2, double port3, double port4);
//
////! LP_MptaSetDutPortPowerLevelOffset -- Obsoleted
///*!
// * \remark LP_MptaSetDutPortPowerLevelOffset() has been renamed to LP_MpsSetDutPortPowerLevelOffset()
// */
IQSEQUENCE_API int LP_MptaSetDutPortPowerLevelOffset(double port1, double port2, double port3, double port4);

//! Retrieve the Serial Number of MPTA connected
/*!
 * \param[out] serialNumber A pointer to the buffer that will hold the serial number
 * \param[in] bufSize The buffer size for storing the serial number
 *
 * \return ERR_OK if the serial number has been successfully retrieved; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_MptaGetSerialNumber(char *serialNumber, int bufSize);

//! Check if MPTA connected
/*!
 * \param[out] mptaConnected Return 1 if MPTA connected; otherwise 0
 *
 * \return ERR_OK if the serial number has been successfully retrieved; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_MptaConnected(int *mptaConnected);

//IQSEQUENCE_API int LP_GetSampleData(int vsaNum, double bufferReal[], double bufferImag[], int bufferLength);

/*****************************/
/* Result Handling Functions */
/*****************************/

/***********************/
/* Debugging Functions */
/***********************/


//! Toggle the display of MPTA debugging info
/*!
 * \param[in] enableDebug Turn on/off (true/false) the MPTA debugging info
 *
 * \return ERR_OK
 */
IQSEQUENCE_API int LP_MptaPrintDebug(bool enableDebug);



//! Set MPS Global Parameter
/*!
 * \param[in] paramName The global parameter name
 * \param[in] paramValue The value of the parameter in string, which will be converted to corresponding value
 *
 * \return ERR_OK if offsets are set; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_MpsSetGlobalParam(const char *paramName, const char *paramValue);


//! Get MPS Global Parameter
/*!
 * \param[in] paramName The global parameter name
 * \param[out] paramValue The value of the parameter in string.
 * \param[in] paramValueSize The size of paramValue
 *
 * \return ERR_OK if offsets are set; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_MpsGetGlobalParam(const char *paramName, char *paramValue, int paramValueSize);


//! Configure parameters for the DUT Self-cal Detect (PUSH specific)
/*!
 * \remark This function applies the following IQapiExt global parameters to IQ2020:
 *
 *          - SYNC_START_GAP_MS;              
 *          - SYNC_TIMEOUT_MS;                
 *          - GAP_BEFORE_CAL_START_US;        
 *          - CAL_WINDOW_LENGTH_US;           
 *          - CAL_DETECT_TIMEOUT_MS;          
 *          - CAL_DETECT_TARGET_LEVEL_DBM;      
 *          
 *          Before this function is called, all parameters listed above shall be passed 
 *          to IQapiExt by calling LP_MpsSetGlobalParam()
 *
 *          This function has caching capability built-in.  It only applies the changed parameters to IQ2020
 *
* \return ERR_OK if offsets are set; otherwise call LP_GetErrorString() for detailed error message.
*/
IQSEQUENCE_API int LP_PUSH_DutBehaviorParamsConfigure();

//! Configure parameters for the BlueTooth VSG Play
/*!
 * \remark This function applies the following IQapiExt global parameters to IQ2020:
 *
 *          - BASE_TIMESLOT_US;              
 *          - ACK_CATCH_UP_POWER_LEVEL_DBM;                 
 *          
 *          Before this function is called, all parameters listed above shall be passed 
 *          to IQapiExt by calling LP_MpsSetGlobalParam()
 *
 *          This function has caching capability built-in including the frequency parameter passedn. 
 *			It only applies the changed parameters to IQ2020
 *
* \return ERR_OK if offsets are set; otherwise call LP_GetErrorString() for detailed error message.
*/
IQSEQUENCE_API int LP_PUSH_BTparamsConfigure(int freqMHz);

//! Check the connection to tester(s)
/*!
 * \return ERR_OK if the tester has been successfully initialized; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_CheckTesterIsValid();

//! Close the connection to tester(s)
/*!
 * \return ERR_OK if the tester has been successfully initialized; otherwise call LP_GetErrorString() for detailed error message.
 */
IQSEQUENCE_API int LP_CloseTesterCon();
