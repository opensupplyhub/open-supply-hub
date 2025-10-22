import COLOURS from '../../../util/COLOURS';

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
        }),
        sectionTitle: Object.freeze({
            fontSize: '1.5rem',
            fontWeight: 600,
            marginBottom: theme.spacing.unit * 2,
        }),
        sectionDescription: Object.freeze({
            fontSize: '1rem',
            color: COLOURS.DARK_GREY,
            marginBottom: theme.spacing.unit * 3,
        }),
        loadingContainer: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '400px',
        }),
        errorContainer: Object.freeze({
            padding: theme.spacing.unit * 3,
            textAlign: 'center',
        }),
        errorText: Object.freeze({
            color: theme.palette.error.main,
            marginBottom: theme.spacing.unit * 2,
        }),
        errorButton: Object.freeze({
            marginTop: theme.spacing.unit * 2,
        }),
    });

export default claimFormStyles;
