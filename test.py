import io
import lxml.etree

XMLNS_DSIG = 'http://www.w3.org/2000/09/xmldsig#'
XMLNS_DSIG_PREFIX = '{%s}' % XMLNS_DSIG
XMLNS_MD = 'urn:oasis:names:tc:SAML:2.0:metadata'
XMLNS_MD_PREFIX = '{%s}' % XMLNS_MD
XMLNS_PVZD = 'http://egov.gv.at/pvzd1.xsd'
XMLNS_PVZD_PREFIX = '{%s}' % XMLNS_PVZD
XMLNS_MDRPI = 'urn:oasis:names:tc:SAML:2.0:metadata:rpi'
XMLNS_MDRPI_PREFIX = '{%s}' % XMLNS_MDRPI

# notes on lxml:
#   - xpath() has different namespace semantics (using QNames) as opposed to find(),
#     Element.attrib addressing, Element() etc.
#   - Element has the usedful aspect of listing its children (-> for child in element:)
#   - parse() and fromstring() yield ElementTree and Element, respectively
#   - To open an xml-document from the filesystem always use parse(), because it will detect the encoding

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
assert len(t32.xpath('//@md:Location', namespaces={'md': XMLNS_MD})) > 0


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
# to convert to utf-8:
# lxml.etree.tostring(self.tree, encoding='utf-8', pretty_print=True)

print('5 C14N')
o51 = io.BytesIO()
t51 = lxml.etree.parse('ed1_without_ns.xml')
t51.write_c14n(o51)
assert o51.getvalue().decode('utf-8')[0:61] == '<EntityDescriptor entityID="https://idp.example.com/idp.xml">'
o51.close()

print('6 Modify Tree')
print('6.1 Append element and remove it')
def append_if_missing(
        tree: lxml.etree.ElementTree,
        xpath_insert_parent: str,
        xpath_new_element: str,
        new_element: lxml.etree.Element,
        namespaces: dict):
    if len(tree.xpath(xpath_new_element, namespaces=namespaces)) == 0:
        parent_element = tree.xpath(xpath_insert_parent, namespaces=namespaces)
        parent_element[0].append(new_element)  # append only for 1st

t61 = lxml.etree.parse('ed2_with_ns.xml')
new = lxml.etree.Element(XMLNS_MD_PREFIX+"Extensions")
append_if_missing(t61, '/md:EntityDescriptor', '/md:EntityDescriptor/md:Extensions', new, {'md': XMLNS_MD})
o61=io.BytesIO()
t61.write(o61)
o61.getvalue()

print('remove element')
child=t61.xpath('/md:EntityDescriptor/md:Extensions', namespaces={'md': XMLNS_MD, 'ns0': XMLNS_MDRPI})[0]
parent=t61.xpath('/md:EntityDescriptor', namespaces={'md': XMLNS_MD, 'ns0': XMLNS_MDRPI})[0]
parent.remove(child)
o61=io.BytesIO()
t61.write(o61)
o61.getvalue()

#if len(t61.xpath('/md:EntityDescriptor/md:Extensions', namespaces={'md': XMLNS_MD})) == 0:
#    insert_to_element = t61.xpath('/md:EntityDescriptor', namespaces={'md': XMLNS_MD})
#new = lxml.etree.Element(XMLNS_MDRPI_PREFIX+"RegistrationInfo")
#insert_to_element = t61.xpath('/md:EntityDescriptor/md:Extensions', namespaces={'md': XMLNS_MD})
#if len(insert_to_element) > 0:
#    insert_to_element[0].append(new)  # append only for 1st
#assert lxml.etree.tostring(t61, pretty_print=True) == b'<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" xmlns:alg="urn:oasis:names:tc:SAML:metadata:algsupport" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:mdui="urn:oasis:names:tc:SAML:metadata:ui" entityID="https://idp.example.com/idp.xml">\n    <md:IDPSSODescriptor WantAuthnRequestsSigned="false" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">\n         <md:Extensions>\n            <alg:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>\n            <alg:SigningMethod MinKeySize="256" MaxKeySize="511" Algorithm="http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha256"/>\n            <alg:SigningMethod MinKeySize="2048" MaxKeySize="4096" Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>\n            <!-- blacklisted: http://www.w3.org/2000/09/xmldsig#rsa-sha1 -->\n            <mdui:UIInfo>\n                <mdui:DisplayName xml:lang="en">Test Driver IdP </mdui:DisplayName>\n                <mdui:Description xml:lang="en">Saml2Test Test Driver IdP</mdui:Description>\n            </mdui:UIInfo>\n            <mdui:DiscoHints>\n                <mdui:DomainHint>https://github.com/rohe/fedlab/</mdui:DomainHint>\n                <mdui:IPHint>81.217.70.0/8</mdui:IPHint>\n                <mdui:GeolocationHint>geo:92.3308,17.0516</mdui:GeolocationHint>\n            </mdui:DiscoHints>\n        <ns0:RegistrationInfo xmlns:ns0="urn:oasis:names:tc:SAML:metadata:rpi"/><ns0:RegistrationInfo xmlns:ns0="urn:oasis:names:tc:SAML:metadata:rpi"/></md:Extensions>\n        <md:KeyDescriptor use="signing">\n            <ds:KeyInfo>\n                <ds:X509Data>\n                    <ds:X509Certificate>MIIC8jCCAlugAwIBAgIJAJHg2V5J31I8MA0GCSqGSIb3DQEBBQUAMFoxCzAJBgNVBAYTAlNFMQ0wCwYDVQQHEwRVbWVhMRgwFgYDVQQKEw9VbWVhIFVuaXZlcnNpdHkxEDAOBgNVBAsTB0lUIFVuaXQxEDAOBgNVBAMTB1Rlc3QgU1AwHhcNMDkxMDI2MTMzMTE1WhcNMTAxMDI2MTMzMTE1WjBaMQswCQYDVQQGEwJTRTENMAsGA1UEBxMEVW1lYTEYMBYGA1UEChMPVW1lYSBVbml2ZXJzaXR5MRAwDgYDVQQLEwdJVCBVbml0MRAwDgYDVQQDEwdUZXN0IFNQMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDkJWP7bwOxtH+E15VTaulNzVQ/0cSbM5G7abqeqSNSs0l0veHr6/ROgW96ZeQ57fzVy2MCFiQRw2fzBs0n7leEmDJyVVtBTavYlhAVXDNa3stgvh43qCfLx+clUlOvtnsoMiiRmo7qf0BoPKTj7c0uLKpDpEbAHQT4OF1HRYVxMwIDAQABo4G/MIG8MB0GA1UdDgQWBBQ7RgbMJFDGRBu9o3tDQDuSoBy7JjCBjAYDVR0jBIGEMIGBgBQ7RgbMJFDGRBu9o3tDQDuSoBy7JqFepFwwWjELMAkGA1UEBhMCU0UxDTALBgNVBAcTBFVtZWExGDAWBgNVBAoTD1VtZWEgVW5pdmVyc2l0eTEQMA4GA1UECxMHSVQgVW5pdDEQMA4GA1UEAxMHVGVzdCBTUIIJAJHg2V5J31I8MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEFBQADgYEAMuRwwXRnsiyWzmRikpwinnhTmbooKm5TINPE7A7gSQ710RxioQePPhZOzkM27NnHTrCe2rBVg0EGz7QTd1JIwLPvgoj4VTi/fSha/tXrYUaqc9AqU1kWI4WN                        +vffBGQ09mo+6CffuFTZYeOhzP/2stAPwCTU4kxEoiy0KpZMANI=\n                    </ds:X509Certificate>\n                </ds:X509Data>\n            </ds:KeyInfo>\n        </md:KeyDescriptor>\n        <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://idp.example.com/slo/post"/>\n        <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://idp.example.com/slo/redirect"/>\n        <md:ManageNameIDService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://idp.example.com/mni/post"/>\n        <md:ManageNameIDService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://idp.example.com/mni/redirect"/>\n        <md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</md:NameIDFormat>\n        <md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</md:NameIDFormat>\n        <md:SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://idp.example.com/sso/redirect"/>\n        <md:SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://idp.example.com/sso/post"/>\n        <md:AssertionIDRequestService Binding="urn:oasis:names:tc:SAML:2.0:bindings:URI" Location="https://idp.example.com/airs"/>\n    </md:IDPSSODescriptor>\n    <md:Organization>\n        <md:OrganizationName xml:lang="en">Saml2Test Harness</md:OrganizationName>\n        <md:OrganizationDisplayName xml:lang="en">Saml2Test Harness</md:OrganizationDisplayName>\n        <md:OrganizationURL xml:lang="en">https://github.com/rohe/saml2test/</md:OrganizationURL>\n    </md:Organization>\n    <md:ContactPerson contactType="technical">\n        <md:GivenName>Testiani</md:GivenName>\n        <md:SurName>Testosteroni</md:SurName>\n        <md:EmailAddress>testiani@example.com</md:EmailAddress>\n    </md:ContactPerson>\n</md:EntityDescriptor>\n'

print('6.2 Insert element as first subelement')
def insert_if_missing(
        tree: lxml.etree.ElementTree,
        xpath_insert_parent: str,
        xpath_new_element: str,
        new_element: lxml.etree.Element,
        namespaces: dict):
    if len(tree.xpath(xpath_new_element, namespaces=namespaces)) == 0:
        parent_element = tree.xpath(xpath_insert_parent, namespaces=namespaces)
        parent_element[0].insert(0, new_element)  # append only for 1st

t62 = lxml.etree.parse('ed2_with_ns.xml')
new = lxml.etree.Element(XMLNS_MD_PREFIX+"Extensions")
insert_if_missing(t62, '/md:EntityDescriptor', '/md:EntityDescriptor/md:Extensions', new, {'md': XMLNS_MD})
o62=io.BytesIO()
t62.write(o62)
o62.getvalue()

