
import base64
import json
import six


def _parse_pem_key(raw_key_input):
    """Identify and extract PEM keys.

    Determines whether the given key is in the format of PEM key, and extracts
    the relevant part of the key if it is.

    Args:
        raw_key_input: The contents of a private key file (either PEM or
                       PKCS12).

    Returns:
        string, The actual key if the contents are from a PEM file, or
        else None.
    """
    offset = raw_key_input.find(b'-----BEGIN ')
    if offset != -1:
        return raw_key_input[offset:]


def _json_encode(data):
    return json.dumps(data, separators=(',', ':'))


def _to_bytes(value, encoding='ascii'):
    """Converts a string value to bytes, if necessary.

    Unfortunately, ``six.b`` is insufficient for this task since in
    Python2 it does not modify ``unicode`` objects.

    Args:
        value: The string/bytes value to be converted.
        encoding: The encoding to use to convert unicode to bytes. Defaults
                  to "ascii", which will not allow any characters from ordinals
                  larger than 127. Other useful values are "latin-1", which
                  which will only allows byte ordinals (up to 255) and "utf-8",
                  which will encode any unicode that needs to be.

    Returns:
        The original value converted to bytes (if unicode) or as passed in
        if it started out as bytes.

    Raises:
        ValueError if the value could not be converted to bytes.
    """
    result = (value.encode(encoding)
              if isinstance(value, six.text_type) else value)
    if isinstance(result, six.binary_type):
        return result
    else:
        raise ValueError('%r could not be converted to bytes' % (value,))


def _from_bytes(value):
    """Converts bytes to a string value, if necessary.

    Args:
        value: The string/bytes value to be converted.

    Returns:
        The original value converted to unicode (if bytes) or as passed in
        if it started out as unicode.

    Raises:
        ValueError if the value could not be converted to unicode.
    """
    result = (value.decode('utf-8')
              if isinstance(value, six.binary_type) else value)
    if isinstance(result, six.text_type):
        return result
    else:
        raise ValueError('%r could not be converted to unicode' % (value,))


def _urlsafe_b64encode(raw_bytes):
    raw_bytes = _to_bytes(raw_bytes, encoding='utf-8')
    return base64.urlsafe_b64encode(raw_bytes).rstrip(b'=')


def _urlsafe_b64decode(b64string):
    # Guard against unicode strings, which base64 can't handle.
    b64string = _to_bytes(b64string)
    padded = b64string + b'=' * (4 - len(b64string) % 4)
    return base64.urlsafe_b64decode(padded)


def _b64encode(raw_bytes):
    raw_bytes = _to_bytes(raw_bytes, encoding='utf-8')
    return base64.b64encode(raw_bytes)


def _b64decode(b64string):
    base64_bytes = b64string.encode('utf-8')
    return base64.decodebytes(base64_bytes)
