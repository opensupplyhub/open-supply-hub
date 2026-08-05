import React, { useState } from 'react';
import { object, string } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Collapse from '@material-ui/core/Collapse';
import { withStyles } from '@material-ui/core/styles';

import ExpandToggleChevron from '../../../Shared/ExpandToggleChevron/ExpandToggleChevron.jsx';
import { PROVENANCE_FIELD_LABELS } from '../constants';
import provenanceAccordionStyles from './styles';

const TOGGLE_LABEL = 'Source details';

/**
 * Collapsible accordion showing the per-row provenance of the
 * FacilityListItem a contribution came from (OSDEV-3073). Renders nothing
 * when the contribution carries no provenance. Collapsed by default.
 */
const ProvenanceAccordion = ({
    classes,
    provenance,
    'data-testid': dataTestId,
}) => {
    const [isOpen, setIsOpen] = useState(false);

    if (!provenance) return null;

    const rows = PROVENANCE_FIELD_LABELS.filter(
        ({ key }) => provenance[key],
    );
    if (!rows.length) return null;

    const handleToggle = () => setIsOpen(previous => !previous);
    const handleKeyDown = event => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            handleToggle();
        }
    };

    return (
        <div className={classes.container} data-testid={dataTestId}>
            <div
                className={classes.header}
                role="button"
                tabIndex={0}
                aria-expanded={isOpen}
                onClick={handleToggle}
                onKeyDown={handleKeyDown}
                data-testid="provenance-accordion-toggle"
            >
                <Typography component="span" className={classes.toggleLabel}>
                    {TOGGLE_LABEL}
                </Typography>
                <ExpandToggleChevron
                    isExpanded={isOpen}
                    className={classes.chevron}
                    expandLessTestId="provenance-accordion-expand-less"
                    expandMoreTestId="provenance-accordion-expand-more"
                />
            </div>
            <Collapse in={isOpen}>
                <div className={classes.contentArea}>
                    {rows.map(({ key, label, isLink }) => (
                        <Typography
                            key={key}
                            component="div"
                            className={classes.provenanceRow}
                        >
                            <span className={classes.provenanceLabel}>
                                {label}:
                            </span>
                            {isLink ? (
                                <a
                                    href={provenance[key]}
                                    className={classes.provenanceLink}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    {provenance[key]}
                                </a>
                            ) : (
                                provenance[key]
                            )}
                        </Typography>
                    ))}
                </div>
            </Collapse>
        </div>
    );
};

ProvenanceAccordion.propTypes = {
    classes: object.isRequired,
    provenance: object,
    'data-testid': string,
};

ProvenanceAccordion.defaultProps = {
    provenance: null,
    'data-testid': undefined,
};

export default withStyles(provenanceAccordionStyles)(ProvenanceAccordion);
