#!/usr/bin/env python3

class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

import sys, getopt

def main(argv) :

    # get arXiv ID from commandline
    ID = ""
    bibfile = ""
    key = ""
    force = False

    helpstring = "arXbib.py [-o <bibfile to patch>] [-k <new bibtex key>] [-f] <arXiv ID>"

    IDs=[]
    while len(argv)>0:
        try :
            opts, argv = getopt.getopt(argv,"o:k:fs",["open=","key=","force","safe"])
        except getopt.GetoptError :
            print(helpstring)
            exit(1)

        if len(argv)+len(IDs)==0 :
            print(helpstring)
            exit(2)
        if len(argv)>0:
            IDs.append(argv[0])
        argv=argv[1:]

        # later opts override earlier (for now)
        # force can be undone with -s = save
        for opt,arg in opts :
            if   opt=='-o' or opt=="--open" : bibfile = arg
            elif opt=='-k' or opt=="--key"  : key = arg
            elif opt=='-f' or opt=="--force": force = True
            elif opt=='-s' or opt=="--safe" : force = False

    ID=IDs[0]
    if len(IDs)>1:
        print("sorry, only one key at a time for now");
        exit(2)


    if ID=="" :
        print("No arXiv ID given");
        exit(2)

    # assemble INSPIRE url to search for this article
    url = "http://inspirehep.net/search?p=find+eprint+{}".format(ID)

    import urllib.request as urlrequest
    from bs4 import BeautifulSoup

    # get webpage and put it into the beautifulsoup parser
    web_page = urlrequest.urlopen(url).read()
    #print(web_page)
    soup = BeautifulSoup(web_page)

    # browse to the first search entry and extract links to bib files
    entries= soup.find("div",attrs={'class' : 'record_body'})
    l=entries.find("ul",attrs={'class' : 'tight_list'})
    links = l.findAll("a")
    biburl = [a['href'] for a in links if a.text=="BibTeX"]

    #print(biburl)

    # follow link to bib file
    bib_page= urlrequest.urlopen(biburl[0]).read()
    bibsoup = BeautifulSoup(bib_page)
    bibtex = bibsoup.find("pre")

    # check that the eprint ID is the same as the one you requested
    lines=bibtex.text.splitlines()
    for line in lines :
        if "eprint" in line and not ID in line :
            print(bcolors.FAIL+"Entry eprint ID differs from requested one!"+bcolors.ENDC)
            exit(3)

    # get (and possibly replace) article bibID
    keyline=[(i,line) for i,line in enumerate(lines) if "@article" in line][0]
    bibID = keyline[1][9:-1]

    if key!="" :
        lines[keyline[0]]=lines[keyline[0]].replace(bibID,key)
    else : key=bibID

    # print bibtex entry to the console
    for line in lines :
        print(line)


    # if bibfile is given, patch the bibfile
    if bibfile!="" :
        # check if entry is already present
        # http://stackoverflow.com/questions/82831/check-whether-a-file-exists-using-python
        import os.path
        if os.path.isfile(bibfile):
            biblio=open(bibfile,'r').read()
            if key in biblio :
                print(bcolors.FAIL+"bibtex key {} already in use! \nDid not patch bib file.".format(key) + bcolors.ENDC)
                exit(4) # exit after duplicate key has been found
            if ID in biblio :
                print(bcolors.WARNING+"An article with the same arXive ID is already in the bibliography"+bcolors.ENDC)
                if not force :
                    print(bcolors.WARNING+"Force entry with -f option."+bcolors.ENDC)
                    exit(5)
            accessmode = "a"
        else:
            accessmode = "w"

        with open(bibfile, accessmode) as f:
            for line in lines : f.write(line+"\n")

        print(bcolors.OKGREEN+"Added bibtex entry with key {}.".format(key) + bcolors.ENDC)

if __name__ == "__main__":
   main(sys.argv[1:])
