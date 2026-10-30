import COLOURS from '../../../util/COLOURS';
import processingTypeSearchStyles from '../ProcessingTypeSearch/styles';

export default function isicSearchStyles(theme) {
    return Object.freeze({
        ...processingTypeSearchStyles(theme),
        // A category with no locations: dimmed and not clickable.
        resultRowEmpty: Object.freeze({
            cursor: 'default',
            '&:hover': Object.freeze({ background: 'transparent' }),
        }),
        revisionTag: Object.freeze({
            marginLeft: '6px',
            fontSize: '11px',
            lineHeight: '16px',
            borderRadius: '3px',
            padding: '0 5px',
            whiteSpace: 'nowrap',
            background: COLOURS.LIGHT_GREY,
            color: COLOURS.DARK_GREY,
        }),
    });
}
