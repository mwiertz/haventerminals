import streamlit as st
import pandas as pd
import untangle as ut

# ======================================================================================================================

# == VARIABELEN
foutmeldingen = None
aangiftesymbool = None
soort_aangifte = None
code_controleresultaat = None
locatie = None
terminal = None
terminaltype = None
eindpunt_transit = None
voorafgaand_document_type = None
voorafgaand_document_soort = None
voorafgaand_document_referentie = None
voorafgaand_document_categorie = None
boekingsreferentie = None
opvolgende_vervoerswijze = None
containernummer_1 = None
containernummer_2 = None
containernummer_3 = None
containers = None
identificatie_vervoersmiddel_1 = None
identificatie_vervoersmiddel_2 = None
identificatie_vervoersmiddel_3 = None
ter_doc = None
berichttype = None
containernummers = None
equipmentnummers = None
gevraagde_regeling = None
soort_entrepot = None
shortsea_ferry = None
vrachttype = None
aangiftetype = None
regelingstype = None
douaneprocedure = None
douanestatus = None
vervoerstype = None
douanekantoor_van_uitgang = None

# ======================================================================================================================

# == FUNCTIES
def foutmelding(melding):
    global foutmeldingen
    if foutmeldingen is not None:
        foutmeldingen += '\n\n{}'.format(melding)
    else:
        foutmeldingen = melding


def hulp(tekst):
    return st.sidebar.markdown('<span style="font-size:0.8em; color:#0066CC">{}</span>'.format(tekst), unsafe_allow_html=True)


def terminalcode_naar_locatiecode(terminalcode, terminalnaam, terminalland, tms_id):
    if terminalland == 'NL':
        return '{} {} {} | {}'.format(terminalcode[0:4], terminalcode[4:6], terminalcode[6:9].lstrip('0'), terminalnaam)
    elif terminalland == 'BE' and terminalcode.startswith('BE'):
        return '{} {} {} | {}'.format(terminalcode[0:5], terminalcode[5:10], terminalcode[10:15], terminalnaam)
    elif terminalland == 'BE' and not terminalcode.startswith('BE'):
        if tms_id == 3:
            return '{} | {}'.format(terminalcode, 'PSA')
        elif tms_id == 4:
            return '{} | {}'.format(terminalcode, 'DP World')
        else:
            return '{}'.format(terminalcode)


def ophalen_codelijst(codelijst_xml, codelijstnaam):
    codelijsten = ut.parse(codelijst_xml)

    codelijst = []
    for tbl in codelijsten.cls.cbk.tbl:
        if tbl.tnr == codelijstnaam:
            for elm in tbl.elm:
                codelijst.append('{} | {}'.format(elm.ecd.cdata, elm.oms.cdata))

    return codelijst


def ophalen_codelijst_invoer(codelijstnaam):
    return ophalen_codelijst('datafiles/onderdeel-codeboek, onderdeel aangiftebehandeling.xml', codelijstnaam)


def ophalen_codelijst_transit(codelijstnaam):
    return ophalen_codelijst('datafiles/onderdeel-codeboek sagitta, onderdeel transit.xml', codelijstnaam)


def type_omschrijving_codelijst_samenvoegen(codelijst):
    _codelijst = pd.read_csv(codelijst)
    _codelijst['type - omschrijving'] = _codelijst.apply(lambda row: '{} - {}'.format(row['type'], row['omschrijving']), axis=1)
    return _codelijst['type - omschrijving']


# ======================================================================================================================

# == VOORBEREIDEND WERK

# inlezen en uitbreiden lijst terminals uit csv (dump uit mcc database, tabel mda_ter_terminal)
lijst_terminals = pd.read_csv('datafiles/mda_ter_terminal.csv')

lijst_terminals['ter_loc'] = lijst_terminals.apply(lambda row: terminalcode_naar_locatiecode(row['ter_code'], row['ter_name'], row['ter_country'], row['ter_tms_id']), axis=1)

# lijst terminals NL maken
lijst_terminals_NL = lijst_terminals[lijst_terminals['ter_country'] == 'NL']
lijst_terminals_NL.set_index(['ter_id'], inplace=True)
lijst_terminals_NL.reset_index(level=['ter_id'], inplace=True)

# lijst deepsea terminals NL maken
lijst_deepsea_terminals_NL = lijst_terminals[(lijst_terminals['ter_country'] == 'NL') & (lijst_terminals['ter_type'] == 1)]

# lijst ferry terminals NL maken
lijst_ferry_terminals_NL = lijst_terminals[(lijst_terminals['ter_country'] == 'NL') & (lijst_terminals['ter_type'] == 2)]

# lijst terminals BE maken
lijst_terminals_BE = lijst_terminals[(lijst_terminals['ter_country'] == 'BE')]
lijst_terminals_BE.set_index(['ter_id'], inplace=True)
lijst_terminals_BE.reset_index(level=['ter_id'], inplace=True)

# lijst IMPDEC terminals BE maken
lijst_impdec_terminals_BE = lijst_terminals[(lijst_terminals['ter_country'] == 'BE') & (lijst_terminals['ter_tms_id'] == 5)]

# lijst EBADEC terminals BE maken
lijst_ebadec_terminals_BE = lijst_terminals[(lijst_terminals['ter_country'] == 'BE') & (lijst_terminals['ter_tms_id'] == 6)]

# lijst TUL terminals BE maken
lijst_tul_terminals_BE = lijst_terminals[(lijst_terminals['ter_country'] == 'BE') & ((lijst_terminals['ter_tms_id'] == 3) | (lijst_terminals['ter_tms_id'] == 4))]

# lijst met toegelaten locaties samenstellen
lijst_locaties_NL = lijst_terminals_NL['ter_loc'].tolist()
lijst_locaties_NL.append('9876 ZB 5 | Testlocatie BTO NCTS Vertrek')
lijst_locaties_NL.append('1234 AA 56 | Testlocatie BTO NCTS Aankomst')
lijst_locaties_NL.append('6089 NB 2 | De Bergjes Heibloem')

# ======================================================================================================================

# == SIDEBAR

# selectie voor aangifte regime
aangifteregime = st.sidebar.selectbox('Aangifteregime', ('Uitvoer NL', 'Invoer NL', 'Transit vertrek NL', 'Invoer BE', 'Transit vertrek BE'), 0)
st.sidebar.text('\n')
st.sidebar.text('\n')


# aangiftetype toevoegen
if aangifteregime == 'Uitvoer NL':

    # relevante selecties uit aangiftesymbolen toevoegen
    aangiftesymbool = st.sidebar.selectbox('Aangiftesymbool', ('CO', 'EU', 'EX'), 2)

if aangifteregime == 'Invoer NL':

    # lijst met regelingen samenstellen
    codelijst_A35_regelingen = ophalen_codelijst_invoer('A35')

    # lijst met soorten entrepots samenstellen
    codelijst_A30_soorten_entrepots = ophalen_codelijst_invoer('A30')

    # gevraagde regeling toevoegen (reg 71 is id 21, reg 40 is id 10)
    gevraagde_regeling = st.sidebar.selectbox('Gevraagde regeling', codelijst_A35_regelingen, 10)
    hulp('71 of [Iets anders]')

    # soort entrepot toevoegen
    if gevraagde_regeling == '71 | PLAATSING ONDER DOUANEENTREPOT + AND INRICHTING DOUANETOEZ':
        soort_entrepot = st.sidebar.selectbox('Soort entrepot', codelijst_A30_soorten_entrepots, 2)
        hulp('S of [iets anders]')

if aangifteregime == 'Transit vertrek NL' or aangifteregime == 'Transit vertrek BE':

    # relevante selecties uit aangiftetypes toevoegen
    aangiftetype = st.sidebar.selectbox('Aangiftetype', ('T-', 'T1', 'T2', 'T2F', 'T2SM', 'TIR'), 1)
    hulp('TIR of [iets anders]')

if aangifteregime == 'Transit vertrek NL':

    # code controleresultaat toevoegen voor keuze normale of vereenvoudigde procedure
    code_controleresultaat = st.sidebar.selectbox('Code controleresultaat', ('A3', ''))

    if code_controleresultaat == 'A3':
        locatie = st.sidebar.selectbox('Toegelaten locatie goederen', lijst_locaties_NL)

if aangifteregime == 'Invoer BE':

    # aangiftesymbool
    aangiftesymbool = st.sidebar.selectbox('Aangiftesymbool', ('CO', 'EU', 'IM'), 2)

    # aangiftetype
    aangiftetype = st.sidebar.selectbox('Aangiftetype', type_omschrijving_codelijst_samenvoegen('datafiles/aangiftetype_be.csv'), 0)
    hulp('X of Y of [iets anders]')

    # regelingstype
    regelingstype = st.sidebar.selectbox('Regelingstype', type_omschrijving_codelijst_samenvoegen('datafiles/regelingstype_be.csv'), 7)
    hulp('H, I of J of [iets anders]')


# voorafgaand document toevoegen
if aangifteregime == 'Transit vertrek NL':

    # lijst met voorafgaande documenten samenstellen
    codelijst_014_voorafgaand_doc = ophalen_codelijst_transit('014')

    voorafgaand_document_type = st.sidebar.selectbox('Voorafgaand document type', codelijst_014_voorafgaand_doc, 18)

if aangifteregime == 'Invoer NL':

    # lijst met types voorafgaande documenten samenstellen
    codelijst_A80_type_voorafgaand_doc = ophalen_codelijst_invoer('A80')

    # lijst met soorten voorafgaande documenten samenstellen
    codelijst_A28_soort_voorafgaand_doc = ophalen_codelijst_invoer('A28')

    # voorafgaand document sectie toevoegen (soort 705 is id 20)
    voorafgaand_document_type = st.sidebar.selectbox('Type voorafgaand document', codelijst_A80_type_voorafgaand_doc, 0)
    voorafgaand_document_soort = st.sidebar.selectbox('Soort voorafgaand document', codelijst_A28_soort_voorafgaand_doc, 20)

if aangifteregime == 'Invoer NL' or aangifteregime == 'Transit vertrek NL':
    voorafgaand_document_referentie = st.sidebar.text_input('Voorafgaand document referentie')
    hulp('Voorbeelden:<br/>YMLUN236197722 (deepsea)<br/>DFDS534548380001 (ferry)')

if aangifteregime == 'Invoer BE':

    # categorie
    voorafgaand_document_categorie = st.sidebar.selectbox('Voorafgaand document categorie', type_omschrijving_codelijst_samenvoegen('datafiles/categorie_voorafgaand_doc_be.csv'), 0)

    # type
    voorafgaand_document_type = st.sidebar.selectbox('Voorafgaand document type', type_omschrijving_codelijst_samenvoegen('datafiles/type_voorafgaand_doc_be.csv'), 12)

    # B/L of AWB
    voorafgaand_document_referentie = st.sidebar.text_input('B/L of AWB')
    hulp('Voorbeelden:<br/>DFDS534548380001 (ferry)')


# locaties toevoegen
if aangifteregime == 'Uitvoer NL' or aangifteregime == 'Invoer NL':
    locatie = st.sidebar.selectbox('Goederenlocatie', lijst_locaties_NL)

if aangifteregime == 'Transit vertrek BE':
    locatie = st.sidebar.selectbox('Vertrekterminal', lijst_terminals_BE['ter_loc'])


# containernummers toevoegen
if aangifteregime == 'Uitvoer NL' or aangifteregime == 'Invoer NL' or aangifteregime == 'Transit vertrek NL' or aangifteregime == 'Invoer BE' or aangifteregime == 'Transit vertrek BE':

    # containernummers toevoegen
    containernummer_1 = st.sidebar.text_input('Containernummer 1')
    containernummer_2 = st.sidebar.text_input('Containernummer 2')
    containernummer_3 = st.sidebar.text_input('Containernummer 3')
    hulp('Voorbeelden:<br/>MSCU517820-2<br/>SEKU440137-1<br/>TCLU275439-5')

# ======================================================================================================================

# == MAIN SCREEN
st.header('Douanedocument voormelden')
st.write('\n')

# foutmelding en stoppen als aangiftetype TIR is gekozen
if aangifteregime == 'Transit vertrek NL' or aangifteregime == 'Transit vertrek BE':
    if aangiftetype == 'TIR':
        foutmelding('Voormelden douanedocumenten niet mogelijk voor aangiftetype {}!'.format(aangiftetype))
        st.error(foutmeldingen)
        st.stop()

# soort aangifte
if aangifteregime == 'Transit vertrek NL' or aangifteregime == 'Transit vertrek BE':
    soort_aangifte = st.radio('Soort aangifte', ('Invoer', 'Uitvoer'))

# eindpunt transit
if aangifteregime == 'Transit vertrek NL':
    if soort_aangifte == 'Uitvoer':
        eindpunt_transit = st.radio('Eindpunt transit', ('Terminal in NL', 'Elders'))


# vervoerstype
if aangifteregime == 'Invoer BE':

    shortsea_ferry = st.checkbox('Shortsea- en ferryverkeer')
    if not shortsea_ferry:
        foutmelding('Voormelden douanedocumenten enkel mogelijk voor shortsea- en ferryverkeer!')
        st.error(foutmeldingen)
        st.stop()

if aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Invoer':
    vervoerstype = st.radio('Vervoerstype', ('Shortsea- en ferryverkeer', 'Deepsea via PSA of DP World'))


# terminal
if aangifteregime == 'Uitvoer NL' or aangifteregime == 'Invoer NL' or aangifteregime == 'Transit vertrek NL':

    if locatie in lijst_terminals['ter_loc'].tolist():

        if locatie in lijst_deepsea_terminals_NL['ter_loc'].tolist():
            terminaltype = 'Deepsea terminal'
        elif locatie in lijst_ferry_terminals_NL['ter_loc'].tolist():
            terminaltype = 'Ferry terminal'

        terminal = locatie

    else:

        # terminal type (uitvoer)
        if aangifteregime == 'Uitvoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Uitvoer'):
            terminaltype = st.radio('Terminaltype', ('Deepsea terminal', 'Ferry terminal'))

        # terminal (invoer)
        elif aangifteregime == 'Invoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer' and code_controleresultaat != 'A3'):
            terminal = st.selectbox('Terminal', lijst_terminals_NL['ter_loc'])

            if terminal in lijst_deepsea_terminals_NL['ter_loc'].tolist():
                terminaltype = 'Deepsea terminal'
            elif terminal in lijst_ferry_terminals_NL['ter_loc'].tolist():
                terminaltype = 'Ferry terminal'

        elif aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer' and code_controleresultaat == 'A3':
            foutmelding('Toegelaten locatie goederen ({}) is geen (ondersteunde) terminal!'.format(locatie[:10]))

if aangifteregime == 'Invoer BE' and shortsea_ferry:
    terminal = st.selectbox('Terminal', lijst_impdec_terminals_BE['ter_loc'].tolist())

if aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Invoer':

    if locatie.startswith('BE'):
        _locatie = locatie[:locatie.find('|')].replace(' ', '')
    else:
        _locatie = locatie[:locatie.find('(')]

    if vervoerstype == 'Shortsea- en ferryverkeer':
        if locatie in lijst_impdec_terminals_BE['ter_loc'].tolist():
            terminal = locatie
        else:
            foutmelding('Gekozen vertrekterminal ({}) ondersteunt geen C-Point IMPDEC melding!'.format(_locatie))

    if vervoerstype == 'Deepsea via PSA of DP World':
        if locatie in lijst_tul_terminals_BE['ter_loc'].tolist():

            if locatie.endswith('PSA'):
                terminaltype = 'PSA'
            elif locatie.endswith('DP World'):
                terminaltype = 'DP World'

            terminal = locatie

        else:
            foutmelding('Gekozen vertrekterminal ({}) is geen PSA of DP World en ondersteunt geen TUL!'.format(_locatie))

if aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Uitvoer':

    if locatie in lijst_ebadec_terminals_BE['ter_loc'].tolist():
        terminal = locatie
    else:
        terminal = st.selectbox('Terminal', lijst_ebadec_terminals_BE['ter_loc'].tolist())


# controle X-705
if aangifteregime == 'Invoer NL' and (voorafgaand_document_type[:1] != 'X' or voorafgaand_document_soort[:3] != '705'):
    foutmelding('Geen X-705 als type voorafgaand document!')
elif aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer' and voorafgaand_document_type[:5] != 'X-705':
    foutmelding('Geen X-705 als type voorafgaand document!')
elif aangifteregime == 'Invoer BE' and (voorafgaand_document_categorie[:1] != 'X' or voorafgaand_document_type[:3] != '705'):
    foutmelding('Geen X-705 als type voorafgaand document!')


# opvolgende vervoerswijze
if aangifteregime == 'Invoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer'):
    opvolgende_vervoerswijze = st.selectbox('Opvolgende vervoerswijze', ('1 - Zeevervoer', '2 - Spoorvervoer', '3 - Wegvervoer', '8 - Binnenvaart', '9 - Onbekend'), 2)

if aangifteregime == 'Transit vertrek BE' and (soort_aangifte == 'Uitvoer' or (soort_aangifte == 'Invoer' and vervoerstype == 'Deepsea via PSA of DP World')):
    opvolgende_vervoerswijze = st.selectbox('Opvolgende vervoerswijze', ('BG - Barge', 'RL - Rail', 'TR - Truck', 'VS - Vessel'), 2)


# boekingsreferentie Portbase
if aangifteregime == 'Uitvoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Uitvoer'):
    boekingsreferentie = st.text_input('Boekingsreferentie Portbase')

    if boekingsreferentie == '':
        foutmelding('Boekingsreferentie Portbase niet ingevuld!')


# containernummers
if terminaltype == 'Deepsea terminal' or aangifteregime == 'Invoer BE' or (aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Invoer') or (aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Uitvoer'):

    containers = None
    containernummers = (containernummer_1, containernummer_2, containernummer_3)
    for containernummer in containernummers:
        if containernummer != '':
            if containers is None:
                containers = containernummer
            else:
                containers += ', ' + containernummer

    if containers is not None:
        st.text('Containernummer(s):  {}'.format(containers))
    elif terminaltype is not None:
        if terminaltype == 'Deepsea terminal' or terminaltype.startswith('TUL'):
            foutmelding('Geen containernummers in aangifte!')


# vrachttype
if (aangifteregime == 'Invoer BE' and shortsea_ferry) or (aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Invoer' and vervoerstype == 'Shortsea- en ferryverkeer'):
    vrachttype = st.selectbox('Vrachttype', ('RORO - Roll-on/roll-off', 'FRRY - Ferry'))

if aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Uitvoer':

    if containers is not None:
        vrachttype = 'CONT'
        st.text('Vrachttype:  {}'.format(vrachttype))

    else:
        vrachttype = st.selectbox('Vrachttype', ('RORO - Roll-on/roll-off', 'FRRY - Ferry', 'CONT - Container'))
        if vrachttype[:4] == 'CONT' and containers is None:
            foutmelding('Geen containernummers in aangifte!')


# boekingsreferentie ferry MID
if (aangifteregime == 'Invoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer')) and terminaltype == 'Ferry terminal':
    if voorafgaand_document_referentie == '':
        foutmelding('Geen referentie voorafgaand document ingevuld!')
    else:
        boekingsreferentie = voorafgaand_document_referentie
        st.text('Boekingsreferentie ferry:  {}'.format(boekingsreferentie))


# boekingsreferentie ferry IMPDEC/EBADEC
if (aangifteregime == 'Invoer BE' and shortsea_ferry) and vrachttype[:4] == 'FRRY':
    if voorafgaand_document_referentie == '':
        foutmelding('Geen B/L of AWB ingevuld!')
    else:
        boekingsreferentie = voorafgaand_document_referentie
        st.text('Boekingsreferentie ferry:  {}'.format(boekingsreferentie))

elif (aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Invoer' and vervoerstype == 'Shortsea- en ferryverkeer') or (aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Uitvoer') and vrachttype[:4] == 'FRRY':
    boekingsreferentie = st.text_input('Boekingsreferentie ferry')

    if boekingsreferentie == '':
        foutmelding('Geen boekingsreferentie ferry ingevuld!')


# equipment ids ferry of FRRY/RORO
if (aangifteregime == 'Uitvoer NL' and terminaltype == 'Ferry terminal') or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Uitvoer' and terminaltype == 'Ferry terminal') or (aangifteregime == 'Invoer BE' and containers is None) or (aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Invoer' and vervoerstype == 'Shortsea- en ferryverkeer' and containers is None) or (aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Uitvoer' and (vrachttype[:4] == 'FRRY' or vrachttype[:4] == 'RORO')):
    identificatie_vervoersmiddel_1 = st.text_input('Identificatie vervoersmiddel 1')
    identificatie_vervoersmiddel_2 = st.text_input('Identificatie vervoersmiddel 2')
    identificatie_vervoersmiddel_3 = st.text_input('Identificatie vervoersmiddel 3')

    if identificatie_vervoersmiddel_1 == '' and identificatie_vervoersmiddel_2 == '' and identificatie_vervoersmiddel_3 == '':
        foutmelding('Geen identificatie vervoersmiddel(en) ingevuld!')


# douanekantoor van uitgang
if aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Uitvoer':
    douanekantoor_van_uitgang = st.selectbox('Douanekantoor van uitgang', type_omschrijving_codelijst_samenvoegen('datafiles/kantoren_van_uitgang_be.csv'))


# berichttype
if aangifteregime == 'Invoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer'):
    berichttype = 'Portbase MID'
elif aangifteregime == 'Uitvoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Uitvoer'):
    berichttype = 'Portbase MED'
elif aangifteregime == 'Invoer BE' or (aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Invoer' and vervoerstype == 'Shortsea- en ferryverkeer'):
    berichttype = 'C-Point IMPDEC'
elif aangifteregime == 'Invoer BE' or (aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Invoer' and vervoerstype == 'Deepsea via PSA of DP World'):
    berichttype = 'TUL'
elif aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Uitvoer':
    berichttype = 'C-Point EBADEC'


# berichttype
st.text('Berichttype:  {}'.format(berichttype))


# documenttype
documenttype = st.empty()
if aangifteregime == 'Uitvoer NL':
    documenttype.text('Documenttype: {}'.format(aangiftesymbool))
    ter_doc = 'ter_{}'.format(aangiftesymbool.lower())
elif aangifteregime == "Invoer NL":
    if gevraagde_regeling == '71 | PLAATSING ONDER DOUANEENTREPOT + AND INRICHTING DOUANETOEZ':
        if soort_entrepot == 'S | PUBLIEK DOUANE-ENTREPOT TYPE II':
            documenttype.text('Documenttype:  IM7')
            ter_doc = 'ter_im7'
        else:
            documenttype.text('Documenttype:  PIE')
            ter_doc = 'ter_pie'
    else:
        documenttype.text('Documenttype:  IM4')
        ter_doc = 'ter_im4'
elif aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer' and code_controleresultaat == 'A3':
    documenttype.text('Documenttype:  MRN')
    ter_doc = 'ter_mrn'
elif aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer' and code_controleresultaat == '':
    documenttype.text('Documenttype:  NT1')
    ter_doc = 'ter_nt1'
elif aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Uitvoer' and aangiftetype.startswith('T2'):
    if eindpunt_transit == 'Terminal in NL':
        documenttype.text('Documenttype:  RT2')
        ter_doc = 'ter_rt2'
    elif eindpunt_transit == 'Elders':
        documenttype.text('Documenttype:  TT2')
        ter_doc = 'ter_tt2'
elif aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Uitvoer' and aangiftetype in ('T1', 'T-'):
    if eindpunt_transit == 'Terminal in NL':
        documenttype.text('Documenttype:  RT1')
        ter_doc = 'ter_rt1'
    elif eindpunt_transit == 'Elders':
        documenttype.text('Documenttype:  TT1')
        ter_doc = 'ter_tt1'
elif aangifteregime == 'Invoer BE' or (aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Invoer' and vervoerstype == 'Shortsea- en ferryverkeer') or (aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Uitvoer'):
    documenttype.text('Documenttype:  MRN')
    ter_doc = 'MRN'


# terminal
if aangifteregime == 'Invoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer'):
    st.text('Terminal:  {}'.format(terminal))


# terminaltype
if locatie not in lijst_terminals['ter_loc'].tolist():
    if terminal in lijst_deepsea_terminals_NL['ter_loc'].tolist():
        terminaltype = 'Deepsea terminal'
    elif terminal in lijst_ferry_terminals_NL['ter_loc'].tolist():
        terminaltype = 'Ferry terminal'

if terminaltype is not None:
    st.text('Terminaltype:  {}'.format(terminaltype))


# ondersteunt terminal documenttype?
if aangifteregime == 'Uitvoer NL' or aangifteregime == 'Invoer NL' or aangifteregime == 'Transit vertrek NL':
    if terminal is not None and not lijst_terminals.loc[lijst_terminals['ter_loc'] == terminal, ter_doc].iloc[0]:
        foutmelding('Terminal {} ondersteunt documenttype {} niet!'.format(terminal[:11], ter_doc[-3:].upper()))


# douaneprocedure IMPDEC
if aangifteregime == 'Invoer BE':

    douaneprocedure = '{}{}{}'.format(aangiftesymbool, aangiftetype[:1], regelingstype[:1])

    # ondersteunt IMPDEC douaneprocedure?
    if aangiftetype[:1] not in ('A', 'B', 'C', 'D', 'E', 'F', 'Z'):
        foutmelding('Douaneprocedure {} niet ondersteund; aangiftetype {} niet ondersteund!'.format(douaneprocedure, aangiftetype[:1]))
    if regelingstype[:1] not in ('H', 'I', 'J'):
        foutmelding('Douaneprocedure {} niet ondersteund; regelingstype {} niet ondersteund!'.format(douaneprocedure, regelingstype[:1]))

    st.text('Douaneprocedure:  {}'.format(douaneprocedure))

if aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Invoer' and vervoerstype == 'Shortsea- en ferryverkeer':

    douaneprocedure = aangiftetype

    # ondersteunt IMPDEC douaneprocedure?
    if aangiftetype not in ('T-', 'T1', 'T2', 'T2L'):
        foutmelding('Douaneprocedure {} niet ondersteund; aangiftetype {} niet ondersteund!'.format(douaneprocedure, aangiftetype))

    st.text('Douaneprocedure:  {}'.format(douaneprocedure))

# douaneprocedure EBADEC
if aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Uitvoer':
    douaneprocedure = 'T'
    st.text('Douaneprocedure:  {}'.format(douaneprocedure))


# douanestatus
if aangifteregime == 'Invoer BE' or (aangifteregime == 'Transit vertrek BE' and soort_aangifte == 'Invoer' and vervoerstype == 'Shortsea- en ferryverkeer'):
    douanestatus = 'RELEASED'
    st.text('Douanestatus:  {}'.format(douanestatus))


# ======================================================================================================================

# == UITKOMST
st.text('\n')
st.text('\n')
st.text('\n')
if foutmeldingen is not None:
    st.error(foutmeldingen)
else:
    xml = None

    # MID xml
    if berichttype == 'Portbase MID':

        # first part of xml
        xml = '''
Portbase MID - M2400 xml (relevante elementen)\n
    <pcsDocument>
        <pcsDocumentHeader>
            ...
            <receiverIdentifier>{}</receiverIdentifier>
            ...
        </pcsDocumentHeader>
        <pcsDocumentContent>
            ...
            <contentBody>
                <importDocument>
                    <number>{}</number>
                    <type>{}</type>
                    <transportMode>{}</transportMode>'''.format(terminal[:7].replace(' ', '') + terminal[7:11].replace(' ', '').replace('|','').zfill(3), '[MRN AANGIFTE]', ter_doc[-3:].upper(), opvolgende_vervoerswijze[:1])

        # second part of xml deepsea
        if terminaltype == 'Deepsea terminal':
            xml += '''
                    <equipmentList>'''

            for containernummer in containernummers:
                if containernummer != '':
                    xml += '''
                        <equipment>
                            <id>{}</id>
                            <type>CN</type>
                        </equipment>'''.format(containernummer)

            xml += '''
                    </equipmentList>'''

        # second part of xml ferry
        if terminaltype == 'Ferry terminal':
            xml += '''
                    <shipmentId>{}</shipmentId>'''.format(boekingsreferentie)

        # third part of xml
        xml += '''
                </importDocument>
            </contentBody>
        </pcsDocumentContent>
    </pcsDocument>'''

    elif berichttype == 'Portbase MED':

        # first part of xml
        xml = '''
Portbase MED - M114 xml (relevante elementen)\n    
    <StandardBusinessDocument>
        ...
        <documentContent>
            ...
            <contentBody>
                <exportShipment>
                    <customsDocument>
                        <documentType>{}</documentType>
                        <documentNumber>{}</documentNumber>
                    </customsDocument>'''.format(ter_doc[-3:].upper(), '[MRN AANGIFTE]', )

        # second part of xml
        if terminaltype == 'Deepsea terminal':
            equipmentnummers = containernummers
        elif terminaltype == 'Ferry terminal':
            equipmentnummers = (identificatie_vervoersmiddel_1, identificatie_vervoersmiddel_2, identificatie_vervoersmiddel_3)

        for equipmentnummer in equipmentnummers:
            if equipmentnummer != '':
                xml += '''
                    <equipment>
                        <equipmentNumber>{}</equipmentNumber>
                        <bookingReferenceNumber>{}</bookingReferenceNumber>
                    </equipment>'''.format(equipmentnummer, boekingsreferentie)

        # third part of xml
        xml += '''
                </exportShipment>
           </contentBody>
        </documentContent>
    </StandardBusinessDocument>'''

    # IMPDEC xml
    elif berichttype == 'C-Point IMPDEC':

        # first part of xml
        xml = '''
C-Point IMPDEC xml (relevante elementen)\n
    <S:Envelope ...>
        ...
        <S:Body>
            ...
            <IMPDEC ...>
                ...
                <Body>
                    ...
                    <Document type="{}">
                        <Terminal>{}</Terminal>
                        <Number>[MRN AANGIFTE]</Number>
                        <CustomsProcedure>{}</CustomsProcedure>
                        <CustomsStatus>{}</CustomsStatus>
                    </Document>
                    <Cargos type="RORO">'''.format(ter_doc, terminal[:17].replace(' ', ''), douaneprocedure, douanestatus)

        # second part of xml
        if containers is not None:
            equipmentnummers = containernummers
        else:
            equipmentnummers = (identificatie_vervoersmiddel_1, identificatie_vervoersmiddel_2, identificatie_vervoersmiddel_3)

        for equipmentnummer in equipmentnummers:
            if equipmentnummer != '':
                xml += '''
                        <Cargo>{}</Cargo>'''.format(equipmentnummer)

        xml += '''
                    </Cargos>'''

        if vrachttype[:4] == 'FRRY':
            xml += '''
                    <Units type="{}">
                        <bookingsReference>{}</bookingsReference>
                    </Units>'''.format(vrachttype[:4], boekingsreferentie)

        # third part of xml
        xml += '''
                    <Attachment>
                        <AttachmentName>[MRN AANGIFTE].pdf</AttachmentName>
                        <ValidityDate>[VRIJGAVEDATUM AANGIFTE - YYYY-MM-DD]</ValidityDate>
                        <BinaryAttachmentData>[Base64 encoded PDF AANGIFTE]</BinaryAttachmentData>
                    </Attachment>
                </Body>
           </IMPDEC>
       </S:Body>
    </S:Envelope>'''

    # EBADEC xml
    elif berichttype == 'C-Point EBADEC':

        # first part of xml
        xml = '''
C-Point EBADEC xml (relevante elementen)\n
    <S:Envelope ...>
        ...
        <S:Body type="{}">
            <EBADEC ...>
                ...
                <Body>
                    ...'''.format(vrachttype[:4])

        # second part of xml
        if vrachttype[:4] == 'CONT':

            equipmentnummers = containernummers

            for equipmentnummer in equipmentnummers:
                if equipmentnummer != '':
                    xml += '''
                    <Container number="{}">
                        <Document type="{}" code="{}" office="{}">[MRN AANGIFTE]</Document>
                        <BookingsReference />
                        <Terminal>{}</Terminal>
                        <CarrierType>{}</CarrierType>
                    </Container>'''.format(equipmentnummer, ter_doc, douaneprocedure, douanekantoor_van_uitgang[:8], terminal[:17].replace(' ', ''), opvolgende_vervoerswijze[:2])

        elif vrachttype[:4] in ('RORO', 'FRRY'):

            equipmentnummers = (identificatie_vervoersmiddel_1, identificatie_vervoersmiddel_2, identificatie_vervoersmiddel_3)

            for equipmentnummer in equipmentnummers:
                if equipmentnummer != '':
                    xml += '''
                    <Vehicle number="{}">
                        <Document type="{}" code="{}" office="{}">[MRN AANGIFTE]</Document>'''.format(equipmentnummer, ter_doc, douaneprocedure, douanekantoor_van_uitgang[:8])

                    if vrachttype[:4] == 'RORO':
                        xml += '''
                        <BookingsReference />'''
                    elif vrachttype[:4] == 'FRRY':
                        xml += '''
                        <BookingsReference>{}</BookingsReference>'''.format(boekingsreferentie)

                    xml += '''
                        <Terminal>{}</Terminal>
                        <CarrierType>{}</CarrierType>
                    </Vehicle>'''.format(terminal[:17].replace(' ', ''), opvolgende_vervoerswijze[:2])

        # third part of xml
        xml += '''
                </Body>
            </EBADEC>
        </S:Body>
    </S:Envelope>'''

    # TUL xml
    elif berichttype == 'TUL':

        # first part of xml
        xml = '''
TUL xml (relevante elementen) - {}\n
    <CustomsEnvelope ...>
	    ...'''.format(terminaltype)

        # second part of xml
        for containernummer in containernummers:
            if containernummer != '':
                xml += '''
        <ContainerID>{}</ContainerID>'''.format(containernummer)

        # third part of xml
        xml += '''
        <ModeOfTransport>{}</ModeOfTransport>
        ...
        <DocumentInfo>
            <MRN>[MRN AANGIFTE]</MRN>
            <DocumentType>AccompanyingLetter</DocumentType>
            <ValidityDate>[VRIJGAVEDATUM AANGIFTE - YYYY-MM-DD]</ValidityDate>
            <AttachmentName>[MRN AANGIFTE].pdf</AttachmentName>
            <BinaryAttachmentData>[Base64 encoded PDF AANGIFTE]</BinaryAttachmentData>
        </DocumentInfo>
    </CustomsEnvelope>'''.format(opvolgende_vervoerswijze[:2])

    st.success(xml)
