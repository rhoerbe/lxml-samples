import lxml.etree

print('1. Examples without namespace')

print('1.1 Parse file into ElementTree and find elements')
t11 = lxml.etree.parse('ed1_without_ns.xml')
t11.xpath('//X509Certificate')
t11.getroot()
t11.find('IDPSSODescriptor')
t11.find('Organization')
t11.find('OrganizationName')

print('1.2 Parse file into Element and find elements')
f = open('ed1_without_ns.xml', encoding='utf8')
xml_str=f.read()
e12 = lxml.etree.fromstring(xml_str.encode('utf-8'))
assert e12.tag == 'EntityDescriptor'
assert e12.attrib == {'entityID': 'https://idp.example.com/idp.xml'}
assert e12.xpath('//X509Certificate')[0].tag == 'X509Certificate'
e12.find('IDPSSODescriptor')
e12.find('Organization')
e12.find('OrganizationName')


print('2. Examples with namespace')

XMLNS_DSIG = 'http://www.w3.org/2000/09/xmldsig#'
XMLNS_DSIG_PREFIX = '{%s}' % XMLNS_DSIG
XMLNS_MD = 'urn:oasis:names:tc:SAML:2.0:metadata'
XMLNS_MD_PREFIX = '{%s}' % XMLNS_MD
XMLNS_PVZD = 'http://egov.gv.at/pvzd1.xsd'
XMLNS_PVZD_PREFIX = '{%s}' % XMLNS_PVZD

print('2.1 Parse file into ElementTree and find elements')
t21 = lxml.etree.parse('ed2_with_ns.xml')
assert t21.getroot().tag == '{urn:oasis:names:tc:SAML:2.0:metadata}EntityDescriptor'
assert t21.getroot().attrib['entityID'] == 'https://idp.example.com/idp.xml'

assert t21.xpath('/*')[0].tag == '{urn:oasis:names:tc:SAML:2.0:metadata}EntityDescriptor'
xp = 'md:IDPSSODescriptor//ds:X509Certificate'
assert t21.xpath(xp, namespaces={'ds': XMLNS_DSIG, 'md': XMLNS_MD})[0].tag == '{http://www.w3.org/2000/09/xmldsig#}X509Certificate'
assert t21.find('//'+XMLNS_MD_PREFIX+'GivenName').text == 'Testiani'

print('3 Examples with pvzd namespace')

print('3.1 Parse file into ElementTree and find elements')
t31 = lxml.etree.parse('ed3_deleterequest.xml')
assert t31.getroot().attrib[XMLNS_PVZD_PREFIX+'disposition'] == 'delete'

print('3.2 Parse string into ElementTree and find elements/attributes (pvzd namespace')
with open('ed3_deleterequest.xml', encoding='utf8') as fd:
    xml_str = fd.read()
e32 = lxml.etree.fromstring(xml_str.encode('utf-8'))
t32 = e32.getroottree()
assert t32.getroot().attrib[XMLNS_PVZD_PREFIX+'disposition'] == 'delete'
assert t32.find('//pvzd:disposition', namespaces={'pvzd': XMLNS_PVZD}).text == 'delete'
assert e32.xpath('//md:Extensions', namespaces={'md': XMLNS_MD})[0].tag == '{urn:oasis:names:tc:SAML:2.0:metadata}Extensions'
assert t32.xpath('//pvzd:disposition',namespaces={'pvzd': XMLNS_PVZD})[0].tag == XMLNS_PVZD_PREFIX+'disposition'


print('4 Examples with UTF-16 XML document')

print('4.1 UTF-16 using etree.parse()')
t41 = lxml.etree.parse('ed4_utf16_encoding.xml')
assert t41.xpath('//OrganizationName')[0].text == 'ÜDÖLLÄ Ltd'
assert t41.xpath('//OrganizationDisplayName')[0].text == 'Many Umlauts: äöü'

#print('4.2 UTF-16 using etree.fromstring()')
# The following example is wrong, because the encoding is defined in the file, and should not be assumed by open():
#with open('ed4_utf16_encoding.xml', encoding='utf-16') as fd:
#    xml_str = fd.read()
# use etree.parse() instead
