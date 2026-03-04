import COLOURS from '../../../../util/COLOURS';
import commonStyles from '../../commonStyles';

export default theme =>
    Object.freeze({
        ...commonStyles(theme),
        navContainer: Object.freeze({
            padding: '8px',
            marginBottom: theme.spacing.unit,
        }),
        title: Object.freeze({
            fontWeight: 600,
            fontSize: '1.125rem',
            padding: '4px 12px 8px',
        }),
        menuList: Object.freeze({
            padding: 0,
        }),
        menuItem: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            padding: '6px 12px',
            borderRadius: 0,
            minHeight: 'unset',
            height: '36px',
            gap: '8px',
            transition: 'background-color 0.2s ease',
            '&:hover': {
                backgroundColor: COLOURS.HOVER_GREY,
            },
        }),
        menuItemActive: Object.freeze({
            color: `${theme.palette.primary.main}14`,
        }),
        menuIcon: Object.freeze({
            fontSize: 18,
            width: 18,
            height: 18,
            flexShrink: 0,
            color: theme.palette.text.secondary,
        }),
        menuIconActive: Object.freeze({
            color: theme.palette.primary.main,
        }),
        menuLabel: Object.freeze({
            fontWeight: 500,
            fontSize: '0.875rem',
            color: theme.palette.text.primary,
        }),
        menuLabelActive: Object.freeze({
            fontWeight: 600,
            color: theme.palette.primary.main,
        }),
        link: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            textDecoration: 'none',
            color: 'inherit',
            width: '100%',
        }),
    });
