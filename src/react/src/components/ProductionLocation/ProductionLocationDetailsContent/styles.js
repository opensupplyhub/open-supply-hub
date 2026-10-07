export default theme =>
    Object.freeze({
        container: Object.freeze({
            [theme.breakpoints.up('md')]: {
                paddingLeft: '20px',
            },
        }),
        /*
        OS ID takes two thirds of the row and the data labels legend one third,
        so the legend reads as a footnote to the ID instead of a page section
        of its own (OSDEV-3239). Stacks below md.
        */
        identityRow: Object.freeze({
            display: 'grid',
            gridTemplateColumns: '1fr',
            marginBottom: '16px',
            [theme.breakpoints.up('md')]: {
                gridTemplateColumns: '2fr 1fr',
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
