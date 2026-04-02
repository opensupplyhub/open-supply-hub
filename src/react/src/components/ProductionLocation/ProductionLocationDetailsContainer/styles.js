import COLOURS from '../../../util/COLOURS';

export default theme =>
    Object.freeze({
        root: Object.freeze({
            background: theme.palette.background.grey,
            padding: '48px 5% 120px 5%',
            flexWrap: 'nowrap',
            [theme.breakpoints.down('lg')]: {
                padding: '28px 1.5% 60px 1.5%',
            },
            [theme.breakpoints.down('sm')]: {
                flexWrap: 'wrap',
                display: 'flex',
                flexDirection: 'column-reverse',
            },
        }),
        loadingRoot: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '60vh',
            background: theme.palette.background.grey,
        }),
        errorList: Object.freeze({
            listStyle: 'none',
            padding: theme.spacing.unit * 2,
        }),
        errorItem: Object.freeze({
            color: theme.palette.error.main,
            marginBottom: theme.spacing.unit,
        }),
        sidebarContainer: {
            minWidth: '267px',
            [theme.breakpoints.down('sm')]: {
                borderTop: `2px solid ${COLOURS.PURPLE}`,
                paddingTop: '20px',
                marginTop: '20px',
            },
        },
        sidebar: {
            [theme.breakpoints.up('md')]: {
                position: 'sticky',
                top: '10px',
                alignSelf: 'flex-start',
            },
            [theme.breakpoints.up('lg')]: {
                top: '120px',
            },
        },
        backToSearch: {
            display: 'none',
            [theme.breakpoints.up('md')]: {
                display: 'block',
            },
        },
        navBar: {
            [theme.breakpoints.down('sm')]: {
                display: 'none',
            },
        },
    });
