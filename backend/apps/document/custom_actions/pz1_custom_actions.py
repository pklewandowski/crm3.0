from apps.document.models import Document, DocumentAttribute
from apps.document.view_base import DocumentException


class CustomActions:
    # document = None



    """
attribute_1_codes - dyrektor ryzyka
    
305	  Wysokość prowizji dz. II	             1_5820c757fdd74d3a8def353ebddf68b5
307	  Wysokość prowizji dz. IV	             1_58bf55f6da8049639ea73b68fd6ae652
304	  Max przyznana kwota pożyczki dz. II    1_b0618ba527264770b70cc35ea1053f23
324	  Uwagi	                                 1_1a7ec336d8664e86f842293406be76ee
323	  Wybrana forma zabezpieczenia	         1_c032458a6e4d4377870718a356044230
306	  Max. przyznana kwota pożyczki IV	     1_4fd23d32bf484093ae2bc6a2e7973a8d

attribute_2_codes - dyrektor_zarzadzający

321	Wybrana forma zabezpieczenia	         1_c032458a6e4d4377870718a356044230_1
322	Uwagi	                                 1_1a7ec336d8664e86f842293406be76ee_1
313	Max przyznana kwota pożyczki dz. II	     1_b0618ba527264770b70cc35ea1053f23_1
311	Max. przyznana kwota pożyczki dz. IV	 1_4fd23d32bf484093ae2bc6a2e7973a8d_1
314	Wysokość prowizji dz. II	             1_5820c757fdd74d3a8def353ebddf68b5_1
312	Wysokość prowizji dz. IV	             1_58bf55f6da8049639ea73b68fd6ae652_1


317	Max. przyznana kwota pożyczki dz. II	1_b0618ba527264770b70cc35ea1053f23_2
315	Max. przyznana kwota pożyczki dz. IV	1_4fd23d32bf484093ae2bc6a2e7973a8d_2
318	Wysokość prowizji dz. II	            1_5820c757fdd74d3a8def353ebddf68b5_2
316	Wysokość prowizji dz. IV	            1_58bf55f6da8049639ea73b68fd6ae652_2
319	Uwagi	                                1_1a7ec336d8664e86f842293406be76ee_2
320	Wybrana forma zabezpieczenia	        1_c032458a6e4d4377870718a356044230_2



rata mc II  1_a30112ce690a4f0090c9330b9696014c
rata mc IV  1_ca4367e02876472fa610d0363b93b089

okres splaty II  1_037d9e12c2b14088aaeda0df0026b4e2
okres splaty IV  1_98e626527fcc494998811cff1b0a0148

103	Przyznana kwota pożyczki	1_2d241cb0dd7d4482b1156015b064f691
142	Nominalna wartość raty	    1_be48f4f71c2f452c807b43ababe921bc
138	Nominalna ilość rat	        1_2811ed77edc743bba947c4b9682f3ee3
    
    """

    @staticmethod
    def fill_loan_decision_data(user, id):
        return
