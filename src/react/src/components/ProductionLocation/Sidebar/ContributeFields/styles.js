import commonStyles from '../../commonStyles';

export default theme =>
    Object.freeze({
        ...commonStyles(theme),
        contributeSectionContainer: Object.freeze({
            marginBottom: theme.spacing.unit,
            padding: theme.spacing.unit * 2,
        }),
        title: Object.freeze({
            fontWeight: theme.typography.fontWeightSemiBold,
            marginBottom: theme.spacing.unit,
            fontSize: '1rem',
        }),
        subtitle: Object.freeze({
            color: theme.palette.text.secondary,
            marginBottom: theme.spacing.unit * 2,
            fontSize: '0.875rem',
        }),
        actionsList: Object.freeze({
            width: '100%',
            flexDirection: 'column',
            margin: 0,
        }),
        actionItemWrapper: Object.freeze({
            borderBottom: `1px solid ${theme.palette.divider}`,
            '&:last-child': {
                borderBottom: 'none',
            },
        }),
        actionItem: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            padding: `${theme.spacing.unit}px ${theme.spacing.unit * 2}px`,
            textDecoration: 'none',
            color: theme.palette.text.primary,
            transition: 'background-color 0.2s ease',
            width: '100%',
            boxSizing: 'border-box',
            cursor: 'pointer',
            '&:hover': {
                backgroundColor: theme.palette.action.hover,
            },
        }),
        actionIcon: Object.freeze({
            marginRight: theme.spacing.unit * 1.5,
            fontSize: 20,
            color: theme.palette.text.secondary,
        }),
        actionLabel: Object.freeze({
            flex: 1,
            fontWeight: theme.typography.fontWeightMedium,
        }),
        actionChevron: Object.freeze({
            fontSize: 20,
            color: theme.palette.text.disabled,
        }),
    });
