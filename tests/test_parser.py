import unittest
from meter_reader.clients.socket import EagleSocketClient

class TestXMLParser(unittest.TestCase):
    def setUp(self):
        # Create a minimal client instance (no network needed for parsing tests)
        self.client = EagleSocketClient.__new__(EagleSocketClient)
        
    def test_simple_xml(self):
        xml = """<response>
            <DeviceMacId>0xd8d5b9000000abcd</DeviceMacId>
            <Status>Connected</Status>
        </response>"""
        result = self.client._xml2dict(xml, convert=False)
        self.assertEqual(result['DeviceMacId'], '0xd8d5b9000000abcd')
        self.assertEqual(result['Status'], 'Connected')
        
    def test_nested_xml(self):
        xml = """<response>
            <DeviceInfo>
                <DeviceMacId>0xd8d5b9000000abcd</DeviceMacId>
                <ModelId>Z109-EAGLE</ModelId>
            </DeviceInfo>
        </response>"""
        result = self.client._xml2dict(xml, convert=False)
        self.assertIn('DeviceInfo', result)
        self.assertEqual(result['DeviceInfo']['DeviceMacId'], '0xd8d5b9000000abcd')
        
    def test_list_detection(self):
        xml = """<response>
            <HistoryData>
                <CurrentSummation>
                    <TimeStamp>0x1a2b3c4d</TimeStamp>
                    <SummationDelivered>0x12345</SummationDelivered>
                </CurrentSummation>
                <CurrentSummation>
                    <TimeStamp>0x1a2b3c5e</TimeStamp>
                    <SummationDelivered>0x12346</SummationDelivered>
                </CurrentSummation>
            </HistoryData>
        </response>"""
        result = self.client._xml2dict(xml, convert=False)
        self.assertIn('HistoryData', result)
        self.assertIn('CurrentSummation', result['HistoryData'])
        self.assertIsInstance(result['HistoryData']['CurrentSummation'], list)
        self.assertEqual(len(result['HistoryData']['CurrentSummation']), 2)

if __name__ == '__main__':
    unittest.main()
