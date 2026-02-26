import COLOURS from '../../../../util/COLOURS';
import { getTypographyStyles } from '../../../../util/typographyStyles';

export default theme => {
    const spacing = theme.spacing.unit ?? 8;
    const typography = getTypographyStyles(theme);
    return Object.freeze({
        ...typography,
        root: {
            marginTop: spacing * 3,
            marginBottom: spacing * 3,
            flexDirection: 'column',
            padding: 0,
            marginLeft: 0,
            marginRight: 0,
        },
        row: {
            display: 'flex',
            flexDirection: 'row',
            flexWrap: 'nowrap',
            alignItems: 'center',
            marginLeft: 0,
            marginRight: 0,
        },
        iconColumn: {
            flex: '0 0 36px',
            width: 36,
            minWidth: 36,
            maxWidth: 36,
            boxSizing: 'border-box',
            paddingRight: theme.spacing.unit * 1.5,
            paddingLeft: 0,
            paddingTop: 0,
            paddingBottom: 0,
            margin: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
        },
        iconClaimed: {
            color: COLOURS.DARK_GREEN,
            fontSize: 24,
        },
        iconPending: {
            color: COLOURS.NAVIGATION,
            fontSize: 24,
        },
        iconUnclaimed: {
            color: COLOURS.DARK_GREY,
            fontSize: 24,
        },
        statusText: Object.freeze({
            ...typography.formLabelTight,
        }),
        statusTextClaimed: {
            color: COLOURS.DARK_GREEN,
        },
        statusTextPending: {
            color: theme.palette.text.primary,
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
        subtitle: Object.freeze({
            ...typography.bodyText,
            marginTop: 0,
        }),
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
            paddingLeft: 0,
            marginLeft: 0,
        },
        statusRow: {
            display: 'flex',
            flexWrap: 'nowrap',
            margin: 0,
            padding: 0,
            alignItems: 'center',
        },
        subtitleRow: {
            marginTop: spacing,
        },
    });
};
