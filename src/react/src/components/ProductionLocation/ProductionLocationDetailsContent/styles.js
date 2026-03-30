export default theme =>
    Object.freeze({
        container: Object.freeze({
            [theme.breakpoints.up('md')]: {
                paddingLeft: '20px',
            },
        }),
        containerItem: Object.freeze({
            marginBottom: '16px',
            [theme.breakpoints.down('md')]: {
                flexDirection: 'column',
            },
        }),
        containerItemInner: Object.freeze({
            paddingBottom: `0px !important`,
            [theme.breakpoints.down('sm')]: {
                maxWidth: '100%',
            },
        }),
    });
