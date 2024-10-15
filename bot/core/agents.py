import random

existing_versions = {
    120: [
        '120.0.6099.230',
        '120.0.6099.210',
        '120.0.6099.194',
        '120.0.6099.193',
        '120.0.6099.145',
        '120.0.6099.144',
        '120.0.6099.116',
        '120.0.6099.115',
        '120.0.6099.44',
        '120.0.6099.43'
    ],
    121: [
        '121.0.6167.178',
        '121.0.6167.165',
        '121.0.6167.164',
        '121.0.6167.144',
        '121.0.6167.143',
        '121.0.6167.101'
    ],
    122: [
        '122.0.6261.119',
        '122.0.6261.106',
        '122.0.6261.105',
        '122.0.6261.91',
        '122.0.6261.90',
        '122.0.6261.64',
        '122.0.6261.43'
    ],
    123: [
        '123.0.6312.121',
        '123.0.6312.120',
        '123.0.6312.119',
        '123.0.6312.118',
        '123.0.6312.99',
        '123.0.6312.80',
        '123.0.6312.41',
        '123.0.6312.40'
    ],
    124: [
        '124.0.6367.179',
        '124.0.6367.172',
        '124.0.6367.171',
        '124.0.6367.114',
        '124.0.6367.113',
        '124.0.6367.83',
        '124.0.6367.82',
        '124.0.6367.54'
    ],
    125: [
        '125.0.6422.165',
        '125.0.6422.164',
        '125.0.6422.147',
        '125.0.6422.146',
        '125.0.6422.113',
        '125.0.6422.72',
        '125.0.6422.53',
        '125.0.6422.52'
    ],
    126: [
        '126.0.6478.122',
        '126.0.6478.72',
        '126.0.6478.71',
        '126.0.6478.50'
    ],
    127: [
        '127.0.6519.87',
        '127.0.6519.83',
        '127.0.6519.62',
        '127.0.6519.38'
    ]
}


def generate_webview_user_agent():
    android_versions = ['10', '11', '12', '13', '14']
    android_version = random.choice(android_versions)

    chrome_version = random.choice(list(existing_versions.keys()))
    chrome_full_version = random.choice(existing_versions[chrome_version])

    android_devices = [
        'SM-G960F', 'Pixel 5', 'SM-A505F', 'Pixel 4a', 'Pixel 6 Pro', 'SM-N975F',
        'SM-G973F', 'Pixel 3', 'SM-G980F', 'Pixel 5a', 'SM-G998B', 'Pixel 4',
        'SM-G991B', 'SM-G996B', 'SM-F711B', 'SM-F916B', 'SM-G781B', 'SM-N986B',
        'SM-N981B', 'Pixel 2', 'Pixel 2 XL', 'Pixel 3 XL', 'Pixel 4 XL',
        'Pixel 5 XL', 'Pixel 6', 'Pixel 6 XL', 'Pixel 6a', 'Pixel 7', 'Pixel 7 Pro',
        'OnePlus 8', 'OnePlus 8 Pro', 'OnePlus 9', 'OnePlus 9 Pro', 'OnePlus Nord', 'OnePlus Nord 2',
        'OnePlus Nord CE', 'OnePlus 10', 'OnePlus 10 Pro', 'OnePlus 10T', 'OnePlus 10T Pro',
        'Xiaomi Mi 9', 'Xiaomi Mi 10', 'Xiaomi Mi 11', 'Xiaomi Redmi Note 8', 'Xiaomi Redmi Note 9',
        'Huawei P30', 'Huawei P40', 'Huawei Mate 30', 'Huawei Mate 40', 'Sony Xperia 1',
        'Sony Xperia 5', 'LG G8', 'LG V50', 'LG V60', 'Nokia 8.3', 'Nokia 9 PureView',
        'Pixel 7a', 'Pixel 8', 'Pixel 8 Pro', 'Samsung Galaxy S23', 'Samsung Galaxy S23 Ultra',
        'OnePlus 11', 'Xiaomi 13', 'Xiaomi 13 Pro', 'Oppo Find X6 Pro', 'Vivo X90 Pro',
        'Asus ROG Phone 7', 'Motorola Edge 40 Pro', 'Nothing Phone (2)', 'Realme GT3'
    ]
    android_device = random.choice(android_devices)

    user_agent = (f"Mozilla/5.0 (Linux; Android {android_version}; {android_device}) "
                  f"AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
                  f"Chrome/{chrome_full_version} Mobile Safari/537.36")

    sec_ch_ua = f'"Not)A;Brand";v="99", "Android WebView";v="{chrome_version}", "Chromium";v="{chrome_version}"'

    return user_agent, sec_ch_ua

def generate_sec_ch_ua(major_version):
    if major_version < 122:
        return f'"Not A;Brand";v="99", "Android WebView";v="{major_version}", "Chromium";v="{major_version}"'
    else:
        return f'"Not)A;Brand";v="24", "Android WebView";v="{major_version}", "Chromium";v="{major_version}"'

def generate_random_user_agent(device_type='android', browser_type='webview'):
    firefox_versions = list(range(90, 124))  # Updated to include more recent Firefox versions

    if browser_type == 'webview':
        return generate_webview_user_agent()

    if browser_type == 'chrome':
        major_version = random.choice(list(existing_versions.keys()))
        browser_version = random.choice(existing_versions[major_version])
        sec_ch_ua = generate_sec_ch_ua(major_version)

    elif browser_type == 'firefox':
        browser_version = random.choice(firefox_versions)
        sec_ch_ua = f'"Firefox";v="{browser_version}", "Not)A;Brand";v="99"'

    if device_type == 'android':
        android_versions = ['10.0', '11.0', '12.0', '13.0', '14.0', '15.0']
        android_device = random.choice([
            'SM-G960F', 'Pixel 5', 'SM-A505F', 'Pixel 4a', 'Pixel 6 Pro', 'SM-N975F',
            'SM-G973F', 'Pixel 3', 'SM-G980F', 'Pixel 5a', 'SM-G998B', 'Pixel 4',
            'SM-G991B', 'SM-G996B', 'SM-F711B', 'SM-F916B', 'SM-G781B', 'SM-N986B',
            'SM-N981B', 'Pixel 2', 'Pixel 2 XL', 'Pixel 3 XL', 'Pixel 4 XL',
            'Pixel 5 XL', 'Pixel 6', 'Pixel 6 XL', 'Pixel 6a', 'Pixel 7', 'Pixel 7 Pro',
            'OnePlus 8', 'OnePlus 8 Pro', 'OnePlus 9', 'OnePlus 9 Pro', 'OnePlus Nord', 'OnePlus Nord 2',
            'OnePlus Nord CE', 'OnePlus 10', 'OnePlus 10 Pro', 'OnePlus 10T', 'OnePlus 10T Pro',
            'Xiaomi Mi 9', 'Xiaomi Mi 10', 'Xiaomi Mi 11', 'Xiaomi Redmi Note 8', 'Xiaomi Redmi Note 9',
            'Huawei P30', 'Huawei P40', 'Huawei Mate 30', 'Huawei Mate 40', 'Sony Xperia 1',
            'Sony Xperia 5', 'LG G8', 'LG V50', 'LG V60', 'Nokia 8.3', 'Nokia 9 PureView',
            'Pixel 7a', 'Pixel 8', 'Pixel 8 Pro', 'Samsung Galaxy S23', 'Samsung Galaxy S23 Ultra',
            'OnePlus 11', 'Xiaomi 13', 'Xiaomi 13 Pro', 'Oppo Find X6 Pro', 'Vivo X90 Pro',
            'Asus ROG Phone 7', 'Motorola Edge 40 Pro', 'Nothing Phone (2)', 'Realme GT3'
        ])
        android_version = random.choice(android_versions)
        if browser_type == 'chrome':
            user_agent = (f"Mozilla/5.0 (Linux; Android {android_version}; {android_device}) AppleWebKit/537.36 "
                          f"(KHTML, like Gecko) Chrome/{browser_version} Mobile Safari/537.36")
        elif browser_type == 'firefox':
            user_agent = (f"Mozilla/5.0 (Android {android_version}; Mobile; rv:{browser_version}.0) "
                          f"Gecko/{browser_version}.0 Firefox/{browser_version}.0")

    elif device_type == 'ios':
        ios_versions = ['13.0', '14.0', '15.0', '16.0', '17.0', '18.0']
        ios_version = random.choice(ios_versions)
        if browser_type == 'chrome':
            user_agent = (f"Mozilla/5.0 (iPhone; CPU iPhone OS {ios_version.replace('.', '_')} like Mac OS X) "
                          f"AppleWebKit/537.36 (KHTML, like Gecko) CriOS/{browser_version} Mobile/15E148 Safari/604.1")
        elif browser_type == 'firefox':
            user_agent = (f"Mozilla/5.0 (iPhone; CPU iPhone OS {ios_version.replace('.', '_')} like Mac OS X) "
                          f"AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/{browser_version}.0 Mobile/15E148 Safari/605.1.15")

    elif device_type == 'windows':
        windows_versions = ['10.0', '11.0']
        windows_version = random.choice(windows_versions)
        if browser_type == 'chrome':
            user_agent = (
                f"Mozilla/5.0 (Windows NT {windows_version}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{browser_version} Safari/537.36")
        elif browser_type == 'firefox':
            user_agent = (f"Mozilla/5.0 (Windows NT {windows_version}; Win64; x64; rv:{browser_version}.0) "
                          f"Gecko/{browser_version}.0 Firefox/{browser_version}.0")

    elif device_type == 'ubuntu':
        if browser_type == 'chrome':
            user_agent = (f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          f"Chrome/{browser_version} Safari/537.36")
        elif browser_type == 'firefox':
            user_agent = (f"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:{browser_version}.0) Gecko/{browser_version}.0 "
                          f"Firefox/{browser_version}.0")
    else:
        return None, None

    return user_agent, sec_ch_ua