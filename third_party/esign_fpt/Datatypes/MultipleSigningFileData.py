from builtins import bytearray


# This class use for contain value of filedata

class MultipleSigningFileData:
    _signingFileData = ''
    _signingFileName = bytearray()
    _mimeType = ''
    _signCloudMetaData = None

    def __init__(self):
        None

    @property
    def mimeType(self):
        return self._mimeType

    @mimeType.setter
    def mimeType(self, input):
        self._mimeType = input

    @property
    def signingFileName(self):
        return self._signingFileName

    @signingFileName.setter
    def signingFileName(self, input):
        print('setter filename')
        self._signingFileName = input

    @property
    def signingFileData(self):
        return self._signingFileData

    @signingFileData.setter
    def signingFileData(self, input):
        self._signingFileData = input

    @property
    def signCloudMetaData(self):
        return self._signCloudMetaData

    @signCloudMetaData.setter
    def signCloudMetaData(self, input):
        self._signCloudMetaData = input
