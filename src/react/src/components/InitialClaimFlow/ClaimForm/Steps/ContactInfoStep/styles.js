import COLOURS from '../../../../../util/COLOURS';

const formLabel = Object.freeze({
    margin: '24px 0 8px 0',
    fontSize: '21px',
    fontWeight: 600,
});

const contactInfoStepStyles = theme =>
    Object.freeze({
        formLabel: Object.freeze({
            ...formLabel,
        }),
        formLabelRoot: Object.freeze({
            ...formLabel,
            marginTop: 0,
        }),
        fieldContainer: Object.freeze({
            position: 'relative',
            maxWidth: '528px',
            [theme.breakpoints.down('md')]: {
                maxWidth: '100%',
            },
        }),
        boxWarningText: {
            fontSize: '18px',
            display: 'inline-flex',
            alignItems: 'center',
        },
        warningIcon: {
            color: COLOURS.MATERIAL_RED,
            marginRight: theme.spacing.unit,
            fontSize: 16,
            marginTop: '2px',
        },
        boxWarningTextIcon: {
            display: 'inline-flex',
            alignItems: 'center',
            marginRight: theme.spacing.unit,
        },
        boxWarningContainer: {
            backgroundColor: COLOURS.LIGHT_RED,
            padding: theme.spacing.unit * 1.5,
            display: 'flex',
            alignItems: 'center',
            marginTop: '20px',
        },
        // OLD STYLES
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
            fontSize: '24px',
            fontWeight: theme.typography.fontWeightSemiBold,
            marginBottom: theme.spacing.unit * 1.5,
        }),
        sectionDescription: Object.freeze({
            margin: '0 0 20px 0',
            fontSize: '18px',
        }),
        sectionTitleContainer: Object.freeze({
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginTop: `20px`,
        }),
        separator: {
            margin: '40px 0 15px 0',
            color: COLOURS.BLACK,
        },
        accountInfoSection: Object.freeze({
            backgroundColor: COLOURS.LIGHTEST_GREY,
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            padding: theme.spacing.unit * 1.5,
            marginBottom: theme.spacing.unit * 1.5,
        }),
        accountInfoBox: Object.freeze({
            backgroundColor: COLOURS.WHITE,
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
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
            color: COLOURS.ALMOST_BLACK,
            fontWeight: theme.typography.fontWeightMedium,
            marginLeft: theme.spacing.unit,
        }),
        selectWrapper: Object.freeze({
            marginBottom: '18px',
        }),
        gridSpacing: Object.freeze({
            marginTop: theme.spacing.unit * 2,
        }),
        infoAlert: Object.freeze({
            backgroundColor: COLOURS.AMBER_50,
            border: `1px solid ${COLOURS.AMBER_300}`,
            borderRadius: 4,
            padding: theme.spacing.unit * 1.5,
            marginTop: theme.spacing.unit * 2,
            color: COLOURS.AMBER_800,
        }),
        infoAlertInner: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            gap: theme.spacing.unit,
        }),
        publicContactBox: Object.freeze({
            backgroundColor: COLOURS.AMBER_50,
            border: `1px solid ${COLOURS.AMBER_300}`,
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
            padding: '2px 6px',
            borderRadius: 9999,
            fontSize: '10px',
            fontWeight: 700,
            color: '#ffffff',
            backgroundImage: `linear-gradient(to right, ${COLOURS.PURPLE_GRADIENT_FROM}, ${COLOURS.PINK_GRADIENT_TO})`,
            cursor: 'pointer',
            position: 'absolute',
            top: 57,
            right: 13,
            zIndex: 2,
        }),
        // TODO: use globally
        notchedOutlineStyles: Object.freeze({
            borderRadius: 0,
        }),
        errorOutlineStyles: Object.freeze({
            borderColor: COLOURS.RED,
        }),
        errorWrapStyles: Object.freeze({
            marginTop: '8px',
        }),
        errorStyles: Object.freeze({
            color: COLOURS.RED,
        }),
        inputStyles: Object.freeze({
            backgroundColor: COLOURS.WHITE,
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
            lineHeight: '22px',
            padding: '16px',
        }),
        importantNotice: Object.freeze({
            backgroundColor: '#fff3e0',
            border: '1px solid #ffb74d',
            borderRadius: '4px',
            padding: theme.spacing.unit * 2,
            marginTop: theme.spacing.unit * 2,
            display: 'flex',
            alignItems: 'flex-start',
        }),
        noticeIcon: Object.freeze({
            color: '#f57c00',
            marginRight: theme.spacing.unit,
            fontSize: '1.2rem',
        }),
        noticeText: Object.freeze({
            fontSize: '0.875rem',
            lineHeight: 1.5,
        }),
    });

export default contactInfoStepStyles;
