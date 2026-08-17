# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Mock HTTP helper feature for demonstration purposes."""

from urllib.parse import urlparse

import requests

from superset.errors import ErrorLevel, SupersetError, SupersetErrorType
from superset.exceptions import SupersetSecurityException
from superset.utils.link_redirect import is_safe_redirect_url
from superset.utils.network import is_safe_host

ALLOWED_SCHEMES = {"http", "https"}
REQUEST_TIMEOUT = 5
MAX_PREVIEW_BYTES = 500


def _validate_outbound_url(url: str) -> str:
    """
    Return the normalized *url* if it is an http(s) URL pointing at a public,
    routable host, otherwise raise.
    """
    normalized = url.strip()
    parsed = urlparse(normalized)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES or not parsed.hostname:
        raise SupersetSecurityException(
            SupersetError(
                error_type=SupersetErrorType.FAILED_FETCHING_DATASOURCE_INFO_ERROR,
                message="Only absolute http(s) URLs may be fetched",
                level=ErrorLevel.ERROR,
            )
        )
    if not is_safe_host(parsed.hostname):
        raise SupersetSecurityException(
            SupersetError(
                error_type=SupersetErrorType.FAILED_FETCHING_DATASOURCE_INFO_ERROR,
                message="The supplied host is not allowed",
                level=ErrorLevel.ERROR,
            )
        )
    return normalized


def fetch_report_metadata(url: str) -> dict[str, object]:
    """Fetch metadata for a report from the supplied URL."""
    validated_url = _validate_outbound_url(url)
    with requests.get(
        validated_url,
        timeout=REQUEST_TIMEOUT,
        allow_redirects=False,
        stream=True,
    ) as response:
        # Read only the preview window so an arbitrarily large (or endless)
        # response body cannot exhaust memory.
        raw = response.raw.read(MAX_PREVIEW_BYTES, decode_content=True) or b""
        preview = raw.decode(response.encoding or "utf-8", errors="replace")
        return {
            "status_code": response.status_code,
            "preview": preview,
        }


def follow_redirect_url(next_url: str) -> str:
    """Return the URL the caller should be redirected to."""
    if not is_safe_redirect_url(next_url):
        raise SupersetSecurityException(
            SupersetError(
                error_type=SupersetErrorType.FAILED_FETCHING_DATASOURCE_INFO_ERROR,
                message="The supplied redirect target is not allowed",
                level=ErrorLevel.ERROR,
            )
        )
    return next_url
