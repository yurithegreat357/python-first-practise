import datetime
import logging
import time
from apollo.libs import lib, cesiumlib
from apollo.engine import apexceptions
from ....libs.error import BarbadosError
from ....libs.uut import UUT, BAND_2G, BAND_5G
from .....libs.foc.bojay_fixture import Fixture
from .....libs.foc.hyt_fixture import Fixture as hyt_fixture
from .....libs.switch_3850 import Switch
from .....libs.pulizzi import Pulizzi
from .....libs.server import Server
from .....utils.scan import scan_test_area, set_scan_container_number, scan_all_labels,\
                            ScanError, set_scan_part_number, set_scan_serial_number
from .....utils.product_def import load_config_module
from .....utils.decorator import apollo_debug, apollo_log, add_user_log, apollo_error, apollo_abort
from .....utils import utils, fail_lock


__author__ = 'clhu'
__version__ = '0.1'

logger = logging.getLogger(__name__)
code_path = __name__

# Constant
DC = 'DC'
POE = 'POE'
ON = 'ON'
OFF = 'OFF'

# global
config = None
uut = None
switch1 = None
switch2 = None
fixture = None
server = None
powerbox = None
switch = None

# user_dict
mb_tst_info = None


def pre_sequence_definition():
    """ Run pre-sequence that includes operator scanning, board info discovery,
        add tst start record and etc.

    :return: seq (object)
    """
    seq = lib.get_sequence_definition('PRE SEQ')
    seq.add_step(version_control)
    seq.add_step(pre_initialize, name='PRE_INITIALIZE')
    seq.add_step(labels_scan, name='label_scan')
    seq.add_step(get_test_area, name='GET_TEST_AREA')
    seq.add_step(tst_area_check, name='TST_AREA_CHECK')
    seq.add_step(add_tst_data, name='ADD_TST_DATA')
    seq.add_step(pre_finalize, name='PRE_FINALIZE', group_level=lib.FINALIZATION)

    return seq


def main_sequence_definition():
    """ Run sequence that includes power on & off, uut programming,
        check eeprom against label/cmpd, test connections, MTS test, and etc.

        It has multi steps sub-sequence in sequence and test are divided into individual test
        instead of diag run all for Adaptive test compliance and ease in debugging failures.

    :return: seq
    """
    seq = lib.get_sequence_definition('MAIN INT PRODUCT SEQ')
    seq.add_step(main_initialize, name='MAIN_INITIALIZE')
    seq.add_step('DC_POWER_ON', codepath=code_path, function='uut_power_on', kwargs={'mode': DC}, loop_on_error=2)
    seq.add_step('PORT_ON_EGIGA1', codepath=code_path, function='switch_port_on', kwargs={'interface': 'egiga1'}, loop_on_error=1)
    seq.add_step(clear_storage, name='CLEAR_STORAGE')
    seq.add_step('UPGRADE_UBOOT', codepath=code_path, function='upgrade_uboot', kwargs={'speed': 10}, loop_on_error=1)
    seq.add_step('DOWNLOAD_MGIG_FW', codepath=code_path, function='download_mgig_fw', precondition="userdict['mgig_fw_need']", loop_on_error=1)
    seq.add_step(secure_boot, name='SECURE_BOOT')
    seq.add_step(create_nand_partition, name='CREATE_NAND_PARTITION')
    seq.add_step(load_nand_image_part_1, name='LOAD_NAND_IMAGE_PART_1', kwargs={'speed': 100})
    seq.add_step(load_nand_image_part_2, name='LOAD_NAND_IMAGE_PART_2', kwargs={'speed': 1000})
    seq.add_step(set_boot_env, name='SET_BOOT_ENV')
    seq.add_step(reset_uboot, name='RESET_UBOOT')
    seq.add_step(em_detect, name='DETECT_EM')
    seq.add_step(em_check_link, name='CHECK_EM_LINK')
    seq.add_step('BOOT_MFG_LINUX_1', codepath=code_path, function='boot_mfg_image', loop_on_error=1)
    seq.add_step(program_cookie, name='PROGRAM_COOKIE')
    seq.add_step(mb_mac_fetch, name='MB_MAC_FETCH')
    seq.add_step(radio_mac_fetch, name='RADIO_MAC_FETCH')
    seq.add_step('PORT_ON_EGIGA2', codepath=code_path, function='switch_port_on', kwargs={'interface': 'egiga2'}, loop_on_error=1)
    seq.add_step('BOOT_MFG_LINUX_2', codepath=code_path, function='reload_mfg_image', loop_on_error=1)
    seq.add_step(verify_cookie, name='VERIFY_COOKIE')
    seq.add_step(em_talk, name='EM_TALK')
    seq.add_step(led_test, name='LED_TEST', precondition="userdict['led_test_need']")
    seq.add_step('CAPWAP_PING_TEST', codepath=code_path, function='capwap_ping_test', loop_on_error=1)
    seq.add_step('LINUX_PING_TEST_5G', codepath=code_path, function='linux_ping_test', kwargs={'speed': 5000}, loop_on_error=1)
    seq.add_step('LINUX_PING_TEST_2G', codepath=code_path, function='linux_ping_test', kwargs={'speed': 2500}, loop_on_error=1)
    seq.add_step('LINUX_PING_TEST_100M', codepath=code_path, function='linux_ping_test', kwargs={'speed': 100}, loop_on_error=1)
    seq.add_step('LINUX_PING_TEST_1000M', codepath=code_path, function='linux_ping_test', kwargs={'speed': 1000}, loop_on_error=1)
    seq.add_step('POE_POWER_ON', codepath=code_path, function='uut_power_on', kwargs={'mode': POE}, loop_on_error=1)
    seq.add_step('BOOT_MFG_LINUX_3', codepath=code_path, function='boot_mfg_image', loop_on_error=1)
    seq.add_step(usb_test, name='USB_TEST')
    seq.add_step('X509_PROGRAM', codepath=code_path, function='program_x509')
    seq.add_step(validate_x509, name='X509_VALIDATE')
    seq.add_step('ACT2_PROGRAM', codepath=code_path, function='program_act2')
    seq.add_step(validate_act2, name='ACT2_VALIDATE')
    seq.add_step(clear_storage, name='CLEAR_STORAGE_2')
    seq.add_step(set_factory_default, name='SET_FACTORY_DEFAULT')
    seq.add_step(main_finalize, name='MAIN_FINALIZE', group_level=lib.FINALIZATION)
    return seq


def labels_scan():
    """ Labels scanning from operator input
    :return: lib.PASS if the function passes
    """
    mb_pn = set_scan_part_number('mb part number')
    mb_sn = set_scan_serial_number('mb serial number')
    cn = set_scan_container_number('container number', label_format=lib.get_my_container_key().split('|')[-1])
    mb_pn, mb_sn, container_number = scan_all_labels(mb_pn, mb_sn, cn)
    mb_tst_info['uut_type'], mb_tst_info['version_id'] = mb_pn.split()
    mb_tst_info['serial_number'] = mb_sn
    mb_tst_info['test_container'] = container_number
    container_num = int(container_number[-2:])
    mb_tst_info['slot'] = container_num

    return lib.PASS


def get_test_area():
    """
    Request OP to select test area if there are multiple areas defined in config
    :return: lib.PASS or lib.FAIL
    """
    area = scan_test_area('test area')
    mb_tst_info['test_area'] = area
    return lib.PASS


def tst_area_check():
    """
    Areacheck test for scanned serial number; Also determine if the unit is a fresh unit or not
    :return: lib.PASS once the function passes
    """

    # if we are in debug mode, it is always seen as fresh unit
    lib.apdicts.userdict['fresh_unit'] = False
    if lib.get_apollo_mode() == lib.MODE_DEBUG:
        logger.info('Skip area check if run in DEBUG mode')
        return lib.PASS

    sn, uuttype, area = mb_tst_info['serial_number'], mb_tst_info['uut_type'], mb_tst_info['test_area']
    for test_area in config.mb_test_areas:
        try:
            logger.info("[{}] areacheck on serial number [{}], uut type [{}]".format(test_area, sn, uuttype))
            cesiumlib.verify_area(serial_number=sn, uut_type=uuttype, area=test_area, timeframe='2y')
        except apexceptions.ServiceFailure as ex:
            if test_area == area:
                if '12101' in ex.message:    # Data not found
                    logger.info('This is a fresh unit, no record at {}'.format(test_area))
                    lib.apdicts.userdict['fresh_unit'] = True
                    break
                elif '11129' in ex.message:   # Num. passes or last record check failed
                    logger.info('This is not a fresh unit, has failed record at {}'.format(test_area))
                    break
            raise
        # only verify test area ahead of this current area (including this area)
        if test_area == area:
            logger.info('This is not a fresh unit, has passed record at {}'.format(test_area))
            break
    return lib.PASS


def add_tst_data():
    """
    To provide the required serial number, container, pid, and test area for tst logging.
    :return: lib.PASS or lib.FAIL
    """
    # Logging TST data for MB
    logger.info('Sernum: {}, Uuttype: {}, Area: {}, container: {}, slot:{}'.format(mb_tst_info['serial_number'],
                                                                                   mb_tst_info['uut_type'],
                                                                                   mb_tst_info['test_area'],
                                                                                   mb_tst_info['test_container'],
                                                                                   mb_tst_info['slot']))
    lib.add_tst_data(**mb_tst_info)
    return lib.PASS


def config_load(save_userdict=False):
    """
    Load config file by config module name
    :return:
    """
    # load the config module now
    # if all arguments are None, load the default product defination file
    global config
    config = load_config_module(
        (mb_tst_info.get('uut_type'), mb_tst_info.get('version_id')),
        mb_tst_info.get('deviation'),
    )

    # Save the data from station config to this module
    config.mgiga_temp_mac = lib.apdicts.configuration_data['MGIGA_TEMP_MAC'].upper()
    config.giga_temp_mac = lib.apdicts.configuration_data['GIGA_TEMP_MAC'].upper()
    config.mac_address.value = config.mgiga_temp_mac.upper()        # Temperary MAC
    config.r0_mac_address.value = lib.apdicts.configuration_data['R0_TEMP_MAC'].upper()     # Temperary MAC
    config.r1_mac_address.value = lib.apdicts.configuration_data['R1_TEMP_MAC'].upper()     # Temperary MAC

    if save_userdict:
        # fill in serial number to config
        config.pcb_serial_num.value = mb_tst_info['serial_number']
        # fill in pca reversion num
        config.pca_revision_num.value = mb_tst_info['version_id']
        # fill in pca part num
        config.pca_part_num.value = mb_tst_info['uut_type']
        # fill in 2G/5G virtual serial number
        config.radio_sn_virtual[BAND_2G] += mb_tst_info['serial_number'][3:]
        config.radio_sn_virtual[BAND_5G] += mb_tst_info['serial_number'][3:]
        # config.top_assy_serial_num.value = mb_tst_info['serial_number']


def module_load():
    first_exception = None
    config_data = lib.apdicts.configuration_data
    # Load connection module
    global uut, switch1, switch2, fixture, server, powerbox

    try:
        uut = UUT(lib.conn.UUT, config, em_connection=lib.conn.EM)
    except Exception, ex:
        if first_exception is None:
            first_exception = ex

    try:
        server = Server(lib.conn.SERVER)
    except Exception, ex:
        if first_exception is None:
            first_exception = ex

    try:
        switch1 = Switch(lib.conn.SWITCH1, {config_data['SWITCH_1']['port_num']: config_data['SWITCH_1']['port_type']})
        switch2 = Switch(lib.conn.SWITCH2, {config_data['SWITCH_2']['port_num']: config_data['SWITCH_2']['port_type']})
    except Exception, ex:
        if first_exception is None:
            first_exception = ex

    try:
        if lib.conn.POWER.model == 'Pulizzi':
            powerbox = Pulizzi(lib.conn.POWER, port=config_data['PULIZZI_PORT_NUM'])
    except Exception, ex:
        if first_exception is None:
            first_exception = ex

    try:
        if 'FIXTURE' in lib.getconnections():
            if lib.conn.FIXTURE.model == 'HYT':
                fixture = hyt_fixture(lib.conn.FIXTURE)
            else:
                fixture = Fixture(lib.conn.FIXTURE)
    except Exception, ex:
        if first_exception is None:
            first_exception = ex

    if first_exception is not None:
        raise first_exception


def userdict_init():
    """
    Initialize userdict to sttore the scanned labels of MB and Radio
    :return: None
    """
    userdict = lib.apdicts.userdict
    if 'mb_tst_info' not in userdict:
        userdict['mb_tst_info'] = dict()

    global mb_tst_info
    mb_tst_info = userdict['mb_tst_info']


def pre_initialize():
    """
    Initialize action: power off uut, open uut console
    And load the configure file by uut_type
    :return:
    """
    logger.info('This test is being run in {} mode'.format(lib.get_apollo_mode()))
    userdict_init()
    config_load()
    return lib.PASS


def main_initialize():
    """
    Initialize action: load module instances saved in cache
    Also load the configure file by uut_type
    :return:
    """
    logger.info('This test is being run in {} mode'.format(lib.get_apollo_mode()))
    userdict_init()
    config_load(save_userdict=True)
    module_load()
    userdict = lib.apdicts.userdict
    userdict['mgig_fw_need'] = config.mgig_fw_need
    userdict['led_test_need'] = config.led_test_need

    mb_tst_info['testr1name'] = 'Barbados Uboot Name'
    mb_tst_info['testr1'] = config.u_boot_image.name
    mb_tst_info['testr2name'] = 'barbados_Part1_Linux'
    mb_tst_info['testr2'] = config.mfg_image.name
    lib.add_tst_data(**mb_tst_info)

    return lib.PASS


def power_off():
    """
    Power off uut from both of Power box and PoE
    :return:
    """
    powerbox.off()
    switch.power_off()
    time.sleep(2)


def power_on(mode):
    """
    Power on uut from either Power box and PoE
    :return:
    """
    if mode == DC:
        powerbox.on()
    else:
        switch.power_on()


@apollo_error
def uut_power_on(mode=None):
    """
    Connect UUT, and Set switch to power on UUT
    :return:
    """
    global switch
    # switch2 has POE feature
    switch = switch2
    # if set loop_on_error, hopes it will have a reminder to operator for connection check
    if lib.apdicts.test_info.current_status != 'PASS':
        logger.info('the current status is {}'.format(lib.apdicts.test_info.current_status))
        uut.close()
        lib.ask_question('UUT seems NOT to power on, pls check cable connection !!')
        uut.open()
        time.sleep(5)
    power_off()
    time.sleep(10)
    power_on(mode)
    uut.jump_to_uboot(power_cycle=True)
    return lib.PASS


def uut_power_off():
    """
    Power off UUT
    :return:
    """
    power_off()
    return lib.PASS


@apollo_error
def boot_mfg_image():
    """
    Boot mfg image and jump to devshell
    and close watchdog
    :return:
    """
    uut.stop_watch_dog()
    time.sleep(30)
    return lib.PASS


@apollo_error
def reload_mfg_image():
    """
    Back to cisco shell and reload image
    and close watchdog
    :return:
    """
    uut.jump_to_ciscoshell()
    uut.jump_to_uboot()
    uut.stop_watch_dog()
    time.sleep(30)
    return lib.PASS


def load_nand_image_part_1(speed=None):
    switch.set_speed(speed=speed)
    uut.set_tftp_env()
    uut.ping_router()
    uut.load_nand_image_part1()
    return lib.PASS


def load_nand_image_part_2(speed=None):
    switch.set_speed(speed=speed)
    uut.set_tftp_env()
    uut.ping_router()
    uut.load_nand_image_part2(use_labtool=False)
    return lib.PASS


def create_nand_partition():
    uut.create_nand_partition()
    return lib.PASS


def clear_storage():
    uut.clear_storage()
    return lib.PASS


@apollo_error
def switch_port_on(interface=None):
    global switch
    if interface == 'egiga1':
        switch = switch1
        config.ip_addr = lib.apdicts.configuration_data['SWITCH_1']['ip_addr']    # 10.1.1.xxx, etc...
        config.active_port = interface                                            # egiga1, egiga2
        switch1.port_on()
        switch2.port_off()
    elif interface == 'egiga2':
        switch = switch2
        config.ip_addr = lib.apdicts.configuration_data['SWITCH_2']['ip_addr']
        config.active_port = interface
        switch2.port_on()
        switch1.port_off()

    return lib.PASS


def set_boot_env():
    uut.set_boot_env()
    return lib.PASS


def set_factory_default():
    uut.set_default_env()
    return lib.PASS


@apollo_error
def upgrade_uboot(speed=None):
    """
    Verify UBOOT version; if not latest, upgrade it
    :return:
    """
    switch.set_speed(speed=speed)
    uut.set_tftp_env()
    uut.reset_uboot()
    uut.ping_router()
    uut.upgrade_uboot(always_download=True)
    return lib.PASS


@apollo_error
def download_mgig_fw(speed=10):
    """
    Verify UBOOT version; if not latest, upgrade it
    :return:
    """
    logger.info("DOWNLOAD FW for VE unit")
    switch.set_speed(speed=speed)
    uut.set_tftp_env()
    uut.ping_router()
    uut.download_mgig_fw()
    return lib.PASS


def secure_boot():
    """
    secure boot in uboot environment
    and boot verification
    :return:
    """
    if config.secure_boot:
        uut.secure_boot()
        uut.verify_secure_boot()
    else:
        logger.info('secure_boot in config file is False, so skip secure boot')
    return lib.PASS


def reset_uboot(resetenv=False):
    """
    Uboot reset and re-login
    :return:
    """
    uut.reset_uboot(resetenv)
    return lib.PASS


def usb_test():
    """
    Run USB test at DEVSHELL
    :return:
    """
    uut.usb_test()
    return lib.PASS


def led_test():
    """
    Capture if led test can run or not, don't require user to check LED color
    :return:
    """
    uut.set_led_on('RED')
    uut.set_led_off()
    return lib.PASS


def em_detect():
    """
    Try to detect EM (extension module) during uboot
    :return:
    """
    if config.prod_type == '4K':
        logger.info('Skip em test !')
    else:
        uut.em_detect()
    return lib.PASS


def em_check_link():
    """
    check if EM is linked
    :return:
    """
    if config.prod_type == '4K':
        logger.info('Skip em test !')
    else:
        uut.em_link_check()
    return lib.PASS


def em_talk():
    """
    MB talk to EM
    :return:
    """
    if config.prod_type == '4K':
        logger.info('Skip em test !')
    else:
        uut.em_talk()
    return lib.PASS


def pre_finalize():
    """
    test finalize, power off uut, disconnect uut
    :return:
    """
    config_load(save_userdict=True)
    module_load()
    try:
        lock = fail_lock.Faillock(mb_tst_info['serial_number'])
        lock.fail_count_check(lib.get_apollo_mode())
    except KeyError:
        pass
    if fixture:
        fixture.close()
        time.sleep(1)
        fixture.test_result('run')
    try:
        switch1.login()
        switch2.login()
    except Exception:
        switch1.close()
        switch2.close()
        time.sleep(2)
        switch1.login()
        switch2.login()
    return lib.PASS


def main_finalize():
    """
    test finalize, disconnect switch/thermal PC, power off uut, disconnect uut
    :return:
    """
    try:
        lock = fail_lock.Faillock(mb_tst_info['serial_number'])
        lock.fail_count_check(lib.apdicts.test_info.current_status, lib.get_apollo_mode())

    finally:
        if lib.apdicts.test_info.current_status != 'PASS':
            # Change the failure log path
            utils.backup_fail_log(mb_tst_info['serial_number'])
            if fixture:
                fixture.test_result('fail')
        else:
            if lib.apdicts.userdict.get('fresh_unit', False) and lib.get_apollo_mode() == lib.MODE_PROD:
                logger.debug('This is fresh unit, need to run log compare')
                utils.log_compare('/opt/cisco/te/scripts/projects/wnbu/trunk/product_group_1/barbados/foc/log_cmp/',
                                  config.prod_type,
                                  mb_tst_info['test_area'],
                                  mb_tst_info['uut_type'],
                                  mb_tst_info['serial_number'])
            if fixture:
                fixture.test_result('pass')

        if lib.get_apollo_mode() == lib.MODE_DEBUG:
                logger.info('Skip connection close if in DEBUG mode')
                # Only close the connection and power off if run in prod mode
        else:
            uut_power_off()
            if uut:
                uut.close()
            # if fixture:
            #     fixture.open()
        lib.apdicts.userdict.clear()
    return lib.PASS


def request_mac(uut_serial_number, uut_type_pid, uut_block_size, uut_mac_group):
    """ request mac from db
    :param uut_serial_number: serial number
    :param uut_type_pid:
    :param uut_block_size:
    :param uut_mac_group:
    :return: a tuple of mac['abcdefghijk', 'ab:cd:ef:gh:ij:kl', 'ab-cd-ef-gh-ij-kl')
    """
    mac_str, mac_block_size = cesiumlib.generate_mac(serial_number=uut_serial_number,
                                                     uut_type=uut_type_pid,
                                                     block_size=uut_block_size,
                                                     mac_group=uut_mac_group)
    logger.info("mac:{}, block_size:{}".format(mac_str, mac_block_size))
    mac_str_1 = ':'.join(lib.chunk(mac_str, 2))
    mac_str_2 = '-'.join(lib.chunk(mac_str, 2))
    return mac_str, mac_str_1, mac_str_2


def mb_mac_fetch():
    try:
        mb_mac_verify()  # compare current mac with the one in db (found based on serial number)
    except apexceptions.ServiceFailure:
        raise
    except Exception:
        mb_mac_program()
        mb_mac_verify()
    return lib.PASS


def mb_mac_program():
    """
    step1: request MAC
    step2: program MAC to uut
    step3: record MAC
    :return:
    """
    mac1, mac2, _ = request_mac(mb_tst_info['serial_number'],
                                mb_tst_info['uut_type'],
                                config.mac_block_size.value,
                                't' if lib.get_apollo_mode() == lib.MODE_DEBUG else 'm')

    logger.info('mac1 --- [{}], mac2 --- [{}]'.format(mac1, mac2))
    config.mac_address.value = mac2.upper()
    uut.write_mb_mac()
    """
    cesiumlib.record_mac(mb_tst_info['serial_number'],
                         mb_tst_info['uut_type'],
                         '0x{}'.format(mac1),
                         # int('0x{}'.format(mac1), 16),
                         config.mac_block_size.value)
    """


def mb_mac_verify():
    mac_from_uut, mac_block_size_from_uut = uut.read_mb_mac()

    cesiumlib.verify_mac(
        mb_tst_info['serial_number'],
        mb_tst_info['uut_type'],
        '0x{}'.format(mac_from_uut),
        mac_block_size_from_uut
    )

    config.mac_address.value = mac_from_uut.upper()
    config.mac_block_size.value = mac_block_size_from_uut

    return lib.PASS


def radio_mac_fetch():
    """
    use this for mac program on daughter board
    :return: lib.PASS
    """
    try:
        radio_mac_verify()
    except apexceptions.ServiceFailure:
        raise
    except Exception:
        radio_mac_program()
        radio_mac_verify()

    return lib.PASS


def radio_mac_program():
    """
    Request mac for daughter board
    :return:
    """
    mac1, mac2, _ = request_mac(config.radio_sn_virtual[BAND_2G],
                                config.radio_uuttype,
                                config.r0_mac_block_size.value + config.r1_mac_block_size.value,
                                't' if lib.get_apollo_mode() == lib.MODE_DEBUG else 'm')

    config.r0_mac_address.value = mac2.upper()
    # config.r1_mac_address.value = ':'.join(lib.chunk(hex(int(mac1, 16) + 16)[2:].upper(), 2))
    config.r1_mac_address.value = ':'.join(lib.chunk('{:012x}'.format(int(mac1, 16) + 16).upper(), 2))

    uut.write_r0_mac()
    uut.write_r1_mac()

    logger.info('MAC verification with MAC:{}, SN:{}'.format(mac1, config.radio_sn_virtual[BAND_2G]))
    """
    cesiumlib.record_mac(config.radio_sn_virtual[BAND_2G],
                         config.radio_uuttype,
                         '0x{}'.format(mac1),
                         config.r0_mac_block_size.value + config.r1_mac_block_size.value)
    """


def radio_mac_verify():
    """
    get mac from daughter board and do mac verify
    :return:
    """
    r0_mac_from_uut, r0_mac_block_size_from_uut = uut.read_r0_mac()
    r1_mac_from_uut, r1_mac_block_size_from_uut = uut.read_r1_mac()

    if int(r1_mac_from_uut, 16) - int(r0_mac_from_uut, 16) != r0_mac_block_size_from_uut:
        raise BarbadosError('MAC_ADDRESS_ERROR', 'Wrong radio MAC block size')

    cesiumlib.verify_mac(
        config.radio_sn_virtual[BAND_2G],
        config.radio_uuttype,
        '0x{}'.format(r0_mac_from_uut),
        r0_mac_block_size_from_uut + r1_mac_block_size_from_uut
    )

    config.r0_mac_address.value = r0_mac_from_uut.upper()
    config.r0_mac_block_size.value = r0_mac_block_size_from_uut
    config.r1_mac_address.value = r1_mac_from_uut.upper()
    config.r1_mac_block_size.value = r1_mac_block_size_from_uut

    return lib.PASS


def program_cookie():
    # If fresh cookie (no PCB Serial Number), set temporary MAC now
    time.sleep(15)
    if uut.is_fresh_cookie():
        uut.write_all_mac()
    # MB SN
    uut.write_mb_sn()
    # Product part numbers and revision numbers
    uut.write_all_pn()
    # Defeult radio setting
    uut.write_default_radio_setting()
    return lib.PASS


def verify_cookie():
    uut.verify_cookie()
    return lib.PASS


@apollo_abort(cleanup_func=main_finalize)
def program_x509():
    try:
        uut.set_console_level4()
        uut.program_x509()
    finally:
        uut.set_console_level7()
    return lib.PASS


def validate_x509():
    try:
        uut.set_console_level4()
        uut.validate_x509(verify_service_date=False)
    finally:
        uut.set_console_level7()
    return lib.PASS


@apollo_abort(cleanup_func=main_finalize)
def program_act2():
    @apollo_log(file_name='act2/<station>.csv', headers=['ACT2 error code'])
    def _program_act2():
        uut.set_console_level4()
        # with FailLocking('PROGRAM_ACT2', 1800, 2, lock_by_container=False, exc_type=apexceptions.ServiceFailure):
        try:
            uut.program_act2()
        except Exception, ex:
            add_user_log(ex.message)
            raise
        uut.set_console_level7()

    _program_act2()
    return lib.PASS


def validate_act2():
    try:
        uut.set_console_level4()
        uut.validate_act2()
    finally:
        uut.set_console_level7()
    return lib.PASS


@apollo_error
def capwap_ping_test():
    uut.capwap_ping_test()
    return lib.PASS


def remove_giga_file():
    uut.remove_giga_file()
    return lib.PASS


@apollo_error
def linux_ping_test(speed=None):
    switch.set_speed(speed=speed)
    time.sleep(20)
    uut.linux_ping_test(speed)
    return lib.PASS


def version_control():
    """
    check the script verion
    :return:
    """
    if lib.get_apollo_mode() == lib.MODE_DEBUG:
        logger.info('Skip version check if run in DEBUG mode')
        return lib.SKIPPED
    server = Server(lib.conn.SERVER, 'server')
    server.source_code_diff_check('/opt/cisco/te/scripts/projects/wnbu/trunk/',
                                  ['utils', 'product_group_1', 'libs'])
    return lib.PASS
