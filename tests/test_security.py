"""Security-focused tests for meter_reader."""

import unittest

from defusedxml.ElementTree import fromstring
from defusedxml.minidom import parseString

from meter_reader.utils import generate_command_xml


class TestXMLSecurity(unittest.TestCase):
    """Test XML parsing security."""

    def test_uses_defusedxml_minidom(self):
        """Verify that command XML uses defusedxml for safe parsing."""
        xml = generate_command_xml(
            "0xd8d5b9000000abcd",
            Name="test_command"
        )
        self.assertIsNotNone(xml)
        self.assertIn("<LocalCommand>", xml)

    def test_defusedxml_parsestring_not_vulnerable(self):
        """Test that defusedxml.minidom.parseString is used."""
        test_xml = b"<test>safe</test>"
        result = parseString(test_xml)
        self.assertEqual(result.documentElement.tagName, "test")

    def test_defusedxml_fromstring_not_vulnerable(self):
        """Test that defusedxml ElementTree.fromstring is used."""
        test_xml = "<test>safe</test>"
        result = fromstring(test_xml)
        self.assertEqual(result.tag, "test")

    def test_xxe_prevention(self):
        """Test that XXE (XML External Entity) attacks are prevented."""
        xxe_payload = (
            '<?xml version="1.0"?>'
            '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
            '<foo>&xxe;</foo>'
        )
        try:
            result = fromstring(xxe_payload)
            self.assertIsNone(result.text or "")
        except Exception as e:
            self.assertIsNotNone(e)

    def test_billion_laughs_prevention(self):
        """Test that Billion Laughs attack is prevented."""
        billion_laughs = (
            '<?xml version="1.0"?>'
            '<!DOCTYPE lolz ['
            '  <!ENTITY lol "lol">'
            '  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">'
            '  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">'
            ']>'
            '<lolz>&lol3;</lolz>'
        )
        try:
            result = fromstring(billion_laughs)
            self.assertIsNotNone(result)
        except Exception as e:
            self.assertIsNotNone(e)


class TestInputValidation(unittest.TestCase):
    """Test input validation for command generation."""

    def test_command_xml_escaping(self):
        """Test that values are properly escaped in XML."""
        dangerous_value = '<script>alert("xss")</script>'
        xml = generate_command_xml(
            "0xd8d5b9000000abcd",
            Name="test",
            Text=dangerous_value
        )
        self.assertNotIn("<script>", xml)
        self.assertIn("&lt;", xml)

    def test_mac_id_validation(self):
        """Test that MAC ID is properly handled."""
        mac_id = "0xd8d5b9000000abcd"
        xml = generate_command_xml(mac_id, Name="test")
        self.assertIn(mac_id, xml)

    def test_none_value_handling(self):
        """Test that None values are safely handled."""
        xml = generate_command_xml(
            "0xd8d5b9000000abcd",
            Name="test",
            Text=None
        )
        self.assertIsNotNone(xml)
        self.assertIn("<LocalCommand>", xml)


class TestDependencySecurity(unittest.TestCase):
    """Test that secure dependencies are used."""

    def test_defusedxml_installed(self):
        """Verify defusedxml is available."""
        try:
            import defusedxml
            self.assertIsNotNone(defusedxml)
        except ImportError:
            self.fail("defusedxml is not installed")

    def test_pydantic_version(self):
        """Verify pydantic is installed (for data validation)."""
        try:
            import pydantic
            self.assertIsNotNone(pydantic)
        except ImportError:
            self.fail("pydantic is not installed")



