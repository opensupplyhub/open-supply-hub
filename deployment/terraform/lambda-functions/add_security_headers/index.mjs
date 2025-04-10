"use strict";

export const handler = async (event) => {
    const response = event.Records[0].cf.response;
    const headers = response.headers;

    const request = event.Records[0].cf.request;
    const queryString = request.querystring || "";

    if (!queryString.includes("embed=1")) {
        headers["x-frame-options"] = [
            { key: "X-Frame-Options", value: "DENY" },
        ];
        headers["content-security-policy"] = [
            { key: "Content-Security-Policy", value: "frame-ancestors 'none'" },
        ];
    }

    return response;
};
