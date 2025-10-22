import COLOURS from '../../../util/COLOURS';
import { HEADER_HEIGHT } from '../../../util/constants';

const claimFormStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: '#F9F7F7',
            padding: '48px 0 120px 0',
        }),
        innerContainer: Object.freeze({
            maxWidth: '896px',
            margin: '0 auto',
        }),
        paper: Object.freeze({
            padding: '40px 40px',
            backgroundColor: COLOURS.WHITE,
            boxShadow: 'none',
            borderRadius: 0,
            marginTop: '32px',
        }),
        title: Object.freeze({
            marginBottom: '48px',
            fontSize: '56px',
            fontWeight: 900,
            lineHeight: '60px',
            textAlign: 'center',
            color: COLOURS.JET_BLACK,
        }),
        description: Object.freeze({
            marginBottom: '24px',
            fontSize: '18px',
            fontWeight: 600,
            textAlign: 'center',
        }),
        navigationButtons: Object.freeze({
            justifyContent: 'space-between',
            padding: '48px 0',
        }),
        buttonBack: Object.freeze({
            width: '200px',
            height: '49px',
            borderRadius: 0,
            textTransform: 'none',
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightExtraBold,
            border: '1px solid #0D1128',
        }),
        buttonPrimary: Object.freeze({
            width: 'fit-content',
            height: '49px',
            borderRadius: 0,
            textTransform: 'none',
            backgroundColor: theme.palette.action.main,
            color: theme.palette.common.black,
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightExtraBold,
            boxShadow: 'none',
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
            '&:disabled': {
                backgroundColor: COLOURS.GREY,
                color: COLOURS.DARK_GREY,
                cursor: 'not-allowed',
            },
        }),
        titleStyles: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            fontSize: '36px',
            lineHeight: '40px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
        }),
        titleStyles: Object.freeze({
            fontSize: '36px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
            gap: '5px',
            display: 'flex',
            alignItems: 'center',
        }),
        sectionDescription: Object.freeze({
            fontSize: '18px',
            fontWeight: 500,
            margin: '0 0 20px 0',
            color: COLOURS.DARK_GREY,
        }),
        loadingContainer: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: `calc(100vh - ${HEADER_HEIGHT}px)`,
        }),
    });

const eligibilityStepStyles = theme =>
    Object.freeze({
        card: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            border: `1px solid ${COLOURS.GREY}`,
        }),
        content: Object.freeze({
            padding: theme.spacing.unit * 3,
        }),
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
            fontSize: '16px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
            color: '#111827',
            marginBottom: theme.spacing.unit * 2,
        }),
        selectWrapper: Object.freeze({
            marginBottom: 0,
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
            '&:disabled': {
                backgroundColor: '#facc15',
                opacity: 0.5,
            },
        }),
    });

export { claimFormStyles, eligibilityStepStyles };
