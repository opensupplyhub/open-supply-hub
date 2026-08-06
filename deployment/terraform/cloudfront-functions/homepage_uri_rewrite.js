function handler(event) {
    var request = event.request;
    var qs = request.querystring;
    // If we add a filter key here, make sure it exists in React frontend code in
    // util/util.js in the createQueryStringFromSearchFilters function.
    // Note: CloudFront Functions runtime 1.0 does not support Set/Map, so we use
    // a plain object for O(1) key lookup.
    var mapParams = {
        "q": true, "contributors": true, "lists": true, "contributor_types": true,
        "countries": true, "statuses": true, "sectors": true, "parent_company": true,
        "facility_type": true, "processing_type": true, "product_type": true,
        "number_of_workers": true, "native_language_name": true, "combine_contributors": true,
        "boundary": true, "sort_by": true, "embed": true, "detail": true,
        "partner_contributor": true
    };

    var keys = Object.keys(qs);
    // If no React app params are present, serve the Craft CMS homepage.
    if (!keys.some(function(key) { return mapParams[key]; })) {
        request.uri = "/home-page";
        return request;
    }

    // In CloudFront Functions runtime 1.0, request.querystring is an object
    // ({ key: { value: "..." } }) not a string, so we serialize it manually.
    // Multi-value params (e.g. ?country=US&country=UK) are stored as
    // { multiValue: [{ value: "US" }, { value: "UK" }] } and expanded here.
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
