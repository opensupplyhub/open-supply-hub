import COLOURS from '../../../../util/COLOURS';

export default theme =>
    Object.freeze({
        rootClaimed: {
            backgroundColor: COLOURS.GREEN,
            color: '#191919',
            display: 'flex',
            justifyContent: 'center',
        },
        rootPending: {
            backgroundColor: COLOURS.NAVIGATION,
            color: '#191919',
            display: 'flex',
            justifyContent: 'center',
        },
        rootUnclaimed: {
            backgroundColor: COLOURS.LIGHT_RED,
            color: '#191919',
            display: 'flex',
            justifyContent: 'center',
        },
        contentContainer: {
            width: '100%',
            maxWidth: '1072px',
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            paddingRight: theme.spacing.unit,
            paddingBottom: theme.spacing.unit,
        },
        link: {
            color: theme.palette.primary.main,
        },
        itemPadding: {
            paddingLeft: theme.spacing.unit * 3,
            paddingTop: theme.spacing.unit,
            paddingBottom: theme.spacing.unit / 4,
        },
    });
