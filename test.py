import lxml.etree


print('1. Examples without namespace')

print('1.1 Parse file into ElementTree and find elements')
t = lxml.etree.parse('ed_without_ns.xml')
t.xpath('//X509Certificate')
t.getroot()
t.find('IDPSSODescriptor')
t.find('Organization')
t.find('OrganizationName')

print('1.2 Parse file into Element and find elements')
f = open('ed_without_ns.xml', encoding='utf8')
xml_str=f.read()
e = lxml.etree.fromstring(xml_str.encode('utf-8'))
assert e.tag == 'EntityDescriptor'
assert e.attrib == {'entityID': 'https://idp.example.com/idp.xml'}
assert e.xpath('//X509Certificate')[0].tag == 'X509Certificate'
e.find('IDPSSODescriptor')
e.find('Organization')
e.find('OrganizationName')


print('2. Examples with namespace')

XMLNS_DSIG = '{http://www.w3.org/2000/09/xmldsig#}'
# XMLNS_MD = '{urn:oasis:names:tc:SAML:2.0:metadata}'
XMLNS_MD = 'urn:oasis:names:tc:SAML:2.0:metadata'
print('2.1 Parse file into ElementTree and find elements')
t = lxml.etree.parse('ed_with_ns.xml')
assert t.getroot().tag == '{urn:oasis:names:tc:SAML:2.0:metadata}EntityDescriptor'
assert t.xpath('/*')[0].tag == '{urn:oasis:names:tc:SAML:2.0:metadata}EntityDescriptor'
xp = 'md:IDPSSODescriptor//ds:X509Certificate'
t.xpath(xp, namespaces={'ds': XMLNS_DSIG, 'md': XMLNS_MD})

print(t.find('.//{'+XMLNS_MD+'}GivenName', namespaces={'ds': XMLNS_DSIG, 'md': XMLNS_MD}).text)

