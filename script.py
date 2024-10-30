import base64
import requests
import xml.etree.ElementTree as ET

def main():
    # Get user input
    number = input("Enter Your Number: ")
    password = input("Enter Your Password: ")
    email = input("Enter Your Email: ")

    # Process the number
    if "011" in number:
        num = number[1:]  # Remove the leading "0"
    else:
        num = number

    # Prepare Basic Authentication
    code = f"{email}:{password}"
    ccode = code.encode("ascii")
    base64_bytes = base64.b64encode(ccode)
    auth = base64_bytes.decode("ascii")
    xauth = f"Basic {auth}"

    urllog = "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan"
    
    headerslog = {
        "applicationVersion": "2",
        "applicationName": "MAB",
        "Accept": "text/xml",
        "Authorization": xauth,
        "APP-BuildNumber": "964",
        "APP-Version": "27.0.0",
        "OS-Type": "Android",
        "OS-Version": "12",
        "APP-STORE": "GOOGLE",
        "Is-Corporate": "false",
        "Content-Type": "text/xml; charset=UTF-8",
    }

    datalog = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
    <loginRequest>
        <deviceId></deviceId>
        <firstLoginAttempt>true</firstLoginAttempt>
        <modelType></modelType>
        <osVersion></osVersion>
        <platform>Android</platform>
        <udid></udid>
    </loginRequest>"""
    
    # Send login request
    log = requests.post(urllog, headers=headerslog, data=datalog)

    if "true" in log.text:
        # Retrieve cookies and auth token from the response
        st = log.headers["Set-Cookie"]
        ck = st.split(";")[0]
        br = log.headers["auth"]

        # Construct URL for offers
        url = f"https://mab.etisalat.com.eg:11003/Saytar/rest/zero11/offersV3?req=<dialAndLanguageRequest><subscriberNumber>{num}</subscriberNumber><language>1</language></dialAndLanguageRequest>"

        headers = {
            'applicationVersion': "2",
            'Content-Type': "text/xml",
            'applicationName': "MAB",
            'Accept': "text/xml",
            'Language': "ar",
            'APP-BuildNumber': "10459",
            'APP-Version': "29.9.0",
            'OS-Type': "Android",
            'OS-Version': "11",
            'APP-STORE': "GOOGLE",
            'auth': f"Bearer {br}",
            'Host': "mab.etisalat.com.eg:11003",
            'Is-Corporate': "false",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'User-Agent': "okhttp/5.0.0-alpha.11",
            'Cookie': ck
        }

        # Send request for offers
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            root = ET.fromstring(response.text)
            offer_id = None
            
            # Parse the XML response to find the Offer_ID
            for category in root.findall('.//mabCategory'):
                for product in category.findall('.//mabProduct'):
                    for parameter in product.findall('.//fulfilmentParameter'):
                        if parameter.find('name').text == 'Offer_ID':
                            offer_id = parameter.find('value').text
                            break
                    if offer_id:
                        break
                if offer_id:
                    break

            if offer_id:
                print(f"Offer ID: {offer_id}")

                # Submit the order
                urlsub = "https://mab.etisalat.com.eg:11003/Saytar/rest/zero11/submitOrder"

                headerssub = {
                    "applicationVersion": "2",
                    "applicationName": "MAB",
                    "Accept": "text/xml",
                    "Cookie": ck,
                    "Language": "ar",
                    "APP-BuildNumber": "964",
                    "APP-Version": "27.0.0",
                    "OS-Type": "Android",
                    "OS-Version": "12",
                    "APP-STORE": "GOOGLE",
                    "auth": f"Bearer {br}",
                    "Is-Corporate": "false",
                    "Content-Type": "text/xml; charset=UTF-8",
                }

                datasub = f"""<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
                <submitOrderRequest>
                    <mabOperation></mabOperation>
                    <msisdn>{num}</msisdn>
                    <operation>ACTIVATE</operation>
                    <parameters>
                        <parameter>
                            <name>GIFT_FULLFILMENT_PARAMETERS</name>
                            <value>Offer_ID:{offer_id};ACTIVATE:True;isRTIM:Y</value>
                        </parameter>
                    </parameters>
                    <productName>FAN_ZONE_HOURLY_BUNDLE</productName>
                </submitOrderRequest>"""

                subs = requests.post(urlsub, headers=headerssub, data=datasub).text

                if "true" in subs:
                    print("❤️‍🔥 معاك ساعتين سوشيال استخدمهم ف ما يرضي الله❤️‍🔥")
                else:
                    print("اتاكد من بياناتك")
            else:
                print("العرض مش هينفع معاك")
        else:
            print("العرض مش متوفر الان")
    else:
        print("اسم المستخدم او كلمة السر خطا")

if __name__ == "__main__":
    main()
