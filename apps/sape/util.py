"""
This library allows to integrate sape.ru service into python website.
This library is NOT official sape.ru script.

This code uses fcntl library which is not windows compatible.
This library is port from PHP version 1.0.3.
I tryed to save original structure (even identifier names) of code to easely comparing with original.
You can find source of PHP version here: http://dumpz.org/2883/

Example of usage:

sape = SapeClient(host='YOUR SITE DOMAIN',
                  request_uri='THE URI OF REQUESTED PAGE',
                  user='SAPE USER ID',
                  db_file='path where sape links should be saved')
links = sape.return links()

You can send questions, bugreports and wishes to lizendir@gmail.com
"""

import random
import socket
import fcntl
import os
from datetime import datetime, timedelta
import time
import urllib2
import urllib

import phpserialize

# Default settings
SAPE_VERBOSE = False
SAPE_CHARSET = None
SAPE_SERVER_LIST = ['dispenser-01.sape.ru', 'dispenser-02.sape.ru']
SAPE_CACHE_LIFETIME = 3600
SAPE_CACHE_RELOADTIME = 600
SAPE_ERROR = ''
SAPE_FETCH_REMOTE_TYPE = 'file_get_contents'
SAPE_SOCKET_TIMEOUT = 6
SAPE_DB_FILE = ''
SAPE_USER_AGENT = 'SAPE_Client python'
SAPE_FORCE_SHOW_CODE = True

class SapeException(Exception):
    pass


class SapeBase(object):
    def __init__(self, *args, **kwargs):
        self.host = kwargs['host']
        if self.host.startswith('www.'):
            self.host = self.host[4:]
        self.request_uri = kwargs['request_uri']
        self.user = kwargs['user']
        self.db_file = kwargs['db_file']

        keys = ('verbose', 'charset', 'socket_timeout',
                'cache_lifetime', 'cache_reloadtime',
                'force_show_code', 'debug', 'server_list')
        for key in keys:
            default = globals().get('SAPE_%s' % key.upper())
            setattr(self, key, kwargs.get(key, default))

        self.dispenser_path = '/code.php?user=%s&host=%s&charset=utf-8' % (self.user, self.host)

        cookies = kwargs.get('cookies', {})
        self.is_our_bot = cookies.get('sape_cookie') == self.user
        self.debug = cookies.get('sape_debug') == '1'

        random.shuffle(self.server_list)


    def fetch_remote_file(self, host, path):
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(self.socket_timeout)

        url = 'http://%s%s' % (host, path)
        req = urllib2.Request(url)
        req.add_header('User-Agent', SAPE_USER_AGENT)
        try:
            resp = urllib2.urlopen(req)
        except urllib2.URLError:
            socket.setdefaulttimeout(old_timeout)
            raise SapeException('Network error')
        else:
            socket.setdefaulttimeout(old_timeout)
            return resp.read()



    def _open(self, fname, mode, lock):
        """
        Open file in MODE mode and the lock it with LOCK level.
        """

        try:
            fh = file(fname, mode)
        except IOError:
            raise SapeException('Could not open %s in %s mode' % (fname, mode))
        else:
            try:
                fcntl.flock(fh, lock)
            except IOError:
                raise SapeException('Could not lock file %s' % fname)
            else:
                return fh


    def _read(self, fname):
        """
        Read the file safely.
        """

        fh = self._open(fname, 'r', fcntl.LOCK_SH)
        data = fh.read()
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()
        return data


    def _write(self, fname, data):
        """
        Write to file safely.
        """

        fh = self._open(fname, 'w', fcntl.LOCK_EX)
        fh.write(data)
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()


    def load_data(self):
        """
        Load cached links and refresh them from sape.ru site if they is too old.
        """

        if not os.path.exists(self.db_file):
            try:
                file(self.db_file, 'w').write('')
                os.chmod(self.db_file, 0666)
            except IOError:
                raise SapeException('Could not create %s' % self.db_file)

        mtime = datetime.fromtimestamp(os.stat(self.db_file).st_mtime)
        check_time = datetime.now() - timedelta(seconds=self.cache_lifetime)

        self.db_file_mtime = mtime
        self.db_file_updated = False

        if mtime < check_time or not os.path.getsize(self.db_file):
            self.db_file_updated = True

            new_mtime = check_time + timedelta(seconds=self.cache_reloadtime)
            ts = time.mktime(new_mtime.timetuple())
            os.utime(self.db_file, (ts, ts))

            for server in self.server_list:
                data = self.fetch_remote_file(server, self.dispenser_path)
                if data.startswith('FATAL ERROR'):
                    raise SapeException(data)
                else:
                    try:
                        # check the integrity of data
                        phpserialize.loads(data)
                    except:
                        raise SapeException('Could not deserialize repsonse from server')
                    else:
                        self._write(self.db_file, data)

        data = self._read(self.db_file)
        return phpserialize.loads(data)


class SapeClient(SapeBase):

    def __init__(self, *args, **kwargs):
        self.links_delimiter = ''
        self.links = []
        self.links_page = []

        super(SapeClient, self).__init__(self, *args, **kwargs)
        self.set_data(self.load_data())


    def return_links(self, number=None, join=False):
        """
        Return links for current URI.

        You can call this function several times with NUMBER argument.
        Note that last call MUST NOT have NUMBER argument.
        """

        if isinstance(self.links_page, list):
            total_page_links = len(self.links_page)
            if not number or number > total_page_links:
                number = total_page_links
            links = self.links_page[:number]
            self.links_page = self.links_page[number:]

            links = map(self.decode, links)
            if join:
                html = self.links_delimiter.join(links)
                if self.is_our_bot:
                    html = '<sape_noindex>%s</sape_noindex>' % html
                return html
            else:
                return links
        else:
            return self.links_page


    def set_data(self, data):
        self.links = data

        if '__sape_delimiter__' in self.links:
            self.links_delimiter = self.links['__sape_delimiter__']

        uri_links = self.links.get(urllib.quote(
            self.request_uri.encode('utf-8'), safe='/?&='), None)

        if isinstance(uri_links, dict):
            self.links_page = uri_links.values()
        else:
            new_url = self.links.get('__sape_new_url__', None)
            if new_url:
                # Note that default force_show_code value is True
                # I did this because I'm not sure that every user
                # of this library will pass cookies dict to SapeClient
                # constructor (cookies required for detecting sape bot)
                if self.is_our_bot or self.force_show_code:
                    self.links_page = [new_url]


    def decode(self, data):
        data = data.decode('utf-8')
        if self.charset:
            data = data.encode(self.charset)
        return data
