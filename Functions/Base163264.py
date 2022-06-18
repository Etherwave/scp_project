import base64

def base64encode_string2string(string):
    string = string.encode('utf-8')
    ans = base64.b64encode(string)
    ans = bytes(ans).decode('utf-8')
    return ans

def base64decode_string2string(string):
    string = string.encode('utf-8')
    ans = base64.b64decode(string)
    ans = ans.decode('utf-8')
    return ans

def base64encode_bytes2string(bytes_data):
    ans = base64.b64encode(bytes_data)
    ans = bytes(ans).decode('utf-8')
    return ans

def base64decode_bytes2string(bytes_data):
    ans = base64.b64decode(bytes_data)
    ans = ans.decode('utf-8')
    return ans

def base64encode_bytes2bytes(bytes_data):
    ans = base64.b64encode(bytes_data)
    return ans

def base64decode_bytes2bytes(bytes_data):
    ans = base64.b64decode(bytes_data)
    return ans

if __name__ == '__main__':
    ans = base64encode_string2string('Why Blog')
    print(ans)
    ans = base64decode_string2string(ans)
    print(ans)
