# SPDX-License-Identifer: Apache-2.0
import google.protobuf.any_pb2 as AnyPb

URL_PREFIX = "type.googleapis.com/"


def pb_any_unpack(from_, to):
    """
    Unpack the protobuf "any" "from_" message and place the result in the "to" message.
    """
    any = AnyPb.Any()
    any.CopyFrom(from_)
    pb_any_fix_url(any)
    any.Unpack(to)


def pb_any_fix_url(any):
    """
    Fix the type_url of a protobuf Any message.
    If it is missing the URL_PREFIX, add it, otherwise the unpacking will fail.
    io4edge devices do not send the URL_PREFIX.
    """
    if not any.type_url.startswith(URL_PREFIX):
        any.type_url = URL_PREFIX + any.type_url
