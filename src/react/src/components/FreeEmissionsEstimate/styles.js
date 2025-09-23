import {
    claimedFacilitiesDetailsStyles,
    textFieldErrorStyles,
} from '../../util/styles.js';

export const freeEmissionsEstimateStyles = {
    ...textFieldErrorStyles(),
    ...claimedFacilitiesDetailsStyles(),
    emissionsSection: {
        background: 'linear-gradient(to right, #f0fdf4, #eff6ff)',
        padding: '24px',
        borderRadius: '8px',
        border: '1px solid #bbf7d0',
        marginTop: '16px',
    },
    sectionTitle: {
        display: 'flex',
        alignItems: 'center',
        marginBottom: '8px',
        fontSize: '18px',
        fontWeight: 600,
    },
    sectionDescription: {
        marginBottom: '24px',
        color: '#64748b',
        fontSize: '14px',
        lineHeight: '1.5',
    },
    fieldLabel: {
        fontWeight: 500,
    },
    energyConsumptionTitle: {
        fontWeight: 500,
        marginBottom: '16px',
    },
};

export const energySourceInputStyles = {
    energyCheckbox: {
        minWidth: '140px',
    },
    unitText: {
        minWidth: '50px',
        marginLeft: '8px',
        fontSize: '14px',
        color: '#64748b',
    },
};
