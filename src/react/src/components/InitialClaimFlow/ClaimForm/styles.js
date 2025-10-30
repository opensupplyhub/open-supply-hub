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

export default claimFormStyles;
