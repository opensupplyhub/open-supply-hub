import COLOURS from '../../../../../util/COLOURS';

const contactInfoStepStyles = theme =>
    Object.freeze({
        // Copied base styles from EligibilityStep with minimal extensions
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
        sectionTitle: Object.freeze({
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
            marginBottom: theme.spacing.unit * 1.5,
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
        selectWrapper: Object.freeze({
            marginBottom: 0,
        }),
        gridSpacing: Object.freeze({
            marginTop: theme.spacing.unit * 2,
        }),
        textField: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
        }),
        infoAlert: Object.freeze({
            backgroundColor: '#fffbeb',
            border: '1px solid #fde68a',
            borderRadius: 4,
            padding: theme.spacing.unit * 1.5,
            marginTop: theme.spacing.unit * 2,
            color: '#92400e',
        }),
        infoAlertInner: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            gap: theme.spacing.unit,
        }),
        publicContactBox: Object.freeze({
            backgroundColor: '#fffbeb',
            border: '1px solid #fde68a',
            borderRadius: 4,
            padding: theme.spacing.unit * 1.5,
            marginTop: theme.spacing.unit * 2,
            marginBottom: theme.spacing.unit * 2,
        }),
        publicContactRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: theme.spacing.unit * 2,
        }),
        helperTextSmall: Object.freeze({
            fontSize: '12px',
            color: COLOURS.DARK_GREY,
        }),
        labelRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.unit,
            marginBottom: theme.spacing.unit * 0.5,
        }),
        fieldLabel: Object.freeze({
            fontSize: '14px',
            fontWeight: theme.typography.fontWeightMedium,
        }),
        betaBadge: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: theme.spacing.unit / 2,
            padding: '2px 6px',
            borderRadius: 9999,
            fontSize: '10px',
            fontWeight: 700,
            color: '#ffffff',
            backgroundImage: 'linear-gradient(to right, #a855f7, #ec4899)',
            cursor: 'pointer',
            marginLeft: theme.spacing.unit,
        }),
    });

export default contactInfoStepStyles;
