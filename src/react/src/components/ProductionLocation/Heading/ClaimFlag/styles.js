import COLOURS from '../../../../util/COLOURS';

export default theme => {
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        root: {
            marginTop: spacing * 3,
            marginBottom: spacing * 3,
            flexDirection: 'column',
        },
        rootClaimed: {
            // No full-width background; compact banner like mockup
        },
        rootPending: {
            // No full-width background; compact banner like mockup
        },
        rootUnclaimed: {
            // No full-width background; compact banner like mockup
        },
        row: {
            display: 'flex',
            flexDirection: 'row',
            flexWrap: 'nowrap',
            alignItems: 'center',
        },
        iconClaimed: {
            color: COLOURS.DARK_GREEN,
            flexShrink: 0,
            fontSize: 24,
            marginRight: theme.spacing.unit * 1.5,
        },
        iconPending: {
            color: COLOURS.NAVIGATION,
            flexShrink: 0,
            fontSize: 24,
            marginRight: theme.spacing.unit * 1.5,
        },
        iconUnclaimed: {
            color: COLOURS.DARK_GREY,
            flexShrink: 0,
            fontSize: 24,
            marginRight: theme.spacing.unit * 1.5,
        },
        statusText: {
            fontSize: '1.125rem',
            fontWeight: 600,
        },
        statusTextClaimed: {
            color: COLOURS.DARK_GREEN,
        },
        statusTextPending: {
            color: COLOURS.DARK_AMBER,
        },
        statusTextUnclaimed: {
            color: theme.palette.text.primary,
        },
        infoButton: {
            marginLeft: spacing * 0.5,
            padding: spacing * 0.5,
            color: theme.palette.text.secondary,
            '&:hover': {
                color: theme.palette.text.primary,
                backgroundColor: theme.palette.action.hover,
            },
        },
        subtitle: {
            marginTop: 0,
            fontSize: '1rem',
            color: theme.palette.text.secondary,
        },
        subtitleHighlight: {
            fontWeight: 500,
            color: theme.palette.text.primary,
            display: 'inline',
        },
        subtitleSameLine: {
            whiteSpace: 'nowrap',
        },
        link: {
            color: theme.palette.primary.main,
        },
        statusContent: {
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            minWidth: 0,
            flex: 1,
        },
        statusRow: {
            display: 'flex',
            flexWrap: 'nowrap',
        },
    });
};
