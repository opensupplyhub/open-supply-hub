import COLOURS from '../../../../util/COLOURS';

const errorStateStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: '#F9F7F7',
            padding: '48px 0 120px 0',
        }),
        paper: Object.freeze({
            padding: '40px 40px',
            backgroundColor: '#FFFFFF',
            boxShadow: 'none',
            borderRadius: 0,
            marginTop: '32px',
        }),
        errorContainer: Object.freeze({
            padding: theme.spacing.unit * 3,
            textAlign: 'center',
        }),
        errorTitle: Object.freeze({
            color: theme.palette.error.main,
            marginBottom: theme.spacing.unit * 2,
            fontSize: '32px',
            fontWeight: 'normal',
        }),
        errorText: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            // fontSize: '18px',
        }),
        buttonContainer: Object.freeze({
            justifyContent: 'center',
            alignItems: 'center',
        }),
        searchButton: Object.freeze({
            width: 'fit-content',
            height: '49px',
            borderRadius: 0,
            textTransform: 'none',
            backgroundColor: theme.palette.action.main,
            color: theme.palette.common.black,
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightExtraBold,
            boxShadow: 'none',
            marginRight: '24px',
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
            '&:disabled': {
                backgroundColor: COLOURS.GREY,
                color: COLOURS.DARK_GREY,
                cursor: 'not-allowed',
            },
        }),
        errorButton: Object.freeze({
            width: 'fit-content',
            height: '49px',
            borderRadius: 0,
            textTransform: 'none',
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightExtraBold,
            border: '1px solid #0D1128',
        }),
    });

export default errorStateStyles;
