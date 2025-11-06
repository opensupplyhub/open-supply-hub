export const labelStyles = Object.freeze({
    labelContainer: Object.freeze({
        flexWrap: 'nowrap',
        marginBottom: '5px',
    }),
    label: Object.freeze({
        marginRight: '8px',
        fontWeight: 600,
        fontSize: '18px',
        whiteSpace: 'nowrap',
    }),
    tooltipContainer: Object.freeze({
        alignItems: 'center',
        marginTop: '3px',
    }),
    tooltipPopper: Object.freeze({
        opacity: 1,
        maxWidth: '512px',
    }),
    tooltip: Object.freeze({
        marginLeft: '8px',
        marginBottom: '4px',
        padding: '3px 12px',
        backgroundColor: '#ffffff',
        color: '#000000',
        fontSize: '17px',
        fontWeight: 500,
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
        border: '1px solid #d1d5db',
        maxWidth: 'fit-content',
        letterSpacing: '0.2px',
    }),
    helpIcon: Object.freeze({
        fontSize: '17px',
        color: '#64748B',
        cursor: 'pointer',
    }),
});

export const freeEmissionsEstimateStyles = Object.freeze({
    emissionsSection: Object.freeze({
        background: 'linear-gradient(to right, #f0fdf4, #eff6ff)',
        padding: '19px 24px 24px 24px',
        borderRadius: '8px',
        border: '1px solid #bbf7d0',
        marginTop: '16px',
    }),
    sectionTitle: Object.freeze({
        marginBottom: '3px',
        fontSize: '22px',
        fontWeight: 700,
    }),
    sectionDescription: Object.freeze({
        marginBottom: '17px',
        color: '#64748b',
        fontSize: '18px',
        lineHeight: '1.5',
    }),
    energyConsumptionTitle: Object.freeze({
        fontWeight: 600,
        fontSize: '18px',
        marginBottom: '16px',
    }),
    datePickerContainer: Object.freeze({
        marginBottom: 0,
    }),
    estimatedAnnualThroughputContainer: Object.freeze({
        marginBottom: '10px',
    }),
});

export const energySourceInputStyles = Object.freeze({
    unitText: Object.freeze({
        minWidth: '50px',
        marginLeft: '8px',
        fontSize: '18px',
        fontWeight: 600,
        color: '#64748b',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    }),
    energySourceInputRoot: Object.freeze({
        boxSizing: 'border-box',
    }),
    energySourceInputContainer: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    }),
    checkboxLabel: Object.freeze({
        fontSize: '18px',
        fontWeight: 600,
    }),
});

export const yearPickerStyles = Object.freeze({
    loadingItem: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '12px 16px',
        minHeight: '48px',
    }),
    loadingSpinner: Object.freeze({
        marginRight: '8px',
    }),
    loadingText: Object.freeze({
        color: '#64748b',
        fontStyle: 'italic',
    }),
    endItem: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '12px 16px',
        backgroundColor: '#f8fafc',
    }),
    endText: Object.freeze({
        color: '#64748b',
        fontStyle: 'italic',
        fontSize: '12px',
    }),
});
