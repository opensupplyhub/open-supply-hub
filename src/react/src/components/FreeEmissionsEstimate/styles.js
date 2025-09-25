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

export const monthYearPickerStyles = {
    monthYearPickerLabel: {
        marginBottom: '8px',
        fontWeight: 500,
    },
};

export const infiniteScrollYearDropdownStyles = {
    loadingItem: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '12px 16px',
        minHeight: '48px',
    },
    loadingSpinner: {
        marginRight: '8px',
    },
    loadingText: {
        color: '#64748b',
        fontStyle: 'italic',
    },
    endItem: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '12px 16px',
        backgroundColor: '#f8fafc',
    },
    endText: {
        color: '#64748b',
        fontStyle: 'italic',
        fontSize: '12px',
    },
};
