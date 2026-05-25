import { shape, string } from 'prop-types';

export const DATA_PARTNERS = 'DATA_PARTNERS';

export const contributorOptionPropType = shape({
    groupLabel: string.isRequired,
    label: string.isRequired,
    value: string.isRequired,
});
