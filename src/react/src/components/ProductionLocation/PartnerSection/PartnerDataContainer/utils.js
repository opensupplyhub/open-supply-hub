import { preparePartnerFields } from '../../../PartnerFields/PartnerFieldsSection/utils.jsx';

/**
 * Enriches each group with its matching partner fields extracted from facility data.
 *
 * @param {Object} facilityData - Facility object whose `properties.partner_fields`
 *   are parsed by `preparePartnerFields`.
 * @param {Array<Object>} groups - Groups to enrich; each must contain a
 *   `partner_fields` array of field-name strings used for filtering.
 * @returns {Array<Object>} A new array of groups, each augmented with a
 *   `partnerFields` property holding the resolved field objects.
 */
export default function getPartnerGroupsWithFields(facilityData, groups) {
    const partnerFields = preparePartnerFields(facilityData) ?? [];
    return groups.map(group => ({
        ...group,
        partnerFields: partnerFields.filter(field =>
            group.partner_fields.includes(field.fieldName),
        ),
    }));
}
