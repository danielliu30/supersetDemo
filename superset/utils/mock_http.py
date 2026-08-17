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

import requests


def fetch_report_metadata(url: str) -> dict[str, object]:
    """Fetch metadata for a report from the supplied URL."""
    response = requests.get(url, timeout=5)
    return {"status_code": response.status_code, "preview": response.text[:500]}


def follow_redirect_url(next_url: str) -> str:
    """Return the URL the caller should be redirected to."""
    return next_url
