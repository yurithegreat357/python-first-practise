import datetime
import logging
import os
import shelve
from apollo.libs import lib
from apollo.config import config_fail_lock

logger = logging.getLogger(__name__)


class Faillock(object):
    def __init__(self, serial_number):
        self.container = str(lib.get_my_container_key().split("|")[-1])
        logger.info('The container number is {}'.format(self.container))
        self.serial = str(serial_number)
        logger.info('The serial number is {}'.format(self.serial))
        self.reset_time = config_fail_lock.reset_time
        self.count = config_fail_lock.max_fail_time
        self.timestampkey = self.container + 'tcount'
        self.keytotal = str(self.container) + 'total'
        self.all_total = self.get_data('total')
        self.passkey = self.container + 'P'

    def fail_count_check(self, *args):
        """Include serial number when invoke the Faillock() class. Place this function in pre-finalize steps first,
         use lib.get_apollo_mode() to assign a value to *args.(example 1)
         Use lib.apdicts.test_info.current_status to assign fail or pass status at step main-finalize in order to
        catch & record any fails.
        If you wanna use lock on step mode, put try .... except Exception between your desired steps and place the fail
        message at finalize step to catch the Fail message(see example 3 and 2)

        example 1 :
           def main_initialize():
                lock = fail_lock.Faillock(mb_tst_info['serial_number'])
                lock.fail_count_check(lib.get_apollo_mode())
                 return lib.PASS

        example 2:
            def main_finalize():
                try:
                    pass
                finally:
                    lock = fail_lock.Faillock(mb_tst_info['serial_number'])
                    lock.fail_count_check(lib.apdicts.test_info.current_status, lib.get_apollo_mode())
             return lib.PASS

         example 3:
            try:
             pn = set_scan_part_number('part number', label_format='74-{:d}{:d}{:d}{:d}{:d}{:d}-{:d}{:d} {:w}{:d}')
             sn = set_scan_serial_number('serial number')
             cn = set_scan_container_number('container number', label_format=lib.get_my_container_key().split('|')[-1])
             pn, sn, container_number = scan_all_labels(pn, sn, cn)
                .......
             retuen lib.PASS

             except Exception:
                lock = fail_lock.Faillock(mb_tst_info['serial_number'])
                lock.lock_on_step('Label scan Failed')
                return lib.FAIL, 'Label scan Failed'

        """
        mode = config_fail_lock.mode
        self.compare_count_time()
        if 'PASS' in args:
            self.passing_count()
            self.product_count()
        elif 'DEBUG' in args and 'FAIL' in args:
            logger.info('This is Debug mode, Count will not be considered')
            self.product_count()
        elif 'FAIL' in args:
            if 'PROD' in args:
                self.increase_count()
                self.compare_count()
                self.create_time_stamp()
                if mode is '1':
                    self.compare_count()
                    self.write_data(self.serial, 'Failed')
                    self.product_count()
                elif mode is '2':
                    self.lock_on_step(args)
                    self.write_data(self.serial, 'Failed')
                    self.product_count()
                elif mode is '3':
                    self.yields_cal()
                    self.write_data(self.serial, 'Failed')
                    self.product_count()
                elif mode is '4':
                    self.total_yields_cal()
                    self.write_data(self.serial, 'Failed')
                    self.product_count()
                elif mode is '5':
                    logger.info('Count started to compare')
                    self.compare_count_time()
                    self.yields_cal()
                    self.total_yields_cal()
                    self.write_data(self.serial, 'Failed')
                    self.product_count()
            else:
                pass
        elif 'PROD' in args:
            self.compare_count()
        return lib.PASS

    def lock_on_step(self, error_message):
        if error_message in config_fail_lock.designated_failstep1:
            logger.info('Start comparing FAIL message')
            self.increase_stepcount(error_message)
            self.compare_stepcount(error_message, 1)
        elif error_message in config_fail_lock.designated_failstep2:
            self.increase_stepcount(error_message)
            self.compare_stepcount(error_message, 2)
        elif error_message in config_fail_lock.designated_failstep3:
            self.increase_stepcount(error_message)
            self.compare_stepcount(error_message, 3)
        elif error_message in config_fail_lock.designated_failstep4:
            self.increase_stepcount(error_message)
            self.compare_stepcount(error_message, 4)

        pass

    def increase_stepcount(self, errmsg):
        check = self.get_data(self.serial)
        mode = lib.get_apollo_mode()
        if check is 0 and mode is not 'DEBUG':
            count = self.get_data(self.container + errmsg)
            count += 1
            self.write_data(self.container + errmsg, count)
            logger.warning('Step {0} has {1} counts'.format(errmsg, count))
        else:
            logger.info('This is a retest board!')
            pass

    def compare_stepcount(self, errmsg, number):
        count = self.get_data(self.container + errmsg)
        if count > config_fail_lock.stepmaxfail[number]:
            self.lock_engage(reason='Step {0} Exceed {1} times of fails'.format(errmsg,
                                                                                      config_fail_lock.max_fail_time))
            logger.info('Step {0} Exceed {1} times of fails'.format(errmsg, config_fail_lock.max_fail_time))
        else:
            pass

    def compare_count(self):
        count = self.get_data(self.container)
        logger.warning('The current count is {}'.format(count))
        if count >= config_fail_lock.max_fail_time:
            self.lock_engage(reason= 'Exceed {} times of fails'.format(config_fail_lock.max_fail_time))
        else:
            pass

    def create_time_stamp(self):
        counter = self.get_data(self.timestampkey)
        logger.info('The time stamp count is {}'.format(self.get_data(self.timestampkey)))
        counter += 1
        stamp = datetime.datetime.now()
        key = self.container + str(counter)
        logger.info('The stamp key is {}'.format(key))
        self.write_data(key, stamp)
        self.write_data(self.timestampkey, counter)

    def compare_count_time(self):
        failtime1 = str(self.container) + '1'
        time1 = self.get_data(failtime1)
        logger.info('The time1 is {}'.format(time1))
        reset = datetime.timedelta(hours=config_fail_lock.reset_time)
        now = datetime.datetime.now()
        logger.info('The current time is {}'.format(now))
        failcount = self.get_data(self.container)
        logger.info('The failcount is {}'.format(failcount))
        count = config_fail_lock.max_fail_time
        logger.info('The current max fail count is {}'.format(count))
        if time1 is 0 and failcount < count:
            pass
        elif failcount <= count and now - time1 > reset:
            self.write_data(self.container, 0)
            self.write_data(self.keytotal, 0)
            self.write_data(self.passkey, 0)
            self.write_data(self.timestampkey, 0)
            self.write_data(failtime1, 0)
            logger.info("Reset counts because {} hours reset setting".format(reset))
            return lib.PASS

        elif failcount > count:
            self.lock_engage(reason= 'the cell is still in lock up')

        elif failcount < count:
            pass

    def increase_count(self):
        mode = lib.get_apollo_mode()
        serial = self.serial
        check = self.get_data(serial)
        logger.info('The serial check is {}'.format(check))
        if check is 0 and mode is not 'DEBUG':
            count = self.get_data(self.container)
            count += 1
            logger.warning('The count is {}'.format(count))
            self.write_data(self.container, count)
            self.write_data(self.serial, 'PASS')
        elif mode is 'DEBUG' or check is 'PASS':
            logger.warning('This is a retest board in {} mode!'.format(mode))
            pass

    def faillock_debug_menu(self):
        logger.info('The container number is {}'.format(self.container))
        menu1 = """Select an item to run?
               0. EXIT
               1. Show current count
               2. Clear all Fail counts
               3. Remove count files (Wipe out the serial number counts)
               4. Show current count reset duration
               5. Show history failtimes
               6. Clear step fail counts"""
        menu2 = """Run item {} success. """ + menu1
        menu3 = """Run item {} failed - {}. """ + menu1
        menu = menu1

        while True:
            try:
                answer = lib.ask_question(menu)
                if answer == '0':
                    break
                elif answer == '1':
                    num = self.get_data(self.container)
                    lib.ask_question('The current count is {}'.format(num))
                elif answer == '2':
                    self.reset_counts()
                elif answer == '3':
                    os.remove('/opt/cisco/constellation/apollo/logs/faillock.db')
                elif answer == '4':
                    lib.ask_questions(questions='The current duration is {}'.format(str(config_fail_lock.reset_time)))
                elif answer == '5':
                    i = self.get_data(self.timestampkey)
                    for i in range(i):
                        key = self.container + str(i)
                        time = self.get_data(key)
                        lib.ask_question('the time{0} is {1}'.format(i, time))
                elif answer == '6':
                    self.write_data(config_fail_lock.designated_failstep1, 0)
                    self.write_data(config_fail_lock.designated_failstep2, 0)
                    self.write_data(config_fail_lock.designated_failstep3, 0)
                    self.write_data(config_fail_lock.designated_failstep4, 0)
                menu = menu2.format(answer)
            except Exception, ex:
                menu = menu3.format(answer, str(ex))

    def get_data(self, key):
        try:
            s = shelve.open('/opt/cisco/constellation/apollo/logs/faillock.db', 'c')
            data = s[key]
            s.close()
            return data

        except Exception:
            self.write_data(key, 0)
            return 0

    def write_data(self, args, number):
        s = shelve.open('/opt/cisco/constellation/apollo/logs/faillock.db', 'c')
        s[args] = number
        s.close()

    def reset_counts(self):
        self.write_data(self.container, 0)
        self.write_data(self.passkey, 0)
        self.write_data(self.timestampkey, 0)
        self.write_data(config_fail_lock.designated_failstep1, 0)
        self.write_data(config_fail_lock.designated_failstep2, 0)
        self.write_data(config_fail_lock.designated_failstep3, 0)
        self.write_data(config_fail_lock.designated_failstep4, 0)

    def lock_engage(self, reason):
        mode = lib.get_apollo_mode()
        if mode is 'DEBUG':
            logger.info('Debug mode, lock will be dismissed')
            self.reset_counts()
            return lib.PASS
        else:
            for i in range(3):
                questions = 'Too many FAILS because of {},Stop testing and contact TE now!'.format(reason)
                check_answer = lib.ask_question(question=questions,
                                                picture_path='images/fail.jpg', picture_size='small',
                                                timeout=1000)

                if 'debug' in check_answer:
                    self.faillock_debug_menu()
                    return lib.PASS

                elif config_fail_lock.password in check_answer:
                    self.reset_counts()
                    return lib.PASS

                elif check_answer not in config_fail_lock.password:
                    text = 'Wrong answer!'
                    lib.ask_question(question=text)
            else:
                logger.info('Wrong answers, count reset fail!')
                raise Exception("Wrong password! Unable to proceed test!")

    def passing_count(self):
        number = self.get_data(self.passkey)
        mode = lib.get_apollo_mode()
        if number < 2 and mode is not 'DEBUG':
            number += 1
            self.write_data(self.passkey, number)
            logger.info('The pass count is {}'.format(number))
        elif number >= 2 and mode is not 'DEBUG':
            self.write_data(self.container, 0)
            self.write_data(self.passkey, 0)
            self.write_data(self.timestampkey, 0)
            logger.warning('Two consecutive Pass. Fail count has been reset!')
        elif mode is 'DEBUG':
            pass

    def product_count(self):
        total = self.all_total
        cell_product = self.get_data(self.keytotal)
        reset_time = self.get_data('product')
        current = datetime.datetime.now()
        if reset_time is 0:
            self.write_data('product', datetime.datetime.now())
        elif current - reset_time < datetime.timedelta(days=config_fail_lock.product_count_reset):
            total += 1
            cell_product += 1
            self.write_data(self.keytotal, cell_product)
            self.write_data('total', total)
            logger.warning('The mass product is {0}, the cell product is {1}'.format(total, cell_product))
        elif current - reset_time > datetime.timedelta(days=config_fail_lock.product_count_reset):
            self.write_data('product', 0)

    def yields_cal(self):
        total = float(self.get_data(self.keytotal))
        fail = float(self.get_data(self.container))
        if total >= 100:
            try:
                logger.info('The fail is {}'.format(fail))
                logger.info('The total is {}'.format(total))
                rate = 1.0 - (fail/total)
                logger.info('The yield rate is {}'.format(rate))
                if rate != 0 and rate < config_fail_lock.cell_yield:
                    self.lock_engage(reason='Total yields is lower than {0}, The '
                                                     'current rate is {1}'.format(config_fail_lock.cell_yield,
                                                                                  rate))
                else:
                    pass
            except ZeroDivisionError:
                pass
        else:
            pass

    def total_yields_cal(self):
        total = self.all_total
        fail = float(self.get_data(self.container))
        if total >= 100:
            try:
                logger.info('The fail is {}'.format(fail))
                logger.info('The all station total is {}'.format(total))
                rate = 1.0 - (fail/total)
                logger.info('The yield rate is {}'.format(rate))
                if rate != 0 and rate < config_fail_lock.total_yield:
                    self.lock_engage(reason='This total yields rate is lower than {0}, The '
                                                     'current rate is {1}'.format(config_fail_lock.total_yield,
                                                                                  rate))
                else:
                    pass
            except ZeroDivisionError:
                pass
        else:
            pass