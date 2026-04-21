export default theme =>
    Object.freeze({
        root: {
            overflowWrap: 'anywhere',
            fontWeight: 500,
            fontSize: '16px',
            lineHeight: '19px',
            paddingTop: theme.spacing.unit,
            '& *': {
                margin: 0,
                padding: 0,
            },
        },
    });
