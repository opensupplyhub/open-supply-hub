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
        eligibilityStepContainer: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
        }),
        titleIcon: Object.freeze({
            fontSize: '1.25rem',
        }),
        title: Object.freeze({
            fontSize: '24px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
        }),
        accountInfoSection: Object.freeze({
            padding: '0 0 40px 0',
        }),
        accountInfoBox: Object.freeze({
            display: 'flex',
            justifyContent: 'flex-start',
        }),
        accountInfoRow: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            fontSize: '18px',
            marginRight: '50px',
        }),
        accountInfoLabel: Object.freeze({
            color: COLOURS.DARK_GREY,
            fontWeight: theme.typography.fontWeightBold,
            fontSize: '16px',
            marginBottom: '4px',
        }),
        accountInfoValue: Object.freeze({
            color: COLOURS.ALMOST_BLACK,
            fontWeight: theme.typography.fontWeightBold,
        }),
        sectionTitle: Object.freeze({
            fontSize: '18px',
            color: theme.palette.text.primary,
            fontWeight: theme.typography.fontWeightSemiBold,
            margin: '0 0 8px 0',
        }),
        selectWrapper: Object.freeze({
            marginBottom: 0,
            maxWidth: '528px',
            [theme.breakpoints.down('md')]: {
                maxWidth: '100%',
            },
        }),
        sectionHeading: Object.freeze({
            fontSize: '24px',
            fontWeight: theme.typography.fontWeightSemiBold,
            marginBottom: theme.spacing.unit * 1.5,
        }),
        dialogTitle: Object.freeze({
            fontSize: '36px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
            display: 'flex',
            alignItems: 'center',
            textAlign: 'center',
            justifyContent: 'center',
        }),
        dialogBodyText: Object.freeze({
            textAlign: 'center',
            fontSize: '18px',
        }),
        dialogActions: Object.freeze({
            justifyContent: 'center',
            padding: theme.spacing.unit * 2,
        }),
        buttonContainer: Object.freeze({
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: theme.spacing.unit * 3,
            [theme.breakpoints.down('sm')]: {
                flexDirection: 'column',
                padding: '24px 0',
            },
        }),
        backButton: Object.freeze({
            width: '200px',
            height: '49px',
            borderRadius: 0,
            textTransform: 'none',
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightExtraBold,
            border: '1px solid #0D1128',
            [theme.breakpoints.down('sm')]: {
                width: '100%',
            },
        }),
        sectionTitleRequired: Object.freeze({
            color: theme.palette.error.main,
            fontSize: '21px',
            fontWeight: theme.typography.fontWeightSemiBold,
        }),
        continueButton: Object.freeze({
            height: '49px',
            borderRadius: 0,
            textTransform: 'none',
            backgroundColor: theme.palette.action.main,
            color: theme.palette.common.black,
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightExtraBold,
            width: '200px',
            boxShadow: 'none',
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
            '&:disabled': {
                backgroundColor: COLOURS.GREY,
                color: COLOURS.DARK_GREY,
                cursor: 'not-allowed',
            },
            [theme.breakpoints.down('sm')]: {
                width: '100%',
            },
        }),
        errorWrapStyles: Object.freeze({
            margin: '8px 12px 0 0',
        }),
    });

export default eligibilityStepStyles;
