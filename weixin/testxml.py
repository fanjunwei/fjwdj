__author__ = 'fanjunwei003'
import xml.etree.ElementTree as ET

def test():
    tree=ET.fromstring('<xml></xml>')
    fromE=ET.Element('ToUserName')
    fromE.text='sfsdfsdfsdf'
    tree.append(fromE)
    print ET.tostring(tree,'utf8')


if __name__ == '__main__':
    test()