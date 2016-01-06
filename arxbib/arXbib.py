class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

HELPSTRING = """
    usage: arXbib.py [-o|--open <bibfile>] [-k|--key <key>] [-f|--force|-s|--safe] <arXiv ID> [<arXiv ID> ...]
       <bibfile>      : the bibfile to be patched, will be created if it doesn't exist
                        in case of multiple -o arguments, the last is taken
       <key>          : the citation key to be used for the arXivID
                        in case of multiple IDs, the most latest key before each ID will be used
                        if there is no other arXiv ID between that key and the current ID
                        if there are more than one -k arguments between two IDs, the last is taken
       -f --force     : force adding entry to file, even if it exists already
                        overrides previous occurances of -s or --safe
       -s --safe      : safe usage, do not create duplicated entries (default)
                        overrides previous occurances of -f or --force
       <arXiv ID>     : the arXiv ID(s) to be looked up
                        in case of a single ID, the order "-k <key> <ID>" is not enforced
    """


import sys
import getopt

class arXbib(object):
    def __init__(self):
        self.bibfile = ""
        self.id_key_pairs = {}
        self.force = False

    def parse(self,argv):
        while len(argv) > 0:
            key = ""
            ID = ""
            try:
                opts, argv = getopt.getopt(argv,
                                           "o:k:fs",
                                           ["open=", "key=", "force", "safe"])
            except getopt.GetoptError:
                print(HELPSTRING)
                exit(1)
    
            # only fails if ending with options without further ID
            if len(argv) > 0:
                ID = argv[0]
            argv = argv[1:]
    
            # later opts override earlier (for now)
            # force can be undone with -s = save
            for opt, arg in opts:
                if opt == '-o' or opt == "--open":
                    self.bibfile = arg
                elif opt == '-k' or opt == "--key":
                    self.key = arg
                elif opt == '-f' or opt == "--force":
                    self.force = True
                elif opt == '-s' or opt == "--safe":
                    self.force = False
            if ID != "":
                self.id_key_pairs[ID] = key
            elif key != "":
                # this should read
                # ```
                # print("last key didn't match any ID")
                # exit(2)
                # ```
                # but I'm now doing very nasty "exception" handeling
                if len(self.id_key_pairs) == 1:
                    only_entry = self.id_key_pairs.popitem()
                    if only_entry[1] == "":
                        # for the only ID, the key-id order was reversed.
                        # permitting this.
                        print("You provided first the ID, then the key. This is okay for *one* ID")
                        self.id_key_pairs[only_entry[0]] = key
                    else:
                        print("cannot assign the last key!")
                        exit(2)

    def process_single_entry(self,ID,key=""):
        '''Downloading a single entry, returns lines containing the bibtex
        MANIPULATES id_key_pairs!!!
    
        Keyword arguments:
        ID   -- the arXiv ID as string
        key  -- the citation key
        '''
        if ID == "":
            print("pseyfert made a coding error")
            exit(6)

        # assemble INSPIRE url to search for this article
        url = "http://inspirehep.net/search?p=find+eprint+{}".format(ID)

        # import urllib.request as urlrequest
        # http://python-future.org/compatible_idioms.html#urllib-module
        # http://github.com/pseyfert/LFVdiagrams
        if sys.version < '3':
            import urllib as urlrequest
        else:
            import urllib.request as urlrequest
        from bs4 import BeautifulSoup

        # get webpage and put it into the beautifulsoup parser
        web_page = urlrequest.urlopen(url).read()
        # print(web_page)
        soup = BeautifulSoup(web_page, "html.parser")

        # browse to the first search entry and extract links to bib files
        entries = soup.find("div", attrs={'class': 'record_body'})
        l = entries.find("ul", attrs={'class': 'tight_list'})
        links = l.findAll("a")
        biburl = [a['href'] for a in links if a.text == "BibTeX"]

        # print(biburl)

        # follow link to bib file
        bib_page = urlrequest.urlopen(biburl[0]).read()
        bibsoup = BeautifulSoup(bib_page)
        bibtex = bibsoup.find("pre")

        # check that the eprint ID is the same as the one you requested
        lines = bibtex.text.splitlines()
        for line in lines:
            if "eprint" in line and ID not in line:
                print(bcolors.FAIL+"Entry eprint ID differs from requested one!"+bcolors.ENDC)
                exit(3)

        # get (and possibly replace) article bibID
        keyline = [(i, line) for i, line in enumerate(lines) if "@article" in line][0]
        bibID = keyline[1][9:-1]

        if key != "":
            lines[keyline[0]] = lines[keyline[0]].replace(bibID, key)
        else:
            self.id_key_pairs[ID] = bibID
        
        return lines

    def write_to_file(self,lines,ID,key):
        '''Write BibTeX to bibfile
        needs self.bibfile and self.force to be set
    
        Keyword arguments:
        lines-- the actual bibtex code
        ID   -- the arXiv ID as string
        key  -- the citation key
        '''
        # check if entry is already present
        # http://stackoverflow.com/questions/82831/check-whether-a-file-exists-using-python
        import os.path
        if os.path.isfile(self.bibfile):
            # http://stackoverflow.com/questions/491921/unicode-utf8-reading-and-writing-to-files-in-python#844443
            if sys.version < '3':
                import codecs
                biblio = codecs.open(self.bibfile, 'r', 'utf-8').read()
            else:
                biblio = open(self.bibfile, 'r').read()
            if key in biblio:
                print(bcolors.FAIL+"bibtex key {} already in use! \nDid not patch bib file.".format(key) + bcolors.ENDC)
                exit(4)  # exit after duplicate key has been found
            if ID in biblio:
                print(bcolors.WARNING+"An article with the same arXive ID is already in the bibliography"+bcolors.ENDC)
                if not self.force:
                    print(bcolors.WARNING+"Force entry with -f option."+bcolors.ENDC)
                    exit(5)
            accessmode = "a"
        else:
            accessmode = "w"
    
        if sys.version < '3':
            # http://stackoverflow.com/questions/4970378/write-in-a-file-with-python-3-unicode
            # http://stackoverflow.com/questions/5483423/how-to-write-unicode-strings-into-a-file
            with open(self.bibfile, accessmode) as f:
                for line in lines:
                    f.write((line+"\n").encode("UTF-8"))
        else:
            with open(self.bibfile, accessmode, encoding='utf-8') as f:
                for line in lines:
                    f.write((line+"\n"))
    
        print(bcolors.OKGREEN+"Added bibtex entry with key {}.".format(key) + bcolors.ENDC)

    def main(self,argv):
        '''Main function
    
        Keyword arguments:
        argv -- the command line arguments, except the executable itself
                i.e. sys.argv[1:]
        '''

    
        self.parse(argv)
    
        if len(self.id_key_pairs) == 0:
            print(HELPSTRING)
            exit(2)
    
        for ID in self.id_key_pairs:
            # FIXME this is evilevilevil
            key = self.id_key_pairs[ID]
            lines = self.process_single_entry(ID,key)
            key = self.id_key_pairs[ID]
    
            # print bibtex entry to the console
            for line in lines:
                print(line)
    
            # if bibfile is given, patch the bibfile
            if self.bibfile != "":
                self.write_to_file(lines,ID,key)

