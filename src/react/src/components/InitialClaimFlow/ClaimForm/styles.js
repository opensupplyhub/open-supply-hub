import COLOURS from '../../../util/COLOURS';
import { HEADER_HEIGHT } from '../../../util/constants';

export const selectStyles = Object.freeze({
    fontSize: '18px',
    fontWeight: '600',
});

export const claimFormStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            background: theme.palette.background.grey,
            padding: '48px 5% 120px 5%',
        }),
        innerContainer: Object.freeze({
            marginTop: '48px',
            backgroundColor: COLOURS.WHITE,
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            display: 'flex',
            flexDirection: 'column',
            borderRadius: '0',
        }),
        paper: Object.freeze({
            backgroundColor: COLOURS.WHITE,
            boxShadow: 'none',
            borderRadius: 0,
            marginTop: '32px',
            padding: '40px 110px 0 110px',
            [theme.breakpoints.down('lg')]: {
                padding: '40px 4% 0 4%',
            },
            [theme.breakpoints.down('sm')]: {
                padding: '24px 4% 0 4%',
            },
        }),
        title: Object.freeze({
            fontSize: '56px',
            fontWeight: 900,
            color: COLOURS.JET_BLACK,
            marginBottom: theme.spacing.unit,
            textAlign: 'center',
            [theme.breakpoints.down('sm')]: {
                fontSize: '36px',
            },
        }),
        description: Object.freeze({
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
            margin: '24px 0 32px 0',
            textAlign: 'center',
        }),
        navigationButtons: Object.freeze({
            justifyContent: 'center',
            gap: '24px',
            padding: '48px 0',
            [theme.breakpoints.down('sm')]: {
                flexDirection: 'column',
                gap: '12px',
            },
        }),
        buttonBack: Object.freeze({
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
        buttonPrimary: Object.freeze({
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
        titleStyles: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            fontSize: '36px',
            lineHeight: '40px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
            marginBottom: theme.spacing.unit * 2,
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
        popupButtonStyles: Object.freeze({
            fontWeight: 'bold',
            margin: '10px',
            backgroundColor: theme.palette.action.main,
            color: theme.palette.common.black,
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
        form: Object.freeze({
            padding: '0',
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
            gap: '24px',
            [theme.breakpoints.down('sm')]: {
                flexDirection: 'column',
                gap: '12px',
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
        boxWarningContainer: Object.freeze({
            maxWidth: '1071px',
            boxSizing: 'border-box',
            backgroundColor: COLOURS.LIGHT_RED,
            padding: theme.spacing.unit * 1.5,
            display: 'flex',
            alignItems: 'center',
            marginTop: '20px',
        }),
        boxWarningText: Object.freeze({
            fontSize: '18px',
            display: 'inline-flex',
            alignItems: 'center',
        }),
        warningIcon: Object.freeze({
            color: COLOURS.MATERIAL_RED,
            marginRight: theme.spacing.unit,
            fontSize: 16,
            marginTop: '2px',
        }),
        boxWarningTextIcon: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            marginRight: theme.spacing.unit,
        }),
    });

export default claimFormStyles;
