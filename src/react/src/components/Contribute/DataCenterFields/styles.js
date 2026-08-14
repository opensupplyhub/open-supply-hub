import COLOURS from '../../../util/COLOURS';

export default theme =>
    Object.freeze({
        sectionsTitle: Object.freeze({
            fontSize: '21px',
            fontWeight: theme.typography.fontWeightExtraBold,
            marginTop: '30px',
        }),
        sectionsSubTitle: Object.freeze({
            fontSize: '16px',
            fontWeight: theme.typography.fontWeightRegular,
            margin: '5px 0 10px 0',
        }),
        section: Object.freeze({
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            borderRadius: '4px',
            marginBottom: '8px',
            backgroundColor: COLOURS.WHITE,
        }),
        sectionHeader: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            cursor: 'pointer',
            padding: '12px 16px',
            userSelect: 'none',
        }),
        sectionTitle: Object.freeze({
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
        }),
        chevron: Object.freeze({
            color: COLOURS.DARK_GREY,
        }),
        sectionContent: Object.freeze({
            padding: '0 16px 16px 16px',
        }),
        fieldWrap: Object.freeze({
            marginTop: '12px',
        }),
        fieldLabel: Object.freeze({
            fontSize: '16px',
            fontWeight: theme.typography.fontWeightSemiBold,
            marginBottom: '4px',
        }),
        fieldDescription: Object.freeze({
            fontSize: '14px',
            fontWeight: theme.typography.fontWeightRegular,
            color: COLOURS.DARK_GREY,
            margin: '0 0 6px 0',
        }),
        checkboxLabel: Object.freeze({
            marginLeft: 0,
        }),
        unitsRow: Object.freeze({
            display: 'flex',
            gap: '8px',
        }),
        unitsValue: Object.freeze({
            flex: 2,
        }),
        unitsUnit: Object.freeze({
            flex: 1,
        }),
        textInputStyles: Object.freeze({
            width: '100%',
        }),
        helperText: Object.freeze({
            margin: '4px 0 0 0',
        }),
        notchedOutlineStyles: Object.freeze({
            borderRadius: 0,
        }),
    });
