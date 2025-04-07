function handler(event) {
    const response = event.response;
    const headers = response.headers;

    headers["x-frame-options"] = { value: "DENY" };
    headers["content-security-policy"] = { value: "frame-ancestors 'none';" };

    return response;
}
