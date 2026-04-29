import COLOURS from '../../util/COLOURS';

const cellHeader = theme =>
    Object.freeze({
        fontWeight: '700',
        padding: `0 ${theme.spacing.unit}px`,
        fontSize: '18px',
    });

const cell = theme =>
    Object.freeze({
        fontSize: '18px',
        padding: `0 ${theme.spacing.unit}px`,
        fontWeight: '500',
    });

export default theme => ({
    appGridContainer: {
        justifyContent: 'space-between',
        marginBottom: '30px',
        backgroundColor: COLOURS.WHITE,
        padding: '0 24px',
        [theme.breakpoints.down('sm')]: {
            padding: '0 12px',
        },
    },
    container: {
        padding: '10px 0',
        width: '100%',
    },
    heading: {
        fontWeight: '900',
        fontSize: '28px',
        lineHeight: '28px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        [theme.breakpoints.down('sm')]: {
            fontSize: '22px',
            lineHeight: '24px',
        },
    },
    panelSummary: {
        paddingLeft: 0,
        paddingRight: 0,
    },
    expandIcon: {
        padding: 0,
    },
    panelDetails: {
        padding: 0,
    },
    detailsContent: {
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
    },
    headerRow: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: `${theme.spacing.unit}px 0`,
        [theme.breakpoints.down('sm')]: {
            display: 'none',
        },
    },
    headerDivider: {
        [theme.breakpoints.down('sm')]: {
            display: 'none',
        },
    },
    nameHeader: {
        ...cellHeader(theme),
        flex: 2,
    },
    descriptionHeader: {
        ...cellHeader(theme),
        flex: 5,
    },
    actionHeader: {
        ...cellHeader(theme),
        flex: '0 0 80px',
        textAlign: 'right',
        paddingRight: '17px',
    },
    facilityRow: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: `${theme.spacing.unit}px 0`,
        [theme.breakpoints.down('sm')]: {
            flexDirection: 'column',
            alignItems: 'flex-start',
            gap: '4px',
            padding: `${theme.spacing.unit * 1.5}px 0`,
        },
    },
    nameCell: {
        flex: 2,
        ...cell(theme),
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        [theme.breakpoints.down('sm')]: {
            flex: '1 1 100%',
            overflow: 'visible',
            textOverflow: 'clip',
            whiteSpace: 'normal',
            padding: 0,
            fontSize: '16px',
        },
    },
    descriptionCell: {
        flex: 5,
        ...cell(theme),
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        [theme.breakpoints.down('sm')]: {
            flex: '1 1 100%',
            overflow: 'visible',
            textOverflow: 'clip',
            whiteSpace: 'normal',
            padding: 0,
            fontSize: '16px',
        },
    },
    actionCell: {
        flex: '0 0 80px',
        textAlign: 'right',
        ...cell(theme),
        [theme.breakpoints.down('sm')]: {
            flex: '0 0 auto',
            alignSelf: 'flex-end',
            textAlign: 'right',
            padding: `${theme.spacing.unit}px 0 0 0`,
        },
    },
    mobileLabel: {
        display: 'none',
        [theme.breakpoints.down('sm')]: {
            display: 'inline',
            fontWeight: '700',
            marginRight: '4px',
        },
    },
    centeredGrid: {
        marginLeft: 'auto',
        marginRight: 'auto',
    },
    loadMoreContainer: {
        display: 'flex',
        justifyContent: 'center',
        padding: `${theme.spacing.unit * 2}px 0`,
    },
    loadMoreButton: {
        minWidth: '100px',
    },
    loaderContainer: {
        minHeight: '60px',
    },
    viewButton: {
        fontSize: '14px',
    },
});
