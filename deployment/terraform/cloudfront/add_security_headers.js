function handler(event) {
    var response = event.response;
    var headers = response.headers;

    headers["x-frame-options"] = { value: "DENY" };
    headers["content-security-policy"] = { value: "frame-ancestors 'none';" };

    return response;
}
