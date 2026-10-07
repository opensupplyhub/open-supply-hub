import React from 'react';
import PropTypes from 'prop-types';
import ChevronLeft from '@material-ui/icons/ChevronLeft';

import { DATA_LABELS_BACK_TEXT } from './constants';

const DataSourceDetail = ({
    classes,
    item,
    onBack,
    tabIndex,
    backButtonRef,
}) => (
    <>
        <button
            type="button"
            ref={backButtonRef}
            className={classes.backButton}
            onClick={onBack}
            tabIndex={tabIndex}
            data-testid="data-label-back"
        >
            <ChevronLeft className={classes.backChevron} aria-hidden />
            {DATA_LABELS_BACK_TEXT}
        </button>
        {item && (
            <>
                <div className={classes.detailTitle}>
                    <item.Icon
                        className={classes[item.iconClassNameKey]}
                        aria-hidden
                    />
                    <span className={classes[item.labelClassNameKey]}>
                        {item.title}
                    </span>
                </div>
                <p className={classes.detailText}>
                    {item.subsectionText}
                    {item.learnMoreUrl && (
                        <>
                            {' '}
                            <a
                                href={item.learnMoreUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={classes.learnMoreLink}
                                tabIndex={tabIndex}
                            >
                                Learn more →
                            </a>
                        </>
                    )}
                </p>
            </>
        )}
    </>
);

DataSourceDetail.propTypes = {
    classes: PropTypes.object.isRequired,
    item: PropTypes.shape({
        Icon: PropTypes.oneOfType([PropTypes.func, PropTypes.object]),
        iconClassNameKey: PropTypes.string,
        labelClassNameKey: PropTypes.string,
        title: PropTypes.string,
        subsectionText: PropTypes.string,
        learnMoreUrl: PropTypes.string,
    }),
    onBack: PropTypes.func.isRequired,
    tabIndex: PropTypes.number,
    backButtonRef: PropTypes.object,
};

DataSourceDetail.defaultProps = {
    item: null,
    tabIndex: 0,
    backButtonRef: undefined,
};

export default DataSourceDetail;
