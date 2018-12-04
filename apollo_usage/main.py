import pxssh

check_list = ['fxcavp212', 'fxcavp221', 'fxcavp214', 'fxcavp217', 'fxcavp351', 'fxcavp369', 'fxcavp362',
                        'fxcavp354', 'fxcavp455', 'fxcavp306', 'fxcavp149', 'fxcavp211', 'fxcavp367',
                           'fxcavp373', 'fxcavp139', 'fxcavp287', 'fxcavp288', 'fxcapp38',
                           'fxcapp161', 'fxcavp18', 'fxcavp19', 'fxcavp135',
                           'fxcavp220', 'fxcavp230', 'fxcavp219', 'fxcavp79', 'fxcavp82', 'fxcavp55', 'fxcavp218']

test1 = ['fxcavp217', 'fxcavp351', 'fxcavp149', 'fxcapp161', 'fxcavp18', 'fxcavp19', 'fxcavp135', 'fxcavp82']
username = 'blaze'
password = 'Foxconn20190.'
limits = 60


class CheckStatus(object):
    def __init__(self):
        pass

    def login_check(self):
        out_put_buffer = []
        for i in check_list:
            print 'logging in to {}'.format(i)
            try:
                s = pxssh.pxssh()
                s.login(i, username, password)
                s.sendline('df -h')
                s.prompt()
                ret = s.before
                # print ret
                s.logout()
                if self.process_data(ret):
                    out_put_buffer.append(i + self.process_data(ret))
            except Exception:
                print 'log in to {} fail'.format(i)
        return out_put_buffer

    @staticmethod
    def process_data(input_data):
        proce1 = input_data.split('\n')
        for i in proce1:
            if ' /home' in i:
                print i
                res1 = i.split( )
                res2 = res1[3]
                compare = int(res2[:-1])
                if compare >= limits:
                    return i
                else:
                    return False


def main():
    g = CheckStatus()
    ret = g.login_check()
    print ret
    f = open('machine_result.txt', 'w')
    for i in ret:
        f.write(i + '\n')

    f.close()

if __name__ == '__main__':
    main()