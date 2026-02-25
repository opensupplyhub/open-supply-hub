import commonStyles from '../../commonStyles';

export default theme =>
    Object.freeze({
        ...commonStyles(theme),
        contributeSectionContainer: Object.freeze({
            padding: '12px',
            marginBottom: theme.spacing.unit,
        }),
        title: Object.freeze({
            fontWeight: 600,
            fontSize: '1.125rem',
        }),
        subtitle: Object.freeze({
            color: theme.palette.text.secondary,
            fontSize: '0.875rem',
            marginBottom: '12px',
        }),
        actionsList: Object.freeze({
            width: '100%',
            flexDirection: 'column',
            margin: 0,
            gap: '6px',
        }),
        actionItemWrapper: Object.freeze({}),
        actionItem: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            padding: '0 12px',
            height: '36px',
            gap: '8px',
            textDecoration: 'none',
            color: theme.palette.text.primary,
            transition: 'background-color 0.2s ease',
            width: '100%',
            boxSizing: 'border-box',
            cursor: 'pointer',
            background: 'none',
            border: 'none',
            '&:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.08)',
            },
        }),
        actionIcon: Object.freeze({
            fontSize: 16,
            width: 16,
            height: 16,
            flexShrink: 0,
            color: theme.palette.text.primary,
        }),
        actionLabel: Object.freeze({
            fontWeight: 500,
            fontSize: '1rem',
        }),
    });
