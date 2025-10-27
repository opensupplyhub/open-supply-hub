import COLOURS from '../../../../../util/COLOURS';

const eligibilityStepStyles = theme =>
    Object.freeze({
        titleSection: Object.freeze({
            fontSize: '36px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.unit,
            marginBottom: theme.spacing.unit * 3,
        }),
        titleIcon: Object.freeze({
            fontSize: '1.25rem',
        }),
        title: Object.freeze({
            fontSize: '24px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
        }),
        accountInfoSection: Object.freeze({
            backgroundColor: '#f9fafb',
            border: '1px solid #e5e7eb',
            padding: theme.spacing.unit * 1.5,
            marginBottom: theme.spacing.unit * 1.5,
        }),
        accountInfoBox: Object.freeze({
            backgroundColor: '#ffffff',
            border: '1px solid #e5e7eb',
            padding: theme.spacing.unit * 1.5,
            marginBottom: theme.spacing.unit * 1.5,
        }),
        accountInfoRow: Object.freeze({
            fontSize: '14px',
            marginBottom: theme.spacing.unit,
            '&:last-child': {
                marginBottom: 0,
            },
        }),
        accountInfoLabel: Object.freeze({
            color: COLOURS.DARK_GREY,
            fontWeight: theme.typography.fontWeightMedium,
        }),
        accountInfoValue: Object.freeze({
            color: '#111827',
            fontWeight: theme.typography.fontWeightMedium,
            marginLeft: theme.spacing.unit,
        }),
        sectionTitle: Object.freeze({
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
            marginBottom: theme.spacing.unit * 1.5,
        }),
        selectWrapper: Object.freeze({
            marginBottom: 0,
        }),
        dialogTitle: Object.freeze({
            textAlign: 'center',
        }),
        dialogBodyText: Object.freeze({
            textAlign: 'center',
            fontSize: '16px',
        }),
        dialogActions: Object.freeze({
            justifyContent: 'center',
            padding: theme.spacing.unit * 2,
        }),
        buttonContainer: Object.freeze({
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: theme.spacing.unit * 3,
        }),
        backButton: Object.freeze({
            border: `1px solid ${COLOURS.GREY}`,
            backgroundColor: '#ffffff',
            padding: `${theme.spacing.unit}px ${theme.spacing.unit * 3}px`,
            fontSize: '14px',
            fontWeight: theme.typography.fontWeightSemiBold,
            textTransform: 'uppercase',
            '&:hover': {
                backgroundColor: '#f9fafb',
            },
        }),
        continueButton: Object.freeze({
            backgroundColor: '#facc15',
            color: '#000000',
            padding: `${theme.spacing.unit}px ${theme.spacing.unit * 2}px`,
            fontSize: '14px',
            fontWeight: theme.typography.fontWeightSemiBold,
            textTransform: 'none',
            '&:hover': {
                backgroundColor: '#eab308',
            },
        }),
    });

export default eligibilityStepStyles;
