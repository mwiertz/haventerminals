import streamlit as st
import pandas as pd
import untangle as ut

# == VARIABELEN
foutmeldingen = None
aangiftetype = None
code_controleresultaat = None
toegelaten_locatie = None
terminal = None
terminaltype = None
eindpunt_transit = None
voorafgaand_document_type = None
voorafgaand_document_referentie = None
boekingsreferentie = None
opvolgende_vervoerswijze = None
containernummer_1 = None
containernummer_2 = None
containernummer_3 = None
identificatie_vervoersmiddel_1 = None
identificatie_vervoersmiddel_2 = None
identificatie_vervoersmiddel_3 = None
ter_doc = None
berichttype = None
containernummers = None
equipmentnummers = None


# == FUNCTIES
def foutmelding(melding):
    global foutmeldingen
    if foutmeldingen is not None:
        foutmeldingen += '\n\n{}'.format(melding)
    else:
        foutmeldingen = melding


def maak_locatiecode_van_terminalcode(terminalcode, terminalnaam):
    return '{} {} {} | {}'.format(terminalcode[0:4], terminalcode[4:6], terminalcode[6:9].lstrip('0'), terminalnaam)


# == VOORBEREIDEND WERK

# inlezen en uitbreiden lijst terminals uit csv (dump uit mcc database, tabel mda_ter_terminal)
lijst_terminals = pd.read_csv('mda_ter_terminal.csv')

lijst_terminals['ter_loc'] = lijst_terminals.apply(lambda row: maak_locatiecode_van_terminalcode(row['ter_code'], row['ter_name']), axis=1)

# lijst deepsea terminals maken
lijst_deepsea_terminals = lijst_terminals[lijst_terminals['ter_type'] == 1]

# lijst ferry terminals maken
lijst_ferry_terminals = lijst_terminals[lijst_terminals['ter_type'] == 2]


# == SIDEBAR

# selectie voor aangifte regime
aangifteregime = st.sidebar.selectbox('Aangifteregime', ('Uitvoer NL', 'Invoer NL', 'Transit vertrek NL'), 2)


# === indien Uitvoer NL gekozen
if aangifteregime == 'Uitvoer NL':

    # lijst met toegelaten locaties samenstellen
    lijst_toegelaten_locaties = lijst_terminals['ter_loc'].tolist()
    lijst_toegelaten_locaties.append('9876 ZB 5 | Testlocatie BTO NCTS Vertrek')
    lijst_toegelaten_locaties.append('1234 AA 56 | Testlocatie BTO NCTS Aankomst')
    lijst_toegelaten_locaties.append('6089 NB 2 | De Bergjes Heibloem')

    # relevante selecties uit aangiften toevoegen
    aangiftetype = st.sidebar.selectbox('Aangiftetype', ('CO', 'EU', 'EX'), 2)

    containernummer_1 = st.sidebar.text_input('Containernummer 1')
    containernummer_2 = st.sidebar.text_input('Containernummer 2')
    containernummer_3 = st.sidebar.text_input('Containernummer 3')
    st.sidebar.markdown('<span style="font-size:0.8em">Voorbeelden:<br/>MSCU517820-2<br/>SEKU440137-1<br/>TCLU275439-5</span>', unsafe_allow_html=True)


# === indien Transit vertrek NL gekozen
if aangifteregime == 'Transit vertrek NL':

    # lijst met toegelaten locaties samenstellen
    lijst_toegelaten_locaties = lijst_terminals['ter_loc'].tolist()
    lijst_toegelaten_locaties.append('9876 ZB 5 | Testlocatie BTO NCTS Vertrek')
    lijst_toegelaten_locaties.append('1234 AA 56 | Testlocatie BTO NCTS Aankomst')
    lijst_toegelaten_locaties.append('6089 NB 2 | De Bergjes Heibloem')

    # lijst met voorafgaande documenten samenstellen
    codelijsten_transit = ut.parse('onderdeel-codeboek sagitta, onderdeel transit.xml')

    codelijst_transit_014_voorafgaand_doc = []
    for tbl in codelijsten_transit.cls.cbk.tbl:
        if tbl.tnr == '014':
            for elm in tbl.elm:
                codelijst_transit_014_voorafgaand_doc.append('{} | {}'.format(elm.ecd.cdata, elm.oms.cdata))

    # relevante selecties uit aangiften toevoegen
    aangiftetype = st.sidebar.selectbox('Aangiftetype', ('T-', 'T1', 'T2', 'T2F', 'T2SM', 'TIR'), 1)

    code_controleresultaat = st.sidebar.selectbox('Code controleresultaat', ('A3', ''))

    if code_controleresultaat == 'A3':
        toegelaten_locatie = st.sidebar.selectbox('Toegelaten locatie goederen', lijst_toegelaten_locaties)

    voorafgaand_document_type = st.sidebar.selectbox('Voorafgaand document type', codelijst_transit_014_voorafgaand_doc, 18)
    voorafgaand_document_referentie = st.sidebar.text_input('Voorafgaand document referentie')
    st.sidebar.markdown('<span style="font-size:0.8em">Voorbeelden:<br/>YMLUN236197722 (deepsea)<br/>DFDS534548380001 (ferry)</span>', unsafe_allow_html=True)

    containernummer_1 = st.sidebar.text_input('Containernummer 1')
    containernummer_2 = st.sidebar.text_input('Containernummer 2')
    containernummer_3 = st.sidebar.text_input('Containernummer 3')
    st.sidebar.markdown('<span style="font-size:0.8em">Voorbeelden:<br/>MSCU517820-2<br/>SEKU440137-1<br/>TCLU275439-5</span>', unsafe_allow_html=True)


# == MAIN SCREEN
st.header('Douanedocument voormelden')

if aangifteregime == 'Transit vertrek NL' and aangiftetype != 'TIR':

    # soort aangifte
    soort_aangifte = st.radio('Soort aangifte', ('Invoer', 'Uitvoer'))

    # eindpunt transit
    if soort_aangifte == 'Uitvoer':
        eindpunt_transit = st.radio('Eindpunt transit', ('Terminal in NL', 'Elders'))

    # terminal
    if code_controleresultaat == 'A3' and toegelaten_locatie in lijst_terminals['ter_loc'].tolist():

        if toegelaten_locatie in lijst_deepsea_terminals['ter_loc'].tolist():
            terminaltype = 'Deepsea terminal'
        elif toegelaten_locatie in lijst_ferry_terminals['ter_loc'].tolist():
            terminaltype = 'Ferry terminal'

        terminal = toegelaten_locatie

    else:

        # terminal type (uitvoer)
        if soort_aangifte == 'Uitvoer':
            terminaltype = st.radio('Terminaltype', ('Deepsea terminal', 'Ferry terminal'))

        # terminal (invoer)
        elif soort_aangifte == 'Invoer':
            terminal = st.selectbox('Terminal', lijst_terminals['ter_loc'])

            if terminal in lijst_deepsea_terminals['ter_loc'].tolist():
                terminaltype = 'Deepsea terminal'
            elif terminal in lijst_ferry_terminals['ter_loc'].tolist():
                terminaltype = 'Ferry terminal'

    # controle X-705
    if soort_aangifte == 'Invoer' and voorafgaand_document_type != 'X-705 | COGNOSSEMENT (BILL OF LADING)':
        foutmelding('Geen X-705 als type voorafgaand document!')

    # opvolgende vervoerswijze
    if soort_aangifte == 'Invoer':
        opvolgende_vervoerswijze = st.selectbox('Opvolgende vervoerswijze', ('1 - Zeevoer', '2 - Spoorvervoer', '3- Wegvervoer', '8 - Binnenvaart', '9 - Onbekend'))

    # boekingsreferentie Portbase
    if soort_aangifte == 'Uitvoer':
        boekingsreferentie = st.text_input('Boekingsreferentie Portbase')

        if boekingsreferentie == '':
            foutmelding('Boekingsreferentie Portbase niet ingevuld!')

    # containernummers
    if terminaltype == 'Deepsea terminal':

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

        else:
            foutmelding('Geen containernummers in aangifte!')

    # boekingsreferentie ferry
    if soort_aangifte == 'Invoer' and terminaltype == 'Ferry terminal':
        if voorafgaand_document_referentie == '':
            foutmelding('Geen referentie voorafgaand document ingevuld!')
        else:
            boekingsreferentie = voorafgaand_document_referentie
            st.text('Boekingsreferentie ferry:  {}'.format(boekingsreferentie))

    # equipment ids ferry
    if soort_aangifte == 'Uitvoer' and terminaltype == 'Ferry terminal':
        identificatie_vervoersmiddel_1 = st.text_input('Identificatie vervoersmiddel 1')
        identificatie_vervoersmiddel_2 = st.text_input('Identificatie vervoersmiddel 2')
        identificatie_vervoersmiddel_3 = st.text_input('Identificatie vervoersmiddel 3')

        if identificatie_vervoersmiddel_1 == '' and identificatie_vervoersmiddel_2 == '' and identificatie_vervoersmiddel_3 == '':
            foutmelding('Geen identificatie vervoersmiddel(en) ingevuld!')

    # berichttype
    if soort_aangifte == 'Invoer':
        berichttype = 'Portbase MID'
    elif soort_aangifte == 'Uitvoer':
        berichttype = 'Portbase MED'

    st.text('Berichttype:  {}'.format(berichttype))

    # documenttype
    documenttype = st.empty()
    if soort_aangifte == 'Invoer' and code_controleresultaat == 'A3':
        documenttype.text('Documenttype:  MRN')
        ter_doc = 'ter_mrn'
    elif soort_aangifte == 'Invoer' and code_controleresultaat == '':
        documenttype.text('Documenttype:  NT1')
        ter_doc = 'ter_nt1'
    elif soort_aangifte == 'Uitvoer' and aangiftetype.startswith('T2'):
        if eindpunt_transit == 'Terminal in NL':
            documenttype.text('Documenttype:  RT2')
            ter_doc = 'ter_rt2'
        elif eindpunt_transit == 'Elders':
            documenttype.text('Documenttype:  TT2')
            ter_doc = 'ter_tt2'
    elif soort_aangifte == 'Uitvoer' and aangiftetype in ('T1', 'T-'):
        if eindpunt_transit == 'Terminal in NL':
            documenttype.text('Documenttype:  RT1')
            ter_doc = 'ter_rt1'
        elif eindpunt_transit == 'Elders':
            documenttype.text('Documenttype:  TT1')
            ter_doc = 'ter_tt1'

    # terminal
    if soort_aangifte == 'Invoer':
        st.text('Terminal:  {}'.format(terminal))

    # terminaltype
    if toegelaten_locatie not in lijst_terminals['ter_loc'].tolist():
        if terminal in lijst_deepsea_terminals['ter_loc'].tolist():
            terminaltype = 'Deepsea terminal'
        elif terminal in lijst_ferry_terminals['ter_loc'].tolist():
            terminaltype = 'Ferry terminal'

    st.text('Terminaltype:  {}'.format(terminaltype))

    # ondersteunt terminal documenttype
    if soort_aangifte == 'Invoer' and not lijst_terminals.loc[lijst_terminals['ter_loc'] == terminal, ter_doc].iloc[0]:
        foutmelding('Terminal {} ondersteunt documenttype {} niet!'.format(terminal[:11], ter_doc[-3:].upper()))

elif aangifteregime == 'Transit vertrek NL' and aangiftetype == 'TIR':
    foutmelding('Voormelden douanedocumenten niet mogelijk voor aangiftetype {}!'.format(aangiftetype))


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
Portbase MID - M2400 xml (relevant parts)\n
    <pcsDocument>
        <pcsDocumentHeader>
            <receiverIdentifier>{}</receiverIdentifier>
        </pcsDocumentHeader>
        <pcsDocumentContent>
            <contentBody>
                <importDocument>
                    <number>{}</number>
                    <type>{}</type>
                    <transportMode>{}</transportMode>'''.format(terminal[:11], '[MRN AANGIFTE]', ter_doc[-3:].upper(), opvolgende_vervoerswijze[:1])

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

    if berichttype == 'Portbase MED':

        # first part of xml
        xml = '''
Portbase MED - M114 xml (relevant parts)\n    
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

    st.success(xml)
