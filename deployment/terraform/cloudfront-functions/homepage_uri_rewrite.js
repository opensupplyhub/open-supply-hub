function handler(event) {
    var request = event.request;
    var qs = request.querystring;

    // Any query params at / indicate a React app request (embedded map,
    // contributor filter, search, etc.). Redirect to /map preserving the
    // full query string so existing URLs continue to work without any
    // changes on the customer side.
    //
    // In CloudFront Functions runtime 1.0, request.querystring is an object
    // ({ key: { value: "..." } }) not a string, so we serialize it manually.
    // Multi-value params (e.g. ?country=US&country=UK) are stored as
    // { multiValue: [{ value: "US" }, { value: "UK" }] } and expanded here.
    var keys = Object.keys(qs);
    if (keys.length > 0) {
        var parts = [];
        for (var i = 0; i < keys.length; i++) {
            var key = keys[i];
            var param = qs[key];
            if (param.multiValue) {
                for (var j = 0; j < param.multiValue.length; j++) {
                    parts.push(key + "=" + param.multiValue[j].value);
                }
            } else {
                parts.push(key + "=" + param.value);
            }
        }
        return {
            statusCode: 302,
            statusDescription: "Found",
            headers: {
                location: { value: "/map?" + parts.join("&") },
            },
        };
    }

    request.uri = "/home-page";
    return request;
}
