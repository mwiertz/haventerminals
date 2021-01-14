# import untangle as ut
#
# codelijsten_transit = ut.parse('onderdeel-codeboek sagitta, onderdeel transit.xml')
#
# codelijst_transit_014_voorafgaand_doc = []
#
# for tbl in codelijsten_transit.cls.cbk.tbl:
#     if tbl.tnr == '014':
#         count = 0
#         for elm in tbl.elm:
#             codelijst_transit_014_voorafgaand_doc.append('{} -- {} | {}'.format(count, elm.ecd.cdata, elm.oms.cdata))
#             count += 1
#
# print(codelijst_transit_014_voorafgaand_doc)

foutmeldingen = None
def foutmelding(melding):
    global foutmeldingen
    if foutmeldingen != None:
        foutmeldingen += '\n{}'.format(melding)
    else:
        foutmeldingen = melding


print('---')
print(foutmeldingen)

foutmelding('aap')

print('---')
print(foutmeldingen)

foutmelding('monkey')

print('---')
print(foutmeldingen)