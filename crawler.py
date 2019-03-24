#!/usr/bin/python3
# _*_ coding:utf-8 _*_

import random
import re
import threading
import socket
import ssl
from urllib import parse


# Clase principal
class Bot(object):
    
    # Constructor
    def __init__(self):

        self.cookies = {}
        self.lastUrl = None


    def executeFlow(self):

        result = self.httpRequest(url='https://hackerdev.net/robots.txt')
        print(result)


    def clearContext(self):

        # Crea una nueva instancia de navegación
        self.cookies = {}
        self.lastUrl = None


    def httpRequest(
        self,
        url,
        customHeaders=None,
        postData=None
    ):

        if(customHeaders):
            # Une las cabeceras personalizadas
            headers.update(customHeaders)

        referer = url
        if(self.lastUrl):
            referer = self.lastUrl

        self.lastUrl = url

        #Formatea la dirección URL
        urlParsed = parse.urlparse(url)
        urlData = {
            'original' : url,
            'path'     : urlParsed.path,
            'host'     : urlParsed.netloc,
            'port'     : urlParsed.port,
            'scheme'   : urlParsed.scheme
        }

        if urlData['path'] == '':
            urlData['path'] = '/'

        if(not urlData['port']):
            urlData['port'] = 443 if (urlData['scheme'] == 'https') else 80

        # Contenido del envío HTTP
        packet = (
            'GET ' + str(urlData['path'].strip()) + ' HTTP/1.1\r\n'
            'Host: ' + urlData['host'] + '\r\n'
            'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/54.0\r\n'
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n'
            'Accept-Language: en-US\r\n'
            'Referer: ' + referer + '\r\n'
            'Cookie: ' + self.getCookiesHttpFormat() + '\r\n'
            'Connection: close\r\n'
            '\r\n'
        )

        print('Conectando: ' + url + ' ...')

        socketHandler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketHandler.settimeout(40)
        
        # Usa SSL?
        if(urlData['scheme'] == 'https'):
            socketWraped = ssl.wrap_socket(socketHandler)
        else:
            socketWraped = socketHandler

        socketWraped.connect((str(urlData['host']), int(urlData['port'])))

        socketWraped.send(packet.encode('utf-8', 'ignore'))

        bytesRresponse = b''
        while True:
            bytesPart = socketWraped.recv(1024)
            bytesRresponse = bytesRresponse + bytesPart
            if bytesPart == b'':
                break
        socketWraped.shutdown(1)
        socketWraped.close()

        # Guarda las cookies
        self.parseCookiesByHttpResponse(bytesRresponse)

        statusCode = 0
        matches = re.search(br'HTTP\/\d\.\d (\d+) ', bytesRresponse, re.IGNORECASE | re.MULTILINE)
        if(matches):
            statusCode = int(matches.group(1))

        body = bytesRresponse.split(b'\r\n\r\n')
        headers = body.pop(0).strip()
        body = b'\r\n'.join(body)

        # Decodifica las cabeceras
        if(b'\r\n' in headers):
            tmp = {}
            for item in headers.split(b'\r\n'):
                value = item.split(b':')
                key = value.pop(0).strip()
                value = b':'.join(value)
                tmp[key] = value
            headers = tmp

        # Retorna los datos obtenidos
        return {
            'status-code'      : statusCode,
            'response-content' : body,
            'response-headers' : headers,
            'request-content'  : packet
        }


    def getCookiesHttpFormat(self):
        cookies = []
        for key, value in self.cookies.items():
            cookies.append(key + '=' + value)
        return '; '.join(cookies)


    def parseCookiesByHttpResponse(self, buffer_response):
        cookies = []
        matches = re.findall(br'set\-cookie:\s*(.*?);', buffer_response, re.IGNORECASE | re.MULTILINE)

        if len(matches) > 0:
            for cookie in matches:

                cookie = re.search(rb'(.*?)=(.*)', cookie, re.IGNORECASE | re.MULTILINE)
                
                var = cookie.group(1).strip()
                val = cookie.group(2).strip()

                if val:
                    self.cookies[var] = val

                else:
                    # Si la cookie existe la eliminará
                    if var in self.cookies.keys():
                        self.cookies.pop(var, None)


# Prueba la clase creada
bot = Bot()
bot.executeFlow()