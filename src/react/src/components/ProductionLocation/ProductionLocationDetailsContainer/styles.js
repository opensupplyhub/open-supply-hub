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
    });
