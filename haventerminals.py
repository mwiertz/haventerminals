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

# ======================================================================================================================

# == FUNCTIES
def foutmelding(melding):
    global foutmeldingen
    if foutmeldingen is not None:
        foutmeldingen += '\n\n{}'.format(melding)
    else:
        foutmeldingen = melding


def hulp(tekst):
    return st.sidebar.markdown('<span style="font-size:0.8em; color:#FF5733">{}</span>'.format(tekst), unsafe_allow_html=True)


def terminalcode_naar_locatiecode(terminalcode, terminalnaam):
    return '{} {} {} | {}'.format(terminalcode[0:4], terminalcode[4:6], terminalcode[6:9].lstrip('0'), terminalnaam)


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

lijst_terminals['ter_loc'] = lijst_terminals.apply(lambda row: terminalcode_naar_locatiecode(row['ter_code'], row['ter_name']), axis=1)

# lijst terminals NL maken
lijst_terminals_NL = lijst_terminals[lijst_terminals['ter_country'] == 'NL']
lijst_terminals_NL.set_index(['ter_id'], inplace=True)
lijst_terminals_NL.reset_index(level=['ter_id'], inplace=True)

# lijst deepsea terminals NL maken
lijst_deepsea_terminals_NL = lijst_terminals[(lijst_terminals['ter_country'] == 'NL') & (lijst_terminals['ter_type'] == 1)]

# lijst ferry terminals NL maken
lijst_ferry_terminals_NL = lijst_terminals[(lijst_terminals['ter_country'] == 'NL') & (lijst_terminals['ter_type'] == 2)]

# lijst IMPDEC terminals BE maken
lijst_impdec_terminals_BE = lijst_terminals[(lijst_terminals['ter_country'] == 'BE') & (lijst_terminals['ter_tms_id'] == 5)]

# lijst met toegelaten locaties samenstellen
lijst_locaties_NL = lijst_terminals_NL['ter_loc'].tolist()
lijst_locaties_NL.append('9876 ZB 5 | Testlocatie BTO NCTS Vertrek')
lijst_locaties_NL.append('1234 AA 56 | Testlocatie BTO NCTS Aankomst')
lijst_locaties_NL.append('6089 NB 2 | De Bergjes Heibloem')

# ======================================================================================================================

# == SIDEBAR

# selectie voor aangifte regime
aangifteregime = st.sidebar.selectbox('Aangifteregime', ('Uitvoer NL', 'Invoer NL', 'Transit vertrek NL', 'Invoer BE'), 3)
st.sidebar.text('\n')
st.sidebar.text('\n')


# aangiftetype toevoegen
if aangifteregime == 'Uitvoer NL':

    # relevante selecties uit aangiftesymbolen toevoegen
    aangiftesymbool = st.sidebar.selectbox('Aangiftesymbool', ('CO', 'EU', 'EX'), 2)

# Invoer NL
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

if aangifteregime == 'Transit vertrek NL':

    # relevante selecties uit aangiftetypes toevoegen
    aangiftesymbool = st.sidebar.selectbox('Aangiftetype', ('T-', 'T1', 'T2', 'T2F', 'T2SM', 'TIR'), 1)

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


# containernummers toevoegen
if aangifteregime == 'Uitvoer NL' or aangifteregime == 'Invoer NL' or aangifteregime == 'Transit vertrek NL' or aangifteregime == 'Invoer BE':

    # containernummers toevoegen
    containernummer_1 = st.sidebar.text_input('Containernummer 1')
    containernummer_2 = st.sidebar.text_input('Containernummer 2')
    containernummer_3 = st.sidebar.text_input('Containernummer 3')
    hulp('Voorbeelden:<br/>MSCU517820-2<br/>SEKU440137-1<br/>TCLU275439-5')

# ======================================================================================================================

# == MAIN SCREEN
st.header('Douanedocument voormelden')
st.write('\n')

if aangifteregime == 'Transit vertrek NL':

    # foutmelding en stoppen als aangiftetype TIR is gekozen
    if aangiftesymbool == 'TIR':
        foutmelding('Voormelden douanedocumenten niet mogelijk voor aangiftetype {}!'.format(aangiftesymbool))
        st.error(foutmeldingen)
        st.stop()

    # soort aangifte
    soort_aangifte = st.radio('Soort aangifte', ('Invoer', 'Uitvoer'))

    # eindpunt transit
    if soort_aangifte == 'Uitvoer':
        eindpunt_transit = st.radio('Eindpunt transit', ('Terminal in NL', 'Elders'))

# ferry/shortsea of deepsea
if aangifteregime == 'Invoer BE':

    shortsea_ferry = st.checkbox('Shortsea- en ferryverkeer')
    if not shortsea_ferry:
        foutmelding('Voormelden douanedocumenten enkel mogelijk voor shortsea- en ferryverkeer!')
        st.error(foutmeldingen)
        st.stop()

# terminal
if aangifteregime == 'Uitvoer NL' or aangifteregime == 'Invoer NL' or (aangifteregime == 'Transit vertrek NL' and code_controleresultaat == 'A3'):

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
        elif aangifteregime == 'Invoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer'):
            terminal = st.selectbox('Terminal', lijst_terminals_NL['ter_loc'])

            if terminal in lijst_deepsea_terminals_NL['ter_loc'].tolist():
                terminaltype = 'Deepsea terminal'
            elif terminal in lijst_ferry_terminals_NL['ter_loc'].tolist():
                terminaltype = 'Ferry terminal'

if aangifteregime == 'Invoer BE' and shortsea_ferry:
    terminal = st.selectbox('Terminal', lijst_impdec_terminals_BE['ter_loc'].tolist())

# controle X-705
if aangifteregime == 'Invoer NL' and (voorafgaand_document_type[:1] != 'X' or voorafgaand_document_soort[:3] != '705'):
    foutmelding('Geen X-705 als type voorafgaand document!')
elif aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer' and voorafgaand_document_type[:5] != 'X-705':
    foutmelding('Geen X-705 als type voorafgaand document!')
elif aangifteregime == 'Invoer BE' and (voorafgaand_document_categorie[:1] != 'X' or voorafgaand_document_type[:3] != '705'):
    foutmelding('Geen X-705 als type voorafgaand document!')

# opvolgende vervoerswijze
if aangifteregime == 'Invoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer'):
    opvolgende_vervoerswijze = st.selectbox('Opvolgende vervoerswijze', ('1 - Zeevervoer', '2 - Spoorvervoer', '3- Wegvervoer', '8 - Binnenvaart', '9 - Onbekend'))

# boekingsreferentie Portbase
if aangifteregime == 'Uitvoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Uitvoer'):
    boekingsreferentie = st.text_input('Boekingsreferentie Portbase')

    if boekingsreferentie == '':
        foutmelding('Boekingsreferentie Portbase niet ingevuld!')

# containernummers
if terminaltype == 'Deepsea terminal' or aangifteregime == 'Invoer BE':

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
    elif terminaltype == 'Deepsea terminal':
        foutmelding('Geen containernummers in aangifte!')

# vrachttype
if aangifteregime == 'Invoer BE' and shortsea_ferry:
    vrachttype = st.selectbox('Vrachttype', ('RORO - Roll-on/roll-off', 'FRRY - Ferry'))

# boekingsreferentie ferry MID
if (aangifteregime == 'Invoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer')) and terminaltype == 'Ferry terminal':
    if voorafgaand_document_referentie == '':
        foutmelding('Geen referentie voorafgaand document ingevuld!')
    else:
        boekingsreferentie = voorafgaand_document_referentie
        st.text('Boekingsreferentie ferry:  {}'.format(boekingsreferentie))

# boekingsreferentie ferry IMPDEC
if aangifteregime == 'Invoer BE' and shortsea_ferry and vrachttype[:4] == 'FRRY':
    if voorafgaand_document_referentie == '':
        foutmelding('Geen B/L of AWB ingevuld!')
    else:
        boekingsreferentie = voorafgaand_document_referentie
        st.text('Boekingsreferentie ferry:  {}'.format(boekingsreferentie))

# equipment ids ferry of FRRY/RORO
if (aangifteregime == ('Uitvoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Uitvoer')) and terminaltype == 'Ferry terminal') or (aangifteregime == 'Invoer BE' and containers is None):
    identificatie_vervoersmiddel_1 = st.text_input('Identificatie vervoersmiddel 1')
    identificatie_vervoersmiddel_2 = st.text_input('Identificatie vervoersmiddel 2')
    identificatie_vervoersmiddel_3 = st.text_input('Identificatie vervoersmiddel 3')

    if identificatie_vervoersmiddel_1 == '' and identificatie_vervoersmiddel_2 == '' and identificatie_vervoersmiddel_3 == '':
        foutmelding('Geen identificatie vervoersmiddel(en) ingevuld!')

# berichttype
if aangifteregime == 'Invoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Invoer'):
    berichttype = 'Portbase MID'
elif aangifteregime == 'Uitvoer NL' or (aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Uitvoer'):
    berichttype = 'Portbase MED'
elif aangifteregime == 'Invoer BE':
    berichttype = 'C-Point IMPDEC'

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
elif aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Uitvoer' and aangiftesymbool.startswith('T2'):
    if eindpunt_transit == 'Terminal in NL':
        documenttype.text('Documenttype:  RT2')
        ter_doc = 'ter_rt2'
    elif eindpunt_transit == 'Elders':
        documenttype.text('Documenttype:  TT2')
        ter_doc = 'ter_tt2'
elif aangifteregime == 'Transit vertrek NL' and soort_aangifte == 'Uitvoer' and aangiftesymbool in ('T1', 'T-'):
    if eindpunt_transit == 'Terminal in NL':
        documenttype.text('Documenttype:  RT1')
        ter_doc = 'ter_rt1'
    elif eindpunt_transit == 'Elders':
        documenttype.text('Documenttype:  TT1')
        ter_doc = 'ter_tt1'
elif aangifteregime == 'Invoer BE':
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

# ondersteunt IMPDEC documenttype?
if aangifteregime == 'Invoer BE':

    # douaneprocedure (IMPDEC)
    douaneprocedure = '{}{}{}'.format(aangiftesymbool, aangiftetype[:1], regelingstype[:1])
    if aangiftetype[:1] not in ('A', 'B', 'C', 'D', 'E', 'F', 'Z'):
        foutmelding('Douaneprocedure {} niet ondersteund; aangiftetype {} niet ondersteund!'.format(douaneprocedure, aangiftetype[:1]))
    if regelingstype[:1] not in ('H', 'I', 'J'):
        foutmelding('Douaneprocedure {} niet ondersteund; regelingstype {} niet ondersteund!'.format(douaneprocedure, regelingstype[:1]))
    st.text('Douaneprocedure:  {}'.format(douaneprocedure))

    # douanestatus
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
                    <transportMode>{}</transportMode>'''.format(terminal[:11].replace(' ', ''), '[MRN AANGIFTE]', ter_doc[-3:].upper(), opvolgende_vervoerswijze[:1])

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
                    <Cargos type="RORO">'''.format(ter_doc, terminal[:11].replace(' ', ''), douaneprocedure, douanestatus)

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

    st.success(xml)
