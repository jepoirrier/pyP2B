#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retrieve PubMed reference from its PMID given in function
Copyright (C) 2006-2007 Jean-Etienne Poirrier

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

WARNING: no check for duplicate references (just add the ref)
TODO: all exception handling
INFOS: http://www.poirrier.be/~jean-etienne/software/pyp2b/
E-MAIL: jepoirrier@gmail.com
"""
import codecs

from lxml import etree
from lxml.etree import fromstring

import os
import sys
#import urllib2
import requests

class pyP2B:


    def getPubmedReference(self, pubmedUID):

        def is_non_zero_file(fpath):  
            return os.path.isfile(fpath) and os.path.getsize(fpath) > 0
        
        def striplastdot(s):
            """ Small function to strip last dot in string (along with leading and trailing spaces) """
            l = len(s)
            if l > 1: # at least 1 letter (dot!)
                s.strip()
                if s.endswith('.'):
                    s = s[0:l-1]
            return s

        def stripelref(s):
            """ Small function to strip electronic reference in Journal title (if exists) """
            l = len(s)
            if l > 22: # at least 22 letters
                if s.endswith(" [electronic resource]"):
                    s = s[0:l-22]
            return s

        if len(str(pubmedUID)) < 1:
            return("Error, pubmedId not sent\n")

#        print("Get info for pubmedId : {0}".format(str(pubmedUID)))

        correctRef = False
#        tmpFileName = 'pyP2Btmp.xml'
        tmpFileName = "./XmlFiles/" + pubmedUID + ".xml"
        tmpFileName = tmpFileName.replace('?', '')
        

        deftab = 2
        
        if (is_non_zero_file(tmpFileName) is False):
            qsStart = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" +\
                  "&db=pubmed&id="
            qsEnd = "&retmode=xml&rettype=medline"

            """ get a PubMed ID and returns a string with ref in BibTex format """
            # Building complete query string
            queryString = qsStart + str(pubmedUID) + qsEnd

            # print("\n*****\n {0} \n****\n".format(queryString))
            # Sample :
            # http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&id=23982426&retmode=xml&rettype=medline

            # Getting something from PubMed ...
            # result = urllib2.urlopen(queryString)
            result1 = requests.post(queryString)
            result = result1.text
            print("\n=====\n {0} \n=====\n".format(result))

            # Processing file (because it was plain HTML, not text)
            f = open(tmpFileName, 'w', encoding="utf-8")

            for line in result:
                line = line.replace('<pre>', '')
                line = line.replace('</pre>', '')
                line = line.replace('&lt;', '<')
                line = line.replace('&gt;', '>')
                line = line.replace('\n', '')
                line = line.replace('&quot;', '"')
                line = line.replace('â€‰', '')
                line = line.replace(' ', '')            # â€‰
                line = line.replace('±', '+/-')         # ±
                line = line.replace('Â', '')            # Â
                f.write(line)
            f.close()

        # Verification if it's a correct reference ...
        
        # print("parsing file {0}".format(tmpFileName))
        
        f = open(tmpFileName, 'r', encoding="utf-8")
        for line in f:
            if line.endswith('</PubmedArticleSet>'):
                correctRef = True
        f.close()

        if(correctRef == True):
            # Opening it with lxml and XPath
            f = open(tmpFileName, 'r', encoding="utf-8")
            tree = etree.parse(f)

            # get authors
            authors = ""
            firstLastname = ""

            authl = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/AuthorList/Author/LastName')
            authi = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/AuthorList/Author/Initials')
            for i in range(len(authl)):
#                lastname = str((authl[i].text).encode("utf-8"))
                lastname = str((authl[i].text))

                if (i == 0):
                    firstLastname = lastname

                initials = ""
                for j in range(len(authi[i].text)):
                    initials = initials + str(authi[i].text)[j]
                    initials = initials + "."
                if i > 0:
                    authors = "%s and %s, %s" % (authors, lastname, initials)
                else: #i = 0
                    authors = "%s, %s" % (lastname, initials)

            # Can't find the author name, may be collective publication

            if (len(authors) == 0):
                authCol = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/AuthorList/Author/CollectiveName')
                if (len(authCol) > 0):
                    lastname = str((authCol[0].text))
                    authors = lastname
                    firstLastname = lastname[: lastname.find(' ')]
                else:
                    lastname = "Collective"
                    authors = lastname
                    firstLastname = "Collective"

            # get title
            title = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/ArticleTitle')
            title = striplastdot(title[0].text)

            # get year
            year = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/PubDate/Year')
            if (len(year) > 0):
                #print("Year |{0}|".format(year))
                try:
                    year = year[0].text
                except:
                    year = year[0:3]
                # Sometimes the publication date has the format "2016 june 10" and the tag year is unknown
                # So we use the pubmed date publication.
                # We can change this by the right field name
            else:
                year = tree.xpath('/PubmedArticleSet/PubmedArticle/PubmedData/History/PubMedPubDate/Year')
                year = year[0].text

            # build id (first author's last name + two last year digit)
            # four year digits - compliance with Jabref

            bibtexId = firstLastname.lower() + year

            # Remote spaces from bibtex Id
            if (bibtexId.find(" ") >= 0):
                bibtexId = bibtexId.replace(" ", "_")

            # get journal
            journal = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/Journal/Title')
            journal = stripelref(striplastdot(journal[0].text))

            # get volume
            volume = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/Volume')
            if (len(volume) > 0):
                volume = volume[0].text
            else:
                volume = ""

            # get issue (if exists)
            issue = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/Issue')
            if len(issue) > 0:
                issue = issue[0].text
            else:
                issue = "0"

            # get pages
            pages = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/Pagination/MedlinePgn')
            pages = pages[0].text
            try:
                if (pages.find("-") >= 0):
                    pages = pages.replace("-", "--")
            except:
                pages = ""

            # get PMID
            pmid = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/PMID')
            pmid = pmid[0].text

            # get doi (if exists)
            idlist = tree.xpath('/PubmedArticleSet/PubmedArticle/PubmedData/ArticleIdList/ArticleId')
            doi = "0"
            if len(idlist) > 0:
                for i in range(len(idlist)):
                    if str(idlist[i].attrib['IdType'])== 'doi':
                        doi = idlist[i].text

            # get abstract (if exists)
            idlist = tree.xpath("/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/Abstract/AbstractText")
            abstractText = ""
            if len(idlist) > 0:
                 kk = len(idlist)
                 ll = 0
                 for tAbstract in tree.xpath("/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/Abstract/AbstractText"):
                    try:
                        abstractText = abstractText + tAbstract.text
                        ll = ll + 1
                        if ll <= kk - 2:
                            abstractText = abstractText + "\n"
                    except:
                        if (len(abstractText) > 0):
                            abstractText = abstractText + "\n"

            # get keywords
            # remark : in pubmed, the keywords are not the keywords found in the publication but
            # the MESH terms indicatied by the author(s)
            # Should be better to find them by
            # <DescriptorName MajorTopicYN="Y" UI="Dnnnn">MESH_TERM</DescriptorName>
            # with MajorTopicYN = Y UI is a letter followed by numbers

            idlist = tree.xpath("/PubmedArticleSet/PubmedArticle/MedlineCitation/KeywordList/Keyword")
            lKeywords = ""
            if len(idlist) > 0:
                for i in range(len(idlist)):
                    lKeywords = lKeywords + idlist[i].text
                    if i <= (len(idlist) - 2):
                        #print(i)
                        lKeywords = lKeywords + "; "

             # get Publication Type (if exists)
             # for our purpose, you get all the terms. It is possible to get the firts one (option ?)
            idlist = tree.xpath("/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/PublicationTypeList/PublicationType")
            pubType = ""

            if len(idlist) > 0:
                kk = len(idlist)
                ll = 0
                for tPubType in tree.xpath("/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/PublicationTypeList/PublicationType"):
                    ll = ll + 1
                    pubType = pubType + tPubType.text
                    if (ll < kk):
                        pubType = pubType + "; "


            f.close()

            # Now write output (to include in a pipe)
            result = ""
            result = result + "@article{%s,\n" % (bibtexId)
            result = result + ("\tauthor = {%s},\n" % (authors)).expandtabs(deftab)
            result = result + ("\ttitle = {%s},\n" % (title)).expandtabs(deftab)
            if (len(abstractText) > 0):
                result = result + ("\tabstract = {%s},\n" % (abstractText)).expandtabs(deftab)

            if (len(lKeywords) > 0):
                result = result + ("\tkeywords = {%s},\n" % (lKeywords)).expandtabs(deftab)

            result = result + ("\tyear = {%s},\n" % (year)).expandtabs(deftab)
            result = result + ("\tjournal = {%s},\n" % (journal)).expandtabs(deftab)
            result = result + ("\tvolume = {%s},\n" % (volume)).expandtabs(deftab)

            if issue != "0":
                result = result + ("\tnumber = {%s},\n" % (issue)).expandtabs(deftab)
            result = result + ("\tpages = {%s},\n" % (pages)).expandtabs(deftab)

            if (len(pubType) > 0):
                result = result + ("\ttype = {%s},\n" % (pubType)).expandtabs(deftab)

            result = result + ("\tpmid = {%s}" % (pmid)).expandtabs(deftab)

            if doi != "0":
                result = result + (",\n\tdoi = {%s}\n" % (doi)).expandtabs(deftab)
            else:
                result = result + ("\n")
                
            result = result + "}\n"

            # Clean up things ...
            # Better to add an arg in the command line.
            # Inactivate here for special needs
            
#            os.remove(tmpFileName)
        else:
            result = "Reference %s not found. Aborting" % str(pubmedUID)

        return(result)
