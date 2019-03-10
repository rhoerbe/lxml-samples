from pathlib import Path
import lxml.etree

XMLNS_MD = 'urn:oasis:names:tc:SAML:2.0:metadata'
XMLNS_MD_PREFIX = '{%s}' % XMLNS_MD

def _extract_saml_entitydescriptor(tree: lxml.etree.ElementTree) -> lxml.etree.ElementTree:
    xsl82_path = str(Path('82_extract_ed.xslt'))
    xslt = lxml.etree.parse(xsl82_path)
    transform = lxml.etree.XSLT(xslt)
    return transform(tree)


def _tidy_saml_entitydescriptor(tree: lxml.etree.ElementTree) -> lxml.etree.ElementTree:
    xsl81_path = str(Path('81_tidy_samled.xslt'))
    xslt = lxml.etree.parse(xsl81_path)
    transform = lxml.etree.XSLT(xslt)
    return transform(tree)


def normalize_ed(xml: bytes) -> bytes:
    ''' convert EntityDescriptor to UTF-8, move namespace declarations to the top,
        remove EntitiesDescriptor root element,
        remove signature/validuntil/cacheduration pretty-print '''
    tree: lxml.etree.ElementTree = lxml.etree.fromstring(xml).getroottree()
    tree: lxml.etree.ElementTree = _extract_saml_entitydescriptor(tree)
    tree: lxml.etree.ElementTree = _tidy_saml_entitydescriptor(tree)
    return lxml.etree.tostring(tree, encoding='UTF-8', xml_declaration=True, pretty_print=True)


print('9.1 remove EntitiesDescriptor Root element and make EntityDescrptor new Root')
xml91_path = Path('24_entities_utf16.xml')
xml91_bytes = xml91_path.read_bytes()
try:
    xml91_str = normalize_ed(xml91_bytes)
except Exception as e:
    pass
xml91out_path = Path('testout/24_entities_utf16.xml')
xml91out_path.write_bytes(xml91_bytes)
