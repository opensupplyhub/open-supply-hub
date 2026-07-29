function handler(event) {
    var request = event.request;
    var qs = request.querystring;
    // If we add a filter key here, make sure it exists in React frontend code in
    // util/util.js in the createQueryStringFromSearchFilters function.
    var mapParams = new Set([
        "q", "contributors", "lists", "contributor_types", "countries", "statuses",
        "sectors", "parent_company", "facility_type", "processing_type", "product_type",
        "number_of_workers", "native_language_name", "combine_contributors", "boundary",
        "sort_by", "embed", "detail", "partner_contributor"
    ]);

    var keys = Object.keys(qs);
    // If no React app params are present, serve the Craft CMS homepage.
    if (!keys.some(key => mapParams.has(key))) {
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
