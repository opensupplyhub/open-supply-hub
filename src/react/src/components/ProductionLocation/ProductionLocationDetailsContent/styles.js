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
        /*
        The OS ID and the data labels legend share a row (OSDEV-3239). It is
        laid out with the same Grid container, spacing and breakpoints as the
        General Information / map row below, so the two panels line up with the
        columns under them at every width rather than only looking close.

        Each panel is its own card here, so the item stretches its child to the
        full height of the row: side by side, two cards of different heights
        would leave a ragged bottom edge.
        */
        identityRowItem: Object.freeze({
            display: 'flex',
            paddingBottom: `0px !important`,
            '& > *': Object.freeze({
                flex: 1,
                minWidth: 0,
            }),
            [theme.breakpoints.down('sm')]: {
                maxWidth: '100%',
            },
        }),
    });
