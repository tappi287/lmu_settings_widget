from bottle import hook, response, request, HTTPResponse

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    # 'Access-Control-Allow-Headers': 'X-Token, ...',
    # 'Access-Control-Expose-Headers': 'X-My-Custom-Header, ...',
    # 'Access-Control-Max-Age': '86400',
    # 'Access-Control-Allow-Credentials': 'true',
}


@hook("before_request")
def handle_options():
    if request.method == "OPTIONS":
        # Bypass request routing and immediately return a response
        raise HTTPResponse(headers=cors_headers)


@hook("after_request")
def enable_cors():
    for key, value in cors_headers.items():
        response.set_header(key, value)


def expose_cors_methods():
    pass
