# -*- encoding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from arxbib import arXbib

TESTID = "1507.03414"
DEFAULTKEY = "Aaij:2015tga"
PENTAQUARK = [
u'',
u'',
u'%%% contains utf-8, see: http://inspirehep.net/info/faq/general#utf8',
u'%%% add \\usepackage[utf8]{inputenc} to your latex preamble',
u'',
u'@article{Aaij:2015tga,',
u'      author         = "Aaij, Roel and others",',
u'      title          = "{Observation of J/ψp Resonances Consistent with',
u'                        Pentaquark States in Λ$_b^0$ → J/ψK$^-$p Decays}",',
u'      collaboration  = "LHCb",',
u'      journal        = "Phys. Rev. Lett.",',
u'      volume         = "115",',
u'      year           = "2015",',
u'      pages          = "072001",',
u'      doi            = "10.1103/PhysRevLett.115.072001",',
u'      eprint         = "1507.03414",',
u'      archivePrefix  = "arXiv",',
u'      primaryClass   = "hep-ex",',
u'      reportNumber   = "CERN-PH-EP-2015-153, LHCB-PAPER-2015-029",',
u'      SLACcitation   = "%%CITATION = ARXIV:1507.03414;%%"',
u'}',
]


class SingleEntryTest(unittest.TestCase):
    def test_pentaquark(self):
        arxbib = arXbib()
        lines = arxbib.process_single_entry(TESTID)
        self.assertEqual(lines,PENTAQUARK)
        self.assertEqual(DEFAULTKEY,arxbib.id_key_pairs[TESTID])

if __name__ == '__main__':
    unittest.main()
