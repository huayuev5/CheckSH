# coding:utf-8
# author lijingxin
# Date 2016/06/04

import urllib
import urllib2
import httplib
import urlparse
import logging
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

from lxml import etree
import gevent


def get_file_logger(name, path='.', 
                    format='%(asctime)s %(levelname)s\n%(message)s\n', 
                    level=logging.DEBUG):
    log = logging.getLogger(name)
    if not log.handlers:
        handler = logging.FileHandler('%s/%s.log' % (path, name))
        formatter = logging.Formatter(format)
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.setLevel(level)
    return log

log = get_file_logger('sohu', level=logging.DEBUG)


class GetPageHandler(object):
    def __init__(self):
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4)'
        self.headers = {'User-Agent': user_agent}

    def get_page(self, url='', decode_str='utf-8'):
        """
            根据url获取页面信息
        """
        try:
            page = ''
            if not url.strip():
                raise Exception('url is None')
            req = urllib2.Request(url, headers=self.headers)
            response = urllib2.urlopen(req, timeout=0.5)
            html = response.read()
            page = html.decode(decode_str)
        except Exception, e:
            log.debug('[%s] download page failed: %s' % (url, e))
            return None
        return page

    def check_sohu_url(self, url):
        """
            过滤出符合规则的url
        """
        value = urlparse.urlparse(url)
        if value.scheme not in ['http', 'https', '']:
            return None
        if value.path in ['', '#', '/']:
            return None

        if value.netloc not in ['', 'm.sohu.com']:
            return None
        else:
            return urlparse.urlunparse(value._replace(netloc="m.sohu.com", 
                                                      scheme="http"))

    def clean_sohu_page(self, url):
        """
            处理html页面过滤出url
        """
        result = []
        try:
            page = self.get_page(url)
            e_page = etree.HTML(page.lower())
            hrefs = e_page.xpath(u"//a")
            for href in hrefs:
                if href.get('href'):
                    value = self.check_sohu_url(href.get('href'))
                    if value:
                        result.append(value)
        except Exception, e:
            log.debug('[%s] parse page failed: %s' % (url, e))
        return result

    def clean_sohu_pages(self, urls, urlshandler):
        result = []
        for url in urls:
            result = result + self.clean_sohu_page(url)
        
        return result

    def recursion_sohu_pages(self, url_list, urlshandler):
        if urlshandler.add(url_list):
            result = list(set(self.clean_sohu_pages(url_list, urlshandler)).difference(set(urlshandler.urls)))
            return self.recursion_sohu_pages(result, urlshandler)
        else:
            return None


class UrlsHandler(object):
    """
    """
    urls = []

    def __init__(self, url_list=[]):
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4)'
        self.headers = {'User-Agent': user_agent}
        for i in url_list:
            self.urls.append(i)

    def add(self, url_list):
        len_a = len(self.urls)
        if url_list:
            for i in url_list:
                if i not in self.urls:
                    self.urls.append(i)
            len_b = len(self.urls)
            log.info("已更新url列表 %s" % str(self.urls))
            return True if len_a < 100 else False
            # return True if len_a != len_b else False
        else:
            return False

    def chunks(self, length=10):
        for i in range(0, len(self.urls), length):
            yield self.urls[i:i+length]

    def check_url(self, url):
        try:
            req = urllib2.Request(url, headers = self.headers)
            page_open = urllib2.urlopen(req)

        except urllib2.HTTPError, e:
            log.error("%s 访问错误 %s" % (url, str(e)))
        except urllib2.URLError, e:
            log.error("%s 访问错误 %s" % (url, str(e)))
        except Exception, e:
            import ipdb; ipdb.set_trace();
            log.error("%s 访问异常" % (url, str(e)))
        return True


    def check_urls(self):
        for url_list in self.chunks():
            threads = [gevent.spawn(self.check_url, i) for i in url_list]
            gevent.joinall(threads)


def main():
    pagehandler = GetPageHandler()
    urlshandler = UrlsHandler()
    print "程序已启动，正在抓取页面..."
    pagehandler.recursion_sohu_pages(['http://m.sohu.com'], urlshandler)
    print "url 收集完成，正在检查..."
    urlshandler.check_urls()


if __name__ == '__main__':
    main()

