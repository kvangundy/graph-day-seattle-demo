#!/usr/bin/env python2
#this is a sample app built using Nigel Small's py2neo drive
#to install, copy and paste the following two comments into your cmd line without the hash
#sudo easy_install pip
#pip install py2neo
#
import py2neo
from py2neo import Graph, Path
from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse

HTTP_PORT = 8080
NEO_PROTOCOL = 'http'
NEO_HOST = 'localhost'
NEO_PORT = 7474
NEO_USER = 'neo4j'
NEO_PASSWORD = '123'

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
      response_parts = [
        "<html><head>",
        "<style type='text/css'>",
        "td,li,h1 { font-family: 'Open Sans','Helvetica Neue','Helvetica','Arial' } ",
        "</style>",
        "</head>",
        "<body>",
        "<table border='0'><tr><td>"
        "<img src='http://neo4j.com/wp-content/themes/neo4jweb/assets/images/neo4j-blue-logo.png' />"
        "</td></tr></table>",
        "<h1>Employee Relationships</h1>",
        "<ul>"
        ]

      # py2neo.set_auth_token('%s:%s' % (NEO_HOST, NEO_PORT), NEO_AUTH_TOKEN)
      graph = Graph('%s://%s:%s@%s:%s/db/data/' % 
        (NEO_PROTOCOL, NEO_USER, NEO_PASSWORD, NEO_HOST, NEO_PORT))

      cyres = graph.cypher.execute("""MATCH 
        path = (e:Employee)<-[:REPORTS_TO*]-(sub)
      WITH 
        e, sub, 
        [person in NODES(path) | person.firstName][1..-1] AS path
      RETURN 
        e.employeeID AS managerID,
        e.firstName AS managerName,
        sub.employeeID AS employeeID,
        sub.firstName AS employeeName,
        CASE 
          WHEN LENGTH(path) = 0 
            THEN null 
          ELSE path END AS via
      ORDER BY LENGTH(path)""");

      for record in cyres:
        response_parts.append("<li>")
        response_parts.append("<b>%s</b> reports to <b>%s</b>" % 
          (record['employeeName'], record['managerName']))
        if isinstance(record['via'], list):
          response_parts.append("via")
          response_parts.append("<b>")
          response_parts.append(','.join(record['via']))
          response_parts.append("</b>")
        response_parts.append("</li>")

      response_parts.append("</body></html>")
      message = '\r\n'.join(response_parts)
      self.send_response(200)
      self.end_headers()
      self.wfile.write(message)
      return


if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('', HTTP_PORT), GetHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()



