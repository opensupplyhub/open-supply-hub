import { preparePartnerFields } from '../../../PartnerFields/PartnerFieldsSection/utils.jsx';

/**
 * The API returns all configured partner field groups regardless of whether
 * the current facility actually has data for them. Without filtering, the UI
 * would display empty group sections. This pairs the facility's actual partner
 * field data with only the groups that contain at least one matching field.
 *
 * @param {Object} facilityData - The facility data from the API.
 * @param {Array} groups - The partner field groups from the API.
 * @returns {Object} An object containing the partner fields and groups.
 */
export default function getPartnerFieldsAndGroups(facilityData, groups) {
    const partnerFields = preparePartnerFields(facilityData) ?? [];
    const availableFieldNames = new Set(partnerFields.map(f => f.fieldName));
    const partnerGroups = groups.filter(group =>
        group.partner_fields.some(name => availableFieldNames.has(name)),
    );

    return { partnerFields, partnerGroups };
}
