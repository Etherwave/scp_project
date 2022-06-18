import hashlib

def MessageDigestAlgorithmForFile(fpath: str, algorithm: str) -> str:
    f = open(fpath, 'rb')
    hash = hashlib.new(algorithm)
    for chunk in iter(lambda: f.read(2**20), b''):
        hash.update(chunk)
    f.close()
    return hash.hexdigest()

def MessageDigestAlgorithmForStr(strfordigest: str, algorithm: str) -> str:
    hash = hashlib.new(algorithm)
    hash.update(strfordigest.encode('utf-8'))
    return hash.hexdigest()

if __name__ == '__main__':
    # algorithm = "md5"
    algorithm = "sha256"
    # file_path = "D:/software/uiso/system_iso/cn_windows_10_consumer_editions_version_20h2_updated_april_2021_x64_dvd_ace7e59c.iso"
    # hexdigest = MessageDigestAlgorithmForFile(file_path, algorithm)
    # print(f'{algorithm}: {hexdigest}')

    strfordigest = "156as4d6a5sd4"
    hexdigest = MessageDigestAlgorithmForStr(strfordigest, algorithm)
    print(f'{algorithm}: {hexdigest}')


