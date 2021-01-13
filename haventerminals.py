import streamlit as st
import pandas as pd
import untangle as ut

# == VOORBEREIDEND WERK

# inlezen en uitbreiden lijst terminals uit csv (dump uit mcc database, tabel mda_ter_terminal)
lijst_terminals = pd.read_csv('mda_ter_terminal.csv')

lijst_terminals['ter_desc'] = lijst_terminals['ter_name'] + ' | ' + lijst_terminals['ter_code']


def maak_locatiecode_van_terminalcode(terminalcode, terminalnaam):
    return '{} {} {} | {}'.format(terminalcode[0:4], terminalcode[4:6], terminalcode[6:9].lstrip('0'), terminalnaam)


lijst_terminals['ter_loc'] = lijst_terminals.apply(lambda row: maak_locatiecode_van_terminalcode(row['ter_code'], row['ter_name']), axis=1)

# lijst deepsea terminals maken
lijst_deepsea_terminals = lijst_terminals[lijst_terminals['ter_type'] == 1]

# lijst ferry terminals maken
lijst_ferry_terminals = lijst_terminals[lijst_terminals['ter_type'] == 2]

aangiftetype = None
code_controleresultaat = None
toegelaten_locatie = None
terminal = None
terminaltype = None
eindpunt_transit = None
voorafgaand_document_type = None
voorafgaand_document_referentie = None
containernummer_1 = None
containernummer_2 = None
containernummer_3 = None

# == SIDEBAR

# selectie voor aangifte regime
aangifteregime = st.sidebar.selectbox('Aangifteregime', ('Uitvoer NL', 'Invoer NL', 'Transit vertrek NL'), 2)

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

    containernummer_1 = st.sidebar.text_input('Containernummer 1')
    containernummer_2 = st.sidebar.text_input('Containernummer 2')
    containernummer_3 = st.sidebar.text_input('Containernummer 3')

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
            terminaltype = st.radio('Terminaltype', ('Deepsea', 'Ferry'))

        # terminal (invoer)
        elif soort_aangifte == 'Invoer':
            terminal = st.selectbox('Terminal', lijst_terminals['ter_desc'])

            if terminal in lijst_deepsea_terminals['ter_desc'].tolist():
                terminaltype = 'Deepsea terminal'
            elif terminal in lijst_ferry_terminals['ter_desc'].tolist():
                terminaltype = 'Ferry terminal'

    # opvolgende vervoerswijze
    if soort_aangifte == 'Invoer':
        opvolgende_vervoerswijze = st.selectbox('Opvolgende vervoerswijze', ('1 - Zeevoer', '2 - Spoorvervoer', '3- Wegvervoer', '8 - Binnenvaart', '9 - Onbekend'))

    # boekingsreferentie
    if soort_aangifte == 'Uitvoer':
        boekingsreferentie = st.text_input('Boekingsreferentie Portbase')

    # containernummers
    if soort_aangifte == 'Invoer' and terminaltype == 'Deepsea terminal':

        equipment_ids = None
        containernummers = (containernummer_1, containernummer_2, containernummer_3)
        for containernummer in containernummers:
            if containernummer != '':
                if equipment_ids is None:
                    equipment_ids = containernummer
                else:
                    equipment_ids += ', ' + containernummer

        if equipment_ids is not None:
            st.text('Containernummers:  {}'.format(equipment_ids))

        else:
            equipment_id_1 = st.text_input('Containernummer 1', key='equipment_id_1')
            equipment_id_2 = st.text_input('Containernummer 2', key='equipment_id_2')
            equipment_id_3 = st.text_input('Containernummer 3', key='equipment_id_3')

    # boekingsreferentie ferry
    elif soort_aangifte == 'Invoer' and terminaltype == 'Ferry terminal':
        boekingsreferentie = st.text_input('Boekingsreferentie ferry')

    # documenttype
    documenttype = st.empty()
    if soort_aangifte == 'Invoer' and code_controleresultaat == 'A3':
        documenttype.text('Documenttype:  MRN')
    elif soort_aangifte == 'Invoer' and code_controleresultaat == '':
        documenttype.text('Documenttype:  NT1')
    elif soort_aangifte == 'Uitvoer' and aangiftetype.startswith('T2'):
        if eindpunt_transit == 'Terminal in NL':
            documenttype.text('Documenttype:  RT2')
        elif eindpunt_transit == 'Elders':
            documenttype.text('Documenttype:  TT2')
    elif soort_aangifte == 'Uitvoer' and aangiftetype in ('T1', 'T-'):
        if eindpunt_transit == 'Terminal in NL':
            documenttype.text('Documenttype:  RT1')
        elif eindpunt_transit == 'Elders':
            documenttype.text('Documenttype:  TT1')

    # terminal
    if soort_aangifte == 'Invoer':
        st.text('Terminal:  {}'.format(terminal))

    # terminaltype
    if toegelaten_locatie not in lijst_terminals['ter_loc'].tolist():
        if terminal in lijst_deepsea_terminals['ter_desc'].tolist():
            terminaltype = 'Deepsea terminal'
        elif terminal in lijst_ferry_terminals['ter_desc'].tolist():
            terminaltype = 'Ferry terminal'

    st.text('Terminaltype:  {}'.format(terminaltype))

elif aangifteregime == 'Transit vertrek NL' and aangiftetype == 'TIR':
    st.subheader('Voormelden douanedocumenten niet mogelijk voor aangiftetype {}!'.format(aangiftetype))
