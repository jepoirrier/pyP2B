#!/usr/bin/python
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
import os
import sys
import urllib2

class pyP2B:

    def getPubmedReference(self, pubmedUID):
    
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
        
        correctRef = False
        tmpFileName = 'pyP2Btmp.xml'
        deftab = 2
	qsStart = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" +\
	          "&db=pubmed&id="
        qsEnd = "&retmode=xml&rettype=medline"

        """ get a PubMed ID and returns a string with ref in BibTex format """
        # Building complete query string
        queryString = qsStart + str(pubmedUID) + qsEnd
        
        # Getting something from PubMed ...
        result = urllib2.urlopen(queryString)

        # Processing file (because it was plain HTML, not text)
        f = open(tmpFileName, 'w')

        for line in result:
            line = line.replace('<pre>', '')
            line = line.replace('</pre>', '')
            line = line.replace('&lt;', '<')
            line = line.replace('&gt;', '>')
            line = line.replace('\n', '')
            line = line.replace('&quot;', '"')
            f.write(line)
        f.close()

        # Verification if it's a correct reference ...
        f = open(tmpFileName, 'r')
        for line in f:
            if line.endswith('</PubmedArticleSet>'):
                correctRef = True
        f.close()

        if(correctRef == True):
            # Opening it with lxml and XPath
            f = open(tmpFileName, 'r')
            tree = etree.parse(f)

            # get authors
            authors = ""
            authl = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/AuthorList/Author/LastName')
            authi = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/AuthorList/Author/Initials')
            for i in range(len(authl)):
                lastname = str((authl[i].text).encode("utf-8"))
                initials = ""
                for j in range(len(authi[i].text)):
                    initials = initials + str(authi[i].text)[j]
                    initials = initials + "."
                if i > 0:
                    authors = "%s and %s, %s" % (authors, lastname, initials)
                else: #i = 0
                    authors = "%s, %s" % (lastname, initials)

            # get title
            title = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/ArticleTitle')
            title = striplastdot(title[0].text)

            # get year
            year = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/PubDate/Year')
            year = year[0].text

            # build id (first author's last name + two last year digit)
            bibtexId = authl[0].text.lower() + year[len(year)-2:len(year)]

            # get journal
            journal = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/Journal/Title')
            journal = stripelref(striplastdot(journal[0].text))

            # get volume
            volume = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/Volume')
            volume = volume[0].text

            # get issue (if exists)
            issue = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/Issue')
            if len(issue) > 0:
                issue = issue[0].text
            else:
                issue = "0"

            # get pages
            pages = tree.xpath('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/Pagination/MedlinePgn')
            pages = pages[0].text
            pages = pages.replace("-", "--")

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

            f.close()

            # Now write output (to include in a pipe)
            result = ""
            result = result + "@article{%s,\n" % (bibtexId)
            result = result + ("\tauthor = {%s},\n" % (authors)).expandtabs(deftab)
            result = result + ("\ttitle = {%s},\n" % (title)).expandtabs(deftab)
            result = result + ("\tyear = %s,\n" % (year)).expandtabs(deftab)
            result = result + ("\tjournal = {%s},\n" % (journal)).expandtabs(deftab)
            result = result + ("\tvolume = %s,\n" % (volume)).expandtabs(deftab)
            if issue != "0":
                result = result + ("\tnumber = %s,\n" % (issue)).expandtabs(deftab)
            result = result + ("\tpages = {%s},\n" % (pages)).expandtabs(deftab)
            result = result + ("\tpmid = %s,\n" % (pmid)).expandtabs(deftab)
            if doi != "0":
                result = result + ("\tdoi = {%s},\n" % (doi)).expandtabs(deftab)
            result = result + ("\tkeywords = {}\n").expandtabs(deftab)
            result = result + "}"

            # Clean up things ...
            os.remove(tmpFileName)
        else:
            result = "Reference %s not found. Aborting" % str(pubmedUID)
            
        return(result)
