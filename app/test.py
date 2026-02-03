
url = "https://onu.instructure.com/"

def parse_url(url: str):
    start = url.find("https://")
    if start == -1:
        return None
    
    rest = url[start + len("https://"): ]
    host = rest.split(".", 1)[0]
    print(f"Host = {host}")


instance = parse_url(url)
print(f"Instance = {instance}")