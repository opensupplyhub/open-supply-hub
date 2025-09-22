import {
    claimedFacilitiesDetailsStyles,
    textFieldErrorStyles,
} from '../../util/styles.js';

export const freeEmissionsEstimateStyles = {
    ...textFieldErrorStyles(),
    ...claimedFacilitiesDetailsStyles(),
    emissionsSection: {
        background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
        padding: '24px',
        borderRadius: '8px',
        border: '1px solid #bae6fd',
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
};

export const energySourceInputStyles = {
    energyInputContainer: {
        display: 'flex',
        alignItems: 'center',
        marginBottom: '12px',
    },
    energyCheckbox: {
        minWidth: '140px',
    },
    energyInput: {
        flex: 1,
        marginLeft: '12px',
    },
    unitText: {
        minWidth: '50px',
        marginLeft: '8px',
        fontSize: '14px',
        color: '#64748b',
    },
};
