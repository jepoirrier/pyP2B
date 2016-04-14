# pyP2B, an automated Pubmed reference to BibTeX script

## Introduction

In biology, we often need to use [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?db=PubMed), a biomedical articles search engine for citations from MEDLINE and other life science journals.

In the MS-Windows world, you have nice, proprietary tools (like Reference Manager or Endnote) that retrieves citations from PubMed, store them in a database and allow you to use them in proprietary word processing software (in fact, in MS-Word only since nor Wordperfect nor OpenOffice.org are supported). If you are using BibTeX (for LaTeX) as your citations repository, there isn’t a lot of tools. The best one, imho, is [JabRef](http://www.jabref.org/), a free reference manager written in Java (for me, the only "problem" is that it adds custom, non-BibTeX tags). Or you can edit the BibTeX file by yourself with any text editor. Closer to EndNote and Reference Manager, [Zotero](https://www.zotero.org/) could also do the job.

The problem with manual edition is that it is prone to error (even when copying/pasting from the web). Since Python programming is my hobby horse for the moment, there are two solutions to this problem:

* Use Biopython to [get a reference from PubMed](http://biopython.org/DIST/docs/tutorial/Tutorial.html#htoc32) but are you ready to have a huge module dependency just to use 1 function?
* Write your own Python script, using a PubMed URL to download your reference and a little bit of XML parsing to extract the relevant info (one can use the ESearch and EFetch tools but my lazy nature tells me to simply use the URL).

Obviously, I chose to write my own Python script. Each reference from this PubMed XML format example (full DTDs) should be like this:

```
@article{poirrier06,
  author = {Poirrier, J.E. and Poirrier, L. and Leprince, P. and
Maquet, P.},
  title = {Gemvid, an open source, modular, automated activity
recording system for rats using digital video},
  year = 2006,
  journal = {Journal of circadian rhythms},
  volume = 4,
  pages = {10},
  pmid = 16934136,
  doi = {10.1186/1740-3391-4-10}
}
```

**The aim of pyP2B is to simply retrieve a PubMed reference (via its PMID) and to display it in the BibTeX format.**

## Practically ...

You need Python. I use version 2.4. It will surely work on higher versions. I don't know about lower versions. It should work on any platform with Python ; I tested it under GNU/Linux and MS-Windows. In addition, you need to have the LXML python library (it may already be installed with your GNU/Linux flavor).

The archive containing scripts is in the src/ directory. It contains the command line version, the GUI version and the class. This software is released under the GNU General Public Licence (GPL).

## ... if you use the command line version

First, use PubMed to check the reference you want, then take its PubMed ID (PMID) and launch the program, giving your BibTeX file in a pipe, for example:

```
./pyP2B.py 16934136 >> myrefs.bib
```

(under MS-Windows: python.exe pyP2B.py 16934136 >> myrefs.bib provided the script is in the same directory as your python.exe

## ... if you use the GUI version

First, use PubMed to check the reference you want, then take its PubMed ID (PMID) and launch the program pyP2Bgui.py. In the top text box, give (paste) the PubMed ID you want and click on the "OK" button. The box below will then give you the reference you want and correctly formatted. You can select it, copy it (usually Ctrl + C) and paste it somewhere else.

## How does it work?

* With PubMed, I do not use the correct tool but a HTTP query. It is much more simple and easier. The script asks for the PMID citations. Since it gets a HTTP answer, I need to parse this answer to replace entities (like < , >, etc.) and obtain a valid XML file.
* Once I got the XML file and after some checking, I use XPaths from LXML (for me, XPaths are quick and dirty compared to write a DOM/SAX structure but it works!)
* Then the script simply prints the result to the standard output (even if it's an error ; improvement : print on the error output). You simply need to get this output into your BibTeX file with the correct pipe.

If you like, you can edit the class (pyP2Bclass.py) to change the tab size (here = 2).

Note: this script was originally posted in my blog on October 22nd, 2006. The UTF-8 error is no longer there: author names with non-ASCII characters will be correctly processed.

Note on October 1st, 2009: thanks to Pascal Pollet and Ben Goldstein who drew my attention of the format change, I updated everything (version 0.2) and it works again.

You can contact me at jepoirrier "at" gmail.com. Please report if you have any problem, comment or if you would like new features in this software.
