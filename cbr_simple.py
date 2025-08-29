#!/usr/bin/env python3
"""
Simplified CBR Client for getting USD exchange rates
"""

import requests
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal
from typing import Optional


class CBRClient:
    """Simple client for Central Bank of Russia API."""
    
    BASE_URL = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
    TIMEOUT = 30  # seconds
    
    def get_rate(self, currency: str, date_req: date) -> Optional[Decimal]:
        """
        Get exchange rate for specific date.
        
        Args:
            currency (str): Currency code (e.g., 'USD', 'EUR')
            date_req (date): Date for which to get the rate
            
        Returns:
            Optional[Decimal]: Exchange rate or None if not found
        """
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
            xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
            xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <GetCursOnDate xmlns="http://web.cbr.ru/">
              <On_date>{date_req.strftime('%Y-%m-%d')}</On_date>
            </GetCursOnDate>
          </soap12:Body>
        </soap12:Envelope>"""

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": "http://web.cbr.ru/GetCursOnDate",
        }

        try:
            response = requests.post(
                self.BASE_URL, 
                data=soap_body, 
                headers=headers, 
                timeout=self.TIMEOUT
            )
            
            if response.status_code != 200:
                print(f"CBR API error: HTTP {response.status_code}")
                return None

            root = ET.fromstring(response.text)

            # Parse XML response
            namespace = {
                "soap12": "http://www.w3.org/2003/05/soap-envelope",
                "cbr": "http://web.cbr.ru/",
                "diffgr": "urn:schemas-microsoft-com:xml-diffgram-v1",
            }

            for valute in root.findall(".//diffgr:diffgram/ValuteData/ValuteCursOnDate", namespace):
                vch_code = valute.find("VchCode").text
                if vch_code == currency:
                    vcurs = valute.find("Vcurs").text
                    vnom = valute.find("Vnom").text
                    print(f"Found rate for {currency}: {vcurs} / {vnom}")
                    return Decimal(vcurs) / Decimal(vnom)

        except Exception as e:
            print(f"Error getting exchange rate: {e}")
            return None

        return None


if __name__ == "__main__":
    # Test the client
    client = CBRClient()
    today = date.today()
    rate = client.get_rate('USD', today)
    if rate:
        print(f"USD rate for {today}: {rate}")
    else:
        print("Could not get USD rate")
