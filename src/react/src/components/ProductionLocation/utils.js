const getSelectedDrawerField = (fields, fieldKey) =>
    fieldKey
        ? (fields && fields.find(field => field.key === fieldKey)) ?? null
        : null;

/**
 * Maps General Information / map field keys to the fields the v1
 * production-locations API serves them under. The *_source objects carry the
 * attribution of the promoted (highlighted) value computed by the OpenSearch
 * sync pipeline.
 */
const V1_FIELD_MAPPING = Object.freeze({
    name: { valueKey: 'name', sourceKey: 'name_source' },
    address: { valueKey: 'address', sourceKey: 'address_source' },
    sector: { valueKey: 'sector', sourceKey: 'sector_source' },
    parent_company: {
        valueKey: 'parent_company',
        sourceKey: 'parent_company_source',
    },
    product_type: {
        valueKey: 'product_type',
        sourceKey: 'product_type_source',
    },
    facility_type: {
        valueKey: 'location_type',
        sourceKey: 'location_type_source',
    },
    processing_type: {
        valueKey: 'processing_type',
        sourceKey: 'processing_type_source',
    },
    number_of_workers: {
        valueKey: 'number_of_workers',
        sourceKey: 'number_of_workers_source',
    },
    native_language_name: {
        valueKey: 'local_name',
        sourceKey: 'local_name_source',
    },
    rba_id: { valueKey: 'rba_id', sourceKey: 'rba_id_source' },
    duns_id: { valueKey: 'duns_id', sourceKey: 'duns_id_source' },
    lei_id: { valueKey: 'lei_id', sourceKey: 'lei_id_source' },
});

const formatV1Value = (fieldKey, rawValue) => {
    if (rawValue == null) {
        return null;
    }
    if (fieldKey === 'number_of_workers') {
        const { min, max } = rawValue;
        if (min == null && max == null) {
            return null;
        }
        return max === min ? `${max}` : `${min}-${max}`;
    }
    if (Array.isArray(rawValue)) {
        return rawValue.length ? rawValue : null;
    }
    const stringValue = String(rawValue).trim();
    return stringValue || null;
};

/**
 * Returns the highlighted (promoted) value and its attribution for a field
 * from the v1 production-locations document, or null when the document does
 * not cover the field. Documents indexed before the *_source fields were
 * introduced have no attribution objects; those fall back to null so callers
 * keep the legacy behavior.
 */
export const getV1HighlightedField = (v1Data, fieldKey) => {
    const mapping = V1_FIELD_MAPPING[fieldKey];
    if (!v1Data || !mapping) {
        return null;
    }
    const source = v1Data[mapping.sourceKey];
    if (!source || typeof source !== 'object') {
        return null;
    }
    const value = formatV1Value(fieldKey, v1Data[mapping.valueKey]);
    if (!value) {
        return null;
    }
    return {
        value,
        sourceName: source.contributor_name || null,
        userId: source.contributor_id != null ? source.contributor_id : null,
        date: source.contributed_at || null,
        isClaimedData: !!source.is_claimed_data,
    };
};

/**
 * Normalizes a display value (string or array of strings) so the highlighted
 * v1 value can be matched against the corresponding entry in the legacy
 * facilities-API contribution list, tolerating ordering and casing
 * differences.
 */
export const normalizeDisplayValue = value => {
    if (Array.isArray(value)) {
        return [
            ...new Set(
                value.map(entry =>
                    String(entry ?? '')
                        .trim()
                        .toLowerCase(),
                ),
            ),
        ]
            .sort()
            .join('|');
    }
    return String(value ?? '')
        .trim()
        .toLowerCase();
};

export default getSelectedDrawerField;
