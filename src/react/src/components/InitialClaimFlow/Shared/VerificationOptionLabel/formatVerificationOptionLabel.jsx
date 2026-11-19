import React from 'react';
import VerificationOptionLabel from './VerificationOptionLabel';

/**
 * How an option in a verification dropdown is drawn (react-select's
 * `formatOptionLabel`). In the open list an option shows its `tag`
 * ("Preferred" or "Can delay review") beside its label. The chosen value
 * shows the label alone. The tag is display only: the option's `label` is
 * what the claim stores, so the tag must never be folded into it.
 */
const formatVerificationOptionLabel = (option, { context }) =>
    context === 'menu' ? (
        <VerificationOptionLabel label={option.label} tag={option.tag} />
    ) : (
        option.label
    );

export default formatVerificationOptionLabel;
