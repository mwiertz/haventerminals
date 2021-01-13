import streamlit as st
import pandas as pd

# inlezen en uitbreiden lijst terminals uit csv (dump uit mcc database, tabel mda_ter_terminal)
lijst_terminals = pd.read_csv('mda_ter_terminal.csv')
lijst_terminals['ter_desc'] = lijst_terminals['ter_name'] + ' | ' + lijst_terminals['ter_code']

gekozen_terminal = st.selectbox('Kies terminal', lijst_terminals['ter_desc'])

'gekozen:',  gekozen_terminal

#lijst_terminals

